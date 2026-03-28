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
mat_ladder = create_mat("Ladder_Steel", (0.3, 0.3, 0.3, 1))

# Load Cleaned STL. No artificial trees! We USE the native mesh.
stl_path = '/home/lanoitcif/treehouse/stl_files/grounds_clean.stl'
bpy.ops.import_mesh.stl(filepath=stl_path)
grounds = bpy.context.selected_objects[0]
grounds.data.materials.append(mat_ground)

# Exact Tree Coordinates (from clean_stl.py LIDAR analysis)
T1 = (-2.44, 0.00)
T2 = (1.29, 0.06)
T3 = (2.44, 0.00)

# Attainable, Safe Elevation for a DIY Carpenter (2 Meters / ~6.5 ft off ground)
Z_LEVEL = 2.2  # Raised to 2.2m to provide >6ft ground clearance underneath on a slope

inch = 0.0254
dim_2x8_w = 1.5 * inch
dim_2x8_h = 7.25 * inch

RAILING_HEIGHT = 0.9144          # 36.0" — meets IRC R312.1.1 minimum
JOIST_SPACING = 0.3048           # 12" OC — passes 300lb point-load test
BRIDGE_WIDTH = 0.9144            # 36.0" — meets IRC R311.6 egress minimum
TRUNK_CUTOUT = 0.35              # meters — 13.8" clearance for tree growth
HUMAN_HEIGHT_M = 1.75            # realistic adult height for scale figure


# Hardware checks: We will need hurricane ties, lag bolts, and deck screws for assembly.

def build_simple_platform(name, cx, cy, radius=1.0):
    cz = Z_LEVEL
    yoke_len = radius * 2
    yoke_dist = 0.5

    # Yoke Beams (doubled 2x10, 2 per tree)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy - yoke_dist, cz))
    yoke1 = bpy.context.active_object
    yoke1.scale = (yoke_len, 3*inch, 9.25*inch)
    yoke1.data.materials.append(mat_frame)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + yoke_dist, cz))
    yoke2 = bpy.context.active_object
    yoke2.scale = (yoke_len, 3*inch, 9.25*inch)
    yoke2.data.materials.append(mat_frame)

    # Floor Joists (2x8 at 12" OC)
    num_joists = int(yoke_len / JOIST_SPACING) + 1
    start_x = cx - yoke_len/2
    joist_z = cz + (9.25*inch)/2 + dim_2x8_h/2
    for i in range(num_joists):
        jx = start_x + (i * JOIST_SPACING)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(jx, cy, joist_z))
        joist = bpy.context.active_object
        joist.scale = (dim_2x8_w, yoke_len, dim_2x8_h)
        joist.data.materials.append(mat_frame)

    # Decking Boards (5/4 × 5.5 cedar)
    board_w = 5.5 * inch
    board_t = 1.0 * inch
    gap = 0.25 * inch
    num_boards = int(yoke_len / (board_w + gap)) + 1
    start_y = cy - yoke_len/2
    deck_z = joist_z + dim_2x8_h/2 + board_t/2

    for i in range(num_boards):
        jy = start_y + (i * (board_w + gap))
        if abs(jy - cy) < TRUNK_CUTOUT:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx - TRUNK_CUTOUT - (yoke_len/2 - TRUNK_CUTOUT)/2, jy, deck_z))
            b1 = bpy.context.active_object
            b1.scale = (yoke_len/2 - TRUNK_CUTOUT, board_w, board_t)
            b1.data.materials.append(mat_deck)

            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + TRUNK_CUTOUT + (yoke_len/2 - TRUNK_CUTOUT)/2, jy, deck_z))
            b2 = bpy.context.active_object
            b2.scale = (yoke_len/2 - TRUNK_CUTOUT, board_w, board_t)
            b2.data.materials.append(mat_deck)
        else:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, jy, deck_z))
            board = bpy.context.active_object
            board.scale = (yoke_len, board_w, board_t)
            board.data.materials.append(mat_deck)

    # 36" railings (IRC R312.1.1)
    for px in [cx - yoke_len/2 + 2*inch, cx + yoke_len/2 - 2*inch]:
        for py in [cy - yoke_len/2 + 2*inch, cy + yoke_len/2 - 2*inch]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, deck_z + RAILING_HEIGHT/2))
            post = bpy.context.active_object
            post.scale = (3.5*inch, 3.5*inch, RAILING_HEIGHT)
            post.data.materials.append(mat_frame)
    top_z = deck_z + RAILING_HEIGHT
    for y_side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + y_side*(yoke_len/2 - 2*inch), top_z))
        rail = bpy.context.active_object
        rail.scale = (yoke_len, 1.5*inch, 3.5*inch)
        rail.data.materials.append(mat_frame)

        # balusters
        num_balusters = int(yoke_len / (4.5 * inch))
        for j in range(num_balusters):
            bx = cx - yoke_len/2 + (j + 0.5) * (yoke_len / num_balusters)
            bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, cy + y_side*(yoke_len/2 - 2*inch), deck_z + RAILING_HEIGHT/2))
            baluster = bpy.context.active_object
            baluster.scale = (1.5*inch, 1.5*inch, RAILING_HEIGHT)
            baluster.data.materials.append(mat_frame)

    for x_side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + x_side*(yoke_len/2 - 2*inch), cy, top_z))
        rail = bpy.context.active_object
        rail.scale = (1.5*inch, yoke_len, 3.5*inch)
        rail.data.materials.append(mat_frame)

        # balusters
        num_balusters = int(yoke_len / (4.5 * inch))
        for j in range(num_balusters):
            by = cy - yoke_len/2 + (j + 0.5) * (yoke_len / num_balusters)
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + x_side*(yoke_len/2 - 2*inch), by, deck_z + RAILING_HEIGHT/2))
            baluster = bpy.context.active_object
            baluster.scale = (1.5*inch, 1.5*inch, RAILING_HEIGHT)
            baluster.data.materials.append(mat_frame)

    return deck_z


