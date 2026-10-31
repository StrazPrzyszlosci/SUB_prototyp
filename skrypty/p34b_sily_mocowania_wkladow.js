#!/usr/bin/env node
"use strict";
// P34B: research force envelopes only, not design certification for fasteners.
const fs=require("node:fs"),path=require("node:path");
const conditions={
  "states": [
    {
      "liters": 100,
      "largeRear": 8,
      "largeFront": 8,
      "small": 4
    },
    {
      "liters": 120,
      "largeRear": 8,
      "largeFront": 4,
      "small": 0
    },
    {
      "liters": 150,
      "largeRear": 1,
      "largeFront": 0,
      "small": 0
    }
  ],
  "module_shapes_mm": {
    "rear": [
      210,
      120,
      100
    ],
    "front": [
      210,
      150,
      100
    ],
    "small": [
      180,
      100,
      100
    ]
  },
  "mdf_density": [
    650,
    730,
    800
  ],
  "module_wall_mm": [
    6,
    8,
    10
  ],
  "acceleration_g": [
    1,
    3,
    5,
    10
  ],
  "net_pressure_delta_Pa": [
    250,
    1000,
    2500
  ],
  "support_points_per_module": 2,
  "design_factor": 2,
  "source": "P30E 20 removable sealed AABB modules, shell-body estimate (not physical mounting)."
};
function estimate(conds){
 const rows=[];
 for(const state of conds.states)for(const rho of conds.mdf_density)for(const wall of conds.module_wall_mm)
 for(const acc of conds.acceleration_g)for(const pressure of conds.net_pressure_delta_Pa){
  const blocks=Object.entries({rear:state.largeRear,front:state.largeFront,small:state.small})
  .filter(([_,n])=>n>0).map(([kind,count])=>{
   const [x,y,z]=conds.module_shapes_mm[kind],inner=(x-2*wall)*(y-2*wall)*(z-2*wall);
   if(inner<0)throw Error("wall too thick");
   const volumeMDFm3=(x*y*z-inner)*1e-9;
   const m=rho*volumeMDFm3,faceArea=Math.max(x*y,x*z,y*z)*1e-6;
   const Fgrav=m*acc*9.80665,Fp=faceArea*pressure;
   const Ftotal=Fgrav+Fp;
   return {kind,count,mass_kg:m,largest_face_m2:faceArea,F_grav_N:Fgrav,F_net_diff_pressure_N:Fp,
     F_worst_sum_N:Ftotal,required_capacity_per_fixing_N:Ftotal*conds.design_factor/conds.support_points_per_module};
  });
  rows.push({liters:state.liters,rho,wall_mm:wall,acceleration_g:acc,net_differential_pressure_Pa:pressure,
   block_count:blocks.reduce((s,x)=>s+x.count,0),total_module_mass_kg:blocks.reduce((s,x)=>s+x.count*x.mass_kg,0),
   max_required_capacity_per_fixing_N:Math.max(...blocks.map(x=>x.required_capacity_per_fixing_N)),
   blocks});
 }
 if(rows.length!==324)throw Error("expected 324");
 return {study:"P34B",date:"2026-10-31",cases:rows.length,conditions,rows,warnings:["This is a single-module force envelope (weight times acceleration plus differential pressure force on largest face), not joint FEM, not a true screw pullout or fatigue test.","Pressure differential on opposite faces of one closed module is presumed, deliberately conservative; physical acoustic pressure nearly cancels at low frequency.","Design factor 2 and 2 mounts are hypothetical, not validated certification; torsion/peel and distributed forces omitted.","Mass excludes anchors, seals, paint and any additional foam insert; closed insert construction may change.","Acceleration 1/3/5/10g denotes study loads only, not a certified drop or transportation rating.","Do not select fasteners until adhesive, actual MDF, geometry and measured load paths are evaluated."]};
}
if(require.main===module){
 const out=estimate(conditions);
 if(out.cases!==324)throw Error("case count");
 const file=path.join(__dirname,"..","wyniki","p34b_moduly_wklady_324_20261031.json");
 fs.mkdirSync(path.dirname(file),{recursive:true});
 fs.writeFileSync(file,JSON.stringify(out,null,2)+"\n");
 console.log(JSON.stringify({cases:out.cases,reference:out.rows.find(z=>z.liters===100&&z.rho===730&&z.wall_mm===8&&z.acceleration_g===5&&z.net_differential_pressure_Pa===1000)},null,2));
}
module.exports={conditions,estimate};
