import bpy
import math
import os

bpy.ops.wm.open_mainfile(filepath="/home/lanoitcif/treehouse/Skyward_MultiTree.blend")

human_path = '/home/lanoitcif/treehouse/human.obj'

def create_human(loc, rot_z):
    if os.path.exists(human_path):
        if hasattr(bpy.ops.wm, 'obj_import'):
            bpy.ops.wm.obj_import(filepath=human_path)
        else:
            bpy.ops.import_scene.obj(filepath=human_path)
            
        human = bpy.context.selected_objects[0]
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
        dim_z = human.dimensions.z if human.dimensions.z > 0 else 1
        scale_f = 5.0 / dim_z 
        human.scale = (scale_f, scale_f, scale_f)
        human.rotation_euler[2] = rot_z
        
        bpy.context.view_layer.update()
        z_offset = human.bound_box[0][2] * scale_f 
        human.location = (loc[0], loc[1], loc[2] - z_offset)
        
        mat = bpy.data.materials.new(name="Human_Scale_Mat")
        mat.use_nodes = True
        principled = mat.node_tree.nodes.get('Principled BSDF')
        if principled:
            principled.inputs['Base Color'].default_value = (0.2, 0.5, 0.9, 1)
        human.data.materials.append(mat)
    else:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=5.0, location=(loc[0], loc[1], loc[2] + 2.5))
        human = bpy.context.active_object
        
    human.name = "Scale_Child_13yo_5ft"

create_human((0, -2, 15.25), math.radians(45))
create_human((-12, 8, 26.25), math.radians(-45))
create_human((12, 8, 20.25), math.radians(180))

bpy.ops.wm.save_mainfile()

# Ensure camera is set
cam = bpy.data.objects.get("Camera")
if not cam:
    bpy.ops.object.camera_add(location=(40, -45, 50))
    cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Re-render ISO
bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/skywalk_iso.png'
bpy.ops.render.render(write_still=True)

# Re-render Top
cam.location = (0, 6, 75)
cam.rotation_euler = (0, 0, 0)
bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/skywalk_top.png'
bpy.ops.render.render(write_still=True)

print("SUCCESS: Humans added and re-rendered.")
