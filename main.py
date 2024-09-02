from Classes import Display, Menu, Weather, HardwareMonitor
from Functions import applet_hw, applet_time, applet_clock, applet_cats
from Functions import get_keystroke
import time
import threading


active_applets = {
                  0: applet_time,
                  1: applet_hw,
                  2: applet_clock,
                  3: applet_cats,
                  }


def run_applet():
    while True:
        try:
            if display.applet == 0:
                active_applets[display.applet](display, active_applets, weather, hardware)
            # elif display.applet == 1:
            #     active_applets[display.applet](display, active_applets)
            else:
                active_applets[display.applet](display, active_applets)
        except ValueError:
            print('Unknown error')


def run_poll_keyboard():
    while True:
        get_keystroke(menu, applets=active_applets)


def run_slideshow():
    while True:
        for i in active_applets.keys():
            display.applet = i
            time.sleep(10)


if __name__ == '__main__':
    display = Display()
    menu = Menu(display)
    weather = Weather(56.311684, 58.008947)
    hardware = HardwareMonitor()
    thr1 = threading.Thread(target=run_applet)
    thr2 = threading.Thread(target=run_poll_keyboard)
    thr3 = threading.Thread(target=weather.poller)
    thr4 = threading.Thread(target=hardware.update_values)
    # thr3 = threading.Thread(target=run_slideshow)
    thr1.start()
    thr2.start()
    thr3.start()
    thr4.start()
