import bpy
import math
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Material definitions
def make_mat(name, color, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Metallic'].default_value = metallic
    return mat

mat_trunk = make_mat('Pine_Trunk', (0.1, 0.05, 0.02, 1))
mat_deck = make_mat('Cedar_Planks', (0.7, 0.45, 0.2, 1))
mat_rope = make_mat('Suspension_Bridge', (0.8, 0.7, 0.6, 1))
mat_text = make_mat('Dimension_Text', (1.0, 0.8, 0.0, 1))
mat_ground = make_mat('Ground_Lidar', (0.25, 0.2, 0.15, 1)) # Dirt/Needles color
mat_yard = make_mat('Yard_Grass', (0.15, 0.3, 0.1, 1))
mat_fence = make_mat('Wood_Fence', (0.4, 0.3, 0.2, 1))

# 1. Load Ground STL Scan (The central 19x19ft dirt mound where the main tree is)
stl_path = '/home/lanoitcif/treehouse/stl_files/grounds.stl'
if os.path.exists(stl_path):
    bpy.ops.import_mesh.stl(filepath=stl_path)
    grounds = bpy.context.active_object
    grounds.rotation_euler[0] = -math.radians(90)
    grounds.data.materials.append(mat_ground)

# 1.5 Add large Yard surroundings visible in images
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -2.5)) # Slightly below the high point of STL
yard = bpy.context.active_object
yard.data.materials.append(mat_yard)

# Add split-rail fence representation behind the trees (e.g. at Y=15) based on site images
for x in range(-40, 41, 8):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=4, location=(x, 18, -0.5))
    bpy.context.active_object.data.materials.append(mat_fence)
# Rails
for z in [0.5, 1.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=80, location=(0, 18, z))
    bpy.context.active_object.rotation_euler[1] = math.radians(90)
    bpy.context.active_object.data.materials.append(mat_fence)

# Helper to build a platform
def build_platform(name, loc, radius, height):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=0.5, location=(loc[0], loc[1], height))
    plat = bpy.context.active_object
    plat.name = f"Platform_{name}"
    plat.data.materials.append(mat_deck)
    
    bpy.ops.object.text_add(location=(loc[0]-radius+1, loc[1]-radius-1, height+1))
    txt = bpy.context.active_object
    txt.data.body = f"{name}\\nElev: +{height}ft"
    txt.data.extrude = 0.1
    txt.rotation_euler = (math.radians(60), 0, 0)
    txt.scale = (2.5, 2.5, 2.5)
    txt.data.materials.append(mat_text)

# Helper to build a suspension bridge
def build_bridge(p1_loc, p1_h, p2_loc, p2_h):
    dx = p2_loc[0] - p1_loc[0]
    dy = p2_loc[1] - p1_loc[1]
    dz = p2_h - p1_h
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    mx = (p1_loc[0] + p2_loc[0])/2
    my = (p1_loc[1] + p2_loc[1])/2
    mz = (p1_h + p2_h)/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mx, my, mz))
    bridge = bpy.context.active_object
    bridge.scale = (1.5, dist, 0.2)
    
    yaw = math.atan2(dy, dx) - math.pi/2
    pitch = -math.atan2(dz, math.sqrt(dx*dx + dy*dy))
    bridge.rotation_euler = (pitch, 0, yaw)
    bridge.data.materials.append(mat_rope)

    bpy.ops.object.text_add(location=(mx, my-2, mz+1.5))
    txt = bpy.context.active_object
    txt.data.body = f"Span: {round(dist, 1)}ft"
    txt.data.extrude = 0.1
    txt.rotation_euler = (math.radians(70), 0, yaw)
    txt.scale = (2.0, 2.0, 2.0)
    txt.data.materials.append(mat_text)

# 2. Define Trees with realistic layout relative to fence
trees = [
    ("Main_Alpha", (0, 0), 1.25),      # Dead center on STL mound
    ("Beta_Tree", (-12, 10), 1.0),     # Back Left, closer to fence
    ("Gamma_Tree", (12, 8), 1.1)       # Back Right
]

for name, loc, r in trees:
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=60, location=(loc[0], loc[1], 25))
    t = bpy.context.active_object
    t.name = name
    t.data.materials.append(mat_trunk)

# 3. Platforms
build_platform("Base_Camp", trees[0][1], 5.0, 15.0)
build_platform("Mid_Station", trees[2][1], 4.0, 20.0)
build_platform("Crows_Nest", trees[1][1], 4.0, 26.0)

# 4. Bridges
build_bridge(trees[0][1], 15.0, trees[2][1], 20.0)
build_bridge(trees[2][1], 20.0, trees[1][1], 26.0)
build_bridge(trees[1][1], 26.0, trees[0][1], 15.0)

# Save
bpy.ops.wm.save_as_mainfile(filepath="/home/lanoitcif/treehouse/Skyward_MultiTree.blend")

# 5. Render
bpy.ops.object.empty_add(location=(0, 6, 18))
target = bpy.context.active_object

bpy.ops.object.camera_add(location=(35, -45, 45))
cam = bpy.context.active_object
tt = cam.constraints.new(type='TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'
bpy.context.scene.camera = cam

bpy.ops.object.light_add(type='SUN', location=(10, -10, 50))
sun1 = bpy.context.active_object
sun1.data.energy = 5.0
sun1.rotation_euler = (math.radians(45), 0, math.radians(45))

bpy.ops.object.light_add(type='SUN', location=(-20, 20, 30))
sun2 = bpy.context.active_object
sun2.data.energy = 2.0
sun2.rotation_euler = (math.radians(-45), 0, math.radians(-135))

if not bpy.data.worlds:
    bpy.data.worlds.new("World")
world = bpy.data.worlds[0]
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (0.2, 0.3, 0.4, 1)
bpy.context.scene.world = world

bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.RenderSettings, 'engine') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/skywalk_iso.png'
bpy.ops.render.render(write_still=True)

cam.location = (0, 6, 75)
bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/skywalk_top.png'
bpy.ops.render.render(write_still=True)
