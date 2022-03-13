#!/usr/bin/env python

import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from io import BytesIO
import base64
import re

class RgbMatrix():
    def __init__(self, rows=32, cols=32):
        options = RGBMatrixOptions()
        options.rows = rows
        options.cols = cols
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.drop_privileges = False

        self.size = (rows, cols)

        self.matrix = RGBMatrix(options=options)

    def render_img(self, img_file, duration, pixelate=False):
        try:
            image = Image.open(img_file)
            if pixelate:
                image = self.pixelate(image)
            self.display_img(image, duration)
        except IOError:
            print("Unable to load image")

    def pixelate(self, pilImage):
        """
        :param pilImg: img file path
        :return: Pixelated image, resized to fit the canvas
        """
        # Resize Pillow image to have dimension of LED Matrix
        pilImage = pilImage.resize(self.size)
        return pilImage

    def display_img(self, img, duration):
        self.matrix.SetImage(img.convert('RGB'))
        time.sleep(duration)

    @staticmethod
    def analyseImage(path):
        """
        Pre-process pass over the image to determine the mode (full or additive).
        Necessary as assessing single frames isn't reliable. Need to know the mode
        before processing all frames.
        """

        im = Image.open(path)
        results = {
            'size': im.size,
            'mode': 'full',
        }

        try:
            while True:
                if im.tile:
                    tile = im.tile[0]
                    update_region = tile[1]
                    update_region_dimensions = update_region[2:]
                    if update_region_dimensions != im.size:
                        results['mode'] = 'partial'
                        break
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        return results

    def processImage(self, path):
        """
        Iterate the GIF, extracting each frame.
        """
        mode = self.analyseImage(path)['mode']

        im = Image.open(path)

        frames = []

        i = 0
        p = im.getpalette()
        last_frame = im.convert('RGBA')


        try:
            while True:
                '''
                If the GIF uses local colour tables, each frame will have its own palette.
                If not, we need to apply the global palette to the new frame.
                '''
                if not im.getpalette():
                    im.putpalette(p)

                new_frame = Image.new('RGBA', im.size)

                '''
                Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
                If so, we need to construct the new frame by pasting it on top of the preceding frames.
                '''
                if mode == 'partial':
                    new_frame.paste(last_frame)

                new_frame.paste(im, (0,0), im.convert('RGBA'))
                frames.append(new_frame)

                i += 1
                last_frame = new_frame
                im.seek(im.tell() + 1)
        except EOFError:
            pass

        return frames

    # @TODO: Transparent GIFs are broken
    def render_gif(self, img_file, duration):
        print("Render gif:", img_file, duration)
        frames = [self.pixelate(f) for f in self.processImage(img_file)]
        print(len(frames))
        start = time.time()
        while time.time() - start < duration if duration else True:
            for f in frames:
                self.display_img(f, 0.1)

    def render_base64(self, image, duration):
        image = re.sub(r'^data:image\/[a-z]+;base64,', '', image)
        image = Image.open(BytesIO(base64.b64decode(image)))
        self.display_img(image, duration)
        return True
