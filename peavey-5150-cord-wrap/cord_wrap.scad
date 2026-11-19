// Peavey 5150 cord-wrap bracket: L-shaped standoff that bolts to the rear grille.
// Print 2 identical parts. Mount them a few inches apart on the back grille with the
// arms pointing AWAY from each other (rotate one 180°), then loop the cord around both.
// Screws go in from behind the grille, so nothing shows on the front.
// All dimensions in mm.

height    = 22;   // bracket height (top to bottom on the amp)
foot      = 22;   // width of the standoff leg that touches the grille
gap       = 22;   // clear space between grille and arm (room for the cord)
arm_len   = 43;   // how far the arm reaches past the standoff
arm_t     = 10;   // arm thickness
tip_lip   = 3;    // small hook at the arm tip toward the grille (0 = none)
fillet    = 6;    // inside-corner reinforcement
// Screws come in from BEHIND the grille (remove the cage) into blind holes in the foot.
use_insert = false; // false = self-tapping screw pilot; true = M4 heat-set insert pocket
pilot_d   = 3.4;  // pilot for #8 / M4 self-tapping (plastite) screws
hole_depth= 26;   // blind hole depth from the grille face (part is 32 deep)
insert_d  = 5.6;  // heat-set insert hole (M4 x 8 mm insert, check your insert's spec)
insert_h  = 8.5;
hole_pitch= 10;   // spacing between the two screws: match two adjacent grille openings

$fn = 40;
x0 = arm_len;     // standoff starts here

module profile() {   // in X (along arm) / Z (out from grille)
    translate([x0, 0]) square([foot, gap]);                   // standoff leg
    translate([0, gap]) square([arm_len + foot, arm_t]);      // arm
    if (tip_lip > 0) translate([0, gap - tip_lip]) square([4, tip_lip]);
    translate([x0, gap]) polygon([[0,0],[0,-fillet],[-fillet,0]]); // gusset
}

difference() {
    rotate([90,0,0]) translate([0,0,-height]) linear_extrude(height) profile();
    for (dx = [-hole_pitch/2, hole_pitch/2])
        translate([x0 + foot/2 + dx, height/2, -1]) {
            cylinder(d = pilot_d, h = hole_depth + 1);
            if (use_insert) cylinder(d = insert_d, h = insert_h + 1);
        }
}
