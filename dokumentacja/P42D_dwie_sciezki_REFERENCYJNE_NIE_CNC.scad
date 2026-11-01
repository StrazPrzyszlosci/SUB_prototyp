// P42D - EXPLORATORY 3D paths; geometry only, NOT CNC or checked load paths.
// OpenSCAD, units mm. Change variant to "rails4" to compare.
// Driver basket/magnet and bolted connections are SURROGATES.
$fn=72;
variant="carrier4"; // carrier4 or rails4
show_panel=true;
show_driver_envelope=true;
show_supports=true;
show_straight_links=false; // WARNING: some straight 2D links cross cutout (P42C).
baffle_W=1020;baffle_D=425;baffle_H=500;front_t=44;wall_t=22;
driver_x=231;driver_z=250;cutout_d=355.8;frame_d=388.4;bolt_r=184;
carrier_points=[[75,45],[425,45],[75,455],[425,455]];
rails_points=[[176,37],[286,37],[176,463],[286,463]];
points=variant=="carrier4"?carrier_points:rails_points;
half_width=9;
assert(variant=="carrier4"||variant=="rails4","Unknown variant");
assert(driver_x-frame_d/2>wall_t,"Driver flanged edge crosses left inner wall");
assert(driver_z-frame_d/2>wall_t,"Driver flanged edge crosses lower inner wall");
module ycylinder(d,h,x,y,z){
 translate([x,y,z])rotate([90,0,0])cylinder(d=d,h=h,center=true);
}
module panel(){
 color([0.80,0.65,0.48,.75])difference(){
  cube([baffle_W,front_t,baffle_H]);
  ycylinder(cutout_d,front_t+2,driver_x,front_t/2,driver_z);
 }
}
module basket_envelope(){
 color([.22,.36,.52,.50])ycylinder(frame_d,10.5,driver_x,-5.25,driver_z);
 color([.35,.55,.65,.16])ycylinder(260,123.5,driver_x,front_t+123.5/2,driver_z);
}
module pad(q){
 color([.26,.58,.65,.85])translate([q[0]-half_width,front_t,q[1]-half_width])
 cube([2*half_width,30,2*half_width]);
}
module rail(q){
 color([.35,.58,.60,.65])translate([q[0]-half_width,front_t,q[1]-half_width])
 cube([2*half_width,baffle_D-front_t-wall_t,2*half_width]);
}
module link_segment(a,b){
 // Unqualified straight carrier link: may project into cutout/motor.
 color([.87,.43,.32,.70])hull(){
  ycylinder(8,7,a[0],front_t+8,a[1]);
  ycylinder(8,7,b[0],front_t+8,b[1]);
 }
}
function dist2(a,b)=(a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1]);
function nearest_pad_idx(b)=let(v=[for(i=[0:len(points)-1])dist2(points[i],b)])
 search(min(v),v)[0];
if(show_panel)panel();
if(show_driver_envelope)basket_envelope();
if(show_supports)for(p=points) {
 if(variant=="carrier4")pad(p);
 else rail(p);
}
if(show_straight_links)for(i=[0:7]){
 bolt=[driver_x+bolt_r*cos(45*i),driver_z+bolt_r*sin(45*i)];
 link_segment(bolt,points[nearest_pad_idx(bolt)]);
}
echo("P41 supports:",variant,"points:",len(points));
echo("All support-to-driver links and wall joints are NOT qualified. Do not use for CNC.");
