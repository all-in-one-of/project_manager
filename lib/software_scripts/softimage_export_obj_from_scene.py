xsi = Application

def export_obj(file_path, export_path):


    Application.OpenScene(file_path, "", "")

    xsi.selectAll()
    xsi.ObjExport(export_path, "", "", "", "", "", "", "", "", "", 0, False, False, "", False)