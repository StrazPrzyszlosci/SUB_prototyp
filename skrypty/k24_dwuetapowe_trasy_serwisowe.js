#!/usr/bin/env node
"use strict";
// K24: critical-plane 3D orthogonal BFS + continuous swept-AABB checks; NEVER use as CNC.
const fs=require("node:fs"),path=require("node:path");
function buildK24(A,B,K23){
 const modules=A.module_positions,assert=(v,msg)=>{if(!v)throw Error(msg)};
 assert(modules.length===20&&A.parts.length===138&&B.spines.length===12,"Upstream dimensions drift");
 assert(K23.results.with_lower_lips_omitted_full_construction===20,"K23 result drift");
 const cabinet=A.parts.filter(p=>p.module_index===-1&&!["FR1","FR2"].includes(p.id)).map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm}));
 const mat={id:"mat50",o:[22,353,22],s:[976,50,456]};
 const obstacles=(missing,placed)=>{
  const removed=new Set(missing);
  return [...cabinet,mat,
   ...B.spines.filter(p=>!removed.has(p.id)).map(p=>({id:p.id,o:p.o,s:p.s})),
   ...placed.map(i=>({id:"box_"+i,o:modules[i].global_origin_xyz_mm,s:modules[i].dims_xyz_mm}))];
 };
 const snap=v=>Math.round(v*1000)/1000;
 const overlap=(a,b)=>a.o.every((v,k)=>Math.min(v+a.s[k],b.o[k]+b.s[k])-Math.max(v,b.o[k])>1e-7);
 function route(module,obs,margin=0,save=false){
  const half=module.dims_xyz_mm.map(v=>v/2),room=[[22+half[0]+margin,998-half[0]-margin],[44+half[1]+margin,403-half[1]-margin],[22+half[2]+margin,478-half[2]-margin]];
  const start=[231,44+half[1]+margin,250],goal=module.global_center_xyz_mm;
  if(goal.some((v,k)=>v<room[k][0]-1e-7||v>room[k][1]+1e-7))return {ok:false,reason:"nominal destination leaves clearance envelope"};
  const lo=obs.map(o=>o.o.map((v,k)=>v-half[k]-margin));
  const hi=obs.map(o=>o.o.map((v,k)=>v+o.s[k]+half[k]+margin));
  const axes=[0,1,2].map(k=>{
    const raw=[start[k],goal[k],...room[k],...lo.map(v=>v[k]),...hi.map(v=>v[k])];
    const u=[...new Set(raw.map(v=>snap(Math.max(room[k][0],Math.min(room[k][1],v)))))].sort((a,b)=>a-b);
    return [...new Set([...u,...u.slice(1).map((v,i)=>snap((v+u[i])/2))])].sort((a,b)=>a-b);
  });
  const [nx,ny,nz]=axes.map(v=>v.length),count=nx*ny*nz;
  assert(count<=1500000,"Too many grid nodes");
  const flat=(x,y,z)=>(x*ny+y)*nz+z;
  const toIdx=v=>v.map((z,k)=>axes[k].findIndex(x=>Math.abs(x-z)<1e-7));
  const s=toIdx(start),t=toIdx(goal);assert(!s.includes(-1)&&!t.includes(-1),"endpoints off graph");
  const src=flat(...s),dst=flat(...t),visited=new Int32Array(count),occ=new Uint8Array(count),queue=new Int32Array(count);
  visited.fill(-1);
  const point=index=>{const z=index%nz,y=Math.floor(index/nz)%ny,x=Math.floor(index/(ny*nz));return [axes[0][x],axes[1][y],axes[2][z]]};
  const free=index=>{
   if(occ[index])return occ[index]===1;
   const p=point(index);
   for(let j=0;j<lo.length;j++)if(p.every((v,k)=>v>lo[j][k]+1e-7&&v<hi[j][k]-1e-7)){occ[index]=2;return false}
   occ[index]=1;return true
  };
  if(!free(src)||!free(dst))return {ok:false,reason:"start or finished placement blocked",grid:[nx,ny,nz]};
  let left=0,right=0;queue[right++]=src;visited[src]=src;
  while(left<right){
   const n=queue[left++];if(n===dst)break;
   const z=n%nz,y=Math.floor(n/nz)%ny,x=Math.floor(n/(ny*nz));
   for(const [dx,dy,dz]of [[-1,0,0],[1,0,0],[0,-1,0],[0,0,-1],[0,0,1],[0,1,0]]){
    const xx=x+dx,yy=y+dy,zz=z+dz;
    if(xx<0||yy<0||zz<0||xx>=nx||yy>=ny||zz>=nz)continue;
    const ni=flat(xx,yy,zz);
    if(visited[ni]!==-1||!free(ni))continue;
    visited[ni]=n;queue[right++]=ni
   }
  }
  const ok=visited[dst]!==-1;
  if(!ok||!save)return {ok,expanded_nodes:left,grid:[nx,ny,nz]};
  const reverse=[];let cur=dst;
  while(true){reverse.push(point(cur));if(cur===src)break;cur=visited[cur]}
  const all=reverse.reverse(),chosen=[all[0]];
  for(let i=1;i<all.length-1;i++){
   const aa=all[i-1],bb=all[i],cc=all[i+1];
   const d1=aa.findIndex((v,k)=>Math.abs(v-bb[k])>1e-7);
   const d2=bb.findIndex((v,k)=>Math.abs(v-cc[k])>1e-7);
   if(d1!==d2)chosen.push(bb);
  }
  chosen.push(all.at(-1));
  for(let i=0;i<chosen.length-1;i++){
   const a=chosen[i],b=chosen[i+1];
   assert(a.filter((v,k)=>Math.abs(v-b[k])>1e-7).length===1,"Nonaxis segment");
   const v={o:a.map((x,k)=>Math.min(x,b[k])-half[k]-margin),s:a.map((x,k)=>Math.abs(x-b[k])+2*half[k]+2*margin)};
   const conflicts=obs.filter(o=>overlap(v,o));
   assert(conflicts.length===0,"Swept path collision "+JSON.stringify({id:module.i,i,conflicts:conflicts.map(x=>x.id),a,b}));
  }
  return {ok:true,expanded_nodes:left,grid:[nx,ny,nz],from_front_aperture_to_target:chosen,
    continuous_swept_AABB_rechecked:true};
 }
 function phase(name,installed,toRemove,missing,margin=0){
  let present=[...installed];const actions=[];
  for(let step=0;step<toRemove.length;step++){
   const candidates=toRemove.filter(id=>present.includes(id));
   const ready=[];
   for(const id of candidates)if(route(modules[id],obstacles(missing,present.filter(x=>x!==id)),margin,false).ok)ready.push(id);
   if(!ready.length)return {name,missing_spines:missing,clearance_mm:margin,completed:false,removed:actions.map(x=>x.id),remaining:present,actions,first_stalled_step:step};
   const id=ready[0];
   const way=route(modules[id],obstacles(missing,present.filter(x=>x!==id)),margin,true);
   assert(way.ok&&way.continuous_swept_AABB_rechecked,"BFS route invalid");
   actions.push({id,available_to_remove_before_selection:ready,reverse_for_extract:way.from_front_aperture_to_target,
     note:"The listed route runs aperture→box. Reverse its segments to extract the box."});
   present=present.filter(v=>v!==id);
  }
  return {name,missing_spines:missing,clearance_mm:margin,completed:true,removed:actions.map(x=>x.id),remaining:present,actions}
 }
 const all=modules.map(x=>x.i),states120=modules.filter(x=>x.candidate_state_inclusion.includes("120")).map(x=>x.i);
 const remove8=[0,1,2,3,16,17,18,19],remove11=states120.filter(i=>i!==4);
 const p100=phase("100 to 120: temporary release of small guide 02",all,remove8,["G17_COLUMN_02"]);
 const p150=phase("120 to 150: temporary release of large rear guide 10",states120,remove11,["G17_COLUMN_10"]);
 const b100=phase("100 to 120: all rails present",all,remove8,[]);
 const b150=phase("120 to 150: all rails present",states120,remove11,[]);
 const alt03=phase("100 to 120: guide 03",all,remove8,["G17_COLUMN_03"]);
 const alt04=phase("100 to 120: guide 04",all,remove8,["G17_COLUMN_04"]);
 const margin100=phase("100 to 120: guide 02 with 1mm uniform clearance",all,remove8,["G17_COLUMN_02"],1);
 const margin150=phase("120 to 150: guide 10 with 1mm uniform clearance",states120,remove11,["G17_COLUMN_10"],1);
 const smallGuideIds=[1,2,3,4].map(i=>"G17_COLUMN_"+String(i).padStart(2,"0"));
 const masks=[];
 for(let mask=0;mask<16;mask++){
  const missing=smallGuideIds.filter((_,i)=>!!(mask&(1<<i)));
  const isAccessible=[0,1,2,3].map(i=>route(modules[i],obstacles(missing,states120),0,false).ok);
  masks.push({missing_small_guides:missing,accessible_small_modules:isAccessible.map((v,i)=>({id:i,ok:v})),all4:isAccessible.every(Boolean)});
 }
 assert(p100.completed&&p150.completed&&!b100.completed&&!b150.completed&&alt03.completed&&alt04.completed,"K24 stage change");
 assert(masks.filter(v=>!v.all4).length===2,"K24 mask divergence");
 const loadSpecs=[
  {name:"small_rear_guide02",id:0,L:23,rail:"G17_COLUMN_02",affected:[0,1]},
  {name:"large_rear_guide10",id:12,L:19,rail:"G17_COLUMN_10",affected:[12,13,14,15]}
 ].map(g=>{
   const mass=A.parts.filter(p=>p.module_index===g.id).reduce((s,p)=>s+p.box_size_xyz_mm.reduce((a,v)=>a*v,1),0)*730/1e9;
   const perPair=mass*9.81*5/2,single=perPair*2;
   return {...g,shell_mass_kg:snap(mass),two_support_share_each_N:snap(perPair),
    one_remaining_support_if_unassisted_N:snap(single),nominal_far_tip_single_support_moment_Nmm:snap(single*g.L),
    hypothetical_elastic_stress_single_support_MPa:snap(6*single*g.L/(16*4*4)),strength_qualified:false};
 });
 const jointAt250=id=>{
  const r=B.spines.find(x=>x.id===id);
  return B.contact_lips.filter(t=>t.group===r.group&&t.o[0]===r.o[0]&&t.o[2]<=250&&t.o[2]+t.s[2]>=250)
   .map(t=>({id:t.id,z_span:[t.o[2],t.o[2]+t.s[2]]}));
 };
 const support={split_guide02_at_z250_existing_contact_lips:jointAt250("G17_COLUMN_02"),
  split_guide10_at_z250_existing_contact_lips:jointAt250("G17_COLUMN_10"),
  each_guide_full_height_mm:456,proposed_unjoined_segments_mm:[228,228],
  half_guide_16mm_by228mm_aperture_projection_corner_plus6mm_margin:snap(Math.hypot(16/2+6,228/2+6)),
  reference_aperture_radius_mm:177.9,
  hypothetical_material_density_kg_m3:730,hypothetical_transport_acceleration_g:5,
  structural_demand_if_one_side_support_removed:loadSpecs,
  gap_from_rear_small_rail_to_box_front_mm:11,gap_from_rear_large_rail_to_box_front_mm:7,
  gap_from_front_rail_to_front_box_mm:0,
  front_large_box_back_to_large_rear_rail_front_mm:6,
  hypothetical_tool_diameter_mm:10,hypothetical_tool_clearance_per_side_mm:1,
  needed_tool_envelope_mm:12,
  actual_hardware_designed:false,ability_to_remove_rail_after_all_boxes_installed_proven:false};
 const output={
  study:"K24",date:"2026-11-04",status:"CNC HOLD — nominal reversible state topology exists only if structural guide and shelf hardware can be removed and resecured",
  model:"Critical-plane Minkowski AABB decomposition; Cartesian orthogonal graph BFS with boundary planes and midpoints, 1 micrometre rounded grid, no box rotation; reconstructed paths checked as continuous swept AABB segments; exact nominal face contacts allowed.",
  inputs:"K15, K17, K23",
  entry:"All rigid boxes enter/leave through nominal centred Ø355.8 opening with driver removed, at X231/Z250; front two panels replaced by circular entry check. Front module 210x100 projected rectangle corner <177.9mm. Cabinet cavity [X22,998],[Y44,403],[Z22,478].",
  excluded:"ALL removable lower ledges and upper keepers, fastening screws, real basket, hand/tool access, full 6DOF, tolerances, rail segment attachment; all material, mechanical and CNC approvals absent.",
  targetStates:{state100_ids:all,state120_ids:states120,state150_ids:[4]},
  releasePhase100to120:p100,releasePhase120to150:p150,
  unremovedRailControls:{attempt100to120:b100,attempt120to150:b150},
  alternativeSmallGuideIds:{guide03:alt03.completed,guide04:alt04.completed},
  full16maskSmallGuideStudy:masks,
  uniformOneMillimetreMarginScreens:{attempt100to120:margin100,attempt120to150:margin150},
  reverseTransition:"Under identical absent-shelf and temporary-guide conditions, reverse the saved removal order and each saved path to model 150→120 and 120→100. Reinsertion of guides, mechanical supports and locks is NOT verified.",
  supportRiskScreen:support,
  releaseFlags:{cnc_approved:false,all_dynamic_collision_sweeps_of_saved_ideal_paths_verified:true,
    true_fastener_bearing_pullout_and_fatigue_verified:false,
    actual_module_service_and_rail_reattachment_verified:false,
    no_nominal_clearance_claimed_as_production_tolerance:true}
 };
 return output;
}
function main(){
 const root=path.resolve(__dirname,"..");
 const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
 const r=buildK24(read("wyniki/k15_p30e_przed_CNC_zestawienie.json"),read("wyniki/k17_prowadnice_boczne_wkladow.json"),read("wyniki/k23_swept_montaz_wkladow.json"));
 const out=path.join(root,"wyniki/k24_drogi_serwisowe_i_podpory.json");
 fs.mkdirSync(path.dirname(out),{recursive:true});
 fs.writeFileSync(out,JSON.stringify(r,null,2)+"\n");
 console.log(JSON.stringify({status:r.status,phase1:r.releasePhase100to120.removed,phase2:r.releasePhase120to150.removed,cnc:r.releaseFlags.cnc_approved}));
}
if(require.main===module)main();
module.exports={buildK24};
