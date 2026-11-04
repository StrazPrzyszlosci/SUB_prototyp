#!/usr/bin/env node
"use strict";
// K26 full 3D translation (no rotation) of removable rail halves under present modular box occupancy.
// Source data: K15, K17, K25. NO PHYSICAL CONNECTORS. CNC HOLD.
const fs=require("node:fs"),path=require("node:path");
function buildK26(K15,K17,K25){
  const die=msg=>{throw Error(msg);};
  const assert=(v,msg)=>{if(!v)die(msg);};
  assert(K15.module_positions.length===20&&K17.spines.length===12,"Unexpected K15/K17 data");
  const items=K15.module_positions,room=K15.parts.filter(p=>p.module_index===-1&&!["FR1","FR2"].includes(p.id)).map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm}));
  const mat={id:"rear_mat",o:[22,353,22],s:[976,50,456]};
  const r3=v=>Math.round(v*1000)/1000;
  const box=(b)=>({id:b.id,o:b.o,s:b.s});
  function scene(rail,ids,extra=[]){
    return [...room,mat,...K17.spines.filter(x=>x.id!==rail).map(box),...ids.map(i=>({id:"module_"+i,o:items[i].global_origin_xyz_mm,s:items[i].dims_xyz_mm})),...extra];
  }
  function collision(a,b,eps=1e-7){
    return a.o.every((v,k)=>Math.min(v+a.s[k],b.o[k]+b.s[k])-Math.max(v,b.o[k])>eps);
  }
  function route(part,obstacles,margin=0,full=true){
    const half=part.s.map(v=>v/2);
    const bounds=[[22+half[0]+margin,998-half[0]-margin],[44+half[1]+margin,403-half[1]-margin],[22+half[2]+margin,478-half[2]-margin]];
    const source=[231,44+half[1]+margin,250],target=part.o.map((v,k)=>v+half[k]);
    const apertureMargin=177.9-Math.hypot(half[0]+margin,half[2]+margin);
    if(apertureMargin<=0)return {pass:false,reason:"opening projection",aperture_margin_mm:r3(apertureMargin)};
    if(target.some((v,k)=>v<bounds[k][0]-1e-7||v>bounds[k][1]+1e-7))return {pass:false,reason:"end-cap/cabinet clearance incompatible with exact seated end",aperture_margin_mm:r3(apertureMargin)};
    const lows=obstacles.map(o=>o.o.map((v,k)=>v-half[k]-margin));
    const highs=obstacles.map(o=>o.o.map((v,k)=>v+o.s[k]+half[k]+margin));
    const axes=[0,1,2].map(k=>{
      const raw=[source[k],target[k],...bounds[k],...lows.map(x=>x[k]),...highs.map(x=>x[k])];
      const u=[...new Set(raw.map(v=>r3(Math.max(bounds[k][0],Math.min(bounds[k][1],v)))))].sort((a,b)=>a-b);
      return [...new Set([...u,...u.slice(1).map((v,i)=>r3((v+u[i])/2))])].sort((a,b)=>a-b);
    });
    const [nx,ny,nz]=axes.map(a=>a.length),n=nx*ny*nz;
    if(n>1500000)die("Graph cap exceeded");
    const index=(x,y,z)=>(x*ny+y)*nz+z;
    const indexOf=p=>p.map((v,k)=>axes[k].findIndex(x=>Math.abs(x-v)<1e-7));
    const ss=indexOf(source),gg=indexOf(target);
    if(ss.includes(-1)||gg.includes(-1))die("Endpoint lost in graph");
    const start=index(...ss),goal=index(...gg),parent=new Int32Array(n),blocked=new Uint8Array(n),q=new Int32Array(n);parent.fill(-1);
    const point=id=>{const zz=id%nz,yy=Math.floor(id/nz)%ny,xx=Math.floor(id/(ny*nz));return [axes[0][xx],axes[1][yy],axes[2][zz]];};
    function free(id){
      if(blocked[id])return blocked[id]===1;
      const p=point(id);
      for(let j=0;j<lows.length;j++){
        if(p.every((v,k)=>v>lows[j][k]+1e-7&&v<highs[j][k]-1e-7)){blocked[id]=2;return false;}
      }
      blocked[id]=1;return true;
    }
    if(!free(start)||!free(goal))return {pass:false,reason:"target or entry intersects expanded obstacle",aperture_margin_mm:r3(apertureMargin)};
    let front=0,rear=0;q[rear++]=start;parent[start]=start;
    while(front<rear){
      const now=q[front++];if(now===goal)break;
      const z=now%nz,y=Math.floor(now/nz)%ny,x=Math.floor(now/(ny*nz));
      for(const [dx,dy,dz]of [[-1,0,0],[1,0,0],[0,-1,0],[0,0,-1],[0,0,1],[0,1,0]]){
        const xx=x+dx,yy=y+dy,zz=z+dz;
        if(xx<0||yy<0||zz<0||xx>=nx||yy>=ny||zz>=nz)continue;
        const next=index(xx,yy,zz);
        if(parent[next]!==-1||!free(next))continue;
        parent[next]=now;q[rear++]=next;
      }
    }
    const pass=parent[goal]!==-1,summary={pass,expanded_nodes:front,grid_shape_xyz:[nx,ny,nz],aperture_margin_mm:r3(apertureMargin)};
    if(!pass||!full)return summary;
    const reversed=[];let here=goal;
    while(true){reversed.push(point(here));if(here===start)break;here=parent[here];}
    const all=reversed.reverse(),pts=[all[0]];
    for(let j=1;j<all.length-1;j++){
      const a=all[j-1],b=all[j],c=all[j+1];
      if(a.findIndex((v,k)=>Math.abs(v-b[k])>1e-7)!==b.findIndex((v,k)=>Math.abs(v-c[k])>1e-7))pts.push(b);
    }
    pts.push(all.at(-1));
    for(let i=0;i<pts.length-1;i++){
      const a=pts[i],b=pts[i+1];
      assert(a.filter((v,k)=>Math.abs(v-b[k])>1e-7).length===1,"Non-axis compacted path");
      const sw={o:a.map((v,k)=>Math.min(v,b[k])-half[k]-margin),s:a.map((v,k)=>Math.abs(v-b[k])+2*(half[k]+margin))};
      const collisions=obstacles.filter(o=>collision(sw,o));
      assert(!collisions.length,"False feasible swept path "+JSON.stringify({part:part.id,segment:i,hits:collisions.map(v=>v.id)}));
    }
    summary.path_global_center_xyz_from_driver_to_rail=pts;
    summary.all_continuous_swept_AABBs_rechecked=true;
    summary.segment_count=pts.length-1;
    return summary;
  }
  const configurations={
    full100:items.map(i=>i.i),
    core120:items.filter(i=>i.candidate_state_inclusion.includes("120")).map(i=>i.i),
    single150:[4]
  };
  const cases=[
    {name:"rail02_service_release_at_100",rail:"G17_COLUMN_02",split:250,state:"full100"},
    {name:"rail02_reinstall_at_120",rail:"G17_COLUMN_02",split:250,state:"core120"},
    {name:"rail10_service_release_at_120",rail:"G17_COLUMN_10",split:194,state:"core120"},
    {name:"rail10_reinstall_at_150",rail:"G17_COLUMN_10",split:194,state:"single150"},
    {name:"rail10_out_of_order_attempt_at_100",rail:"G17_COLUMN_10",split:194,state:"full100"},
    {name:"rail10_alternative_Z300_at_120",rail:"G17_COLUMN_10",split:300,state:"core120"},
    {name:"rail10_alternative_Z300_at_150",rail:"G17_COLUMN_10",split:300,state:"single150"}
  ];
  const records=[];
  for(const variant of cases){
    const rail=K17.spines.find(p=>p.id===variant.rail);
    const segs=[
      {id:variant.rail+"_LOW",o:[...rail.o],s:[rail.s[0],rail.s[1],variant.split-rail.o[2]]},
      {id:variant.rail+"_UP",o:[rail.o[0],rail.o[1],variant.split],s:[rail.s[0],rail.s[1],rail.o[2]+rail.s[2]-variant.split]}
    ];
    const obstacles=scene(variant.rail,configurations[variant.state]);
    const orders=[[0,1],[1,0]].map(order=>{
      const first=segs[order[0]],second=segs[order[1]];
      const f=route(first,obstacles,0,true);
      const s=route(second,[...obstacles,first],0,true);
      return {install_order:[first.id,second.id],first:f,second:s,all_segments_installable:f.pass&&s.pass,
        removal_feasible_in_reverse_order_without_latches:f.pass&&s.pass};
    });
    const marginOnlySegments=segs.map(s=>({id:s.id,zero_mm:route(s,obstacles,0,false).pass,
      one_mm:route(s,obstacles,1,false)}));
    records.push({id:variant.name,rail:variant.rail,state:variant.state,split_global_z_mm:variant.split,
      segment_original_unfastened_boxes:segs,other_installed_modules:configurations[variant.state],
      order_tests:orders,zero_to_one_mm_uniform_clearance_sensitivity:marginOnlySegments,
      valid_in_both_orders:orders.every(x=>x.all_segments_installable),
      tool_access_assumed:false,splice_strength_verified:false,
      own_integrated_lips_present:false});
  }
  for(const id of cases.slice(0,4).map(x=>x.name)){
    if(!records.find(x=>x.id===id).valid_in_both_orders)die("Required assembly geometry unexpectedly blocked "+id);
  }
  if(records.find(x=>x.id==="rail10_out_of_order_attempt_at_100").valid_in_both_orders)die("Unexpected guide10 entry in all-100 state");
  if(!records.filter(x=>x.id.includes("alternative")).every(x=>x.valid_in_both_orders))die("Alternate split blocked");
  const plate02=K25.selected_guide_studies.G17_COLUMN_02;
  const plate10=K25.selected_guide_studies.G17_COLUMN_10;
  assert(plate02.chosen_research_split_global_z_mm===250&&plate10.chosen_research_split_global_z_mm===194,"K25 splits changed");
  const report={
    study:"K26",date:"2026-11-04",
    status:"CNC HOLD — independently swept segment motions pass in ideal 0mm translational model; physical fastening/clearance still unqualified",
    model:"Six cabinet-facing axes XYZ (X width, Y depth, Z vertical); each 16×12×172/228/284mm rail half is translated without rotation. Finite 3D critical-plane grid BFS expanded by segment half-size, continuous swept AABB verified for every route leg.",
    input_versions:"K15/K17 full solids and module positions; K25 verified lip-free split windows and actual tool-access obstruction",
    front_hole:"Nominal driver D355.8, centered X231/Z250, actual driver absent; front two baffle solids represented by aperture projection at initial crossing only; all other MDF supports and rear 50mm mat included",
    excluded:["Original K17 top/bottom integrated shelves and K20 upper keeper hardware","K25 hypothetical 2mm plates, real positive metal splice and screws","Full 6DOF rotation, gluing, tolerances, practical hand/tool access, positive anti-rotation fixings and material batch strength","Installer supporting the boxes while rail detached, electrical wiring and compressed acoustic damping"],
    zero_margin_rule:"Exact face tangencies allowed. Rail halves nominally touch each other at the split and touch cabinet bottom/top at Z22 or478. A uniformly expanded 1mm target is intrinsically incompatible with this face-seated reference geometry; this does NOT measure free service-throat clearance.",
    configurations:{full100:configurations.full100,core120:configurations.core120,single150:[4]},
    segment_sweeps:records,
    k25_tool_access_crosscheck:{
      guide02_split250_front_tool_nominal_clear:plate02.straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model,
      guide10_split194_front_tool_nominal_clear:plate10.straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model,
      guide10_face_plate_nominal_front_rear_Y_gaps_mm:plate10.hypothetical_2mm_face_plates.map(p=>p.available_front_back_normal_Y_gap_mm),
      guide10_straight_front_tool_blocked_by_baffle_cutout:true,
      guide10_tool_fastening_or_remote_latch_still_missing:true,
      projection_is_not_mechanical_approval:true
    },
    operational_conclusion:{
      can_remove_and_reinstall_rail02_half_shapes_with_all20_modules_in_the_nominal_unfastened_model:true,
      can_remove_and_reinstall_rail02_half_shapes_at_core120:true,
      can_remove_and_reinstall_rail10_half_shapes_at_core120:true,
      can_remove_and_reinstall_rail10_half_shapes_at_single150:true,
      can_remove_and_reinstall_rail10_half_shapes_at_all20:false,
      correct_staging_order_required:"100->120 with guide02 only; restore it; then 120->150 with guide10 only; restore it. Invert these stages for reverse capacity changes, with physically serviceable fixtures still to design.",
      full_joint_design_approved:false,
      CNC_ready:false
    },
    next_engineering_gates:["Design physically releasable, load-rated guide02/guide10 connectors and safe temporary box support.","Resolve guide10 remote/tool-free locking from Ø355.8 driver aperture: K25 straight face tool cannot reach.","Rerun complete 100↔120↔150 installation/removal *with actual joint metal, locks, shelves, fasteners and tool envelope as solids*.","Qualify shelf and MDF+metal joint bearing, fatigue, creep, shear, pullout, safe 5g/operational scenarios with measured material and calibrated fixtures.","Recompute real air volumes with hardware & damping and FEM/acoustics; then produce tolerance/kerf/radii/datum specified CNC drawings."]
  };
  return report;
}
function main(){
  const root=path.resolve(__dirname,"..");
  const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
  const m=buildK26(load("wyniki/k15_p30e_przed_CNC_zestawienie.json"),load("wyniki/k17_prowadnice_boczne_wkladow.json"),load("wyniki/k25_zlacza_prowadnic_i_dostep.json"));
  const result=path.join(root,"wyniki/k26_przejscia_dzielonych_prowadnic.json");
  fs.mkdirSync(path.dirname(result),{recursive:true});
  fs.writeFileSync(result,JSON.stringify(m,null,2)+"\n","utf8");
  console.log(JSON.stringify({status:m.status,result:m.segment_sweeps.map(v=>[v.id,v.valid_in_both_orders]),cnc:m.operational_conclusion.CNC_ready}));
}
if(require.main===module)main();
module.exports={buildK26};
