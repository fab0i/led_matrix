from flask import Flask
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

    def post(self, action, image):
        matrix.render_gif(image, 0)