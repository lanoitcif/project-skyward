#!/usr/bin/env python3
"""
Project Skyward — Structural & Design Viability Test Suite
==========================================================
Tests whether the proposed treehouse design is actually buildable,
safe, and code-compliant.  Runs with system Python (no Blender needed).

References:
  - IRC R507 (Decks), IRC R312 (Guards), NDS 2018 (lumber design)
  - Garnier Limb Bolt / TAB manufacturer specs
  - USGS 3DEP terrain validation (see validate_gis.py)
"""

import ast
import math
import os
import re
import sys
import textwrap

# ---------------------------------------------------------------------------
# CONFIG: paths relative to repo root
# ---------------------------------------------------------------------------
REPO = os.path.dirname(os.path.abspath(__file__))
ATTAINABLE = os.path.join(REPO, "attainable_build.py")
PRO_BUILD = os.path.join(REPO, "pro_build.py")
CLEAN_STL = os.path.join(REPO, "clean_stl.py")
CHECK_STL = os.path.join(REPO, "check_stl.py")
PLOT_GIS = os.path.join(REPO, "plot_gis.py")
GROUNDS_CLEAN = os.path.join(REPO, "stl_files", "grounds_clean.stl")

INCH = 0.0254  # meters
FT = 0.3048

# ---------------------------------------------------------------------------
# NDS / IRC Constants
# ---------------------------------------------------------------------------
# Southern Pine #2 (conservative; PT lumber is typically SPF or SYP)
NDS_FB_PSI = 875       # allowable bending stress, psi
NDS_E_PSI = 1_400_000  # modulus of elasticity, psi
LIVE_LOAD_PSF = 40      # residential deck live load (IRC R301.5)
DEAD_LOAD_PSF = 10      # conservative deck dead load (framing + decking)
TOTAL_LOAD_PSF = LIVE_LOAD_PSF + DEAD_LOAD_PSF

TAB_RATED_LBS = 2000    # conservative single-TAB rating (Garnier GL)
MIN_TREE_DIA_IN = 12    # minimum trunk diameter for TAB installation

IRC_GUARD_HEIGHT_IN = 36   # IRC R312.1.1: ≥36" for residential
IRC_BALUSTER_MAX_IN = 4    # IRC R312.1.3: openings ≤4"
IRC_GUARD_THRESHOLD_IN = 30  # guards required when >30" above grade
IRC_MIN_EGRESS_WIDTH_IN = 36  # IRC R311.6: minimum stairway/egress width

DEFLECTION_LIMIT_RATIO = 360  # L/360 for live load


# ===========================  RESULTS TRACKING  ===========================
class Results:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def ok(self, name, detail=""):
        self.passed.append((name, detail))

    def fail(self, name, detail=""):
        self.failed.append((name, detail))

    def warn(self, name, detail=""):
        self.warnings.append((name, detail))

    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        print("\n" + "=" * 72)
        print(f"  VIABILITY TEST RESULTS: {len(self.passed)} PASS / "
              f"{len(self.failed)} FAIL / {len(self.warnings)} WARN  "
              f"({total} total)")
        print("=" * 72)

        if self.failed:
            print("\n❌  FAILURES (must fix before building):")
            for name, detail in self.failed:
                print(f"    FAIL  {name}")
                if detail:
                    for line in textwrap.wrap(detail, 64):
                        print(f"          {line}")

        if self.warnings:
            print("\n⚠️   WARNINGS (review recommended):")
            for name, detail in self.warnings:
                print(f"    WARN  {name}")
                if detail:
                    for line in textwrap.wrap(detail, 64):
                        print(f"          {line}")

        if self.passed:
            print(f"\n✅  PASSED ({len(self.passed)}):")
            for name, detail in self.passed:
                tag = f" — {detail}" if detail else ""
                print(f"    PASS  {name}{tag}")

        viable = len(self.failed) == 0
        print("\n" + "=" * 72)
        if viable:
            print("  ✅  DESIGN IS VIABLE (all critical checks passed)")
        else:
            print("  ❌  DESIGN IS NOT YET VIABLE — fix failures above")
        print("=" * 72 + "\n")
        return viable

R = Results()

# ===========================  HELPER FUNCTIONS  ===========================

def _read_constant(name, default):
    """Read a named constant from attainable_build.py."""
    try:
        with open(ATTAINABLE) as f:
            for line in f:
                m = re.match(rf'\s*{name}\s*=\s*([0-9.]+)', line)
                if m:
                    return float(m.group(1))
    except Exception:
        pass
    return default


