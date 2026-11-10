"""Generate a wearable, 3D-printable 'King of Jira' medallion.

Outputs (in this folder):
  medallion.stl          - single-colour, one-piece print
  medallion_gold.stl     - gold body (disc, rims, text, bail)   } multi-colour parts,
  medallion_blue.stl     - dark-blue diamond frame + back inlay text             } all share the same
  medallion_lightblue.stl- light-blue inner diamond             } coordinates
  medallion.3mf          - all three parts in one file for AMS/MMU printers

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
R = 25.0            # medallion radius (50 mm diameter)
BASE = 3.2          # base disc thickness
CHAMFER = 0.6       # bevel on the front edge
RIM_W, RIM_H = 2.2, 1.2         # raised outer rim
RING_R, RING_W, RING_H = 20.6, 0.8, 0.6   # thin decorative inner ring
EMB_Y, EMB_HALF = 6.0, 11.0     # diamond emblem centre y and half-diagonal
EMB_H = 1.6                     # emblem height above base
INNER_HALF = 5.4                # inner light diamond half-diagonal
GAP = 0.8                       # gold gap between frame and inner diamond
TEXT = "Jira"
TEXT_H, TEXT_Y, TEXT_RAISE = 9.0, -13.0, 1.2
# back: "STATUS = SUCCESS" inlaid into the bottom face, printed in blue in the first layer.
# Text is mirrored in the model so it reads correctly when you turn the medallion over.
BACK_LINES = [("STATUS", 9.5), ("=", 0.0), ("SUCCESS", -9.5)]   # (text, centre y)
BACK_CAP_H = 6.0                # capital letter height
BACK_MAX_W = 34.0               # longest line is shrunk to fit this width
BACK_DEPTH = 0.2                # inlay depth = your first-layer height (use 0.4 for two layers)
BAIL_OR, BAIL_HOLE = 5.8, 2.6   # bail outer radius / hole radius (5.2 mm hole)
BAIL_CY = R + 3.4               # bail centre (overlaps the disc)
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

# raised text
txt = text_poly(TEXT, TEXT_H)
gold += extrude(poly_to_cs(txt), BASE - 0.01, TEXT_RAISE + 0.01)

# gold gap ring around the inner diamond, raised to emblem height (so it reads as an outline)
outer_d = diamond(0, EMB_Y, EMB_HALF)
inner_d = diamond(0, EMB_Y, INNER_HALF)
gap_ring = diamond(0, EMB_Y, INNER_HALF + GAP).difference(inner_d)
gold += extrude(poly_to_cs(gap_ring), BASE - 0.01, EMB_H + 0.01)

# ---- back inlay (cut out of gold, filled by the blue part) ----
back_txt = unary_union([text_poly(t, BACK_CAP_H, y=y, size_by_font=True, max_w=BACK_MAX_W, mirror=True)
                        for t, y in BACK_LINES])
back = extrude(poly_to_cs(back_txt), 0, BACK_DEPTH)
gold -= back.translate([0, 0, -0.01]) + back   # clean cut through the bottom face

# ---- blue diamond frame ----
frame = outer_d.difference(diamond(0, EMB_Y, INNER_HALF + GAP))
blue = extrude(poly_to_cs(frame), BASE, EMB_H) + back

# ---- light-blue inner diamond ----
light = extrude(poly_to_cs(inner_d), BASE, EMB_H)

def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=True)

import os
here = os.path.dirname(os.path.abspath(__file__))
parts = {"gold": gold, "blue": blue, "lightblue": light}
colors = {"gold": [212, 175, 55, 255], "blue": [30, 70, 200, 255],
          "lightblue": [120, 170, 255, 255]}
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

single = to_trimesh(gold + blue + light)
assert single.is_watertight
single.export(os.path.join(here, "medallion.stl"))
print("bounds (mm):", single.bounds.round(2).tolist(), "volume cm3:", round(single.volume / 1000, 2))
