#!/usr/bin/env python
# coding=utf-8

import requests
import os

values = {"a": "nadupdate@yahoo.com", "b": "axc4b2c"}

request = requests.post('https://api.frame.io/login', params=values)
request = request.json()

user_id = str(request["x"])
token = str(request["y"])
messages = request["messages"]

values = {"mid": user_id, "t": token}

request = requests.post('https://api.frame.io/users/' + user_id + '/data', params=values)
request = request.json()

projects = request["user"]["teams"][0]["projects"][0]
project_id = str(projects["id"])
root_folder_key = str(projects["root_folder_key"])

file_path = "H:/01-NAD/testframe.mp4"
file_size = os.path.getsize(file_path)
max_bytes  = 50000000

# determine the number of file parts
part_number = file_size / max_bytes
if (file_size % max_bytes) > 0 :
  part_number = part_number + 1


values = {"mid":user_id,"t":token,"aid":project_id,"file_references":{ "0":{
                            "name":"testframe.mp4",
                            "filetype": "application/octet-stream",
                            "filesize": str(int(file_size)),
                            "detail":"10 MB",
                            "frontend_id":"test",
                            "is_multipart":"true",
                            "parts":str(part_number)}}}



request = requests.post('https://api.frame.io/folders/' + root_folder_key + '/file_references', params=values)
print(request.text)
# request = request.json()


