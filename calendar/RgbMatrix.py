#!/usr/bin/env python
import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

class RgbMatrix():
    def __init__(self, rows=32, chain_length=1, parallel=1):
        options = RGBMatrixOptions()
        options.rows = rows
        options.cols = rows
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'

        self.matrix = RGBMatrix(options=options)

    def render_img(self, img_file):
        image = Image.open(img_file)
        image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        
        self.matrix.SetImage(image.convert('RGB'))

