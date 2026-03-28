import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)

# Delete default items
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Materials
def create_mat(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    principled = mat.node_tree.nodes['Principled BSDF']
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Roughness'].default_value = 0.8
    return mat

mat_ground = create_mat("Ground_STL", (0.05, 0.08, 0.04, 1))
mat_frame = create_mat("Treated_Frame", (0.15, 0.08, 0.04, 1))
mat_deck = create_mat("Cedar_Deck", (0.5, 0.25, 0.1, 1))
mat_steel = create_mat("Galvanized_Steel", (0.5, 0.5, 0.5, 1))
mat_steel.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 1.0
mat_steel.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.3

# 1. Load Cleaned STL
stl_path = '/home/lanoitcif/treehouse/stl_files/grounds_clean.stl'
bpy.ops.import_mesh.stl(filepath=stl_path)
grounds = bpy.context.selected_objects[0]
grounds.data.materials.append(mat_ground)

# Exact Tree Coordinates discovered mathematically
T1 = (1.71, 8.58)
T2 = (3.72, 8.48)
T3 = (2.76, 5.36)

# Extrapolate trees vertically to replace missing canopy data
mat_trunk = create_mat("Pine_Trunk", (0.1, 0.05, 0.02, 1))
mat_trunk.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.95
for tx, ty in [T1, T2, T3]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=25.0, location=(tx, ty, 10.0))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_trunk)

# Elevations (Ground is perfectly resting at Z=0)
Z1 = 5.0 # ~16ft up
Z2 = 7.0 # ~23ft up
Z3 = 9.0 # ~30ft up

inch = 0.0254
dim_2x8_w = 1.5 * inch
dim_2x8_h = 7.25 * inch

def build_pro_platform(name, cx, cy, cz, radius=1.6):
    yoke_len = radius * 2
    yoke_dist = 0.8 
    
    # 1. Yoke Beams
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy - yoke_dist, cz))
    yoke1 = bpy.context.active_object
    yoke1.scale = (yoke_len, 3*inch, 9.25*inch)
    yoke1.data.materials.append(mat_frame)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + yoke_dist, cz))
    yoke2 = bpy.context.active_object
    yoke2.scale = (yoke_len, 3*inch, 9.25*inch)
    yoke2.data.materials.append(mat_frame)
    
    # 2. Joists
    joist_spacing = 16 * inch
    num_joists = int(yoke_len / joist_spacing) + 1
    start_x = cx - yoke_len/2
    joist_z = cz + (9.25*inch)/2 + dim_2x8_h/2
    for i in range(num_joists):
        jx = start_x + (i * joist_spacing)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(jx, cy, joist_z))
        joist = bpy.context.active_object
        joist.scale = (dim_2x8_w, yoke_len, dim_2x8_h)
        joist.data.materials.append(mat_frame)
        
    # 3. Decking Boards split around tree
    board_w = 5.5 * inch
    board_t = 1.0 * inch
    gap = 0.25 * inch
    num_boards = int(yoke_len / (board_w + gap)) + 1
    start_y = cy - yoke_len/2
    deck_z = joist_z + dim_2x8_h/2 + board_t/2
    
    for i in range(num_boards):
        jy = start_y + (i * (board_w + gap))
        if abs(jy - cy) < 0.45:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx - 0.45 - (yoke_len/2 - 0.45)/2, jy, deck_z))
            b1 = bpy.context.active_object
            b1.scale = (yoke_len/2 - 0.45, board_w, board_t)
            b1.data.materials.append(mat_deck)
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + 0.45 + (yoke_len/2 - 0.45)/2, jy, deck_z))
            b2 = bpy.context.active_object
            b2.scale = (yoke_len/2 - 0.45, board_w, board_t)
            b2.data.materials.append(mat_deck)
        else:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, jy, deck_z))
            board = bpy.context.active_object
            board.scale = (yoke_len, board_w, board_t)
            board.data.materials.append(mat_deck)
            
    # 4. Posts
    for px in [cx - yoke_len/2 + 2*inch, cx + yoke_len/2 - 2*inch]:
        for py in [cy - yoke_len/2 + 2*inch, cy + yoke_len/2 - 2*inch]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, deck_z + 0.5))
            post = bpy.context.active_object
            post.scale = (3.5*inch, 3.5*inch, 1.0)
            post.data.materials.append(mat_frame)
            
    # 5. Rails
    top_z = deck_z + 1.0
    for y_side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + y_side*(yoke_len/2 - 2*inch), top_z))
        rail = bpy.context.active_object
        rail.scale = (yoke_len, 1.5*inch, 3.5*inch)
        rail.data.materials.append(mat_frame)
    for x_side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + x_side*(yoke_len/2 - 2*inch), cy, top_z))
        rail = bpy.context.active_object
        rail.scale = (1.5*inch, yoke_len, 3.5*inch)
        rail.data.materials.append(mat_frame)

