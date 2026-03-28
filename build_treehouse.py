import bpy
import math
import os

# Clear existing mesh objects from default scene
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Material definitions
def make_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        principled.inputs['Base Color'].default_value = color
    return mat

mat_trunk = make_material('Pine_Trunk', (0.1, 0.05, 0.02, 1))
mat_hardware = make_material('Steel_TABs', (0.5, 0.5, 0.5, 1))
mat_beam = make_material('Treated_Lumber', (0.4, 0.25, 0.1, 1))
mat_deck = make_material('Cedar_Planks', (0.7, 0.45, 0.2, 1))
mat_ground = make_material('Ground_Lidar', (0.2, 0.3, 0.2, 1))

# 1. Load Ground STL Scan
stl_path = '/home/lanoitcif/treehouse/stl_files/grounds.stl'
if os.path.exists(stl_path):
    bpy.ops.import_mesh.stl(filepath=stl_path)
    grounds = bpy.context.active_object
    grounds.name = 'GroundTopology'
    # Rotate X -90 to convert Z-up from many STL lidar tools
    grounds.rotation_euler[0] = -math.radians(90)
    if not grounds.data.materials:
        grounds.data.materials.append(mat_ground)

# Treehouse Configuration
deck_height = 8.0
tab_height = 8.0 - (9.25 / 12) # ~7.2ft to support joists at 8ft
trunk_radius = 1.25 # 30 inch diameter = 15 inch radius

# 2. Add Central Pine Trunk Representative Geometry
bpy.ops.mesh.primitive_cylinder_add(radius=trunk_radius, depth=30, location=(0, 0, 15))
trunk = bpy.context.active_object
trunk.name = 'Central_Trunk_Reference'
trunk.data.materials.append(mat_trunk)

# 3. Add TABs (Treehouse Attachment Bolts)
for i in range(4):
    angle = i * (math.pi/2) + (math.pi/4) # 45, 135, 225, 315 deg
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.5)
    tab = bpy.context.active_object
    tab.rotation_euler[1] = math.radians(90)
    tab.rotation_euler[2] = angle
    tab.location = (math.cos(angle)*(trunk_radius+0.5), math.sin(angle)*(trunk_radius+0.5), tab_height)
    tab.name = f'TAB_Boss_{i+1}'
    tab.data.materials.append(mat_hardware)

# 4. Construct Yoke Frame (Doubled 2x10s forming an 8x8 box)
yoke_len = 8.0
# We will just make a solid representative rim box
bpy.ops.mesh.primitive_cube_add(size=1)
yoke_left = bpy.context.active_object
yoke_left.scale = (0.25, yoke_len, 0.77)
yoke_left.location = (-yoke_len/2 + 0.125, 0, tab_height)
yoke_left.data.materials.append(mat_beam)

bpy.ops.mesh.primitive_cube_add(size=1)
yoke_right = bpy.context.active_object
yoke_right.scale = (0.25, yoke_len, 0.77)
yoke_right.location = (yoke_len/2 - 0.125, 0, tab_height)
yoke_right.data.materials.append(mat_beam)

bpy.ops.mesh.primitive_cube_add(size=1)
yoke_front = bpy.context.active_object
yoke_front.scale = (yoke_len, 0.25, 0.77)
yoke_front.location = (0, -yoke_len/2 + 0.125, tab_height)
yoke_front.data.materials.append(mat_beam)

bpy.ops.mesh.primitive_cube_add(size=1)
yoke_back = bpy.context.active_object
yoke_back.scale = (yoke_len, 0.25, 0.77)
yoke_back.location = (0, yoke_len/2 - 0.125, tab_height)
yoke_back.data.materials.append(mat_beam)

# 5. Knee Braces
brace_len = 5.6
for i in range(4):
    angle = i * (math.pi/2) + (math.pi/4)
    bpy.ops.mesh.primitive_cube_add(size=1)
    brace = bpy.context.active_object
    brace.scale = (0.33, brace_len, 0.5)
    
    # Position mid-way between trunk at Z=4 and yoke at Z=tab_height
    rad = trunk_radius + 0.2
    end_rad = yoke_len/2
    dx = math.cos(angle)
    dy = math.sin(angle)
    
    brace.location = (dx * ((rad + end_rad)/2), dy * ((rad + end_rad)/2), (4 + tab_height)/2)
    # Rotation math for 45 deg tilt toward center
    brace.rotation_euler[2] = angle
    brace.rotation_euler[1] = math.radians(45) if dx > 0 else math.radians(-45) # Simplified representation
    brace.data.materials.append(mat_beam)

# 6. Floor Joists (2x8s separated by 16" = 1.33ft)
joist_z = tab_height + 0.385 + 0.385
for j in range(-4, 5):
    bpy.ops.mesh.primitive_cube_add(size=1)
    joist = bpy.context.active_object
    joist.scale = (10.0, 0.125, 0.77)
    joist.location = (0, j * 1.33, joist_z)
    joist.data.materials.append(mat_beam)
    joist.name = f'Floor_Joist_{j}'

# 7. Decking Platform (10x10 with Hole)
deck_z = joist_z + 0.385 + 0.05
bpy.ops.mesh.primitive_cube_add(size=1)
deck = bpy.context.active_object
deck.scale = (10.0, 10.0, 0.1)
deck.location = (0, 0, deck_z)
deck.name = 'Cedar_Decking'
deck.data.materials.append(mat_deck)

# Cut tree hole using Boolean modifier
bpy.ops.mesh.primitive_cylinder_add(radius=trunk_radius + 0.25, depth=2, location=(0,0,deck_z))
cutter = bpy.context.active_object
cutter.hide_render = True
cutter.hide_viewport = True

mod = deck.modifiers.new("TreeClearance", 'BOOLEAN')
mod.object = cutter
mod.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = deck
bpy.ops.object.modifier_apply(modifier="TreeClearance")
bpy.data.objects.remove(cutter, do_unlink=True)

# 8. Save
bpy.ops.wm.save_as_mainfile(filepath="/home/lanoitcif/treehouse/Project_Skyward.blend")
print("SUCCESS: Treehouse architectural CAD fully generated and saved to /home/lanoitcif/treehouse/Project_Skyward.blend")
