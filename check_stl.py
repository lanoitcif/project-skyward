import bpy
import bmesh
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_mesh.stl(filepath='/home/lanoitcif/treehouse/stl_files/grounds.stl')
obj = bpy.context.selected_objects[0]

dims = obj.dimensions
print(f'Dimensions: X={dims.x:.2f}, Y={dims.y:.2f}, Z={dims.z:.2f}')

# Detect if Y is actually the vertical (height) axis in the raw STL.
# For a ground-level drone scan the vertical extent is much larger than the
# horizontal spread, so the "vertical" axis will be the LARGEST dimension.
# However, this particular LIDAR capture stored absolute elevation in Y while
# the ground footprint spans X and Z — making Y the largest.  We also guard
# against near-cubic meshes with a 20 % ratio threshold.
AXIS_RATIO_THRESHOLD = 0.8
if dims.y > max(dims.x, dims.z) and min(dims.x, dims.z) < dims.y * AXIS_RATIO_THRESHOLD:
    print('Y appears to be the vertical axis (largest dimension). Rotating to standard Z-up.')
    obj.rotation_euler[0] = math.radians(90)
else:
    print('Z appears to be the vertical axis. No rotation needed.')

bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

bm = bmesh.new()
bm.from_mesh(obj.data)
bm.transform(obj.matrix_world)

min_z = min([v.co.z for v in bm.verts])
max_z = max([v.co.z for v in bm.verts])
# Slice through the lower trunk region (e.g. 10% up from the bottom)
slice_z = min_z + (max_z - min_z) * 0.15 
print(f'Slicing at height Z={slice_z:.2f}')

pts = [v.co for v in bm.verts if abs(v.co.z - slice_z) < (max_z - min_z) * 0.05]

clusters = []
merge_dist = max(obj.dimensions.x, obj.dimensions.y) * 0.08  # ~1.5 meters if 19m
for p in pts:
    found = False
    for c in clusters:
        if math.hypot(p.x - c['x'], p.y - c['y']) < merge_dist:
            c['pts'].append(p)
            c['x'] = sum(pt.x for pt in c['pts']) / len(c['pts'])
            c['y'] = sum(pt.y for pt in c['pts']) / len(c['pts'])
            found = True
            break
    if not found:
        clusters.append({'x': p.x, 'y': p.y, 'pts': [p]})

clusters.sort(key=lambda c: len(c['pts']), reverse=True)
print('Detected Trunks (Top 5 clusters):')
for i, c in enumerate(clusters[:5]):
    print(f"Trunk {i+1}: X={c['x']:.2f}, Y={c['y']:.2f}, points={len(c['pts'])}")

# Save alignment
bpy.ops.wm.save_as_mainfile(filepath='/home/lanoitcif/treehouse/stl_aligned.blend')
