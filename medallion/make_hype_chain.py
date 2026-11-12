"""'Hype chain' plate: the medallion and a closed loop of chain, printed together in one go.

  * The chain (same gold links / blue Jira diamonds / upright connectors as make_chain.py)
    is laid out as one closed rounded square: no clasp, it goes over your head.
  * The medallion prints in the middle of the loop.
  * A gold bail prints already linked through both: it is an upright connector loop whose
    bottom rod runs through a tunnel under the inner rail of a wider "bail link" in the chain
    and a tunnel under the top of the medallion's loop. The medallion comes off the bed
    already hanging from the chain.

Outputs: hype_plate.3mf (gold + blue parts), hype_plate_gold.stl / hype_plate_blue.stl,
hype_plate.stl (single colour).
Requires the same packages as make_chain.py / make_medallion.py.
"""
import itertools
import math
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

import make_chain as C
import make_medallion as M

# ---------------- parameters (mm) ----------------
LOOP_LEN = 760          # chain length around the loop (~30 in)
MAX_JOINT_DEG = 9.0     # how far each joint is bent on the corners (tested OK to 11)
BED = (350, 350)
BED_MARGIN = 10
C.SLOT = C.BW / 2 + C.GAP + 0.5   # wider channel in the diamonds so joints can bend on the corners
WO_B = 13.0             # width of the bail link (wider gold link at the top centre)
G2 = 12.0               # gap between the bail link and the medallion's loop: long enough that the
                        # medallion can swing ~180 degrees over the chain to hang down when worn
BAIL_RISE = 4.0         # the bail's roof rises at 45 degrees by this much (keeps its flat bridge short)

GOLD = [212, 175, 55, 255]
BLUE = [30, 70, 200, 255]


def place(m, origin, angle_deg):
    return m.rotate([0, 0, angle_deg]).translate([origin[0], origin[1], 0])


def bail_link(x0):
    """wider gold link with a tunnel under the inner (-y) rail for the bail"""
    r = 1.5
    from manifold3d import CrossSection, JoinType
    outer = CrossSection.square([C.LO - 2 * r, WO_B - 2 * r]).translate([r, r - WO_B / 2]).offset(
        r, JoinType.Round, circular_segments=C.SEG)
    inner = CrossSection.square([C.LO - 2 * C.RW, WO_B - 2 * C.RW]).translate([C.RW, C.RW - WO_B / 2])
    m = (outer - inner).extrude(C.HL).translate([x0, 0, 0]) - C.tunnels(x0, x0 + C.LO)
    xc = x0 + C.LO / 2
    m -= C.box(xc - C.TUN, xc + C.TUN, -WO_B / 2 - 1, -WO_B / 2 + C.RW + 0.6, -1, C.HB)
    return m


# ---------------- chain loop ----------------
# links alternate gold / blue; link 0 is the bail link (gold, centred at the top)
kinds = []
total, i = 0.0, 0
while True:
    k = "d" if i % 2 else "r"
    total += (C.LD if k == "d" else C.LO) + C.S
    kinds.append(k)
    i += 1
    if total >= LOOP_LEN and i % 2 == 0:
        break
lengths = [C.LD if k == "d" else C.LO for k in kinds]
perim = sum(lengths) + C.S * len(kinds)

# rounded-square path: corner radius from the joint-angle limit
max_step = max(C.LO, C.LD) + C.S
RC = max_step / math.radians(MAX_JOINT_DEG)
side = (perim - 2 * math.pi * RC) / 4
assert side >= C.LO + 2 * C.S, "loop too short for these corners - raise LOOP_LEN or MAX_JOINT_DEG"
half = side / 2


def path(s):
    """point on the rounded square at arc length s, starting at the top centre, clockwise"""
    s %= perim
    segs = []
    # top straight right half, then corner, right straight, corner, bottom, corner, left, corner, top left half
    pieces = [("line", (0, half + RC), (1, 0), half)]
    centres = [(half, half), (half, -half), (-half, -half), (-half, half)]
    dirs = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    starts = [(half + RC, half), (half, -half - RC), (-half - RC, -half), (-half, half + RC)]
    start_ang = [90, 0, -90, 180]
    for k in range(4):
        pieces.append(("arc", centres[k], start_ang[k], math.pi / 2 * RC))
        pieces.append(("line", starts[k], dirs[k], side if k < 3 else half))
    for kind, a, b, length in pieces:
        if s <= length + 1e-9:
            if kind == "line":
                return np.array([a[0] + b[0] * s, a[1] + b[1] * s])
            ang = math.radians(b) - s / RC
            return np.array([a[0] + RC * math.cos(ang), a[1] + RC * math.sin(ang)])
        s -= length
    raise ValueError


