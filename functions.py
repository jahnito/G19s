from display_g19s import Display
from PIL import Image, ImageDraw, ImageFont
from psutil import cpu_percent, getloadavg, cpu_count, virtual_memory
from psutil import sensors_temperatures, pids, boot_time
import datetime
import time
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


def show_clock_image(color=(0, 51, 102),
                          font='/usr/share/fonts/truetype/liberation/'
                          'LiberationMono-Regular.ttf') -> Image.Image:
    '''
    Creating a display image - time
    '''
    sec = datetime.datetime.now().second
    img = Image.new('RGB', (320, 240), color)
    draw = ImageDraw.Draw(img)
    draw.circle((160, 120), 100, outline='red')
    draw.line((160, 120, sec + sec, sec + sec), fill='red', width=2)
    draw.circle((160, 120), 10, fill=color, outline=color)
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
        img = show_clock_image()
        data = Display.convert_image_to_frame(img)
        display.write_frame(data)
        time.sleep(1)
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