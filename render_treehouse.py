import bpy
import math

try:
    # Load the file
    bpy.ops.wm.open_mainfile(filepath="/home/lanoitcif/treehouse/Project_Skyward.blend")
    print("Successfully opened Project_Skyward.blend")

    # Add an empty at center to track to (Z=8 for deck height)
    bpy.ops.object.empty_add(location=(0, 0, 8))
    target = bpy.context.active_object

    # Add a camera
    bpy.ops.object.camera_add(location=(25, -25, 25))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    # Add Track To constraint
    tt = cam.constraints.new(type='TRACK_TO')
    tt.target = target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    # Setup lighting (Sun lights for EEVEE)
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 30))
    sun1 = bpy.context.active_object
    sun1.data.energy = 5.0
    sun1.rotation_euler = (math.radians(45), 0, math.radians(45))

    bpy.ops.object.light_add(type='SUN', location=(-20, 20, 20))
    sun2 = bpy.context.active_object
    sun2.data.energy = 2.0
    sun2.rotation_euler = (math.radians(-45), 0, math.radians(-135))

    # Setup render settings
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.RenderSettings, 'engine') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    
    # Optional: World background lighting
    if not bpy.data.worlds:
        bpy.data.worlds.new("World")
    world = bpy.data.worlds[0]
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (0.6, 0.7, 0.8, 1) # Sky blue
        bg.inputs[1].default_value = 1.0
    bpy.context.scene.world = world

    # Render ISO
    iso_path = '/home/lanoitcif/treehouse/render_iso.png'
    bpy.context.scene.render.filepath = iso_path
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {iso_path}")

    # Render Top-Down
    cam.location = (0, 0, 35)
    top_path = '/home/lanoitcif/treehouse/render_top.png'
    bpy.context.scene.render.filepath = top_path
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {top_path}")

except Exception as e:
    print(f"Error during rendering: {e}")
