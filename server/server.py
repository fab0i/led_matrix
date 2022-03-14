from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from JobController import JobController

from RgbMatrix import RgbMatrix
import time
import sys
import json
import _thread as thread
import os, signal
from tinydb import TinyDB, Query

class FlaskPiServer(Resource):
    def get(self):
        return "What?"

    def post(self):
        response = {'status': 200}
        try:
            print( 'data', request.data)
            print('form', request.form)
            print('json', request.json)
            print('values', request.values)
            print('files', request.files)
            json_data = request.form
            action = json_data['action']

            print(action)

            if action == 'render_gif':
                self.render_gif(json_data)
            elif action == 'render_base64':
                job_id = "DisplayImage"
                print("THIS JOB:", job_id)

                self.clear_current_process()
                self.execute_process(lambda: self.render_base64(json_data, job_id))
            elif action == 'save_image':
                print(json_data)

        except Exception as e:
            response['status'] = 500
            response['error'] = str(e)
            print("ERROR:", str(e))
        return jsonify(response)

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
            print("PARENT: I'm Parent =", os.getpid())
            self.update_current_process_db(pid)
        else:
            print("CHILD: I'm the Child =", os.getpid())
            try:
                task(**kwargs)
            finally:
                print("[CHILD] Execution complete.")
                self.clear_current_process(db_only=True)
                print("CHILD: I removed myself from the database.")
                print("CHILD: ")
                exit(1)

    def clear_current_process(self, db_only=False):
        """
        Deletes the current process in the database and kills the associated process.
        :param db_only: True to not kill the process.
        :return:
        """
        print("pid={}. Clear_current_process()".format(os.getpid()))
        pid = self.clear_current_process_db()

        if not db_only and pid is not None:
            try:
                print("KILLING PROCESS - PID =", pid)
                os.kill(pid, signal.SIGBREAK)  # signal.SIGTERM   signal.SIGKILL
            finally:
                print("KILLED PROCESS - PID =", pid)

    def clear_current_process_db(self, nocache=True):
        """
        Deletes the current process in the database, if one exists.
        :param nocache: no cache.
        :return: pid of current process, if one exists.
        """

        print("Clearing current process db")
        if nocache:
            app.db.clear_cache()

        Q = Query()
        results = app.db.search(Q.job_type == 'current')
        if not results:
            app.db.insert({'pid': None, 'job_type': 'current'})
            return None
        app.db.update({'pid': None}, Q.job_type == 'current')

        print("Removed current process from DB (pid={})".format(os.getpid()))
        return results[0]['pid']

    def update_current_process_db(self, pid):
        """
        Updates the DB's current process with pid.
        :param pid: New current process pid.
        """
        app.db.clear_cache()
        app.db.update({'pid': pid}, Query().job_type == 'current')

    @staticmethod
    def render_gif(data):
        print("Render GIF")
        image = data['img']
        duration = int(data['duration'])
        matrix = RgbMatrix(32, 32)
        matrix.render_gif(image, duration)

    @staticmethod
    def render_base64(data, job_id):
        print("Render Base64")
        image = data['img']
        duration = int(data['duration'])
        matrix = RgbMatrix(32, 32)
        matrix.render_base64(image, duration)


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(FlaskPiServer, '/')

    db = TinyDB('task_db.json')
    app.db = db
    app.jobs = db.table('jobs')

    job_controller = JobController(db, app)

    app.run(host='0.0.0.0', port=5000, debug=False)
