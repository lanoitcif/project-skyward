import bpy
import os
import math

# Load the file with the humans
bpy.ops.wm.open_mainfile(filepath="/home/lanoitcif/treehouse/Skyward_MultiTree.blend")

# 1. Switch to Cycles (CPU raytracing is robust in headless Linux environments)
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.cycles.use_denoising = True # Get a clean image quickly

# 2. Fix the lighting for Cycles
for obj in bpy.data.objects:
    if obj.type == 'LIGHT' and obj.data.type == 'SUN':
        obj.data.energy = 2.0 # Eevee to Cycles conversion often needs lower energy
        obj.data.angle = math.radians(5) # Soft realistic shadows

# 3. Ensure a bright physical sky background
if not bpy.data.worlds:
    bpy.data.worlds.new("World")
world = bpy.data.worlds[0]
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (0.6, 0.8, 0.95, 1.0) # Bright daytime sky blue
    bg.inputs[1].default_value = 1.0 # Strength
bpy.context.scene.world = world

# 4. Ensure Camera is pointing at the center of the triad (Z=15)
cam = bpy.data.objects.get("Camera")
if not cam:
    bpy.ops.object.camera_add(location=(45, -55, 45))
    cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Set up TrackTo if it doesn't exist
if len(cam.constraints) == 0:
    bpy.ops.object.empty_add(location=(0, 6, 20)) # Focus on Mid Station/Base Camp area
    target = bpy.context.active_object
    tt = cam.constraints.new(type='TRACK_TO')
    tt.target = target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

# Give camera a slightly wider lens for the isometric shot so nothing is cut off
cam.data.lens = 35 

# Render ISO
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/skywalk_iso.png'
bpy.ops.render.render(write_still=True)
print("Finished ISO Cycles Render")

# Render TOP
cam.location = (0, 6, 85) # High enough to see all 3 trees and the fences
bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/skywalk_top.png'
bpy.ops.render.render(write_still=True)
print("Finished Top Cycles Render")
