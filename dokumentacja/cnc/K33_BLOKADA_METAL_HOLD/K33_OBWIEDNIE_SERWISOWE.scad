// K33 SERVICE ENVELOPES ONLY, CNC HOLD. ext=true selects long row1.
ext=false;
if(true) translate([430, 45, 63]) cube([18, 312, 50]); // bar
if(true) translate([448, 160, 63]) cube([22, 80, 50]); // integral_nose
if(true) translate([448, 156, 63]) cube([4, 4, 50]); // root_F_envelope
if(true) translate([448, 240, 63]) cube([4, 4, 50]); // root_R_envelope
if(!ext) translate([430, 45, 179]) cube([18, 312, 50]); // bar
if(!ext) translate([448, 160, 179]) cube([22, 80, 50]); // integral_nose
if(!ext) translate([448, 156, 179]) cube([4, 4, 50]); // root_F_envelope
if(!ext) translate([448, 240, 179]) cube([4, 4, 50]); // root_R_envelope
if(ext) translate([430, 45, 179]) cube([18, 312, 50]); // bar
if(ext) translate([448, 160, 179]) cube([4, 80, 50]); // flange
if(ext) translate([452, 190, 194]) cube([295.1, 20, 20]); // tube_envelope
if(ext) translate([452, 188, 192]) cube([2, 24, 24]); // weld_envelope
if(ext) translate([452, 176, 185]) cube([4, 8, 8]); // M4_head
if(ext) translate([452, 176, 215]) cube([4, 8, 8]); // M4_head
if(ext) translate([452, 216, 185]) cube([4, 8, 8]); // M4_head
if(ext) translate([452, 216, 215]) cube([4, 8, 8]); // M4_head
if(true) translate([430, 45, 295]) cube([18, 312, 50]); // bar
if(true) translate([448, 160, 295]) cube([22, 80, 50]); // integral_nose
if(true) translate([448, 156, 295]) cube([4, 4, 50]); // root_F_envelope
if(true) translate([448, 240, 295]) cube([4, 4, 50]); // root_R_envelope
if(true) translate([430, 45, 401]) cube([18, 312, 50]); // bar
if(true) translate([448, 160, 401]) cube([22, 80, 50]); // integral_nose
if(true) translate([448, 156, 401]) cube([4, 4, 50]); // root_F_envelope
if(true) translate([448, 240, 401]) cube([4, 4, 50]); // root_R_envelope
