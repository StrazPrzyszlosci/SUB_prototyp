// K30 nominal research assembly, CNC HOLD. Axes X width Y depth Z height.
$fn=96;
state=100; // choose 100,120,150; targets, not measured volumes
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([0, 0, 0]) cube([1080, 22, 500]);
translate([231, 23, 250]) rotate([90, 0, 0]) cylinder(h=24,r=177.9);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([0, 22, 0]) cube([1080, 22, 500]);
translate([231, 45, 250]) rotate([90, 0, 0]) cylinder(h=24,r=177.9);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([0, 410, 0]) cube([1080, 22, 500]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([0, 44, 0]) cube([22, 366, 500]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1058, 44, 0]) cube([22, 366, 500]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([22, 44, 0]) cube([1036, 366, 22]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([22, 44, 478]) cube([1036, 366, 22]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([448, 44, 22]) cube([22, 366, 456]);
translate([447, 55, 88.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 341, 88.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 55, 204.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 341, 204.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 55, 320.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 341, 320.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 55, 426.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
translate([447, 341, 426.0]) rotate([0, 90, 0]) cylinder(h=24,r=3);
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
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([750, 44, 22]) cube([22, 366, 456]);
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
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([474, 60, 22]) cube([276, 8, 456]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([474, 332, 22]) cube([276, 8, 456]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 60, 22]) cube([286, 8, 456]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 332, 22]) cube([286, 8, 456]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 68, 22]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 282, 22]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 68, 138]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 282, 138]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 68, 254]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 282, 254]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 68, 370]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 282, 370]) cube([280, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 68, 466]) cube([280, 50, 12]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([470, 282, 466]) cube([280, 50, 12]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 68, 22]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 282, 22]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 68, 138]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 282, 138]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 68, 254]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 282, 254]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 68, 370]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 282, 370]) cube([286, 50, 18]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 68, 466]) cube([286, 50, 12]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([772, 282, 466]) cube([286, 50, 12]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([474, 70, 40]) cube([8, 260, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([733.1, 70, 40]) cube([8, 260, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 70, 40]) cube([251.10000000000002, 8, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 322, 40]) cube([251.10000000000002, 8, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 40]) cube([251.10000000000002, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 128]) cube([251.10000000000002, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([749.1, 70, 40]) cube([8, 260, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([1008.2, 70, 40]) cube([8, 260, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 70, 40]) cube([251.10000000000002, 8, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 322, 40]) cube([251.10000000000002, 8, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 78, 40]) cube([251.10000000000002, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 78, 128]) cube([251.10000000000002, 244, 8]);
}
if(state==100 || state==120) color([0.65, 0.65, 0.72, 0.4]) difference(){translate([741.1, 70, 40]) cube([8, 260, 96]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1018, 70, 40]) cube([22, 260, 96]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1040, 70, 40]) cube([18, 260, 96]);
}
color([0.8, 0.2, 0.2, 1]) difference(){translate([430, 45, 63.0]) cube([18, 306, 50]);
translate([429, 55, 88.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 341, 88.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
color([0.8, 0.2, 0.2, 1]) difference(){translate([448, 160, 63.0]) cube([22, 80, 50]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([474, 70, 156]) cube([8, 260, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([733.1, 70, 156]) cube([8, 260, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 70, 156]) cube([251.10000000000002, 8, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 322, 156]) cube([251.10000000000002, 8, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 156]) cube([251.10000000000002, 244, 8]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 244]) cube([251.10000000000002, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([749.1, 70, 156]) cube([8, 260, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([1008.2, 70, 156]) cube([8, 260, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 70, 156]) cube([251.10000000000002, 8, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 322, 156]) cube([251.10000000000002, 8, 96]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 78, 156]) cube([251.10000000000002, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 78, 244]) cube([251.10000000000002, 244, 8]);
}
if(state==100) color([0.65, 0.65, 0.72, 0.4]) difference(){translate([741.1, 70, 156]) cube([8, 260, 96]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1018, 70, 156]) cube([22, 260, 96]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1040, 70, 156]) cube([18, 260, 96]);
}
color([0.8, 0.2, 0.2, 1]) difference(){translate([430, 45, 179.0]) cube([18, 306, 50]);
translate([429, 55, 204.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 341, 204.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
if(state!=120) color([0.8, 0.2, 0.2, 1]) difference(){translate([448, 160, 179.0]) cube([22, 80, 50]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([474, 70, 272]) cube([8, 260, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([733.1, 70, 272]) cube([8, 260, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 70, 272]) cube([251.10000000000002, 8, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 322, 272]) cube([251.10000000000002, 8, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 272]) cube([251.10000000000002, 244, 8]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 360]) cube([251.10000000000002, 244, 8]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([749.1, 70, 272]) cube([8, 260, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([1008.2, 70, 272]) cube([8, 260, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 70, 272]) cube([251.10000000000002, 8, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 322, 272]) cube([251.10000000000002, 8, 96]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 78, 272]) cube([251.10000000000002, 244, 8]);
}
if(state==100) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([757.1, 78, 360]) cube([251.10000000000002, 244, 8]);
}
if(state==100) color([0.65, 0.65, 0.72, 0.4]) difference(){translate([741.1, 70, 272]) cube([8, 260, 96]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1018, 70, 272]) cube([22, 260, 96]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1040, 70, 272]) cube([18, 260, 96]);
}
color([0.8, 0.2, 0.2, 1]) difference(){translate([430, 45, 295.0]) cube([18, 306, 50]);
translate([429, 55, 320.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 341, 320.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
color([0.8, 0.2, 0.2, 1]) difference(){translate([448, 160, 295.0]) cube([22, 80, 50]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([474, 70, 388]) cube([8, 260, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([719.0, 70, 388]) cube([8, 260, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 70, 388]) cube([237.0, 8, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 322, 388]) cube([237.0, 8, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 388]) cube([237.0, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([482, 78, 456]) cube([237.0, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([735.0, 70, 388]) cube([8, 260, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([980.0, 70, 388]) cube([8, 260, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([743.0, 70, 388]) cube([237.0, 8, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([743.0, 322, 388]) cube([237.0, 8, 76]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([743.0, 78, 388]) cube([237.0, 244, 8]);
}
if(state==100 || state==120) color([0.75, 0.47, 0.2, 0.65]) difference(){translate([743.0, 78, 456]) cube([237.0, 244, 8]);
}
if(state==100 || state==120) color([0.65, 0.65, 0.72, 0.4]) difference(){translate([727.0, 70, 388]) cube([8, 260, 76]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1018, 70, 388]) cube([22, 260, 76]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([1040, 70, 388]) cube([18, 260, 76]);
}
color([0.65, 0.65, 0.72, 0.4]) difference(){translate([993, 70, 388]) cube([25, 260, 76]);
}
color([0.8, 0.2, 0.2, 1]) difference(){translate([430, 45, 401.0]) cube([18, 306, 50]);
translate([429, 55, 426.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
translate([429, 341, 426.0]) rotate([0, 90, 0]) cylinder(h=20,r=3);
}
color([0.8, 0.2, 0.2, 1]) difference(){translate([448, 160, 401.0]) cube([22, 80, 50]);
}
color([0.4,0.45,0.5]) translate([470, 46, 73.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 52.5, 85.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 50, 83.0]) cube([5, 10, 10]);
color([0.4,0.45,0.5]) translate([470, 332, 73.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 338.5, 85.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 336, 83.0]) cube([5, 10, 10]);
color([0.4,0.45,0.5]) translate([470, 46, 189.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 52.5, 201.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 50, 199.0]) cube([5, 10, 10]);
color([0.4,0.45,0.5]) translate([470, 332, 189.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 338.5, 201.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 336, 199.0]) cube([5, 10, 10]);
color([0.4,0.45,0.5]) translate([470, 46, 305.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 52.5, 317.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 50, 315.0]) cube([5, 10, 10]);
color([0.4,0.45,0.5]) translate([470, 332, 305.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 338.5, 317.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 336, 315.0]) cube([5, 10, 10]);
color([0.4,0.45,0.5]) translate([470, 46, 411.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 52.5, 423.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 50, 421.0]) cube([5, 10, 10]);
color([0.4,0.45,0.5]) translate([470, 332, 411.0]) cube([4, 18, 30]);
color([0.4,0.45,0.5]) translate([429, 338.5, 423.5]) cube([45, 5, 5]);
color([0.4,0.45,0.5]) translate([424, 336, 421.0]) cube([5, 10, 10]);
if(state==120) color([0.6,0.2,0.2]) {translate([448,160,179]) cube([4,80,50]); difference(){translate([452,190,194]) cube([295.1,20,20]); translate([454,192,196]) cube([291.1,16,16]);}}
