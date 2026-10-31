#!/usr/bin/env node
"use strict";
// P36A: analytic static plate compliance (Navier SSSS) × 324 design scenarios.
// NOT physically validated cabinet stiffness or frequency-domain acoustic response.
const fs=require("node:fs"),path=require("node:path");
const inputs={
  "date": "2026-10-31",
  "W_mm": 1020,
  "D_mm": 425,
  "H_mm": 500,
  "front_thickness_mm": 44,
  "driver_hole_d_mm": 355.8,
  "t_wall_mm": [
    18,
    22,
    25,
    28
  ],
  "E_GPa": [
    1.5,
    2.1,
    3
  ],
  "rho_kgm3": [
    650,
    730,
    800
  ],
  "nu": 0.3,
  "V_l": [
    100,
    120,
    150
  ],
  "supports": [
    "no_braces",
    "one_ideal_line",
    "two_ideal_lines"
  ],
  "pressure_80Hz": {
    "100": {
      "front": 0.929808,
      "back": 1.134342,
      "left": 0.696862,
      "right": 1.541625,
      "top": 0.991168,
      "bottom": 1.015926
    },
    "120": {
      "front": 0.945733,
      "back": 1.098816,
      "left": 0.772883,
      "right": 1.368966,
      "top": 0.993341,
      "bottom": 1.018311
    },
    "150": {
      "front": 0.945635,
      "back": 1.043213,
      "left": 0.616859,
      "right": 1.349796,
      "top": 0.980257,
      "bottom": 0.986821
    }
  },
  "ambient_air_density_kgm3": 1.2,
  "sound_speed_ms": 343,
  "pressure_test_Pa": 1000,
  "series_mn_max_odd": 25,
  "convergence_odd": [
    7,
    15,
    25
  ],
  "support_at_x_mm": [
    426,
    701
  ],
  "restrictions": [
    "Rectangular isotropic Kirchhoff plates SSSS all around. One/two ideal internal support lines only, not calibrated joints.",
    "Front opening ignored in stiffness (intact front 44mm, optimistic, uncalibrated).",
    "Plate stiffness cannot be considered assembly FEM, panel bends independently and neighboring panels don't exchange moments.",
    "Wall thickness differences alter inside geometry, placement and nominal volume, so those comparisons are exploratory only.",
    "P35A 80Hz wall pressure ratios applied to static compliance as a one-way average-face load diagnostic, not dynamic FSI.",
    "This model does not estimate real SPL, THD or fatigue, and does not release CNC."
  ]
};
function panel(a,b,t,E,nu,rho,oddMax){
 const D=E*t**3/(12*(1-nu**2));
 let compliance=0,wcenter=0;
 for(let m=1;m<=oddMax;m+=2)for(let n=1;n<=oddMax;n+=2){
  const stiffness=(m/a)**2+(n/b)**2;
  const ampl=16/(D*Math.PI**6*m*n*stiffness*stiffness);
  compliance+=(4*a*b/(Math.PI**2*m*n))*ampl;
  wcenter+=ampl*Math.sin(m*Math.PI/2)*Math.sin(n*Math.PI/2);
 }
 const f11=Math.PI/2*Math.sqrt(D/(rho*t))*(1/a**2+1/b**2);
 return {comp_m3_perPa:compliance,centre_m_perPa:wcenter,f11_hz:f11};
}
function model(inputs,tmm,Eg,rho,Vliters,support,oddMax=25){
 const w=inputs.W_mm/1000,d=inputs.D_mm/1000,h=inputs.H_mm/1000,ft=inputs.front_thickness_mm/1000,t=tmm/1000;
 const a=w-2*t,b=d-ft-t,z=h-2*t;
 const dx=[inputs.support_at_x_mm[0]/1000,inputs.support_at_x_mm[1]/1000];
 let spans=[a];
 if(support==="one_ideal_line")spans=[dx[0],a-dx[0]];
 if(support==="two_ideal_lines")spans=[dx[0],dx[1]-dx[0],a-dx[1]];
 if(spans.some(x=>x<=0)||[a,b,z].some(x=>x<=0))throw Error("Bad dimensions");
 function sumWidth(breadth,thick){
  return spans.reduce((s,L)=>s+panel(L,breadth,thick,Eg*1e9,inputs.nu,rho,oddMax).comp_m3_perPa,0);
 }
 const surfaces={
 top:sumWidth(b,t),bottom:sumWidth(b,t),
 front:sumWidth(z,ft),back:sumWidth(z,t),
 left:panel(b,z,t,Eg*1e9,inputs.nu,rho,oddMax).comp_m3_perPa,
 right:panel(b,z,t,Eg*1e9,inputs.nu,rho,oddMax).comp_m3_perPa};
 const C=Object.values(surfaces).reduce((sum,x)=>sum+x,0),air=inputs.ambient_air_density_kgm3*inputs.sound_speed_ms**2;
 const Cgas=(Vliters/1000)/air,weights=inputs.pressure_80Hz[Vliters];
 const Cweighted=Object.entries(surfaces).reduce((tot,[face,value])=>tot+value*weights[face],0);
 const values=[];
 for(const L of spans)for(const [breadth,thick] of [[b,t],[z,t],[z,ft]]){
  const x=panel(L,breadth,thick,Eg*1e9,inputs.nu,rho,oddMax);
  values.push({kind:thick===ft?"front":(breadth===b?"top/bottom":"back"),span_x_m:L,span_other_m:breadth,f11_hz:x.f11_hz,um_centre_at_1000Pa:x.centre_m_perPa*1e9});
 }
 for(const breadth of [b]){
  const side=panel(b,z,t,Eg*1e9,inputs.nu,rho,oddMax);
  values.push({kind:"side",span_x_m:b,span_other_m:z,f11_hz:side.f11_hz,um_centre_at_1000Pa:side.centre_m_perPa*1e9});
 }
 const cavityVolumeM3=a*b*z;
 const approxShellMassKg=(2*w*d*t+w*h*t+2*d*h*t+(w*h-Math.PI*(inputs.driver_hole_d_mm/2000)**2)*ft)*rho;
 return {
  thickness_mm:tmm,E_GPa:Eg,rho_kgm3:rho,target_l:Vliters,support,
  internal_clear_rect_l:cavityVolumeM3*1000,ideal_Cwall_m3_perPa:C,
  equivalent_stiffness_volume_l:C*air*1000,
  fraction_gas_compliance:C/Cgas,
  one_way_P35A_Cwall_m3_perPa:Cweighted,
  one_way_80Hz_equivalent_l:Cweighted*air*1000,
  model_gas_plus_panel_equivalent_l:Vliters+C*air*1000,
  estimated_panel_only_mass_kg:approxShellMassKg,
  model_first_local_f11_Hz:Math.min(...values.map(x=>x.f11_hz)),
  max_ideal_panel_centre_um_at_1kPa:Math.max(...values.map(x=>x.um_centre_at_1000Pa)),
  faces_compliance:surfaces
 };
}
function main(){
 const rows=[];
 for(const t of inputs.t_wall_mm)for(const E of inputs.E_GPa)
  for(const rho of inputs.rho_kgm3)for(const V of inputs.V_l)
   for(const s of inputs.supports)rows.push(model(inputs,t,E,rho,V,s));
 if(rows.length!==324)throw Error("Wrong scenario count");
 const reference=rows.filter(x=>x.thickness_mm===22&&x.E_GPa===2.1&&x.rho_kgm3===730&&x.target_l===120);
 const convergence=inputs.convergence_odd.map(n=>({n,equivalent_l:model(inputs,22,2.1,730,120,"no_braces",n).equivalent_stiffness_volume_l,with_braces:model(inputs,22,2.1,730,120,"two_ideal_lines",n).equivalent_stiffness_volume_l}));
 const out={study:"P36A",date:"2026-10-31",status:"STATIC ANALYTIC PLATE SCREENING; NOT cabinet validated FEM",
 method:"Navier SSSS Kirchhoff panel double-sine series",inputs,grid_cases:rows.length,
 convergence,reference,rows};
 const name=path.join(__dirname,"..","wyniki","p36a_podatnosc_MDF_324_20261031.json");
 fs.mkdirSync(path.dirname(name),{recursive:true});fs.writeFileSync(name,JSON.stringify(out,null,2)+"\n");
 const x=reference.find(x=>x.support==="no_braces"),y=reference.find(x=>x.support==="two_ideal_lines");
 if(Math.abs(x.equivalent_stiffness_volume_l-12.25586)>0.1||Math.abs(y.equivalent_stiffness_volume_l-3.58513)>0.1)throw Error("unit regression");
 if(convergence.some(x=>Math.abs(x.equivalent_l-convergence[convergence.length-1].equivalent_l)>.005))throw Error("series convergence");
 console.log(JSON.stringify({cases:rows.length,reference,convergence},null,2));
}
if(require.main===module)main();
module.exports={inputs,panel,model,main};
