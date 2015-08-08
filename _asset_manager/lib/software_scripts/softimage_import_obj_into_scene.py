xsi = Application

def import_obj(file_path, obj_path):


    Application.OpenScene(file_path, "", "")

    Application.ObjImport(obj_path, 1, 0, False, True, False, True)

    Application.SaveScene()