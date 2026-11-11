"""Print-in-place chain with toggle clasps, sized for the medallion.

The chain prints flat, already linked, with no supports. It has two kinds of link:
  * flat links  - lying on the bed; they alternate between gold rounded rectangles
                  and blue diamond "logo" links matching the medallion's emblem
  * bridges     - solid staples whose feet sit inside neighbouring flat links
                  and arch (45 degree ramps, self-supporting) over their end bars
Bed space limits one piece, so the necklace is SEGMENTS pieces. Each piece starts
with a toggle RING and ends with a toggle T-BAR, so pieces clip together, and the
last joint is the clasp you open to put it on. To hang the medallion, feed a
T-bar through its loop before clipping that T-bar into the next ring.

Outputs: chain_plate.stl (all pieces, one colour), chain_plate.3mf (gold + blue parts
for multi-colour printers), chain_plate_gold.stl / chain_plate_blue.stl (same parts as
separate STLs) and chain_segment.stl (one piece).
Requires: pip install manifold3d trimesh numpy
"""
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, JoinType

# ---------------- parameters (mm) ----------------
NECKLACE_LEN = 760      # total length when closed (~30 in)
SEGMENTS = 2            # pieces: 2 = clasp at the back + medallion joint at the front
BED = (350, 350)        # print bed (mm); pieces are laid diagonally if they don't fit straight
BED_MARGIN = 10         # keep this far from the bed edges
GAP = 0.5               # print-in-place clearance (0.4-0.6 typical)

LO, WO = 14.0, 8.5      # flat link outer length / width
RW, RH = 1.8, 2.0       # flat link rail width / height
S = 1.0                 # bed gap between consecutive flat links
BW = 3.5                # bridge width
BT = 2.0                # bridge vertical thickness
FOOT = 1.6              # bridge foot length
H = RH + GAP            # bridge underside height over the flat links
CLEAR = 0.45            # extra run so the ramp clears the bar corner

# diamond "logo" links (every other flat link)
LOGO_LINKS = True
D_HALF = 10.0           # half-diagonal: 20 mm wide across the chain
D_TIP = 2.4             # the along-chain points are blunted to this half-width (they sit under the bridges)
D_HOLE = 0.56           # open centre as a fraction of the outer size (same look as the medallion)
SLOT = BW / 2 + GAP + 0.05   # clearance channel for the bridge where it crosses the diamond's points
LD = 2 * (D_HALF - D_TIP)    # diamond link length along the chain

RING_ID = 10.0          # toggle ring inner diameter
TBAR_LEN, TBAR_W = 21.0, 2.6   # toggle bar (length across, along-chain width)
SEG = 48

def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def flat_link(x0):
    r = 1.5
    outer = CrossSection.square([LO - 2 * r, WO - 2 * r]).translate([r, r - WO / 2]).offset(
        r, JoinType.Round, circular_segments=SEG)
    inner = CrossSection.square([LO - 2 * RW, WO - 2 * RW]).translate([RW, RW - WO / 2])
    return (outer - inner).extrude(RH).translate([x0, 0, 0])

def diamond_link(x0):
    """diamond frame, points blunted along the chain so each end is a straight bar like a flat link's"""
    cx = x0 + LD / 2
    def dia(h):
        return CrossSection([[(cx + h, 0), (cx, h), (cx - h, 0), (cx, -h)]])
    outer = dia(D_HALF) ^ CrossSection.square([LD, 2 * D_HALF + 2]).translate([x0, -D_HALF - 1])
    inner = dia(D_HALF * D_HOLE) + CrossSection.square([LD - 2 * RW, 2 * SLOT]).translate([x0 + RW, -SLOT])
    assert cx - D_HALF * D_HOLE >= x0 + RW, "diamond hole would cut through the end bar"
    return (outer - inner).extrude(RH)

def toggle_ring(x_end):
    """round ring ending at x_end, placed so that under the bridge its rear rail sits where a flat link's does"""
    ri = RING_ID / 2
    ro = ri + RW
    cx = x_end - RW - np.sqrt(ri ** 2 - (BW / 2) ** 2)
    ring = CrossSection.circle(ro, SEG * 2) - CrossSection.circle(RING_ID / 2, SEG * 2)
    return ring.extrude(RH).translate([cx, 0, 0]), cx - ro