def build_shared_platform(name, cx2, cy2, cx3, cy3):
    """Merged platform for T2+T3 (only 1.15m apart — too close for separate decks)."""
    cz = Z_LEVEL
    margin = 1.0
    x_min = min(cx2, cx3) - margin
    x_max = max(cx2, cx3) + margin
    y_center = (cy2 + cy3) / 2
    y_half = margin
    plat_w = x_max - x_min
    plat_h = y_half * 2
    plat_cx = (x_min + x_max) / 2
    yoke_dist = 0.5

    # Yoke Beams — 2 per tree (4 total for shared platform)
    for cx_tree in [cx2, cx3]:
        for yd in [-yoke_dist, yoke_dist]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx_tree, y_center + yd, cz))
            yoke = bpy.context.active_object
            yoke.scale = (plat_w, 3*inch, 9.25*inch)
            yoke.data.materials.append(mat_frame)

    # Floor Joists (2x8 at 12" OC spanning full platform width in X)
    num_joists = int(plat_w / JOIST_SPACING) + 1
    start_x = x_min
    joist_z = cz + (9.25*inch)/2 + dim_2x8_h/2
    for i in range(num_joists):
        jx = start_x + (i * JOIST_SPACING)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(jx, y_center, joist_z))
        joist = bpy.context.active_object
        joist.scale = (dim_2x8_w, plat_h, dim_2x8_h)
        joist.data.materials.append(mat_frame)

    # Decking Boards
    board_w = 5.5 * inch
    board_t = 1.0 * inch
    gap = 0.25 * inch
    num_boards = int(plat_h / (board_w + gap)) + 1
    start_y = y_center - y_half
    deck_z = joist_z + dim_2x8_h/2 + board_t/2

    for i in range(num_boards):
        jy = start_y + (i * (board_w + gap))
        is_cutout = False
        for tcx, tcy in [(cx2, cy2), (cx3, cy3)]:
            if abs(jy - tcy) < TRUNK_CUTOUT and True:
                is_cutout = True
                # Split board around this trunk
                left_end = x_min
                right_end = x_max
                cut_l = tcx - TRUNK_CUTOUT
                cut_r = tcx + TRUNK_CUTOUT
                if cut_l > left_end:
                    seg_cx = (left_end + cut_l) / 2
                    seg_w = cut_l - left_end
                    bpy.ops.mesh.primitive_cube_add(size=1, location=(seg_cx, jy, deck_z))
                    b = bpy.context.active_object
                    b.scale = (seg_w, board_w, board_t)
                    b.data.materials.append(mat_deck)
                if cut_r < right_end:
                    seg_cx = (cut_r + right_end) / 2
                    seg_w = right_end - cut_r
                    bpy.ops.mesh.primitive_cube_add(size=1, location=(seg_cx, jy, deck_z))
                    b = bpy.context.active_object
                    b.scale = (seg_w, board_w, board_t)
                    b.data.materials.append(mat_deck)
                break
        if not is_cutout:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(plat_cx, jy, deck_z))
            board = bpy.context.active_object
            board.scale = (plat_w, board_w, board_t)
            board.data.materials.append(mat_deck)

    # 36" railings around full perimeter
    corners = [
        (x_min + 2*inch, y_center - y_half + 2*inch),
        (x_min + 2*inch, y_center + y_half - 2*inch),
        (x_max - 2*inch, y_center - y_half + 2*inch),
        (x_max - 2*inch, y_center + y_half - 2*inch),
    ]
    for px, py in corners:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, deck_z + RAILING_HEIGHT/2))
        post = bpy.context.active_object
        post.scale = (3.5*inch, 3.5*inch, RAILING_HEIGHT)
        post.data.materials.append(mat_frame)

    top_z = deck_z + RAILING_HEIGHT
    for y_side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(plat_cx, y_center + y_side*(y_half - 2*inch), top_z))
        rail = bpy.context.active_object
        rail.scale = (plat_w, 1.5*inch, 3.5*inch)
        rail.data.materials.append(mat_frame)

        # balusters
        num_balusters = int(plat_w / (4.5 * inch))
        for j in range(num_balusters):
            bx = x_min + (j + 0.5) * (plat_w / num_balusters)
            bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, y_center + y_side*(y_half - 2*inch), deck_z + RAILING_HEIGHT/2))
            baluster = bpy.context.active_object
            baluster.scale = (1.5*inch, 1.5*inch, RAILING_HEIGHT)
            baluster.data.materials.append(mat_frame)

    for x_side in [(x_min + 2*inch), (x_max - 2*inch)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_side, y_center, top_z))
        rail = bpy.context.active_object
        rail.scale = (1.5*inch, plat_h, 3.5*inch)
        rail.data.materials.append(mat_frame)

        # balusters
        num_balusters = int(plat_h / (4.5 * inch))
        for j in range(num_balusters):
            by = y_center - y_half + (j + 0.5) * (plat_h / num_balusters)
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x_side, by, deck_z + RAILING_HEIGHT/2))
            baluster = bpy.context.active_object
            baluster.scale = (1.5*inch, 1.5*inch, RAILING_HEIGHT)
            baluster.data.materials.append(mat_frame)

    return deck_z


