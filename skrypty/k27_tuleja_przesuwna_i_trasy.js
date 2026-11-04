#!/usr/bin/env node
"use strict";
// K27 research only: preloaded hollow guide collar, conservative assembly path and lip-intersection veto.
const fs=require("node:fs"),path=require("node:path");
function buildK27(A,B,C,D){
 const assert=(ok,message)=>{if(!ok)throw Error(message)};
 const three=v=>Math.round(v*1000)/1000;
 const positiveOverlap=(a,b)=>a.o.every((v,k)=>Math.min(v+a.s[k],b.o[k]+b.s[k])-Math.max(v,b.o[k])>1e-7);
 const collisions=(parts,other)=>[...new Set(parts.flatMap(x=>other.filter(y=>positiveOverlap(x,y)).map(y=>y.id)))].sort();
 assert(A.module_positions.length===20&&B.spines.length===12&&A.parts.length===138,"K15/K17 input geometry changed");
 assert(D.operational_conclusion.can_remove_and_reinstall_rail10_half_shapes_at_core120===true,"K26 baseline changed");
 const fixed=A.parts.filter(p=>p.module_index===-1&&!["FR1","FR2"].includes(p.id)).map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm}));
 const mat={id:"MAT50",o:[22,353,22],s:[976,50,456]};
 const states={
  full100:A.module_positions.map(v=>v.i),
  core120:A.module_positions.filter(v=>v.candidate_state_inclusion.includes("120")).map(v=>v.i),
  single150:[4]
 };
 function railBy(id){const r=B.spines.find(v=>v.id===id);assert(!!r,"Unknown selected K17 spine "+id);return r;}
 function environment(id,state){
  return [...fixed,mat,...B.spines.filter(v=>v.id!==id).map(v=>({id:v.id,o:v.o,s:v.s})),
    ...states[state].map(i=>({id:"MODULE_"+i,o:A.module_positions[i].global_origin_xyz_mm,s:A.module_positions[i].dims_xyz_mm}))];
 }
 function sleeveAt(rail,z){
  const x=rail.o[0],y=rail.o[1],w=rail.s[0],d=rail.s[1];
  return [
   {id:"FRONT_Y",o:[x-2.5,y-2.5,z],s:[w+5,2,50]},
   {id:"BACK_Y",o:[x-2.5,y+d+0.5,z],s:[w+5,2,50]},
   {id:"LEFT_X",o:[x-2.5,y-0.5,z],s:[2,d+1,50]},
   {id:"RIGHT_X",o:[x+w+0.5,y-0.5,z],s:[2,d+1,50]}
  ];
 }
 function criticalPlaneRoute(part,scene){
  const half=part.s.map(v=>v/2),rect=[[22+half[0],998-half[0]],[44+half[1],403-half[1]],[22+half[2],478-half[2]]];
  const source=[231,44+half[1],250],target=part.o.map((v,i)=>v+half[i]);
  const radial=177.9-Math.hypot(half[0],half[2]);
  if(radial<=0)return {passed:false,reason:"outside nominal circular front opening"};
  const lo=scene.map(o=>o.o.map((v,k)=>v-half[k]));
  const hi=scene.map(o=>o.o.map((v,k)=>v+o.s[k]+half[k]));
  const axes=[0,1,2].map(k=>{
    const raw=[...rect[k],source[k],target[k],...lo.map(q=>q[k]),...hi.map(q=>q[k])];
    const u=[...new Set(raw.map(z=>three(Math.max(rect[k][0],Math.min(rect[k][1],z)))))].sort((a,b)=>a-b);
    return [...new Set([...u,...u.slice(1).map((z,i)=>three((z+u[i])/2))])].sort((a,b)=>a-b);
  });
  const [nx,ny,nz]=axes.map(q=>q.length),count=nx*ny*nz;
  assert(count<1500000,"K27 graph cap exceeded");
  const flat=(x,y,z)=>(x*ny+y)*nz+z;
  const indexes=p=>p.map((v,k)=>axes[k].findIndex(z=>Math.abs(z-v)<1e-7));
  const idxStart=indexes(source),idxTarget=indexes(target);
  assert(!idxStart.includes(-1)&&!idxTarget.includes(-1),"source/target no corresponding grid planes");
  const start=flat(...idxStart),goal=flat(...idxTarget),parents=new Int32Array(count),seen=new Uint8Array(count),queue=new Int32Array(count);
  parents.fill(-1);
  const point=id=>{const z=id%nz,y=Math.floor(id/nz)%ny,x=Math.floor(id/(ny*nz));return [axes[0][x],axes[1][y],axes[2][z]]};
  function free(id){
   if(seen[id])return seen[id]===1;
   const p=point(id);
   for(let j=0;j<lo.length;j++)if(p.every((v,k)=>v>lo[j][k]+1e-7&&v<hi[j][k]-1e-7)){seen[id]=2;return false;}
   seen[id]=1;return true;
  }
  if(!free(start)||!free(goal))return {passed:false,reason:"entry or final pose interpenetrates existing geometry",nodes:count};
  let begin=0,end=0;queue[end++]=start;parents[start]=start;
  while(begin<end){
   const here=queue[begin++];if(here===goal)break;
   const z=here%nz,y=Math.floor(here/nz)%ny,x=Math.floor(here/(ny*nz));
   for(const [dx,dy,dz]of [[-1,0,0],[1,0,0],[0,0,-1],[0,0,1],[0,-1,0],[0,1,0]]){
    const xx=x+dx,yy=y+dy,zz=z+dz;
    if(xx<0||yy<0||zz<0||xx>=nx||yy>=ny||zz>=nz)continue;
    const next=flat(xx,yy,zz);
    if(parents[next]!==-1||!free(next))continue;
    parents[next]=here;queue[end++]=next;
   }
  }
  const passed=parents[goal]!==-1;
  const output={passed,aperture_projected_radial_margin_mm:three(radial),visited_nodes:begin,grid_shape_xyz:[nx,ny,nz]};
  if(!passed)return output;
  const reverse=[];let here=goal;
  while(true){reverse.push(point(here));if(here===start)break;here=parents[here];}
  const all=reverse.reverse(),pts=[all[0]];
  for(let i=1;i<all.length-1;i++){
   const a=all[i-1],b=all[i],c=all[i+1],ax=a.findIndex((v,k)=>Math.abs(v-b[k])>1e-7),bx=b.findIndex((v,k)=>Math.abs(v-c[k])>1e-7);
   if(ax!==bx)pts.push(b);
  }
  pts.push(all.at(-1));
  for(let i=0;i<pts.length-1;i++){
   const a=pts[i],b=pts[i+1];
   assert(a.filter((v,k)=>Math.abs(v-b[k])>1e-7).length===1,"not axis segment in K27");
   const box={id:"swept",o:a.map((v,k)=>Math.min(v,b[k])-half[k]),s:a.map((v,k)=>Math.abs(v-b[k])+part.s[k])};
   assert(!collisions([box],scene).length,"K27 saved route hits static solid");
  }
  return {...output,waypoints_global_centers_xyz_mm:pts,independently_checked_swept_AABB_segments:true};
 }
 function runCase(railId,split,state){
  const rail=railBy(railId),scene=environment(railId,state);
  const lowLength=split-rail.o[2],upLength=rail.o[2]+rail.s[2]-split;
  assert(lowLength>50&&upLength>50,"rail segments too short");
  const sleeveWall=2,clearance=0.5,height=50;
  const preloadZ=split-75,finalZ=split-25;
  assert(preloadZ>=rail.o[2]&&preloadZ+height<=split,"collar cannot be preloaded onto lower rail");
  const preloadedLower={id:railId+"_LOW_WITH_SLEEVE_CONSERVATIVE_AABB",
   o:[rail.o[0]-2.5,rail.o[1]-2.5,rail.o[2]],
   s:[rail.s[0]+5,rail.s[1]+5,lowLength]};
  const upper={id:railId+"_UP",
   o:[rail.o[0],rail.o[1],split],s:[rail.s[0],rail.s[1],upLength]};
  const low=criticalPlaneRoute(preloadedLower,scene);
  const up=criticalPlaneRoute(upper,[...scene,preloadedLower]);
  const preloadWalls=sleeveAt(rail,preloadZ),finalWalls=sleeveAt(rail,finalZ);
  const slide=preloadWalls.map((p,i)=>({id:p.id,o:[p.o[0],p.o[1],preloadZ],s:[p.s[0],p.s[1],height+50]}));
  const railParts=[{id:"LOW_RAIL",o:rail.o,s:[rail.s[0],rail.s[1],lowLength]},upper];
  const originalLips=B.contact_lips.filter(p=>p.group===rail.group&&p.o[0]===rail.o[0])
   .map(p=>({id:p.id,o:p.o,s:p.s}));
  const finalCollides=collisions(finalWalls,scene);
  const sweepCollides=collisions(slide,scene);
  const ownRailHit=collisions(slide,railParts);
  const oldLips=collisions(slide,originalLips);
  const rayRadius=Math.hypot(rail.o[0]+rail.s[0]/2-231,split-250);
  return {rail:railId,state,split_global_z_mm:split,
   geometry:{
     original_unfastened_rail_cross_section_mm:rail.s.slice(0,2),
     sleeve_outer_cross_section_mm:[rail.s[0]+5,rail.s[1]+5],
     sleeve_inner_free_cross_section_mm:[rail.s[0]+1,rail.s[1]+1],
     hypothetical_wall_thickness_mm:sleeveWall,
     nominal_slide_clearance_each_radial_side_mm:clearance,
     sleeve_axial_height_mm:height,
     preload_z_interval_mm:[preloadZ,preloadZ+height],
     final_z_interval_mm:[finalZ,finalZ+height],
     sleeve_slide_distance_upward_z_mm:50,
     sleeve_four_wall_cuboids_final:finalWalls,
     static_ring_material_net_displacement_l:three(((rail.s[0]+5)*(rail.s[1]+5)-(rail.s[0]+1)*(rail.s[1]+1))*height/1e6)
   },
   collision_tests:{
     sleeve_final_with_other_cabinet_rails_and_all_modules:finalCollides,
     sleeve_slide_swept_with_other_cabinet_rails_and_all_modules:sweepCollides,
     sleeve_slide_swept_with_own_two_rail_halves:ownRailHit,
     sleeve_slide_swept_with_original_K17_integral_lips:oldLips
   },
   composite_install_lower_then_upper:{
     first_lower_rail_with_preloaded_sleeve:low,
     next_plain_upper_rail_while_lower_installed:up,
     both_halves_fit_nominal_translational_route:low.passed&&up.passed,
     sleeve_axial_slide_collision_free_without_integrated_lips:finalCollides.length===0&&sweepCollides.length===0&&ownRailHit.length===0,
     motion_verified_with_integral_original_lips:oldLips.length===0},
   axial_y_tool_screen:{rail_front_y_mm:rail.o[1],
     nominal_front_opening_center_xz_mm:[231,250],
     rail_face_projection_distance_from_driver_axis_mm:three(rayRadius),
     source_K25_direct_face_tool_is_accessible:C.selected_guide_studies[railId].straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model,
     sleeve_has_real_axial_lock:false,
     remote_actuation_or_tool_path_proven:false}
  };
 }
 const cases=[
  runCase("G17_COLUMN_02",250,"full100"),
  runCase("G17_COLUMN_02",250,"core120"),
  runCase("G17_COLUMN_10",194,"core120"),
  runCase("G17_COLUMN_10",194,"single150"),
  runCase("G17_COLUMN_10",194,"full100"),
  runCase("G17_COLUMN_10",300,"core120")
 ];
 assert(cases.slice(0,4).every(v=>v.composite_install_lower_then_upper.both_halves_fit_nominal_translational_route),"required K27 composite path blocked");
 assert(cases[4].composite_install_lower_then_upper.both_halves_fit_nominal_translational_route===false,"unexpected guide10 full100 route");
 assert(cases[5].composite_install_lower_then_upper.both_halves_fit_nominal_translational_route===true,"alternate Z300 route blocked");
 assert(cases.every(v=>v.collision_tests.sleeve_final_with_other_cabinet_rails_and_all_modules.length===0&&v.collision_tests.sleeve_slide_swept_with_other_cabinet_rails_and_all_modules.length===0),"sleeve collisions with fixed scene");
 assert(cases[0].collision_tests.sleeve_slide_swept_with_original_K17_integral_lips.length===0,"guide02 legacy lip sensitivity changed");
 assert(cases[2].collision_tests.sleeve_slide_swept_with_original_K17_integral_lips.length===2,"guide10 legacy lip conflict changed");
 const displacement=6800/1e6;
 const model={
  study:"K27",date:"2026-11-04",status:"CNC HOLD — sliding sleeve geometrically feasible in ideal model but REJECTED as a finished load-bearing lock",
  coordinates:"K15 global XYZ in millimetres; X horizontal cabinet, Y depth, Z vertical",
  inputs:["K15 shell+20 sealed box positions","K17 fixed spines+original integral lips","K25 split positions and tool access","K26 nominal service-state rail-half routes"],
  studied_not_selected_hardware:{
   sleeve_topology:"one-piece open-through tube around the two butt-jointed 16×12mm MDF guide halves",
   wall_thickness_mm:2,nominal_radial_sliding_clearance_each_side_mm:0.5,axial_length_mm:50,
   outside_cross_section_mm:[21,17],inside_cross_section_mm:[17,13],
   cross_section_wall_net_area_mm2:136,solid_material_volume_per_collar_l:displacement,
   both_sleeve_material_volume_l:2*displacement,
   material_density_measured:false,steel_grade_selected:false,supplier_fitting_available:false,
   fasteners_actual_number:0,positive_axial_retaining_features:0,actual_tooling_approved:false,
   user_must_not_manufacture_from_these_envelopes:true},
  test_method:"Conservative rigid AABB of entire pre-sleeved lower half is routed from centered factory Ø355.8 front cutout into cabinet with Y,X,Z orthogonal translations via 3D Minkowski critical-plane graph BFS. Upper plain rail then routed with the entire lower bounding AABB installed. Each leg independently swept and collision checked. Four sleeve walls then translated 50mm along Z from preload to bridge the split; sweep checked against all neighboring nominal solids, own rail halves and original integral K17 lips separately.",
  cases,
  axial_lock_falsification:{
   sleeve_without_holes_pins_captive_stops_or_positive_end_support_can_slide_off_rail:true,
   butt_joint_cannot_transfer_positive_axial_tension_by_sleeve_alone:true,
   sleeve_0_5mm_clearance_does_not_impose_known_preload_or_bending_stiffness:true,
   neither_MDF_bearing_nor_wall_yield_fatigue_or_corrosion_tested:true,
   real_joint_design_approved:false},
  safe_service_gates:{
   guide02_K25_hypothetical_Y_tool_only_geometrically_accessible:true,
   guide10_K25_straight_Y_tool_blocked_by_front_opening:true,
   guide10_sleeve_cannot_be_operated_and_locked_by_an_assumed_straight_screwdriver:true,
   installing_or_removing_rail_requires_positive_temporary_support_for_guide02_modules:[0,1],
   guide10_modules_at_risk:[12,13,14,15],
   necessary_named_fixture_tests:["Positive axial lock and anti-vibration stop accessible from Ø355.8 hole","Bending, shear, pullout, torsional retention and cycling qualification with real dimensions","After-insertion installation of structurally qualified lower support, upper anti-inversion keeper and real tool access","Full 100↔120↔150 state cycle with every physical latch and screw modeled","MDF22 anchoring, joint tolerance, tool/CAM radius, cabinet depth, true basket and measured air volume"],
   nominal_CNC_release:false}
 };
 return model;
}
function main(){
  const root=path.resolve(__dirname,".."),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
  const r=buildK27(read("wyniki/k15_p30e_przed_CNC_zestawienie.json"),read("wyniki/k17_prowadnice_boczne_wkladow.json"),read("wyniki/k25_zlacza_prowadnic_i_dostep.json"),read("wyniki/k26_przejscia_dzielonych_prowadnic.json"));
  const output=path.join(root,"wyniki/k27_tuleja_przesuwna_i_trasy.json");
  fs.mkdirSync(path.dirname(output),{recursive:true});
  fs.writeFileSync(output,JSON.stringify(r,null,2)+"\n");
  console.log(JSON.stringify({status:r.status,results:r.cases.map(v=>[v.rail,v.state,v.split_global_z_mm,v.composite_install_lower_then_upper.both_halves_fit_nominal_translational_route,v.collision_tests.sleeve_slide_swept_with_original_K17_integral_lips]),cnc:r.safe_service_gates.nominal_CNC_release}));
}
if(require.main===module)main();
module.exports={buildK27};