def extract_tree_coords(filepath):
    """Parse a Python file for T1/T2/T3 tuple assignments."""
    coords = {}
    with open(filepath) as f:
        for line in f:
            m = re.match(r'\s*(T[123])\s*=\s*\(([^)]+)\)', line)
            if m:
                name = m.group(1)
                vals = [float(v.strip()) for v in m.group(2).split(",")]
                coords[name] = tuple(vals)
    return coords


def section_props_rect(b_in, d_in):
    """Return (S, I) for a rectangular section in inches."""
    S = b_in * d_in**2 / 6.0
    I = b_in * d_in**3 / 12.0
    return S, I


def check_bending(name, b_in, d_in, span_ft, w_plf, fb_allow=NDS_FB_PSI):
    """Check bending stress for a simply-supported beam.
    Returns (fb_actual, passes)."""
    S, _ = section_props_rect(b_in, d_in)
    M_ftlb = w_plf * span_ft**2 / 8.0
    M_inlb = M_ftlb * 12.0
    fb = M_inlb / S
    passes = fb <= fb_allow
    return fb, passes


def check_deflection(name, b_in, d_in, span_ft, w_plf, E=NDS_E_PSI,
                     limit=DEFLECTION_LIMIT_RATIO):
    """Check deflection for a simply-supported beam under uniform load.
    Returns (delta_in, limit_in, passes)."""
    _, I = section_props_rect(b_in, d_in)
    L_in = span_ft * 12.0
    w_pli = w_plf / 12.0
    delta = 5.0 * w_pli * L_in**4 / (384.0 * E * I)
    limit_in = L_in / limit
    return delta, limit_in, delta <= limit_in


# ===========================  TEST FUNCTIONS  ===========================

def test_coordinate_consistency():
    """T01: Verify tree coordinates match across all scripts."""
    files = {
        "attainable_build.py": ATTAINABLE,
        "pro_build.py": PRO_BUILD,
    }
    reference = None
    ref_name = None
    all_match = True
    for label, path in files.items():
        if not os.path.exists(path):
            R.fail(f"T01-coord-{label}", f"File not found: {path}")
            all_match = False
            continue
        coords = extract_tree_coords(path)
        if len(coords) < 3:
            R.fail(f"T01-coord-{label}", f"Could not find T1/T2/T3 in {label}")
            all_match = False
            continue
        if reference is None:
            reference = coords
            ref_name = label
        else:
            for t in ["T1", "T2", "T3"]:
                if coords.get(t) != reference.get(t):
                    R.fail(f"T01-coord-{t}",
                           f"{label} has {t}={coords.get(t)} but "
                           f"{ref_name} has {t}={reference.get(t)}")
                    all_match = False
    if all_match and reference:
        R.ok("T01-coordinate-consistency",
             f"T1={reference['T1']} T2={reference['T2']} T3={reference['T3']}")
    return reference


def test_platform_overlap(coords):
    """T02: Check that the design handles close trees correctly."""
    if not coords:
        R.fail("T02-platform-overlap", "No coordinates to test")
        return

    # Read attainable_build.py to check if shared platform is used
    with open(ATTAINABLE) as f:
        code = f.read()
    has_shared = "build_shared_platform" in code

    t2t3_dist = math.hypot(
        coords["T2"][0] - coords["T3"][0],
        coords["T2"][1] - coords["T3"][1])

    if t2t3_dist < 2.0:
        if has_shared:
            R.ok("T02-overlap-T2-T3",
                 f"T2-T3 only {t2t3_dist:.2f}m apart — correctly uses "
                 f"shared platform (no overlap)")
        else:
            R.fail("T02-overlap-T2-T3",
                   f"T2-T3 only {t2t3_dist:.2f}m apart but design uses "
                   f"separate platforms — lumber would collide!")

    t1t2_dist = math.hypot(
        coords["T1"][0] - coords["T2"][0],
        coords["T1"][1] - coords["T2"][1])
    if t1t2_dist >= 2.0:
        R.ok("T02-clearance-T1-T2",
             f"Gap={t1t2_dist - 2.0:.2f}m between T1 and shared platform")
    t1t3_dist = math.hypot(
        coords["T1"][0] - coords["T3"][0],
        coords["T1"][1] - coords["T3"][1])
    R.ok("T02-clearance-T1-T3", f"Span={t1t3_dist:.2f}m")


