#!/usr/bin/env node
"use strict";
// P38A: source-grounded 2D reference, NOT verified CNC or screw pattern.
// Dayton PDF: https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf
const fs=require("node:fs"),path=require("node:path");
const C={"W":1020,"D":425,"H":500,"wall":22,"front":44,"X":231,"Z":250,"OD":388.4,"CUT":355.8,"BCD":368,"HOLE":6.5,"DEPTH":178,"FLANGE":10.5,"HOLES":8,"ring_x":[448,723],"mat":50,"maxdepth":500};
function calc(){
 const p=C,r=p.BCD/2;
 const holes=Array.from({length:p.HOLES},(_,i)=>({number:i+1,angle_deg:i*45,x_mm:+(p.X+r*Math.cos(i*Math.PI/4)).toFixed(4),z_mm:+(p.Z+r*Math.sin(i*Math.PI/4)).toFixed(4)}));
 const clearance={
  wood_radial_at_flange_hole_mm:+(r-p.CUT/2-p.HOLE/2).toFixed(4),
  outer_flange_land_mm:+(p.OD/2-r-p.HOLE/2).toFixed(4),
  flange_margin_from_side_inner_face_mm:+(p.X-p.OD/2-p.wall).toFixed(4),
  flange_x_to_first_brace_external_mm:+(p.ring_x[0]-p.X-p.OD/2).toFixed(4),
  bolt_edge_x_to_first_brace_external_mm:+(p.ring_x[0]-p.X-r-p.HOLE/2).toFixed(4),
  projected_total_depth_surface_mount_mm:p.D+p.FLANGE,
  remaining_depth_budget_mm:p.maxdepth-p.D-p.FLANGE,
  rear_mat_to_driver_gap_surface_mm:p.D-p.wall-p.mat-(p.DEPTH-p.FLANGE)};
 return {study:"P38A",date:"2026-11-01",status:"NOT CNC / provisional CAD profile",source:"Manufacturer Dayton Audio RSS390HF-4 drawing; official datasheet",specification:C,
  external_origin:"lower left, x right, z up",local_origin:"inner cavity lower left",local_center_mm:[p.X-p.wall,p.Z-p.wall],
  ring_local_x_mm:p.ring_x.map(x=>x-p.wall),holes,clearance,insert_OD_scenarios_mm:[6.5,8,10,12,14,16].map(d=>({OD_mm:d,remaining_radial_wood_mm:+(r-d/2-p.CUT/2).toFixed(3)})),
  warnings:["Frame Ø6.5 holes are NOT specified MDF drill pilots.","Assumed eight-hole rotational phase; verify physical speaker before drilling.","Residual radial ligament 2.85mm requires a separate load-path/fastener study.","DXF contains visual REFERENCE circles and should never be used unreviewed for machining.","Actual driver basket, countersink, gasket, screws, tool clearance, grille and terminal not modeled."]};
}
function svg(d){
 const p=d.specification;
 const hs=d.holes.map(q=>`<circle cx="${q.x_mm}" cy="${p.H-q.z_mm}" r="${p.HOLE/2}" fill="#e18b57" stroke="#7b4325" stroke-width="1"/>`).join("");
 return `<svg xmlns="http://www.w3.org/2000/svg" width="1090" height="625" viewBox="-20 -50 1090 625"><rect x="-20" y="-50" width="1090" height="625" fill="white"/><text x="5" y="-20" font-family="Arial" font-size="26" font-weight="bold" fill="#24455b">P38A — rzeczywiste wymiary kosza Dayton / szkic 2D</text>
 <rect width="1020" height="500" fill="#f2e9de" stroke="#805e40" stroke-width="2"/><rect x="22" y="22" width="976" height="456" fill="none" stroke="#6a98ab" stroke-dasharray="7 5"/>
 <circle cx="231" cy="250" r="194.2" fill="#d3e1ec" stroke="#3d718f" stroke-width="1.8"/>
 <circle cx="231" cy="250" r="184" fill="none" stroke="#d77a42" stroke-dasharray="5 4"/>
 <circle cx="231" cy="250" r="177.9" fill="#fff" stroke="#263f52" stroke-width="3"/>${hs}
 <line x1="448" x2="448" y1="0" y2="500" stroke="#b1754c" stroke-dasharray="7 6"/>
 <line x1="723" x2="723" y1="0" y2="500" stroke="#b1754c" stroke-dasharray="7 6"/>
 <g font-family="Arial" fill="#2f5164"><text x="490" y="90" font-size="20">Otwór Ø355,8 mm</text><text x="490" y="123" font-size="20">Średnica zewn. Ø388,4 mm</text><text x="490" y="156" font-size="20">8 otworów Ø6,5 / BCD Ø368</text><text x="490" y="189" font-size="18">Oś zewnętrzna 231, 250 mm</text><text x="490" y="222" font-size="18">Oś wewnętrzna 209, 228 mm</text><text x="490" y="325" font-size="21" fill="#a74828">MDF między otworem Ø6,5</text><text x="490" y="350" font-size="21" fill="#a74828">a wycięciem: tylko 2,85 mm</text><text x="490" y="385" font-size="18">Mocowanie trzeba zaprojektować osobno.</text></g>
 <text x="0" y="543" font-family="Arial" font-size="16" fill="#a14532">RYSUNEK BADAWCZY — NIE WYDAWAĆ DO CNC. Położenia śrub sprawdzić na rzeczywistym głośniku.</text></svg>\n`;
}
function dxf(d){
 const p=d.specification,seq=["0","SECTION","2","HEADER","9","$INSUNITS","70","4","0","ENDSEC","0","SECTION","2","ENTITIES"];
 const push=(code,val)=>{seq.push(String(code),String(val))};
 const line=(layer,x1,y1,x2,y2)=>{push(0,"LINE");push(8,layer);push(10,x1);push(20,y1);push(30,0);push(11,x2);push(21,y2);push(31,0)};
 const circle=(layer,x,y,r)=>{push(0,"CIRCLE");push(8,layer);push(10,x);push(20,y);push(30,0);push(40,r)};
 line("PANEL_OUTLINE_REF",0,0,p.W,0);line("PANEL_OUTLINE_REF",p.W,0,p.W,p.H);
 line("PANEL_OUTLINE_REF",p.W,p.H,0,p.H);line("PANEL_OUTLINE_REF",0,p.H,0,0);
 circle("CUTOUT_REF_NOT_CNC",p.X,p.Z,p.CUT/2);
 circle("FRAME_OUTER_REF",p.X,p.Z,p.OD/2);circle("BOLT_BCD_REF",p.X,p.Z,p.BCD/2);
 d.holes.forEach(h=>circle("FLANGE_HOLES_NOT_PILOTS",h.x_mm,h.z_mm,p.HOLE/2));
 line("RING_X_PROJECTION",448,0,448,p.H);line("RING_X_PROJECTION",723,0,723,p.H);
 seq.push("0","ENDSEC","0","EOF");return seq.join("\n")+"\n";
}
function main(){const data=calc();const dir=path.join(__dirname,"..","wyniki");fs.mkdirSync(dir,{recursive:true});
fs.writeFileSync(path.join(dir,"p38a_front_geom_20261101.json"),JSON.stringify(data,null,2)+"\n");
fs.writeFileSync(path.join(dir,"p38a_front_NIE_CNC.svg"),svg(data));
fs.writeFileSync(path.join(dir,"p38a_front_NIE_CNC.dxf"),dxf(data));
if(Math.abs(data.clearance.wood_radial_at_flange_hole_mm-2.85)>1e-5)throw Error("Mounting ligament regression");
console.log("P38A verified hole count",data.holes.length,"ligament",data.clearance.wood_radial_at_flange_hole_mm);
}
if(require.main===module)main();
