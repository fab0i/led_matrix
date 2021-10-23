from flask import Flask, request, jsonify
from flask_restful import Api, Resource

from RgbMatrix import RgbMatrix
import time
import sys
import json
import _thread as thread
import os

app = Flask(__name__)
api = Api(app)

def render_image():
    print("R", os.getuid())
    matrix = RgbMatrix(32, 32)
    matrix.render_gif('./img/icon/ghost.gif', 2)
    
render_image()

def render_gif(image, duration):
    matrix.render_gif(image, duration)

class ImageDisplay(Resource):
    def get(self):
        return "What?"

    def post(self):
        print("REQUEST:", request)
        #data = json.loads(request.data)
        #print("JSON LOADS", data)
        json_data = request.form
        print("REQUEST.JSON:", json_data)
        data = request.get_json()
        print("REQUEST.GET_JSON():", data)
        action = json_data['action']
        image = json_data['img']
        duration = int(json_data['duration'])
        if action == 'render_gif':
            print("Render image")
            #thread.start_new_thread( render_gif, (image, 0))
            matrix = RgbMatrix(32, 32)
            matrix.render_gif(image, duration)
            print("R", os.getuid())
            #render_image()
            print("Done.?")
        return jsonify({'status': 200})


api.add_resource(ImageDisplay, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
