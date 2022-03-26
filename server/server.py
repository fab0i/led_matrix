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
import base64
import re

IMG_DIR = '/pixeled_images'

class FlaskPiServer(Resource):
    def get(self):
        return "What?"

    def post(self):
        response = {'status': 200}
        try:
            print('data', request.data)
            print('form', request.form)
            print('json', request.json)
            print('values', request.values)
            print('files', request.files)
            json_data = request.form if request.form else json.loads(request.json)
            action = json_data['action']

            print(action)

            if action == 'render_gif':
                self.render_gif(json_data)
            elif action == 'render_base64':
                job_id = "DisplayImage"
                print("THIS JOB:", job_id)

                sapp.jobs.clear_current_process()
                self.app.jobs.execute_process(lambda: self.render_base64(json_data, job_id))
            elif action == 'save_image':
                print("\n\nSave Image...")
                img_data = json_data['data']
                self.app.jobs.save_image(IMG_DIR, img_data['file'], img_data['image'], img_data['id'], img_data['user_id'])
            elif action == 'save_keywords_dict':
                print("\n\nSave Keywords...")
                job_controller.save_keywords(json_data['keywords_dict'])


        except Exception as e:
            response['status'] = 500
            response['error'] = str(e)
            print("ERROR:", str(e))
        return jsonify(response)

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

    # TODO: IF NEEDED< CREATE DIFFERENT FILES FOR DIFFERENT PURPOSES/TABLES
    db = TinyDB('main_db.json')
    app.db = db
    #app.jobs = db.table('jobs')
    app.images = db.table('images')

    job_controller = JobController(db, app)
    app.jobs = job_controller

    app.run(host='0.0.0.0', port=5000, debug=False)
