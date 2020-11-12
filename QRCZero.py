#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import socket
import logging
import epd2in13b_V3
import time
from PIL import Image, ImageDraw, ImageFont
import pyqrcode

hostname = socket.gethostname()

ip_address_cmd = "hostname -I | awk '{print $1}'"
ip_address = os.popen(ip_address_cmd).read()

battery_cmd = "echo 'get battery' | nc -q 0 127.0.0.1 8423 | cut -d ' ' -f2"
battery = os.popen(battery_cmd).read()

url = pyqrcode.create('https://github.com/cpranzl/QRCZero')
url.png('code.png', quiet_zone=0)
QRCCodeBMP = Image.open('code.png')
QRCCodeBMP.save('code.bmp')


try:
    # Initialise the e-ink display
    epd = epd2in13b_V3.EPD()
    epd.init()
    epd.Clear()
    time.sleep(1)

    # Create the two images to display
    HBlackImage = Image.new('1', (epd.height, epd.width), 255)
    HRedImage = Image.new('1', (epd.height, epd.width), 255)

    # Get a drawing context
    drawblack = ImageDraw.Draw(HBlackImage)
    drawred = ImageDraw.Draw(HRedImage)

    # Load fonts
    font14 = ImageFont.truetype('font.ttc', 14)
    font20 = ImageFont.truetype('font.ttc', 20)

    # Draw a line of text starting 106 pixels from the left and 10
    # from the top in Red with font size 20
    drawblack.text(((epd.height // 2), 10), 'MSdT', font=font20, fill=0)
    drawblack.text(((epd.height // 2), 45), hostname, font=font14, fill=0)
    drawblack.text(((epd.height // 2), 60), ip_address, font=font14, fill=0)
    drawred.text(((epd.height // 2), 75), battery, font=font14, fill=0)

    # Scale the bmp and calculate offset to center it
    QRCodeBMP = Image.open('code.bmp')
    width, height = QRCodeBMP.size
    scale = epd.width // width
    QRCodeBMP = QRCodeBMP.resize((width * scale, height * scale))
    WOffset = (epd.width - (width * scale)) // 2
    HOffset = (epd.height - (height * scale)) // 2

    # Paste the bmp into the image
    HBlackImage.paste(QRCodeBMP, (WOffset, WOffset))

    # Display the images on the e-ink display
    epd.display(epd.getbuffer(HBlackImage), epd.getbuffer(HRedImage))
    time.sleep(2)

    # Power off the display
    epd.sleep()
    epd.Dev_exit()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13b_V3.epdconfig.module_exit()
    exit()
