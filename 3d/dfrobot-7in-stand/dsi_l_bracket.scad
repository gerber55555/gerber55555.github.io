// L-bracket stand for DFRobot 7" 800x480 DSI capacitive touchscreen (DFR0678 V1.0)
// Print TWO of these. They screw into the OUTER mounting holes (155 x 80 mm,
// M2.5) at the left and right edges, leaving the centre (Pi on the 58 x 49
// inner holes) completely free so all Pi I/O stays accessible.
//
// Orientation: print lying on its side (the "side" face flat on the bed)
// for the strongest layer direction. See README.

/* [Display] */
hole_spacing_v   = 80;   // vertical distance between outer holes (mm)
hole_edge_offset = 10;   // bottom hole centre to bottom edge of board (mm)
screw_d          = 2.9;  // M2.5 clearance hole
head_d           = 5.6;  // counterbore for screw head (DK 4.9)
screw_grip       = 3;    // material left under the screw head (mm) -> 6 mm screw = 3 mm thread engagement

/* [Bracket] */
boss_h      = 3;    // standoff boss height between board and plate (clears back components)
boss_d      = 7;
plate_t     = 4;    // upright thickness
plate_w     = 14;   // upright width
foot_t      = 5;    // foot thickness
foot_w      = 22;   // foot width (side to side)
foot_back   = 70;   // foot length behind the board
foot_front  = 25;   // foot length in front of the board's back plane (under the screen)
clearance   = 8;    // gap between table/foot top and bottom edge of the board
top_margin  = 8;    // upright extends this far above the top hole
gusset_t    = 3;
gusset_h    = 40;
gusset_len  = 40;

$fn = 48;

board_bottom = foot_t + clearance;
z1 = board_bottom + hole_edge_offset;
z2 = z1 + hole_spacing_v;
plate_h = z2 + top_margin;
y_plate = boss_h;                 // board back plane is y = 0, +y goes behind the display

module bracket() {
  difference() {
    union() {
      // upright
      translate([-plate_w/2, y_plate, 0]) cube([plate_w, plate_t, plate_h]);
      // foot
      translate([-foot_w/2, -foot_front, 0]) cube([foot_w, foot_front + y_plate + plate_t + foot_back, foot_t]);
      // bosses
      for (z = [z1, z2]) translate([0, 0, z]) rotate([-90, 0, 0]) cylinder(d = boss_d, h = y_plate + 0.01);
      // twin gussets on the edges (screwdriver fits between them)
      for (s = [-1, 1])
        translate([s * (plate_w/2 - gusset_t/2) - gusset_t/2, y_plate + plate_t, 0])
          rotate([90, 0, 90]) linear_extrude(gusset_t)
            polygon([[0, 0], [gusset_len, 0], [gusset_len, foot_t], [0, gusset_h]]);
    }
    for (z = [z1, z2]) translate([0, 0, z]) rotate([-90, 0, 0]) {
      translate([0, 0, -1]) cylinder(d = screw_d, h = 50);
      translate([0, 0, screw_grip]) cylinder(d = head_d, h = 50);   // counterbore from behind
    }
  }
}

bracket();
