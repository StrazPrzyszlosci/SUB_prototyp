#!/usr/bin/env node
"use strict";
const fs=require("node:fs"),path=require("node:path");
function buildK27(A,B,K25){
 const check=(v,m)=>{if(!v)throw Error(m)};
 check(A.module_positions.length===20 && B.spines.length===12 && B.contact_lips.length===80,"source drift");
 const plate=K25.selected_guide_studies.G17_COLUMN_10.hypothetical_2mm_face_plates.find(p=>p.plate.orientation==="toward smaller Y").plate;
 check(JSON.stringify(plate.o)==="[661.5,206,169]"&&JSON.stringify(plate.s)==="[16,2,50]","K25 plate changed");
 const states={};
 for(const k of ["100","120","150"])states[k]=A.module_positions.filter(m=>m.candidate_state_inclusion.includes(k)).map(m=>m.i);
 check(states["100"].length===20&&states["120"].length===12&&states["150"].length===1,"state drift");
 function obs(k,addPlate){
  return [
   ...A.parts.filter(p=>p.module_index===-1&&p.id!=="FR1"&&p.id!=="FR2").map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm})),
   ...B.spines.map(p=>({id:p.id,o:p.o,s:p.s})),
   ...B.contact_lips.map(p=>({id:p.id,o:p.o,s:p.s})),
   ...A.module_positions.filter(m=>states[k].includes(m.i)).map(m=>({id:"BOX_"+m.i,o:m.global_origin_xyz_mm,s:m.dims_xyz_mm})),
   {id:"MAT",o:[22,353,22],s:[976,50,456]},
   ...(addPlate?[plate]:[])
  ]
 }
 const overlap=(a,b)=>a.o.reduce((s,v,i)=>s*Math.max(0,Math.min(v+a.s[i],b.o[i]+b.s[i])-Math.max(v,b.o[i])),1);
 function path(z){
  const R=15,segments=32,p=[[231,44,z],[231,205-R,z]];
  for(let j=1;j<=segments;j++){
   const th=Math.PI-(Math.PI/2)*j/segments;
   p.push([231+R+R*Math.cos(th),205-R+R*Math.sin(th),z]);
  }
  p.push([669.5,205,z]);
  return p;
 }
 function trial(k,size,addPlate=false,z=194){
  const obstacles=obs(k,addPlate),p=path(z),failed=[];
  for(let i=0;i<p.length-1;i++){
   const half=size/2,a=p[i],b=p[i+1];
   const sweep={o:a.map((v,j)=>Math.min(v,b[j])-half),s:a.map((v,j)=>Math.abs(v-b[j])+size)};
   const intersects=obstacles.filter(o=>overlap(sweep,o)>1e-7);
   if(intersects.length)failed.push({segment:i,obstacles:intersects.map(o=>o.id)});
  }
  const entryMargin=A.cfg.cutout_factory_reference_d_mm/2-Math.hypot(size/2,Math.abs(250-z)+size/2);
  return {state:k,outer_mm:size,plate_present:addPlate,z_mm:z,
   checked_full_segment_sweeps:p.length-1,entry_margin_mm:+entryMargin.toFixed(6),
   positive_overlap_segment_count:failed.length,first_hits:failed.slice(0,3),
   nominal_pass:entryMargin>0&&failed.length===0,
   gap_Y202_to208_mm:6,residual_width_at_center_Y205_mm:6-size};
 }
 const cases=[],plates=[];
 for(const state of ["100","120","150"]){
  for(const outer of [4,5,6,7,14])cases.push(trial(state,outer));
  plates.push(trial(state,4,true));
 }
 const compare=cases.filter(x=>x.state==="120").map(x=>({outer:x.outer_mm,passes:x.nominal_pass,first_hit:x.first_hits[0]?.obstacles||[]}));
 check(compare.map(x=>x.passes).join(",")==="true,true,true,false,false","width regression");
 check(cases.filter(x=>x.outer_mm===4).every(x=>x.nominal_pass),"4mm blocked");
 check(plates.find(x=>x.state==="120").positive_overlap_segment_count>0,"K25 plate should obstruct centered envelope");
 check(K25.selected_guide_studies.G17_COLUMN_10.straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model===false,"K25 access regression");
 const totalMass=4*(0.602408+0.2);
 const data={
  study:"K27",date:"2026-11-04",status:"CNC HOLD — flexible actuation cable corridor only, NO structural remote latch",
  source:"K15 cabinet/boxes, all K17 guide rails and all 80 original lips, K25 hypothetical Z194 front faceplate",
  modeled_route:{start_global_xyz_mm:[231,44,194],bend_start_global_xyz_mm:[231,190,194],
   bend_end_global_xyz_mm:[246,205,194],termination_global_xyz_mm:[669.5,205,194],
   distance_from_termination_to_guide10_front_Y_face_mm:3,
   bend_radius_hypothesis_mm:15,bend_chord_count:32,
   maximum_bend_sagitta_mm:+(15*(1-Math.cos(Math.PI/128))).toFixed(7),
   square_AABB_outer_envelope_continuously_swept_over_each_polyline_segment:true,
   front_baffle_mode:"both MDF front panels replaced with nominal Ø355.8 centred speaker hole; driver removed",
   cable_flexibility_or_bend_manufacturer_verified:false,
   real_connector_or_latch_implemented:false},
  states,
  outer_envelope_screen:cases,
  with_K25_trial_faceplate_screen:plates,
  core120_width_comparison:compare,
  corridor:{front_large_box_back_global_Y_mm:202,guide10_front_face_global_Y_mm:208,
   gap_mm:6,nominal_pass_envelope_mm:4,
   example_hypothetical_cable_OD_mm:2,example_clearance_each_side_mm:1,
   nominal_free_margin_per_side_at_outer4_mm:1,
   when_faces_each_encroach_hypothetical_0_5mm_gap_mm:5,
   remaining_margin_each_side_for_outer4_mm:0.5,
   when_faces_each_encroach_hypothetical_1mm_gap_mm:4,
   remaining_margin_each_side_for_outer4_mm:0,
   K25_plate_projection_Y_global_mm:[206,208],plate_depth_mm:2,
   gap_minus_plate_minus_outer4_mm:0,
   measured_material_or_cable_tolerances:false},
  bending_load_assumptions:{density_kg_m3:730,extra_assumed_hardware_per_large_box_kg:0.2,acceleration_g:5,
   assumed_number_large_rear_boxes:4,combined_assumed_mass_kg:+totalMass.toFixed(6),
   combined_hypothetical_inertial_force_N:+(totalMass*9.81*5).toFixed(5),
   positive_temporary_support_mandatory:true,link_not_structural:true,
   measured_MDF_strength_or_fatigue_allowables_present:false},
  design_decision:{
   candidate_4mm_square_remote_duct_clear_in_all_3_nominal_states:true,
   conventional_K25_front_faceplate_collides_with_centered_4mm_duct:true,
   direct_K25_14mm_driver_blocked:true,
   rigid_torque_driver_cannot_follow_bent_remote_cable_route:true,
   positive_mechanical_latch_and_connector_missing:true,
   true_cable_end_capture_and_bend_force_stroke_unverified:true,
   release_to_CNC:false},
  next_engineering_goals:[
   "Define separately load-rated positive internal guide10 latch with spring/captive fail-safe stop, and its cable-side coupling, avoiding six-millimetre slit intrusion.",
   "Design temporary independent load-bearing supports for modules 12–15 while guide10 is removed; do not let actuator cable bear load.",
   "Model true metal latch and cable sheath solids, connector reach, real supplier bend radii and force losses in K24/K26 100↔120↔150 chronological service.",
   "Measure material and tool tolerances; verify fatigue, MDF pull-out, screw edge distances, acoustics and enclosure leakage; then regenerate production CNC with independent QA."]
 };
 return data;
}
function main(){
const root=path.resolve(__dirname,"..");const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
const d=buildK27(load("wyniki/k15_p30e_przed_CNC_zestawienie.json"),load("wyniki/k17_prowadnice_boczne_wkladow.json"),load("wyniki/k25_zlacza_prowadnic_i_dostep.json"));
const out=path.join(root,"wyniki/k27_zdalne_sterowanie_przekroje.json");fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(d,null,2)+"\n");
console.log(JSON.stringify({status:d.status,core120:d.core120_width_comparison,plate120:d.with_K25_trial_faceplate_screen.find(v=>v.state==="120").nominal_pass,cnc:d.design_decision.release_to_CNC}));
}
if(require.main===module)main();module.exports={buildK27};
