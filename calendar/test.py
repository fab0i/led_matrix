from RgbMatrix import RgbMatrix
import time
import sys

matrix = RgbMatrix()
matrix.run_gif('./img/icon/et.gif')
try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
