import bpy
import sys

obj_path = sys.argv[-1]

items_to_delete = []

for item in bpy.data.objects:
    items_to_delete.append(item.name)
    
    
# select them only.
for object_name in items_to_delete:
  bpy.data.objects[object_name].select = True

# remove all selected.
bpy.ops.object.delete()

# remove the meshes, they have no users anymore.
for item in bpy.data.meshes:
  bpy.data.meshes.remove(item)

bpy.ops.import_scene.obj(filepath=obj_path, use_split_objects=True, use_split_groups=True)
for obj in bpy.context.selected_objects:
    obj.name = "OBJ"
        
OBJ = bpy.data.objects["OBJ"]
bpy.context.scene.objects.active = bpy.data.objects["OBJ"]
bpy.ops.object.join()
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Determine OBJ dimensions
maxDimension = 5
scaleFactor = maxDimension / max(OBJ.dimensions)

# Scale uniformly
OBJ.scale = (scaleFactor,scaleFactor,scaleFactor)

# Center pivot
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')

# Move object to origin
bpy.ops.object.location_clear()

# Move mesh up by half of Z dimension
dimX = OBJ.dimensions[0]/2
dimY = OBJ.dimensions[1]/2
dimZ = OBJ.dimensions[2]/2
OBJ.location = (0,0,dimZ)

bpy.ops.object.select_all(action='TOGGLE')
bpy.ops.object.shade_smooth()
bpy.ops.object.select_all(action='TOGGLE')
bpy.ops.object.shade_smooth()

bpy.ops.export_scene.obj(filepath=export_path, use_materials=False, use_mesh_modifiers=False, use_vertex_groups=True, use_blen_objects=False, group_by_object=True)