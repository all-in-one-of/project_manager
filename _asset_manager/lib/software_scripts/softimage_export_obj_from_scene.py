def export_obj(file_path, export_path):
    Application.OpenScene(file_path, "", "")

    try:
        Application.SelectObj("output", "BRANCH", "")
    except:
        Application.selectAll()

    Application.ObjExport(export_path, "", "", "", "", "", "", "", "", "", 0, False, False, "", False)