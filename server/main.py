from flask import Flask, request, jsonify
from flask_restful import Api, Resource

from RgbMatrix import RgbMatrix
import time
import sys

app = Flask(__name__)
api = Api(app)
matrix = RgbMatrix(32, 32)

class ImageDisplay(Resource):
    def get(self):
        return "What?"

    def post(self):
        json_data = request.get_json(force=True)
        action = json_data['action']
        image = json_data['img']

        if action == 'render_gif':
            matrix.render_gif(image, 10)

        return jsonify({'status': 200})


api.add_resource(ImageDisplay, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)