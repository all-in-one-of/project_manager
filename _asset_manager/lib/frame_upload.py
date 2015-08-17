#!/usr/bin/env python
# coding=utf-8


import requests

values = {"a": "nadupdate@yahoo.com", "b": "axc4b2c"}

request = requests.post('https://api.frame.io/login', params=values)
request = request.json()

user_id = request["x"]
token = request["y"]
messages = request["messages"]


values = {"mid": user_id, "t": token}

request = requests.post('https://api.frame.io/users/' + user_id + '/data', params=values)
request = request.json()

#print(request["shared_projects"])
projects = request["user"]["teams"][0]["projects"][0]
project_id = projects["id"]



# values = {
# "mid": user_id,
# "t": token,
# "aid": project_id,
# "file_references":{ "0":{   "name":"myMovie.mov",           // the name of the file reference
#                             "metadata": "",
#                             "shared": "1",                  // optional, turn on sharing for this item
#                             "can_download" :"1",            // optional, allow download when sharing is enabled
#                             "password": "onetwo",           // optional, set a password if sharing is enabled
#                             "user_stars": { "6425154b-1ae7-42e5-9654-b6120c52fa6e": "3"  }, // star rating
#                             "filetype": "application/octet-stream",  // mime-type, if unknown "application/octet-stream"
#                             "filesize": "11248776",         // total file size in bytes
#                             "detail":"10 MB",               // pretty file size for details below the thumbnail in the project viewer
#                             "frontend_id":"my custom id",   // optional, custom field that is passed through to the response object. It is not saved. Feel free to pass in strings or objects that help you identify the returned file reference
#                             "is_multipart":"true",          // tell the server that it´s a multipart upload
#                             "parts":"4"                     // tell the server in how many parts you´re going to split and upload the file
#                         }
#                     //, "1":{"name":"...",...}
#                     }
# }
#
# headers = {
#   'Content-Type': 'application/json'
# }
# request = Request('https://api.frame.io/folders/' + project_id + '/file_references', data=values, headers=headers)
#
# response_body = urlopen(request).read()
# print response_body
