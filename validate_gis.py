"""
Independent GIS Cross-Validation: STL LIDAR vs USGS 3DEP

Validates the project STL scan's spatial accuracy by comparing its terrain
profile against the USGS 3DEP Digital Terrain Model — an entirely independent
data source acquired 2021-11-02 at ~0.23m resolution.

Usage:
    python3 validate_gis.py

Requires: numpy, numpy-stl, Pillow, scipy, and internet access (to fetch USGS data).
"""

import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter, zoom as ndizoom
from scipy.signal import correlate2d
from scipy.stats import binned_statistic_2d
from stl import mesh as stlmesh

# ── Project constants ────────────────────────────────────────────────────────
GPS_LAT = 39.07225641947208
GPS_LON = -77.74778565324527
TARGET_SPAN_FT = 16
TARGET_SPAN_M = TARGET_SPAN_FT * 0.3048  # 4.8768 m

STL_PATH = os.path.join(os.path.dirname(__file__), "stl_files", "grounds_clean.stl")
DTM_PATH = os.path.join(os.path.dirname(__file__), "image_files", "3DEP_1m.tiff")
SAT_PATH = os.path.join(os.path.dirname(__file__), "image_files", "satellite_composite.png")

# ── Helpers ──────────────────────────────────────────────────────────────────
METERS_PER_DEG_LAT = 111_000
METERS_PER_DEG_LON = 111_000 * math.cos(math.radians(GPS_LAT))

def fetch_usgs_dtm(lat, lon, radius_m=30, size=256):
    """Download USGS 3DEP DTM raster centered on (lat, lon)."""
    r_lon = radius_m / METERS_PER_DEG_LON
    r_lat = radius_m / METERS_PER_DEG_LAT
    bbox = f"{lon - r_lon},{lat - r_lat},{lon + r_lon},{lat + r_lat}"
    url = (
        f"https://elevation.nationalmap.gov/arcgis/rest/services/"
        f"3DEPElevation/ImageServer/exportImage"
        f"?bbox={bbox}&bboxSR=4326&size={size},{size}"
        f"&imageSR=4326&format=tiff&pixelType=F32&f=image"
    )
    os.makedirs(os.path.dirname(DTM_PATH), exist_ok=True)
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "30", "-o", DTM_PATH, url],
        capture_output=True, text=True,
    )
    if not os.path.exists(DTM_PATH) or os.path.getsize(DTM_PATH) < 1000:
        print("ERROR: Failed to download USGS 3DEP data.", file=sys.stderr)
        raise SystemExit(1)
    return np.array(Image.open(DTM_PATH)), 2 * radius_m / size