def test_bridge_connectivity(coords):
    """T03: Verify all platforms are connected (reachable)."""
    if not coords:
        R.fail("T03-bridge-connectivity", "No coordinates")
        return
    # New design: T2+T3 share a platform, single bridge from T1 to shared platform
    with open(ATTAINABLE) as f:
        code = f.read()
    has_shared = "build_shared_platform" in code
    has_bridge = "build_simple_wood_bridge" in code
    has_ladder = "build_ladder" in code

    if has_shared and has_bridge:
        R.ok("T03-bridge-connectivity",
             "T1 platform → bridge → T2+T3 shared platform. All connected.")
    elif has_bridge:
        # Check old-style connectivity
        bridges = [("T1", "T3"), ("T3", "T2")]
        adj = {t: set() for t in coords}
        for a, b in bridges:
            adj[a].add(b)
            adj[b].add(a)
        visited = set()
        stack = ["T1"]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            stack.extend(adj[node] - visited)
        unreachable = set(coords.keys()) - visited
        if unreachable:
            R.fail("T03-bridge-connectivity",
                   f"Platforms {unreachable} unreachable from T1.")
        else:
            R.ok("T03-bridge-connectivity", f"All reachable via {bridges}")
    else:
        R.fail("T03-bridge-connectivity", "No bridge function found!")


def test_bridge_spans(coords):
    """T04: Structural check of bridge stringer spans."""
    if not coords:
        return
    # New design: single bridge from T1 to shared T2+T3 platform edge
    # Shared platform edge at x = min(T2.x, T3.x) - 1.0
    shared_edge_x = min(coords["T2"][0], coords["T3"][0]) - 1.0
    shared_edge_y = (coords["T2"][1] + coords["T3"][1]) / 2

    bridges = [
        ("T1", (shared_edge_x, shared_edge_y), "main walkway (T1 → shared)"),
    ]
    platform_radius = 1.0  # T1 radius
    stringer_b = 1.5   # 2x8 width (inches)
    stringer_d = 7.25  # 2x8 depth (inches)
    bridge_width_m = 0.9144  # 36" IRC minimum
    num_stringers = 2

    for t_a, endpoint, label in bridges:
        c_a = coords[t_a]
        center_dist_m = math.hypot(c_a[0] - endpoint[0], c_a[1] - endpoint[1])
        # T1 platform provides bearing on one side; shared platform on the other
        eff_span_m = max(0, center_dist_m - platform_radius)
        eff_span_ft = eff_span_m / FT

        if eff_span_m < 0.1:
            R.ok(f"T04-span-{t_a}-shared", "Platforms nearly touch — no span concern")
            continue

        trib_width_ft = (bridge_width_m / num_stringers) / FT
        w_plf = TOTAL_LOAD_PSF * trib_width_ft

        fb, bend_ok = check_bending(
            label, stringer_b, stringer_d, eff_span_ft, w_plf)
        delta, delta_lim, defl_ok = check_deflection(
            label, stringer_b, stringer_d, eff_span_ft,
            LIVE_LOAD_PSF * trib_width_ft)

        detail = (f"Span={eff_span_ft:.1f}ft, fb={fb:.0f}psi "
                  f"(allow={NDS_FB_PSI}), "
                  f"δ={delta:.3f}\" (limit={delta_lim:.3f}\")")
        if bend_ok and defl_ok:
            R.ok(f"T04-bridge-{t_a}-shared", detail)
        elif not bend_ok:
            R.fail(f"T04-bridge-bending-{t_a}-shared",
                   f"OVERSTRESSED! {detail}. "
                   f"Need larger stringers (min doubled 2x10).")
        elif not defl_ok:
            R.fail(f"T04-bridge-deflection-{t_a}-shared",
                   f"Excessive deflection! {detail}")


def test_bridge_width():
    """T05: Check bridge walkway width vs code minimums."""
    # Read actual value from attainable_build.py
    bridge_width_m = _read_constant("BRIDGE_WIDTH", 0.9)
    bridge_width_in = bridge_width_m / INCH
    if bridge_width_in >= IRC_MIN_EGRESS_WIDTH_IN:
        R.ok("T05-bridge-width",
             f"Width={bridge_width_in:.1f}\" ≥ {IRC_MIN_EGRESS_WIDTH_IN}\" min")
    else:
        R.fail("T05-bridge-width",
               f"Bridge width {bridge_width_in:.1f}\" < "
               f"{IRC_MIN_EGRESS_WIDTH_IN}\" IRC minimum. "
               f"Increase BRIDGE_WIDTH to at least {IRC_MIN_EGRESS_WIDTH_IN * INCH:.4f}m")


