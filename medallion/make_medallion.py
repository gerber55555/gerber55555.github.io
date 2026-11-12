"""Generate a wearable, 3D-printable 'King of Jira' medallion.

Outputs (in this folder):
  medallion.stl          - single-colour, one-piece print
  medallion_gold.stl     - gold body (disc, rims, bail)   } multi-colour parts,
  medallion_blue.stl     - blue diamond frame, front 'Jira' text, back inlay text } (same coordinates)
  medallion.3mf          - both parts in one file for AMS/MMU printers

Requires: pip install manifold3d trimesh shapely matplotlib numpy
All dimensions in millimetres. Prints flat, face up, no supports.
"""
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, FillRule
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon
from shapely.ops import unary_union

# ---------------- parameters ----------------
DIAMETER = 75.0     # overall disc diameter; all face artwork scales with it
K = DIAMETER / 50.0 # scale factor relative to the original 50 mm design
R = DIAMETER / 2
BASE = 3.6          # base disc thickness
CHAMFER = 0.8       # bevel on the front edge
RIM_W, RIM_H = 2.2 * K, 1.5                 # raised outer rim
RING_R, RING_W, RING_H = 20.6 * K, 0.8 * K, 0.6   # thin decorative inner ring
EMB_Y, EMB_HALF = 6.0 * K, 11.0 * K         # diamond emblem centre y and half-diagonal
EMB_H = 2.0                                 # emblem height above base
HOLE_HALF = 6.2 * K                         # half-diagonal of the open centre (gold face shows through)
TEXT = "Jira"
TEXT_H, TEXT_Y, TEXT_RAISE = 9.0 * K, -13.0 * K, 1.5
# back: "STATUS = SUCCESS" inlaid into the bottom face, printed in blue in the first layer.
# Text is mirrored in the model so it reads correctly when you turn the medallion over.
BACK_LINES = [("STATUS", 9.5 * K), ("=", 0.0), ("SUCCESS", -9.5 * K)]   # (text, centre y)
BACK_CAP_H = 6.0 * K            # capital letter height
BACK_MAX_W = 34.0 * K           # longest line is shrunk to fit this width
BACK_DEPTH = 0.2                # inlay depth = your first-layer height (use 0.4 for two layers)
# bail = a toggle ring, same size as the chain's, so a chain T-bar clips straight into it
BAIL_HOLE = 5.0                 # hole radius (10 mm hole) - keep matching the chain's RING_ID
BAIL_OR = BAIL_HOLE + 3.0       # 3 mm wall for the heavier medallion
BAIL_CY = R + BAIL_HOLE + 0.8   # hole stays just clear of the disc edge
SEG = 128

def poly_to_cs(polys):
    """shapely Polygon/MultiPolygon -> manifold CrossSection"""
    geoms = getattr(polys, "geoms", [polys])
    contours = []
    for g in geoms:
        contours.append(np.asarray(g.exterior.coords)[:-1])
        for h in g.interiors:
            contours.append(np.asarray(h.coords)[:-1])
    return CrossSection(contours, FillRule.EvenOdd)

def diamond(cx, cy, h):
    return Polygon([(cx, cy + h), (cx + h, cy), (cx, cy - h), (cx - h, cy)])

def text_poly(s, height, y=None, size_by_font=False, max_w=None, mirror=False):
    fp = FontProperties(family="DejaVu Sans", weight="bold")
    tp = TextPath((0, 0), s, size=10, prop=fp)
    polys = []
    for verts in tp.to_polygons(closed_only=True):
        if len(verts) >= 3:
            polys.append(Polygon(verts).buffer(0))
    # even-odd assembly: letters minus counters
    polys.sort(key=lambda p: -p.area)
    shape = Polygon()
    for p in polys:
        shape = shape.difference(p) if shape.contains(p) else shape.union(p)
    from shapely import affinity
    minx, miny, maxx, maxy = shape.bounds
    # size_by_font: scale so capital letters are `height` tall (keeps "=" in proportion)
    k = height / (7.29 if size_by_font else (maxy - miny))
    if max_w and (maxx - minx) * k > max_w:
        k = max_w / (maxx - minx)
    shape = affinity.scale(shape, -k if mirror else k, k, origin=(0, 0))
    minx, miny, maxx, maxy = shape.bounds
    if size_by_font:   # centre on the cap-height band, not the glyph box
        return affinity.translate(shape, -(minx + maxx) / 2, (TEXT_Y if y is None else y) - 3.645 * k)
    return affinity.translate(shape, -(minx + maxx) / 2, (TEXT_Y if y is None else y) - (miny + maxy) / 2)