def bridge(x_end, tbar=False):
    """bridge from the flat link ending at x_end over the gap S to the next one"""
    a = x_end - RW - CLEAR - H - FOOT          # front foot start
    b = 2 * (x_end + S / 2) - a                # symmetric about the gap
    rear_foot = TBAR_W if tbar else FOOT
    if tbar:
        b = b - FOOT + TBAR_W
    bottom = [(a, 0), (a + FOOT, 0), (a + FOOT + H, H),
              (b - rear_foot - H, H), (b - rear_foot, 0), (b, 0)]
    top = [(x, z + BT) for x, z in reversed(bottom)]
    prof = CrossSection([bottom + top])                       # profile in (x, z)
    m = prof.extrude(BW).rotate([90, 0, 0]).translate([0, BW / 2, 0])
    if tbar:
        m += box(b - TBAR_W, b, -TBAR_LEN / 2, TBAR_LEN / 2, 0, BT)
    return m

def union(ms):
    out = ms[0]
    for m in ms[1:]:
        out += m
    return out

def segment(n_links, check=False):
    """ring, n_links flat links (alternating gold / blue diamond), T-bar.
    Returns (gold manifold, blue manifold or None, length)."""
    ring, start = toggle_ring(LO)
    gold, blue, order = [ring], [], [ring]
    ends = [LO]
    for i in range(1, n_links + 1):
        x0 = ends[-1] + S
        if LOGO_LINKS and i % 2 == 0:
            link = diamond_link(x0); blue.append(link); ends.append(x0 + LD)
        else:
            link = flat_link(x0); gold.append(link); ends.append(x0 + LO)
        order.append(link)
    bridges = [bridge(e) for e in ends[:-1]] + [bridge(ends[-1], tbar=True)]
    gold += bridges
    if check:   # parts must not touch: each bridge vs every link, and links vs each other
        for p in bridges:
            for q in order:
                assert (p ^ q).volume() < 1e-6, "links overlap - increase GAP/CLEAR"
        for p, q in zip(order, order[1:]):
            assert (p ^ q).volume() < 1e-6, "links overlap"
        for p, q in zip(bridges, bridges[1:]):
            assert (p ^ q).volume() < 1e-6, "bridges overlap - links too short"
    g = union(gold).translate([-start, 0, 0])
    bl = union(blue).translate([-start, 0, 0]) if blue else None
    length = (g + bl if bl else g).bounding_box()[3]
    return g, bl, length

# ring-to-bar length per piece; each joint uses up roughly a ring diameter of overlap
seg_target = NECKLACE_LEN / SEGMENTS + RING_ID
n = 1
while segment(n + 1)[2] <= seg_target:
    n += 1
if abs(segment(n + 1)[2] - seg_target) < abs(segment(n)[2] - seg_target):
    n += 1          # pick the link count closest to the requested length
seg_gold, seg_blue, seg_len = segment(n, check=True)

def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)

def centre_offset(m):
    b = m.bounding_box()
    return [-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]]

def fits(m):
    b = m.bounding_box()
    return b[3] - b[0] <= BED[0] - 2 * BED_MARGIN and b[4] - b[1] <= BED[1] - 2 * BED_MARGIN

here = os.path.dirname(os.path.abspath(__file__))
seg_all = seg_gold + seg_blue if seg_blue else seg_gold
t = to_trimesh(seg_all)
assert t.is_watertight
t.export(os.path.join(here, "chain_segment.stl"))

# lay out SEGMENTS pieces side by side; same transform for the gold and blue parts
spacing = max(TBAR_LEN, 2 * D_HALF if LOGO_LINKS else WO) + 3
def layout(m, rot):
    out = union([m.translate([0, k * spacing, 0]) for k in range(SEGMENTS)])
    return out.rotate([0, 0, rot])
rot = 0
if not fits(layout(seg_all, 0)):
    rot = 45
plate_all = layout(seg_all, rot)
assert fits(plate_all), "pieces don't fit the bed - increase SEGMENTS"
off = centre_offset(plate_all)
plate_all = plate_all.translate(off)
to_trimesh(plate_all).export(os.path.join(here, "chain_plate.stl"))

scene = trimesh.Scene()
for name, m, col in [("gold", seg_gold, [212, 175, 55, 255]), ("blue", seg_blue, [30, 70, 200, 255])]:
    if m is None:
        continue
    pm = to_trimesh(layout(m, rot).translate(off))
    pm.export(os.path.join(here, f"chain_plate_{name}.stl"))
    pm.visual.face_colors = col
    scene.add_geometry(pm, node_name=name, geom_name=name)
scene.export(os.path.join(here, "chain_plate.3mf"))

b = plate_all.bounding_box()
print(f"{n} flat links per piece ({n // 2 if LOGO_LINKS else 0} diamonds), piece length {seg_len:.1f} mm, "
      f"plate {b[3] - b[0]:.0f} x {b[4] - b[1]:.0f} mm ({'diagonal' if rot else 'straight'}), "
      f"approx necklace {SEGMENTS * (seg_len - RING_ID):.0f} mm")
