"""Print-in-place chain with toggle clasps, sized for the medallion.

The chain prints flat, already linked, with no supports. It has two kinds of link:
  * flat links  - rounded rectangular rings lying on the bed
  * bridges     - solid staples whose feet sit inside neighbouring flat links
                  and arch (45 degree ramps, self-supporting) over their end bars
Bed space limits one piece, so the necklace is SEGMENTS pieces. Each piece starts
with a toggle RING and ends with a toggle T-BAR, so pieces clip together, and the
last joint is the clasp you open to put it on. To hang the medallion, feed a
T-bar through its loop before clipping that T-bar into the next ring.

Outputs: chain_segment.stl (one piece) and chain_plate.stl (all pieces laid out).
Requires: pip install manifold3d trimesh numpy
"""
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, JoinType

# ---------------- parameters (mm) ----------------
NECKLACE_LEN = 620      # total length when closed (~24 in)
SEGMENTS = 4            # pieces; each must fit on your bed (~155 mm each at 620/4)
GAP = 0.5               # print-in-place clearance (0.4-0.6 typical)

LO, WO = 14.0, 8.5      # flat link outer length / width
RW, RH = 1.8, 2.0       # flat link rail width / height
S = 1.0                 # bed gap between consecutive flat links
BW = 3.5                # bridge width
BT = 2.0                # bridge vertical thickness
FOOT = 1.6              # bridge foot length
H = RH + GAP            # bridge underside height over the flat links
CLEAR = 0.45            # extra run so the ramp clears the bar corner

RING_ID = 10.0          # toggle ring inner diameter
TBAR_LEN, TBAR_W = 21.0, 2.6   # toggle bar (length across, along-chain width)
SEG = 48

P = LO + S              # pitch: one flat link + one bridge

def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def flat_link(x0):
    r = 1.5
    outer = CrossSection.square([LO - 2 * r, WO - 2 * r]).translate([r, r - WO / 2]).offset(
        r, JoinType.Round, circular_segments=SEG)
    inner = CrossSection.square([LO - 2 * RW, WO - 2 * RW]).translate([RW, RW - WO / 2])
    return (outer - inner).extrude(RH).translate([x0, 0, 0])

def toggle_ring(x0):
    """round ring placed so that, under the bridge, its rear rail sits where a flat link's does"""
    ri = RING_ID / 2
    ro = ri + RW
    cx = x0 + LO - RW - np.sqrt(ri ** 2 - (BW / 2) ** 2)
    ring = CrossSection.circle(ro, SEG * 2) - CrossSection.circle(RING_ID / 2, SEG * 2)
    return ring.extrude(RH).translate([cx, 0, 0]), cx - ro

def bridge(x0, tbar=False):
    """bridge connecting the flat link starting at x0 with the one starting at x0 + P"""
    a = x0 + LO - RW - CLEAR - H - FOOT        # front foot start
    b = 2 * (x0 + LO + S / 2) - a              # symmetric about the gap
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

def segment(n_links):
    """ring, then n_links flat links, then a T-bar. Returns (manifold, length)."""
    parts = []
    ring, start = toggle_ring(0)
    parts.append(ring)
    for i in range(1, n_links + 1):
        parts.append(flat_link(i * P))
    for i in range(0, n_links):
        parts.append(bridge(i * P))
    parts.append(bridge(n_links * P, tbar=True))
    # sanity: neighbouring parts must not touch
    for i, p in enumerate(parts):
        for q in parts[i + 1:]:
            assert (p ^ q).volume() < 1e-6, "links overlap - increase GAP/CLEAR"
    m = parts[0]
    for p in parts[1:]:
        m += p
    lo, hi = m.bounding_box()[0], m.bounding_box()[3]
    return m.translate([-start, 0, 0]), hi - start

# ring-to-bar length per piece; each joint uses up roughly a ring diameter of overlap
seg_target = NECKLACE_LEN / SEGMENTS + RING_ID
n = 1
while segment(n + 1)[1] <= seg_target:
    n += 1
seg, seg_len = segment(n)

def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)

here = os.path.dirname(os.path.abspath(__file__))
t = to_trimesh(seg)
assert t.is_watertight
t.export(os.path.join(here, "chain_segment.stl"))
plate = seg
for k in range(1, SEGMENTS):
    plate += seg.translate([0, k * (TBAR_LEN + 3), 0])
to_trimesh(plate).export(os.path.join(here, "chain_plate.stl"))
print(f"{n} flat links per piece, piece length {seg_len:.1f} mm, "
      f"plate {seg_len:.0f} x {(SEGMENTS - 1) * (TBAR_LEN + 3) + TBAR_LEN:.0f} mm, "
      f"approx necklace {SEGMENTS * (seg_len - RING_ID):.0f} mm")
