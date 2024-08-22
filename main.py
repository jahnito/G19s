from Classes import Display
from Functions import APPLET
from Functions import applet_hw, applet_time, applet_clock
import time
import threading


def run_applet():
    while True:
        if display.applet == 0:
            applet_hw(display)
        elif display.applet == 1:
            applet_time(display)
        elif display.applet == 2:
            applet_clock(display)


def slideshow():
    while True:
        for i in range(3):
            display.applet = i
            time.sleep(10)

if __name__ == '__main__':
    display = Display()
    thr1 = threading.Thread(target=run_applet)
    # thr2 = threading.Thread(target=slideshow)
    thr1.start()
    # thr2.start()
