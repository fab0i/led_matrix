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

    def render_img(self, img_file, duration):
        image = Image.open(img_file)
        image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        
        self.matrix.SetImage(image.convert('RGB'))
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
    def render_gif(self, img_file):
       frames = self.processImage(img_file)
       while True:
           for f in frames:
               self.matrix.SetImage(f.convert('RGB'))
               time.sleep(0.1)
