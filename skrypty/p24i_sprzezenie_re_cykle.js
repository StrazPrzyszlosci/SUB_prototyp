#!/usr/bin/env node
"use strict";
// P24I: hypothetical frequency-dependent heating with Re(T) (Node >=18).
// Not a real amplifier, sensor, factory limit or speaker protection.
const fs=require("node:fs"),path=require("node:path");
const c={
  "date": "2026-10-31",
  "driver": "RSS390HF-4 nominal C02, 80 L",
  "Re0": 3,
  "alpha": 0.00393,
  "Le": 0.00092,
  "BL": 15,
  "Fs": 19.5,
  "Mms": 0.306,
  "Qms": 3.02,
  "Vas_m3": 0.212,
  "Sd_m2": 0.08296,
  "rho": 1.2,
  "sound": 343,
  "Vb_m3": 0.08,
  "Rs": 0.0026,
  "peak_x_guard_m": 0.0112,
  "amp_current_peak_A": 27,
  "dt_s": 0.2,
  "simulation_s": 3600,
  "diagnostic_stop_K": 200,
  "thermal": {
    "favorable": {
      "Cc": 90,
      "Rcm": 0.25,
      "Cm": 1500,
      "Rma": 0.8
    },
    "central": {
      "Cc": 40,
      "Rcm": 0.6,
      "Cm": 1000,
      "Rma": 1.5
    },
    "adverse": {
      "Cc": 20,
      "Rcm": 1.2,
      "Cm": 500,
      "Rma": 2.5
    }
  },
  "frequencies": [
    20,
    40,
    80
  ],
  "voltages": [
    10,
    20,
    30
  ],
  "periods": [
    10,
    30
  ],
  "duty": [
    0.1,
    0.25,
    0.5
  ]
};
function eParts(c,f){
 const w=2*Math.PI*f,sd=c.Sd_m2,cms=c.Vas_m3/(c.rho*c.sound*c.sound*sd*sd);
 const r=2*Math.PI*c.Fs*c.Mms/c.Qms;
 const x=w*c.Mms-1/(w*cms)-sd*sd*c.rho*c.sound*c.sound/(w*c.Vb_m3);
 const mr=c.BL*c.BL*r/(r*r+x*x),mi=-c.BL*c.BL*x/(r*r+x*x);
 const a=c.Rs+mr,b=w*c.Le+mi;
 return {w,motorR:r,motorX:x,zRealOther:a,zImagOther:b,zOtherMag:Math.hypot(a,b),
    motorMag:Math.hypot(r,x)};
}
function copper(c,e,temp,uMax){
 const re=c.Re0*(1+c.alpha*temp),zr=re+e.zRealOther,zi=e.zImagOther;
 const iPer=1/Math.hypot(zr,zi),xPer=Math.SQRT2*c.BL*iPer/(e.motorMag*e.w);
 const u=Math.min(uMax,c.amp_current_peak_A/(Math.SQRT2*iPer),c.peak_x_guard_m/xPer);
 if(zr<re||u<0||!Number.isFinite(u))throw Error("nonpassive/invalid circuit");
 return {P:re*(iPer*u)**2,peak_mm:u*xPer*1000};
}
function overlap(t,dt,period,duty){
 const on=period*duty;
 const integral=(x)=>{const n=Math.floor(x/period),z=x-n*period;return n*on+Math.min(on,z);};
 return Math.max(0,Math.min(1,(integral(t+dt)-integral(t))/dt));
}
function update(x,heat,p,dt){
 const [tc,tm]=x;
 const a=tc+dt*(heat-(tc-tm)/p.Rcm)/p.Cc;
 const b=tm+dt*((tc-tm)/p.Rcm-tm/p.Rma)/p.Cm;
 if(a<-1e-8||b<-1e-8||!Number.isFinite(a))throw Error("thermal positivity");
 return [a,b];
}
function one(c,name,f,u,period,duty,dt=c.dt_s){
 const th=c.thermal[name],el=eParts(c,f),cold=copper(c,el,0,u);
 let hot=[0,0],constant=[0,0],peakHot=0,peakConst=0,energyHot=0,energyConst=0,active=0,maxX=0,stop=null;
 for(let k=0;k<Math.round(c.simulation_s/dt);k++){
  const t=k*dt, frac=overlap(t,dt,period,duty);
  const heated=frac>0?copper(c,el,hot[0],u):{P:0,peak_mm:0};
  const p=heated.P*frac,pcold=cold.P*frac;
  hot=update(hot,p,th,dt);constant=update(constant,pcold,th,dt);
  peakHot=Math.max(peakHot,hot[0]);peakConst=Math.max(peakConst,constant[0]);
  energyHot+=p*dt;energyConst+=pcold*dt;active+=frac*dt;maxX=Math.max(maxX,heated.peak_mm);
  if(peakHot>=c.diagnostic_stop_K||peakConst>=c.diagnostic_stop_K){stop=+(t+dt).toFixed(3);break;}
 }
 return {thermal:name,freq_hz:f,input_vrms:u,period_s:period,duty,
  simulated_duration_s:stop??c.simulation_s,stopped_at_diagnostic_200K:stop!==null,
  peak_T_dynamic_K:+peakHot.toFixed(5),peak_T_constant_coldP_K:+peakConst.toFixed(5),
  peak_dynamic_minus_constant_K:+(peakHot-peakConst).toFixed(5),
  final_T_dynamic_K:+hot[0].toFixed(5),final_T_constant_K:+constant[0].toFixed(5),
  energy_dynamic_J:+energyHot.toFixed(2),energy_constant_J:+energyConst.toFixed(2),
  copper_power_cold_W:+cold.P.toFixed(4),effective_on_s:+active.toFixed(3),
  max_model_peak_x_mm:+maxX.toFixed(3)};
}
function run(c){
 const rows=[];
 for(const name of Object.keys(c.thermal))for(const f of c.frequencies)for(const u of c.voltages)
 for(const per of c.periods)for(const duty of c.duty)rows.push(one(c,name,f,u,per,duty));
 if(rows.length!==162||rows.some(x=>x.max_model_peak_x_mm>11.200001))throw Error("grid/ideal X");
 const byFreq={};
 for(const f of c.frequencies){
  const v=rows.filter(x=>x.freq_hz===f);
  byFreq[f]={cases:v.length,positive:v.filter(x=>x.peak_dynamic_minus_constant_K>.01).length,
   negative:v.filter(x=>x.peak_dynamic_minus_constant_K<-.01).length,
   largest_increase_K:Math.max(...v.map(x=>x.peak_dynamic_minus_constant_K)),
   largest_decrease_K:Math.min(...v.map(x=>x.peak_dynamic_minus_constant_K)),
   truncated:v.filter(x=>x.stopped_at_diagnostic_200K).length,
   cold_other_impedance_ohm:+eParts(c,f).zOtherMag.toFixed(4),
   initial_dP_dRe_sign_at_unlimited_voltage:eParts(c,f).zOtherMag>c.Re0?"positive":"negative"};
 }
 const tests=[
  ["favorable",20,30,30,.1],
  ["central",80,20,10,.5],
  ["adverse",40,20,30,.25]
 ].map(args=>{
  const coarse=one(c,...args,.2),fine=one(c,...args,.1);
  return {scenario:args,diff_peak_K:+(coarse.peak_T_dynamic_K-fine.peak_T_dynamic_K).toFixed(5),
   coarse_duration_s:coarse.simulated_duration_s,fine_duration_s:fine.simulated_duration_s};
 });
 if(tests.some(x=>Math.abs(x.diff_peak_K)>.5))throw Error("step test exceeds 0.5K "+JSON.stringify(tests));
 const selected=rows.filter(x=>x.thermal==="central"&&x.input_vrms===20&&x.period_s===30&&x.duty===.25);
 if(selected.length!==3)throw Error("not selected");
 // Pulse integral must produce exactly 25% on-time over whole numbers of cycles.
 if(selected.some(x=>Math.abs(x.effective_on_s-900)>.0001))throw Error("incorrect pulse overlap "+JSON.stringify(selected));
 return {study:"P24I",status:"hypothetical time-dependent Re(T) frequency comparison",base:"7bd8760fb4213b25836fe4d648172cdbdc08e37a",
    parameters:c,scenarios:rows.length,stopped_at_200K:rows.filter(x=>x.stopped_at_diagnostic_200K).length,
    frequency_summary:byFreq,step_halving_tests:tests,selected_20V_period30_duty25: selected,
    methodology:["Analytical sensitivity d(Pcu)/d(Re) at fixed terminal U is proportional to |Zother|^2-Re^2, before current/X limits.","Pulse overlap integrated exactly within dt; ensures equal nominal duty and avoids phase-boundary aliasing.",
     "Two parallel Euler Cauer states are driven by Pcu(T) or constant cold Pcu under same command and same simulation duration, with comparison truncated if either reaches 200K."],
    warnings:["No measured thermal parameters, no calibrated U/I or real voltage/current waveforms.","Model 200K termination is an extrapolation limit, not failure physics.",
    "Ideal X peak/current envelopes have not been implemented/validated in miniDSP.","No true music spectra, power-compression changes to BL/Cms/Le, dynamic class-D thermal foldback."] ,rows};
}
if(require.main===module){
 const o=run(c),p=path.join(__dirname,"..","wyniki","p24i_sprzezenie_re_cykle_20261031.json");
 fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(o,null,2)+"\n");
 console.log(JSON.stringify({scenarios:o.scenarios,frequency_summary:o.frequency_summary,
  selected:o.selected_20V_period30_duty25,tests:o.step_halving_tests},null,2));
}
module.exports={c,eParts,copper,overlap,update,one,run};
