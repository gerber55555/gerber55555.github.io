# King of Jira medallion (3D printable)

A 50 mm wearable pendant with a raised rim, a diamond emblem and raised "Jira" text, plus a loop at the top for a chain or cord.

![preview](preview.png)

| File | Use |
|---|---|
| `medallion.stl` | Single-colour, one-piece print |
| `medallion.3mf` | Gold, blue and light-blue parts in one file for AMS/MMU printers |
| `medallion_gold.stl`, `medallion_blue.stl`, `medallion_lightblue.stl` | The same parts as separate STLs (they share coordinates, so load them together as one multi-part object) |
| `make_medallion.py` | Parametric source. Change size, text or bail at the top of the file and run it again |

**Size:** 50 × 59 × 4.8 mm, about 7.4 cm³ (≈9 g PLA at 100% infill). Hole for the chain is 5.2 mm.

**Print settings:** lay it flat face-up, no supports, 0.12–0.16 mm layers, 3–4 walls, 20–30% infill.
Single-colour: gold/silk-gold PLA, then paint the diamond blue. Or use a filament swap at the 3.2 mm layer height so the rim, emblem and text print in a second colour.

**Wear it:** thread a 4–5 mm jump ring through the loop, or run a ball chain or cord straight through it.

Regenerate: `pip install manifold3d trimesh shapely matplotlib networkx lxml && python3 make_medallion.py`
