import bpy
import bmesh
import math
import mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_mesh.stl(filepath='/home/lanoitcif/treehouse/stl_files/grounds.stl')
obj = bpy.context.selected_objects[0]

# 1. Critical Axis Correction: The STL used Y as height (4.7m). Blender uses Z.
# Rotate 90 degrees around X to map the vertical topology correctly.
obj.rotation_euler[0] = math.radians(90)
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# 2. Ground Alignment: Shift the entire mesh so the lowest point rests perfectly at Z = 0
bpy.context.view_layer.update()
verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
z_min = min(v.z for v in verts)
obj.location.z = -z_min
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

# 3. Analyze for exact tree coordinates
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.transform(obj.matrix_world)

# Slice horizontally at Z = 1.5 meters to capture the trunks above the ground sweep
slice_z = 1.5
pts = [v.co for v in bm.verts if abs(v.co.z - slice_z) < 0.15]

# Group the vertices into dense clusters (the trunks)
clusters = []
for p in pts:
    found = False
    for c in clusters:
        if math.hypot(p.x - c['x'], p.y - c['y']) < 1.0: # 1 meter max trunk grouping
            c['pts'].append(p)
            c['x'] = sum(pt.x for pt in c['pts']) / len(c['pts'])
            c['y'] = sum(pt.y for pt in c['pts']) / len(c['pts'])
            found = True
            break
    if not found:
        clusters.append({'x': p.x, 'y': p.y, 'pts': [p]})

clusters.sort(key=lambda c: len(c['pts']), reverse=True)

# Find the three major tree trunks forming a linear row
import itertools
target_group = None
target_dist = 0

for comb in itertools.combinations(range(min(15, len(clusters))), 3):
    c1, c2, c3 = clusters[comb[0]], clusters[comb[1]], clusters[comb[2]]

    # Require massive trees
    if len(c1['pts']) < 500 or len(c2['pts']) < 500 or len(c3['pts']) < 500:
        continue

    d12 = math.hypot(c1['x']-c2['x'], c1['y']-c2['y'])
    d23 = math.hypot(c2['x']-c3['x'], c2['y']-c3['y'])
    d13 = math.hypot(c1['x']-c3['x'], c1['y']-c3['y'])

    max_d = max(d12, d23, d13)

    # Collinearity check using cross product
    cp = (c2['x']-c1['x'])*(c3['y']-c1['y']) - (c2['y']-c1['y'])*(c3['x']-c1['x'])

    # The linear row should be spanning ~5.21 meters
    if abs(cp) < 0.5 and 4.0 < max_d < 6.0:
        target_group = (comb[0], comb[1], comb[2])
        target_dist = max_d
        break

if not target_group:
    print("ERROR: Could not identify a linear row of three massive trees.")
    exit(1)

# Sort the 3 chosen trees linearly along X
t_group = [clusters[target_group[0]], clusters[target_group[1]], clusters[target_group[2]]]
t_group.sort(key=lambda c: c['x'])
t0 = t_group[0]
t1 = t_group[1]
t2 = t_group[2]

# Outer trees are t0 and t2
mid_x = (t0['x'] + t2['x']) / 2
mid_y = (t0['y'] + t2['y']) / 2

# 1. Translate so midpoint is at origin
obj.location.x = -mid_x
obj.location.y = -mid_y
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

# Re-evaluate coords
t0_x, t0_y = t0['x'] - mid_x, t0['y'] - mid_y
t1_x, t1_y = t1['x'] - mid_x, t1['y'] - mid_y
t2_x, t2_y = t2['x'] - mid_x, t2['y'] - mid_y

# 2. Rotate so t2 lies exactly on positive X-axis
angle = math.atan2(t2_y, t2_x)
obj.rotation_euler[2] = -angle
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# 3. Scale so outer trees are exactly 16 feet (4.8768 meters) apart
scale_factor = 4.8768 / target_dist
obj.scale = (scale_factor, scale_factor, scale_factor)
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Export perfectly leveled, Z-up ground scan
bpy.ops.export_mesh.stl(filepath='/home/lanoitcif/treehouse/stl_files/grounds_clean.stl', use_selection=True)
print("SUCCESS: Cleaned STL saved to grounds_clean.stl")

# Output new tree coordinates
def transform_pt(x, y):
    # rotate
    rx = math.cos(-angle)*x - math.sin(-angle)*y
    ry = math.sin(-angle)*x + math.cos(-angle)*y
    # scale
    return rx * scale_factor, ry * scale_factor

new_t0_x, new_t0_y = transform_pt(t0_x, t0_y)
new_t1_x, new_t1_y = transform_pt(t1_x, t1_y)
new_t2_x, new_t2_y = transform_pt(t2_x, t2_y)

print("=== CRITICAL TREE COORDINATES ===")
print(f"TREE_1: X={new_t0_x:.2f}, Y={new_t0_y:.2f}, PTS={len(t0['pts'])}")
print(f"TREE_2: X={new_t1_x:.2f}, Y={new_t1_y:.2f}, PTS={len(t1['pts'])}")
print(f"TREE_3: X={new_t2_x:.2f}, Y={new_t2_y:.2f}, PTS={len(t2['pts'])}")
