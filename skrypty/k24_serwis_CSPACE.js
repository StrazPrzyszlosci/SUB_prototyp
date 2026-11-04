#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path');
function analyse(A,B,K23){
 if(A.module_positions.length!==20||B.spines.length!==12||K23.results.with_lower_lips_omitted_full_construction!==20)throw Error("upstream drift");
 const mods=A.module_positions;
 const gaps=[],stress=[];
 for(const m of mods){
  const below=mods.filter(q=>q.i!==m.i&&q.global_origin_xyz_mm[0]===m.global_origin_xyz_mm[0]&&q.global_origin_xyz_mm[1]===m.global_origin_xyz_mm[1]&&q.global_origin_xyz_mm[2]+q.dims_xyz_mm[2]<=m.global_origin_xyz_mm[2]).sort((a,b)=>b.global_origin_xyz_mm[2]-a.global_origin_xyz_mm[2]);
  const z=below.length?below[0].global_origin_xyz_mm[2]+below[0].dims_xyz_mm[2]:22;
  const gap=m.global_origin_xyz_mm[2]-z,remain=gap-4;
  gaps.push({module:m.i,gap_below_mm:gap,after_original_4mm_shelf_mm:remain,straight_14mm_tool_envelope_pass:remain>=14});
  const mass=A.parts.filter(q=>q.module_index===m.i).reduce((s,q)=>s+q.box_size_xyz_mm.reduce((a,b)=>a*b,1),0)*730/1e9;
  const shelf=B.contact_lips.find(q=>q.module_index===m.i&&q.position==="shelf");
  const spine=B.spines.find(q=>q.group===shelf.group&&q.o[0]===shelf.o[0]);
  const lever=shelf.o[1]+shelf.s[1]-spine.o[1]-spine.s[1];
  const force=(mass+.2)*5*9.81;
  stress.push({module:m.i,dry_shell_mass_kg:+mass.toFixed(6),single_support_force_with_extra_0_2kg_at_5g_N:+force.toFixed(6),old_tab_lever_mm:lever,ideal_4mm_root_stress_MPa:+(6*force*lever/256).toFixed(6)});
 }
 const bolt=B.spines.map(s=>({rail:s.id,y_depth_mm:s.s[1],trial_hole_d_mm:4.5,residual_edge_ligament_mm:+((s.s[1]-4.5)/2).toFixed(3),center_to_edge_mm:s.s[1]/2,passes_assumed_1_5d_rule:s.s[1]/2>=6.75}));
 function cspace(moving,retained,c){
  const m=mods[moving],h=m.dims_xyz_mm.map(x=>x/2);
  const bounds=[[22+h[0]+c,998-h[0]-c],[44+h[1]+c,353-h[1]-c],[22+h[2]+c,478-h[2]-c]];
  const obs=A.parts.filter(p=>p.module_index===-1&&p.id!=="FR1"&&p.id!=="FR2").map(p=>({o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm}))
   .concat(B.spines.filter(s=>s.id!=="G17_COLUMN_10").map(s=>({o:s.o,s:s.s})),[{o:[22,353,22],s:[976,50,456]}],
   mods.filter(t=>t.i!==moving&&retained.includes(t.i)).map(t=>({o:t.global_origin_xyz_mm,s:t.dims_xyz_mm})));
  const blocked=obs.map(o=>o.o.map((q,i)=>[q-h[i]-c,q+o.s[i]+h[i]+c]));
  const cuts=bounds.map(([lo,hi],i)=>{const a=[lo,hi];for(const b of blocked)for(const v of b[i])if(v>lo&&v<hi)a.push(v);a.sort((x,y)=>x-y);return a.filter((v,j)=>j===0||v-a[j-1]>1e-8);});
  const mid=cuts.map(a=>a.slice(0,-1).map((v,i)=>(v+a[i+1])/2)),size=mid.map(a=>a.length),n=size.reduce((a,b)=>a*b,1);
  const ix=(x,y,z)=>(z*size[1]+y)*size[0]+x,decode=id=>[id%size[0],Math.floor(id/size[0])%size[1],Math.floor(id/(size[0]*size[1]))];
  const free=new Uint8Array(n),seen=new Uint8Array(n),Q=new Int32Array(n);
  for(let z=0;z<size[2];z++)for(let y=0;y<size[1];y++)for(let x=0;x<size[0];x++){
   const p=[mid[0][x],mid[1][y],mid[2][z]];
   free[ix(x,y,z)]=blocked.some(b=>p.every((v,i)=>v>b[i][0]+1e-9&&v<b[i][1]-1e-9))?0:1;
  }
  const candidates=m.global_center_xyz_mm.map((v,i)=>cuts[i].slice(0,-1).map((lo,j)=>v>=lo-1e-9&&v<=cuts[i][j+1]+1e-9?j:-1).filter(x=>x>=0));
  let count=0;
  for(const x of candidates[0])for(const y of candidates[1])for(const z of candidates[2]){
   const p=ix(x,y,z);if(free[p]&&!seen[p]){seen[p]=1;Q[count++]=p;}
  }
  if(!count)return {module:moving,clearance_mm:c,status:"INVALID_START",cells:n};
  let goal=false,front=0,visited=0;
  for(let i=0;i<count;i++){
   const [x,y,z]=decode(Q[i]);visited++;
   if(y===0){
    front++;
    const fx=Math.max(Math.abs(mid[0][x]-h[0]-231),Math.abs(mid[0][x]+h[0]-231));
    const fz=Math.max(Math.abs(mid[2][z]-h[2]-250),Math.abs(mid[2][z]+h[2]-250));
    if(Math.hypot(fx,fz)+c<=177.9+1e-8){goal=true;break;}
   }
   for(const [dx,dy,dz]of [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]){
    const xx=x+dx,yy=y+dy,zz=z+dz;
    if(xx<0||yy<0||zz<0||xx>=size[0]||yy>=size[1]||zz>=size[2])continue;
    const p=ix(xx,yy,zz);if(free[p]&&!seen[p]){seen[p]=1;Q[count++]=p;}
   }
  }
  return {module:moving,clearance_mm:c,status:goal?"EXIT_CIRCLE":front?"FRONT_ONLY":"NO_FRONT_PATH",cells:n,visited,front_cells:front,grid:size};
 }
 const sets={full_100:mods.map(x=>x.i),retained_120:mods.filter(m=>m.i>=4&&m.i<=15).map(x=>x.i),
  only_four_small:[0,1,2,3],retained_120_without_12_14:mods.filter(m=>m.i>=4&&m.i<=15&&m.i!==12&&m.i!==14).map(x=>x.i)};
 const ctests=[];
 for(const c of [0,1,3])for(const [name,s]of Object.entries(sets))for(const id of [0,1,2,3])ctests.push({scenario:name,...cspace(id,s,c)});
 for(const t of ctests){
  const expected=["only_four_small","retained_120_without_12_14"].includes(t.scenario)?"EXIT_CIRCLE":"NO_FRONT_PATH";
  if(t.status!==expected)throw Error("Cspace validation changed "+JSON.stringify(t));
 }
 const combos=[];
 for(let small=0;small<=4;small++)for(let rear=0;rear<=8;rear++)for(let front=0;front<=8;front++){
  const step=180*small+252*rear+315*front;
  combos.push({small,rear,front,displacement_l:step/100,error_l:+((step-1980)/100).toFixed(2),abs_error_l:+(Math.abs(step-1980)/100).toFixed(2)});
 }
 combos.sort((x,y)=>x.abs_error_l-y.abs_error_l||x.small-y.small||(x.rear+x.front)-(y.rear+y.front));
 const exact=combos.filter(x=>x.abs_error_l===0),near=combos.filter(x=>x.small===0).slice(0,5);
 if(exact.length!==2||exact.some(x=>x.small!==4)||near[0].abs_error_l!==.27)throw Error("nominal volume drift");
 if(gaps.filter(x=>x.module>=4&&!x.straight_14mm_tool_envelope_pass).length!==16||bolt.some(x=>x.passes_assumed_1_5d_rule))throw Error("tool screen drift");
 return {study:"K24",date:"2026-11-04",release:"CNC_HOLD",kind:"Numerical screening, not validated hardware or physical 6DOF service",
  source:"K15 module/cabinet solids; K17 spines and lips; K23 nominal assembly",
  tool_access:{hypothetical_tool_diameter_mm:12,hypothetical_required_each_side_mm:1,reference_original_shelf_z_mm:4,
   gap_by_module:gaps,large_module_direct_below_access_failures:16,
   caution:"One straight Z tool approach only; remote/angled/side access not tested"},
  fastener_screen:{hypothetical_hole_d_mm:4.5,assumed_min_center_edge_factor:1.5,rail_geometry:bolt,rails_passing_assumed_rule:0,
   caution:"Screening heuristic, not MDF material design allowable or fastener qualification"},
  support_load:{assumed_density_kg_m3:730,hypothetical_additional_mass_per_box_kg:.2,hypothetical_inertial_g:5,
   hypothetical_one_surviving_support:true,original_4mm_MDF_section_reference_only:true,per_module:stress,
   strength_capacity_tested:false},
  cspace:{method:"Rectangular obstacle face configuration-space partition, open-free-cell 6-neighbor exhaustive BFS. Only rigid fixed XYZ orientation translations; zero-width passage and any 3D rotation untested.",
   absent_spine:"G17_COLUMN_10",intentionally_absent_shelves_and_keepers:true,
   rear_mat_limit_y_mm:353,clearances_screened_mm:[0,1,3],tests:ctests,
   caveat:"No genuine 6DOF rotation, hands, real driver basket, fasteners or motion under load verified."},
  nominal_step_combinatorics:{baseline_100_to120_l:19.8,external_modules_l:{small:1.8,rear:2.52,front:3.15},
   exact_solutions:exact,nearest_no_small:near,
   caveat:"Only ideal modular external displacement sums, no new mounts, hardware or measured acoustics"},
  engineering_decision:"Prior K18 profile DXFs not machinable; redesign serviceable volume carrier/locations or controlled access hatch, then 6DOF service and structural material qualification."
 };
}
function main(){const root=path.resolve(__dirname,'..');const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));const r=analyse(read('wyniki/k15_p30e_przed_CNC_zestawienie.json'),read('wyniki/k17_prowadnice_boczne_wkladow.json'),read('wyniki/k23_swept_montaz_wkladow.json'));fs.writeFileSync(path.join(root,'wyniki/k24_serwis_CSPACE_wyniki.json'),JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify({release:r.release,noExit120:r.cspace.tests.filter(x=>x.scenario==='retained_120'&&x.clearance_mm===1).map(x=>x.status)}));}
if(require.main===module)main();module.exports={analyse};
