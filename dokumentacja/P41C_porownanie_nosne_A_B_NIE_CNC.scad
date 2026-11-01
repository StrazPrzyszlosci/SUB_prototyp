// P41C — hypothesis only: A C-shaped load carrier, B two beams to first brace.
// NOT for CNC. No accurate Dayton basket, screw heads, rail joints, MDF strengths.
// Unit mm. x right, y to rear, z up. Param: -D 'concept="B"'
$fn=96;
concept="A";
W=1020;D=425;H=500;side=22;front=44;
cx=231;cz=250;cutout_d=355.8;driver_flange_d=388.4;
concept_A_centers=[[80,55],[231,35],[380,55],[420,125],[420,375],[380,445],[231,465],[80,445]];
concept_B_centers=[[80,55],[231,35],[380,55],[451,95],[451,405],[380,445],[231,465],[80,445]];
show_shell=true;
show_basket_envelope=true;
assert(concept=="A"||concept=="B","Select A or B");
assert(70>side,"carrier inner edge");
assert(435<448,"carrier must avoid first brace in plan X");
assert(D+40+20<=500,"depth limit: hypothetical 40mm front grille, 20mm terminal");
function minval(v)=min(v);
module normal_cylinder(d,h,xx,yy,zz) {translate([xx,yy,zz])rotate([90,0,0])cylinder(d=d,h=h,center=true);}
module shell(){
 color([.87,.72,.52,.25]){
  difference(){cube([W,front,H]);normal_cylinder(cutout_d,front+2,cx,front/2,cz);}
  translate([0,front,0])cube([side,D-front-side,H]);
  translate([W-side,front,0])cube([side,D-front-side,H]);
  translate([side,front,0])cube([W-2*side,D-front-side,side]);
  translate([side,front,H-side])cube([W-2*side,D-front-side,side]);
  translate([0,D-side,0])cube([W,side,H]);
 }
 color([.26,.58,.76,.26]){
  for(x=[448,723]){
   translate([x,front,side])cube([side,D-front-side,side]);
   translate([x,front,H-2*side])cube([side,D-front-side,side]);
   translate([x,front,2*side])cube([side,10,H-4*side]);
   translate([x,D-2*side,2*side])cube([side,side,H-4*side]);
  }
 }
}
module carrier_A(){
 // C-shape cut from 365x440x6mm plate; open at left where cutout approaches the boundary.
 color([.25,.42,.64,.89])
 difference(){
   translate([70,44,30])cube([365,6,440]);
   normal_cylinder(370,8,cx,47,cz);
   for(v=concept_A_centers)normal_cylinder(8,8,v[0],47,v[1]);
 }
}
module brace_rails_B(){
 // Upper and lower rails; their physical joints and bending are only analytical.
 color([.30,.52,.69,.9])
 difference(){
   union(){
    translate([70,44,25])cube([396,25,45]);
    translate([70,44,430])cube([396,25,45]);
    translate([434,44,70])cube([33,25,55]);  // toward 1st brace: upper tab
    translate([434,44,375])cube([33,25,55]); // toward 1st brace: lower tab
   }
   for(v=concept_B_centers)normal_cylinder(8,29,v[0],56,v[1]);
 }
}
module source_envelope(){
 // This is NOT the Dayton basket CAD; only a test cylinder of diameter 360 after baffle.
 color([.80,.31,.24,.2])normal_cylinder(360,120,cx,105,cz);
 color([.20,.27,.30,.5])normal_cylinder(388.4,10.5,cx,-5.25,cz);
}
module anchor_indicators(){
 for(v=concept=="A"?concept_A_centers:concept_B_centers){
  color([.88,.36,.16,.65])normal_cylinder(12,7,v[0],52,v[1]);
 }
}
echo("SELECTED CONCEPT",concept);
echo("DRAWING STATUS: only general load-path topology; no strength or assembly validation");
if(show_shell)shell();
if(concept=="A")carrier_A();else brace_rails_B();
if(show_basket_envelope)source_envelope();
anchor_indicators();
