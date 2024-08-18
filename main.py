from display_g19s import Display
from functions import APPLET
from functions import applet_hw, applet_time
import time


if __name__ == '__main__':
    display = Display()
    APPLET = 1
    while True:
        if APPLET == 0:
            applet_hw(display)
        elif APPLET == 1:
            applet_time(display)

