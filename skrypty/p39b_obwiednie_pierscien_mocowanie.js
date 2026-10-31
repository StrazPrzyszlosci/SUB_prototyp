#!/usr/bin/env node
"use strict";
// P39B: geometric CSG envelope screen ONLY. Not engineering approval, material strength or CNC.
const fs=require('node:fs'),path=require('node:path');
const P={"W":1020,"D":425,"H":500,"wall":22,"front":44,"cx":231,"cz":250,"driver_OD":388.4,"cutout":355.8,"BCD":368,"flange_hole":6.5,"driver_depth":178,"flange_projection":10.5,"ring1_x":448,"back_inner_y":403,"mat_start_y":353,"steel_density_kgm3":7850,"al_density_kgm3":2700};
function run(){
 const rings=[];for(const od of [392,400,408])for(const id of [356,360])for(const t of [2,4,6])for(const centerOffsetX of [-2,0,2]){
 const sideGap=P.cx+centerOffsetX-od/2-P.wall,braceGap=P.ring1_x-(P.cx+centerOffsetX+od/2),
 topGap=P.cz-od/2-P.wall,boreWeb=P.BCD/2-P.flange_hole/2-id/2;
 const volume_mm3=Math.PI/4*(od*od-id*id)*t-8*Math.PI/4*P.flange_hole*P.flange_hole*t;
 rings.push({od_mm:od,id_mm:id,t_mm:t,centerOffsetX_mm:centerOffsetX,
  inner_side_gap_mm:+sideGap.toFixed(3),first_brace_gap_x_mm:+braceGap.toFixed(3),top_gap_mm:+topGap.toFixed(3),
  metal_hole_ligament_mm:+boreWeb.toFixed(3),ring_weight_steel_kg:+(volume_mm3*1e-9*P.steel_density_kgm3).toFixed(3),
  ring_weight_al_kg:+(volume_mm3*1e-9*P.al_density_kgm3).toFixed(3),air_displacement_l:+(volume_mm3/1e6).toFixed(4),
  bolt_concentric_offset_mm:Math.abs(centerOffsetX),
  violates_geometry:sideGap<0||braceGap<0||topGap<0||boreWeb<0,unknown_strength:true});
 }
 const depth=[];for(const grilleProtrusion of [20,40,50,60,80])for(const rearConnectorProtrusion of [0,10,20,30]){
  const total=P.D+Math.max(grilleProtrusion,P.flange_projection)+rearConnectorProtrusion;
  depth.push({grilleProtrusion_mm:grilleProtrusion,rearConnectorProtrusion_mm:rearConnectorProtrusion,total_mm:total,
   reserve_mm:500-total,pass_total_le500mm:total<=500});
 }
 const ref=rings.find(x=>x.od_mm===400&&x.id_mm===356&&x.t_mm===4&&x.centerOffsetX_mm===0);
 if(!ref||ref.inner_side_gap_mm!==9||ref.first_brace_gap_x_mm!==17)throw Error('Ring geometry reference wrong');
 if(rings.length!==54||depth.length!==20)throw Error('Grid count wrong');
 const result={study:'P39B',date:'2026-11-01',status:'Conceptual 3D CSG only, no qualified fastener strength or CNC',
  inputs:P,cases:rings.length,ring_candidates:rings,depth_cases:depth.length,depth_envelope_scenarios:depth,
  reference_geometry:ref,warnings:["Ring is an EXAMPLE backer annulus; unknown true basket shape and terminal contact may make it impossible.","Manufacturer 8x6.5 are frame holes, not MDF drill prescriptions. Any ring misregistration requires fastener clearance/slotted hole redesign.","Thin 2.85mm MDF ligament at Ø6.5 and cutout remains even with a backer ring; load path, preload, crush, fatigue and leakage not checked.","No true collision with all module parts/lock access/driver gasket or full basket path established. Ring first brace separation is projected in x only.","Grille and terminal protrusions are hypothetical; max 500mm must include all real external hardware.","Do not machine this reference OpenSCAD as a validated component."]};
 const dest=path.join(__dirname,'..','wyniki','p39b_kolizje_pierscien_glebokosc_20261101.json');
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({cases:rings.length,depth_cases:depth.length,reference_geometry:ref},null,2));
}
if(require.main===module)run();module.exports={P,run};
