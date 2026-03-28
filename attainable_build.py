import bpy
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

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

# Load Cleaned STL. No artificial trees! We USE the native mesh.
stl_path = '/home/lanoitcif/treehouse/stl_files/grounds_clean.stl'
bpy.ops.import_mesh.stl(filepath=stl_path)
grounds = bpy.context.selected_objects[0]
grounds.data.materials.append(mat_ground)

# Exact Tree Coordinates 
T1 = (1.71, 8.58)
T2 = (3.72, 8.48)
T3 = (2.76, 5.36)

# Attainable, Safe Elevation for a DIY Carpenter (2 Meters / ~6.5 ft off ground)
Z_LEVEL = 2.0 

inch = 0.0254
dim_2x8_w = 1.5 * inch
dim_2x8_h = 7.25 * inch

def build_simple_platform(name, cx, cy, radius=1.0):
    cz = Z_LEVEL
    yoke_len = radius * 2
    yoke_dist = 0.5 
    
    # Yoke Beams
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy - yoke_dist, cz))
    yoke1 = bpy.context.active_object
    yoke1.scale = (yoke_len, 3*inch, 9.25*inch)
    yoke1.data.materials.append(mat_frame)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + yoke_dist, cz))
    yoke2 = bpy.context.active_object
    yoke2.scale = (yoke_len, 3*inch, 9.25*inch)
    yoke2.data.materials.append(mat_frame)
    
    # Joists
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
        
    # Decking Boards
    board_w = 5.5 * inch
    board_t = 1.0 * inch
    gap = 0.25 * inch
    num_boards = int(yoke_len / (board_w + gap)) + 1
    start_y = cy - yoke_len/2
    deck_z = joist_z + dim_2x8_h/2 + board_t/2
    
    for i in range(num_boards):
        jy = start_y + (i * (board_w + gap))
        if abs(jy - cy) < 0.35: # Trunk cutout
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx - 0.35 - (yoke_len/2 - 0.35)/2, jy, deck_z))
            b1 = bpy.context.active_object
            b1.scale = (yoke_len/2 - 0.35, board_w, board_t)
            b1.data.materials.append(mat_deck)
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + 0.35 + (yoke_len/2 - 0.35)/2, jy, deck_z))
            b2 = bpy.context.active_object
            b2.scale = (yoke_len/2 - 0.35, board_w, board_t)
            b2.data.materials.append(mat_deck)
        else:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, jy, deck_z))
            board = bpy.context.active_object
            board.scale = (yoke_len, board_w, board_t)
            board.data.materials.append(mat_deck)
            
    # Safe 36" railing for children
    for px in [cx - yoke_len/2 + 2*inch, cx + yoke_len/2 - 2*inch]:
        for py in [cy - yoke_len/2 + 2*inch, cy + yoke_len/2 - 2*inch]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, deck_z + 0.45))
            post = bpy.context.active_object
            post.scale = (3.5*inch, 3.5*inch, 0.9)
            post.data.materials.append(mat_frame)
    top_z = deck_z + 0.9
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

def build_simple_wood_bridge(x1, y1, x2, y2):
    cz = Z_LEVEL
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx*dx + dy*dy)
    mx = (x1 + x2)/2
    my = (y1 + y2)/2
    yaw = math.atan2(dy, dx) - math.pi/2
    
    # 2x8 floor joists
    joist_z = cz + (9.25*inch)/2 + dim_2x8_h/2
    for offset in [-0.4, 0.4]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(mx, my, joist_z))
        joist = bpy.context.active_object
        joist.scale = (dim_2x8_w, dist, dim_2x8_h)
        joist.rotation_euler = (0, 0, yaw)
        joist.location.x += math.cos(yaw) * offset
        joist.location.y += math.sin(yaw) * offset
        joist.data.materials.append(mat_frame)

    # Decking
    board_len = 0.9
    step_size = 6.0*inch
    num_boards = int(dist / step_size)
    deck_z = joist_z + dim_2x8_h/2 + 0.5*inch
    for i in range(num_boards):
        t = (i + 0.5) / num_boards
        bx = x1 + dx * t
        by = y1 + dy * t
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, deck_z))
        board = bpy.context.active_object
        board.scale = (board_len, 5.5*inch, 1*inch)
        board.rotation_euler = (0, 0, yaw)
        board.data.materials.append(mat_deck)
        
    # Railing
    top_z = deck_z + 0.9
    for offset in [-0.4, 0.4]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(mx, my, top_z))
        rail = bpy.context.active_object
        rail.scale = (1.5*inch, dist, 3.5*inch)
        rail.rotation_euler = (0, 0, yaw)
        rail.location.x += math.cos(yaw) * offset
        rail.location.y += math.sin(yaw) * offset
        rail.data.materials.append(mat_frame)

# Triangle layout at safe height
build_simple_platform("T1", T1[0], T1[1])
build_simple_platform("T2", T2[0], T2[1])
build_simple_platform("T3", T3[0], T3[1])

build_simple_wood_bridge(T1[0], T1[1], T3[0], T3[1])
build_simple_wood_bridge(T3[0], T3[1], T2[0], T2[1])

bpy.ops.wm.save_mainfile(filepath="/home/lanoitcif/treehouse/Attainable_Skyward.blend")

# Add humans for scale
human_path = '/home/lanoitcif/treehouse/human.obj'
if os.path.exists(human_path):
    if hasattr(bpy.ops.wm, 'obj_import'):
        bpy.ops.wm.obj_import(filepath=human_path)
    else:
        bpy.ops.import_scene.obj(filepath=human_path)
    if bpy.context.selected_objects:
        human = bpy.context.selected_objects[0]
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
        dim_z = human.dimensions.z if human.dimensions.z > 0 else 1
        scale_f = 5.0 / dim_z 
        human.scale = (scale_f, scale_f, scale_f)
        human.rotation_euler[2] = math.radians(45)
        
        bpy.context.view_layer.update()
        z_offset = human.bound_box[0][2] * scale_f 
        human.location = (T3[0], T3[1]+1, Z_LEVEL + 0.3 - z_offset)
        
        mat = bpy.data.materials.new(name="Human_Scale_Mat")
        mat.use_nodes = True
        principled = mat.node_tree.nodes.get('Principled BSDF')
        if principled:
            principled.inputs['Base Color'].default_value = (0.2, 0.5, 0.9, 1)
        human.data.materials.append(mat)

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

cx = (T1[0]+T2[0]+T3[0])/3
cy = (T1[1]+T2[1]+T3[1])/3
cz = Z_LEVEL

bpy.ops.object.empty_add(location=(cx, cy, cz))
target = bpy.context.active_object

bpy.ops.object.camera_add(location=(cx-6, cy-9, cz+3))
cam = bpy.context.active_object
cam.data.lens = 24 # Wide architectural format
bpy.context.scene.camera = cam

tt = cam.constraints.new(type='TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/attainable_iso.png'
bpy.ops.render.render(write_still=True)

cam.location = (cx, cy-12, cz+1)
cam.data.lens = 35 
bpy.context.scene.render.filepath = '/home/lanoitcif/treehouse/attainable_side.png'
bpy.ops.render.render(write_still=True)
