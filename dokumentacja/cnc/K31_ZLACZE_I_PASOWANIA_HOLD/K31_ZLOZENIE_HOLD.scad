// K31 corrected assembly, synthetic stock unless measurement flag in JSON.
// CNC HOLD: glue, plate retention and real driver/terminal interfaces unqualified.
$fn=64; state=100;
color([0.65,0.65,0.7,0.35]) difference(){translate([0, 0, 0]) cube([1080, 22, 500]);
translate([231, 23, 250]) rotate([90, 0, 0]) cylinder(h=24,r=177.9);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([0, 22, 0]) cube([1080, 22, 500]);
translate([231, 45, 250]) rotate([90, 0, 0]) cylinder(h=24,r=177.9);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([0, 410, 0]) cube([1080, 22, 500]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([0, 44, 0]) cube([22, 366, 500]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1058, 44, 0]) cube([22, 366, 500]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([22, 44, 0]) cube([1036, 366, 22]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([22, 44, 478]) cube([1036, 366, 22]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([448, 44, 22]) cube([22, 366, 456]);
translate([447, 55, 88.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 347, 88.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 55, 204.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 347, 204.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 55, 320.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 347, 320.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 55, 426.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 347, 426.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
hull(){
translate([447,68,42]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,68,136]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,42]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,136]) rotate([0,90,0]) cylinder(h=24,r=4);
}
hull(){
translate([447,68,158]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,68,252]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,158]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,252]) rotate([0,90,0]) cylinder(h=24,r=4);
}
hull(){
translate([447,68,274]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,68,368]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,274]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,368]) rotate([0,90,0]) cylinder(h=24,r=4);
}
hull(){
translate([447,68,390]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,68,464]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,390]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([447,332,464]) rotate([0,90,0]) cylinder(h=24,r=4);
}
}
color([0.65,0.65,0.7,0.35]) difference(){translate([750, 44, 22]) cube([22, 366, 456]);
hull(){
translate([749,68,44]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,68,134]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,44]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,134]) rotate([0,90,0]) cylinder(h=24,r=4);
}
hull(){
translate([749,68,160]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,68,250]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,160]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,250]) rotate([0,90,0]) cylinder(h=24,r=4);
}
hull(){
translate([749,68,276]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,68,366]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,276]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,366]) rotate([0,90,0]) cylinder(h=24,r=4);
}
hull(){
translate([749,68,392]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,68,462]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,392]) rotate([0,90,0]) cylinder(h=24,r=4);
translate([749,332,462]) rotate([0,90,0]) cylinder(h=24,r=4);
}
}
color([0.65,0.65,0.7,0.35]) difference(){translate([474, 60, 22]) cube([276, 8, 456]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([474, 332, 22]) cube([276, 8, 456]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 60, 22]) cube([286, 8, 456]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 332, 22]) cube([286, 8, 456]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 68, 22]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 282, 22]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 68, 138]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 282, 138]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 68, 254]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 282, 254]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 68, 370]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 282, 370]) cube([280, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 68, 466]) cube([280, 50, 12]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([470, 282, 466]) cube([280, 50, 12]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 68, 22]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 282, 22]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 68, 138]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 282, 138]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 68, 254]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 282, 254]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 68, 370]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 282, 370]) cube([286, 50, 18]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 68, 466]) cube([286, 50, 12]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([772, 282, 466]) cube([286, 50, 12]);
}
if(state==100 || state==120) color([0.65,0.65,0.7,0.35]) difference(){translate([741.1, 70, 40]) cube([8, 260, 96]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1018, 70, 40]) cube([22, 260, 96]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1040, 70, 40]) cube([18, 260, 96]);
}
color([0.8,0.2,0.2]) difference(){translate([430, 45, 63.0]) cube([18, 312, 50]);
translate([429, 55, 88.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 347, 88.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([448, 160, 63.0]) cube([22, 80, 50]);
}
if(state==100) color([0.65,0.65,0.7,0.35]) difference(){translate([741.1, 70, 156]) cube([8, 260, 96]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1018, 70, 156]) cube([22, 260, 96]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1040, 70, 156]) cube([18, 260, 96]);
}
color([0.8,0.2,0.2]) difference(){translate([430, 45, 179.0]) cube([18, 312, 50]);
translate([429, 55, 204.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 347, 204.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
if(state!=120) color([0.65,0.65,0.7,0.35]) difference(){translate([448, 160, 179.0]) cube([22, 80, 50]);
}
if(state==100) color([0.65,0.65,0.7,0.35]) difference(){translate([741.1, 70, 272]) cube([8, 260, 96]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1018, 70, 272]) cube([22, 260, 96]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1040, 70, 272]) cube([18, 260, 96]);
}
color([0.8,0.2,0.2]) difference(){translate([430, 45, 295.0]) cube([18, 312, 50]);
translate([429, 55, 320.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 347, 320.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([448, 160, 295.0]) cube([22, 80, 50]);
}
if(state==100 || state==120) color([0.65,0.65,0.7,0.35]) difference(){translate([727.0, 70, 388]) cube([8, 260, 76]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1018, 70, 388]) cube([22, 260, 76]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([1040, 70, 388]) cube([18, 260, 76]);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([993, 70, 388]) cube([25, 260, 76]);
}
color([0.8,0.2,0.2]) difference(){translate([430, 45, 401.0]) cube([18, 312, 50]);
translate([429, 55, 426.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 347, 426.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
color([0.65,0.65,0.7,0.35]) difference(){translate([448, 160, 401.0]) cube([22, 80, 50]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([474, 70, 40]) cube([8.0, 260, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([733.1, 70, 40]) cube([8.0, 260, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 70, 40]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 322.0, 40]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 40]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 128.0]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([749.1, 70, 40]) cube([8.0, 260, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([1008.2, 70, 40]) cube([8.0, 260, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 70, 40]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 322.0, 40]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 78.2, 40]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 78.2, 128.0]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([474, 70, 156]) cube([8.0, 260, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([733.1, 70, 156]) cube([8.0, 260, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 70, 156]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 322.0, 156]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 156]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 244.0]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([749.1, 70, 156]) cube([8.0, 260, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([1008.2, 70, 156]) cube([8.0, 260, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 70, 156]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 322.0, 156]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 78.2, 156]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 78.2, 244.0]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([474, 70, 272]) cube([8.0, 260, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([733.1, 70, 272]) cube([8.0, 260, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 70, 272]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 322.0, 272]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 272]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 360.0]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([749.1, 70, 272]) cube([8.0, 260, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([1008.2, 70, 272]) cube([8.0, 260, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 70, 272]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 322.0, 272]) cube([250.70000000000002, 8.0, 96]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 78.2, 272]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100) color([0.7,0.45,0.2,0.6]) difference(){translate([757.3000000000001, 78.2, 360.0]) cube([250.70000000000002, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([474, 70, 388]) cube([8.0, 260, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([719.0, 70, 388]) cube([8.0, 260, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 70, 388]) cube([236.6, 8.0, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 322.0, 388]) cube([236.6, 8.0, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 388]) cube([236.6, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([482.2, 78.2, 456.0]) cube([236.6, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([735.0, 70, 388]) cube([8.0, 260, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([980.0, 70, 388]) cube([8.0, 260, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([743.2, 70, 388]) cube([236.6, 8.0, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([743.2, 322.0, 388]) cube([236.6, 8.0, 76]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([743.2, 78.2, 388]) cube([236.6, 243.6, 8.0]);
}
if(state==100 || state==120) color([0.7,0.45,0.2,0.6]) difference(){translate([743.2, 78.2, 456.0]) cube([236.6, 243.6, 8.0]);
}
color([0.4,0.4,0.5]) translate([470, 46, 73.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([470, 338, 73.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([470, 46, 189.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([470, 338, 189.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([470, 46, 305.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([470, 338, 305.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([470, 46, 411.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([470, 338, 411.0]) cube([4, 18, 30]);
color([0.4,0.4,0.5]) translate([429,55,88.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,55,88.0]) rotate([0,90,0]) cylinder(h=5,r=5);
color([0.4,0.4,0.5]) translate([429,347,88.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,347,88.0]) rotate([0,90,0]) cylinder(h=5,r=5);
color([0.4,0.4,0.5]) translate([429,55,204.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,55,204.0]) rotate([0,90,0]) cylinder(h=5,r=5);
color([0.4,0.4,0.5]) translate([429,347,204.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,347,204.0]) rotate([0,90,0]) cylinder(h=5,r=5);
color([0.4,0.4,0.5]) translate([429,55,320.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,55,320.0]) rotate([0,90,0]) cylinder(h=5,r=5);
color([0.4,0.4,0.5]) translate([429,347,320.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,347,320.0]) rotate([0,90,0]) cylinder(h=5,r=5);
color([0.4,0.4,0.5]) translate([429,55,426.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,55,426.0]) rotate([0,90,0]) cylinder(h=5,r=5);
color([0.4,0.4,0.5]) translate([429,347,426.0]) rotate([0,90,0]) cylinder(h=50,r=2.5);
color([0.4,0.4,0.5]) translate([424,347,426.0]) rotate([0,90,0]) cylinder(h=5,r=5);
if(state==120) color([0.8,0.2,0.2]) {translate([448,160,179]) cube([4,80,50]); difference(){translate([452,190,194]) cube([295.1,20,20]);translate([454,192,196]) cube([291.1,16,16]);}}
