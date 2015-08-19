#!/usr/bin/env python
# coding=utf-8

import requests
import os
import urlparse
from urllib2 import Request, urlopen
import json

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

file_path = "H:/01-NAD/test.mov"
file_size = os.path.getsize(file_path)
max_bytes  = 50000000

# determine the number of file parts
part_number = file_size / max_bytes
if (file_size % max_bytes) > 0 :
  part_number = part_number + 1




values = {"mid":user_id,"t":token,"aid":project_id,"file_references":{ "0":{
                            "name":"test.mp4",
                            "filetype": "application/octet-stream",
                            "filesize": str(int(file_size)),
                            "detail":"115 MB",
                            "frontend_id":"test",
                            "is_multipart":"true",
                            "parts":str(part_number)}}}



request = requests.post('https://api.frame.io/folders/' + root_folder_key + '/file_references', json=values)
request = request.json()
upload_urls = request["file_references"][0]["multipart_urls"]
file_ref_id = str(request["file_references"][0]["id"])


for i, url in enumerate(upload_urls):
    data_offset = i * max_bytes
    data_size = max_bytes
    if ((i+1) == len(upload_urls)):
      data_size = file_size - data_offset # determine the size for the last part

    f = open(file_path, 'rb')
    f.seek(data_offset)       # go to Nth byte in file
    data = f.read(data_size)  # read bytes

    file_dic = {"file": data}
    headers = {'Content-Type': 'application/octet-stream', 'x-amz-acl': 'private'}
    r = requests.put(urlparse.unquote(url), data=file_dic, headers=headers)

    # when upload succeeds, close file in order to free memory
    f.close()

    values = {"part_num":str(i), "mid": user_id, "t": token, "aid": project_id}
    request = requests.post('https://api.frame.io/file_references/' + file_ref_id + '/part_complete', json=values)
    print(request.text)

values = {"mid": user_id, "t": token, "aid": project_id, "upload_id":"dummy","num_parts":"dummy"}
request = requests.post("https://api.frame.io/file_references/" + file_ref_id + "/merge_parts", json=values)
print(request.text)

values = {"mid":user_id, "t":token, "aid":project_id, "process":"new-upload", "file_reference_id": file_ref_id}
request = requests.post('https://api.frame.io/worker/create_job', json=values)
print(request.text)





