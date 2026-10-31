#!/usr/bin/env node
"use strict";
// P36B: 972 ideal sealed-box transfer evaluations, 3 driver variants.
// Source: published T/S in dane/przetworniki/pula_rozszerzona.json.
const fs=require('node:fs'),path=require('node:path');
const drivers=[
  {
    "id": "C02",
    "name": "Dayton RSS390HF-4",
    "fs_hz": 19.5,
    "qes": 0.5,
    "qms": 3.02,
    "vas_l": 212
  },
  {
    "id": "C06",
    "name": "STX W.32.800.8.FCX",
    "fs_hz": 24,
    "qes": 0.45,
    "qms": 3.34,
    "vas_l": 96
  },
  {
    "id": "C08",
    "name": "STX W.38.800.8.MC",
    "fs_hz": 28,
    "qes": 0.27,
    "qms": 3.71,
    "vas_l": 247
  }
];
function response(d,V,extra){
 const Qts=d.qes*d.qms/(d.qes+d.qms), Veff=V+extra;
 const factor=Math.sqrt(1+d.vas_l/Veff),fc=d.fs_hz*factor,qtc=Qts*factor;
 const A=1/qtc**2-2,y=(A+Math.sqrt(A*A+4))/2,f3=fc*Math.sqrt(y);
 function gain(f){let x=f/fc;return 20*Math.log10((x*x)/Math.sqrt((1-x*x)**2+(x/qtc)**2))}
 return {V_eff_l:Veff,Qts,fc_hz:fc,Qtc:qtc,f3_hz:f3,
 gain25_db:gain(25),gain35_db:gain(35),gain50_db:gain(50),
 extra_l_equiv:extra};
}
function main(){
 const source=JSON.parse(fs.readFileSync(path.join(__dirname,'..','wyniki','p36a_podatnosc_MDF_324_20261031.json'),'utf8')).rows;
 if(source.length!==324)throw Error('P36A missing');
 const rows=[];
 for(const x of source)for(const d of drivers){
  const rigid=response(d,x.target_l,0),soft=response(d,x.target_l,x.equivalent_stiffness_volume_l);
  rows.push({id:d.id,name:d.name,volume_l:x.target_l,wall_mm:x.thickness_mm,
   E_GPa:x.E_GPa,rho_kgm3:x.rho_kgm3,brace_support:x.support,rigid_case:rigid,
   elastic_static_equivalent:soft,one_way_80Hz_bias_DIAGNOSTIC:response(d,x.target_l,x.one_way_80Hz_equivalent_l),
   delta_f3_hz:soft.f3_hz-rigid.f3_hz,delta_fc_hz:soft.fc_hz-rigid.fc_hz,delta_qtc:soft.Qtc-rigid.Qtc});
 }
 if(rows.length!==972)throw Error('Wrong number of cases');
 const x={study:"P36B",date:"2026-10-31",status:"LINEAR SMALL-SIGNAL BOX MODEL ONLY",drivers,cases:rows.length,
  rows,caveats:["Effective volume = physical V+static panel volume-equivalent from simply supported Kirchhoff SSSS approximation; not a real volume change.","This approximation ignores panel dynamic mode resonance, its radiated sound, acoustic leakage and pressure-induced nonlinear distortion.","P35A 80Hz face-weighted result is only a static load sensitivity diagnostic, not a true frequency-dependent F3.","The P36A intact front model ignores cut-out; idealized two-line braces may dramatically exaggerate stiffness gains.","Drivers use published T/S from repository, not verified specimen measurements. No current amp DSP costs, efficiency, max SPL or THD.","Do not judge driver sound quality solely from F3 or Qtc."]};
 const p=path.join(__dirname,'..','wyniki','p36b_trzy_glosniki_972_20261031.json');
 fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
 console.log(JSON.stringify({cases:rows.length,reference:rows.filter(x=>x.volume_l===120&&x.wall_mm===22&&x.E_GPa===2.1&&x.rho_kgm3===730)},null,2));
}
if(require.main===module)main();
module.exports={drivers,response,main};
