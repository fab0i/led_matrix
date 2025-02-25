from tinydb import TinyDB, Query
from Alerts import NotificationAlert, CalendarAlert
from RgbMatrix import RgbMatrix
from apscheduler.schedulers.background import BackgroundScheduler
from Calendar import CalendarController
from database.Databases import JobsDB, ImagesDB
import time
import json
import os
import signal
import base64
import re

pre_process_jobs_freq = 30
process_jobs_freq = 15

IMAGE_KEYWORDS_FILE = './user_info/image_keywords.json'
IMG_DIR = '/pixeled_images'

class JobController:
    def __init__(self, app):
        self.app = app

        # TODO: IF NEEDED< CREATE DIFFERENT FILES FOR DIFFERENT PURPOSES/TABLES
        db = TinyDB('main_db.json')
        self.db = JobsDB()
        self.img_db = ImagesDB()
        with open(IMAGE_KEYWORDS_FILE, ) as kf:
            self.keywords = json.load(kf)

        self.calendar = CalendarController()
        self.scheduler = BackgroundScheduler()

        self.scheduler.add_job(lambda: self.process_jobs(), trigger="interval", seconds=process_jobs_freq)
        self.scheduler.add_job(lambda: self.pre_process_jobs(), trigger="interval", seconds=pre_process_jobs_freq)
        self.scheduler.start()

        self.process_jobs()

    def pre_process_jobs(self):
        """
        Every 1 min:
            - Checks for Calendar Events
            - Other stuff
            - @TODO: Check if calendar id already exists
            - @TODO: Remove calendar events that are past the date_end from the jobs db (self.db)
        """
        print("Looking for events")
        calendar_events = self.calendar.get_upcoming_events()
        for event in calendar_events:
            print(event)
            event_info = self.calendar.get_event_info(event)
            print(event_info)
            if event_info['start_in'] < pre_process_jobs_freq:
                display = self.calendar.get_event_display(event_info['summary'], self.keywords)
                calendar_job = CalendarAlert(
                    calendar_id=event_info['id'],
                    name=event_info['summary'],
                    stop={"condition": "time", "time": event_info['end_after']},
                    soon=1,
                    date_start=time.time() + event_info['start_in'],
                    display=display['display'],
                    display_info=display['display_info']
                )
                print("Inserted new Calendar Job", calendar_job.to_dict())
                self.db.insert(calendar_job.to_dict())

    def process_jobs(self):
        """
        Every 5s: TODO: this pydoc
        :return:
        """
        print("Processing jobs...")
        Q = Query()
        jobs = self.db.search(Q.job == 'alert' and Q.soon <= 1)

        print("\n\nALL JOBS:\n")
        print(jobs)
        print("\n\n\n")

        if False and not jobs:
            not1 = NotificationAlert(
                name="test1",
                stop={"condition": "date", "date": time.time() + 120},
                soon=0,
                date_start=time.time() + 3,
                display="image",
                display_info=None
            )
            self.db.insert(not1.to_dict())

            print("Inserted test jobs")
            jobs = self.db.search(Q.job == 'alert' and Q.soon <= 2)
            print(jobs)

        if len(jobs) == 0:
            return False
        elif len(jobs) == 1:
            job = jobs[0]
        else:
            # If there are more than 1 jobs to be executed in the next 5s, run the helper function to figure out which
            job = self._get_job_to_execute(jobs)
        print("\nExecuting job:")
        print(job, '\n')

        self.execute_job(job)

    def execute_job(self, job):
        # sleep
        task = None
        if job['display'] == 'image_file':
            file_location = job['display_info']['file_location']
            image_type = job['display_info']['image_type']
            duration = job['stop']['time']
            task = lambda: self.render_image_by_type(image_type, file_location, duration)
            self.clear_current_process()
            self.execute_process(task)

    @staticmethod
    def _get_job_to_execute(jobs):
        """
        soon = -2 -> Job marked as completed but we're before the end_date (E.g. Calendar event was canceled manually)
        soon = -1 -> Job is currently running.
        soon =  0 -> Job is queued to be executed next
        soon =  1 -> Job is going o happen in the next [pre_process_jobs_freq] seconds


        Given multiple jobs that are currently on the "soon" queue, returns the appropriate job to be executed. Logic:
        - If any job has soon=-1, return None, since a job is already queued for execution.
        - All jobs that have soon=1 have priority over jobs with soon=0, since new jobs that should be displayed on time
        - For more than 1 job with soon=1, queue the one with oldest (min) date_start
        - For more than 1 job with soon=0, queue the one with oldest (min) last_run
        :param jobs:
        :return: job to be executed or None
        """

        min_job = None

        for job in jobs:
            # If we already have a job already queued for execution => We're not executing another one => return None
            if job['soon'] == -1:
                return None

            elif job['soon'] == 1:
                if not min_job or min_job['soon'] == 0 or job['date_start'] < min_job['date_start']:
                    min_job = job

            elif job['soon'] == 0:
                if not min_job or (min_job['soon'] != 1 and job['last_run'] < min_job['last_run']):
                    min_job = job

        return min_job

    def clear_current_process_db(self, nocache=True):
        """
        Deletes the current process in the database, if one exists.
        :param nocache: no cache.
        :return: pid of current process, if one exists.
        """

        print("Clearing current process db")
        if nocache:
            self.db.clear_cache()

        Q = Query()
        results = self.db.search(Q.job_type == 'current')
        if not results:
            self.db.insert({'pid': None, 'id': None, 'job_type': 'current'})
            return None
        self.db.update({'pid': None, 'id': None}, Q.job_type == 'current')
        if results[0]['id']:
            self.db.update()

        print("Removed current process from DB (pid={})".format(os.getpid()))
        return results[0]['pid']

    def remove_job_from_queue(self, job):
        """
        Removes the given job from the queue/db. If the job has a date_end
        :param job:
        :return:
        """


    def clear_current_process(self, db_only=False, nocache=False):
        """
        Deletes the current process in the database and kills the associated process.
        :param db_only: True to not kill the process.
        :param nocache: Don't use cache in when clearing the process from the DB
        :return:
        """
        print("pid={}. Clear_current_process()".format(os.getpid()))
        pid = self.clear_current_process_db(nocache=nocache)

        if not db_only and pid is not None:
            try:
                print("KILLING PROCESS - PID =", pid)
                os.kill(pid, signal.SIGTERM)  # signal.SIGTERM   signal.SIGKILL
            finally:
                print("KILLED PROCESS - PID =", pid)

    def execute_process(self, task, **kwargs):
        """
        Execute the given task in a chil process and then
        :param task:
        :param kwargs:
        :return:
        """
        print("Executing", task)
        for k, v in kwargs.items():
            print("k:{}, v:{}".format(k, v))

        # pid = 1   # TESTING
        pid = os.fork()   # PI

        if pid > 0:
            print("PARENT: I'm Parent =", os.getpid(), ". child =", pid)
            # Adding child process as current process
            self.update_current_process_db(pid)
        else:
            print("CHILD: I'm the Child =", os.getpid())
            # self.update_current_process_db(os.getpid())
            try:
                task(**kwargs)
            finally:
                print("[CHILD] Execution complete.")
                self.clear_current_process(db_only=True)
                print("CHILD: I removed myself from the database.")
                print("CHILD: Removing myself from existence...")
                #sys.exit(0)
                os._exit(os.EX_OK)


    def update_current_process_db(self, pid):
        """
        Updates the DB's current process with pid.
        :param pid: New current process pid.
        """
        self.db.clear_cache()
        self.db.update({'pid': pid}, Query().job_type == 'current')

    def clear_current_process_db(self, nocache=True):
        """
        Deletes the current process in the database, if one exists.
        :param nocache: no cache.
        :return: pid of current process, if one exists.
        """

        print("Clearing current process db")
        if nocache:
            self.db.clear_cache()

        Q = Query()
        results = self.db.search(Q.job_type == 'current')
        if not results:
            self.db.insert({'pid': None, 'job_type': 'current'})
            return None
        self.db.update({'pid': None}, Q.job_type == 'current')

        print("Removed current process from DB (pid={})".format(os.getpid()))
        return results[0]['pid']

    def save_image(self, file_location, img_str_data, img_id, user_id):
        print("Saving image to database table")
        self.db.images.insert({'id': img_id, 'file_location': file_location, 'user_id': user_id})
        print("Saved to db.")
        print("Converting to binary")
        img_data = base64.b64decode(re.sub(r'data:image\/[a-z]+;base64,', '', img_str_data))
        print("Creating dirs")
        file_location = IMG_DIR + file_location
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        print("Saving image file...")
        with open(file_location, 'wb') as f:
            f.write(img_data)
        print("Save complete")

    def save_keywords(self, keywords_json):
        self.keywords = json.loads(keywords_json)
        with open(IMAGE_KEYWORDS_FILE, 'w') as k:
            k.write(keywords_json)

    @staticmethod
    def render_image_by_type(img_type, img_file, duration):
        print("Render Image File")
        img_file = IMG_DIR + img_file
        print("File: " + img_file)
        matrix = RgbMatrix(32, 32)
        matrix.render_image_by_type(img_type, img_file, duration)
