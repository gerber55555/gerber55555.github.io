"""Print-in-place interlocking chain with toggle clasps, sized for the medallion.

The chain prints flat, already linked, with no supports. Two kinds of link alternate:
  * flat links   - lying on the bed: gold rounded rectangles alternating with blue
                   diamond "logo" links that match the medallion's emblem. Each end
                   bar is a small arch with a tunnel underneath.
  * connectors   - gold closed rectangular loops standing upright. The bottom rod
                   runs along the bed through the tunnels of two neighbouring flat
                   links, the posts rise inside their openings, and the top bar arches
                   over their end bars. Each flat link's end bar therefore passes
                   through a closed connector loop, so the links are truly interlocked.
The only overhangs are short (~6 mm) bridges, so no supports are needed.

Bed space limits one piece, so the necklace is SEGMENTS pieces. Each piece starts
with a toggle RING and ends with a toggle T-BAR, so pieces clip together, and one
joint is the clasp you open to put it on. To hang the medallion, feed a T-bar
through its loop before clipping that T-bar into the next ring.

Outputs: chain_plate.stl (all pieces, one colour), chain_plate.3mf (gold + blue parts
for multi-colour printers), chain_plate_gold.stl / chain_plate_blue.stl (same parts as
separate STLs) and chain_segment.stl (one piece).
Requires: pip install manifold3d trimesh numpy networkx lxml
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

# connectors (gold, standing loops)
BW = 3.5                # connector width across the chain
TC = 1.4                # bottom rod height (runs through the tunnels)
POST = 1.6              # post length along the chain
BT = 2.0                # top bar thickness

# flat links
LO, WO = 14.0, 8.5      # gold link outer length / width
RW = 1.8                # rail width
S = 1.0                 # bed gap between consecutive flat links
TB = 1.6                # thickness of the arched end bar above its tunnel
HB = TC + GAP           # tunnel height under each end bar
HL = HB + TB            # flat link height
TUN = BW / 2 + GAP      # tunnel half-width
TOP0 = HL + GAP         # underside of the connector's top bar

# diamond "logo" links (every other flat link)
LOGO_LINKS = True
D_HALF = 10.0           # half-diagonal: 20 mm wide across the chain
D_TIP = 3.8             # the along-chain points are blunted to this half-width (room for the tunnel arch)
D_HOLE = 0.56           # open centre as a fraction of the outer size (same look as the medallion)
SLOT = BW / 2 + GAP     # channel along the middle for the connector posts
LD = 2 * (D_HALF - D_TIP)    # diamond link length along the chain

RING_ID = 10.0          # toggle ring inner diameter
TBAR_LEN, TBAR_W = 21.0, 2.6   # toggle bar (length across, along-chain width)
SEG = 48

def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def tunnels(x0, x1):
    """cut the tunnels under the end bars of a flat link spanning x0..x1"""
    return (box(x0 - 1, x0 + RW + 0.6, -TUN, TUN, -1, HB)
            + box(x1 - RW - 0.6, x1 + 1, -TUN, TUN, -1, HB))

def flat_link(x0):
    r = 1.5
    outer = CrossSection.square([LO - 2 * r, WO - 2 * r]).translate([r, r - WO / 2]).offset(
        r, JoinType.Round, circular_segments=SEG)
    inner = CrossSection.square([LO - 2 * RW, WO - 2 * RW]).translate([RW, RW - WO / 2])
    return (outer - inner).extrude(HL).translate([x0, 0, 0]) - tunnels(x0, x0 + LO)

def diamond_link(x0):
    """diamond frame, points blunted along the chain so each end is a straight arched bar"""
    x1 = x0 + LD
    cx = x0 + LD / 2
    def dia(h):
        return CrossSection([[(cx + h, 0), (cx, h), (cx - h, 0), (cx, -h)]])
    outer = dia(D_HALF) ^ CrossSection.square([LD, 2 * D_HALF + 2]).translate([x0, -D_HALF - 1])
    hole = dia(D_HALF * D_HOLE) ^ CrossSection.square([LD - 2 * RW, 2 * D_HALF]).translate([x0 + RW, -D_HALF])
    inner = hole + CrossSection.square([LD - 2 * RW, 2 * SLOT]).translate([x0 + RW, -SLOT])
    return (outer - inner).extrude(HL) - tunnels(x0, x1)

def toggle_ring(x_end):
    """round ring ending at x_end; under the connector its rear rail sits where a flat link's bar does"""
    ri = RING_ID / 2
    ro = ri + RW
    cx = x_end - RW - np.sqrt(ri ** 2 - TUN ** 2)
    ring = CrossSection.circle(ro, SEG * 2) - CrossSection.circle(ri, SEG * 2)
    m = ring.extrude(HL).translate([cx, 0, 0])
    m -= box(x_end - RW - 1.0, x_end + 1, -TUN, TUN, -1, HB)
    return m, cx - ro

def connector(x_end, tbar=False):
    """closed upright loop linking the flat link ending at x_end with the next one"""
    a = x_end - RW - GAP - POST
    b = x_end + S + RW + GAP + POST
    loop = box(a, b, -BW / 2, BW / 2, 0, TOP0 + BT) - box(a + POST, b - POST, -BW, BW, TC, TOP0)
    if tbar:
        loop += box(b - TBAR_W, b, -TBAR_LEN / 2, TBAR_LEN / 2, 0, BT)
    return loop

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
    conns = [connector(e) for e in ends[:-1]] + [connector(ends[-1], tbar=True)]
    gold += conns
    if check:
        for c in conns:
            for q in order:
                assert (c ^ q).volume() < 1e-6, "connector touches a link - increase GAP"
        for p, q in zip(order, order[1:]):
            assert (p ^ q).volume() < 1e-6, "links touch"
        for p, q in zip(conns, conns[1:]):
            assert (p ^ q).volume() < 1e-6, "connectors touch - links too short"
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