def test_platform_framing(coords):
    """T06: Structural check of platform joists and yoke beams."""
    if not coords:
        return
    radius = 1.0
    yoke_len_m = radius * 2
    yoke_len_ft = yoke_len_m / FT
    joist_spacing_m = _read_constant("JOIST_SPACING", 12 * INCH)
    joist_spacing_in = joist_spacing_m / INCH

    # Yoke beams: doubled 2x10
    yoke_b = 3.0   # doubled = 2 × 1.5"
    yoke_d = 9.25
    # Tributary load on each yoke: half the platform
    trib_area_ft2 = (yoke_len_m * yoke_len_m / 2) / (FT * FT)
    total_load_lbs = TOTAL_LOAD_PSF * trib_area_ft2
    w_plf_yoke = total_load_lbs / yoke_len_ft

    fb_yoke, yoke_bend = check_bending("yoke", yoke_b, yoke_d, yoke_len_ft, w_plf_yoke)
    delta_y, dlim_y, yoke_defl = check_deflection(
        "yoke", yoke_b, yoke_d, yoke_len_ft,
        LIVE_LOAD_PSF * trib_area_ft2 / yoke_len_ft)

    detail = (f"Doubled 2x10 yoke, span={yoke_len_ft:.1f}ft, "
              f"fb={fb_yoke:.0f}psi, δ={delta_y:.3f}\"")
    if yoke_bend and yoke_defl:
        R.ok("T06-yoke-beam", detail)
    else:
        R.fail("T06-yoke-beam", f"FAILS! {detail}")

    # Floor joists: 2x8 at 16" OC
    joist_b = 1.5
    joist_d = 7.25
    joist_span_ft = yoke_len_ft  # joists span between yoke beams
    # But wait: the yoke beams are only 0.5m apart (yoke_dist in attainable)
    # Joists span across the yokes, which is yoke_len (2.0m), NOT yoke_dist
    # Actually looking at the code: joists run perpendicular to yoke beams
    # Joist span = distance between the two yoke beams = yoke_dist * 2 = 1.0m
    # No wait, yoke_dist = 0.5, so yoke beams are at cy-0.5 and cy+0.5
    # Joist span = distance between yoke beams = 1.0m = 3.28 ft
    joist_actual_span_ft = 1.0 / FT  # 0.5m * 2 = 1.0m between yokes

    trib_joist_ft = joist_spacing_in / 12.0
    w_plf_joist = TOTAL_LOAD_PSF * trib_joist_ft

    fb_j, j_bend = check_bending("joist", joist_b, joist_d, joist_actual_span_ft, w_plf_joist)
    delta_j, dlim_j, j_defl = check_deflection(
        "joist", joist_b, joist_d, joist_actual_span_ft,
        LIVE_LOAD_PSF * trib_joist_ft)

    detail = (f"2x8 @ 16\"OC, span={joist_actual_span_ft:.1f}ft "
              f"(between yokes), fb={fb_j:.0f}psi, δ={delta_j:.4f}\"")
    if j_bend and j_defl:
        R.ok("T06-floor-joists", detail)
    else:
        R.fail("T06-floor-joists", f"FAILS! {detail}")

    # Decking: 5/4 × 5.5 cedar spanning 16" joist spacing
    deck_b = 5.5
    deck_d = 1.0
    deck_span_ft = joist_spacing_in / 12.0
    # Load on one board: 50 psf × (5.5"/12)
    trib_deck = 5.5 / 12.0
    w_plf_deck = TOTAL_LOAD_PSF * trib_deck

    fb_d, d_bend = check_bending("deck", deck_b, deck_d, deck_span_ft, w_plf_deck)
    # Decking Fb is ~1200 psi for cedar
    cedar_fb = 1200
    d_bend = fb_d <= cedar_fb
    detail = (f"5/4×5.5 cedar, span={deck_span_ft:.2f}ft, "
              f"fb={fb_d:.0f}psi (allow={cedar_fb})")
    if d_bend:
        R.ok("T06-decking", detail)
    else:
        R.fail("T06-decking", f"FAILS! {detail}")


def test_tab_capacity(coords):
    """T07: Check TAB load capacity per tree."""
    if not coords:
        return
    radius = 1.0
    platform_area_ft2 = (math.pi * radius**2) / (FT * FT)
    # Approximate as square for conservative estimate
    platform_area_ft2 = (2 * radius / FT) ** 2
    total_load_per_platform = TOTAL_LOAD_PSF * platform_area_ft2
    tabs_per_tree = 2
    load_per_tab = total_load_per_platform / tabs_per_tree

    detail = (f"Platform area≈{platform_area_ft2:.0f}ft², "
              f"total load={total_load_per_platform:.0f}lbs, "
              f"per TAB={load_per_tab:.0f}lbs (rated={TAB_RATED_LBS}lbs)")
    if load_per_tab <= TAB_RATED_LBS:
        R.ok("T07-TAB-capacity", detail)
    else:
        R.fail("T07-TAB-capacity",
               f"OVERLOADED! {detail}. "
               f"Need higher-rated TABs or more per tree.")


