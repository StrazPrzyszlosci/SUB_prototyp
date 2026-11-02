#!/usr/bin/env node
"use strict";
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const model=function model(){
 const widths=[980,1000,1020,1040],depths=[440,445,448,450,455],H=500,t=22,front=44,gap=2,cutout=284,outer=332,pcd=316,bolt=5.5;
 const large=[230,160,100],trim=[85,120,150];
 const B=(lo,hi,kind)=>({lo,hi,kind});
 const V=b=>b.lo.reduce((a,x,i)=>a*(b.hi[i]-x),1)/1e6;
 const intersection=(a,b)=>a.lo.map((x,i)=>Math.max(0,Math.min(a.hi[i],b.hi[i])-Math.max(a.lo[i],b.lo[i]))).reduce((a,b)=>a*b,1)/1e6;
 const touches=(a,b,pad=gap)=>a.lo.every((x,k)=>a.hi[k]+pad>b.lo[k]-pad&&b.hi[k]+pad>x-pad);
 const A=(c,sz,k)=>B(c.map((x,i)=>x-sz[i]/2),c.map((x,i)=>x+sz[i]/2),k);
 const S=(a,b,sz,k)=>B(a.map((x,i)=>Math.min(x,b[i])-sz[i]/2),a.map((x,i)=>Math.max(x,b[i])+sz[i]/2),k);
 const center=b=>b.lo.map((x,i)=>(x+b.hi[i])/2);
 const portal=sz=>Math.hypot(sz[0]/2+3,sz[2]/2+3)<=cutout/2;
 function run(W,D){
  const inner=B([t,front,t],[W-t,D-t,H-t],"inside"), bx=W/2;
  const brace=[
    B([bx-11,front,22],[bx+11,D-t,44],"brace-bottom"),
    B([bx-11,front,456],[bx+11,D-t,478],"brace-top"),
    B([bx-11,front,44],[bx+11,54,456],"brace-front"),
    B([bx-11,D-44,44],[bx+11,D-t,456],"brace-rear")];
  const mat=B([t,D-72,t],[W-t,D-t,H-t],"mat-envelope");
  const blockers=[...brace,mat],brace_l=brace.reduce((s,b)=>s+V(b),0),netMatEnvelope=V(mat)-brace.reduce((s,b)=>s+intersection(b,mat),0);
  const slots=[],fails=[],placed=[];let routes=0,trimRoutes=0;
  const bayWidth=W/2-33,canFitTwo=bayWidth>=2*large[0]+7+10;
  if(!canFitTwo)fails.push("too_narrow_for_2x230mm_columns_in_each_bay");
  else{
    const leftStarts=[27,264],rightStarts=leftStarts.map(a=>W-a-large[0]).sort((a,b)=>a-b);
    const zStarts=[31,143,255,367];
    for(const side of ["L","R"])for(const x of side==="L"?leftStarts:rightStarts)for(const z of zStarts)
      slots.push({side,bb:B([x,211,z],[x+large[0],371,z+large[2]],"large-module")});
    for(let k=0;k<slots.length;k++){
      const it=slots[k],cx=it.side==="L"?W/4:3*W/4,target=center(it.bb),stage=[cx,front+large[1]/2+3,250],
        steps=[stage,[target[0],stage[1],250],[target[0],stage[1],target[2]],target];
      let problem=null;
      if(!portal(large))problem="aperture";
      for(let s=0;s<steps.length&&!problem;s++){
        const env=s===0?A(stage,large,"stage"):S(steps[s-1],steps[s],large,"sweep");
        if(!env.lo.every((v,i)=>v>=inner.lo[i]+(i===1?2:0)-1e-8&&env.hi[i]<=inner.hi[i]-(i===1?2:0)+1e-8))problem="outside_inner_box";
        else {const hit=[...blockers,...placed].find(o=>touches(env,o));if(hit)problem="hit_"+hit.kind;}
      }
      if(problem)fails.push(`large_${k}_${problem}`);else {routes++;placed.push(it.bb);}
    }
  }
  const trimBoxes=[B([27,55,30],[112,175,180],"trim-L"),B([W-112,55,30],[W-27,175,180],"trim-R")];
  for(let k=0;k<2;k++){
    const target=center(trimBoxes[k]),cx=k===0?W/4:3*W/4,stage=[cx,front+trim[1]/2+3,250],
      steps=[stage,[target[0],stage[1],250],[target[0],stage[1],target[2]],target];
    let problem=!portal(trim)?"aperture":null;
    for(let s=0;s<steps.length&&!problem;s++){
      const env=s===0?A(stage,trim,"stage"):S(steps[s-1],steps[s],trim,"sweep");
      if(!env.lo.every((v,i)=>v>=inner.lo[i]-1e-8&&env.hi[i]<=inner.hi[i]+1e-8))problem="outside_inner_box";
      else{const hit=[...blockers,...placed,...trimBoxes.slice(0,k)].find(o=>touches(env,o));if(hit)problem="hit_"+hit.kind;}
    }
    if(problem)fails.push("trim_"+k+"_"+problem);else trimRoutes++;
  }
  const gross=V(inner),nominal=gross-10-brace_l-0.175-netMatEnvelope*20/1380;
  const minStress=gross-16-brace_l*1.05-.3-netMatEnvelope*30/1300;
  const maxStress=gross-4-brace_l*.95-.05-netMatEnvelope*10/1400;
  const nLarge=V(B([0,0,0],large,"dummy")),trimMax=2*V(B([0,0,0],trim,"dummy"));
  const targets=[150,120,100].map(target=>{
    const feasible=[];
    for(let n=0;n<=16;n++){let fine=nominal-n*nLarge-target;if(fine>=-1e-8&&fine<=trimMax+1e-8)feasible.push({n_large:n,fine_l:Math.max(0,fine)});}
    return{target_l:target,options:feasible};
  });
  const edge={side_mm:W/4-outer/2,top_mm:H/2-outer/2,between_flange_mm:W/2-outer,bolt_to_cutout_wood_mm:pcd/2-bolt/2-cutout/2};
  return{W,D,inside_mm:[W-44,D-66,H-44],gross_l:gross,brace_l,solid_mat_l:netMatEnvelope*20/1380,
    nominal_empty_l:nominal,stress_empty_l:[minStress,maxStress],slot_l:nLarge,max_fine_l:trimMax,
    routes,trim_routes:trimRoutes,fails,front:edge,
    geometrical_ok:routes===16&&trimRoutes===2&&fails.length===0,
    full_depth_range_mm:[D+29.5,D+49.5],full_depth_ok:D+49.5<=500,
    targets,step_data:{stage_y_mm:front+large[1]/2+3,slot_y_mm:[211,371],mat_y_mm:[D-72,D-22],mat_clearance_mm:D-72-371,
      driver_rear_assumed_mm:front+133,driver_to_modules_mm:211-front-133,center_x_mm:[W/4,3*W/4],
      bolt_pcd_mm:pcd,bolt_hole_mm:bolt,flange_od_mm:outer,cutout_mm:cutout},
    slots:slots.map(s=>({side:s.side,lo:s.bb.lo,hi:s.bb.hi})),trim_bays:trimBoxes.map(b=>({lo:b.lo,hi:b.hi}))};
 }
 const cases=[];for(const W of widths)for(const D of depths)cases.push(run(W,D));
 const chosen=cases.find(c=>c.W===1020&&c.D===450);
 const qualified=cases.filter(c=>c.geometrical_ok&&c.full_depth_ok&&c.targets.every(t=>t.options.length));
 if(!chosen.geometrical_ok||!chosen.full_depth_ok||!chosen.targets.every(t=>t.options.length))throw Error("Chosen check failed "+JSON.stringify({fails:chosen.fails,targets:chosen.targets}));
 if(chosen.front.bolt_to_cutout_wood_mm<10||chosen.step_data.mat_clearance_mm<4)throw Error("geometry gate");
 if(chosen.nominal_empty_l-chosen.targets.find(t=>t.target_l===100).options[0].n_large*chosen.slot_l-chosen.targets.find(t=>t.target_l===100).options[0].fine_l-100>1e-7)throw Error("Volume identity fail");
 return{schema:"B12-05-rectilinear-swept-3d-geometry-research",date:"2026-11-02",count:cases.length,
   chosen,qualified:qualified.map(c=>({W:c.W,D:c.D,net_l:c.nominal_empty_l,depth_worst:c.full_depth_range_mm[1]})),
   other_cases:cases.filter(c=>c!==chosen).map(c=>({W:c.W,D:c.D,geometry:c.geometrical_ok,depth_ok:c.full_depth_ok,base_l:c.nominal_empty_l,stress:c.stress_empty_l,
     targets:c.targets.map(t=>({l:t.target_l,feasible:t.options.length>0})),fails:c.fails.slice(0,2)})),
   parameters:{large_module_mm:large,trim_block_max_mm:trim,driver_reference:{model:"STX W.32.500.8.MC_v2",outer_mm:outer,cutout_mm:cutout,bolt_pcd_mm:pcd,bolt_hole_mm:bolt,depth_mm:133},
      outside_H_mm:500,front_mm:44,other_wall_mm:22,material:"MDF - no stiffness proof",rear_mat_envelope_mm:50,nominal_mat_solid_fraction:20/1380,
      total_depth_formula:"D + static_front(10-22) + catalog_xmax(7.5) + gap(5) + grille_deflection(2) + grille_skin(3) + rear(0-8) + tolerance(2)",
      effective_displacement_per_driver_scenarios_l:[2,5,8],bracing_volume_stress_fraction:.05,
      trim_and_module_models:"Not approved pieces; designed research geometry, not existing P20D parts"},
   limitations:["Full translation corridors are proven only for ideal AABBs with 2 mm collision allowance, both drivers removed during insertion, no hands/tools/wiring/fasteners modeled",
   "Motor cylinder is conservatively bounded by STX 284mm cutout and 133mm advertised total depth, not a measured body or cooling envelope",
   "Central 22mm window brace has 10mm front depth edge and is NOT strength/deflection/FEA validated",
   "Fine trim blocks are continuous-volume conceptual spacers with no approved locking, fitting, adhesive or sealing",
   "Nominal 100/120/150 L is not robust under the considered effective driver displacement range; need per-unit calibration and alternative module inventory",
   "Rear mat dry-fiber body volume approximate, porosity acoustical effects not included",
   "Full depth worst-case leaves only 0.5mm margin and projections are hypothetical; do not approve 500mm construction/CNC",
   "No real 3D speaker CAD, no measured driver displacement, no installation fixtures, no gravity load in 2 orientations, no cost or FEA test"]};
};
const root=path.resolve(__dirname,'..'),result=model();
assert.deepStrictEqual(result,JSON.parse(fs.readFileSync(path.join(root,'wyniki/b12_05_uklad_2x12_20261102.json'),'utf8')));
console.log('B12-05 PASS:',result.count,'3D geometry candidates, 16+2 swept paths, target-net nominal calculations');
