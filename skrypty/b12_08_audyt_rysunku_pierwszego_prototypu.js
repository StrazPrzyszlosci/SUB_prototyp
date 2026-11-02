#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const calculate=function calculate(){
 const R=x=>Number(x.toFixed(5)),mm=[];
 for(let x=225;x<=255;x++)for(let od of [392,400,408])for(let id of [356,357.8,358,360])for(let hole of [5.5,6.5])for(let err of [0,1,2]){
  const wall=x-od/2-22,brace=448-x-od/2,vertical=250-od/2-22,gap=(id-355.8)/2,web=184-hole/2-id/2,outerWeb=od/2-184-hole/2;
  const position=Math.min(wall,brace)-err>=10&&vertical>=10,radial=gap>=1-1e-8&&web>=2-1e-8&&outerWeb>=2-1e-8;
  mm.push({x,od,id,hole,err,wall:R(wall),brace:R(brace),vertical:R(vertical),gap:R(gap),innerWeb:R(web),outerWeb:R(outerWeb),position,radial,pass:position&&radial});
 }
 const pick=(x,od,id,hole,err)=>mm.find(q=>q.x===x&&q.od===od&&q.id===id&&q.hole===hole&&q.err===err);
 const dd=[];
 for(let body of [420,425,430,435,440])for(let front of [30,40,50,60])for(let rear of [0,10,20,30])for(let error of [0,5]){
  const full=body+front+rear+error;
  dd.push({body,front,rear,error,full,margin:500-full,nominalOk:full<=500,screen10mm:front>=31.5&&full<=490});
 }
 const Fs=19.5,Vas=212,Qts=1/(1/.5+1/3.02);
 function sealed(V,v=Vas,q=Qts){
  const fc=Fs*Math.sqrt(1+v/V),Qtc=q*Math.sqrt(1+v/V),bb=2-1/(Qtc*Qtc),y=(-bb+Math.sqrt(bb*bb+4))/2;
  const db=f=>{let s=f/fc;return 20*Math.log10(s*s/Math.sqrt((s*s-1)**2+(s/Qtc)**2));};
  return {Qtc:R(Qtc),fcHz:R(fc),F3Hz:R(fc*Math.sqrt(y)),dB20:R(db(20)),dB40:R(db(40))};
 }
 const vol=[{target:100,nominal:100.119,min:94.22,max:106,blocks:"16 large + 4 small"},
 {target:120,nominal:119.919,min:114.25,max:125.57,blocks:"12 large"},
 {target:150,nominal:150.159,min:144.83,max:155.48,blocks:"1 large"}].map(o=>{
  const tests=[];for(let V of [o.min,o.nominal,o.max])for(let vas of [190,212,234])for(let qts of [.38,.43,.48])tests.push(sealed(V,vas,qts));
  const range=k=>[R(Math.min(...tests.map(z=>z[k]))),R(Math.max(...tests.map(z=>z[k])))];
  return {...o,nominalAlignment:sealed(o.nominal),sensitivityRanges:{Qtc:range("Qtc"),F3Hz:range("F3Hz"),dB20:range("dB20")},cases:tests.length};
 });
 const eligible=mm.filter(z=>z.pass);
 if(mm.length!==2232||eligible.some(z=>z.hole===6.5)||dd.length!==160||vol.length!==3)throw Error("model counts/logic");
 return{schema:"B12_08_C02_first_prototype_geometry_study",date:"2026-11-02",
 controls:{chassis_WDH_mm:[1020,425,500],front_MDF_mm:44,other_MDF_mm:22,cutout_mm:355.8,flange_OD_mm:388.4,bolt_pcd_mm:368,basket_hole_mm:6.5,legacy_x_mm:231,source_brace_x_mm:448,room_xyz_m:[3.7,4.6,2.5]},
 mounting:{n:2232,passed:eligible.length,passed_basket_hole_6_5:0,passed_hypothetical_hole_5_5:eligible.length,thresholds:{side_brace_mm:10,ID_cutout_radial_mm:1,metal_web_inner_mm:2,axis_uncertainty_mm:[0,1,2]},range:{x:[225,255,1],OD:[392,400,408],ID:[356,357.8,358,360],hole:[5.5,6.5]},
  example_at_old_x:pick(231,400,356,6.5,2),example_unqualified_fastener:pick(235,392,358,5.5,2),example_6_5:pick(235,400,358,6.5,2),
  geometry_proof:"For 6.5mm rear ring fastener through-hole, radial gap>=1mm forces ID>=357.8mm while inner web>=2mm forces ID<=357.5mm, so no such simple concentric annulus satisfies both ASSUMED thresholds.",
  warning:"Basket flange hole Ø6.5mm does not dictate the bolt or hole Ø of an independently designed load carrier. The 5.5mm alternative is hypothetical and NOT approved; XZ obstacles are projected, not 3D structural validation."},
 depth:{n:160,front_budget_min_assumed_mm:31.5,design_reserve_mm:10,all:dd,
  D425_worst5:dd.filter(q=>q.body===425&&q.error===5),
  status:"The aggregate P30E 56mm projection estimate is not added again; front/rear/tolerance are total, alternative assumptions. Grille and rear connector are unverified."},
 net:{nominal_Qts:R(Qts),Fs_hz:Fs,Vas_l:Vas,scenarios:vol,sensitivity_cases:81,source:"P30E 1020×425×500mm after 50mm rear polyester, modules 100/120/150l. Vas190/212/234 and Qts 0.38/0.43/0.48 are hypothetical.",model:"ideal sealed 2nd order, no room, damping losses, DSP or THD"},
 room:{two_width_1020mm_m:2.04,front_wall_m:3.7,remaining_front_wall_m:1.66,monitor_clearances_unmeasured:true},
 conclusion:{selected:"C02 Dayton RSS390HF-4 remains provisional first prototype; B12-08 examines 1020×425×500mm body / nominal 119.919l sealed (12 large modules) and 100/150l settings",
 mounting_gate:"STOP. Ring alone cannot be certified; need true basket geometry and tested path 8 bolts -> carrier/frame -> front/brace + leakage and real tool access.",
 candidates:"C11 RSS390HE-22 thermal countercandidate, C06 STX W.32.800.8.FCX 12in; 2x C05 per sub is a cost-only alternative not baseline",
 limitations:["AABB/projected x margins do not prove clearance from baskets, tools or wires","No measured mounting joint stiffness/preload/pullout/shear/fatigue","No verified full grille/terminal and nominal 19mm P30E margin is conditional","Volume extremes are arbitrary model perturbations, not production tolerance","No measured THD/IMD, compression, coil cooling or distortion spectra","No exact placed cabinets+monitors in listening room"],
 CNC:"BLOCKED",purchase:"BLOCKED"}};
};
const root=path.resolve(__dirname,'..'),data=calculate();
const expected=JSON.parse(fs.readFileSync(path.join(root,'wyniki/b12_08_audyt_konstrukcji_pierwszego_prototypu.json'),'utf8'));
assert.deepStrictEqual(data,expected);
assert.equal(data.mounting.passed_basket_hole_6_5,0);
assert.equal(data.net.scenarios[1].nominalAlignment.F3Hz,32.14568);
console.log('B12-08 OK',data.mounting.n,'mount screens',data.depth.n,'depth screens',data.net.sensitivity_cases,'acoustic stress cases');
