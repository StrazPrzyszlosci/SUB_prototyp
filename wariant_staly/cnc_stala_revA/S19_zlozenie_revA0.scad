// S19: single shared CAD assembly for fixed enclosure 102L rev A0, MDF t=22mm.
// VIEW ONLY, all source cutting profiles from generator.py. No G-code or CAM.
$fn=128;
view_pair=false;
show_nominal_basket=true;
show_front_cassette=true;
show_terminal_box=true;
show_debug_cutaway=false;
W=816.8;
H=473.3;
D=394.0;
T=22.0;
inner_D=D-3*T;
inner_W=W-2*T;
inner_H=H-2*T;
brace_w=inner_W-0.4;
brace_h=inner_H-0.4;
brace_window_w=brace_w-60;
brace_window_h=brace_h-60;
brace_start=2*T+(inner_D-T)/2;
driver_d=355.8;
driver_flange_d=388.4;
ring_outer_d=400;
ring_inner_d=358;
ring_t=6;
ring_pocket_d=400.4;
ring_pocket_depth=6.2;
pcd=368.0;
Cx=W/2;
Cz=H/2;
eps=0.02;

module cylinder_y(x,y,z,diameter,depth) {
    translate([x,y,z]) rotate([-90,0,0]) cylinder(d=diameter,h=depth);
}
module cylinder_x(x,y,z,diameter,depth) {
    translate([x,y,z]) rotate([0,90,0]) cylinder(d=diameter,h=depth);
}

