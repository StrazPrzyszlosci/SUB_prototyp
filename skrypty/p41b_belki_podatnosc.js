#!/usr/bin/env node
"use strict"; // P41B: simply supported beam upper-bound and carrier/brace anchor k in series. NOT CAD / CNC.
const fs=require("node:fs"),path=require("node:path");
const p41=require("./p41a_carrier_vs_szyny.js");
const bcfg={
  "date": "2026-11-01",
  "model": "Simply-supported beam Euler-Bernoulli point load at midspan (upper bound stiffness for non-ideal joints)",
  "beam_length_mm": [
    300,
    380,
    440
  ],
  "section_yd_mm_z_h_mm": [
    [
      20,
      3
    ],
    [
      25,
      4
    ],
    [
      30,
      6
    ]
  ],
  "E_GPa": [
    70,
    200
  ],
  "test_force_N": [
    100,
    200,
    400
  ],
  "g0": 9.80665,
  "notes": [
    "Beam normal deflection in y, longitudinal axis x; rectangle breadth h in z × depth d in y, I_z=h*d^3/12.",
    "No plate torsion, flange contact, real beam end conditions, cross-bracing, local instability or manufacturer mechanical characterization.",
    "7/200 GPa Young moduli are generic exploratory materials not sourced as specific purchased alloys.",
    "Ideal pin-pins, center loading, no nonlinearities; stress is elastic cross-section extreme fiber, not strength margin."
  ]
};
function beamCalc(c,d,h,L,Eg,F){
 const E=Eg*1000,I=h*d**3/12,rigidity=48*E*I/L**3,delta=F/rigidity,M=F*L/4;
 return {section_d_y_mm:d,section_h_z_mm:h,span_mm:L,E_GPa:Eg,center_force_N:F,I_z_mm4:+I.toFixed(5),
  k_beam_N_per_mm:+rigidity.toFixed(5),central_deflection_mm:+delta.toFixed(6),peak_elastic_bending_stress_MPa:+(M*(d/2)/I).toFixed(4),
  beam_mass_per_span_kg_per_rho2700:+(d*h*L*2700/1e9).toFixed(6),beam_mass_per_span_kg_per_rho7850:+(d*h*L*7850/1e9).toFixed(6)};
}
function run(){
 const beams=[];
 for(const [d,h] of bcfg.section_yd_mm_z_h_mm)for(const L of bcfg.beam_length_mm)for(const E of bcfg.E_GPa)
 for(const F of bcfg.test_force_N)beams.push(beamCalc(bcfg,d,h,L,E,F));
 const coupled=[];
 for(const [d,h] of bcfg.section_yd_mm_z_h_mm)for(const L of bcfg.beam_length_mm)for(const E of bcfg.E_GPa){
  const rail=beamCalc(bcfg,d,h,L,E,100),k0=300,k_brace=900;
  const eff=1/(1/k_brace+1/rail.k_beam_N_per_mm),factor=eff/k0;
  for(const dir of ['x','y','z']){
   const A=p41.model(p41.cfg,'A_carrier',15,5,120,dir,300,3,false);
   const Bideal=p41.model(p41.cfg,'B_brace_rails',15,5,120,dir,300,3,false);
   const B=p41.model(p41.cfg,'B_brace_rails',15,5,120,dir,300,factor,false);
   coupled.push({profile:d+'x'+h,span_mm:L,E_GPa:E,d_mm:d,h_mm:h,direction:dir,
    rail_stiffness_N_per_mm:rail.k_beam_N_per_mm,series_support_stiffness_N_per_mm:+eff.toFixed(4),
    max_reaction_A_N:A.max_resultant_N,max_reaction_B_rigid_N:Bideal.max_resultant_N,max_reaction_B_with_beam_N:B.max_resultant_N,
    max_normal_disp_A_mm:A.max_abs_normal_anchor_displacement_mm,
    max_normal_disp_B_rigid_mm:Bideal.max_abs_normal_anchor_displacement_mm,max_normal_disp_B_with_beam_mm:B.max_abs_normal_anchor_displacement_mm});
  }
 }
 if(beams.length!==54||coupled.length!==54)throw Error('P41B count');
 const ref=beams.find(q=>q.section_d_y_mm===25&&q.section_h_z_mm===4&&q.span_mm===380&&q.E_GPa===70&&q.center_force_N===200);
 const exact=200*380**3/(48*(70*1000)*(4*25**3/12));
 if(Math.abs(ref.central_deflection_mm-exact)>1e-5)throw Error('Analytical bending regression');
 const doc={study:'P41B',date:'2026-11-01',status:'54 beam benchmarks and 54 coupled surrogate cases; NOT validated strength',
 inputs:bcfg,beam_cases:beams.length,coupled_cases:coupled.length,beams,coupled,
 warnings:["Beam end idealizations and circular cage geometry unknown; end moment and torsional stiffness not represented.","Beam and anchor reactions in P41A assume rigid distributed carrier and bilateral normal springs; adding scalar spring compliance is screening only, NOT structural 3D FEM.","Elastic stress does not imply pass/fail without yield and safety limits from actual chosen material.","No acceptable bending, stress, deflection, sound seal or fatigue threshold has been measured."]};
 const dest=path.join(__dirname,'..','wyniki','p41b_podatnosc_belek_108_20261101.json');
 fs.writeFileSync(dest,JSON.stringify(doc,null,2)+'\n');
 console.log(JSON.stringify({cases:beams.length,coupled:coupled.length,reference:ref},null,2));
}
if(require.main===module)run();module.exports={bcfg,beamCalc,run};