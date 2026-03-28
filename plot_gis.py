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

# 2. Extrapolate T2 and T3 based on our LIDAR CAD analysis.
# Our CAD found T1=(1.71, 8.58), T2=(3.72, 8.48), T3=(2.76, 5.36).
# The max distance between T1 and T3 is ~3.2 meters (10.5 ft)
# At this latitude, 1 degree latitude = ~111,000 meters.
# 3.2 meters = 3.2 / 111000 = 0.0000288 degrees.

lat_offset_T3 = -0.0000288 # South
lon_offset_T3 = 0.00001    # East slightly

folium.Marker(
    location=[lat + lat_offset_T3, lon + lon_offset_T3],
    popup='<b>T3 (End Span)</b>',
    icon=folium.Icon(color='lightgreen')
).add_to(m)

lat_offset_T2 = -0.00001
lon_offset_T2 = 0.000025

folium.Marker(
    location=[lat + lat_offset_T2, lon + lon_offset_T2],
    popup='<b>T2 (Mid Span)</b>',
    icon=folium.Icon(color='lightgreen')
).add_to(m)

# 3. Draw the structural platform footprint (Polygon)
# 16-foot span (~5 meters) -> +/- 0.000045 degrees
deck_bounds = [
    [lat + 0.000045, lon - 0.000030],
    [lat + 0.000045, lon + 0.000045],
    [lat - 0.000045, lon + 0.000045],
    [lat - 0.000045, lon - 0.000030],
    [lat + 0.000045, lon - 0.000030] # Close loop
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
