from Classes import Display
import usb
import time
from random import randint, choice
# from Functions import get_gkeys_mkeys
from datetime import datetime, timedelta

d = Display()


# def rgb_rnd():
#     r = randint(0,255)
#     g = randint(0,255)
#     b = randint(0,255)
#     return [r, g, b]

# r, g, b = rgb_rnd()
# rx, gx, bx = [1] * 3
# nxt_restart = datetime.now() + timedelta(seconds=15)
# while True:
#     if datetime.now() > nxt_restart:
#         nxt_restart = datetime.now() + timedelta(seconds=15)
#         r, g, b = rgb_rnd()
#     if r == 255:
#         rx = -1
#     elif r == 0:
#         rx = 1
#     if g == 255:
#         gx = -1
#     elif g == 0:
#         gx = 1
#     if b == 255:
#         bx = -1
#     elif b == 0:
#         bx = 1

#     r += 1 * rx
#     g += 1 * gx
#     b += 1 * bx
#     print(r,g,b)
#     d.set_backlight(r, g, b)
#     time.sleep(0.01)

# d.save_backlight(*d.backlight)

# d.get_menu_keys()

# d.poll_menu_keys()

# d.poll_keys()