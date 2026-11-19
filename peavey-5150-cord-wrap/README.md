# Peavey 5150 cord-wrap bracket

A replacement for the power-cord wrap cleats on a Peavey 5150 / 6505 head.
Print **two**. Mount one near the top and one near the bottom of the back panel,
then wind the power cord around both.

- `cord_wrap.stl`: ready to slice (70 × 42 × 38 mm)
- `cord_wrap.scad`: parametric source. Open it in OpenSCAD, change the numbers, then export.

## Printing
- PETG or ABS/ASA. PLA can creep near a warm amp.
- Lay it **on its side** so the Z-profile is flat on the bed. Layers then run along the
  bend, and you don't need supports.
- 4 walls, 30–40% infill.

## Mounting
- The holes take #8 (M4) countersunk wood screws, about 5/8" (16 mm) long. Check that the
  screw is shorter than the panel is thick.
- If your cabinet already has holes or inserts from factory brackets, measure their spacing
  and set `hole_pitch` (and `hole_d` for machine screws) in the .scad file.
- Mount each bracket so its lip faces **away** from the other bracket.
