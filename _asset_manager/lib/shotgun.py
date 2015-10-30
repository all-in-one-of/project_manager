from shotgun_api3 import Shotgun

url = "http://nad.shotgunstudio.com"
script_name = "ThibaultGenericScript"
key = "e014f12acda4074561022f165e8cd1913af2ba4903324a72edbb21430abbb2dc"
project_id = 146 # Demo Project

sg = Shotgun(url, script_name, key)
sg_asset = sg.find_one("Asset", [["code", "is", "ble"]])
mod_step = sg.find_one('Step', [['code','is','Modeling']])
cpt_step = sg.find_one('Step', [['code','is','Concept']])
tex_step = sg.find_one('Step', [['code','is','Texturing']])
shd_step = sg.find_one('Step', [['code','is','Shading']])

data = {'project': {'type':'Project','id':project_id}, 'content':'references', 'entity': sg_asset, 'step':cpt_step}
sg.create('Task', data)
data = {'project': {'type':'Project','id':project_id}, 'content':'concepts', 'entity': sg_asset, 'step':cpt_step}
sg.create('Task', data)
data = {'project': {'type':'Project','id':project_id}, 'content':'modeling', 'entity': sg_asset, 'step':mod_step}
sg.create('Task', data)
data = {'project': {'type':'Project','id':project_id}, 'content':'UV', 'entity': sg_asset, 'step':mod_step}
sg.create('Task', data)
data = {'project': {'type':'Project','id':project_id}, 'content':'texturing', 'entity': sg_asset, 'step':tex_step}
sg.create('Task', data)
data = {'project': {'type':'Project','id':project_id}, 'content':'shading', 'entity': sg_asset, 'step':shd_step}
sg.create('Task', data)



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