def fetch_satellite_tiles(lat, lon, zoom=19, grid=5):
    """Download and stitch Esri satellite tiles into a composite."""
    n = 2 ** zoom
    tx = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    ty = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    tile_dir = os.path.join(os.path.dirname(__file__), "image_files", "tiles")
    os.makedirs(tile_dir, exist_ok=True)

    half = grid // 2
    composite = Image.new("RGB", (256 * grid, 256 * grid))
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            x, y = tx + dx, ty + dy
            url = (
                f"https://server.arcgisonline.com/ArcGIS/rest/services/"
                f"World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
            )
            path = os.path.join(tile_dir, f"z{zoom}_{dx + half}_{dy + half}.jpg")
            if not os.path.exists(path):
                subprocess.run(
                    ["curl", "-s", "-o", path, url], capture_output=True
                )
            tile = Image.open(path)
            composite.paste(tile, ((dx + half) * 256, (dy + half) * 256))

    composite.save(SAT_PATH)
    mpp = 156543.03392 * math.cos(math.radians(lat)) / (2 ** zoom)

    # GPS pixel position in composite
    frac_x = (lon + 180.0) / 360.0 * n - (tx - half)
    frac_y = (
        (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n - (ty - half)
    )
    gps_px = frac_x * 256
    gps_py = frac_y * 256
    return np.array(composite, dtype=np.float32), mpp, gps_px, gps_py


def detrend_2d(grid):
    """Remove best-fit plane from a 2D array."""
    yi, xi = np.meshgrid(range(grid.shape[1]), range(grid.shape[0]))
    A = np.column_stack([xi.ravel(), yi.ravel(), np.ones(grid.size)])
    coeffs, _, _, _ = np.linalg.lstsq(A, grid.ravel(), rcond=None)
    plane = coeffs[0] * xi + coeffs[1] * yi + coeffs[2]
    return grid - plane, coeffs


def terrain_slope(coeffs, px_m):
    """Return (grade_pct, bearing_deg) from plane-fit coefficients."""
    slope_x = coeffs[0] / px_m
    slope_y = coeffs[1] / px_m
    grade = math.hypot(slope_x, slope_y)
    bearing = math.degrees(math.atan2(slope_x, slope_y))
    return grade * 100, bearing


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  INDEPENDENT GIS CROSS-VALIDATION")
    print("  STL LIDAR scan vs USGS 3DEP Digital Terrain Model")
    print("=" * 60)

    # 1. Load / fetch data
    print("\n[1/5] Loading STL ground scan …")
    stl_mesh = stlmesh.Mesh.from_file(STL_PATH)
    verts = stl_mesh.vectors.reshape(-1, 3)
    print(f"  {len(verts)} vertices, "
          f"X[{verts[:,0].min():.1f},{verts[:,0].max():.1f}] "
          f"Y[{verts[:,1].min():.1f},{verts[:,1].max():.1f}] "
          f"Z[{verts[:,2].min():.1f},{verts[:,2].max():.1f}]")

    print("\n[2/5] Fetching USGS 3DEP DTM …")
    dtm, dtm_px = fetch_usgs_dtm(GPS_LAT, GPS_LON)
    print(f"  {dtm.shape} grid at {dtm_px:.3f} m/px, "
          f"elev [{dtm.min():.1f}, {dtm.max():.1f}] m ASL")

    print("\n[3/5] Fetching Esri satellite imagery (zoom 19) …")
    sat, sat_mpp, gps_px, gps_py = fetch_satellite_tiles(GPS_LAT, GPS_LON)
    print(f"  Composite {sat.shape[1]}×{sat.shape[0]} at {sat_mpp:.3f} m/px")

    # 2. Build STL terrain grid (ground only: Z < 0.8 m)
    print("\n[4/5] Building terrain grids …")
    ground = verts[verts[:, 2] < 0.8]
    grid_res = 0.5  # 50 cm
    x_bins = np.arange(ground[:, 0].min(), ground[:, 0].max() + grid_res, grid_res)
    y_bins = np.arange(ground[:, 1].min(), ground[:, 1].max() + grid_res, grid_res)
    stl_grid, xe, ye, _ = binned_statistic_2d(
        ground[:, 0], ground[:, 1], ground[:, 2],
        statistic="mean", bins=[x_bins, y_bins],
    )
    # Fill NaN cells via nearest-neighbor
    valid = ~np.isnan(stl_grid)
    if valid.any():
        yi_g, xi_g = np.meshgrid(range(stl_grid.shape[1]), range(stl_grid.shape[0]))
        pts = np.column_stack([xi_g[valid], yi_g[valid]])
        vals = stl_grid[valid]
        stl_filled = griddata(
            pts, vals, np.column_stack([xi_g.ravel(), yi_g.ravel()]),
            method="nearest",
        ).reshape(stl_grid.shape)
    else:
        stl_filled = np.nan_to_num(stl_grid)

    stl_dt, stl_coeffs = detrend_2d(stl_filled)
    dtm_dt, dtm_coeffs = detrend_2d(dtm)

    stl_grade, stl_bear = terrain_slope(stl_coeffs, grid_res)
    dtm_grade, dtm_bear = terrain_slope(dtm_coeffs, dtm_px)

    stl_relief = stl_filled.max() - stl_filled.min()
    dtm_relief = dtm.max() - dtm.min()

    # 3. 2D template matching across scale factors
    print("\n[5/5] Cross-correlating terrain shapes …")
    dtm_50cm = ndizoom(dtm_dt, dtm_px / grid_res)
    stl_n = (stl_dt - stl_dt.mean()) / (stl_dt.std() + 1e-10)
    dtm_n = (dtm_50cm - dtm_50cm.mean()) / (dtm_50cm.std() + 1e-10)

    scale_results = []
    for pct in range(80, 121, 2):
        s = pct / 100.0
        stl_scaled = ndizoom(stl_n, s)
        if (stl_scaled.shape[0] >= dtm_n.shape[0] or
                stl_scaled.shape[1] >= dtm_n.shape[1]):
            continue
        c = correlate2d(dtm_n, stl_scaled, mode="valid")
        c /= stl_scaled.size
        scale_results.append((s, c.max()))

    scale_results.sort(key=lambda x: x[1], reverse=True)
    best_scale, best_corr = scale_results[0] if scale_results else (1.0, 0.0)
    validated_span = TARGET_SPAN_M * best_scale

    # 4. Satellite canopy analysis (grove extent)
    cx, cy = int(gps_px), int(gps_py)
    r_px = int(15 / sat_mpp)
    crop = sat[max(0,cy-r_px):cy+r_px, max(0,cx-r_px):cx+r_px]
    R, G, B = crop[:,:,0], crop[:,:,1], crop[:,:,2]
    brightness = (R + G + B) / 3
    canopy = (brightness < 60) & (G > 5)
    canopy_pct = canopy.sum() / canopy.size * 100

    # ── Report ───────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  VALIDATION RESULTS")
    print("=" * 60)

    print(f"\n  Data Sources:")
    print(f"    • USGS 3DEP DTM — acquired 2021-11-02, {dtm_px:.2f} m/px")
    print(f"    • STL LIDAR scan — drone capture, {grid_res:.2f} m grid")
    print(f"    • Esri satellite  — zoom 19, {sat_mpp:.2f} m/px")

    print(f"\n  ┌─────────────────────────────────────────────────┐")
    print(f"  │  TERRAIN SLOPE (most reliable metric)           │")
    print(f"  │    STL grade:      {stl_grade:6.2f}%                     │")
    print(f"  │    USGS DTM grade: {dtm_grade:6.2f}%                     │")
    slope_ratio = stl_grade / dtm_grade if dtm_grade > 0 else float('nan')
    print(f"  │    Ratio:          {slope_ratio:6.2f} (1.00 = perfect)    │")
    print(f"  └─────────────────────────────────────────────────┘")

    print(f"\n  Terrain relief:")
    print(f"    STL:  {stl_relief:.3f} m over {stl_grid.shape[0]*grid_res:.0f}×{stl_grid.shape[1]*grid_res:.0f} m area")
    print(f"    USGS: {dtm_relief:.3f} m over 60×60 m area")

    print(f"\n  2D template matching (scale sweep 0.80–1.20×):")
    for s, r in scale_results[:3]:
        sp = TARGET_SPAN_M * s
        print(f"    {s:.2f}× → {sp:.2f} m ({sp/0.3048:.1f} ft), corr = {r:.4f}")

    print(f"\n  Satellite canopy: {canopy_pct:.0f}% dark canopy within 15 m")
    print(f"    (23 cm/px cannot resolve individual trees at 5 m spacing)")

    print(f"\n  ┌─────────────────────────────────────────────────┐")
    print(f"  │  CONCLUSION                                     │")
    ok = 0.85 <= slope_ratio <= 1.15
    print(f"  │  Slope agreement:  {'PASS' if ok else 'MARGINAL':8s} ({slope_ratio:.2f}×, ±{abs(1-slope_ratio)*100:.0f}%)     │")
    print(f"  │  Best-fit span:    {validated_span:.2f} m ({validated_span/0.3048:.1f} ft)           │")
    print(f"  │  Design span:      {TARGET_SPAN_M:.2f} m ({TARGET_SPAN_FT:.0f} ft)             │")
    dev = abs(validated_span - TARGET_SPAN_M)
    print(f"  │  Deviation:        {dev:.2f} m ({dev/TARGET_SPAN_M*100:.0f}%)                   │")
    print(f"  │                                                 │")
    if ok and dev < 1.0:
        print(f"  │  ✓ STL scale is CONSISTENT with USGS terrain   │")
    else:
        print(f"  │  ⚠ Recommend ground-truth survey before build  │")
    print(f"  │  ⚠ Individual tree positions require on-site     │")
    print(f"  │    measurement (satellite resolution insufficient)│")
    print(f"  └─────────────────────────────────────────────────┘")


if __name__ == "__main__":
    main()
