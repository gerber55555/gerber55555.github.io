// Peavey 5150 cord-wrap bracket: L-shaped standoff that bolts to the rear grille.
// Print 2 identical parts. Mount them a few inches apart on the back grille with the
// arms pointing AWAY from each other (rotate one 180°), then loop the cord around both.
// All dimensions in mm.

height    = 22;   // bracket height (top to bottom on the amp)
foot      = 24;   // width of the standoff leg that touches the grille
gap       = 22;   // clear space between grille and arm (room for the cord)
arm_len   = 55;   // how far the arm reaches past the standoff
arm_t     = 10;   // arm thickness
tip_lip   = 3;    // small hook at the arm tip toward the grille (0 = none)
fillet    = 6;    // inside-corner reinforcement
hole_d    = 4.5;  // M4 / #8 clearance
head_d    = 8.5;  // counterbore for the screw head
head_h    = 4;    // counterbore depth
hole_pitch= 12;   // spacing between the two bolts
slot      = 6;    // slot length, lets the bolts line up with the grille's hex holes

$fn = 40;
x0 = arm_len;     // standoff starts here

module profile() {   // in X (along arm) / Z (out from grille)
    translate([x0, 0]) square([foot, gap]);                   // standoff leg
    translate([0, gap]) square([arm_len + foot, arm_t]);      // arm
    if (tip_lip > 0) translate([0, gap - tip_lip]) square([4, tip_lip]);
    translate([x0, gap]) polygon([[0,0],[0,-fillet],[-fillet,0]]); // gusset
}

module slot_cut(d, h) {
    hull() for (s = [-slot/2, slot/2]) translate([s, 0, 0]) cylinder(d = d, h = h);
}

difference() {
    rotate([90,0,0]) translate([0,0,-height]) linear_extrude(height) profile();
    for (dx = [-hole_pitch/2, hole_pitch/2]) {
        translate([x0 + foot/2 + dx, height/2, 0]) rotate([0,0,90]) {
            translate([0,0,-1]) slot_cut(hole_d, gap + arm_t + 2);
            translate([0,0,gap + arm_t - head_h]) slot_cut(head_d, head_h + 1);
        }
    }
}
