import usb.core
import usb.util
import random
import time
from PIL import Image


class Display():
    def __init__(self):
        self.applet = 0
        self._dev_display = self.create_dev_keyboard()
        self._intf0 = self.create_intf_display()
        self._ep_out_display = self.create_endpoint_display_out()
        self._ep_in_keyboard = self.create_endpoint_keyboard_in()
        self.last_image = None

    @staticmethod
    def create_dev_keyboard() -> usb.core.Device:
        dev: usb.core.Device = usb.core.find(idVendor=0x046d, idProduct=0xc229)
        if dev.is_kernel_driver_active(0):
            try:
                dev.detach_kernel_driver(0)
                dev.reset()
            except usb.core.USBError as e:
                print(e)
        if dev is None:
            print('G19s LCD not found on USB bus')
            raise usb.core.USBError
        else:
            return dev

    def create_intf_display(self) -> usb.Interface:
        dev = self.create_dev_keyboard()
        if not dev:
            raise usb.core.USBError('G19s LCD not found on USB')
        cfg = dev.get_active_configuration()
        return cfg[(0,0)]

    def create_endpoint_display_out(self) -> usb.core.Endpoint:
        ep: usb.core.Endpoint = usb.util.find_descriptor(self._intf0, custom_match= lambda e: \
                                usb.util.endpoint_direction(e.bEndpointAddress) == \
                                usb.util.ENDPOINT_OUT)
        return ep

    def create_endpoint_keyboard_in(self) -> usb.core.Endpoint:
        ep: usb.core.Endpoint = usb.util.find_descriptor(self._intf0, custom_match= lambda e: \
                                usb.util.endpoint_direction(e.bEndpointAddress) == \
                                usb.util.ENDPOINT_IN)
        return ep

    def write_frame(self, data:list=None):
        '''
        Write frame to display
        '''
        self.last_image = data
        frame = [0x10, 0x0F, 0x00, 0x58, 0x02, 0x00, 0x00, 0x00,
                 0x00, 0x00, 0x00, 0x3F, 0x01, 0xEF, 0x00, 0x0F]
        for i in range(16, 256):
            frame.append(i)
        for i in range(256):
            frame.append(i)
        if data:
            frame += data
        else:
            x = hex(random.randint(1, 255))
            for i in range(153600):
                frame.append(int(x, base=16))
        self._ep_out_display.write(frame, 1000)

    @staticmethod
    def convert_image_to_frame(filename):
        '''Loads image from given file.

        Format will be auto-detected.  If neccessary, the image will be resized
        to 320x240.

        @return Frame data to be used with send_frame().
        '''
        if isinstance(filename, str):
            img = Image.open(filename)
        else:
            img = filename
        access = img.load()
        if img.size != (320, 240):
            img = img.resize((320, 240), Image.BICUBIC)
            access = img.load()
        data = []
        try:
            r, g, b = access[0, 0]
        except TypeError:
            img = Image.open('error.jpg')
            access = img.load()
        for x in range(320):
            for y in range(240):
                r, g, b = access[x, y]
                val = Display.rgb_to_uint16(r, g, b)
                data.append(val >> 8)
                data.append(val & 0xff)
        return data

    @staticmethod
    def rgb_to_uint16(r, g, b):
        '''Converts a RGB value to 16bit highcolor (5-6-5).

        @return 16bit highcolor value in little-endian.
        '''
        rBits = int(r * 2**5 / 255)
        gBits = int(g * 2**6 / 255)
        bBits = int(b * 2**5 / 255)
        rBits = rBits if rBits <= 0b00011111 else 0b00011111
        gBits = gBits if gBits <= 0b00111111 else 0b00111111
        bBits = bBits if bBits <= 0b00011111 else 0b00011111
        valueH = (rBits << 3) | (gBits >> 3)
        valueL = ((gBits & 7) << 5) | bBits
        return valueL << 8 | valueH

    def reset(self):
        self._dev_display.reset()


class Menu():
    def __init__(self, display: Display):
        self.enabled = 0
        self.display = display

    def get_int_from_key(self, id: int):
        pass

    def set_default_action(self, id: int, num_applets: int):
        if not self.enabled:
            # pass
            if id == 16:
                if self.display.applet < num_applets - 1:
                    self.display.applet += 1
            elif id == 32:
                if self.display.applet > 0:
                    self.display.applet -= 1
            print(self.display.applet)
