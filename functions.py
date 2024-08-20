from display_g19s import Display
from PIL import Image, ImageDraw, ImageFont
from psutil import cpu_percent, getloadavg, cpu_count, virtual_memory
from psutil import sensors_temperatures, pids, boot_time
import datetime
import time
import math
import os

APPLET = 0


def show_hw_monitor_image(color=(0, 0, 0),
                          font='/usr/share/fonts/truetype/liberation/'
                          'LiberationMono-Regular.ttf') -> Image.Image:
    '''
    Creating a display image from hardware stats
    '''

    '''
    {'amdgpu': [shwtemp(label='edge', current=45.0, high=94.0, critical=94.0)],
    'k10temp': [shwtemp(label='', current=23.625, high=70.0, critical=90.0)]}
    '''
    vm = virtual_memory()
    uptime =  datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time())
    la = [str(round(i,2)) for i in getloadavg()]
    sensors = sensors_temperatures()
    text_header = 'PC Hardware Monitor'
    text = f'CPU\n\
  load({cpu_count()}): {cpu_percent()}%\n\
  load average: {" ".join(la)}\n\
  temp: {sensors["k10temp"][0].current}°\n\
RAM \n\
  used: {round(vm.used/1000000000, 2)}Gb ({vm.percent}%)\n\
  free: {round(vm.free/1000000000, 2)}Gb\n\
SYS\n\
  count procs: {len(pids())}\n\
  uptime: {uptime}\n\
'
    img = Image.new('RGB', (320, 240), color)
    fnt_header = ImageFont.truetype(font, 20)
    fnt_text = ImageFont.truetype(font, 13)
    draw = ImageDraw.Draw(img)
    x, y = 10, 10
    if text_header:
        draw.text((x + 30, y), text_header, font=fnt_header, fill=(0, 255, 255), align='right')
        draw.text((x, y + 25), text, font=fnt_text, fill=(0, 255, 255))
    else:
        draw.text((x, y), text, font=fnt_text, fill=(0, 255, 255))
    # img.save('show_hw_monitor_image.png', 'png')
    return img


def show_time_image(color=(0, 51, 102),
                          font='/usr/share/fonts/truetype/liberation/'
                          'LiberationMono-Regular.ttf') -> Image.Image:
    '''
    Creating a display image - time
    '''
    weekday = {'Sunday': 'Воскресенье',
               'Monday': 'Понедельник',
               'Tuesday': 'Ыторник',
               'Wednesday': 'среда',
               'Thursday': 'четверг',
               'Friday': 'пятница',
               'Saturday': 'суббота',
               }
    text_color = (249,185,88)
    img = Image.new('RGB', (320, 240), color)
    fnt_time = ImageFont.truetype(font, 48)
    fnt_date = ImageFont.truetype(font, 16)
    draw = ImageDraw.Draw(img)
    x, y = 10, 10
    text_time = datetime.datetime.now().strftime("%H:%M:%S")
    text_date = datetime.datetime.now().strftime("%d-%m-%Y")
    text_weekday = datetime.datetime.now().strftime("%A")
    draw.text((x + 30, y + 80), text_time, font=fnt_time, fill=text_color, align='right')
    draw.text((x + 30, y + 160), text_date, font=fnt_date, fill=text_color)
    draw.text((x + 30, y + 135), weekday[text_weekday], font=fnt_date, fill=text_color)
    return img


def create_min_sec_line(sec: int, width: int, point: tuple[int, int]):
    x, y = point
    if sec == 0:
        return (x, y - width)
    if sec == 30:
        return (x, y + width)
    if sec == 15:
        return (x + width, y)
    if sec == 45:
        return (x - width, y)
    if 0 < sec < 30:
        _y = width * math.cos(math.radians(sec * 6))
        _x = (width ** 2 - _y ** 2) ** 0.5 
        return (x + _x, y - _y)
    if 30 < sec < 60:
        _y = width * math.cos(math.radians(sec * -6))
        _x = (width ** 2 - _y ** 2) ** 0.5 
        return (x - _x, y - _y)


