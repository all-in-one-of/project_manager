import hou
import sys

file_path = sys.argv[-1].replace("\\", "/")
hou.hipFile.load(file_path)

loaded_assets = hou.hda.loadedFiles()
for asset in loaded_assets:
    if "assets" in asset:
        if not "shd" in asset:
            print(asset)

