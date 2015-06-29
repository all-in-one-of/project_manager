import sys
import subprocess
import os
import time
import re


def convert_ui():
    ''' Drag an drop a file on the QtUiConvert.bat file associated with this python script to convert a .ui file to a .py file using pyuic
    '''

    cur_dir = os.path.dirname(os.path.realpath(__file__)).replace("lib", "")
    ui_path = os.path.dirname(cur_dir) + "\\media\\main_window.ui"

    main_window_path = os.path.dirname(cur_dir) + "\\ui\\main_window_tmp.py"

    if len(sys.argv) < 2:
        script_path = "H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\media\\main_window.ui"
    else:
        script_path = sys.argv[1]

    subprocess.Popen(["python.exe", "H:\\01-NAD\\WinPython\\python-2.7.9.amd64\\Lib\\site-packages\\PyQt4\\uic\\pyuic.py", ui_path, "-o",
                      main_window_path, "-x"])

    time.sleep(0.5)

    # Retrieve all lines from converted python file in tmp_file list
    tmp_file = []
    with open(main_window_path, "r") as f:
        for line in f:
            tmp_file.append(line)

    f.close()

    match = False
    # Delete old file and create a new file "main_window"
    os.remove(os.path.dirname(cur_dir) + "\\ui\\main_window.py")
    f = open(os.path.dirname(cur_dir) + "\\ui\\main_window.py", "a")
    for i in tmp_file:
        if match:
            f.write("        \n")
            f.write("        return Form\n")
            match = False
        if "QtCore.QMetaObject.connectSlotsByName(Form)" in i:  # if string is found, then set match to True
            f.write(i)
            match = True
        else:
            f.write(i)

    f.close

    os.remove(main_window_path)


if __name__ == "__main__":
    convert_ui()
