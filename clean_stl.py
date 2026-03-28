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
z_min = min((obj.matrix_world @ mathutils.Vector(v)).z for v in obj.bound_box)
import mathutils

# Re-calculate correct Z_min
verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
z_min = min(v.z for v in verts)

obj.location.z = -z_min
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

# Export perfectly leveled, Z-up ground scan
bpy.ops.export_mesh.stl(filepath='/home/lanoitcif/treehouse/stl_files/grounds_clean.stl', use_selection=True)
print("SUCCESS: Cleaned STL saved to grounds_clean.stl")

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

# The 3 largest, densest clusters at Z=1.5m are the three trees
clusters.sort(key=lambda c: len(c['pts']), reverse=True)
print("=== CRITICAL TREE COORDINATES ===")
for i, c in enumerate(clusters[:3]):
    print(f"TREE_{i+1}: X={c['x']:.2f}, Y={c['y']:.2f}, PTS={len(c['pts'])}")
