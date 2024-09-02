from Classes import Display
import usb
import time
from random import randint, choice
from Functions import get_gkeys_mkeys

d = Display()
# d.reset()

# time.sleep(5)
# rtype = usb.TYPE_CLASS | usb.RECIP_INTERFACE

# d.reset()

# отцепляем системный дравер с первого интерфейса
# d._dev_display.detach_kernel_driver(1)
c = 1
while True:
    rngs = [range(randint(0, 256), -1, -1),
            range(randint(0, 256), randint(0, 256)),
            range(randint(0, 256), randint(0, 256)),
            range(randint(0, 256), -1, -1)]
    for r in choice(rngs):
        for g in choice(rngs):
            for b in choice(rngs):
                d.set_backlight(r, g, b)
                time.sleep(0.05)

# d.save_backlight(*d.backlight)


# while True:
#     try:
#         res = d._dev_display.read(0x83, 20, 10000)
#         print(res)
#         time.sleep(2)
#     except usb.core.USBError as e:
#         print(e)



# while True:
#     print(d.get_m_g_keys())
#     time.sleep(1)