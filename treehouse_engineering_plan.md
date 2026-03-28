# Project Skyward — Engineering & CAD Bill of Materials

## 1. Multi-Tree Structural Approach (Floating Yoke Method)
The design supports three independent platforms—one per tree—connected by rigid wooden gangways. Each tree bears its own yoke frame, entirely tree-supported with no ground posts. Slotted dynamic brackets on the TABs allow each tree to sway independently without transferring stress to adjacent platforms.

**Tree Coordinates (normalized, meters):**
| Tree | X | Y | Notes |
|------|-------|------|-------|
| T1 | −2.44 | 0.00 | West anchor |
| T2 | 1.29 | 0.06 | Middle (60 mm off-axis) |
| T3 | 2.44 | 0.00 | East anchor |

Outer span (T1–T3): **16 ft (4.88 m)**. Terrain grade ≈ 7%.

## 2. Bill of Materials — Attainable Design (2.0 m / 6.5 ft elevation)
### Hardware
| Qty | Item | Spec | Purpose |
|-----|------|------|---------|
| 6 | TABs (Treehouse Attachment Bolts) | 1.25″ shaft, 3″ boss | 2 per tree — primary vertical load |
| 6 | Slotted Dynamic Brackets | Simpson or equivalent | Allow yoke beams to slide on TAB collars |
| 6 | Lag Bolts | 1″ × 12″ | Knee-brace connections (optional safety tie) |
| ~400 | Star-Drive Deck Screws | 3″ | Joist & decking fasteners |
| ~36 | Hurricane Ties | Simpson Strong-Tie | Joist-to-beam connections |

### Lumber (Pressure-Treated frame / Cedar deck)
| Qty | Size | Length | Purpose |
|-----|------|--------|---------|
| 12 | 2×10 | 8′ | Yoke beams (doubled, 2 yokes × 3 trees) |
| ~18 | 2×8 | varies | Floor joists at 16″ OC (~6 per platform) |
| ~80 | 5/4″ × 5.5″ Cedar | varies | Decking boards (0.25″ gaps, split around trunks) |
| ~24 | 4×4 | 3′ | Railing posts (36″ height) |
| ~24 | 2×4 Cedar | varies | Top rails and balusters |

### Gangway Lumber (2 rigid walkways)
| Qty | Size | Length | Purpose |
|-----|------|--------|---------|
| 4 | 2×10 | ~12′ | Walkway stringers (doubled, T1↔T2 and T2↔T3) |
| ~16 | 2×8 | 4′ | Cross-joists at 16″ OC |
| ~20 | 5/4″ × 5.5″ Cedar | 4′ | Walkway decking |

## 3. Order of Operations
1. **Leveling & Survey**: Confirm the 16 ft span on-site (see `validate_gis.py` for independent GIS cross-validation). Mark the 2.0 m elevation line on each trunk.
2. **Drill & Mount TABs**: Install 2 TABs per tree at the 2.0 m mark, spaced 0.5 m apart vertically. Use dynamic brackets.
3. **Construct Yoke Frames**: Mount doubled 2×10 beams onto the dynamic brackets at each tree.
4. **Set Joists**: Lay 2×8 joists across the yoke beams at 16″ OC. *Leave a 0.35 m growth gap around each trunk.*
5. **Install Decking**: Fasten 5/4″ cedar planks across joists, scribing cutouts around trunks.
6. **Build Gangways**: Erect the rigid walkway stringers between T1↔T2 and T2↔T3. Cross-joist and deck.
7. **Install Railings**: 36″ child-safe railings on all platforms and gangways.
8. **Inspect**: Full structural inspection before use.

## 4. Professional Variant (Multi-Level)
The `pro_build.py` script generates a multi-level variant with:
- T1 at 5.0 m, T2 at 7.0 m, T3 at 9.0 m
- Larger yoke radius (1.6 m), ~9 joists per platform
- 39″ railings, cable suspension bridges between platforms
- Output: `Professional_Skyward_Corrected.blend`

## 5. Blender CAD Script Reference
| Script | Output | Design |
|--------|--------|--------|
| `attainable_build.py` | `Attainable_Skyward.blend` | Recommended: safe 6.5 ft, rigid spans |
| `pro_build.py` | `Professional_Skyward_Corrected.blend` | Multi-level (16–30 ft), cable bridges |
| `build_skywalk.py` | `Skyward_MultiTree.blend` | Conceptual demo with suspension bridges |
| `build_treehouse.py` | `Project_Skyward.blend` | Legacy single-tree design (superseded) |

All CAD scripts import the corrected LIDAR mesh from `stl_files/grounds_clean.stl` and generate exact dimensional lumber locked to the scanned tree positions.
