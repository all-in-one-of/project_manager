import mari

for proj in mari.projects.names():
    mari_project_name = str(proj)

new_version = mari_project_name.split("_")[-1]
new_version = str(int(new_version) + 1).zfill(2)
mari_new_project_name = mari_project_name.split("_")[0] + "_" + new_version
mari.projects.duplicate(mari_project_name)

for proj in mari.projects.names():
    if str(proj) != mari_project_name:
        mari.projects.rename(str(proj), mari_new_project_name)

