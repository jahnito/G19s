import usb.core
import usb.util
import random
import time
from PIL import Image, ImageDraw, ImageFont


class Display():
    def __init__(self):
        self._dev_display = self.create_dev_keyboard()
        self._intf0_display = self.create_intf_display()
        self._ep_out_display = self.create_enfpoint_display_out()

    @staticmethod
    def create_dev_keyboard():
        dev0: usb.core.Device = usb.core.find(idVendor=0x046d, idProduct=0xc229)
        # if dev0.is_kernel_driver_active(0):
        #     try:
        #         dev0.detach_kernel_driver(0)
        #         dev0.reset()
        #     except usb.core.USBError as e:
        #         print(e)
        if dev0 is None:
            print('G19s LCD not found on USB bus')
            return None
        else:
            return dev0

    def create_intf_display(self) -> usb.Interface:
        dev = self.create_dev_keyboard()
        if not dev:
            raise usb.core.USBError('G19s LCD not found on USB')
        cfg = dev.get_active_configuration()
        return cfg[(0,0)]

    def create_enfpoint_display_out(self) -> usb.core.Endpoint:
        ep: usb.core.Endpoint = usb.util.find_descriptor(self._intf0_display, custom_match= lambda e: \
                                usb.util.endpoint_direction(e.bEndpointAddress) == \
                                usb.util.ENDPOINT_OUT)        
        return ep

    def write_frame(self, data:list=None):
        '''
        Write frame to display
        '''
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
                frame.append(int(x,base=16))
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
        for x in range(320):
            for y in range(240):
                r, g, b = access[x, y]
                val = Display.rgb_to_uint16(r, g, b)
                data.append(val >> 8)
                data.append(val & 0xff)
                # print(val, val & 0xff)
                # input()
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
