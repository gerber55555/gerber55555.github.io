# L-bracket stand for the DFRobot 7" DSI touchscreen (DFR0678 V1.0)

Print **2 identical brackets** (`dsi_l_bracket.stl`). Each one screws into the two outer
M2.5 holes on one side of the board (155 × 80 mm hole pattern). The Pi sits on the inner
58 × 49 mm holes and nothing else covers it, so all of its I/O stays reachable.

- Screws: the supplied M2.5×6 screws, or M2.5×8 if the holes are deep enough. Holes are counterbored from behind so a 6 mm screw grips 3 mm.
- Bosses (3 mm) hold the upright away from components on the back of the board.
- The board's bottom edge sits 13 mm above the table. The foot reaches 70 mm behind the board and 25 mm under the screen.
- Print it lying on its side (the 22 mm-wide face flat on the bed), so the upright isn't made of layers that can split. Use PLA or PETG, 3–4 walls, 25 % infill. It needs no supports.
- Before printing, measure the hole spacing with calipers. If it differs, change `hole_spacing_v` / `hole_edge_offset` in `dsi_l_bracket.scad` and re-export from OpenSCAD.
