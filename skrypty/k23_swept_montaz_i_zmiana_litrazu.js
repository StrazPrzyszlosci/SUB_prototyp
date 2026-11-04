#!/usr/bin/env node
"use strict";
// K23: nominal continuous axial swept-box paths; NOT a six-axis planner, not CNC.
const fs=require("node:fs"),path=require("node:path");
function buildK23(A,B,C){
 const removed="G17_COLUMN_10";
 if(C.temporary_removed_rail!==removed)throw Error("K22 source changed");
 const construct=[0,2,1,3,4,12,6,14,7,15,5,13,8,16,10,18,11,19,9,17];
 const nested=[4,5,6,7,8,9,10,11,12,13,14,15,0,1,2,3,16,17,18,19];
 const panels=A.parts.filter(p=>p.module_index===-1&&!["FR1","FR2"].includes(p.id)).map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm,kind:"cabinet"}));
 const rails=B.spines.filter(s=>s.id!==removed).map(s=>({id:s.id,o:s.o,s:s.s,kind:"rail"}));
 const removedSpine=B.spines.find(x=>x.id===removed);
 const lower=B.contact_lips.filter(t=>t.position==="shelf"&&!(t.group===removedSpine.group&&t.o[0]===removedSpine.o[0])).map(t=>({id:t.id,o:t.o,s:t.s,kind:"lower lip"}));
 const mat={id:"REAR_MAT_50",o:[22,353,22],s:[976,50,456],kind:"mat"};
 if(A.module_positions.length!==20||A.parts.length!==138||panels.length!==16||rails.length!==11||lower.length!==36)throw Error("Unexpected source counts "+JSON.stringify({a:A.module_positions.length,parts:A.parts.length,panel:panels.length,rails:rails.length,lips:lower.length}));
 const clearObstacles=[...panels,...rails,mat],fixedObstacles=[...panels,...rails,...lower,mat];
 const eps=1e-7;
 const hit=(a,b,clearance=0)=>a.o.every((v,i)=>Math.min(v+a.s[i]+clearance,b.o[i]+b.s[i])-Math.max(v-clearance,b.o[i])>eps);
 const box=m=>({id:"PREVIOUS_MODULE_"+m.i,o:m.global_origin_xyz_mm,s:m.dims_xyz_mm,kind:"installed box"});
 const sweep=(p,q,h)=>{
   if(p.filter((v,i)=>Math.abs(v-q[i])>eps).length!==1)throw Error("Not axis-segment "+JSON.stringify({p,q}));
   return {o:p.map((v,i)=>Math.min(v,q[i])-h[i]),s:p.map((v,i)=>Math.abs(v-q[i])+h[i]*2)};
 };
 function route(m){
   const [w,d,h]=m.dims_xyz_mm,[x,y,z]=m.global_center_xyz_mm;
   const crossZ=z===414?405:Math.max(100,Math.min(400,z)),front=y<200,waitY=front?131:125,waitX=front?x:650;
   const raw=[[231,-d/2-1,250],[231,44+d/2,250],[231,waitY,250],[231,waitY,crossZ],[waitX,waitY,crossZ],[waitX,y,crossZ]];
   if(!front)raw.push([x,y,crossZ]);
   raw.push([x,y,z]);
   const pts=raw.filter((v,i)=>i===0||v.some((q,j)=>Math.abs(q-raw[i-1][j])>eps));
   const margin=177.9-Math.hypot(w/2,h/2);
   if(margin<=0||pts[0][1]>=0)throw Error("Opening pose invalid");
   return {pts,margin:+margin.toFixed(6),crossZ,waitY,waitX};
 }
 function assess(m,obstacles,reversed=false){
   const info=route(m),pts=reversed?[...info.pts].reverse():info.pts,h=m.dims_xyz_mm.map(v=>v/2);
   let fail=null;
   for(let i=0;i<pts.length-1;i++){
     const collisions=obstacles.filter(p=>hit(sweep(pts[i],pts[i+1],h),p));
     if(collisions.length){fail={segment_index:i,from:pts[i],to:pts[i+1],obstacles:collisions.slice(0,8).map(x=>x.id)};break;}
   }
   return {module:m.i,passed:!fail,first_collision:fail,waypoints:pts,aperture_corner_margin_mm:info.margin,staging:{z:info.crossZ,y:info.waitY,x:info.waitX}};
 }
 function build(order,obstacles){
   const old=[],trials=[];
   for(const id of order){
     const v=assess(A.module_positions[id],[...obstacles,...old]);
     trials.push(v);
     if(!v.passed)break;
     old.push(box(A.module_positions[id]));
   }
   return {tested:trials.length,passed:trials.filter(x=>x.passed).length,complete:trials.length===order.length&&trials.every(x=>x.passed),first_failed:trials.find(x=>!x.passed)||null,all:trials};
 }
 function takeout(order){
   const present=new Set(A.module_positions.map(m=>m.i));const trials=[];
   for(const id of order){
     present.delete(id);
     const v=assess(A.module_positions[id],[...clearObstacles,...A.module_positions.filter(m=>present.has(m.i)).map(box)],true);
     trials.push(v);
     if(!v.passed)break;
   }
   return {passed:trials.filter(x=>x.passed).length,complete:trials.length===order.length&&trials.every(x=>x.passed),first_failed:trials.find(x=>!x.passed)||null};
 }
 const isolatedWith=A.module_positions.map(m=>assess(m,fixedObstacles));
 const isolatedWithout=A.module_positions.map(m=>assess(m,clearObstacles));
 const fixedSequence=build(construct,fixedObstacles),stagedSequence=build(construct,clearObstacles),nestedSequence=build(nested,clearObstacles);
 const reverse=takeout([...construct].reverse());
 const smallExtraction=A.module_positions.filter(m=>m.i<=3).map(m=>assess(m,[...clearObstacles,...A.module_positions.filter(o=>o.i!==m.i).map(box)],true));
 const m=A.module_positions[10],r=route(m),h=m.dims_xyz_mm.map(v=>v/2),ix=r.pts.findIndex((p,i)=>i>0&&p[0]!==r.pts[i-1][0]);
 const lateral=sweep(r.pts[ix-1],r.pts[ix],h);
 const lateralClearance=[0,1,2,3].map(mm=>({mm,passes:!clearObstacles.some(x=>hit(lateral,x,mm)),hits:clearObstacles.filter(x=>hit(lateral,x,mm)).map(x=>x.id)}));
 if(isolatedWith.filter(x=>x.passed).length!==12||isolatedWithout.filter(x=>x.passed).length!==20||!stagedSequence.complete||!reverse.complete||nestedSequence.passed!==12||smallExtraction.some(x=>x.passed)||lateralClearance.map(x=>+x.passes).join(",")!=="1,1,1,0")throw Error("K23 unexpected test outcomes "+JSON.stringify({fixed:isolatedWith.filter(x=>x.passed).length,omit:isolatedWithout.filter(x=>x.passed).length,seq:stagedSequence.passed,rev:reverse.complete,nested:nestedSequence.passed,extract:smallExtraction.map(x=>x.passed),lateralClearance}));
 const record={study:"K23",date:"2026-11-04",status:"CNC HOLD — swept AABB axial movement only; no physically approved support or regulation",
  inputs:"K15 138 nominal solids, K17 12 spines and 40 lower tongues, K22 temporary G17_COLUMN_10 omission, K20 no upper keepers while inserting",
  model:{cabinet_obstacles_without_two_front_plates:panels.length,remaining_full_height_rails:rails.length,fixed_lower_lips_for_first_variant:lower.length,mat_envelope:1,
   opening_radius_mm:177.9,entry_center_xz_mm:[231,250],
   method:"Exact union swept AABB for each continuous purely axis-aligned translated rigid cuboid along all waypoints. Zero-clearance face touching permitted.",
   omitted_geometry:"Two front baffles replaced by nominal centered circle at entry; no actual Dayton driver basket, pads, wires, hardware, glue, human reach, rotations or fit tolerance.",
   absence_note:"36 lower lips omitted in staged variant ONLY as a hypothesis; physical post-insertion attachment is NOT designed."},
  sequences:{construct,nested_target_150_120_100:nested},
  results:{with_integral_lower_lips_isolated:isolatedWith.filter(x=>x.passed).length,
   with_lower_lips_omitted_isolated:isolatedWithout.filter(x=>x.passed).length,
   with_integral_lower_lips_constructed_before_failure:fixedSequence.passed,
   with_lower_lips_omitted_full_construction:stagedSequence.passed,
   reversed_exact_full_construction:reverse.passed,
   nested_150_to120_to100_before_failure:nestedSequence.passed,
   small_rear_one_by_one_extraction_from_full_box_state_passes:smallExtraction.filter(x=>x.passed).length,
   front_lateral_necessary_symmetric_clearance_mm:2,
   lateral_collision_test_nominal_plus_expansion_mm:lateralClearance},
  isolated_with_lips_blockers:isolatedWith.filter(v=>!v.passed).map(v=>({id:v.module,first_collision:v.first_collision})),
  construction_complete_nominal_routes:stagedSequence.all,
  inverse_construction_order_all_clear:reverse.complete,
  nested_order_failed_step:nestedSequence.first_failed,
  small_extraction_fixed_other_boxes:smallExtraction.map(v=>({id:v.module,passes:v.passed,first_collision:v.first_collision})),
  front_necessary_Y_corridor:{front_web_end_global_Y_mm:54,rear_large_rail_start_Y_mm:208,span_mm:154,module_depth_mm:150,max_symmetric_margin_mm:2,
   proof:"As box travels laterally in X, it overlaps B1 front web X448–470 and rear large rail X515.5–531.5 at some intermediate X. Both span its Z. Thus Ynear≥54 and Yfar≤208 for a 150mm depth; uniform margin≤2mm."},
  critical_unresolved:["The only mathematically complete 20-piece assembly omits 36 presently integral support lips; they need a new certifiable after-insertion fastening and tool access.",
   "A physically adjustable 150↔120↔100 set of permitted removal/reinsertion sequences is NOT demonstrated. Nested target order stalls after 12/20; tested four small rear removals fail with other boxes in place.",
   "Upper positive keeper joint, lower shelf support, temporarily missing full rail and segmented splice not structurally designed, measured or qualified.",
   "Front Y transport corridor maximum nominal symmetric clearance 2 mm, below prior hypothetical 6mm design screening; real tolerances not measured.",
   "No 6DOF motion, real basket, cables, user reach or structural response. K18 DXF are NOT released for CNC."]
 };
 const X=x=>26+(x-22)*1.065,Y=y=>98+(y-44)*.88;
 const path14=stagedSequence.all.find(x=>x.module===14).waypoints.filter(p=>p[1]>=44);
 const routePoints=path14.map(p=>`${X(p[0]).toFixed(2)},${Y(p[1]).toFixed(2)}`).join(" ");
 const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="520" viewBox="0 0 1140 520"><rect width="1140" height="520" fill="#fafbfc"/><text x="24" y="30" font-family="sans-serif" font-weight="bold" font-size="21" fill="#283a48">K23 — checked service path for one box (id 14), research only</text><text x="24" y="53" font-family="sans-serif" font-size="13" fill="#506575">XY plan projection of axis-aligned XYZ motion. Other stages and tools are not shown.</text>
