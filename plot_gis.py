import folium
import math

# User provided coords
lat = 39.07225641947208
lon = -77.74778565324527

# Initialize Map using high-res Esri Satellite Layer
m = folium.Map(location=[lat, lon], zoom_start=21, max_zoom=22, control_scale=True)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Esri Satellite',
    overlay=False,
    control=True
).add_to(m)

# 1. Plot the Main Tree (T1)
folium.Marker(
    location=[lat, lon],
    popup='<b>T1 (Main Hub Tree)</b>',
    icon=folium.Icon(color='green', icon='leaf')
).add_to(m)

# 2. Extrapolate T2 and T3 based on our normalized LIDAR CAD analysis.
# After normalization, the trees form a linear row along the X-axis:
#   T1 = (-2.44, 0.00),  T2 = (1.29, 0.06),  T3 = (2.44, 0.00)
# The outer span (T1-T3) is ~4.88 meters (16 feet) by design.
# At this latitude, 1 degree latitude ≈ 111,000 meters.
# 4.88 meters ≈ 0.0000440 degrees.
# The row is aligned along X (≈ east-west at this site), so the offset
# is primarily in longitude, with a negligible latitude shift.

METERS_PER_DEG_LAT = 111_000
METERS_PER_DEG_LON = 111_000 * math.cos(math.radians(lat))  # ~85,300 m at 39°N

# T1 is the westernmost tree (negative X in CAD → lower longitude)
# T3 is the easternmost tree (positive X in CAD → higher longitude)
# T2 sits between them, slightly off-axis (Y = 0.06 m ≈ negligible lat shift)
span_m = 4.88  # outer tree span (T1 to T3)
t1_x_m, t1_y_m = -2.44, 0.00
t2_x_m, t2_y_m =  1.29, 0.06
t3_x_m, t3_y_m =  2.44, 0.00

# Convert CAD meters → degree offsets relative to T1's GPS position
def cad_to_gps_offset(x_m, y_m):
    """Convert CAD (X=east, Y=north) offsets in meters to (Δlat, Δlon)."""
    d_lat = y_m / METERS_PER_DEG_LAT
    d_lon = x_m / METERS_PER_DEG_LON
    return d_lat, d_lon

# T1 is our GPS anchor point; offsets for T2 and T3 are relative to T1
t2_dlat, t2_dlon = cad_to_gps_offset(t2_x_m - t1_x_m, t2_y_m - t1_y_m)
t3_dlat, t3_dlon = cad_to_gps_offset(t3_x_m - t1_x_m, t3_y_m - t1_y_m)

folium.Marker(
    location=[lat + t3_dlat, lon + t3_dlon],
    popup='<b>T3 (End Span)</b>',
    icon=folium.Icon(color='lightgreen')
).add_to(m)

folium.Marker(
    location=[lat + t2_dlat, lon + t2_dlon],
    popup='<b>T2 (Mid Span)</b>',
    icon=folium.Icon(color='lightgreen')
).add_to(m)

# 3. Draw the structural platform footprint (Polygon)
# 16-foot span (~4.88 m) along X → longitude, ~3 m depth along Y → latitude
half_span_deg = (span_m / 2) / METERS_PER_DEG_LON
depth_deg = 3.0 / METERS_PER_DEG_LAT  # ~3 m walkway depth

# Center the polygon on the midpoint of T1–T3
mid_dlon = (t3_dlon) / 2  # midpoint offset from T1
deck_bounds = [
    [lat + depth_deg,  lon + mid_dlon - half_span_deg],
    [lat + depth_deg,  lon + mid_dlon + half_span_deg],
    [lat - depth_deg,  lon + mid_dlon + half_span_deg],
    [lat - depth_deg,  lon + mid_dlon - half_span_deg],
    [lat + depth_deg,  lon + mid_dlon - half_span_deg]  # close loop
]

folium.Polygon(
    locations=deck_bounds,
    color='blue',
    weight=3,
    fill=True,
    fill_color='cyan',
    fill_opacity=0.3,
    popup='<b>Treehouse Footprint</b> (~16ft span)'
).add_to(m)

# Save the interactive map
m.save('/home/lanoitcif/treehouse/gis_map.html')
print("SUCCESS: High-res GIS map generated at gis_map.html")

# Cross-validation: print GIS-derived distances for comparison with STL
t2_loc = (lat + t2_dlat, lon + t2_dlon)
t3_loc = (lat + t3_dlat, lon + t3_dlon)
gis_t1_t3_m = math.sqrt(((t3_dlat) * METERS_PER_DEG_LAT)**2 + ((t3_dlon) * METERS_PER_DEG_LON)**2)
gis_t1_t2_m = math.sqrt(((t2_dlat) * METERS_PER_DEG_LAT)**2 + ((t2_dlon) * METERS_PER_DEG_LON)**2)
print(f"\n=== GIS CROSS-VALIDATION ===")
print(f"GIS T1→T3 distance: {gis_t1_t3_m:.2f} m ({gis_t1_t3_m/0.3048:.1f} ft)")
print(f"GIS T1→T2 distance: {gis_t1_t2_m:.2f} m ({gis_t1_t2_m/0.3048:.1f} ft)")
print(f"CAD design span:    {span_m:.2f} m ({span_m/0.3048:.1f} ft)")
print(f"NOTE: GIS offsets are extrapolated from the normalized CAD model,")
print(f"      not independently measured from satellite imagery.")
