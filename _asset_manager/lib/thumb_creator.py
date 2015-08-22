#!/usr/bin/env python
# coding=utf-8

from PIL import Image, ImageDraw, ImageFont

image_path = "H:/01-NAD/nat_mus_0010_anm_statue_01_full.jpg"
img = Image.open(image_path)
w, h = img.size
background = Image.new('RGBA', (w, w), (255, 255, 255, 0))
background_w, background_h = background.size
background.paste(img, ((background_w - w)/2, (background_h - h)/2))
background.save(image_path.replace(".png", ".jpg"))

