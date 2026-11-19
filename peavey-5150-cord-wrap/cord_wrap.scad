// Peavey 5150 cord-wrap bracket (Z-cleat). Print 2, mount one near the top
// and one near the bottom of the back panel; wrap the power cord around both.
// All dimensions in mm. Adjust to suit your amp, then F6 + export STL.

width      = 70;   // length of the bracket along the panel
flange     = 24;   // mounting flange depth
standoff   = 32;   // how far the cord sits off the panel
lip        = 12;   // retaining lip that keeps the cord from sliding off
t          = 6;    // wall thickness
hole_d     = 4.5;  // screw clearance (#8 / M4 wood screw)
head_d     = 9;    // countersink head diameter
hole_pitch = 46;   // centre-to-centre spacing of the two screws
fillet     = 6;    // inside corner reinforcement

$fn = 48;

module profile() {
    // Z shape: flange (on panel) -> web (standoff) -> lip (outward)
    square([flange + t, t]);                               // flange
    translate([flange, 0]) square([t, standoff + t]);     // web
    translate([flange, standoff]) square([t + lip, t]);   // lip
    // gusset between flange and web
    translate([flange, t]) rotate(90) polygon([[0,0],[fillet,0],[0,fillet]]);
}

difference() {
    rotate([90,0,0]) translate([0,0,-width]) linear_extrude(width) profile();
    for (x = [-hole_pitch/2, hole_pitch/2])
        translate([flange/2 - 1, width/2 + x, 0]) {
            translate([0,0,-1]) cylinder(d = hole_d, h = t + 2);
            translate([0,0,t - (head_d-hole_d)/2]) cylinder(d1 = hole_d, d2 = head_d, h = (head_d-hole_d)/2 + 0.01);
        }
}