def lay(kinds, path_fn, closed=True, bail_index=0):
    """place links along path_fn(s), the bail link (kinds[bail_index]) centred at s = 0,
    and connectors between them"""
    lengths = [C.LD if k == "d" else C.LO for k in kinds]
    starts, s = [], -C.LO / 2 - sum(L + C.S for L in lengths[:bail_index])
    for L in lengths:
        starts.append(s)
        s += L + C.S
    golds, blues, links, conns, dirs, angles = [], [], [], [], [], []
    for i, (k, L, s0) in enumerate(zip(kinds, lengths, starts)):
        p0, p1 = path_fn(s0), path_fn(s0 + L)
        d = (p1 - p0) / np.linalg.norm(p1 - p0)
        ang = math.degrees(math.atan2(d[1], d[0]))
        geom = bail_link(0) if i == bail_index else (C.diamond_link(0) if k == "d" else C.flat_link(0))
        m = place(geom, p0, ang)
        links.append(m)
        dirs.append((ang, p0, p1))
        (blues if k == "d" else golds).append(m)
    n = len(links) if closed else len(links) - 1
    for i in range(n):
        a0, _, e = dirs[i]
        a1, s1, _ = dirs[(i + 1) % len(links)]
        turn = (a1 - a0 + 180) % 360 - 180
        angles.append(abs(turn))
        conns.append(place(C.connector(0).translate([-C.S / 2, 0, 0]), (e + s1) / 2, a0 + turn / 2))
    return golds + conns, blues, links, conns, angles


def hang(y_top, med_gold_src, med_blue_src, med_bail_cy):
    """position a medallion (or loop coupon) under the bail link and make the bail.
    med_*_src have their loop centred at (0, med_bail_cy)."""
    yr = y_top - WO_B / 2                       # outer face of the bail link's inner rail
    ring_top = yr - G2
    ring_c = ring_top - M.BAIL_OR
    dy = ring_c - med_bail_cy
    ri = M.BAIL_HOLE
    sag_in = ri - math.sqrt(ri ** 2 - (C.BW / 2) ** 2)
    rail_bottom = ring_c + ri - sag_in
    top0 = max(C.HL, M.BASE) + C.GAP
    tunnel = C.box(-C.TUN, C.TUN, ring_c + ri - 1.2, ring_top + 1, -1, C.HB)
    mg = med_gold_src.translate([0, dy, 0]) - tunnel
    mb = med_blue_src.translate([0, dy, 0]) if med_blue_src is not None else None
    a = rail_bottom - C.GAP - C.POST
    b = yr + C.RW + C.GAP + C.POST
    # bail profile in (y, z): bottom rod, two posts, and a roof whose underside rises at 45 degrees
    # from each post (self-supporting) to a short flat bridge
    pa, pb = a + C.POST, b - C.POST                     # inner faces of the posts
    rise = max(0.0, min(BAIL_RISE, (pb - pa) / 2 - 2.0))
    inner = [(pa, C.TC), (pb, C.TC), (pb, top0), (pb - rise, top0 + rise),
             (pa + rise, top0 + rise), (pa, top0)]
    outer = [(a, 0), (b, 0), (b, top0 + C.BT), (pb, top0 + C.BT), (pb - rise, top0 + rise + C.BT),
             (pa + rise, top0 + rise + C.BT), (pa, top0 + C.BT), (a, top0 + C.BT)]
    prof = CrossSection([outer]) - CrossSection([inner])          # (y, z) profile
    bail = prof.extrude(C.BW).rotate([90, 0, 90]).translate([-C.BW / 2, 0, 0])
    bb = bail.bounding_box()
    assert abs(bb[1] - a) < 1e-6 and abs(bb[2]) < 1e-6, bb   # profile landed where intended
    assert a - (ring_c - ri) > 0.5, "bail post doesn't fit inside the medallion's loop"
    return mg, mb, bail


gold_parts, blue_parts, links, conns, joint_angles = lay(kinds, path)
assert max(joint_angles) <= MAX_JOINT_DEG + 0.5, max(joint_angles)

# ---------------- medallion + bail ----------------
med_gold, med_blue, bail = hang(half + RC, M.gold, M.blue, M.BAIL_CY)
gold_parts += [med_gold, bail]
blue_parts += [med_blue]