<rect x="${X(22)}" y="${Y(44)}" width="${976*1.065}" height="${359*.88}" fill="#ecf2f4" stroke="#617584" stroke-width="2"/>
<rect x="${X(531.5)}" y="${Y(208)}" width="${259*1.065}" height="${28*.88}" fill="#97d6b9" fill-opacity=".9"/>
${rails.map(p=>`<rect x="${X(p.o[0])}" y="${Y(p.o[1])}" width="${p.s[0]*1.065}" height="${p.s[1]*.88}" fill="#b9524b"/>`).join("\n")}
${panels.filter(p=>p.id.endsWith("FRONT_WEB")||p.id.endsWith("REAR_WEB")).map(p=>`<rect x="${X(p.o[0])}" y="${Y(p.o[1])}" width="${p.s[0]*1.065}" height="${p.s[1]*.88}" fill="#53708c"/>`).join("\n")}
<polyline points="${routePoints}" fill="none" stroke="#167d64" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="${X(231)}" cy="${Y(44)}" r="6" fill="#e7ab42"/><circle cx="${X(596.5)}" cy="${Y(287)}" r="7" fill="#167d64"/>
<text x="25" y="454" font-family="sans-serif" font-weight="bold" font-size="14" fill="#9b3f37">Fixed lower lips: 12/20 isolated tested routes. Lips omitted: 20/20 exact nominal assembly order.</text>
<text x="25" y="481" font-family="sans-serif" font-size="13" fill="#4b6272">The required 150→120→100 nested volume-service sequence fails after 12 inserts; front corridor max margin is 2 mm.</text>
<text x="25" y="507" font-family="sans-serif" font-weight="bold" font-size="16" fill="#a3403c">NO proven reattachable load-bearing supports. NO CNC RELEASE.</text></svg>\n`;
 return {record,svg};
}
function main(){const root=path.resolve(__dirname,"..");const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));const o=buildK23(read("wyniki/k15_p30e_przed_CNC_zestawienie.json"),read("wyniki/k17_prowadnice_boczne_wkladow.json"),read("wyniki/k22_dzielona_szyna_przesmyk.json"));for(const [p,c]of [["wyniki/k23_swept_montaz_wkladow.json",JSON.stringify(o.record,null,2)+"\n"],["wyniki/k23_trasa_montazu_modulu_14_NIE_CNC.svg",o.svg]]){const file=path.join(root,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,c);}console.log(JSON.stringify({status:o.record.status,results:o.record.results}));}
if(require.main===module)main();module.exports={buildK23};
