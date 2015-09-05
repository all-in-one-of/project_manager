xsi = Application

def export_obj(file_path, export_path):
    xsi.OpenScene(file_path, "", "")

    try:
        xsi.SelectObj("output", "", "")
    except:
        xsi.selectAll()
    xsi.ObjExport(export_path, "", "", "", "", "", "", "", "", "", 0, False, False, "", False)