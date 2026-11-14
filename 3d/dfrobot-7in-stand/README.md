# L-bracket stand for the DFRobot 7" DSI touchscreen (DFR0678 V1.0)

Print **2 identical brackets** (`dsi_l_bracket.stl`). Each one screws into the two outer
M2.5 holes on one side of the board (155 × 90 mm hole pattern, 5 mm in from the board edges — per [DFRobot's dimension drawing](https://dfimg.dfrobot.com/wiki/17475/DFR0678_raspberry-pi-7-dsilcd-touchscreen-module_dimension_1.0.pdf)). The Pi sits on the inner
58 × 49 mm holes and nothing else covers it, so all of its I/O stays reachable.

- Screws: the supplied M2.5×6 screws, or M2.5×8 if the holes are deep enough. Holes are counterbored from behind so a 6 mm screw grips 3 mm. They are slotted 1.5 mm vertically for tolerance (`slot`).
- Bosses (3 mm) hold the upright away from components on the back of the board.
- The board's bottom edge sits 38 mm (1.5 in) above the table. The foot reaches 70 mm behind the board and 25 mm under the screen.
- Print it lying on its side (the flat 22 mm side face on the bed — the upright, foot and gusset are all flush on that face), so the upright isn't made of layers that can split. Use PLA or PETG, 3–4 walls, 25 % infill. It needs no supports.
- Before printing, measure the hole spacing with calipers. If it differs, change `hole_spacing_v` / `hole_edge_offset` in `dsi_l_bracket.scad` and re-export from OpenSCAD.