def extrude(cs, z0, h):
    return cs.extrude(h).translate([0, 0, z0])

# ---- gold body ----
# base disc with bevelled front edge, built by revolving a profile
profile = CrossSection([[(0, 0), (R, 0), (R, BASE + RIM_H - CHAMFER),
                         (R - CHAMFER, BASE + RIM_H), (0, BASE + RIM_H)]])
disc_full = profile.revolve(SEG)
# cut the face down to BASE inside the rim
pocket = Manifold.cylinder(RIM_H + 1, R - RIM_W, R - RIM_W, SEG).translate([0, 0, BASE])
gold = disc_full - pocket

# decorative inner ring
ring = (CrossSection.circle(RING_R, SEG) - CrossSection.circle(RING_R - RING_W, SEG))
gold += extrude(ring, BASE - 0.01, RING_H + 0.01)

# bail (flat loop with hole) - joined to disc
bail = CrossSection.circle(BAIL_OR, 64).translate([0, BAIL_CY])
bail_body = extrude(bail, 0, BASE)
gold = (gold + bail_body) - Manifold.cylinder(20, BAIL_HOLE, BAIL_HOLE, 64).translate([0, BAIL_CY, -5])
# keep the hole clean through the rim area too (rim overlaps the bail)

# raised text (printed in blue - added to the blue part below)
txt = text_poly(TEXT, TEXT_H)
front_text = extrude(poly_to_cs(txt), BASE, TEXT_RAISE)

# gold gap ring around the inner diamond, raised to emblem height (so it reads as an outline)
outer_d = diamond(0, EMB_Y, EMB_HALF)

# ---- back inlay (cut out of gold, filled by the blue part) ----
back_txt = unary_union([text_poly(t, BACK_CAP_H, y=y, size_by_font=True, max_w=BACK_MAX_W, mirror=True)
                        for t, y in BACK_LINES])
back = extrude(poly_to_cs(back_txt), 0, BACK_DEPTH)
gold -= back.translate([0, 0, -0.01]) + back   # clean cut through the bottom face

# ---- blue diamond frame ----
frame = outer_d.difference(diamond(0, EMB_Y, HOLE_HALF))
blue = extrude(poly_to_cs(frame), BASE, EMB_H) + front_text + back


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)

def main():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    parts = {"gold": gold, "blue": blue}
    colors = {"gold": [212, 175, 55, 255], "blue": [30, 70, 200, 255],
    }
    scene = trimesh.Scene()
    for name, m in parts.items():
        tm = to_trimesh(m)
        assert tm.is_watertight, name
        if name != "gold":   # parts must not overlap each other
            assert (m ^ gold).volume() < 1e-3, name
        tm.export(os.path.join(here, f"medallion_{name}.stl"))
        tm.visual.face_colors = colors[name]
        scene.add_geometry(tm, node_name=name, geom_name=name)
    scene.export(os.path.join(here, "medallion.3mf"))

    # one-piece version: the blue parts only touch the gold, so add thin overlaps to fuse them into one solid
    fuse = (extrude(poly_to_cs(txt), BASE - 0.1, 0.2) + extrude(poly_to_cs(frame), BASE - 0.1, 0.2)
            + extrude(poly_to_cs(back_txt), 0.1, 0.2))
    one = gold + blue + fuse
    # boolean ops on the coplanar inlay leave a few zero-volume slivers; drop them
    one = max(one.decompose(), key=lambda c: c.volume())
    assert abs(one.volume() - (gold + blue + fuse).volume()) < 1e-3
    assert len(one.decompose()) == 1, "single-colour model is not one fused solid"
    single = to_trimesh(one)
    assert single.is_watertight
    single.export(os.path.join(here, "medallion.stl"))
    print("bounds (mm):", single.bounds.round(2).tolist(), "volume cm3:", round(single.volume / 1000, 2))


if __name__ == "__main__":
    main()
