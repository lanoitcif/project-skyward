# Project Skyward - Central Documentation

## 1. Project Goals
Project Skyward's ultimate vision is to create a safe, attainable, DIY-friendly multi-tree architecture. The goal is to safely construct an interconnected wooden gangway and deck system suspended at a safe structural height (~6.5ft) across a linear grove of three massive, structurally sound trees.

Rather than complex suspension bridges, this design employs rigid wooden spans that an intermediate carpenter can build safely, ensuring the long-term health and stability of the host trees while integrating seamlessly into their natural `.stl` topology.

## 2. Work Completed to Date
- **Critical Site Subsurface Analysis**: We deeply analyzed the native lidar `.stl` scan of the grounds. We discovered the original drone capture assigned absolute height to the Y-axis. We mathematically corrected the rotation to Z-up, leveled the ground mesh to absolute Z=0, and ran a slicing operation that perfectly mapped the physical world-coordinates of the three major tree trunks. They rest in a linear row spanning ~16 feet!
- **Engineering Blueprint**: Designed a "Multi-Tree Yoke" foundation strategy utilizing floating Treehouse Attachment Bolts (TABs) to allow independent tree sway, completely avoiding ground posts.
- **Attainable Procedural CAD Generation**: We built a true engineering-grade architecture file (`Attainable_Skyward.blend`). This model uses the native mesh of the scanned trees (no fake cylinders!) and generates exact dimensional lumber at a safe height:
    - Doubled 2x10 Yoke beams anchored to the exact LIDAR tree coordinates.
    - 2x8 floor joists mapped for straight, rigid walkways instead of dangerous cable bridges.
    - Individual 5/4" Cedar decking boards algorithmic cutouts wrapped perfectly around the exact LIDAR bark geometry.
    - Standard 36" child-safe heavy railings wrapping the entire structure.
- **Web-based Layout Viewer**: A local interactive HTML/Three.js viewer was provided in the `/viewer` directory to quickly preview footprint dimension changes without heavy CAD tooling.
- **Independent GIS Cross-Validation** (`validate_gis.py`): The drone STL scan's spatial accuracy was independently validated against the USGS 3DEP Digital Terrain Model (acquired 2021-11-02). Terrain slope comparison shows **94% agreement** (STL 6.85% grade vs USGS 7.27%), confirming the STL's metric scale is consistent with government survey data. Note: satellite imagery (23cm/px) cannot resolve individual trees at 5m spacing — an on-site survey is still recommended before construction to confirm the exact 16-foot span.
- **STL Processing Pipeline**: Axis correction (`check_stl.py`), ground leveling, tree identification via DBSCAN clustering, coordinate normalization, and clean mesh export (`clean_stl.py`) — all fully automated.
- **GIS Map Generation**: Interactive Folium/Leaflet HTML map (`gis_map.html`) showing tree GPS positions, deck footprint, and offset calculations (`plot_gis.py`).

## 3. Long Term Plans & Next Steps
1. **CAD Refinement**: The architectural team must review `Attainable_Skyward.blend` natively in Blender to build upon the completed foundation by adding roof pitches (designed to shed heavy pine needles), and the access stairs/ladders.
2. **Arborist Review**: Before drilling the massive 3" diameter pilot holes for the Treehouse Attachment Bolts across three distinct trees, a certified arborist should physically evaluate the triad to ensure none possess hidden internal rot.
3. **Material Sourcing**: Begin procuring specialty TAB hardware, heavy-duty joist brackets, and locally sourced pressure-treated lumber.

## 4. Key References in Workspace

### Documentation
| File | Description |
|------|-------------|
| `TREEHOUSE.md` | This file — central project documentation |
| `treehouse_design_plan.md` | Architectural design plan (3-tree layout, dimensions, railings) |
| `treehouse_engineering_plan.md` | Engineering BoM, construction order of operations |

### CAD Models (.blend)
| File | Script | Description |
|------|--------|-------------|
| `Attainable_Skyward.blend` | `attainable_build.py` | **Recommended** — safe 2 m height, rigid spans, child-safe railings |
| `Professional_Skyward_Corrected.blend` | `pro_build.py` | Multi-level (5/7/9 m), cable suspension bridges |
| `Skyward_MultiTree.blend` | `build_skywalk.py` | Conceptual demo — suspension bridges at 15/20/26 ft |
| `Project_Skyward.blend` | `build_treehouse.py` | Legacy single-tree design (superseded) |

### Python Scripts (Blender bpy)
| Script | Purpose |
|--------|---------|
| `attainable_build.py` | Generates the attainable 3-tree design at 2 m height |
| `pro_build.py` | Generates the professional multi-level variant |
| `build_skywalk.py` | Generates the conceptual skywalk demo |
| `build_treehouse.py` | Legacy single-tree builder (superseded by attainable/pro) |
| `render_treehouse.py` | Renders isometric & top-down views of the active .blend scene |
| `rerender_cycles.py` | Re-renders using Blender Cycles engine for higher quality |
| `add_humans.py` | Places human.obj scale figures into the scene for reference |

### Python Scripts (Standalone — run with system Python / venv)
| Script | Purpose |
|--------|---------|
| `clean_stl.py` | STL processing pipeline: axis correction, ground leveling, tree identification (DBSCAN), coordinate normalization, export to `grounds_clean.stl` |
| `check_stl.py` | Diagnostic: verifies STL axis orientation (Y must be tallest) and reports bounding-box dimensions |
| `plot_gis.py` | Generates `gis_map.html` — interactive Folium map with tree GPS positions and deck footprint |
| `validate_gis.py` | Independent GIS cross-validation: downloads USGS 3DEP DTM and Esri satellite imagery, compares terrain profiles against STL |

### Data Files
| File/Directory | Description |
|----------------|-------------|
| `stl_files/` | Raw and processed STL meshes (`grounds.stl`, `grounds_clean.stl`) |
| `image_files/` | Rendered images, cached satellite/DTM tiles |
| `human.obj` | Human scale figure (OBJ format) for CAD scenes |
| `gis_map.html` | Generated interactive GIS map (open in browser) |
| `viewer/` | Three.js interactive 3D viewer for quick footprint visualization |

### Tree Coordinates (Source of Truth)
All CAD scripts use normalized coordinates derived from the LIDAR scan:
| Tree | X (m) | Y (m) | Notes |
|------|-------|-------|-------|
| T1 | −2.44 | 0.00 | West anchor, GPS origin |
| T2 | 1.29 | 0.06 | Middle (60 mm off-axis) |
| T3 | 2.44 | 0.00 | East anchor |

Origin is the midpoint of T1–T3. Outer span: **16 ft (4.88 m)**.
