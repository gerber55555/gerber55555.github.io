"""Draw the hype chain + medallion as worn, to scale, on an average adult-male outline (front view).

Not a physics simulation: the chain goes round the back of the neck, and the front part hangs as a
catenary (the shape a hanging chain makes) between the sides of the neck, with a little of its length
used going forward over the collarbones. Links, diamonds, connectors, bail and medallion are drawn at
their real sizes from make_chain.py / make_hype_chain.py.

Writes worn_preview.png. Usage: python3 make_worn_preview.py
"""
import math
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, Circle, Wedge, FancyBboxPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D

import make_chain as C
import make_hype_chain as H

GOLD, GOLD_D, BLUE = "#d4af37", "#8a6d12", "#1e46c8"
SKIN, SHIRT = "#e9d3c0", "#2d2f36"

# ---- average adult male (approx. 50th percentile), mm; y = 0 at the base of the neck (front) ----
HEAD_W, HEAD_H = 155, 232
NECK_W, NECK_H = 120, 95
SHOULDER_W = 420
NAVEL_Y = -430                    # base of neck to navel
BACK_OF_NECK = 260                # chain length used going round the back of the neck
FORWARD_WRAP = 80                 # used going forward over the collarbones (not visible from the front)
ATTACH = (NECK_W / 2 + 15, 22)    # where the chain comes round the sides of the neck


def catenary_for_length(half_span, length):
    """y = a*cosh(x/a) through (+-half_span, 0) with the given arc length; returns a and depth"""
    lo, hi = 1.0, 1e5
    for _ in range(200):
        a = math.sqrt(lo * hi)
        L = 2 * a * math.sinh(half_span / a)
        lo, hi = (a, hi) if L > length else (lo, a)
    return a, a * (math.cosh(half_span / a) - 1)


def chain_curve(loop_len):
    front = loop_len - BACK_OF_NECK - FORWARD_WRAP
    a, depth = catenary_for_length(ATTACH[0], front)
    xs = np.linspace(-ATTACH[0], ATTACH[0], 4001)
    ys = ATTACH[1] - depth + a * (np.cosh(xs / a) - 1)
    pts = np.c_[xs, ys]
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    return pts, s, depth


def at(pts, s, t):
    i = np.clip(np.searchsorted(s, t), 1, len(s) - 1)
    f = (t - s[i - 1]) / (s[i] - s[i - 1])
    p = pts[i - 1] + f * (pts[i] - pts[i - 1])
    d = pts[i] - pts[i - 1]
    return p, math.degrees(math.atan2(d[1], d[0]))


def draw_shape(ax, poly, centre, ang, **kw):
    tr = Affine2D().rotate_deg(ang).translate(*centre) + ax.transData
    ax.add_patch(Polygon(poly, closed=True, transform=tr, **kw))


def rect_link(ax, c, ang):
    L, W, r = C.LO, C.WO, C.RW
    draw_shape(ax, [(-L/2, -W/2), (L/2, -W/2), (L/2, W/2), (-L/2, W/2)], c, ang, fc=GOLD, ec=GOLD_D, lw=0.6, zorder=5)
    draw_shape(ax, [(-L/2+r, -W/2+r), (L/2-r, -W/2+r), (L/2-r, W/2-r), (-L/2+r, W/2-r)], c, ang, fc=SHIRT, ec=GOLD_D, lw=0.4, zorder=5)


def diamond_link(ax, c, ang):
    hx, hy, tip = C.LD / 2, C.D_HALF, C.D_TIP
    out = [(-hx, -tip), (0, -hy), (hx, -tip), (hx, tip), (0, hy), (-hx, tip)]
    f = C.D_HOLE
    hole = [(-C.D_HALF_X * f, 0), (0, -hy * f), (C.D_HALF_X * f, 0), (0, hy * f)]
    draw_shape(ax, out, c, ang, fc=BLUE, ec="#10286f", lw=0.6, zorder=5)
    draw_shape(ax, hole, c, ang, fc=SHIRT, ec="#10286f", lw=0.4, zorder=5)


def connector(ax, c, ang):
    L = 2 * (C.RW + C.GAP + C.PLAY_X + C.POST) + C.S
    draw_shape(ax, [(-L/2, -C.BW/2), (L/2, -C.BW/2), (L/2, C.BW/2), (-L/2, C.BW/2)], c, ang,
               fc="#e6c45a", ec=GOLD_D, lw=0.5, zorder=6)