module front_FR1() {
    color([.72,.61,.45]) difference() {
        cube([W,T,H]);
        cylinder_y(Cx,-eps,Cz,driver_d,T+2*eps);
        for(a=[0:45:315])
            cylinder_y(Cx+pcd/2*cos(a),-eps,Cz+pcd/2*sin(a),5.6,T+2*eps);
        // RAMPA M6x18 in front, pilot D10 depth18. Not through the 44mm pack.
        for(x=[26.4,W-26.4],z=[28.65,H-28.65])
            cylinder_y(x,-eps,z,10,18+eps);
    }
}
module front_FR2() {
    color([.73,.64,.47]) difference() {
        translate([0,T,0])cube([W,T,H]);
        cylinder_y(Cx,T-eps,Cz,driver_d,T+2*eps);
        cylinder_y(Cx,T-eps,Cz,ring_pocket_d,ring_pocket_depth+eps);
        for(a=[0:45:315])
            cylinder_y(Cx+pcd/2*cos(a),T+ring_pocket_depth-eps,
                       Cz+pcd/2*sin(a),6.5,4+eps);
        for(z=[Cz-194,Cz+194])
            cylinder_y(Cx,T+ring_pocket_depth-eps,z,4.2,5+eps);
    }
}
module steel_ring() {
    color([.56,.61,.67])difference(){
        cylinder_y(Cx,T+0.2,Cz,ring_outer_d,ring_t);
        cylinder_y(Cx,T+0.2-eps,Cz,ring_inner_d,ring_t+2*eps);
        for(a=[0:45:315])
            cylinder_y(Cx+pcd/2*cos(a),T+0.2-eps,
                       Cz+pcd/2*sin(a),4.2,ring_t+2*eps);
        for(z=[Cz-194,Cz+194])
            cylinder_y(Cx,T+0.2-eps,z,4.0,ring_t+2*eps);
    }
}
module walls() {
    color([.73,.62,.45]) {
        translate([0,2*T,0]) cube([T,inner_D,H]); // left side
        translate([T,2*T,0]) cube([inner_W,inner_D,T]); // floor
        translate([T,2*T,H-T]) cube([inner_W,inner_D,T]); // roof
        translate([0,D-T,0]) cube([W,T,H]); // sealed back
    }
    color([.75,.63,.46]) difference() {
        translate([W-T,2*T,0])cube([T,inner_D,H]);
        // cable window D30 through MDF, supported by external sealed base AL3
        cylinder_x(W-T-eps,330,Cz,30,T+2*eps);
        // RAMPA SKD330 M6x18, blind holes from OUTSIDE wall.
        for(y=[282,338],z=[Cz-24,Cz+24])
            cylinder_x(W-18,y,z,10,18+eps);
    }
}
module window_brace() {
    color([.59,.50,.38])difference() {
        translate([T+.2,brace_start,T+.2])cube([brace_w,T,brace_h]);
        translate([Cx,brace_start-eps,Cz])
            rotate([-90,0,0])
                linear_extrude(height=T+2*eps)
                    offset(r=3)
                        square([brace_window_w-6,brace_window_h-6],center=true);
    }
}
module cassette() {
    // Outer MDF12 784x436; 24mm standoffs from face and ≤2mm finish.
    for(x=[26.4,W-26.4],z=[28.65,H-28.65])
        color([.52,.54,.58])
          difference() {
            cylinder_y(x,-24,z,16,24);
            cylinder_y(x,-24-eps,z,6.6,24+2*eps);
          }
    color([.32,.31,.30])difference() {
        translate([(W-784)/2,-36,(H-436)/2])cube([784,12,436]);
        translate([Cx,-36-eps,Cz])cube([744,12+2*eps,396],center=true);
        for(x=[26.4,W-26.4],z=[28.65,H-28.65])
            cylinder_y(x,-36-eps,z,6.6,12+2*eps);
    }
    // Fabric/grille finish drawn as a plane; real acoustic mesh is distinct part.
    color([.2,.3,.38,.18])
       translate([(W-784)/2,-38,(H-436)/2])
           cube([784,2,436]);
}
module basket_envelope() {
    // Manufacturer shows flange D388.4 and full depth178; below is NOT STEP basket.
    color([.18,.32,.72,.32])
      cylinder_y(Cx,0,Cz,355.8,167.5);
    color([.2,.23,.26,.4])
      cylinder_y(Cx,-10.5,Cz,388.4,10.5);
}
module speaker_terminal_box() {
    // Envelope X 70, Y80, Z72; outside RIGHT cabinet side.
    // Base, outside wall, face, back and top/bottom made of AL3.
    color([.65,.67,.7]) {
        difference(){
            translate([W,270,Cz-36]) cube([3,80,72]);
            cylinder_x(W-eps,330,Cz,16.5,3+2*eps);
            for(y=[282,338],z=[Cz-24,Cz+24])
                cylinder_x(W-eps,y,z,6.6,3+2*eps);
        }
        translate([W+67,270,Cz-36])cube([3,80,72]);
        translate([W+3,347,Cz-33])cube([64,3,66]);
        translate([W+3,273,Cz-36])cube([64,74,3]);
        translate([W+3,273,Cz+33])cube([64,74,3]);
        // Front service panel 64x66 at Y270, Neutrik D24 and M3 holes.
    }
    color([.51,.54,.58])difference(){
        translate([W+3,270,Cz-33])cube([64,3,66]);
        cylinder_y(W+35,270-eps,Cz,24,3+2*eps);
        for(x=[W+35-14.6,W+35+14.6],z=[Cz-14.6,Cz+14.6])
            cylinder_y(x,270-eps,z,3.4,3+2*eps);
        for(x=[W+10,W+60],z=[Cz-26,Cz+26])
            cylinder_y(x,270-eps,z,3.4,3+2*eps);
    }
    // gland envelope sourced from LAPP M16, Ø21.1 max cap, Cmax34mm.
    color([.16,.16,.18,.8])
        cylinder_x(W+3,330,Cz,21.1,34);
    // Neutrik body envelope nominal, NOT full 3D CAD part
    color([.18,.18,.18,.8])
        cylinder_y(W+35,273,Cz,24,21.25);
}
module cabinet() {
    front_FR1(); front_FR2(); steel_ring(); walls(); window_brace();
    if(show_nominal_basket) basket_envelope();
    if(show_front_cassette) cassette();
    if(show_terminal_box) speaker_terminal_box();
}
cabinet();
if(view_pair) translate([W+230,0,0]) cabinet();
