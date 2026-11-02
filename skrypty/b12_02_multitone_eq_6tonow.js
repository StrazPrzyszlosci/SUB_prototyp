#!/usr/bin/env node
"use strict";
// B12-02: ideal six-tone spectral equalization; theoretical upper bound, not DSP firmware.
const fs=require('fs'),path=require('path'),assert=require('assert');
function study(drivers) {
 const RHO=1.2041,C=343,P_REF=2e-5,PI=Math.PI,RT=Math.sqrt(2),F=[20,25,31.5,40,63,80],VB=[100,120,150],CAPS=[50,100],XFR=[.7,1];
 const shapes={balanced:[1,1,1,1,.8,.55],restrained20:[.5,.85,1,1,.8,.55],highpass25:[.25,.65,.9,1,.8,.55]};
 const phaseModes=["aligned_pressure","quadratic_pressure"];
 const dict=Object.fromEntries(drivers.map(d=>[d.id,d.model]));
 const z=(r=0,i=0)=>({r,i}),add=(a,b)=>z(a.r+b.r,a.i+b.i),mul=(a,b)=>z(a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r),sc=(a,s)=>z(a.r*s,a.i*s),divide=(a,b)=>sc(mul(a,z(b.r,-b.i)),1/(b.r*b.r+b.i*b.i)),mag=(a)=>Math.hypot(a.r,a.i),polar=(r,p)=>z(r*Math.cos(p),r*Math.sin(p)),rn=(n)=>Number(n.toFixed(6));
 const NS=4000,dt=.0005,osc=F.map(f=>Array.from({length:NS},(_,i)=>[Math.cos(2*PI*f*i*dt),Math.sin(2*PI*f*i*dt)]));
 function make(id,pert={}){
  const d=dict[id],fs=d.fs_hz*(pert.fs||1),vas=d.vas_l*(pert.vas||1),qes=d.qes*(pert.qes||1);
  const sd=d.sd_cm2*.0001,cms=vas*.001/(RHO*C*C*sd*sd),mms=1/((2*PI*fs)**2*cms),w=2*PI*fs,bl=Math.sqrt(w*mms*d.re_ohm/qes),rms=w*mms/d.qms;
  if(id==="C02")return{sd,cms,mms,bl,rms,re:d.re_ohm*(pert.re||1),le:d.le_mh*.001,xmax:d.xmax_mm*.001};
  return{sd:2*sd,cms:cms/2,mms:2*mms,bl,rms:2*rms,re:d.re_ohm/2*(pert.re||1),le:d.le_mh*.001/2,xmax:d.xmax_mm*.001};
 }
 function port(m,vb,f){
  const w=2*PI*f,k=1/m.cms+RHO*C*C*m.sd*m.sd/(vb*.001),zm=z(m.rms,w*m.mms-k/w);
  const Z=add(z(m.re,w*m.le),divide(z(m.bl*m.bl),zm));
  const i=divide(z(1),Z),v=divide(sc(i,m.bl),zm);
  return {i,disp:divide(v,z(0,w)),p:mul(v,z(0,RHO*w*m.sd/(2*PI)))};
 }
 function preset(id,vb,shape,ph){
  const m=make(id),ref=P_REF*10**(90/20);
  return F.map((f,i)=>divide(polar(ref*shapes[shape][i],ph==="aligned_pressure"?0:PI*i*(i-1)/F.length),port(m,vb,f).p));
 }
 function multi(m,vb,us,includePressure=false){
  const ip=[],xp=[],ps=[];let Vr2=0,Ir2=0;
  for(let k=0;k<F.length;k++){
   const t=port(m,vb,F[k]);const i=mul(t.i,us[k]),x=mul(t.disp,us[k]);
   ip.push(i);xp.push(x);ps.push(mag(mul(t.p,us[k])));
   Vr2+=mag(us[k])**2;Ir2+=mag(i)**2;
  }
  let vpk=0,ipk=0,xpk=0;
  for(let t=0;t<NS;t++){
   let v=0,i=0,x=0;
   for(let k=0;k<F.length;k++){
    const co=osc[k][t][0],si=osc[k][t][1];
    v+=us[k].r*co-us[k].i*si;
    i+=ip[k].r*co-ip[k].i*si;
    x+=xp[k].r*co-xp[k].i*si;
   }
   vpk=Math.max(vpk,Math.abs(v));ipk=Math.max(ipk,Math.abs(i));xpk=Math.max(xpk,Math.abs(x));
  }
  const r={v_rms:Math.sqrt(Vr2),i_rms:Math.sqrt(Ir2),v_peak:RT*vpk,i_peak:RT*ipk,x_peak_m:RT*xpk,pcu_w:Ir2*m.re};
  if(includePressure)r.pressure=ps;
  return r;
 }
 function cap(a,xmax,P,xf){
  const tests={voltage_peak:RT*40/a.v_peak,current_peak:RT*12/a.i_peak,voltage_rms:40/a.v_rms,current_rms:12/a.i_rms,excursion:xmax*xf/a.x_peak_m,copper:Math.sqrt(P/a.pcu_w)};
  const [limit,s]=Object.entries(tests).sort((a,b)=>a[1]-b[1])[0];
  if(!Number.isFinite(s)||s<=0)throw Error("invalid ceiling");
  return {db40:rn(90+20*Math.log10(s)),limit,gain:rn(s),actual_copper_w:rn(a.pcu_w*s*s),actual_x_mm:rn(a.x_peak_m*1000*s),actual_vpk:rn(a.v_peak*s),actual_ipk:rn(a.i_peak*s)};
 }
 const corners=[];
 for(const fs of [.92,1.08])for(const vas of [.88,1.12])for(const qes of [.9,1.1])for(const re of [1,1.4])corners.push({fs,vas,qes,re});
 const nominal=[],cornersResults=[];
 for(const id of ["C02","C05"])for(const vb of VB)for(const shape of Object.keys(shapes))for(const phase of phaseModes){
  const m=make(id),us=preset(id,vb,shape,phase),metrics=multi(m,vb,us);
  for(const pc of CAPS)for(const xf of XFR)nominal.push({id,vb_l:vb,shape,phase,pcu_budget_w:pc,xmax_fraction:xf,...cap(metrics,m.xmax,pc,xf)});
  if(vb===120&&shape==="balanced")for(const pc of CAPS)for(const xf of XFR){
   const norm=nominal.find(q=>q.id===id&&q.vb_l===vb&&q.shape===shape&&q.phase===phase&&q.pcu_budget_w===pc&&q.xmax_fraction===xf);
   let worst=Infinity,worstCorner=null,maxAbsCurveError=0;
   for(const perturb of corners){
    const adjusted=make(id,perturb),state=multi(adjusted,vb,us,true),c=cap(state,adjusted.xmax,pc,xf);
    if(c.db40<worst){worst=c.db40;worstCorner=perturb;}
    for(let i=0;i<F.length;i++)maxAbsCurveError=Math.max(maxAbsCurveError,Math.abs(20*Math.log10(state.pressure[i]/(P_REF*10**(90/20)*shapes[shape][i]))));
   }
   cornersResults.push({id,vb_l:120,shape,phase,pcu_budget_w:pc,xmax_fraction:xf,number_corners:corners.length,nominal_db40:norm.db40,worst_corner_db40:worst,difference_db:rn(worst-norm.db40),worst_corner:worstCorner,max_absolute_tonal_error_db:rn(maxAbsCurveError)});
  }
 }
 const select=(id,shape,phase,pc,xf)=>nominal.find(r=>r.id===id&&r.shape===shape&&r.phase===phase&&r.pcu_budget_w===pc&&r.xmax_fraction===xf&&r.vb_l===120);
 const compare=[];
 for(const sh of Object.keys(shapes))for(const ph of phaseModes)for(const pc of CAPS)for(const xf of XFR){
  const a=select("C02",sh,ph,pc,xf),b=select("C05",sh,ph,pc,xf);
  compare.push({shape:sh,phase:ph,pcu_budget_w:pc,xmax_fraction:xf,dayton_db40:a.db40,two_stx_db40:b.db40,dayton_advantage_db:rn(a.db40-b.db40),dayton_limit:a.limit,stx_limit:b.limit});
 }
 const gap=20*Math.log10(dict.C02.sd_cm2*dict.C02.xmax_mm/(2*dict.C05.sd_cm2*dict.C05.xmax_mm));
 const checks={nominal:nominal.length,robust_cases:cornersResults.length,robust_plant_evaluations:cornersResults.length*corners.length,analytic_vd_gap_db:rn(gap)};
 if(checks.nominal!==144||checks.robust_cases!==16||checks.robust_plant_evaluations!==256)throw Error("Count mismatch");
 for(const row of nominal){
  if(row.actual_copper_w>row.pcu_budget_w+1e-3 || row.actual_x_mm>dict[row.id].xmax_mm*row.xmax_fraction+1e-3 || row.actual_vpk>RT*40+1e-3 || row.actual_ipk>RT*12+1e-3)throw Error("limit violation "+JSON.stringify(row));
 }
 const key=compare.find(x=>x.shape==="balanced"&&x.phase==="aligned_pressure"&&x.pcu_budget_w===50&&x.xmax_fraction===1);
 if(Math.abs(key.dayton_advantage_db-gap)>1e-3)throw Error("Vd-invariance check failed");
 return {schema:"b12_02_six_tone_ideal_per_bin_eq",date:"2026-11-02",source_models:drivers.map(d=>d.id),purpose:"A common simultaneous six-tone acoustic target at ideal 2pi/1m, 40Hz per-tone reference 90dB at unit scale, then common scalar gain limited by simultaneous waveform peaks and total copper RMS power. Per-bin complex EQ is ideal, not implemented DSP.",configuration:{frequencies_hz:F,profiles:shapes,phases:phaseModes,net_volumes_l:VB,copper_budgets_w:CAPS,xmax_fractions:XFR,corner_parameters:corners,samples:4000,sample_rate_hz:2000,sample_duration_s:2,amplifier_max_vrms:40,amplifier_max_irms:12,peak_v_limit:RT*40,peak_i_limit:RT*12},checks,nominal,corner_stress:cornersResults,comparison_120l:compare,limitations:["Each nominal frequency bin has an arbitrary complex equalizer, so this is an optimistic spectral upper bound, not a released causal miniDSP preset","2s sampled waveform maxima can underestimate continuous-time intersample peaks; no limiter validated","BL(x), Cms(x), Le(x,f), measured THD, IMD, dynamic heat and in-room response are not evaluated","Copper budget 50/100 W is hypothetical for the whole subwoofer, not a manufacturer's continuous rating","Corner extremes vary Fs ±8%, Vas ±12%, Qes ±10%, Re 1/1.4 without manufacturer evidence, and are not probabilities","Both STX drivers assumed identical, synchronous and co-located acoustically; no physical box or manufacturing signoff"]};
}
const root=path.resolve(__dirname,'..');
const pool=JSON.parse(fs.readFileSync(path.join(root,'dane/przetworniki/pula_rozszerzona.json'),'utf8'));
const drivers=pool.drivers.filter(z=>['C02','C05'].includes(z.candidate_id)).map(z=>({id:z.candidate_id,name:z.model.name,model:z.model}));
const out=study(drivers);
assert.deepStrictEqual(out,JSON.parse(fs.readFileSync(path.join(root,'wyniki/b12_02_multitone_20261102.json'),'utf8')));
const fields=['shape','phase','pcu_budget_w','xmax_fraction','dayton_db40','two_stx_db40','dayton_advantage_db','dayton_limit','stx_limit'];
const csv=fields.join(',')+'\n'+out.comparison_120l.map(x=>fields.map(k=>x[k]).join(',')).join('\n')+'\n';
assert.strictEqual(csv,fs.readFileSync(path.join(root,'wyniki/b12_02_porownanie_120l.csv'),'utf8'));
console.log('B12-02 OK: '+out.checks.nominal+' nominal and '+out.checks.robust_plant_evaluations+' perturbed six-tone scenarios');
