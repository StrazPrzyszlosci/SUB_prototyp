#!/usr/bin/env node
"use strict";
/*
 * P42A - rigid interface supported by elastic anchor points.
 * Explicit reduced-order analytical model, NOT validated contact FEM / fastener design.
 * All stiffnesses are HYPOTHETICAL N/mm per anchor; no real MDF or connector data.
 * Axes: X left-right, Z up, Y front-back. Driver center (231,250) mm on front.
 * Normal reaction N_i=k_i*(w0+ax*x_i+az*z_i); supports are signed bilateral springs
 * (contact lift-off/preload not modeled). In-plane shear allocated by stiffness.
 * Force X/Z at rear eccentricity e creates moments transferred into normal reactions.
 * Two research alternatives: A remote corner carrier; B two depthwise rails
 * tied by front reference brackets into four top/bottom shell stations.
 */
const fs=require("node:fs"),path=require("node:path");
const cfg={
 date:"2026-11-01",
 driver:"Dayton RSS390HF-4 provisional",
 face_center_external_mm:[231,250],outer_baffle_mm:[1020,500],
 flange_outer_radius_mm:194.2,
 mass_kg:[13.61,15],g_levels:[1,5,10],offset_e_mm:[90,120,180],
 k_normal_N_per_mm:[300,1000,3000],
 stiffness_patterns:["uniform","left_half","one_quarter"],
 directions:["X","Z","Y"],g0:9.80665,
 options:{
  direct8:{label:"P40 baseline: eight flange points",type:"legacy interface not independent cabinet support",
   anchors:Array.from({length:8},(_,i)=>[231+184*Math.cos(i*Math.PI/4),250+184*Math.sin(i*Math.PI/4)])},
  carrier4:{label:"A: wide carrier with four remote pads",type:"candidate independent outer carrier",
   anchors:[[75,45],[425,45],[75,455],[425,455]]},
  rails4:{label:"B: two depthwise rails with four top/bottom stations",type:"candidate vertical support rails",
   anchors:[[176,37],[286,37],[176,463],[286,463]]}
 },
 warning:"Reduced-order rigid plate with signed springs, not validated FEM, shell/bolt bearing, contact, joint stress or test."
};
function gauss3(A,b){
 const M=A.map((r,i)=>[...r,b[i]]);
 for(let i=0;i<3;i++){
  let p=i;for(let j=i+1;j<3;j++)if(Math.abs(M[j][i])>Math.abs(M[p][i]))p=j;
  if(Math.abs(M[p][i])<1e-10)throw Error("Singular supports");
  [M[p],M[i]]=[M[i],M[p]];
  const q=M[i][i];for(let a=i;a<4;a++)M[i][a]/=q;
  for(let j=0;j<3;j++)if(j!==i){const t=M[j][i];for(let a=i;a<4;a++)M[j][a]-=t*M[i][a];}
 }
 return M.map(r=>r[3]);
}
function solve(c,opt,mass,g,e,k,pattern,axis){
 const points=c.options[opt].anchors, x0=c.face_center_external_mm[0], z0=c.face_center_external_mm[1],
       xyz=points.map((p,i)=>{
        const dx=p[0]-x0,dz=p[1]-z0;
        const fac=pattern==="uniform"?1:pattern==="left_half"?(p[0]<x0?.5:1):(i===0?.25:1);
        return {id:i+1,x_mm:p[0],z_mm:p[1],dx,dz,k:k*fac};
       }),F=mass*c.g0*g,
       Fx=axis==="X"?F:0,Fz=axis==="Z"?F:0,Fn=axis==="Y"?F:0,
       Q=[Fn,-e*Fx,e*Fz],K=Array.from({length:3},()=>[0,0,0]);
 for(const q of xyz){const v=[1,q.dx,q.dz];for(let i=0;i<3;i++)for(let j=0;j<3;j++)K[i][j]+=q.k*v[i]*v[j];}
 const u=gauss3(K,Q),ktotal=xyz.reduce((v,p)=>v+p.k,0);
 const reactions=xyz.map(q=>{
   const normal=q.k*(u[0]+u[1]*q.dx+u[2]*q.dz);
   const shear=q.k/ktotal*Math.hypot(Fx,Fz);
   return {id:q.id,normal_N:normal,shear_N:shear,resultant_N:Math.hypot(normal,shear),signed_normal:q.k*(u[0]+u[1]*q.dx+u[2]*q.dz)};
 });
 const loadcheck=[
  reactions.reduce((s,z)=>s+z.normal_N,0),
  reactions.reduce((s,z,i)=>s+z.normal_N*xyz[i].dx,0),
  reactions.reduce((s,z,i)=>s+z.normal_N*xyz[i].dz,0)
 ];
 const err=Math.max(...loadcheck.map((v,i)=>Math.abs(v-Q[i])));
 if(err>1e-7)throw Error("Equilibrium residual "+err);
 const R=c.flange_outer_radius_mm;
 const maxRingNormal=Math.abs(u[0])+R*Math.hypot(u[1],u[2]);
 const minEdge=Math.min(...points.map(p=>Math.min(p[0],c.outer_baffle_mm[0]-p[0],p[1],c.outer_baffle_mm[1]-p[1])));
 const flangeClear=Math.min(...points.map(p=>Math.hypot(p[0]-x0,p[1]-z0)-R));
 return {option:opt,load_direction:axis,mass_kg:mass,accel_g:g,e_mm:e,nominal_k_N_mm:k,heterogeneity:pattern,
  number_of_anchors:points.length,force_N:+F.toFixed(5),
  max_signed_tension_reaction_N:+Math.max(0,...reactions.map(t=>t.normal_N)).toFixed(4),
  max_signed_compression_reaction_N:+Math.max(0,...reactions.map(t=>-t.normal_N)).toFixed(4),
  max_resultant_anchor_N:+Math.max(...reactions.map(t=>t.resultant_N)).toFixed(4),
  max_shear_anchor_N:+Math.max(...reactions.map(t=>t.shear_N)).toFixed(4),
  center_deflection_abs_mm:+Math.abs(u[0]).toFixed(7),
  max_reference_flange_normal_displacement_mm:+maxRingNormal.toFixed(7),
  max_rotation_rad:+Math.hypot(u[1],u[2]).toFixed(9),
  min_outer_panel_edge_mm:+minEdge.toFixed(4),
  nominal_front_flange_clearance_mm:+flangeClear.toFixed(4),
  max_equilibrium_residual:+err.toFixed(11)};
}
function run(){
 const rows=[];
 for(const option of Object.keys(cfg.options))
 for(const direction of cfg.directions)
 for(const g of cfg.g_levels)
 for(const e of cfg.offset_e_mm)
 for(const k of cfg.k_normal_N_per_mm)
 for(const pattern of cfg.stiffness_patterns)
 for(const mass of cfg.mass_kg)
  rows.push(solve(cfg,option,mass,g,e,k,pattern,direction));
 if(rows.length!==1458)throw Error("Expected 1458 "+rows.length);
 const reference=rows.filter(r=>r.mass_kg===13.61&&r.accel_g===5&&r.e_mm===120&&r.nominal_k_N_mm===1000&&r.heterogeneity==="uniform");
 const refTable=reference.map(x=>({option:x.option,direction:x.load_direction,
   max_resultant_anchor_N:x.max_resultant_anchor_N,max_flange_displacement_mm:x.max_reference_flange_normal_displacement_mm,
   rotation_rad:x.max_rotation_rad}));
 const notes=["All k springs are hypothetical and cannot be used to infer safety or compliance of MDF without measurements.",
  "Support anchors represent assumed load paths; connection from actual eight flange bolts into a carrier/rail is not modeled.",
  "Compression and uplift require unilateral contact; this signed bilateral model cannot predict actual clamping force.",
  "3D cabin, basket terminals, connector and tools collision NOT checked, only 2D flange and panel margins.",
  "Direct8 is a legacy mathematical comparator, NOT equivalent to eight real independent structural supports.",
  "Fastener ultimate strength, MDF peel/splitting, fatigue, shock timescale and acoustics remain unknown."];
 return {study:"P42A",date:"2026-11-01",method:"3x3 2D rigid-load-plate on signed independent normal anchor springs; ideal tangential shear distribution",cases:rows.length,
  inputs:cfg,reference_conditions:{mass_kg:13.61,g:5,e_mm:120,k_N_mm:1000,heterogeneity:"uniform"},
  reference:refTable,results:rows,warnings:notes};
}
function main(){
 const d=run(),target=path.join(__dirname,"..","wyniki","p41a_porownanie_sciezek_1458_20261101.json");
 fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,JSON.stringify(d,null,2)+"\n");
 console.log(JSON.stringify({cases:d.cases,reference:d.reference},null,2));
}
if(require.main===module)main();
module.exports={cfg,gauss3,solve,run};