def build_pro_bridge(x1, y1, z1, x2, y2, z2):
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    mx = (x1 + x2)/2
    my = (y1 + y2)/2
    mz = (z1 + z2)/2
    yaw = math.atan2(dy, dx) - math.pi/2
    pitch = -math.atan2(dz, dist)
    
    for offset in [-0.4, 0.4]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=dist, location=(mx, my, mz))
        cab = bpy.context.active_object
        cab.rotation_euler = (pitch, 0, yaw)
        cab.location.x += math.cos(yaw) * offset
        cab.location.y += math.sin(yaw) * offset
        cab.data.materials.append(mat_steel)

    board_len = 0.9
    step_size = 6.0*inch
    num_boards = int(dist / step_size)
    for i in range(num_boards):
        t = (i + 0.5) / num_boards
        bx = x1 + dx * t
        by = y1 + dy * t
        bz = z1 + dz * t + 0.05
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, bz))
        board = bpy.context.active_object
        board.scale = (board_len, 5.5*inch, 1*inch)
        board.rotation_euler = (pitch, 0, yaw)
        board.data.materials.append(mat_deck)

# Triangle layout
build_pro_platform("T1", T1[0], T1[1], Z1)
build_pro_platform("T2", T2[0], T2[1], Z2)
build_pro_platform("T3", T3[0], T3[1], Z3)

build_pro_bridge(T1[0], T1[1], Z1, T3[0], T3[1], Z3)
build_pro_bridge(T3[0], T3[1], Z3, T2[0], T2[1], Z2)
build_pro_bridge(T2[0], T2[1], Z2, T1[0], T1[1], Z1)

bpy.ops.wm.save_mainfile(filepath="/home/lanoitcif/treehouse/Professional_Skyward_Corrected.blend")

# CYCLE RENDER
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.cycles.use_denoising = True

world = bpy.data.worlds.new("Pro_World")
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()
node_env = nodes.new(type='ShaderNodeTexSky')
node_env.sky_type = 'NISHITA'
node_env.sun_elevation = math.radians(45)
node_env.sun_rotation = math.radians(135)
node_env.sun_intensity = 1.0
node_bg = nodes.new(type='ShaderNodeBackground')
node_out = nodes.new(type='ShaderNodeOutputWorld')
links.new(node_env.outputs['Color'], node_bg.inputs['Color'])
links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])
bpy.context.scene.world = world

# Camera points to the center of the triangle
cx = (T1[0]+T2[0]+T3[0])/3
cy = (T1[1]+T2[1]+T3[1])/3
cz = (Z1+Z2+Z3)/3

bpy.ops.object.empty_add(location=(cx, cy, cz))
target = bpy.context.active_object

bpy.ops.object.camera_add(location=(cx+10, cy-12, cz+6))
cam = bpy.context.active_object
cam.data.lens = 28 # Wide architectural format
bpy.context.scene.camera = cam

tt = cam.constraints.new(type='TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/pro_iso.png'
bpy.ops.render.render(write_still=True)

cam.location = (cx, cy-15, cz+2)
cam.data.lens = 45 
bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/pro_side.png'
bpy.ops.render.render(write_still=True)
