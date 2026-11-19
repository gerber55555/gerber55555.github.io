# Peavey 5150 cord-wrap bracket (L-shaped)

A replacement for the L-shaped power-cord wrap brackets on the rear grille of a
Peavey 5150 / 6505 head. Print **two identical** parts.

- `cord_wrap.stl`: ready to slice (65 × 22 × 32 mm, matching the factory part)
- `cord_wrap.scad`: parametric source for OpenSCAD

## Printing
- PETG or ABS/ASA. PLA can creep near hot tubes.
- Lay it **on its side** so the L shape is flat on the bed. The inside corner is then
  as strong as it can be, and you don't need supports.
- 4 walls, 40% infill.

## Mounting (screws from behind the grille)
- Take the rear cage off. Hold each bracket in place on the outside and drive two screws
  from the inside of the cage, through the hex openings, into the blind holes in the foot.
  Nothing shows on the front.
- Screws: #8 or M4 self-tapping screws for plastic (e.g. plastite / thread-forming), about
  1/2" (12–14 mm) **plus** the grille thickness, with a washer big enough to bridge a hex
  opening. The holes are 26 mm deep, so there's plenty of room.
- Want to take them on and off a lot? Set `use_insert = true` in the .scad file and press
  in M4 heat-set inserts, then use M4 machine screws.
- Before you print, measure the centre-to-centre distance of two **side-by-side** grille
  openings and set `hole_pitch` to it (the default is 10 mm). Both screws need to line up
  with openings.
- Mount the brackets level with each other, about 15" (390 mm) apart centre-to-centre, at the height of the
  middle of the power tubes, with the arms pointing **away** from each other. The parts are identical:
  rotate one 180°.
- Loop the cord around the outside of both arms.
