from RgbMatrix import RgbMatrix
import time
import sys

matrix = RgbMatrix(32, 32)
#matrix.render_gif('./img/icon/et.gif')
#matrix.render_img('./img/icon/dog.png', 15)
#matrix.render_gif('./img/icon/gun_lady.gif')
matrix.render_gif('./img/icon/shrek.gif', 0)

#matrix.render_gif(sys.argv[1])
try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