def medallion(ax, top):
    """medallion hanging with the top of its loop at `top` (x = 0)"""
    M = H.M
    R = M.DIAMETER / 2
    cy = top[1] - M.BAIL_OR - M.BAIL_CY        # disc centre
    ax.add_patch(Circle((0, cy + M.BAIL_CY), M.BAIL_OR, fc=GOLD, ec=GOLD_D, lw=0.6, zorder=7))
    ax.add_patch(Circle((0, cy + M.BAIL_CY), M.BAIL_HOLE, fc=SHIRT, ec=GOLD_D, lw=0.4, zorder=7))
    ax.add_patch(Circle((0, cy), R, fc=GOLD, ec=GOLD_D, lw=1.0, zorder=7))
    ax.add_patch(Circle((0, cy), R - M.RIM_W, fc="none", ec=GOLD_D, lw=0.6, zorder=8))
    ax.add_patch(Circle((0, cy), M.RING_R, fc="none", ec=GOLD_D, lw=0.5, zorder=8))
    e, ho = M.EMB_HALF, M.HOLE_HALF
    ax.add_patch(Polygon([(0, cy + M.EMB_Y + e), (e, cy + M.EMB_Y), (0, cy + M.EMB_Y - e), (-e, cy + M.EMB_Y)], fc=BLUE, zorder=8))
    ax.add_patch(Polygon([(0, cy + M.EMB_Y + ho), (ho, cy + M.EMB_Y), (0, cy + M.EMB_Y - ho), (-ho, cy + M.EMB_Y)], fc=GOLD, zorder=8))
    tp = TextPath((0, 0), M.TEXT, size=10, prop=FontProperties(family="DejaVu Sans", weight="bold"))
    bb = tp.get_extents()
    k = M.TEXT_H / bb.height
    tr = Affine2D().translate(-(bb.x0 + bb.x1) / 2, -(bb.y0 + bb.y1) / 2).scale(k).translate(0, cy + M.TEXT_Y)
    ax.add_patch(PathPatch(tr.transform_path(tp), fc=BLUE, lw=0, zorder=8))
    return cy - R


def body(ax):
    ax.add_patch(Polygon([(-SHOULDER_W / 2, -10), (-NECK_W / 2 - 25, 40), (NECK_W / 2 + 25, 40), (SHOULDER_W / 2, -10),
                          (SHOULDER_W / 2 + 25, -160), (SHOULDER_W / 2 - 5, -700), (-SHOULDER_W / 2 + 5, -700),
                          (-SHOULDER_W / 2 - 25, -160)], fc=SHIRT, ec="#15161a", lw=1, zorder=1))
    ax.add_patch(FancyBboxPatch((-NECK_W / 2, 0), NECK_W, NECK_H + 20, boxstyle="round,pad=0,rounding_size=20",
                                fc=SKIN, ec="#b89c86", lw=1, zorder=2))
    ax.add_patch(Wedge((0, 22), NECK_W / 2 + 6, 180, 360, fc=SKIN, ec="none", zorder=2))   # collar opening
    ax.add_patch(Ellipse((0, NECK_H + HEAD_H / 2 - 10), HEAD_W, HEAD_H, fc=SKIN, ec="#b89c86", lw=1, zorder=3))
    ax.plot([-SHOULDER_W / 2 + 40, SHOULDER_W / 2 - 40], [NAVEL_Y, NAVEL_Y], ls=":", c="#9aa0aa", lw=1, zorder=1)
    ax.text(SHOULDER_W / 2 - 30, NAVEL_Y + 8, "navel", color="#9aa0aa", ha="right", fontsize=8)


def draw(ax, loop_len, title):
    body(ax)
    pts, s, depth = chain_curve(loop_len)
    mid = s[-1] / 2
    kinds = ["r", "d"]
    # bail link centred at the bottom, then alternate outward both ways until the neck
    for side in (1, -1):
        t = mid + side * C.LO / 2 if side else mid
        k = 1
        if side == 1:
            p, ang = at(pts, s, mid)
            rect_link(ax, p, ang)
        while True:
            t_gap = t + side * C.S / 2
            kind = kinds[k % 2]
            L = C.LD if kind == "d" else C.LO
            t_c = t + side * (C.S + L / 2)
            if not (0 < t_c < s[-1]):
                break
            p, ang = at(pts, s, t_gap)
            connector(ax, p, ang)
            p, ang = at(pts, s, t_c)
            (diamond_link if kind == "d" else rect_link)(ax, p, ang)
            t = t + side * (C.S + L)
            k += 1
    bottom, _ = at(pts, s, mid)
    bail_top = bottom[1] - C.WO_B / 2 if hasattr(C, "WO_B") else bottom[1] - H.WO_B / 2
    bail_len = H.bail.bounding_box()[4] - H.bail.bounding_box()[1]
    ax.add_patch(Polygon([(-C.BW / 2, bail_top), (C.BW / 2, bail_top), (C.BW / 2, bail_top - bail_len),
                          (-C.BW / 2, bail_top - bail_len)], fc="#e6c45a", ec=GOLD_D, lw=0.5, zorder=8))
    med_bottom = medallion(ax, (0, bail_top - bail_len + 2 * H.M.BAIL_OR - 4))
    ax.set_title(f"{title}\nmedallion bottom ≈ {-med_bottom / 10:.0f} cm below the base of the neck", fontsize=10)
    ax.set_xlim(-330, 330)
    ax.set_ylim(-720, 400)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    fig, axs = plt.subplots(1, 2, figsize=(12, 10))
    draw(axs[0], H.perim, f"current hype chain: {H.perim / 10:.0f} cm ({H.perim / 25.4:.0f} in) loop")
    draw(axs[1], 760, "for comparison: 76 cm (30 in) loop")
    fig.suptitle(f"Worn, to scale (average adult male, front view) - {H.M.DIAMETER:.0f} mm medallion", fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worn_preview.png")
    plt.savefig(out, dpi=110)
    print("wrote", out)


if __name__ == "__main__":
    main()
