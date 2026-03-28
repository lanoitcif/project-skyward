# Project Skyward - Central Documentation

## 1. Project Goals
Project Skyward's ultimate vision has evolved into a professional, high-elevation multi-tree architecture. The primary goal is to safely and sustainably construct multiple interconnected treehouse platforms suspended roughly 15-30ft high across a linear grove of three massive, structurally sound trees. These high-elevation decks are joined by dramatic 'Sky Walk' suspension bridges, while ensuring the long-term health and stability of the host trees. 

## 2. Work Completed to Date
- **Critical Site Subsurface Analysis**: We deeply analyzed the native lidar `.stl` scan of the grounds. We discovered the original drone capture assigned absolute height to the Y-axis. We mathematically corrected the rotation to Z-up, leveled the ground mesh to absolute Z=0, and ran a slicing operation that perfectly mapped the physical world-coordinates of the three major tree trunks. They rest in a linear row spanning ~16 feet!
- **Engineering Blueprint**: Designed a "Multi-Tree Yoke" foundation strategy utilizing floating Treehouse Attachment Bolts (TABs) to allow independent tree sway, completely avoiding ground posts.
- **Professional Procedural CAD Generation**: We abandoned early conceptual blocks to procedurally generate a true engineering-grade architecture file (`Professional_Skyward_Corrected.blend`). This script mathematically generates exact, dimensional treated lumber:
    - Doubled 2x10 Yoke beams anchored to the exact LIDAR tree coordinates.
    - 2x8 floor joists spaced physically at 16" O.C (On-Center).
    - Individual 5/4" Cedar decking boards with 1/4" spacing algorithmically wrapped around the trunks.
    - Missing upper tree canopies were mathematically extrapolated so the high platforms attach logically to the trunks.
- **Web-based Layout Viewer**: A local interactive HTML/Three.js viewer was provided in the `/viewer` directory to quickly preview footprint dimension changes without heavy CAD tooling.

## 3. Long Term Plans & Next Steps
1. **CAD Refinement**: The architectural team must review `Skyward_MultiTree.blend` natively in Blender to build upon the completed foundation by detailing the suspension cables, platform sidewalls, and ground-access ladders.
2. **Arborist Review**: Before drilling the massive 3" diameter pilot holes for the Treehouse Attachment Bolts across three distinct trees, a certified arborist should physically evaluate the triad to ensure none possess hidden internal rot.
3. **Material Sourcing**: Begin procuring specialty TAB hardware, heavy-duty galvanized wire rope/cable for the sky walks, and locally sourced pressure-treated lumber.

## 4. Key References in Workspace
- `treehouse_engineering_plan.md` - Primary foundational instructions and materials list.
- `Professional_Skyward_Corrected.blend` - **[NEW]** The master 3D engineering-grade CAD model featuring dimensional lumber and suspension bridges mapped natively to the cleaned lidar scan.
- `stl_files/grounds_clean.stl` - The rotation-corrected and leveled topography mesh.
- `viewer/index.html` - Rapid prototype viewer for fast footprint scale visualization.
