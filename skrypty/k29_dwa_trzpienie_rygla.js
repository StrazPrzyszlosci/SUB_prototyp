#!/usr/bin/env node
"use strict";
// K29 numerical screens for cross-pin geometry only. No real fastener or material qualification.
const fs=require("node:fs"),path=require("node:path");
function buildK29(k15,k17,k25,k28) {
 const invariant=(test,msg)=>{if(!test)throw Error(msg)};
 const round=x=>+x.toFixed(6);
 const volume=(a,b)=>a.o.reduce((p,v,i)=>p*Math.max(0,Math.min(v+a.s[i],b.o[i]+b.s[i])-Math.max(v,b.o[i])),1);
 const box=(id,o,s)=>({id,o,s});
 const fixed=k15.parts.filter(p=>p.module_index===-1&&!["FR1","FR2"].includes(p.id)).map(p=>box(p.id,p.local_origin_global_xyz_mm,p.box_size_xyz_mm));
 const mat=box("50mm rear mat",[22,353,22],[976,50,456]);
 const states={full100:k15.module_positions.map(x=>x.i),core120:k15.module_positions.filter(x=>x.candidate_state_inclusion.includes("120")).map(x=>x.i),single150:[4]};
 invariant(k15.parts.length===138&&k17.spines.length===12&&k28.comparisons.service_route_revised_centre_y_mm===202,"upstream reference drift");
 const variants=[];
 for(const [railId,split,state] of [
  ["G17_COLUMN_02",250,"full100"],["G17_COLUMN_02",250,"core120"],
  ["G17_COLUMN_10",194,"core120"],["G17_COLUMN_10",194,"single150"],
  ["G17_COLUMN_10",194,"full100"]]) {
  const rail=k17.spines.find(x=>x.id===railId),x=rail.o[0]+rail.s[0]/2;
  const y0=rail.o[1]-2.5,y1=rail.o[1]+rail.s[1]+2.5;
  const env=[...fixed,mat,...k17.spines.filter(x=>x.id!==railId).map(x=>box(x.id,x.o,x.s)),
    ...states[state].map(i=>box("MODULE_"+i,k15.module_positions[i].global_origin_xyz_mm,k15.module_positions[i].dims_xyz_mm))];
  const check=p=>env.filter(t=>volume(p,t)>1e-7).map(t=>t.id);
  const sleeveFrontWall=box("FRONT sleeve wall",[rail.o[0]-2.5,y0,split-25],[rail.s[0]+5,2,50]);
  const sleeveBackWall=box("REAR sleeve wall",[rail.o[0]-2.5,y1-2,split-25],[rail.s[0]+5,2,50]);
  const sleeveSlideFront=box("FRONT sleeve wall swept",[rail.o[0]-2.5,y0,split-75],[rail.s[0]+5,2,100]);
  const sleeveSlideBack=box("REAR sleeve wall swept",[rail.o[0]-2.5,y1-2,split-75],[rail.s[0]+5,2,100]);
  const pins=[{half:"lower",z:split-12.5},{half:"upper",z:split+12.5}].map(p=>{
   const d=3,hz=p.z;
   const shank=box("pin",[x-d/2,y0,hz-d/2],[d,y1-y0,d]);
   const rear4=box("rearhead4",[x-2.5,y1,hz-2.5],[5,4,5]);
   const rear5=box("rearhead5",[x-2.5,y1,hz-2.5],[5,5,5]);
   const front4=box("fronthead4",[x-2.5,y0-4,hz-2.5],[5,4,5]);
   const tool=box("tool14",[x-7,44,hz-7],[14,y0-44,14]);
   const toolCircle=Math.hypot(x-231,hz-250)+7;
   const slideIntersections=[
    {wall:sleeveSlideFront.id,overlap_mm3:round(volume(shank,sleeveSlideFront))},
    {wall:sleeveSlideBack.id,overlap_mm3:round(volume(shank,sleeveSlideBack))}
   ];
   return {half:p.half,drilled_centre_global_xyz_mm:[x,(y0+y1)/2,hz],
    trial_pin_d_mm:d,axis:"Y",pin_envelope:shank,
    scene_pin_body_collisions:check(shank),
    rear_cap_4mm_scene_hits:check(rear4),
    rear_cap_5mm_scene_hits:check(rear5),
    front_cap_4mm_scene_hits:check(front4),
    rear_cap_4mm_nominal_gap_to_box14_mm:railId==="G17_COLUMN_10"&&state!=="single150"?round(227-(y1+4)):null,
    direct_Y_tool:{hypothetical_diameter_mm:14,reference_opening_radius_mm:177.9,
       aperture_farthest_radius_mm:round(toolCircle),front_aperture_projection_clear:toolCircle<=177.9,
       remaining_scene_collisions:check(tool),available:toolCircle<=177.9&&check(tool).length===0},
    pin_placed_before_sleeve_axial_stroke_blocks_wall:slideIntersections.some(q=>q.overlap_mm3>0),
    pin_vs_sleeve_swept_wall_overlap_mm3:slideIntersections};
  });
  const holeTrials=[{pin_d_mm:3,hole_d_mm:3.3},{pin_d_mm:4,hole_d_mm:4.5}].flatMap(t=>["Y","X"].map(axis=>{
   // Axis Y: drill enters depth, only X and Z are in-plane edge distances.
   // Axis X: drill enters width, only Y and Z are in-plane edge distances.
   const transverse=axis==="Y"?rail.s[0]/2:rail.s[1]/2;
   const axial=12.5;
   return {...t,axis,transverse_centre_to_edge_mm:transverse,
    axial_split_end_centre_distance_mm:axial,
    min_transverse_centre_edge_over_hole_d:round(transverse/t.hole_d_mm),
    min_axial_end_centre_distance_over_hole_d:round(axial/t.hole_d_mm),
    assumed_geometry_threshold_transverse_d:2,assumed_geometry_threshold_axial_d:3,
    screening_pass:transverse>=2*t.hole_d_mm&&axial>=3*t.hole_d_mm,
    criterion_is_illustrative_not_an_MDF_material_standard:true};
  }));
  const example=k25.one_remaining_support_5g_hypothetical_demand_with_0_2kg_allowance.find(d=>d.rail===railId);
  const totalLoad=example.assumed_inertial_load_5g_on_one_surviving_side_N*rail.module_indices.length;
  const d=3;
  const load={affected_modules:rail.module_indices,total_hypothetical_if_all_5g_transmitted_N:round(totalLoad),
   double_shear_pin_area_mm2:round(2*Math.PI*d*d/4),
   hypothetical_nominal_pin_double_shear_stress_MPa:round(totalLoad/(2*Math.PI*d*d/4)),
   sleeve_two_wall_bearing_projected_area_mm2:2*2*d,
   sleeve_hypothetical_bearing_indicator_MPa:round(totalLoad/(2*2*d)),
   rail_depth_bearing_projected_area_mm2:rail.s[1]*d,
   rail_hypothetical_bearing_indicator_MPa:round(totalLoad/(rail.s[1]*d)),
   load_orientation_actual_force_partition_and_strength_allowables_unverified:true};
  variants.push({rail:railId,service_state:state,split_z_mm:split,
    sleeve_unqualified_reference:{outer_x_mm:21,outer_y_mm:17,height_z_mm:50,front_y_mm:y0,rear_y_mm:y1,
       front_sleeve_wall:sleeveFrontWall,back_sleeve_wall:sleeveBackWall},
    pin_centres_and_approach:pins,
    nominal_hole_geometry_screens:holeTrials,
    hypothetical_full_5g_group_load_if_one_joint_transmits_all:load,
    pins_installable_in_actual_working_cabinet_with_reachable_tool:false,
    first_and_second_pin_retraction_controlled_by_single_remote_actuator:false});
 }
 const r02=variants[0],r10=variants[2],r10full=variants[4];
 invariant(r02.pin_centres_and_approach.every(q=>q.direct_Y_tool.available),"guide02 tool screen drift");
 invariant(r10.pin_centres_and_approach.every(q=>!q.direct_Y_tool.available),"guide10 tool screen drift");
 invariant(r10.pin_centres_and_approach.every(q=>q.rear_cap_5mm_scene_hits.includes("MODULE_14")),"guide10 head near rear box drift");
 invariant(r10full.pin_centres_and_approach.every(q=>q.front_cap_4mm_scene_hits.includes("MODULE_18")),"100L front head clash drift");
 invariant(r10.pin_centres_and_approach.every(q=>q.pin_placed_before_sleeve_axial_stroke_blocks_wall),"Preloaded pins must block sleeve");
 invariant(r10.nominal_hole_geometry_screens.filter(q=>q.screening_pass).length===1,"edge-rule screen changed");
 const ySleeve=k28.comparisons.sleeve_front_wall_y_span_mm[0];
 return {study:"K29",date:"2026-11-05",status:"CNC HOLD — 2-pin dual-half positive retention concept geometry only; NO qualified mechanical joint, guide10 remote retraction remains unsolved",
  sources:["K15 cabinet and K15 boxes","K17 rail geometry","K25 reference tool and hypothetical 5g load","K28 integrated sliding sleeve + revised Y202 remote line"],
  nominal_research_not_hardware:{split_pin_offset_below_and_above_mm:12.5,
   guide_wood_cross_section_x_y_mm:[16,12],illustrative_sleeve_outer_cross_section_mm:[21,17],
   sleeve_length_mm:50,guide10_y202_cable_square_outer_mm:4,trial_pin_nominal_d_mm:3,
   hole_size_screen_mm:[3.3,4.5],rear_head_protrusion_screens_mm:[4,5],
   hypothetical_geometry_rule_centre_to_transverse_edge_over_hole_d:2,
   hypothetical_geometry_rule_centre_to_split_end_over_hole_d:3,
   no_supplier_hardware_fastener_or_qualified_MDF_spec_selected:true},
  five_state_pin_and_tool_screens:variants,
  guide10_remote_cable_endpoint:{
    cable_outer_y_span_mm:[200,204],sleeve_front_wall_y_start_mm:ySleeve,
    nominal_unconnected_gap_y_mm:round(ySleeve-204),
    sleeve_axial_stroke_z_mm:50,guide10_two_separate_positive_pin_retaining_points_z_mm:[181.5,206.5],
    remote_cable_end_has_no_retracting_fork_cam_or_captive_head:true,
    no_50mm_follower_slack_or_bowden_design_verified:true},
  failure_and_release_decision:{
    two_pins_could_prevent_sleeve_sliding_off_if_both_physically_engaged:true,
    each_pin_must_be_added_after_sleeve_reaches_final_bridge_position:true,
    guide02_straight_Y_reference_tool_both_points_nominally_accessible:true,
    guide10_straight_Y_reference_tool_both_points_inaccessible:true,
    guide10_5mm_rear_cap_intersects_box14_in_core120:true,
    guide10_4mm_rear_cap_leaves_only_0_5mm_gap_in_core120:true,
    guide10_full100_front_4mm_cap_intersects_box18:true,
    trial_3_3mm_Y_hole_passes_only_the_stated_illustrative_edge_rule:true,
    trial_4_5mm_hole_fails_that_edge_rule:true,
    guide10_two_postinstalled_releasable_pins_mechanically_approved:false,
    all_pin_material_bearing_shear_pullout_fatigue_creep_tolerances_unqualified:true,
    independent_support_for_four_large_modules_during_guide10_release_missing:true,
    complete_operational_volume_switch_with_real_joints_proven:false,
    release_CNC:false},
  next_actions:["Create a fully finite two-detent spring latch and mechanical release fork design OR abandon rail10 front pin retrofit in favor of a reinforced sealed service cassette.",
    "Prove two positive locks can retract without ever relying on the thin cable for module support; model 50mm sleeve translation and a controlled flexible endpoint.",
    "Specify/measure actual metal rail connector, MDF anchoring, backup supports, exact tool access, gasket and load paths; coupons must cover 5g sensitivity, bearing and vibration.",
    "Recheck all K24/K26 routes at positive realistic clearances before creating a replacement CNC DXF with tabs, kerf, inside radii and declared hole sizes."]};
}
function main(){
 const root=path.resolve(__dirname,"..");
 const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
 const data=buildK29(read("wyniki/k15_p30e_przed_CNC_zestawienie.json"),read("wyniki/k17_prowadnice_boczne_wkladow.json"),read("wyniki/k25_zlacza_prowadnic_i_dostep.json"),read("wyniki/k28_integracja_tulei_linki.json"));
 const dest=path.join(root,"wyniki/k29_rygle_poprzeczne_dostep.json");
 fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,JSON.stringify(data,null,2)+"\n","utf8");
 console.log(JSON.stringify({status:data.status,tested:data.five_state_pin_and_tool_screens.length,CNC:data.failure_and_release_decision.release_CNC}));
}
if(require.main===module)main();
module.exports={buildK29};
