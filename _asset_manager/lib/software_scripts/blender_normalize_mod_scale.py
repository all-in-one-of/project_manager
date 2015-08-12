import bpy
import sys

obj_path = sys.argv[-1]

bpy.ops.import_scene.obj(filepath=obj_path)
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

bpy.ops.export_scene.obj(filepath=obj_path, use_materials=False, use_mesh_modifiers=False, use_blen_objects=False, group_by_object=True)