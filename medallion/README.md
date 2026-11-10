# King of Jira medallion and chain (3D printable)

A 50 mm wearable pendant with a raised rim, a diamond emblem and raised "Jira" text on the front,
"STATUS = SUCCESS" inlaid in blue on the back, and a print-in-place chain to hang it on.

![front](preview.png) ![back](back_preview.png)

## Medallion

| File | Use |
|---|---|
| `medallion.3mf` | Gold, blue and light-blue parts in one file for AMS/MMU printers (**use this for the blue back text**) |
| `medallion_gold.stl`, `medallion_blue.stl`, `medallion_lightblue.stl` | The same parts as separate STLs (shared coordinates; load together as one multi-part object) |
| `medallion.stl` | Single-colour, one-piece print (back text is not cut in) |
| `make_medallion.py` | Parametric source |

**Size:** 50 × 59 × 4.8 mm, about 9 g PLA. Chain hole 5.2 mm.

**Print:** flat, face up, no supports, 3–4 walls, 20–30% infill.
The back text is a 0.2 mm inlay, so it is exactly the **first layer** and comes out blue on the bed side.
Set your first-layer height to 0.2 mm (or change `BACK_DEPTH` to match yours, e.g. 0.4 for two layers if gold shows through).
A textured or smooth PEI plate gives the back its finish.
Without a multi-colour printer: swap filament manually after layer 1 (blue, then gold), and again at 3.2 mm for a coloured diamond.

## Chain

| File | Use |
|---|---|
| `chain_plate.stl` | All 4 pieces on one plate (156 × 85 mm) |
| `chain_segment.stl` | One piece, if you want to print them separately |
| `make_chain.py` | Parametric source (`NECKLACE_LEN`, `SEGMENTS`, `GAP`) |

![chain](chain_preview.png)

The chain prints flat and already linked, with no supports. Flat links lie on the bed and solid bridge links arch
over them on 45° ramps. Each piece starts with a toggle ring and ends with a T-bar, and four pieces clip together into
a ~59 cm (23 in) necklace. One joint is the clasp you open to put it on.

**Print:** 0.2 mm layers, 100% infill or 4+ walls (the links are small), no brim on the links if you can avoid it.
`GAP` is 0.5 mm; if links come out fused, raise it to 0.6 and re-run the script.
Right after printing, flex every link gently to break the links free.

**Assemble:** feed one T-bar through the medallion's loop, then push it lengthwise through the next piece's ring and
let it turn crosswise. Clip the other pieces together the same way. Put the medallion's joint opposite the clasp
joint so it hangs at the front.

## Regenerate

```
pip install manifold3d trimesh shapely matplotlib networkx lxml
python3 make_medallion.py
python3 make_chain.py
```
