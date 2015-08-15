import mari
import sys

project_name = sys.argv[-3]
project_version = sys.argv[-2]
mesh_path = sys.argv[-1].replace("\\", "/")

mari.projects.create(project_name + "_" + project_version, mesh_path, "")