def create_hours_line(hours: int, minutes: int, width: int, point: tuple[int, int]):
    x, y = point
    degrees = (hours % 12 * 60 + minutes) // 2
    if degrees == 0:
        return (x, y - width)
    if degrees == 90:
        return (x + width, y)
    if degrees == 180:
        return (x, y + width)
    if degrees == 270:
        return (x - width, y)

    if 0 < degrees < 180:
        # ky = -1
        kx = 1
    elif 180 < degrees < 360:
        # ky = 1
        kx = -1
    if 90 < degrees < 270:
        ky = 1
    elif 270 < degrees < 360:
        ky = -1

    if 0 < degrees < 90 or 180 < degrees < 270:
        degrees %= 90
        _y = width * math.cos(math.radians(degrees))
        _x = (width ** 2 - _y ** 2) ** 0.5
        return (x + _x * kx, y + _y * ky)
    if 90 < degrees < 180 or 270 < degrees < 360:
        degrees %= 90
        _x = width * math.cos(math.radians(degrees))
        _y = (width ** 2 - _x ** 2) ** 0.5
        return (x + _x * kx, y + _y * ky)


def create_litle_risks(center: tuple[int, int], line: int):
    result = []
    x, y = center
    for i in (30, 60, -60, -30):
        if i > 0:
            ky = 1
        elif i < 0:
            ky = -1
        _y = line * math.cos(math.radians(i))
        _x = (line ** 2 - _y ** 2) ** 0.5
        result.append((x, y, x + _x, y - _y * ky))
    for i in (-30, -60, 60, 30):
        if i > 0:
            ky = 1
        elif i < 0:
            ky = -1
        _y = line * math.cos(math.radians(i))
        _x = (line ** 2 - _y ** 2) ** 0.5
        result.append((x, y, x - _x, y - _y * ky))
    return result


def show_clock_image(size, color=(0, 0, 0),
                          font='/usr/share/fonts/truetype/liberation/'
                          'LiberationMono-Regular.ttf') -> Image.Image:
    '''
    Creating a display image - time
    '''
    R = size
    risk = R * 0.9
    sec_line = risk
    min_line = sec_line * 0.8
    hour_line = sec_line * 0.55
    color_clock = 'yellow'
    center = (160, 120)
    sec = datetime.datetime.now().second
    min = datetime.datetime.now().minute
    hour = datetime.datetime.now().hour
    img = Image.new('RGB', (320, 240), color)
    draw = ImageDraw.Draw(img)
    draw.circle(center, R, outline=color_clock)
    for i in create_litle_risks(center, risk):
        draw.line(i, fill=color_clock, width=1)
    draw.circle(center, risk * 0.91, fill=color, outline=color)
    coordinates_sec = center + create_min_sec_line(sec, sec_line, center)
    coordinates_min = center + create_min_sec_line(min, min_line, center)
    coordinates_hour = center + create_hours_line(hour, min, hour_line, center)
    draw.line((center[0], center[1] + risk, center[0], center[1] - risk), fill=color_clock, width=2)
    draw.line((center[0] - risk, center[1], center[0] + risk, center[1]), fill=color_clock, width=2)
    draw.circle(center, risk * 0.8, fill=color, outline=color)
    draw.line(coordinates_sec, fill=color_clock, width=1)
    draw.line(coordinates_min, fill=color_clock, width=4)
    draw.line(coordinates_hour, fill=color_clock, width=6)
    draw.circle(center, risk * 0.05, fill=color_clock, outline=color)
    return img


def show_file_image(path_to_img: str) -> Image.Image:
    '''
    Creating a display image from image file
    '''
    img = Image.open(path_to_img)
    return img


def applet_hw(display: Display):
    while True:
        img = show_hw_monitor_image()
        data = Display.convert_image_to_frame(img)
        display.write_frame(data)
        time.sleep(5)
        if APPLET != 0:
            break


def applet_time(display: Display):
    while True:
        img = show_time_image()
        data = Display.convert_image_to_frame(img)
        display.write_frame(data)
        time.sleep(1)
        if APPLET != 1:
            break


def applet_clock(display: Display):
    while True:
        img = show_clock_image(105)
        data = Display.convert_image_to_frame(img)
        display.write_frame(data)
        time.sleep(0.5)
        if APPLET != 2:
            break


def applet_photo(display: Display):
    while True:
        img = show_time_image()
        data = Display.convert_image_to_frame(img)
        display.write_frame(data)
        time.sleep(1)
        if APPLET != 1:
            break
