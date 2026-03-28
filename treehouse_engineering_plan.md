# Project Skyward - Engineering & CAD BoM

## 1. Single Tree Structural Approach (The "Yoke" Method)
Building a 10x10ft foundation on a single, 30" diameter Eastern White Pine requires a heavy-duty, entirely tree-supported foundation. To accommodate tree growth and sway, hybrid ground-posts are **NOT** recommended for a high deck; differential movement will pull the frame apart in high winds.
**Solution:** A 4-point single-tree "Yoke" (or square Tribeam) supported by heavy knee braces resting entirely on the trunk.

## 2. Bill of Materials (BoM)
### Hardware (The Structural "Treehouse Hardware")
*   **4x 1.25" TABs (Treehouse Attachment Bolts)** with 3" diameter bosses. These support the main vertical load.
*   **4x 1" Lag Bolts** (12" length) for the lower knee-brace connections.
*   **4x Slotted Dynamic Brackets**. These allow the 2x10 yoke beams to sit on the TAB collars while sliding slightly as the tree bends.
*   **200x 3" star-drive deck screws**.
*   **Metal Hurricane Ties** (Simpson Strong-Tie) for joist connections.

### Lumber (Pressure Treated for Frame, Cedar for Decking)
*   **Yoke Beams (The core box):** 8x `2x10x8'` (Doubled up face-to-face to create four massive 3"x9.25" perimeter beams).
*   **Knee Braces (The supports):** 4x `4x6x8'` Timbers.
*   **Floor Joists:** 13x `2x8x10'` boards (set 16" on center).
*   **Decking:** 40x `5/4"x6"x10'` solid cedar planks.

## 3. Order of Operations
1. **Leveling & Surveying**: Use the existing ropes visible at the 8ft mark to demarcate the level line for the main TABs.
2. **Drill & Mount Lower Hardware**: Install the 4 lower lag bolts at the 3.5ft / 4ft height mark.
3. **Drill & Mount Upper TABs**: Install the 4 main heavy TABs directly into the trunk at the 8ft mark.
4. **Mount Knee Braces**: Hoist the heavy 4x6 timbers and secure them from the lower lag bolts angling 45 degrees up toward the upper TABs.
5. **Construct the Yoke**: Mount the dynamic structural brackets onto the TABs. Lift the doubled 2x10 beams into place and secure them to the brackets and to the top notches of the knee braces.
6. **Set Joists**: Lay the 2x8 joists across the 8x8 yoke beams. *CRITICALLY: Leave a physical 3-inch gap around the trunk so the joists never pinch the bark.*
7. **Install Decking**: Fasten the cedar boards across the joists, scribing a perfect circle around the tree trunk (maintaining the 3-inch growth gap).

## 4. Blender CAD Script Implementation
A sophisticated Python `bpy` script has been written (`build_treehouse.py`) to algorithmically scaffold these exact 3D components into a Blender environment overlaid precisely onto the LIDAR-scanned `grounds.stl`, producing a unified CAD file: `Project_Skyward.blend`.
