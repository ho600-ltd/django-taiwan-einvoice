#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import LCD_1in44
import LCD_Config

import RPi.GPIO as GPIO

import time, logging
from PIL import Image, ImageDraw, ImageFont, ImageColor

logging.basicConfig()
lg = logging.getLogger(__name__)
lg.setLevel('INFO')

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
KEY_PIN_COLOR = 0xffffff
KEY1_PIN_PRESS_COLOR = 0x0000ff
KEY2_PIN_PRESS_COLOR = 0xffef00
KEY3_PIN_PRESS_COLOR = 0xff0000
KEY1_PIN_SHAPE = (120, 40, 100, 20)
KEY2_PIN_SHAPE = (120, 70, 100, 50)
KEY3_PIN_SHAPE = (120, 100, 100, 80)

image = Image.new('RGB', (WIDTH, HEIGHT))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=BACKGROUND_COLOR)
disp.LCD_ShowImage(image, 0, 0)

KEY_PRESS = None
KEY_PRESS_TIME = time.time()
KEY_PRESS_DURATION = 5 # seconds

# try:
while 1:
    now = time.time()
    if now - KEY_PRESS_TIME > KEY_PRESS_DURATION:
        KEY_PRESS = None

    # with canvas(device) as draw:
    if GPIO.input(KEY_UP_PIN) == 0: # button is released       
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)  #Up        
        lg.info("Up")
    else: # button is pressed:
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
        
    if GPIO.input(KEY_LEFT_PIN) == 0: # button is released
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)  #left
        lg.info("left")
    else: # button is pressed:       
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left filled
        
    if GPIO.input(KEY_RIGHT_PIN) == 0: # button is released
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00) #right
        lg.info("right")
    else: # button is pressed:
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right filled       
        
    if GPIO.input(KEY_DOWN_PIN) == 0: # button is released
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00) #down
        lg.info("down")
    else: # button is pressed:
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down filled
        
    if GPIO.input(KEY_PRESS_PIN) == 0: # button is released
        draw.rectangle((20, 22,40,40), outline=255, fill=0xff00) #center 
        lg.info("center")
    else: # button is pressed:
        draw.rectangle((20, 22,40,40), outline=255, fill=0) #center filled
        
    if GPIO.input(KEY1_PIN) == 0 or ('KEY1' == KEY_PRESS and now - KEY_PRESS_TIME < KEY_PRESS_DURATION): # button is released
        if GPIO.input(KEY1_PIN) == 0:
            KEY_PRESS = 'KEY1'
            KEY_PRESS_TIME = time.time()
        draw.rectangle(KEY1_PIN_SHAPE, outline=255, fill=KEY1_PIN_PRESS_COLOR) #A button
        lg.info("KEY1")
    else: # button is pressed:
        draw.rectangle(KEY1_PIN_SHAPE, outline=255, fill=KEY_PIN_COLOR) #A button filled
        
    if GPIO.input(KEY2_PIN) == 0 or ('KEY2' == KEY_PRESS and now - KEY_PRESS_TIME < KEY_PRESS_DURATION): # button is released
        if GPIO.input(KEY2_PIN) == 0:
            KEY_PRESS = 'KEY2'
            KEY_PRESS_TIME = time.time()
        draw.rectangle(KEY2_PIN_SHAPE, outline=255, fill=KEY2_PIN_PRESS_COLOR) #B button]
        lg.info("KEY2")
    else: # button is pressed:
        draw.rectangle(KEY2_PIN_SHAPE, outline=255, fill=KEY_PIN_COLOR) #B button filled
        
    if GPIO.input(KEY3_PIN) == 0 or ('KEY3' == KEY_PRESS and now - KEY_PRESS_TIME < KEY_PRESS_DURATION): # button is released
        if GPIO.input(KEY3_PIN) == 0:
            KEY_PRESS = 'KEY3'
            KEY_PRESS_TIME = time.time()
        draw.rectangle(KEY3_PIN_SHAPE, outline=255, fill=KEY3_PIN_PRESS_COLOR) #A button
        lg.info("KEY3")
    else: # button is pressed:
        draw.rectangle(KEY3_PIN_SHAPE, outline=255, fill=KEY_PIN_COLOR) #A button filled

    disp.LCD_ShowImage(image,0,0)
# except:
        # lg.info("except")
    # GPIO.cleanup()
