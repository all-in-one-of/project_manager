import bpy
import sys
print("1")
obj_path = sys.argv[-1].replace("\\", "/")
print("2")

items_to_delete = []
print("3")

for item in bpy.data.objects:
    items_to_delete.append(item.name)


print("4")
# select them only.
for object_name in items_to_delete:
    bpy.data.objects[object_name].select = True

print("5")
# remove all selected.
bpy.ops.object.delete()
print("6")

# remove the meshes, they have no users anymore.
for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)
print("7")

bpy.ops.import_scene.obj(filepath=obj_path, use_split_objects=True, use_split_groups=True)
for obj in bpy.context.selected_objects:
    obj.name = "OBJ"

print("8")
OBJ = bpy.data.objects["OBJ"]
bpy.context.scene.objects.active = bpy.data.objects["OBJ"]
try:
    bpy.ops.object.join()
except:
    pass
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

print("9")
# Determine OBJ dimensions
maxDimension = 5
scaleFactor = maxDimension / max(OBJ.dimensions)

print("10")
# Scale uniformly
OBJ.scale = (scaleFactor,scaleFactor,scaleFactor)

print("11")
# Center pivot
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')

print("12")
# Move object to origin
bpy.ops.object.location_clear()

print("13")
# Move mesh up by half of Z dimension
dimX = OBJ.dimensions[0]/2
dimY = OBJ.dimensions[1]/2
dimZ = OBJ.dimensions[2]/2
OBJ.location = (0,0,dimZ)
print("14")

bpy.ops.object.select_all(action='TOGGLE')
bpy.ops.object.shade_smooth()
bpy.ops.object.select_all(action='TOGGLE')
bpy.ops.object.shade_smooth()

print("15")
bpy.ops.export_scene.obj(filepath=obj_path, use_materials=False, use_mesh_modifiers=False, use_vertex_groups=True, use_blen_objects=False, group_by_object=True)
print("16")
