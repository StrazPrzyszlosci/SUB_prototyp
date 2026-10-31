#!/usr/bin/env node
"use strict"; // P40A: idealized 8-bolt 3D equilibrium with moment, NOT strength certification
const fs=require("node:fs"),path=require("node:path");
const conf={"date":"2026-11-01","g0":9.80665,"bolt_circle_r_mm":184,"nbolt":8,"driver_mass_kg":[12,15,18],"acceleration_g":[1,3,5,10],"force_eccentricity_y_mm":[60,120,180],"active_bolt_sets":{"all8":[0,1,2,3,4,5,6,7],"sym4":[0,2,4,6],"six_adjacent":[0,1,2,3,4,5],"four_adjacent":[0,1,2,3]},"force_dir":["x","z","y"],"warning":"Ideal equal-stiffness linear 3D bolt-group reaction; no flange contact or preload, friction, material strengths, shock dynamics, safety certification."};
function solve(c, mass,accel,ey,pattern,dir){
 const ids=c.active_bolt_sets[pattern],rad=c.bolt_circle_r_mm, F=mass*c.g0*accel;
 const coords=ids.map(i=>({id:i,x:rad*Math.cos(i*Math.PI/4),z:rad*Math.sin(i*Math.PI/4)}));
 const cx=coords.reduce((v,q)=>v+q.x,0)/coords.length,cz=coords.reduce((v,q)=>v+q.z,0)/coords.length;
 const a=coords.map(q=>({...q,u:q.x-cx,v:q.z-cz})),Sxx=a.reduce((v,q)=>v+q.u*q.u,0),Szz=a.reduce((v,q)=>v+q.v*q.v,0),Sxz=a.reduce((v,q)=>v+q.u*q.v,0);
 const det=Sxx*Szz-Sxz*Sxz;if(det<1e-7)throw Error("Singular bolt arrangement");
 const fx=dir==="x"?F:0,fz=dir==="z"?F:0,fn=dir==="y"?F:0;
 // F_x at y=e => M_z=-e*Fx; F_z at y=e => M_x=e*Fz;
 // physical normal force F_y at global x=z=0, with bolt centroid (cx,cz),
 // M_z about centroid=-cx*Fn, -M_x=cz*Fn.
 const Mz=-ey*fx-cx*fn, Qz=-ey*fz+cz*fn;
 const alpha=(Mz*Szz-Qz*Sxz)/det,beta=(Qz*Sxx-Mz*Sxz)/det;
 const reactions=a.map(q=>{const n=fn/a.length+alpha*q.u+beta*q.v;
 const shear=Math.hypot(fx/a.length,fz/a.length);
 return {id:q.id,normal_N:n,shear_N:shear,resultant_N:Math.hypot(n,shear)};});
 const checkF=reactions.reduce((v,q)=>v+q.normal_N,0),
 checkMz=reactions.reduce((v,q,i)=>v+q.normal_N*a[i].u,0),
 checkQz=reactions.reduce((v,q,i)=>v+q.normal_N*a[i].v,0);
 if(Math.abs(checkF-fn)>1e-5||Math.abs(checkMz-Mz)>1e-5||Math.abs(checkQz-Qz)>1e-5)throw Error("Equilibrium failed");
 const tension=Math.max(0,...reactions.map(q=>q.normal_N)),compression=Math.max(0,...reactions.map(q=>-q.normal_N));
 return {mass_kg:mass,accel_g:accel,eccentricity_mm:ey,active:pattern,active_count:ids.length,direction:dir,force_N:F,
  max_signed_tension_N:+tension.toFixed(4),max_signed_compression_N:+compression.toFixed(4),
  max_resultant_N:+Math.max(...reactions.map(q=>q.resultant_N)).toFixed(4),
  mean_shear_N:+(Math.hypot(fx,fz)/ids.length).toFixed(4),
  reference_equal_8_share_N:+(F/8).toFixed(4),
  force_ratio_to_ideal8:+(Math.max(...reactions.map(q=>q.resultant_N))/(F/8)).toFixed(5)};
}
function main(){
 const results=[];
 for(const m of conf.driver_mass_kg)for(const g of conf.acceleration_g)
 for(const e of conf.force_eccentricity_y_mm)for(const p of Object.keys(conf.active_bolt_sets))
 for(const d of conf.force_dir)results.push(solve(conf,m,g,e,p,d));
 if(results.length!==432)throw Error("case count");
 const x=results.find(t=>t.mass_kg===15&&t.accel_g===5&&t.eccentricity_mm===120&&t.active==='all8'&&t.direction==='x');
 if(!x||x.max_resultant_N<100||x.max_resultant_N>300)throw Error("reference equilibrium");
 const doc={study:"P40A",date:"2026-11-01",cases:results.length,inputs:conf,results,
 interpretation:["The signed reactions are linear-compliance idealizations, compression is not a bolt's tensile load and positive tension is not automatically borne by bolts without flange contact mechanics.","True preload, gasket compression, friction and flange prying can move forces substantially.","Bolt count below eight represents a hypothetical out-of-service fastener case, not a permitted operation.","No bolt stress strengths, MDF tear-out or dynamic transient qualification established."]};
 const name=path.join(__dirname,"..","wyniki","p40a_reakcje_432_20261101.json");
 fs.mkdirSync(path.dirname(name),{recursive:true});fs.writeFileSync(name,JSON.stringify(doc,null,2)+"\n");
 console.log(JSON.stringify({cases:results.length,reference:x},null,2));
}
if(require.main===module)main(); module.exports={conf,solve,main};
