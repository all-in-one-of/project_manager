#!/usr/bin/env python
# coding=utf-8

from shotgun_api3 import Shotgun

url = "http://nad.shotgunstudio.com"
script_name = "ThibaultGenericScript"
key = "e014f12acda4074561022f165e8cd1913af2ba4903324a72edbb21430abbb2dc"
project_id = 146

sg = Shotgun(url, script_name, key)

# Create new asset
asset_name = "tree2"
data = {'project': {'type': 'Project', 'id': 146}, 'code':asset_name, "sequences":"mus"}
sg.create("Asset", data)



# Upload thumbnail to asset
#maison = sg.find_one("Asset", [["code", "is", "maison"]])
#asset_id = 1339
#thumbnail = "Z:/Groupes-cours/NAND999-A15-N01/pub/assets/mod/.thumb/pub_cty_xxxx_mod_abribus_01_full.jpg"
#sg.upload_thumbnail("Asset",asset_id,thumbnail)
