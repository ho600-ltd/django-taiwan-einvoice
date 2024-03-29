#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import LCD_1in44
import LCD_Config

import RPi.GPIO as GPIO

import django, os, time, logging, sys, netifaces, urllib.request, datetime, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageColor
from libs import get_tea_web_name, get_public_ip, get_eths, get_boot_seed, get_hour_minute

logging.basicConfig(
)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

PWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PWD)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escpos_web.settings")
django.setup()


def info_block(lg, draw):
    height = 110
    name = get_tea_web_name()
    draw.text((80 - 10 * len(name), height), name, font=NAME_FONT, fill=0)
    height -= 20
    draw.text((20, height), "Pass key:", font=PASS_KEY_FONT, fill=0)
    height -= 28
    draw.text((5, height), get_boot_seed(), font=SEED_INFO_FONT, fill=0)

    height -= 12
    public_ip = get_public_ip()
    lg.info(public_ip)
    draw.text((50, height), "聯外 IP:", font=IP_INFO_FONT, fill=0)
    height -= 10
    draw.text((5, height), public_ip, font=IP_INFO_FONT, fill=0)

    height -= 13
    draw.text((5, height), "啟動時間:{}".format(get_hour_minute()), font=IP_INFO_FONT, fill=0)
    height -= 3

    eths = get_eths()
    lg.info(eths)
    for e in eths:
        height -= 10
        draw.text((70, height), e[0], font=IP_INFO_FONT, fill=0)
        draw.rectangle((1, height, 70, height+10), outline=0, fill=0xffffff) #A button filled
        draw.text((5, height), e[1], font=IP_INFO_FONT, fill=0x0000ff)


lg = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
lg.setLevel('INFO')
lg.addHandler(consoleHandler)

try:
    TTF_PATH = sys.argv[1]
except:
    TTF_PATH = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
MENU_FONT0 = ImageFont.truetype(TTF_PATH, 18)
MENU_FONT = ImageFont.TransposedFont(MENU_FONT0, orientation=Image.Transpose.ROTATE_180)
NAME_FONT0 = ImageFont.truetype(TTF_PATH, 12)
NAME_FONT = ImageFont.TransposedFont(NAME_FONT0, orientation=Image.Transpose.ROTATE_180)
PASS_KEY_FONT0 = ImageFont.truetype(TTF_PATH, 16)
PASS_KEY_FONT = ImageFont.TransposedFont(PASS_KEY_FONT0, orientation=Image.Transpose.ROTATE_180)
IP_INFO_FONT0 = ImageFont.truetype(TTF_PATH, 10)
IP_INFO_FONT = ImageFont.TransposedFont(IP_INFO_FONT0, orientation=Image.Transpose.ROTATE_180)
SEED_INFO_FONT0 = ImageFont.truetype(TTF_PATH, 32)
SEED_INFO_FONT = ImageFont.TransposedFont(SEED_INFO_FONT0, orientation=Image.Transpose.ROTATE_180)

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

#init GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.cleanup()
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
WIDTH = 128
HEIGHT = 128
BACKGROUND_COLOR = 0x00ff00
RESET_BACKGROUND_COLOR = 0xe5e5e5
KEY_PIN_COLOR = 0xffffff
KEY1_PIN_PRESS_COLOR = 0x0000ff
KEY2_PIN_PRESS_COLOR = 0xffef00
KEY3_PIN_PRESS_COLOR = 0xff0000

KEY1_PIN_SHAPE = (120, 60, 100, 40)
KEY1_PIN_FONT_POSITION = (101, 42)
KEY1_PIN_TEXT = '重'

KEY2_PIN_SHAPE = (120, 90, 100, 70)
KEY2_PIN_FONT_POSITION = (101, 71)
KEY2_PIN_TEXT = '關'

KEY3_PIN_SHAPE = (120, 120, 100, 100)
KEY3_PIN_FONT_POSITION = (101, 102)
KEY3_PIN_TEXT = '整'

PRESS_PIN_SHAPE =  (108, 10, 118, 20) # (20, 22, 40, 40)
LEFT_PIN_SHAPE =  [(98, 15), (107, 10), (107, 20)] # [(0, 30), (18, 21), (18, 41)]
UP_PIN_SHAPE =    [(108, 9), (113, 0), (118, 9)] # [(20, 20), (30, 2), (40, 20)]
RIGHT_PIN_SHAPE = [(128, 15), (119, 10), (119, 20)] # [(60, 30), (42, 21), (42, 41)]
DOWN_PIN_SHAPE =  [(113, 30), (118, 21), (108, 21)] # [(30, 60), (40, 42), (20, 42)]

image = Image.new('RGB', (WIDTH, HEIGHT))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=BACKGROUND_COLOR)
disp.LCD_ShowImage(image, 0, 0)


def reset_image(lg, draw, texts):
    image = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=RESET_BACKGROUND_COLOR)
    w, h = 0, 80
    for text in texts:
        draw.text((w, h), text, font=IP_INFO_FONT)
        h -= 15
    disp.LCD_ShowImage(image, 0, 0)


def save_image_ppm(lg, draw):
    draw.im.save_ppm('.menu.ppm')
    im = Image.open('.menu.ppm')
    im2 = im.rotate(180)
    im2.save('.menu.png')
    lg.info('saved .menu.png')


