from tinydb import TinyDB, Query
from Alerts import NotificationAlert, CalendarAlert
import time
from apscheduler.schedulers.background import BackgroundScheduler
from Calendar import CalendarController
import json

find_jobs_freq = 30
process_jobs_freq = 15
image_keywords_file = './user_info/image_keywords.json'

class JobController:
    def __init__(self, db, app):
        self.db = db
        self.app = app
        self.calendar = CalendarController()
        self.scheduler = BackgroundScheduler()
        #self.scheduler.add_job(lambda: self.process_jobs(), trigger="interval", seconds=process_jobs_freq)
        #self.scheduler.add_job(lambda: self.find_jobs(), trigger="interval", seconds=find_jobs_freq)
        self.scheduler.start()
        with open(image_keywords_file, ) as kf:
            self.keywords = json.load(kf)
        self.process_jobs()

    def find_jobs(self):
        """
        Every 1 min:
            - Checks for Calendar Events
            - Other stuff
        :return:
        """
        print("Looking for events")
        calendar_events = self.calendar.get_upcoming_events()
        for event in calendar_events:
            print(event)
            event_info = self.calendar.get_event_info(event)
            print(event_info)
            if event_info['start_in'] < find_jobs_freq:
                exists = self.db.search(Query().id == event_info['id'])
                if exists:
                    continue
                file_location = None
                for word in event_info['summary'].lower().split():
                    if word in self.keywords:
                        img = self.db.table('images').search(Query().id == self.keywords[word])[0]
                        file_location = img['file_location']
                if file_location:
                    display = "image_file"
                    display_info = file_location
                else:
                    display = "text"
                    display_info = event_info['summary']

                calendar_job = CalendarAlert(
                    calendar_id=event_info['id'],
                    name=event_info['summary'],
                    stop={"condition": "time", "time": event_info['end_after']},
                    soon=1,
                    date_start=time.time() + event_info['start_in'],
                    display=display,
                    display_info=display_info
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

            not2 = NotificationAlert(
                name="test2",
                stop={"condition": "date", "date": time.time() + 120},
                soon=1,
                date_start=time.time() + 6,
                display="image",
                display_info=None
            )
            self.db.insert(not2.to_dict())

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
        print(job)
        #self.db.update({'soon': 0}, Q.job_type == 'current')
        self.execute_job(job)

    def execute_job(self, job):
        # sleep
        task = None
        if job['type'] == 'calendar':
            if job['display'] == 'image_file':
                file_location = job['display_info']
                duration = job['stop']['time']
                task = lambda: self.app.render_image_file(file_location, duration)
        self.app.clear_current_process()
        self.app.execute_process(task)

    @staticmethod
    def _get_job_to_execute(jobs):
        """
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
