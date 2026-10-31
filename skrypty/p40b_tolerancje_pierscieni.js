#!/usr/bin/env node
"use strict"; // P40B: tolerance and circular backer geometry screening (NOT CNC/strength)
const fs=require('node:fs'),path=require('node:path');
const cfg={"date":"2026-11-01","cutout_D_mm":355.8,"bolt_PCD_mm":368,"ring_hole_D_mm":6.5,"front_hole_D_mm":6.5,"driver_center_x_mm":231,"driver_center_z_mm":250,"wall_thickness_mm":22,"first_brace_outer_x_mm":448,"ring_OD_mm":[392,400,408],"ring_ID_mm":[356,358,360],"offset_xz_mm":[-1.5,-0.75,0,0.75,1.5],"bolt_shank_D_mm":[4,5,6],"target_clearances_mm":[{"name":"visual_only","gap":0,"web":0},{"name":"research_1plus1","gap":1,"web":1},{"name":"research_1plus2","gap":1,"web":2}],"notes":["The research-only 1mm opening + 2mm remaining metal ligament thresholds are NOT formal safety standards","A radial intersection of two bolt-hole circles models ideal geometric shank assembly, not threading/tolerance of true fastener."]};
function scan(c){
 const arr=[];const R=c.bolt_PCD_mm/2,rHole=c.ring_hole_D_mm/2,rCut=c.cutout_D_mm/2;
 for(const OD of c.ring_OD_mm)for(const ID of c.ring_ID_mm)for(const dx of c.offset_xz_mm)for(const dz of c.offset_xz_mm)for(const D of c.bolt_shank_D_mm){
   const offset=Math.hypot(dx,dz);
   const innerGap=ID/2-rCut-offset;
   const metalWeb=R-rHole-ID/2;
   const flangeOuterLand=OD/2-(R+rHole);
   const sideGap=c.driver_center_x_mm+dx-OD/2-c.wall_thickness_mm;
   const braceGap=c.first_brace_outer_x_mm-(c.driver_center_x_mm+dx+OD/2);
   // With two equally sized 6.5mm through holes, a shank diameter D can fit if their
   // effective shank-center disks (radius Rhole-D/2) overlap.
   const maxMisalignment=(c.ring_hole_D_mm-D)/2+(c.front_hole_D_mm-D)/2;
   const alignmentOK=offset<=maxMisalignment+1e-12;
   const staticOK=innerGap>=0&&metalWeb>=0&&flangeOuterLand>=0&&sideGap>=0&&braceGap>=0;
   const pass=staticOK&&alignmentOK;
   arr.push({OD_mm:OD,ID_mm:ID,offset_x_mm:dx,offset_z_mm:dz,offset_norm_mm:+offset.toFixed(5),
    shank_D_mm:D,opening_clearance_mm:+innerGap.toFixed(4),metal_web_mm:+metalWeb.toFixed(4),
    flange_outer_land_mm:+flangeOuterLand.toFixed(4),inner_side_gap_mm:+sideGap.toFixed(4),
    first_brace_x_projection_gap_mm:+braceGap.toFixed(4),
    alignment_slack_mm:+(maxMisalignment-offset).toFixed(4),geometry_may_fit:pass,
    research_1plus1:pass&&innerGap>=1&&metalWeb>=1,
    research_1plus2:pass&&innerGap>=1&&metalWeb>=2
   });
 }
 const stats={cases:arr.length,basic_geometric:arr.filter(q=>q.geometry_may_fit).length,
  target_1_plus_1:arr.filter(q=>q.research_1plus1).length,
  target_1_plus_2:arr.filter(q=>q.research_1plus2).length,
  min_gap_any_pass:Math.min(...arr.filter(q=>q.geometry_may_fit).map(q=>q.opening_clearance_mm)),
  max_nominal_metal_web:Math.max(...arr.filter(q=>q.offset_x_mm===0&&q.offset_z_mm===0).map(q=>q.metal_web_mm)),
  radial_budget_mm:R-rHole-rCut,
  nominal_target_infeasibility_margin_mm:(R-rHole-rCut)-(1+2),
  shank6_supported:arr.filter(q=>q.shank_D_mm===6&&q.geometry_may_fit).length
 };
 const selected=arr.filter(q=>q.OD_mm===400&&q.ID_mm===358&&q.shank_D_mm===5);
 return {study:"P40B",date:"2026-11-01",status:"2D robust parametric geometry and tolerance budget, not fastener verification",
   inputs:c,statistics:stats,reference_ID358_screw5:selected,results:arr,
   warnings:["Research thresholds 1mm/1mm and 1mm/2mm are arbitrary screens, NOT verified allowable strength or mounting specifications.",
    "OD clearance to braces is one dimensional and does NOT prove 3D basket assembly or tool access.",
    "Hole clocking is assumed, shank diameter is a mathematical passability parameter not a recommended screw size.",
    "No MDF tensile/splitting properties, no ring yielding, no preload, backlash, gasket compression, vibration fatigue or safety factors."]};
}
function main(){
 const x=scan(cfg);
 if(x.statistics.cases!==675)throw Error('case count');
 if(Math.abs(x.statistics.radial_budget_mm-2.85)>1e-8)throw Error('Radial ligament budget');
 if(x.statistics.target_1_plus_2!==0)throw Error('Analytical incompatible 1+2mm margin should be zero');
 const file=path.join(__dirname,'..','wyniki','p40b_tolerancje_675_20261101.json');
 fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(x,null,2)+'\n');
 console.log(JSON.stringify(x.statistics,null,2));
}
if(require.main===module)main();module.exports={cfg,scan,main};