KEY_PRESS = None
KEY_PRESS_TIME = time.time()
KEY_PRESS_DURATION = 5 # seconds

info_block(lg, draw)

# try:
while 1:
    now = time.time()
    if now - KEY_PRESS_TIME > KEY_PRESS_DURATION:
        KEY_PRESS = None

    # with canvas(device) as draw:
    if GPIO.input(KEY_PRESS_PIN) == 0: # pressed
        draw.rectangle(PRESS_PIN_SHAPE, outline=255, fill=0xff00) #center 
        lg.info("center")
        if KEY_PRESS and 'KEY1' == KEY_PRESS:
            reset_image(lg, draw, ['', '', '重開機...'])
            subprocess.run(['reboot'])
            break
        elif KEY_PRESS and 'KEY2' == KEY_PRESS:
            reset_image(lg, draw, ['關機中...', '請在螢幕全變白色後', '再等待 10 秒，才斷電'])
            subprocess.run(['shutdown', '-h', '+0'])
            break
        elif KEY_PRESS and 'KEY3' == KEY_PRESS:
            reset_image(lg, draw, ['', '', '重整服務中...'])
            subprocess.run(['supervisorctl', 'restart', 'all'])
            break

    else: # released
        draw.rectangle(PRESS_PIN_SHAPE, outline=255, fill=0) #center filled
        
    if GPIO.input(KEY_LEFT_PIN) == 0: # pressed
        draw.polygon(LEFT_PIN_SHAPE, outline=255, fill=0xff00)  #left
        lg.info("left")
        save_image_ppm(lg, draw)
    else: # released
        draw.polygon(LEFT_PIN_SHAPE, outline=255, fill=0)  #left filled
        
    if GPIO.input(KEY_UP_PIN) == 0: # pressed
        draw.polygon(UP_PIN_SHAPE, outline=255, fill=0xff00)  #Up        
        lg.info("Up")
    else: # released
        draw.polygon(UP_PIN_SHAPE, outline=255, fill=0)  #Up filled
        
    if GPIO.input(KEY_RIGHT_PIN) == 0: # pressed
        draw.polygon(RIGHT_PIN_SHAPE, outline=255, fill=0xff00) #right
        lg.info("right")
        KEY_PRESS_TIME = 0
        KEY_PRESS = None
    else: # released
        draw.polygon(RIGHT_PIN_SHAPE, outline=255, fill=0x00ff) #right filled       
        
    if GPIO.input(KEY_DOWN_PIN) == 0: # pressed
        draw.polygon(DOWN_PIN_SHAPE, outline=255, fill=0xff00) #down
        lg.info("down")
    else: # released
        draw.polygon(DOWN_PIN_SHAPE, outline=255, fill=0) #down filled
        
    if GPIO.input(KEY1_PIN) == 0 or ('KEY1' == KEY_PRESS and now - KEY_PRESS_TIME < KEY_PRESS_DURATION): # pressed
        if GPIO.input(KEY1_PIN) == 0:
            KEY_PRESS = 'KEY1'
            KEY_PRESS_TIME = time.time()
        draw.rectangle(KEY1_PIN_SHAPE, outline=255, fill=KEY1_PIN_PRESS_COLOR) #A button
        lg.info("KEY1")
    else: # released
        draw.rectangle(KEY1_PIN_SHAPE, outline=255, fill=KEY_PIN_COLOR) #A button filled
    draw.text(KEY1_PIN_FONT_POSITION, KEY1_PIN_TEXT, font=MENU_FONT, fill=0)
        
    if GPIO.input(KEY2_PIN) == 0 or ('KEY2' == KEY_PRESS and now - KEY_PRESS_TIME < KEY_PRESS_DURATION): # pressed
        if GPIO.input(KEY2_PIN) == 0:
            KEY_PRESS = 'KEY2'
            KEY_PRESS_TIME = time.time()
        draw.rectangle(KEY2_PIN_SHAPE, outline=255, fill=KEY2_PIN_PRESS_COLOR) #B button]
        lg.info("KEY2")
    else: # released
        draw.rectangle(KEY2_PIN_SHAPE, outline=255, fill=KEY_PIN_COLOR) #B button filled
    draw.text(KEY2_PIN_FONT_POSITION, KEY2_PIN_TEXT, font=MENU_FONT, fill=0)
        
    if GPIO.input(KEY3_PIN) == 0 or ('KEY3' == KEY_PRESS and now - KEY_PRESS_TIME < KEY_PRESS_DURATION): # pressed
        if GPIO.input(KEY3_PIN) == 0:
            KEY_PRESS = 'KEY3'
            KEY_PRESS_TIME = time.time()
        draw.rectangle(KEY3_PIN_SHAPE, outline=255, fill=KEY3_PIN_PRESS_COLOR) #A button
        lg.info("KEY3")
    else: # released
        draw.rectangle(KEY3_PIN_SHAPE, outline=255, fill=KEY_PIN_COLOR) #A button filled
    draw.text(KEY3_PIN_FONT_POSITION, KEY3_PIN_TEXT, font=MENU_FONT, fill=0)

    disp.LCD_ShowImage(image,0,0)
# except:
        # lg.info("except")
    # GPIO.cleanup()
