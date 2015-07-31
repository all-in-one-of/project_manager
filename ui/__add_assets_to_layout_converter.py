import sys
import subprocess
import os
import time
import re


def convert_ui():
    ''' Drag an drop a file on the QtUiConvert.bat file associated with this python script to convert a .ui file to a .py file using pyuic
    '''

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    ui_path = cur_dir + "\\add_assets_to_layout.ui"
    
    window_tmp_path = cur_dir + "\\add_assets_to_layout_tmp.py"

    # Check wether or not a file was dropped on the .py file
    if len(sys.argv) < 2:
        script_path = ui_path
    else:
        script_path = sys.argv[1] # Get path of dropped file

    # Converts the .ui file to a temp .py file
    subprocess.Popen(["python.exe", "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\WinPython\\python-2.7.9.amd64\\Lib\\site-packages\\PyQt4\\uic\\pyuic.py", ui_path, "-o",
                      window_tmp_path, "-x"])

    time.sleep(0.5)

    # Retrieve all lines from converted python file in tmp_file list
    tmp_file = []
    with open(window_tmp_path, "r") as f:
        for line in f:
            tmp_file.append(line)

    f.close()



    line_to_find = "QtCore.QMetaObject.connectSlotsByName(Form)"
    match = False # This variable is set to true when line_to_find is found in the file

    # Delete old ui (the python one) file and create a new file "add_assets_to_layout.py"
    os.remove(cur_dir + "\\add_assets_to_layout.py")
    f = open(cur_dir + "\\add_assets_to_layout.py", "a")
    
    # Loop over each line and write "return Form" when the line_to_find is found. Otherwise just write each line
    # exactly the same
    for line in tmp_file:
        if match:
            f.write("        \n")
            f.write("        return Form\n")
            match = False
        if line_to_find in line:  # if string is found, then set match to True
            f.write(line)
            match = True
        else:
            f.write(line)

    f.close

    os.remove(window_tmp_path)

if __name__ == "__main__":
    convert_ui()
