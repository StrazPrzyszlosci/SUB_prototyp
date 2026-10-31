#!/usr/bin/env node
"use strict";
// P38B coordinate frame sensitivity vs original P34B: in ext case X231 Z250 => local X209 Z228.
const fs=require('node:fs'),path=require('node:path'),p34=require('./p34b_przestrzenne_pole_p30e.js');
function run(){
 const old=p34.cfg,updated=JSON.parse(JSON.stringify(old));
 updated.source_xz_mm=[old.source_xz_mm[0]-22,old.source_xz_mm[1]-22];
 const geom=p34.geometry(old),results=[];
 for(const state of ['100','120','150'])for(const frequency_Hz of [20,40,60,80])
  for(const mesh_mm of (frequency_Hz===80?[55,36]:[55])){
   const a=p34.simulate(old,geom,state,mesh_mm,frequency_Hz),z=p34.simulate(updated,geom,state,mesh_mm,frequency_Hz);
   results.push({state,frequency_Hz,mesh_mm,legacy_local_center_mm:old.source_xz_mm,
    correct_local_center_mm:updated.source_xz_mm,legacy_volume_l:a.volume_l,corrected_volume_l:z.volume_l,
    legacy_rms_percent:a.rms_nonuniformity_pct,corrected_rms_percent:z.rms_nonuniformity_pct,
    change_pp:z.rms_nonuniformity_pct-a.rms_nonuniformity_pct,
    legacy_source_pmean_ratio:a.source_pressure_relative_to_mean,corrected_source_pmean_ratio:z.source_pressure_relative_to_mean});
  }
 if(results.length!==15)throw Error('Case count');
 const t=results.find(x=>x.state==='120'&&x.frequency_Hz===80&&x.mesh_mm===55);
 if(!t||Math.abs(t.legacy_rms_percent-19.0882768)>.05||Math.abs(t.corrected_rms_percent-21.0259762)>.05)throw Error('Coordinate regression');
 const out={study:'P38B',date:'2026-11-01',status:'coordinate consistency sensitivity study, not physical validation',cases:results.length,
  definition:{outside_center_xz_mm:[231,250],wall_mm:22,correct_inside_center_mm:[209,228],braces_outside_x_mm:[448,723],braces_inside_x_mm:[426,701]},
  results,warnings:["P34B and P35A original source position 231/250 was used as local although P31C defines these as external coordinates; do not interpret old values as a validated corrected CAD model.","Correction shifts hypothetical basket and source x/z by -22mm; rigid modules remain unchanged.","FV walls rigid, foam loss omitted, basket approximated as a 5 L cylinder, not a real Dayton basket CAD.","Historic result JSON is intentionally retained; new results must declare coordinate frame."]};
 const file=path.join(__dirname,'..','wyniki','p38b_koordynaty_FV_15_20261101.json');
 fs.writeFileSync(file,JSON.stringify(out,null,2)+'\n');
 console.log('P38B cases',results.length,'120l 80Hz original=',t.legacy_rms_percent,' corrected=',t.corrected_rms_percent);
 return out;
}
if(require.main===module)run();
module.exports={run};
