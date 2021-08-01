from RgbMatrix import RgbMatrix
import time
import sys
from tkinter import Tk

# matrix = RgbMatrix()
# matrix.run_gif('./img/icon/et.gif')
# try:
#     print("Press CTRL-C to stop.")
#     while True:
#         time.sleep(100)
# except KeyboardInterrupt:
#     sys.exit(0)

matrix = RgbMatrix(32, 32)
#matrix.render_gif('./img/icon/et.gif')
#matrix.render_img('./img/icon/groceries2.png', 15)
#matrix.render_gif('./img/icon/gun_lady.gif')
#matrix.render_gif('./img/icon/ghost.gif')

matrix.render_gif(sys.argv[1])