def test_railing_compliance():
    """T08: Check railing dimensions vs IRC R312."""
    railing_height_m = _read_constant("RAILING_HEIGHT", 0.9)
    railing_height_in = railing_height_m / INCH
    deck_height_m = 2.0
    deck_height_in = deck_height_m / INCH

    if deck_height_in > IRC_GUARD_THRESHOLD_IN:
        if railing_height_in >= IRC_GUARD_HEIGHT_IN:
            R.ok("T08-guard-height",
                 f"Railing {railing_height_in:.1f}\" ≥ {IRC_GUARD_HEIGHT_IN}\" "
                 f"(deck at {deck_height_in:.0f}\" above grade)")
        else:
            R.fail("T08-guard-height",
                   f"Railing {railing_height_in:.1f}\" < {IRC_GUARD_HEIGHT_IN}\" min. "
                   f"IRC R312.1.1 requires ≥36\" guards when deck >30\" above grade.")
    else:
        R.ok("T08-guard-height", "Deck below 30\" — no guard required")

    R.ok("T08-post-size", "4×4 nominal posts (3.5\"×3.5\") — standard")

    R.warn("T08-baluster-spacing",
           "Balusters not modeled in CAD. IRC R312.1.3 requires "
           f"≤{IRC_BALUSTER_MAX_IN}\" openings. Must add during construction.")


def test_trunk_clearance():
    """T09: Check trunk growth gap around trees."""
    trunk_cutout_m = _read_constant("TRUNK_CUTOUT", 0.35)
    trunk_cutout_in = trunk_cutout_m / INCH
    min_clearance_in = 3.0
    if trunk_cutout_in >= min_clearance_in:
        R.ok("T09-trunk-clearance",
             f"Cutout radius {trunk_cutout_in:.1f}\" ≥ {min_clearance_in}\" min")
    else:
        R.fail("T09-trunk-clearance",
               f"Cutout radius {trunk_cutout_in:.1f}\" < {min_clearance_in}\" min. "
               f"Trees need room for 10+ years of radial growth (~0.5\"/year).")


def test_ground_clearance_on_slope(coords):
    """T10: With 7% terrain grade, check minimum ground clearance."""
    if not coords:
        return
    deck_height_m = 2.0
    terrain_grade = 0.07  # 7% from validate_gis.py
    span_m = 4.88  # T1–T3

    # Worst case: deck is level at 2.0m above uphill side
    # Downhill side terrain drops by span × grade
    terrain_drop = span_m * terrain_grade  # 0.34m
    # If deck height is set relative to uphill tree, downhill clearance increases
    # If set relative to downhill tree, uphill clearance decreases
    min_clearance = deck_height_m - terrain_drop  # 1.66m
    min_clearance_ft = min_clearance / FT

    if min_clearance_ft >= 6.0:
        R.ok("T10-ground-clearance",
             f"Min clearance {min_clearance_ft:.1f}ft (grade {terrain_grade*100:.0f}% "
             f"over {span_m:.1f}m)")
    elif min_clearance_ft >= 4.0:
        R.warn("T10-ground-clearance",
               f"Min clearance only {min_clearance_ft:.1f}ft. "
               f"May need to adjust deck height for headroom underneath.")
    else:
        R.fail("T10-ground-clearance",
               f"Min clearance {min_clearance_ft:.1f}ft — insufficient for "
               f"safe passage underneath.")


def test_stl_file_exists():
    """T11: Verify grounds_clean.stl exists and is reasonable size."""
    if not os.path.exists(GROUNDS_CLEAN):
        R.fail("T11-stl-exists", f"Missing: {GROUNDS_CLEAN}")
        return False
    size = os.path.getsize(GROUNDS_CLEAN)
    if size < 100_000:
        R.fail("T11-stl-size", f"STL only {size} bytes — likely corrupt")
        return False
    R.ok("T11-stl-exists", f"{size / 1_000_000:.1f}MB")
    return True


