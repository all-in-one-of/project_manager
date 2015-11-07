from shotgun_api3 import Shotgun

url = "http://nad.shotgunstudio.com"
script_name = "ThibaultGenericScript"
key = "e014f12acda4074561022f165e8cd1913af2ba4903324a72edbb21430abbb2dc"
project_id = 146 # Demo Project

sg = Shotgun(url, script_name, key)

filename = "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/mod/.thumb/banc_02_full.jpg"
result = sg.upload("Version",1048,filename,"sg_uploaded_movie")




my_local_file = {
    'attachment_links': [{'type':'Version','id':1048}],
    'project': {'type':'Project','id':146}
    }


asset = sg.find_one("Asset", [["code","is","afficheOeuvre"]], ["code"])

sg_user = sg.find_one('HumanUser', [['login', 'is', "houdon.thibault"]])
data = {
    'project': {'type':'Project','id':project_id},
    'note_links': [asset],
    'user': sg_user,
    'content':'Test',
    'subject':"Thibault's Note on afficheOeuvre"
    }

sg.create("Note", data)

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


