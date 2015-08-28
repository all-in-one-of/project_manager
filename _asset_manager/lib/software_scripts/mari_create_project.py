print("1")
import mari
import sys
project_name = sys.argv[-3]
project_version = sys.argv[-2]
mesh_path = sys.argv[-1].replace("\\\\", "/").replace("\\", "/")
print(project_name)
print(project_version)
print(mesh_path)

mari.projects.create(project_name + "_" + project_version, mesh_path, [], [])
print("2")
diffuse = mari.geo.current().currentChannel()
print("3")
mari.geo.current().removeChannel(diffuse)
print("4")

mari.projects.current().save()
print("5")
mari.projects.current().close()
print("6")

mari.app.exit()
print("7")








