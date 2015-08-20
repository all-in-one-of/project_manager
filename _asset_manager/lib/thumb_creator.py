#!/usr/bin/env python
# coding=utf-8

from PIL import Image, ImageDraw, ImageFont
import sys

text = sys.argv[-4]
asset_img = sys.argv[-3]
export_path = sys.argv[-2]
font_path = sys.argv[-1]

W, H = (164, 164)
img = Image.open(asset_img)
background = Image.new('RGBA', (W, H), (255, 255, 255, 0))
background.paste(img, (18, 18))
draw = ImageDraw.Draw(background)


background.save(export_path)

print("end")
