from display_g19s import Display
from functions import APPLET
from functions import applet_hw, applet_time, applet_clock
import time


if __name__ == '__main__':
    display = Display()
    APPLET = 2
    while True:
        if APPLET == 0:
            applet_hw(display)
        elif APPLET == 1:
            applet_time(display)
        elif APPLET == 2:
            applet_clock(display)
