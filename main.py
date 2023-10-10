import cv2 as cv
import numpy as np
from time import time
from window_capture import WindowCapture
from vision import Vision
# print(accuracy(wincap.get_screenshot, "tin_ore.png", method=1))

# WindowCapture.list_window_names()
wincap = WindowCapture("Albion Online Client")
vs = Vision("object.png")
vs.init_control_gui()

loop_time = time()
while True:
    # Mostra a screenshot da tela
    screenshot = wincap.get_screenshot()

    rectangles = vs.find(screenshot, method=1, limite_max=0.9)

    output = vs.draw_rectangles(screenshot, rectangles)

    cv.imshow("Computer Vision", output)

    # print(f"FPS {1 / (time() - loop_time):.0f}")
    # loop_time = time()


    if cv.waitKey(1) == ord("q"):
        cv.destroyAllWindows()
        break


