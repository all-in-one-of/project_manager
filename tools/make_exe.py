import subprocess
import os
import shutil


cur_dir = os.path.dirname(os.path.realpath(__file__))

app_dir = os.path.dirname(os.path.realpath(__file__)).replace("lib", "") + "app.py"
bin_dir = os.path.dirname(os.path.realpath(__file__)).replace("lib", "") + "bin"
favicon_dir = os.path.dirname(os.path.realpath(__file__)).replace("lib", "") + "media\\favicon.ico"
 

subprocess.call(["pyinstaller", "--onefile", "--windowed", "--distpath", bin_dir, "-n", "Asset Manager", "-i", favicon_dir, app_dir])


shutil.rmtree(cur_dir + "\\build")
os.remove(cur_dir + "\\Asset Manager.spec")
