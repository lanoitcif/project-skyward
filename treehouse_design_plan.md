# Project Skyward: Treehouse Architectural Design Plan

## 1. Site Constraints & Specifications
- **Support Trees:** Three mature Eastern White Pines (*Pinus strobus*) arranged in a near-linear row.
- **Tree Positions (normalized CAD coordinates):**
  - T1 = (−2.44, 0.00) — westernmost
  - T2 = ( 1.29, 0.06) — middle
  - T3 = ( 2.44, 0.00) — easternmost
- **Outer Span:** ~16 feet (4.88 m) between T1 and T3.
- **Terrain Grade:** ~7% slope (validated at 94% agreement with USGS 3DEP DTM).
- **Elevation:** All platforms at a safe **2.0 m (~6.5 ft)** above grade (attainable design).

## 2. Structural Foundation (Multi-Tree Yoke Method)
Each tree receives its own independent floating platform, eliminating ground posts entirely:
- **Primary Support:** 2 Treehouse Attachment Bolts (TABs) per tree with slotted dynamic brackets to allow independent trunk sway.
- **Yoke Beams:** Doubled 2×10 pressure-treated beams (3″ × 9.25″ effective) spanning the TAB collars, spaced 0.5 m apart per tree.
- **No Ground Posts:** The entire structure floats on the three trees, so differential ground settlement is not a concern.

## 3. Deck Layout & Framing
- **Individual Platforms:** Each tree gets a ~2.0 m radius deck centered on the trunk.
- **Clearance:** Decking boards are split around each trunk with a minimum 0.35 m gap for growth and sway (algorithmically cut in the CAD model).
- **Joists:** 2×8 pressure-treated boards at 16″ on-center (~6 joists per platform).
- **Decking:** 5/4″ × 5.5″ solid cedar planks with 0.25″ gaps for drainage.
- **Connecting Walks:** Rigid wooden gangways span between adjacent tree platforms, replacing dangerous suspension cables with solid framing.

## 4. Superstructure & Access
- **Deck Level (6.5 ft):** A unified walk-and-deck system connecting all three trees. Access via a secure wooden staircase at T1.
- **Railings:** 36″ high sturdy wooden railings with closely spaced vertical balusters on all platforms and gangways, meeting child-safety standards.
- **Future:** Roof pitches (designed to shed heavy pine needles) and access ladders to be added during CAD refinement.

## 5. Design Variants
| Variant | Script | Output | Height(s) | Notes |
|---------|--------|--------|-----------|-------|
| **Attainable** (recommended) | `attainable_build.py` | `Attainable_Skyward.blend` | 2.0 m (6.5 ft) | DIY-safe, rigid spans |
| **Professional** | `pro_build.py` | `Professional_Skyward_Corrected.blend` | 5/7/9 m | Multi-level, cable bridges |
| **Skywalk** (demo) | `build_skywalk.py` | `Skyward_MultiTree.blend` | 15/20/26 ft | Conceptual suspension demo |

## 6. Review & Editing
Use the provided `/viewer` interactive 3D tool to place your structure within the STL scan and visually modify the dimensions collaboratively with your team.