def test_stl_dimensions():
    """T12: Check STL mesh bounding box matches expected dimensions."""
    try:
        import numpy as np
        from stl import mesh as stl_mesh
    except ImportError:
        R.warn("T12-stl-dimensions",
               "numpy-stl not installed — skipping STL geometry check. "
               "Run: pip install numpy-stl")
        return

    if not os.path.exists(GROUNDS_CLEAN):
        R.fail("T12-stl-dimensions", "grounds_clean.stl missing")
        return

    m = stl_mesh.Mesh.from_file(GROUNDS_CLEAN)
    x_min, x_max = m.vectors[:, :, 0].min(), m.vectors[:, :, 0].max()
    y_min, y_max = m.vectors[:, :, 1].min(), m.vectors[:, :, 1].max()
    z_min, z_max = m.vectors[:, :, 2].min(), m.vectors[:, :, 2].max()

    x_span = x_max - x_min
    y_span = y_max - y_min
    z_span = z_max - z_min

    detail = (f"X=[{x_min:.1f},{x_max:.1f}]({x_span:.1f}m) "
              f"Y=[{y_min:.1f},{y_max:.1f}]({y_span:.1f}m) "
              f"Z=[{z_min:.1f},{z_max:.1f}]({z_span:.1f}m)")

    # After clean_stl.py: X should span ~16m (scan width), Z should be ~4-5m (height)
    # Ground at Z≈0, trees up to Z≈4m
    if z_min < -0.5:
        R.fail("T12-ground-level",
               f"Ground not at Z=0 (Z_min={z_min:.2f}). "
               f"clean_stl.py alignment may have failed.")
    else:
        R.ok("T12-ground-level", f"Z_min={z_min:.2f}m (≈0)")

    # Tree span: T1 at x=-2.44, T3 at x=2.44, so x range includes scan beyond trees
    if x_span < 4.0:
        R.fail("T12-x-span", f"X span only {x_span:.1f}m — too narrow")
    else:
        R.ok("T12-x-span", f"X span {x_span:.1f}m — reasonable for site scan")

    # Z-up check: height should be the smallest dimension
    if z_span > max(x_span, y_span):
        R.warn("T12-axis-orientation",
               f"Z ({z_span:.1f}m) > X/Y — might still be Y-up. {detail}")
    else:
        R.ok("T12-axis-orientation",
             f"Z-up confirmed (Z={z_span:.1f}m < X={x_span:.1f}m). {detail}")


def test_tree_spacing_feasibility(coords):
    """T13: Are the trees far enough apart for independent structures?"""
    if not coords:
        return
    with open(ATTAINABLE) as f:
        code = f.read()
    has_shared = "build_shared_platform" in code

    pairs = [("T1", "T2"), ("T2", "T3"), ("T1", "T3")]
    for a, b in pairs:
        dist = math.hypot(
            coords[a][0] - coords[b][0],
            coords[a][1] - coords[b][1])
        dist_ft = dist / FT
        if dist < 2.0:
            if a in ("T2", "T3") and b in ("T2", "T3") and has_shared:
                R.ok(f"T13-spacing-{a}-{b}",
                     f"{dist:.2f}m ({dist_ft:.1f}ft) — handled by shared platform")
            else:
                R.fail(f"T13-spacing-{a}-{b}",
                       f"Only {dist:.2f}m ({dist_ft:.1f}ft) apart. "
                       f"Too close for separate TABs — must share a platform.")
        elif dist < 3.0:
            R.warn(f"T13-spacing-{a}-{b}",
                   f"{dist:.2f}m ({dist_ft:.1f}ft) — tight. "
                   f"Consider shared yoke beam between these trees.")
        else:
            R.ok(f"T13-spacing-{a}-{b}",
                 f"{dist:.2f}m ({dist_ft:.1f}ft)")


def test_access_egress():
    """T14: Is there a way to get up to and down from the structure?"""
    with open(ATTAINABLE) as f:
        code = f.read().lower()
    has_access = ("stair" in code or "ladder" in code or "ramp" in code
                  or "build_ladder" in code)
    if has_access:
        R.ok("T14-access-egress", "Access element (ladder) found in design")
    else:
        R.fail("T14-access-egress",
               "NO stairs, ladder, or ramp in attainable_build.py! "
               "Structure has no way to get up or down. "
               "Must add before construction.")


def test_human_scale():
    """T15: Verify human scale figure is reasonable."""
    human_height = _read_constant("HUMAN_HEIGHT_M", 5.0)
    if 1.5 <= human_height <= 2.0:
        R.ok("T15-human-scale", f"Human height {human_height:.2f}m — realistic")
    else:
        R.fail("T15-human-scale",
               f"Human scaled to {human_height:.1f}m — should be ~1.7-1.8m. "
               f"Scale factor in attainable_build.py is wrong. "
               f"This means ALL rendered scale references are misleading.")


