// K02, 2026-11-03. P30E cabinet + eight K01 local pads, reference model ONLY.
// NOT CNC: manufacturer 3D basket, terminal, seal, locks, fasteners and glue unverified.
// x global left->right; y outer front->rear; z bottom->top. All dimensions in mm.
$fn=96;
state_liters=100; // [100,120,150]
pad_depth=20;    // [20:30], K02 passage comparison; 20 preferable only for geometric access
show_shell=true;
show_modules=true;
show_braces=true;
show_pads=true;
show_driver_envelope=true;
W=1020;D=425;H=500;front=44;wall=22;
cx=231;cz=250;
R1=178.9;R2=205;pad_width=36;
assert(state_liters==100||state_liters==120||state_liters==150);
assert(pad_depth==20||pad_depth==30);
// reference P30E interior: x0=22, y0=44, z0=22; x=0..976, y=0..359, z=0..456
module front_pan(){
  color([0.72,0.60,0.45,.13])
  difference(){
    cube([W,front,H]);
    translate([cx,front/2,cz]) rotate([90,0,0])
        cylinder(d=355.8,h=front+2,center=true);
  }
}
module shell(){
  color([.7,.67,.57,.16]){
    translate([0,front,0])cube([wall,D-front-wall,H]);
    translate([W-wall,front,0])cube([wall,D-front-wall,H]);
    translate([wall,front,0])cube([W-2*wall,D-front-wall,wall]);
    translate([wall,front,H-wall])cube([W-2*wall,D-front-wall,wall]);
    translate([0,D-wall,0])cube([W,wall,H]);
  }
}
module brace_local(x){
  color([.22,.44,.67,.23]){
     // match P30A/P30E simplified four brace members
     translate([x+22,front,22])cube([22,359,22]);
     translate([x+22,front,22+456-22])cube([22,359,22]);
     translate([x+22,front,22+22])cube([22,10,456-44]);
     translate([x+22,front+359-22,22+22])cube([22,22,456-44]);
  }
}
module local_pad(i){
  // rotation about y=-theta to match K01 polygon (radial + tangential in XZ)
  color([.16,.56,.43,.94])
    translate([cx,front,cz])
      rotate([0,-45*i,0])
        translate([R1,0,-pad_width/2])
          cube([R2-R1,pad_depth,pad_width]);
}
module box_at_local(x,y,z,sx,sy,sz,col){
  color(col)
    translate([x+22-sx/2,y+front-sy/2,z+22-sz/2])
      cube([sx,sy,sz]);
}
module numbered_module(i){
  if(i<4){
    // Four small boxes centered at local y=253 after P30E shift -15mm.
    x=(i<2)?99:323;
    z=(i%2==0)?90:366;
    box_at_local(x,253,z,180,100,100,[.91,.61,.23,.55]);
  } else {
    // 16 big boxes, first bank at x849.5, second bank at x574.5.
    bank=(i-4>=8)?1:0;
    group=floor(((i-4)%8)/4);
    x=(bank==0)?849.5:574.5;
    y=(group==0)?243:83;
    z=[62,392,172,282][(i-4)%4];
    sy=(group==0)?120:150;
    box_at_local(x,y,z,210,sy,100,[.32,.55,.78,.45]);
  }
}
module included(i){
  if(state_liters==100) numbered_module(i);
  if(state_liters==120 && i>=4 && i<16) numbered_module(i);
  if(state_liters==150 && i==4) numbered_module(i);
}
module generic_basket(){
  // NOT the real cast aluminum frame; only a reminder of the unknown envelope.
  color([.27,.39,.47,.14])
    translate([cx,front+65,cz])
      rotate([90,0,0])cylinder(d=260,h=130,center=true);
}
if(show_shell){shell();front_pan();}
if(show_braces){brace_local(426);brace_local(701);}
if(show_pads)for(i=[0:7])local_pad(i);
if(show_modules)for(i=[0:19])included(i);
if(show_driver_envelope)generic_basket();
echo("K02 MODEL ONLY; 100L P30E has 20 modules, 120L has 12, 150L has one");
echo("K01/K02 pads total volume [L]",8*(R2-R1)*pad_width*pad_depth/1e6);
echo("K02 model does NOT verify real basket, tools, latches, sealed materials, or CNC");
