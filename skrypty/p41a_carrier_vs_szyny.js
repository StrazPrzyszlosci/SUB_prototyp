#!/usr/bin/env node
"use strict";
// P41A - numerical spring-supported RIGID carrier/rail comparison; 2D accessible anchor locations only.
// Units: N, mm; not an experimental strength test, no contact/beam deformation in this solver.
const fs=require("node:fs"),path=require("node:path");
const cfg={
  "date": "2026-11-01",
  "coordinate_system": "front external x right z up; y back; all lengths mm",
  "driver_center_xz_mm": [
    231,
    250
  ],
  "cabinet_mm": [
    1020,
    425,
    500
  ],
  "wall_mm": 22,
  "flange_outer_radius_mm": 194.2,
  "anchor_tool_radius_mm": 8,
  "bolt_pcd_radius_mm": 184,
  "idealized_force_eccentricity_mm": [
    60,
    120,
    180
  ],
  "mass_kg": [
    13.6,
    15
  ],
  "acceleration_g": [
    1,
    5,
    10
  ],
  "directions": [
    "x",
    "z",
    "y"
  ],
  "reference_stiffness_N_per_mm": [
    100,
    300,
    1000
  ],
  "relative_connection_factor": [
    0.5,
    1,
    3,
    10
  ],
  "omit_one_anchor": [
    false,
    true
  ],
  "g0": 9.80665,
  "concepts": {
    "A_carrier": {
      "description": "8 exterior-face backer anchors around the driver, all into unmeasured MDF; no proven 3D carrier geometry",
      "coords": [
        [
          80,
          55
        ],
        [
          231,
          35
        ],
        [
          380,
          55
        ],
        [
          420,
          125
        ],
        [
          420,
          375
        ],
        [
          380,
          445
        ],
        [
          231,
          465
        ],
        [
          80,
          445
        ]
      ],
      "special_ids": [
        3,
        4
      ],
      "unknown_interface": "A steel/aluminum shaped backer is assumed infinitely stiff; those points are hypothetical anchors, not a validated carrier assembly."
    },
    "B_brace_rails": {
      "description": "top/bottom rails plus two hypothetical direct anchor points at first brace x448-470, y unknown",
      "coords": [
        [
          80,
          55
        ],
        [
          231,
          35
        ],
        [
          380,
          55
        ],
        [
          451,
          95
        ],
        [
          451,
          405
        ],
        [
          380,
          445
        ],
        [
          231,
          465
        ],
        [
          80,
          445
        ]
      ],
      "special_ids": [
        3,
        4
      ],
      "unknown_interface": "x451 anchors overlap the existing first brace projection and require a 3D end joint; load transfer and stiffness are unmeasured."
    }
  }
};
function linearSolve3(mat,b){
 const A=mat.map((r,i)=>r.concat([b[i]]));
 for(let j=0;j<3;j++){
  let best=j;for(let i=j+1;i<3;i++)if(Math.abs(A[i][j])>Math.abs(A[best][j]))best=i;
  if(Math.abs(A[best][j])<1e-8)throw Error("singular anchor group "+JSON.stringify(mat));
  [A[j],A[best]]=[A[best],A[j]];
  const pivot=A[j][j];for(let k=j;k<4;k++)A[j][k]/=pivot;
  for(let i=0;i<3;i++)if(i!==j){const f=A[i][j];for(let k=j;k<4;k++)A[i][k]-=f*A[j][k];}
 }
 return A.map(r=>r[3]);
}
function model(c,concept,mass,accel,e,dir,k0,factor,omit){
 const a=c.concepts[concept].coords.map(([x,z],i)=>({id:i,x,z,dx:x-c.driver_center_xz_mm[0],dz:z-c.driver_center_xz_mm[1],k:k0*(c.concepts[concept].special_ids.includes(i)?factor:1)}));
 if(omit)a.splice(3,1);
 const b=[1,0,0],K=Array.from({length:3},()=>[0,0,0]);
 for(const p of a){
  const H=[1,p.dx,p.dz];for(let i=0;i<3;i++)for(let j=0;j<3;j++)K[i][j]+=p.k*H[i]*H[j];
 }
 const F=mass*c.g0*accel,Fx=dir==="x"?F:0,Fz=dir==="z"?F:0,Fy=dir==="y"?F:0;
 const f=[Fy,-e*Fx,-e*Fz],q=linearSolve3(K,f);
 const ksum=a.reduce((z,p)=>z+p.k,0);
 const reactions=a.map(p=>{
  const n=p.k*(q[0]+q[1]*p.dx+q[2]*p.dz),shear=F*Math.sqrt((dir==="x"?1:0)+(dir==="z"?1:0))*p.k/ksum;
  return {id:p.id,normal_N:n,shear_N:shear,resultant_N:Math.hypot(n,shear)};
 });
 const sumN=reactions.reduce((s,p)=>s+p.normal_N,0),sumMz=reactions.reduce((s,p,i)=>s+p.normal_N*a[i].dx,0),sumQz=reactions.reduce((s,p,i)=>s+p.normal_N*a[i].dz,0);
 if(Math.max(Math.abs(sumN-Fy),Math.abs(sumMz+e*Fx),Math.abs(sumQz+e*Fz))>1e-5)throw Error("equilibrium");
 const leftMargin=Math.min(...a.map(p=>p.x-c.wall_mm)),topMargin=Math.min(...a.map(p=>500-c.wall_mm-p.z));
 const maxR=Math.max(...reactions.map(z=>z.resultant_N)),maxT=Math.max(0,...reactions.map(z=>z.normal_N)),minN=Math.min(...reactions.map(z=>z.normal_N));
 return {concept,mass_kg:mass,accel_g:accel,eccentricity_mm:e,direction:dir,k_base_N_per_mm:k0,special_factor:factor,omit_one_anchor:omit,
  n_anchors:a.length,force_N:+F.toFixed(3),max_resultant_N:+maxR.toFixed(3),max_tensile_normal_N:+maxT.toFixed(3),max_compressive_normal_N:+(-Math.min(0,minN)).toFixed(3),
  max_shear_N:+Math.max(...reactions.map(z=>z.shear_N)).toFixed(3),
  mean_body_normal_translation_mm:+q[0].toFixed(6),
  max_abs_normal_anchor_displacement_mm:+Math.max(...a.map(p=>Math.abs(q[0]+q[1]*p.dx+q[2]*p.dz))).toFixed(6),
  theta_x_mrad:+(q[2]*1e3).toFixed(5),theta_z_mrad:+(q[1]*1e3).toFixed(5),
  max_ratio_to_P40_equal8:+(maxR/(F/8)).toFixed(5),
  reactions_N:reactions.map(z=>({id:z.id,n:+z.normal_N.toFixed(4),shear:+z.shear_N.toFixed(4)}))};
}
function geometry(c){
 const rows=[];
 for(const [name,con] of Object.entries(c.concepts)){
 for(let i=0;i<con.coords.length;i++){
 const [x,z]=con.coords[i],r=Math.hypot(x-231,z-250),margin_outer=r-c.flange_outer_radius_mm-c.anchor_tool_radius_mm;
 const margins=[x-c.wall_mm-c.anchor_tool_radius_mm,1020-c.wall_mm-x-c.anchor_tool_radius_mm,z-c.wall_mm-c.anchor_tool_radius_mm,500-c.wall_mm-z-c.anchor_tool_radius_mm];
 rows.push({concept:name,id:i,x,z,radial_flange_tool_margin_mm:+margin_outer.toFixed(3),
  min_inside_panel_tool_margin_mm:+Math.min(...margins).toFixed(3),
  x_hits_first_brace_projection:x>=448&&x<=470,
  passed_2d_envelope:margin_outer>=0&&Math.min(...margins)>=0});
 }}
 return rows;
}
function main(){
 const anchors=geometry(cfg);const results=[];
 for(const con of Object.keys(cfg.concepts))for(const m of cfg.mass_kg)
 for(const g of cfg.acceleration_g)for(const e of cfg.idealized_force_eccentricity_mm)
 for(const dir of cfg.directions)for(const k of cfg.reference_stiffness_N_per_mm)
 for(const factor of cfg.relative_connection_factor)for(const omit of cfg.omit_one_anchor)
 results.push(model(cfg,con,m,g,e,dir,k,factor,omit));
 if(results.length!==2592||anchors.length!==16)throw Error("P41A wrong number of scenarios");
 if(anchors.some(a=>!a.passed_2d_envelope))throw Error("P41A anchor collides in 2D");
 const p=results.find(x=>x.concept==='A_carrier'&&x.mass_kg===15&&x.accel_g===5&&x.eccentricity_mm===120&&x.direction==='x'&&x.k_base_N_per_mm===300&&x.special_factor===3&&!x.omit_one_anchor);
 if(!p||p.max_resultant_N<100||p.max_resultant_N>350)throw Error("P41A reference regression");
 const out={study:'P41A',date:'2026-11-01',status:'RIGID frame and bilateral linear anchor springs, NOT material strength or contact FEM',
 cases:results.length,inputs:cfg,anchor_geometry:anchors,
 results_columns:['concept','mass_kg','accel_g','eccentricity_mm','direction','k_base_N_per_mm','special_factor','omit_one_anchor','max_resultant_N','max_tensile_normal_N','max_compressive_normal_N','max_abs_normal_anchor_displacement_mm','theta_x_mrad','theta_z_mrad'],
 results:results.map(x=>[x.concept==='A_carrier'?'A':'B',x.mass_kg,x.accel_g,x.eccentricity_mm,x.direction,x.k_base_N_per_mm,x.special_factor,x.omit_one_anchor?1:0,x.max_resultant_N,x.max_tensile_normal_N,x.max_compressive_normal_N,x.max_abs_normal_anchor_displacement_mm,x.theta_x_mrad,x.theta_z_mrad]),
 reference_detailed_reactions:results.filter(x=>x.mass_kg===15&&x.accel_g===5&&x.eccentricity_mm===120&&x.k_base_N_per_mm===300&&x.special_factor===3&&!x.omit_one_anchor),
 warnings:["Anchor locations are 2D only; unknown real basket, bolts, 3D tools and 20 module paths.","Assumed rigid load distributor, stiffness of MDF and brace never measured; real contact/friction/opening unmodeled.","No selected material, load requirement, safety factor, fatigue or CNC approval."]};
 const file=path.join(__dirname,'..','wyniki','p41a_carrier_vs_szyny_2592_20261101.json');
 fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(out)+'\n');
 console.log(JSON.stringify({cases:results.length,anchor_positions:anchors.length,base:p},null,2));
}
if(require.main===module)main();module.exports={cfg,linearSolve3,model,geometry,main};