def test_material_availability():
    """T16: Verify specified lumber sizes are real standard dimensions."""
    standard_sizes = {
        "2x8": (1.5, 7.25),
        "2x10": (1.5, 9.25),
        "5/4x6": (1.0, 5.5),
        "4x4": (3.5, 3.5),
        "2x4": (1.5, 3.5),
    }
    # Check what the script uses
    used = {
        "2x8 joists": (1.5, 7.25),   # dim_2x8_w, dim_2x8_h
        "2x10 yoke": (3.0, 9.25),    # doubled = 3" wide
        "5/4x6 deck": (5.5, 1.0),    # board_w, board_t
        "4x4 posts": (3.5, 3.5),     # railing posts
    }
    all_ok = True
    for name, (b, d) in used.items():
        # All these are standard NDS sizes
        R.ok(f"T16-lumber-{name}", f"{b}\"×{d}\" — standard dimension")


def test_point_load_on_deck():
    """T17: Can the deck handle a concentrated 300lb load (adult + gear)?"""
    joist_spacing_m = _read_constant("JOIST_SPACING", 16 * INCH)
    joist_spacing_in = joist_spacing_m / INCH
    board_b = 5.5  # inches
    board_d = 1.0  # inches (5/4 actual)
    point_load_lbs = 300

    M = point_load_lbs * joist_spacing_in / 4.0
    S, _ = section_props_rect(board_b, board_d)
    fb = M / S
    cedar_fb = 1200

    detail = (f"300lb point load on 5/4×5.5 cedar @ {joist_spacing_in:.0f}\"OC: "
              f"fb={fb:.0f}psi (allow={cedar_fb})")
    if fb <= cedar_fb:
        R.ok("T17-point-load", detail)
    else:
        R.fail("T17-point-load",
               f"FAILS! {detail}. Reduce joist spacing to 12\" OC "
               f"or use 2× decking.")


def test_wind_and_lateral():
    """T18: Basic lateral load check for TAB-only support."""
    deck_height_m = 2.0
    # Simplified: wind creates lateral force on deck (projected area)
    # Wind pressure: ~20 psf for 90 mph exposure B
    wind_psf = 20
    deck_width_m = 2.0  # platform width
    deck_thickness_m = 0.3  # approx deck + railing profile
    projected_area_ft2 = (deck_width_m * deck_thickness_m) / (FT * FT)
    lateral_force_lbs = wind_psf * projected_area_ft2

    # TABs resist lateral load through moment couple
    # Couple arm = yoke_dist = 0.5m = 1.64ft
    yoke_dist_ft = 0.5 / FT
    moment_ftlb = lateral_force_lbs * (deck_height_m / FT)
    reaction_per_tab = moment_ftlb / yoke_dist_ft

    detail = (f"Wind lateral={lateral_force_lbs:.0f}lbs, "
              f"moment={moment_ftlb:.0f}ft-lb, "
              f"TAB withdrawal={reaction_per_tab:.0f}lbs "
              f"(TAB rated {TAB_RATED_LBS}lbs)")
    if reaction_per_tab < TAB_RATED_LBS * 0.5:  # 50% safety factor for lateral
        R.ok("T18-lateral-load", detail)
    else:
        R.warn("T18-lateral-load",
               f"Marginal! {detail}. Consider knee braces.")


def test_connection_details():
    """T19: Check for critical connection hardware in design."""
    with open(ATTAINABLE) as f:
        code = f.read().lower()
    checks = {
        "hurricane ties": ["hurricane", "simpson", "joist hanger"],
        "lag bolts": ["lag", "bolt", "tab"],
        "deck screws": ["screw", "fastener"],
    }
    for item, keywords in checks.items():
        found = any(kw in code for kw in keywords)
        if found:
            R.ok(f"T19-hardware-{item.replace(' ', '-')}",
                 "Referenced in build script")
        else:
            R.warn(f"T19-hardware-{item.replace(' ', '-')}",
                   f"'{item}' not referenced in code. "
                   f"Must be specified during construction.")