# ---------------- test print ----------------
# 7 links on an arc bent as much as the real corners, with the bail link in the middle,
# the bail, and a copy of the medallion's loop on a small tab.
def build_test():
    """9 links from the top of the real loop: the bail link on the straight, then into the corner bends"""
    t_kinds = ["r", "d", "r", "d", "r", "d", "r", "d", "r"]
    tg, tb, tl, tc, ta = lay(t_kinds, path, closed=False, bail_index=4)
    ring = (M.CrossSection.circle(M.BAIL_OR, 96) - M.CrossSection.circle(M.BAIL_HOLE, 96)
            + M.CrossSection.square([14, 8]).translate([-7, -M.BAIL_OR - 6])).extrude(M.BASE)
    mg, _, bl = hang(half + RC, ring, None, 0.0)
    return tg + [mg, bl], tb, tl, tc, ta, mg, bl


# ---------------- checks ----------------
def bb_overlap(p, q, pad=0.0):
    a, b = p.bounding_box(), q.bounding_box()
    return all(a[i] - pad <= b[i + 3] and b[i] - pad <= a[i + 3] for i in range(3))


def check(links, conns, med_parts, bail, bail_link_idx, closed=True):
    """every pair of nearby parts >= 0.3 mm apart; connectors and bail trapped by their neighbours"""
    parts = links + conns + [m for m in med_parts if m is not None] + [bail]
    names = ([f"link{i}" for i in range(len(links))] + [f"conn{i}" for i in range(len(conns))]
             + [f"medallion{i}" for i, m in enumerate(med_parts) if m is not None] + ["bail"])
    d = 0.3
    shifts = [(d, 0, 0), (-d, 0, 0), (0, d, 0), (0, -d, 0), (0, 0, d), (0, 0, -d)]
    for (i, p), (j, q) in itertools.combinations(enumerate(parts), 2):
        if (names[i].startswith("medallion") and names[j].startswith("medallion")) or not bb_overlap(p, q, 0.5):
            continue
        movable = p if names[i].startswith(("conn", "bail")) else q
        other = q if movable is p else p
        for v in shifts:
            assert (movable.translate(list(v)) ^ other).volume() < 1e-6, \
                f"{names[i]} and {names[j]} closer than 0.3 mm"
    dirs3 = [np.array(v, float) / np.linalg.norm(v) for v in itertools.product([-1, 0, 1], repeat=3) if any(v)]
    traps = [(c, [links[i], links[(i + 1) % len(links)]]) for i, c in enumerate(conns)]
    traps.append((bail, [links[bail_link_idx], med_parts[0]]))
    picks = range(len(traps)) if len(traps) < 12 else \
        sorted(set([0, 1, 5, 9, len(conns) // 4, len(conns) // 2, len(conns) - 1, len(traps) - 1]))
    for idx in picks:
        c, nb = traps[idx]
        for dv in dirs3:
            assert any((c.translate(list(dv * t)) ^ n).volume() > 1e-6
                       for t in np.arange(0.25, 40, 0.25) for n in nb), f"part {idx} can slide free"


def to_trimesh(m, col):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)
    t.visual.face_colors = col
    return t


def export(prefix, gold, blue):
    allm = gold + blue if blue is not None else gold
    bb = allm.bounding_box()
    off = [-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, 0]
    w, h = bb[3] - bb[0], bb[4] - bb[1]
    assert w <= BED[0] - 2 * BED_MARGIN and h <= BED[1] - 2 * BED_MARGIN, "doesn't fit the bed"
    here = os.path.dirname(os.path.abspath(__file__))
    scene = trimesh.Scene()
    for name, m, col in [("gold", gold, GOLD), ("blue", blue, BLUE)]:
        if m is None:
            continue
        t = to_trimesh(m.translate(off), col)
        if prefix == "hype_plate":
            t.export(os.path.join(here, f"{prefix}_{name}.stl"))
        scene.add_geometry(t, node_name=name, geom_name=name)
    scene.export(os.path.join(here, f"{prefix}.3mf"))
    to_trimesh(allm.translate(off), GOLD).export(os.path.join(here, f"{prefix}.stl"))
    return w, h


def main():
    check(links, conns, [med_gold, med_blue], bail, 0)
    w, h = export("hype_plate", C.union(gold_parts), C.union(blue_parts))
    print(f"{len(links)} links ({kinds.count('d')} diamonds), loop {perim:.0f} mm, corner radius {RC:.0f} mm, "
          f"max joint bend {max(joint_angles):.1f} deg, plate {w:.0f} x {h:.0f} mm")
    tg, tb, tl, tc, ta, mg, bl = build_test()
    check(tl, tc, [mg], bl, 4, closed=False)
    w, h = export("hype_test", C.union(tg), C.union(tb))
    print(f"test print: {len(tl)} links bent {min(ta):.1f}-{max(ta):.1f} deg per joint, {w:.0f} x {h:.0f} mm")


if __name__ == "__main__":
    main()
