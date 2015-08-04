import bpy
import os, sys
import time

def generate():


    objFiles = sys.argv[-5]

    objFilename = objFiles


    if objFilename != None:
        bpy.ops.import_scene.obj(filepath=objFilename)


    for obj in bpy.context.selected_objects:
        obj.name = "OBJ"

    OBJ = bpy.data.objects["OBJ"]
    bpy.context.scene.objects.active = bpy.data.objects["OBJ"]
    bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # Determine OBJ dimensions
    maxDimension = 1.0
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

    # Manual adjustments to CAMERAS
    CAMERAS = bpy.data.objects["cameras"]
    scalevalue = 1
    camScale = 0.5+(dimX*scalevalue+dimY*scalevalue+dimZ*scalevalue)/3
    CAMERAS.scale = (camScale,camScale,camScale)
    CAMERAS.location = (0,0,dimZ)

    # Make smooth, add SubSurf modifier and increase subdivisions
    bpy.ops.object.shade_smooth()
    #bpy.ops.object.modifier_add(type='SUBSURF')
    #OBJ.modifiers["Subsurf"].levels = 3

    # Apply SubSurf modifier
    # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

    # Assign existing METAL material to OBJ (Commented out to preserve the .OBJ material colors that are defined in the optional .MTL file)
    # METAL = bpy.data.materials['metal']
    # bpy.context.active_object.active_material = METAL

    bpy.context.scene.cycles.samples = int(sys.argv[-3])
    bpy.context.scene.render.resolution_percentage = int(sys.argv[-2])


    if sys.argv[-4] == "full":
        bpy.context.scene.render.filepath = "C:\\Temp\\" + objFilename.replace("out.obj", sys.argv[-1] + "_full.jpg").split("\\")[-1]
        bpy.ops.render.render(write_still=True)

    elif sys.argv[-4] == "quad":
        for i in range(0, 360, 90):
            bpy.context.object.rotation_euler[2] = i * 0.0174532925
            bpy.context.scene.render.filepath = "C:\\Temp\\" + objFilename.replace("out.obj", sys.argv[-1] + "_" + str(i).zfill(3) + ".jpg").split("\\")[-1]
            bpy.ops.render.render(write_still=True)

    elif sys.argv[-4] == "turn":
        for i in range(0, 360, 15):
            bpy.context.object.rotation_euler[2] = i * 0.0174532925
            bpy.context.scene.render.filepath = "C:\\Temp\\" + objFilename.replace("out.obj", sys.argv[-1] + "_" + str(int(i/15)).zfill(2) + ".jpg").split("\\")[-1]
            bpy.ops.render.render(write_still=True)

    print("RENDER IS FINISHED")
