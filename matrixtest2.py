#!/usr/bin/python

# A more complex RGBMatrix example works with the Python Imaging Library,
# demonstrating a few graphics primitives and image loading.
# Note that PIL graphics do not have an immediate effect on the display --
# image is drawn into a separate buffer, which is then copied to the matrix
# using the SetImage() function (see examples below).
# Requires rgbmatrix.so present in the same directory.

# PIL Image module (create or load images) is explained here:
# http://effbot.org/imagingbook/image.htm
# PIL ImageDraw module (draw shapes to images) explained here:
# http://effbot.org/imagingbook/imagedraw.htm

import Image
import ImageDraw
import time
from rgbmatrix import Adafruit_RGBmatrix

# Rows and chain length are both required parameters:
matrix = Adafruit_RGBmatrix(32, 1)

# Bitmap example w/graphics prims
image = Image.new("1", (32, 32)) # Can be larger than matrix if wanted!!
draw  = ImageDraw.Draw(image)    # Declare Draw instance before prims
# Draw some shapes into image (no immediate effect on matrix)...
draw.rectangle((0, 0, 31, 5), fill=0, outline=1)
draw.rectangle((0, 13, 19, 18), fill=0, outline=1)
draw.rectangle((0, 0, 5, 31), fill=0, outline=1)
# Then scroll image across matrix...
for n in range(-32, 1): # Start off top-left, move off bottom-right
	matrix.Clear()
	matrix.SetImage(image.im.id, 0, 0)
	time.sleep(0.05)

matrix.Clear()

image = Image.open("weed.png")
image.load()          # Must do this before SetImage() calls
matrix.SetImage(image.im.id, 0, 0)
time.sleep(2.025)
	
matrix.Clear()

image = Image.open("dog2.png")
image.load()          # Must do this before SetImage() calls
for n in range(32, -image.size[0], -1): # Scroll R to L
	matrix.SetImage(image.im.id, n, 0)
	time.sleep(0.025)
	
matrix.Clear()

image = Image.open("groceries2.png")
image.load()          # Must do this before SetImage() calls
for n in range(32, -image.size[0], -1): # Scroll R to L
	matrix.SetImage(image.im.id, n, 0)
	time.sleep(0.025)
	
matrix.Clear()

image = Image.open("gym2.png")
image.load()          # Must do this before SetImage() calls
for n in range(32, -image.size[0], -1): # Scroll R to L
	matrix.SetImage(image.im.id, n, 0)
	time.sleep(0.025)
	
matrix.Clear()

image = Image.open("hair2.png")
image.load()          # Must do this before SetImage() calls
for n in range(32, -image.size[0], -1): # Scroll R to L
	matrix.SetImage(image.im.id, n, 0)
	time.sleep(0.025)
	
matrix.Clear()

image = Image.open("pill2.png")
image.load()          # Must do this before SetImage() calls
for n in range(32, -image.size[0], -1): # Scroll R to L
	matrix.SetImage(image.im.id, n, 0)
	time.sleep(0.025)
	
matrix.Clear()

image = Image.open("plate2.png")
image.load()          # Must do this before SetImage() calls
for n in range(32, -image.size[0], -1): # Scroll R to L
	matrix.SetImage(image.im.id, n, 0)
	time.sleep(0.025)
	
matrix.Clear()

image = Image.open("run2.png")
image.load()          # Must do this before SetImage() calls
for n in range(-32, image.size[0], +1): # Scroll R to L
	matrix.SetImage(image.im.id, n, 0)
	time.sleep(0.025)
	
matrix.Clear()

image = Image.open("weed.png")
image.load()
matrix.SetImage(image.im.id, 0, 0)
time.sleep(8.025)
	
matrix.Clear()