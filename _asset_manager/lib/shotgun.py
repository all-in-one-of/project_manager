from shotgun_api3 import Shotgun

url = "http://nad.shotgunstudio.com"
script_name = "ThibaultGenericScript"
key = "e014f12acda4074561022f165e8cd1913af2ba4903324a72edbb21430abbb2dc"
project_id = 146 # Demo Project

sg = Shotgun(url, script_name, key)

# user = sg.find_one('HumanUser', [['login', 'is', 'houdon.thibault']])
# lion = sg.find_one("Asset", [["code","is","lion"]])

sg_version = sg.find('Version', [["code","contains","vaseOriental_"]], ["code"])
versions = [version["code"] for version in sg_version]


if len(versions) == 0:
    last_version_number = "0001"
else:
    last_version = sorted(versions)[-1]
    last_version_number = str(int(last_version.split("_")[-1]) + 1).zfill(4)


# data = {
#    'project': {'type':'Project','id':project_id},
#     'code':'Lion',
#    'entity': lion,
#    'user': user,
#     'image':'Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/mod/.thumb/blocCadre_01_full.jpg'
#    }

#version = sg.create("Version", data)


#sg.upload("Version", version["id"], "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/mod/.thumb/blocCadre_01_full.jpg", "image", "Test")


# data = {
#     'project': {'type':'Project','id':project_id},
#     'code':'Test',
#     'description':'Finir le modeling du lion',
#     'sg_status_list':'ip',
#     'shots':xxxx_shot
#     }


#data = {
#    'project': {'type':'Project','id':project_id},
#    'content':'Finir le modeling du lion'
#    }



#sg.create("Task", data)

# maison = sg.find_one("Asset", [["code", "is", "maison"]])
# asset_id = 1339
# thumbnail = "Z:/Groupes-cours/NAND999-A15-N01/pub/assets/mod/.thumb/pub_cty_xxxx_mod_abribus_01_full.jpg"
# sg.upload_thumbnail("Asset",asset_id,thumbnail)


