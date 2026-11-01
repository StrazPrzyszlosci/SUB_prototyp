#!/usr/bin/env node
"use strict";
/* P42C provisional straight load-link projected opening checks.
 * Pure 2D XZ front projection; NOT full 3D collision/strength.
 * Physical links can be angled in 3D, routed around basket, or attached elsewhere.
 * Straight-link paths begin at bolt centers, which do NOT make screws / pads viable.
 */
const fs=require("node:fs"),path=require("node:path");
const cfg={date:"2026-11-01",cx:231,cz:250,bcd_radius_mm:184,aperture_radius_mm:177.9,
  candidate_paths:{
   carrier4:[[75,45],[425,45],[75,455],[425,455]],
   rails4:[[176,37],[286,37],[176,463],[286,463]]
  },assumed_link_halfwidth_mm:[2,4,5]};
function distanceToSegment(a,b,c){
 const dx=b[0]-a[0],dz=b[1]-a[1],len2=dx*dx+dz*dz;
 const t=Math.max(0,Math.min(1,-((a[0]-c[0])*dx+(a[1]-c[1])*dz)/len2));
 return {point_parameter_t:t,radius_mm:Math.hypot(a[0]+t*dx-c[0],a[1]+t*dz-c[1])};
}
function calculate(){
 const center=[cfg.cx,cfg.cz],bolts=Array.from({length:8},(_,i)=>
  [cfg.cx+cfg.bcd_radius_mm*Math.cos(i*Math.PI/4),cfg.cz+cfg.bcd_radius_mm*Math.sin(i*Math.PI/4)]);
 const rows=[];
 for(const [name,anchors] of Object.entries(cfg.candidate_paths))
 for(const half of cfg.assumed_link_halfwidth_mm)
 for(const [i,b] of bolts.entries()){
  const closest=anchors.map((p,j)=>({p,j,L:Math.hypot(p[0]-b[0],p[1]-b[1])})).sort((a,b)=>a.L-b.L)[0];
  const d=distanceToSegment(b,closest.p,center);
  rows.push({layout:name,bolt_id:i+1,anchor_id:closest.j+1,link_width_mm:half*2,
   length_mm:+closest.L.toFixed(4),minimum_centerline_radius_mm:+d.radius_mm.toFixed(4),
   projected_edge_margin_mm:+(d.radius_mm-half-cfg.aperture_radius_mm).toFixed(4),
   projected_aperture_interference:d.radius_mm-half<cfg.aperture_radius_mm-1e-10});
 }
 if(rows.length!==48)throw Error("Need 48 links");
 const counts={};
 for(const [name] of Object.entries(cfg.candidate_paths))
 for(const half of cfg.assumed_link_halfwidth_mm){
  const selected=rows.filter(r=>r.layout===name&&r.link_width_mm===2*half);
  counts[name+"_width"+2*half]=selected.filter(x=>x.projected_aperture_interference).length;
 }
 return {study:"P42C",date:"2026-11-01",method:"straight nearest-pad links, exact point-to-segment XZ geometry, offset by link half-width",
  cases:rows.length,source_dimensions:"Dayton RSS390HF-4 manufacturer 8 holes BCD368 and aperture D355.8",
  inputs:cfg,interference_counts:counts,rows,
  warnings:["Only orthographic 2D front projection; a 3D link behind the baffle may bypass a cutout, but it may hit the actual basket or magnet.",
   "Link cross-section/plane, head, washer, flange radius, screw pilot and fastening to MDF are not designed.",
   "The nearest-anchor straight segment is a convenience heuristic, not an optimized or validated structural load path.",
   "The projected hole interference can only reject this idealized STRAIGHT connection in the assumed plane, not the entire carrier/rail concept."]};
}
function main(){
 const a=calculate(),file=path.join(__dirname,"..","wyniki","p41c_proste_laczniki_48_20261101.json");
 fs.writeFileSync(file,JSON.stringify(a,null,2)+"\n");console.log(JSON.stringify(a.interference_counts,null,2));
}
if(require.main===module)main();module.exports={cfg,distanceToSegment,calculate};
