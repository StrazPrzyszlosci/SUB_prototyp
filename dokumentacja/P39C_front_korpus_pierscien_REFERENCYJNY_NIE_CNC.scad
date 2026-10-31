// P39C | reference parametric assembly. NOT CNC. OpenSCAD 2021.01 or later.
// The only source-backed geometry is P38A Dayton external frame, 8 holes and cutout.
// All wood braces, rear support and motor body are research envelopes.
// Coordinate convention: x left->right, y front outer surface->back, z bottom->top. Units mm.
// P39B reference backer annulus OD400/ID356/t4 is NOT strength-validated.
$fn=96;
W=1020; D=425; H=500;
wall=22; front=44;
cx=231; cz=250;
cutout_d=355.8; flange_od=388.4; bolt_pcd=368; bolt_d=6.5;
bolt_clocking_deg=0; // VERIFY PHYSICAL DRIVER BEFORE USING
ring_od=400; ring_id=356; ring_t=4;
grille_projection=40; terminal_projection=20;
show_baffle=true;
show_shell=true;
show_braces=true;
show_ring=true;
show_driver_envelope=true;
show_grille_envelope=false;
show_terminal_envelope=false;
assert(cx-ring_od/2-wall>=0,"Ring intersects the inner left wall");
assert(448-(cx+ring_od/2)>=0,"Ring projects onto first brace in X");
assert(cz-ring_od/2-wall>=0,"Ring intersects bottom inner panel");
assert(D+max(grille_projection,10.5)+terminal_projection<=500,
       "Hypothetical external front/rear envelopes exceed 500 mm");
echo("Ring-to-sidewall nominal clearance",cx-ring_od/2-wall);
echo("Ring-to-first-brace X-projection",448-cx-ring_od/2);
echo("MDF web at 6.5mm flange hole",bolt_pcd/2-bolt_d/2-cutout_d/2);
echo("Total external depth, hypothetical",D+max(grille_projection,10.5)+terminal_projection);

// Cylinder normal to front, along y; surfaces centered on given y.
module ycyl(d,t,x,y,z){
 translate([x,y,z]) rotate([90,0,0]) cylinder(d=d,h=t,center=true);
}
module front_baffle(){
 color([0.83,0.66,0.46,1.0]) difference(){
   cube([W,front,H]);
   ycyl(cutout_d,front+2,cx,front/2,cz);
 }
}
module cabinet_sides(){
 color([0.75,0.63,0.47,.45]) {
   translate([0,front,0]) cube([wall,D-front-wall,H]);
   translate([W-wall,front,0]) cube([wall,D-front-wall,H]);
   translate([wall,front,0]) cube([W-2*wall,D-front-wall,wall]);
   translate([wall,front,H-wall]) cube([W-2*wall,D-front-wall,wall]);
   translate([0,D-wall,0]) cube([W,wall,H]);
 }
}
module one_brace(external_x){
 color([0.22,0.54,0.72,.55]){
  translate([external_x,front,wall]) cube([wall,D-front-wall,wall]);
  translate([external_x,front,H-2*wall]) cube([wall,D-front-wall,wall]);
  translate([external_x,front,2*wall]) cube([wall,10,H-4*wall]);
  translate([external_x,D-2*wall,2*wall]) cube([wall,wall,H-4*wall]);
 }
}
module backer_ring(){
 color([0.25,0.27,0.31,.98])
 difference(){
  ycyl(ring_od,ring_t,cx,front+ring_t/2,cz);
  ycyl(ring_id,ring_t+1,cx,front+ring_t/2,cz);
  for(i=[0:7]) {
   ang=bolt_clocking_deg+45*i;
   ycyl(bolt_d,ring_t+1,cx+(bolt_pcd/2)*cos(ang),front+ring_t/2,
        cz+(bolt_pcd/2)*sin(ang));
  }
 }
}
module driver_reference(){
 // Opaque flange and translucent generic motor cylinder are NOT Dayton basket CAD.
 color([.12,.25,.34,.75]) ycyl(flange_od,10.5,cx,-5.25,cz);
 color([.15,.36,.60,.20]) ycyl(260,123.5,cx,front+123.5/2,cz);
}
module grille_reference(){
 color([0.36,.44,.49,.10])
 translate([0,-grille_projection,0]) cube([W,grille_projection,H]);
}
module terminal_reference(){
 // Deliberately stylized. True terminal location not selected.
 color([.9,.30,.2,.3]) translate([W-180,D,200])
 cube([90,terminal_projection,100]);
}
if(show_shell) cabinet_sides();
if(show_baffle) front_baffle();
if(show_braces) {one_brace(448);one_brace(723);}
if(show_ring) backer_ring();
if(show_driver_envelope) driver_reference();
if(show_grille_envelope) grille_reference();
if(show_terminal_envelope) terminal_reference();
