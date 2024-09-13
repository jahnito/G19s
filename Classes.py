import usb.core
import usb.util
import random
import urllib.request, urllib.error, json
import datetime, time
from PIL import Image
import psutil


class Display():
    def __init__(self):
        self.applet = 0
        self._dev_display = self.create_dev_keyboard()
        self._intf0 = self.create_intf_display()
        self._intf1 = self.create_intf_backlight()
        self._ep_out_display = self.create_endpoint_display_out()
        self._ep_in_keyboard = self.create_endpoint_keyboard_in()
        self._ep_in_gkeys = self.create_endpoint_gkeys()
        self.backlight = None
        self.menukey_status = None
        self.gkey_status = None
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
        if dev.is_kernel_driver_active(1):
            try:
                dev.detach_kernel_driver(1)
                dev.reset()
            except usb.core.USBError as e:
                print(e)
        if dev is None:
            print('G19s LCD not found on USB bus')
            raise usb.core.USBError
        else:
            return dev

    def create_intf_display(self) -> usb.Interface:
        if not self._dev_display:
            raise usb.core.USBError('G19s LCD not found on USB')
        cfg = self._dev_display.get_active_configuration()
        return cfg[(0,0)]

    def create_intf_backlight(self) -> usb.Interface:
        if not self._dev_display:
            raise usb.core.USBError('G19s LCD not found on USB')
        cfg = self._dev_display.get_active_configuration()
        return cfg[(1,0)]

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

    def create_endpoint_gkeys(self) -> usb.core.Endpoint:
        ep: usb.core.Endpoint = usb.util.find_descriptor(self._intf1, custom_match= lambda e: \
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

    def set_backlight(self, r, g, b, rndm=False):
        rtype = usb.TYPE_CLASS | usb.RECIP_INTERFACE
        if rndm:
            r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        colorData = [7, r, g, b]
        self.backlight = [r, g, b]
        self._dev_display.ctrl_transfer(rtype, 0x09, 0x307, 0x01, colorData, 1000)

    def save_backlight(self, r, g, b):
        rtype = usb.TYPE_CLASS | usb.RECIP_INTERFACE
        colorData = [7, r, g, b]
        self._dev_display.ctrl_transfer(rtype, 0x09, 0x307, 0x01, colorData, 1000)

    def get_menu_keys(self):
        button_id = None
        try:
            button_id = self._dev_display.read(0x81, 2, timeout=50)
            return button_id
        except usb.core.USBTimeoutError:
            return None

    def get_m_g_keys(self):
        button_id = None
        try:
            button_id = self._dev_display.read(0x83, 11, timeout=50)
            return button_id
        except usb.core.USBTimeoutError:
            return None

    def poll_keys(self):
            while True:
                if gkeys := self.get_m_g_keys():
                    self.gkey_status = tuple(gkeys)
                if menu_keys := self.get_menu_keys():
                    self.menukey_status = tuple(menu_keys)
                # print(self.gkey_status)
                # print(self.menukey_status)

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

    def keys_action(self, num_applets: int):
        while True:
            if not self.enabled:
                if self.display.menukey_status == (16, 128):
                    print('right')
                    if self.display.applet < num_applets - 1:
                        self.display.applet += 1
                elif self.display.menukey_status == (32, 128):
                    print('left')
                    if self.display.applet > 0:
                        self.display.applet -= 1
                # print("Current applet", self.display.applet)
                time.sleep(0.2)


class Weather():
    def __init__(self, lat: int | float, lon: int | float,
                 interval: int = 15, lang: str = 'ru'):
        self.interval = interval
        self.lat = lat
        self.lon = lon
        self.lang = lang
        self.cur_weather = None
        self.prev_weather = None
        self.error_get_count = 0
        self.update = None
        if not self.cur_weather:
            self.nextpoll = datetime.datetime.now() + datetime.timedelta(seconds=10)
        else:
            self.nextpoll = self.set_nextpoll()

    def poller(self):
        while True:
            if self.nextpoll <= datetime.datetime.now():
                self.prev_weather = self.cur_weather
                if new_weather := self.get_weather(self.lat, self.lon, self.lang):
                    self.cur_weather = new_weather
                    self.nextpoll = datetime.datetime.now() + datetime.timedelta(minutes=self.interval)
                    self.update = datetime.datetime.now()
                    self.error_get_count = 0
                elif self.error_get_count >= 5:
                    self.cur_weather = self.prev_weather
                    self.nextpoll = datetime.datetime.now() + datetime.timedelta(minutes=1)
                    self.error_get_count = 0
                else:
                    self.error_get_count += 1
                    self.cur_weather = self.prev_weather
                    self.nextpoll = datetime.datetime.now() + datetime.timedelta(seconds=5)
            time.sleep(5)

    def set_nextpoll(self):
        self.nextpoll = datetime.datetime.now() + datetime.timedelta(minutes=self.interval)

    @staticmethod
    def get_weather(lat: int | float, lon: int | float, lang: str) -> dict | None:
        with open('tokens/openweathermap') as f:
            token = f.read().strip()
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang={lang}&units=metric&appid={token}'
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=3) as u:
                data = json.loads(u.read().decode('utf-8'))
            return data
        except (urllib.error.URLError, ConnectionResetError) as e:
            print(e, datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
            return None


class HardwareMonitor():
    '''
    fs: determines what types of file systems on disks to monitor
    mp_excluded: determines what monitoring mountpoints should be excluded
    '''
    fs = ('ext3', 'ext4', 'fat', 'exfat', 'fat32', 'ntfs')
    mp_excluded = ('boot', 'var')

    def __init__(self, interval: int = 5):
        self.cpu_count = psutil.cpu_count()
        self.cpu_percent = psutil.cpu_percent(0.0)
        self.cpu_freq = psutil.cpu_freq()
        self.cpu_average = psutil.getloadavg()
        self.virt_mem = psutil.virtual_memory()
        self.temp_sensors = psutil.sensors_temperatures()
        self.disks = tuple(i for i in psutil.disk_partitions() \
                           if i.fstype in self.fs and \
                           i.mountpoint.split('/')[-1] not in self.mp_excluded)
        self.disks_usage = {disk.mountpoint: psutil.disk_usage(disk.mountpoint) for disk in self.disks}

        self.sys_started = psutil.boot_time()
        self.interval = datetime.timedelta(seconds=interval)
        self.updated = datetime.datetime.now()

    def update_values(self):
        while True:
            time.sleep(5)
            self.cpu_count = psutil.cpu_count()
            self.cpu_percent = psutil.cpu_percent(0.0)
            self.cpu_freq = psutil.cpu_freq()
            self.cpu_average = psutil.getloadavg()
            self.virt_mem = psutil.virtual_memory()
            self.temp_sensors = psutil.sensors_temperatures()
            self.disks = tuple(i for i in psutil.disk_partitions() \
                            if i.fstype in self.fs and \
                            i.mountpoint.split('/')[-1] not in self.mp_excluded)
            self.disks_usage = {disk.mountpoint: psutil.disk_usage(disk.mountpoint) for disk in self.disks}