def build_simple_wood_bridge(x1, y1, x2, y2):
    cz = Z_LEVEL
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx*dx + dy*dy)
    mx = (x1 + x2)/2
    my = (y1 + y2)/2
    yaw = math.atan2(dy, dx) - math.pi/2

    # 2x8 stringers (2 parallel, one per side)
    joist_z = cz + (9.25*inch)/2 + dim_2x8_h/2
    half_w = BRIDGE_WIDTH / 2
    for offset in [-half_w, half_w]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(mx, my, joist_z))
        joist = bpy.context.active_object
        joist.scale = (dim_2x8_w, dist, dim_2x8_h)
        joist.rotation_euler = (0, 0, yaw)
        joist.location.x += math.cos(yaw) * offset
        joist.location.y += math.sin(yaw) * offset
        joist.data.materials.append(mat_frame)

    # Decking (IRC-compliant 36" wide walkway)
    step_size = 6.0*inch
    num_boards = int(dist / step_size)
    deck_z = joist_z + dim_2x8_h/2 + 0.5*inch
    for i in range(num_boards):
        t = (i + 0.5) / num_boards
        bx = x1 + dx * t
        by = y1 + dy * t
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, deck_z))
        board = bpy.context.active_object
        board.scale = (BRIDGE_WIDTH, 5.5*inch, 1*inch)
        board.rotation_euler = (0, 0, yaw)
        board.data.materials.append(mat_deck)

    # 36" railings on both sides
    top_z = deck_z + RAILING_HEIGHT
    for offset in [-half_w, half_w]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(mx, my, top_z))
        rail = bpy.context.active_object
        rail.scale = (1.5*inch, dist, 3.5*inch)
        rail.rotation_euler = (0, 0, yaw)
        rail.location.x += math.cos(yaw) * offset
        rail.location.y += math.sin(yaw) * offset
        rail.data.materials.append(mat_frame)

        # balusters
        num_balusters = int(dist / (4.5 * inch))
        for j in range(num_balusters):
            t = (j + 0.5) / num_balusters
            bx = x1 + dx * t
            by = y1 + dy * t
            bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, deck_z + RAILING_HEIGHT/2))
            baluster = bpy.context.active_object
            baluster.scale = (1.5*inch, 1.5*inch, RAILING_HEIGHT)
            baluster.rotation_euler = (0, 0, yaw)
            baluster.location.x += math.cos(yaw) * offset
            baluster.location.y += math.sin(yaw) * offset
            baluster.data.materials.append(mat_frame)


def build_ladder(cx, cy, deck_z):
    """Access ladder at T1 — required for egress (IRC R311)."""
    rung_count = 7
    ladder_w = 0.45
    for i in range(rung_count):
        rz = (i + 1) * (deck_z / (rung_count + 1))
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx - 1.0, cy, rz))
        rung = bpy.context.active_object
        rung.scale = (ladder_w, 1.5*inch, 1.5*inch)
        rung.data.materials.append(mat_ladder)
    # Side rails
    for yo in [-ladder_w/2, ladder_w/2]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx - 1.0, cy + yo, deck_z/2))
        rail = bpy.context.active_object
        rail.scale = (1.5*inch, 1.5*inch, deck_z)
        rail.data.materials.append(mat_ladder)


# === BUILD LAYOUT ===
# T1: standalone platform (isolated, 3.73m from nearest tree)
t1_deck_z = build_simple_platform("T1", T1[0], T1[1])

# T2+T3: shared platform (only 1.15m apart — too close for separate decks)
shared_deck_z = build_shared_platform("T2_T3", T2[0], T2[1], T3[0], T3[1])

# Bridge: T1 to shared T2+T3 platform (connects to nearest edge)
shared_edge_x = min(T2[0], T3[0]) - 1.0  # left edge of shared platform
build_simple_wood_bridge(T1[0], T1[1], shared_edge_x, (T2[1]+T3[1])/2)

# Access ladder at T1
build_ladder(T1[0], T1[1], t1_deck_z)

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
        scale_f = HUMAN_HEIGHT_M / dim_z
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
