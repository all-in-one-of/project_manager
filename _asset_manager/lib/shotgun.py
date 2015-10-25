from shotgun_api3 import Shotgun

url = "http://nad.shotgunstudio.com"
script_name = "ThibaultGenericScript"
key = "e014f12acda4074561022f165e8cd1913af2ba4903324a72edbb21430abbb2dc"
project_id = 146 # Demo Project

sg = Shotgun(url, script_name, key)

#test = sg.schema_field_read('Task', 'start_date')
#print(test)


# data = {
#     'project': {'type':'Project','id':project_id},
#     'code':'Test',
#     'description':'Finir le modeling du lion',
#     'sg_status_list':'ip',
#     'shots':xxxx_shot
#     }

#test = sg.schema_field_read("Asset", "shots")
#print(test)
# sg.create("Asset", data)

#task = sg.find_one("Task", [["content","is","test"]], ["start_date"])
#print(task)

#data = {
#    'project': {'type':'Project','id':project_id},
#    'content':'Finir le modeling du lion'
#    }



#sg.create("Task", data)

# maison = sg.find_one("Asset", [["code", "is", "maison"]])
# asset_id = 1339
# thumbnail = "Z:/Groupes-cours/NAND999-A15-N01/pub/assets/mod/.thumb/pub_cty_xxxx_mod_abribus_01_full.jpg"
# sg.upload_thumbnail("Asset",asset_id,thumbnail)