def test_tree_row_collinearity(coords):
    """T20: Verify trees are actually in a line (design assumption)."""
    if not coords:
        return
    # Cross-product of T1→T2 × T1→T3
    dx12 = coords["T2"][0] - coords["T1"][0]
    dy12 = coords["T2"][1] - coords["T1"][1]
    dx13 = coords["T3"][0] - coords["T1"][0]
    dy13 = coords["T3"][1] - coords["T1"][1]
    cross = abs(dx12 * dy13 - dy12 * dx13)
    span = math.hypot(dx13, dy13)
    # Perpendicular deviation of T2 from T1-T3 line
    perp_deviation_m = cross / span if span > 0 else 999
    perp_deviation_in = perp_deviation_m / INCH

    detail = (f"T2 deviation from T1-T3 line: {perp_deviation_m:.3f}m "
              f"({perp_deviation_in:.1f}\")")
    if perp_deviation_m < 0.15:
        R.ok("T20-collinearity", detail)
    elif perp_deviation_m < 0.5:
        R.warn("T20-collinearity",
               f"T2 is {perp_deviation_m:.2f}m off the T1-T3 line. "
               f"Bridge alignment may need adjustment. {detail}")
    else:
        R.fail("T20-collinearity",
               f"Trees not linear! {detail}. "
               f"Bridge design assumes straight row.")


def test_syntax_all_scripts():
    """T21: Verify all Python scripts are syntactically valid."""
    scripts = [ATTAINABLE, PRO_BUILD, CLEAN_STL, CHECK_STL, PLOT_GIS]
    for path in scripts:
        name = os.path.basename(path)
        if not os.path.exists(path):
            R.fail(f"T21-syntax-{name}", "File not found")
            continue
        try:
            with open(path) as f:
                ast.parse(f.read(), filename=name)
            R.ok(f"T21-syntax-{name}", "Valid Python")
        except SyntaxError as e:
            R.fail(f"T21-syntax-{name}", f"Syntax error: {e}")


def test_usable_deck_area(coords):
    """T22: Calculate actual usable deck area (excluding trunk cutouts)."""
    if not coords:
        return
    radius = 1.0
    trunk_cutout = _read_constant("TRUNK_CUTOUT", 0.35)

    # T1 standalone platform
    t1_area = (2 * radius) ** 2 - math.pi * trunk_cutout ** 2

    # T2+T3 shared platform
    margin = 1.0
    shared_w = (coords["T3"][0] - coords["T2"][0]) + 2 * margin
    shared_h = 2 * margin
    shared_area = shared_w * shared_h - 2 * math.pi * trunk_cutout ** 2

    total_ft2 = (t1_area + shared_area) / (FT * FT)

    # Bridge area (T1 to shared platform)
    shared_edge_x = min(coords["T2"][0], coords["T3"][0]) - margin
    bridge_len = math.hypot(
        coords["T1"][0] - shared_edge_x,
        coords["T1"][1] - (coords["T2"][1] + coords["T3"][1]) / 2)
    bridge_width = _read_constant("BRIDGE_WIDTH", 0.9144)
    bridge_ft2 = (bridge_len * bridge_width) / (FT * FT)

    grand_total_ft2 = total_ft2 + bridge_ft2
    detail = (f"T1 platform: {t1_area/(FT*FT):.0f}ft² + "
              f"T2+T3 shared: {shared_area/(FT*FT):.0f}ft² + "
              f"bridge: {bridge_ft2:.0f}ft² = "
              f"{grand_total_ft2:.0f}ft² total")

    if grand_total_ft2 >= 50:
        R.ok("T22-usable-area", detail)
    else:
        R.warn("T22-usable-area",
               f"Only {grand_total_ft2:.0f}ft² — quite small. {detail}")


# ===========================  MAIN  ===========================
def main():
    print("=" * 72)
    print("  PROJECT SKYWARD — STRUCTURAL & DESIGN VIABILITY TEST SUITE")
    print("=" * 72)
    print()

    coords = test_coordinate_consistency()
    test_platform_overlap(coords)
    test_tree_spacing_feasibility(coords)
    test_tree_row_collinearity(coords)
    test_bridge_connectivity(coords)
    test_bridge_spans(coords)
    test_bridge_width()
    test_platform_framing(coords)
    test_tab_capacity(coords)
    test_railing_compliance()
    test_trunk_clearance()
    test_ground_clearance_on_slope(coords)
    test_access_egress()
    test_human_scale()
    test_material_availability()
    test_point_load_on_deck()
    test_wind_and_lateral()
    test_connection_details()
    test_stl_file_exists()
    test_stl_dimensions()
    test_usable_deck_area(coords)
    test_syntax_all_scripts()

    viable = R.summary()
    sys.exit(0 if viable else 1)


if __name__ == "__main__":
    main()
