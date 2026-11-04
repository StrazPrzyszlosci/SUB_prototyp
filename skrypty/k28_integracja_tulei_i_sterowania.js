#!/usr/bin/env node
"use strict";
// K28 integrated K27 sleeve+remote cable collision/slide regression; no structural lock and no CNC.
const fs=require("node:fs"),path=require("node:path");
function buildK28(A,B,K25,S,C){
 const assert=(x,m)=>{if(!x)throw Error(m)},r4=x=>Math.round(x*10000)/10000;
 assert(A.module_positions.length===20&&B.spines.length===12&&B.contact_lips.length===80,"K15/K17 unexpected reference count");
 assert(C.design_decision.candidate_4mm_square_remote_duct_clear_in_all_3_nominal_states,"remote K27 baseline changed");
 assert(S.axial_lock_falsification.real_joint_design_approved===false,"sleeve has unexpected release");
 const guide=S.cases.find(v=>v.rail==="G17_COLUMN_10"&&v.state==="core120"&&v.split_global_z_mm===194);
 assert(!!guide,"K27 guide10 sleeve missing");
 const walls=guide.geometry.sleeve_four_wall_cuboids_final,front=walls.find(v=>v.id==="FRONT_Y");
 assert(JSON.stringify(front.o)==="[659,205.5,169]"&&JSON.stringify(front.s)==="[21,2,50]","sleeve shape drift");
 const plate=K25.selected_guide_studies.G17_COLUMN_10.hypothetical_2mm_face_plates.find(v=>v.plate.orientation==="toward smaller Y").plate;
 const bbox=(a,b)=>a.o.map((v,k)=>Math.max(0,Math.min(v+a.s[k],b.o[k]+b.s[k])-Math.max(v,b.o[k])));
 const intersectionMm3=(a,b)=>bbox(a,b).reduce((p,x)=>p*x,1);
 const intersection=(a,b)=>intersectionMm3(a,b)>1e-7;
 const plateSleeveIntersection=walls.map(w=>({wall:w.id,intersection_mm3:r4(intersectionMm3(w,plate))}));
 assert(plateSleeveIntersection.find(v=>v.wall==="FRONT_Y").intersection_mm3===1200,"K25 plate overlap changed");
 const states={};
 for(const x of ["100","120","150"]){
  states[x]=A.module_positions.filter(m=>m.candidate_state_inclusion.includes(x)).map(m=>m.i);
 }
 function path(y,z=194){
  const p=[[231,44,z],[231,y-15,z]];
  for(let j=1;j<=32;j++){
   const theta=Math.PI-(Math.PI/2)*j/32;
   p.push([231+15+15*Math.cos(theta),y-15+15*Math.sin(theta),z]);
  }
  p.push([669.5,y,z]);
  return p;
 }
 function cableBox(a,b,width){
  return {o:a.map((v,k)=>Math.min(v,b[k])-width/2),s:a.map((v,k)=>Math.abs(v-b[k])+width)};
 }
 function collisionObstacles(state,includeSleeve=true){
  return [
   ...A.parts.filter(p=>p.module_index===-1&&!["FR1","FR2"].includes(p.id)).map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm})),
   ...B.spines.map(p=>({id:p.id,o:p.o,s:p.s})),
   ...B.contact_lips.map(p=>({id:p.id,o:p.o,s:p.s})),
   ...states[state].map(i=>({id:"BOX_"+i,o:A.module_positions[i].global_origin_xyz_mm,s:A.module_positions[i].dims_xyz_mm})),
   {id:"REAR_MAT",o:[22,353,22],s:[976,50,456]},
   ...(includeSleeve?walls:[])
  ];
 }
 function test(state,width,y){
  const pts=path(y),obstacles=collisionObstacles(state,true),errors=[];
  for(let i=0;i<pts.length-1;i++){
   const seg=cableBox(pts[i],pts[i+1],width),hits=obstacles.filter(p=>intersection(seg,p));
   if(hits.length)errors.push({segment:i,obstacles:hits.map(p=>p.id),largest_overlap_volume_mm3:r4(Math.max(...hits.map(h=>intersectionMm3(seg,h))))});
  }
  const entry=177.9-Math.hypot(width/2,Math.abs(250-194)+width/2);
  const cableEnd={o:[669.5-width/2,y-width/2,194-width/2],s:[width,width,width]};
  const segmentMaxY=y+width/2;
  return {state,outer_square_width_mm:width,lateral_end_center_y_mm:y,front_aperture_margin_mm:r4(entry),
   checked_swept_segments:pts.length-1,pass_nominal:entry>0&&errors.length===0,
   first_positive_intersections:errors.slice(0,3),
   near_sleeve_front_face_separation_of_square_envelope_mm:r4(front.o[1]-segmentMaxY),
   end_centre_to_sleeve_front_face_mm:r4(front.o[1]-y),
   final_segment_AABB_intersects_sleeve_front:intersection(cableEnd,front)};
 }
 const widths=[3,4,6,14],ys=[198,202,203,203.5,203.75,205],cases=[];
 for(const state of ["100","120","150"])for(const width of widths)for(const y of ys)cases.push(test(state,width,y));
 const get=(state,width,y)=>cases.find(c=>c.state===state&&c.outer_square_width_mm===width&&c.lateral_end_center_y_mm===y);
 assert(get("120",4,205).pass_nominal===false&&get("120",4,202).pass_nominal===true&&get("150",4,202).pass_nominal===true&&get("100",4,202).pass_nominal===false,"K28 crucial 4mm comparison changed");
 assert(get("120",3,203.75).pass_nominal===true&&get("120",4,203.75).pass_nominal===false,"K28 narrow cable comparison changed");
 assert(get("120",14,198).pass_nominal===true&&get("100",14,198).pass_nominal===false,"K28 wider service-state gap changed");
 assert(get("120",4,202).checked_swept_segments===34,"path segments changed");
 const preloadedSleeve=guide.geometry.sleeve_four_wall_cuboids_final.map(w=>({id:w.id,o:[w.o[0],w.o[1],119],s:[w.s[0],w.s[1],100]}));
 function overlapSleeveSlide(state,width,y){
  const sweepCable=path(y).slice(1).map((p,i)=>cableBox(path(y)[i],p,width));
  const errors=[];
  for(let j=0;j<sweepCable.length;j++){
   const hit=preloadedSleeve.filter(w=>intersection(sweepCable[j],w));
   if(hit.length)errors.push({segment:j,colliding_sleeve_walls:hit.map(w=>w.id)});
  }
  return {state,width_mm:width,y_mm:y,collides_during_sleeve_preload_to_bridge_stroke:errors.length>0,first_hits:errors.slice(0,2)};
 }
 const slideCompatibility=[
 overlapSleeveSlide("120",4,205),overlapSleeveSlide("120",4,202),overlapSleeveSlide("150",4,202)
 ];
 assert(slideCompatibility[0].collides_during_sleeve_preload_to_bridge_stroke===true&&!slideCompatibility[1].collides_during_sleeve_preload_to_bridge_stroke&&!slideCompatibility[2].collides_during_sleeve_preload_to_bridge_stroke,"sleeve movement/cable integration changed");
 const guide10= B.spines.find(v=>v.id==="G17_COLUMN_10");
 const result={
  study:"K28",date:"2026-11-04",
  status:"CNC HOLD — integrated K27 sleeve/cable geometry: old centered cable clashes; service-state forward-offset route nominally clears but has NO end coupling or positive lock",
  sources:["K15 20 sealed modules and fixed cabinet","K17 12 guide rails and reference tabs","K25 hypothetical guide10 2mm front face plate","K27 preloaded 21×17×50mm sleeve","K27 4mm square remote line route"],
  comparisons:{
   rail:"G17_COLUMN_10",guide_split_z_mm:194,selected_service_states:["120","150"],
   remote_bend_radius_hypothesis_mm:15,remote_bend_sample_count:32,
   lateral_cable_end_x_mm:669.5,lateral_cable_end_z_mm:194,
   tested_nominal_outer_square_widths_mm:widths,
   tested_lateral_end_center_y_mm:ys,
   sleeve_front_wall_y_span_mm:[front.o[1],front.o[1]+front.s[1]],
   old_wire_center_y_mm:205,service_route_revised_centre_y_mm:202,
   normal_facing_plate_intersection_with_closed_sleeve_mm3:plateSleeveIntersection,
   front_large_box_18_y_back_mm:202,rail10_front_face_y_mm:guide10.o[1],
   nominal_preexisting_6mm_gap_of_old_route_mm:6,
   now_occupied_sleeve_front_face_y_start_mm:205.5
  },
  complete_polyline_swept_square_tests:cases,
  cable_present_during_sleeve_Z_stroke_wall_sweeps:slideCompatibility,
  operational_interpretation:{
   original_4mm_cable_centerY205_plus_closed_sleeve_is_collision_free:false,
   full100_4mm_Y202_with_all_20_boxes_can_pass:false,
   core120_4mm_Y202_with_closed_sleeve_can_pass_nominally:true,
   single150_4mm_Y202_with_closed_sleeve_can_pass_nominally:true,
   core120_14mm_Y198_bent_envelope_can_pass_nominally:true,
   does_14mm_bent_envelope_imply_a_rigid_driver_can_turn_corner:false,
   actual_cable_termination_at_sleeve_with_4mm_width_and_Y202_is_attached:false,
   nominal_Y202_4mm_envelope_to_sleeve_face_min_edge_gap_mm:1.5,
   Y202_4mm_center_to_sleeve_face_distance_mm:3.5,
   will_a_positive_sleeve_lock_or_actuator_meet_this_geometry:"NOT TESTED",
   old_K17_guide10_integral_lip_slide_conflicts_persist:true,
   sleeve_and_K25_front_faceplate_cannot_coexist_in_unchanged_geometries:true,
   sleeve_without_axial_lock_is_rejected:true,
   positive_temporary_module_support_required:true,
   needs_measured_tol_and_actual_cross_sections:true,
   ready_for_CNC:false
  },
  limitations:["Square AABB sweeps are intentionally conservative envelopes of a hypothetical flexible line, not a real routed cable or a rigid 14mm screwdriver.",
   "No remote connector at the termination, no stroke, attachment, positive locking force, ferrule, sheath, bend limit, friction or return spring exists.",
   "Sleeve itself still cannot positively retain two MDF rails axially; original K17 integrated lower/upper lips block sleeve sliding until replaced.",
   "The 120L/150L route works only with absent front100-only boxes16–19; attaching this cable permanently across 100L state is NOT demonstrated.",
   "All three installed nominal configurations can geometrically include sleeve walls at final pose, but full100 rail10 service entry is blocked and current geometry no physical fasteners.",
   "Two full MDF front sheets are modeled only as the factory speaker hole entry; cables and connector are not included in calculated air displacement.",
   "No impact, strength, fatigue, humidity, material supplier, CNC tolerance, actual engine, assembly access or sealed housing tested."],
  next_experiment:"Choose a real positive axial rail stop/captive lock and a real flex/actuator termination at sleeve face, preserving 120L/150L tool access. Compute multi-part swept 3D and remote force/stroke, then safe temporary module support and material coupon testing. Avoid claiming a bare ring+line is a structural mechanism."
 };
 return result;
}
function main(){
 const root=path.resolve(__dirname,".."),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
 const o=buildK28(read("wyniki/k15_p30e_przed_CNC_zestawienie.json"),read("wyniki/k17_prowadnice_boczne_wkladow.json"),read("wyniki/k25_zlacza_prowadnic_i_dostep.json"),read("wyniki/k27_tuleja_przesuwna_i_trasy.json"),read("wyniki/k27_zdalne_sterowanie_przekroje.json"));
 const out=path.join(root,"wyniki/k28_integracja_tulei_linki.json");
 fs.mkdirSync(path.dirname(out),{recursive:true});
 fs.writeFileSync(out,JSON.stringify(o,null,2)+"\n");
 console.log(JSON.stringify({status:o.status,operational:o.operational_interpretation}));
}
if(require.main===module)main();
module.exports={buildK28};
