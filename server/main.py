from flask import Flask, request, jsonify
from flask_restful import Api, Resource
#from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from apscheduler.jobstores.memory import MemoryJobStore

from RgbMatrix import RgbMatrix
import time
import sys
import json
import _thread as thread
import os, signal
from tinydb import TinyDB, Query

def code_setup():
    print("CODE SETUP!!")
    pass

class FlaskPiServer(Resource):

    def __call__(self, app, *args, **kwargs):
        code_setup()
        return Resource.__call__(self, app, *args, **kwargs)

    def get(self):
        return "What?"

    def post(self):
        response = {'status': 200}
        try:
            json_data = request.form
            action = json_data['action']

            if action == 'render_gif':
                self.render_gif(json_data)
            elif action == 'render_base64':
                job_id = "DisplayImage"
                print("THIS JOB:", job_id)

                self.clear_current_process()

                funcz = lambda: self.render_base64(json_data, job_id)
                job = app.apscheduler.add_job(replace_existing=True, func=self.execute_process, trigger='date',
                        args=[funcz], id=job_id, max_instances=1)

                print(job.id)

        except Exception as e:
            response['status'] = 500
            response['error'] = str(e)
            print("ERROR:", str(e))
        return jsonify(response)

    def execute_process(self, task, **kwargs):
        print("Executing", task)
        for k,v in kwargs.items():
            print("k:{}, v:{}".format(k,v))
        pid = os.fork()

        if pid > 0:
            print("Im Parent =", os.getpid())
            self.add_process_db(pid)
        else:
            print("[CHILD] I'm Child  =", os.getpid())
            try:
                task(**kwargs)
            finally:
                print("[CHILD] Execution complete")
                self.clear_current_process(db_only=True)
                print("[CHILD] File removed")
                print("[CHILD] Sepukku time")
                exit()

    def clear_current_process(self, db_only=False):
        print("pid={}. Clear_current_process()".format(os.getpid()))
        #try:
        #    file_info = os.stat(self.pid_file)
        #    print("pid={}. File Stats={}".format(os.getpid(), file_info))
        #except Exception as e:
        #    print("Error clear:", str(e))
        pid = self.clear_current_process_db()
        if pid is not None:
        #if os.path.exists(self.pid_file):
            if not db_only:
                #with open(self.pid_file, 'r') as pidfile:
                #    pid = int(pidfile.read())
                try:
                    print("KILLING PROCESS - PID =", pid)
                    os.kill(pid, signal.SIGTERM)
                finally:
                    print("KILLED PROCESS - PID =", pid)

    def clear_current_process_db(self, nocache=True):
        if nocache:
            app.db.clear_cache()
        Q = Query()
        results = app.db.search(Query()['job_type'] == 'current')
        print("CLEAR - initial results:", results)

        results = app.db.search(Q.job_type == 'current')
        if not results:
            app.db.insert({'pid': None, 'job_type': 'current'})
            return None

        app.db.update({'pid': None}, Q.job_type == 'current')
        results2 = app.db.search(Query()['job_type'] == 'current')
        print("pid=", os.getpid(),". CLEAR - updated results:", results2)
        return results[0]['pid']

    def add_process_db(self, pid):
        app.db.clear_cache()
        Q = Query()
        results = app.db.search(Query()['job_type'] == 'current')
        print("ADD - initial results:", results)
        #print("Inserting into db")
        #app.db.remove((Q.pid != None) & (Q.job_type == 'current'))
        #app.db.insert({'current_pid': pid, 'job_type': 'current'})
        app.db.update({'pid': pid}, Q.job_type == 'current')
        results = app.db.search(Query()['job_type'] == 'current')
        print("ADD - updated results:", results)


    def render_gif(self, data):
        print("Render GIF")
        image = data['img']
        duration = int(data['duration'])
        matrix = RgbMatrix(32, 32)
        matrix.render_gif(image, duration)

    def render_base64(self, data, job_id):
        print("Render Base64")
        image = data['img']
        duration = int(data['duration'])
        matrix = RgbMatrix(32, 32)
        matrix.render_base64(image, duration)


    def queue_image(self, image, date):
        pass


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(FlaskPiServer, '/')

    db = TinyDB('task_db.json')
    #db.app = app
    app.db = db
    app.jobs = db.table('jobs')

    scheduler = BackgroundScheduler()
    #scheduler.init_app(app)
    scheduler.app = app
    scheduler.app.apscheduler = scheduler
    scheduler.start()

    app.run(host='0.0.0.0', port=5000, debug=False)
