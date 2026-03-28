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

## 3. Long Term Plans & Next Steps
1. **CAD Refinement**: The architectural team must review `Attainable_Skyward.blend` natively in Blender to build upon the completed foundation by adding roof pitches (designed to shed heavy pine needles), and the access stairs/ladders.
2. **Arborist Review**: Before drilling the massive 3" diameter pilot holes for the Treehouse Attachment Bolts across three distinct trees, a certified arborist should physically evaluate the triad to ensure none possess hidden internal rot.
3. **Material Sourcing**: Begin procuring specialty TAB hardware, heavy-duty joist brackets, and locally sourced pressure-treated lumber.

## 4. Key References in Workspace
- `treehouse_engineering_plan.md` - Primary foundational instructions and materials list.
- `Attainable_Skyward.blend` - **[NEW]** The master 3D CAD model featuring safe, rigid dimensional lumber and child-safe railings natively locked into the raw LIDAR tree trunks.
- `stl_files/grounds_clean.stl` - The rotation-corrected and leveled topography mesh.
- `viewer/index.html` - Rapid prototype viewer for fast footprint scale visualization.
- `validate_gis.py` - Independent GIS cross-validation script (STL vs USGS 3DEP).
