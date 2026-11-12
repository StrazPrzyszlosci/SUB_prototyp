// S10 - one fixed 102 L enclosure A, computational assembly ONLY.
// NOT A CNC DRAWING. Does not certify driver fit, fasteners, glue, terminal or grille.
// Source: S06 nominal panels, S07 Dayton envelope and K42 trial ring.
$fn = 96;
show_pair = false;
show_driver_envelope = true;
show_connector_placeholder = true;
W = 816.8;
H = 473.3;
D = 394.0;
T = 22.0;
inner_depth = 328.0;
cx = W / 2;
cz = H / 2;
front_cutout = 355.8;
ring_outer = 400.0;
ring_inner = 358.0;
ring_thickness = 6.0;
ring_pocket_outer = 400.4;
ring_pocket_depth = 6.2;
brace_w = 772.6;
brace_h = 429.1;
brace_open_w = 712.6;
brace_open_h = 369.1;
brace_r = 3.0;
brace_y = 197.0;
eps = 0.02;

// Cylinders along +Y, located using the same assembly coordinates as S06.
module cylinder_y(diameter, y_start, length) {
    translate([cx, y_start, cz])
        rotate([-90,0,0])
            cylinder(d = diameter, h = length);
}

// Fixed front 44 mm. Ring is captive in FR2 but is NOT a tested connection.
module front1() {
    color([0.77,0.67,0.49])
    difference() {
        cube([W,T,H]);
        cylinder_y(front_cutout,-eps,T+2*eps);
    }
}
module front2() {
    color([0.73,0.63,0.45])
    difference() {
        translate([0,T,0]) cube([W,T,H]);
        cylinder_y(front_cutout,T-eps,T+2*eps);
        cylinder_y(ring_pocket_outer,T-eps,ring_pocket_depth+eps);
    }
}
module ring_trial() {
    color([0.63,0.69,0.72])
    difference() {
        cylinder_y(ring_outer,T+0.2,ring_thickness);
        cylinder_y(ring_inner,T+0.2-eps,ring_thickness+2*eps);
    }
}
module sides() {
    color([0.76,0.66,0.49]) {
        translate([0,44,0]) cube([T,inner_depth,H]);
        translate([W-T,44,0]) cube([T,inner_depth,H]);
    }
}
module bottom_top() {
    color([0.77,0.67,0.49]) {
        translate([T,44,0]) cube([W-2*T,inner_depth,T]);
        translate([T,44,H-T]) cube([W-2*T,inner_depth,T]);
    }
}
module rear() {
    color([0.72,0.60,0.42])
        translate([0,D-T,0]) cube([W,T,H]);
}
module brace() {
    // Outline from S06, nominal 0.1 mm clearance on each side.
    color([0.60,0.52,0.39])
    difference() {
        translate([T+0.1,brace_y,T+0.1])
            cube([brace_w,T,brace_h]);
        translate([cx,brace_y-eps,cz])
            rotate([-90,0,0])
                linear_extrude(height=T+2*eps)
                    offset(r=brace_r)
                        square([brace_open_w-2*brace_r,
                                brace_open_h-2*brace_r],center=true);
    }
}
module envelope_not_real_driver() {
    // Full cylindrical 355.8 mm envelope up to 178 mm from front plane:
    // intentionally conservative as a visualization, NOT measured basket contour.
    color([0.17,0.38,0.65,0.18])
        cylinder_y(front_cutout,0,178);
}
module connector_not_real() {
    // S05 external sideways mounting bracket envelope; no hole in MDF yet.
    color([0.92,0.43,0.13,0.4])
        translate([W,270,cz-36])
            cube([70,80,72]);
}
module cabinet_a() {
    front1();
    front2();
    ring_trial();
    sides();
    bottom_top();
    rear();
    brace();
    if (show_driver_envelope) envelope_not_real_driver();
    if (show_connector_placeholder) connector_not_real();
}
cabinet_a();
if (show_pair) translate([W+240,0,0]) cabinet_a();
// A second identical module is translated, not mirrored: only room placement changes.
