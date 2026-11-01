#!/usr/bin/env node
"use strict";
// P41B: provisional 3D AABB collision test; source P34B module sets / braces.
// All coordinates transformed interior to exterior by (+22,+44,+22) mm.
// Does NOT model flange-to-support links, true basket shape, tools or load capability.
const fs=require("node:fs"),path=require("node:path");
const acoustic=require("./p34b_przestrzenne_pole_p30e.js");
const cfg={
 date:"2026-11-01",size_mm:[1020,425,500],wall_mm:22,driver_center:[231,250],flange_radius_mm:194.2,
 layouts:{
  carrier4:{pads:[[75,45],[425,45],[75,455],[425,455]],y:[44,74]},
  rails4:{pads:[[176,37],[286,37],[176,463],[286,463]],y:[44,403]}
 },
 widths_half_mm:[6,9,12],shifts_mm:[[0,0],[-2,-2],[2,2]],
 envelope_radius_mm:[130,170,205],volumes:["100","120","150"]};
function collide(a,b){
 return a[0].every((lo,i)=>a[1][i]>b[0][i]&&b[1][i]>lo);
}
function extBox(b){return [b[0].map((v,i)=>v+[22,44,22][i]),b[1].map((v,i)=>v+[22,44,22][i])]}
function buildState(){
 const g=acoustic.geometry(acoustic.cfg),states={};
 for(const state of cfg.volumes){
  const choice=acoustic.cfg.module_sets.find(z=>z.id===state);
  states[state]=[...g.bars,...g.large.slice(0,choice.large),...g.small.slice(0,choice.small)].map(extBox);
 }
 return states;
}
function model(){
 const blocks=buildState(),rows=[];
 for(const layout of Object.keys(cfg.layouts))
 for(const state of cfg.volumes)
 for(const halfwidth of cfg.widths_half_mm)
 for(const shift of cfg.shifts_mm)
 for(const motorRadius of cfg.envelope_radius_mm){
  const q=cfg.layouts[layout],points=q.pads.map(p=>[p[0]+shift[0],p[1]+shift[1]]);
  const boxes=points.map(p=>[[p[0]-halfwidth,q.y[0],p[1]-halfwidth],[p[0]+halfwidth,q.y[1],p[1]+halfwidth]]);
  const solidCollisions=boxes.reduce((acc,box)=>acc+blocks[state].filter(b=>collide(box,b)).length,0);
  const radial=boxes.map(box=>{
   const x=cfg.driver_center[0],z=cfg.driver_center[1];
   const dx=x<box[0][0]?box[0][0]-x:x>box[1][0]?x-box[1][0]:0;
   const dz=z<box[0][2]?box[0][2]-z:z>box[1][2]?z-box[1][2]:0;
   return Math.hypot(dx,dz);
  });
  const minR=Math.min(...radial);
  const sideClear=Math.min(...boxes.flatMap(box=>[box[0][0]-cfg.wall_mm,cfg.size_mm[0]-cfg.wall_mm-box[1][0]]));
  const edgeClear=Math.min(...boxes.flatMap(box=>[box[0][2]-cfg.wall_mm,cfg.size_mm[2]-cfg.wall_mm-box[1][2]]));
  const motorGap=minR-motorRadius,flangeGap=minR-cfg.flange_radius_mm;
  rows.push({layout,state,halfwidth_mm:halfwidth,shift_ext_mm:shift,motor_surrogate_radius_mm:motorRadius,
   module_brace_aabb_collisions:solidCollisions,
   min_radial_to_center_mm:+minR.toFixed(4),motor_surrogate_gap_mm:+motorGap.toFixed(4),
   flange_gap_mm:+flangeGap.toFixed(4),inner_sidewall_gap_mm:+sideClear.toFixed(4),
   inner_topbottom_gap_mm:+edgeClear.toFixed(4),
   passes_tested_envelopes:solidCollisions===0&&motorGap>=0&&flangeGap>=0&&sideClear>=0&&edgeClear>=0});
 }
 if(rows.length!==162)throw Error("162 cases needed "+rows.length);
 const summary={n:rows.length,pass:rows.filter(x=>x.passes_tested_envelopes).length,
  pass_carrier:rows.filter(x=>x.layout==="carrier4"&&x.passes_tested_envelopes).length,
  pass_rails:rows.filter(x=>x.layout==="rails4"&&x.passes_tested_envelopes).length,
  module_bar_collisions:rows.filter(x=>x.module_brace_aabb_collisions>0).length,
  motor_envelope_failures:rows.filter(x=>x.motor_surrogate_gap_mm<0).length,
  side_wall_failures:rows.filter(x=>x.inner_sidewall_gap_mm<0||x.inner_topbottom_gap_mm<0).length};
 return {study:"P41B",date:"2026-11-01",status:"research geometry envelope; NOT real CAD fit",inputs:cfg,summary,rows,
  warnings:["The physical Dayton basket is not represented; 205mm is a hypothetical stress-test motor radius NOT a measured specification.",
   "P34B block shapes and braces are approximate. Exact flange-to-carrier and flange-to-rail connecting struts, brackets, bolts and access tools are OMITTED.",
   "AABB non-overlap alone cannot qualify exact 3D curved parts, tolerance, static strength or manufacturing.",
   "A rail or pad has no specified load path into real MDF/brace joints; no strain or contact assessment."]};
}
function main(){
 const z=model(),out=path.join(__dirname,"..","wyniki","p41b_obwiednie_162_20261101.json");
 fs.writeFileSync(out,JSON.stringify(z,null,2)+"\n");console.log(JSON.stringify(z.summary,null,2));
}
if(require.main===module)main();module.exports={cfg,model};
