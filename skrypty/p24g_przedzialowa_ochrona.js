#!/usr/bin/env node
"use strict";
// P24G reproducible numerical experiment; requires Node >=18, no dependencies.
// Assumed Cauer model, fixed RMS terminal drive, ideal Xpk control, synthetic current.
// DO NOT treat any temperature or displacement threshold as validated.
const fs=require("node:fs"),path=require("node:path");
const cfg={
  "date": "2026-10-31",
  "dt_s": 0.05,
  "duration_s": 120,
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
  "bounds": {
    "Cc": [
      20,
      90
    ],
    "Rcm": [
      0.25,
      1.2
    ],
    "Cm": [
      500,
      1500
    ],
    "Rma": [
      0.8,
      2.5
    ],
    "Re0": [
      2.7,
      3.3
    ],
    "alpha": [
      0.0037,
      0.0042
    ],
    "valid_current_gain": [
      0.95,
      1.05
    ]
  },
  "frequencies_hz": [
    20,
    40,
    80
  ],
  "sensor_modes": [
    "nominal",
    "current_under_5pct",
    "dropout_20_45s",
    "missing_from_start",
    "current_under_30pct_OUTSIDE_ASSUMPTIONS"
  ],
  "policies": [
    "naive_temperature_55K",
    "interval_current_35K",
    "interval_voltage_35K"
  ],
  "actuator_delay_s": 0.25,
  "timeout_s": 1
};
function transfer(freq,T){
 const w=2*Math.PI*freq,sd=.08296,rho=1.2,c=343,mms=.306,bl=15,re=3*(1+.00393*T),le=.00092;
 const cms=.212/(rho*c*c*sd*sd),r=2*Math.PI*19.5*mms/3.02;
 const x=w*mms-1/(w*cms)-sd*sd*rho*c*c/(w*.080);
 const denom=r*r+x*x, zr=re+.0026+bl*bl*r/denom,zi=w*le-bl*bl*x/denom;
 if(zr<re)throw Error("passivity failed");
 const iper=1/Math.hypot(zr,zi),xpk_per=Math.SQRT2*bl*iper/(Math.hypot(r,x)*w);
 return {re,iper,xpk_per};
}
function envelopeStep(uc,um,power,dt,b){
 let nc=-Infinity,nm=-Infinity;
 for(const Cc of b.Cc)for(const Rcm of b.Rcm)nc=Math.max(nc,uc+dt*(power-(uc-um)/Rcm)/Cc);
 for(const Cm of b.Cm)for(const Rcm of b.Rcm)for(const Rma of b.Rma)
  nm=Math.max(nm,um+dt*((uc-um)/Rcm-um/Rma)/Cm);
 return [Math.max(0,nc),Math.max(0,nm)];
}
function simulate(cfg,thermalId,f,mode,policy){
 const p=cfg.thermal[thermalId],b=cfg.bounds,dt=cfg.dt_s;
 let tc=0,tm=0,uc=0,um=0,heatBound=0,lastGood=mode==="missing_from_start"?-Infinity:0;
 let trip=null,mute=null,latched=false,sensorFault=false,maxT=0,maxUpper=0,maxX=0,secondsOver80=0,onSteps=0,pViol=0,enclViol=0;
 for(let k=0;k<Math.round(cfg.duration_s/dt);k++){
  const t=k*dt,valid=mode!=="missing_from_start"&&!(mode==="dropout_20_45s"&&t>=20&&t<45);
  if(valid)lastGood=t;
  const stale=t-lastGood>=cfg.timeout_s-1e-10;
  const tempUpper=Math.min(uc,heatBound/b.Cc[0]);
  if(stale)sensorFault=true;
  if(trip===null){
   if(stale)trip=t;
   else if(policy==="naive_temperature_55K"&&valid&&tc-20>=55)trip=t;
   else if(policy!=="naive_temperature_55K"&&tempUpper>=35)trip=t;
  }
  if(trip!==null&&t>=trip+cfg.actuator_delay_s-1e-10){latched=true;if(mute===null)mute=t;}
  const e=transfer(f,tc),cap=Math.min(4*Math.pow(10,25.5/20),Math.sqrt(4*500));
  const u=latched?0:Math.min(cap,27/(Math.SQRT2*e.iper),.0112/e.xpk_per);
  const i=u*e.iper,pcu=e.re*i*i;
  let indicated=i;
  if(mode==="current_under_5pct")indicated*=.95;
  if(mode==="current_under_30pct_OUTSIDE_ASSUMPTIONS")indicated*=.7;
  const voltBound=u*u/b.Re0[0];
  const curBound=valid?(indicated/b.valid_current_gain[0])**2*b.Re0[1]*(1+b.alpha[1]*uc):Infinity;
  const pUpper=policy==="interval_current_35K"?Math.min(voltBound,curBound):voltBound;
  if(pcu>pUpper+1e-7)pViol++;
  const ntc=tc+dt*(pcu-(tc-tm)/p.Rcm)/p.Cc;
  const ntm=tm+dt*((tc-tm)/p.Rcm-tm/p.Rma)/p.Cm;
  if(ntc<-1e-9||ntm<-1e-9)throw Error("positivity");
  [uc,um]=envelopeStep(uc,um,pUpper,dt,b);
  heatBound+=dt*pUpper;tc=ntc;tm=ntm;
  const ub=Math.min(uc,heatBound/b.Cc[0]);
  if(tc>ub+1e-7||tm>um+1e-7)enclViol++;
  maxT=Math.max(maxT,tc);maxUpper=Math.max(maxUpper,ub);maxX=Math.max(maxX,u*e.xpk_per*1000);
  if(tc>80+1e-8)secondsOver80+=dt;
  if(!latched)onSteps++;
  if(tc>=200)break;
 }
 return {thermal:thermalId,freq_hz:f,sensor_mode:mode,policy,
 model_violates_sensor_assumption:mode.includes("OUTSIDE"),
 max_true_coil_rise_K:+maxT.toFixed(4),max_calculated_upper_K:+maxUpper.toFixed(4),
 upper_enclosure_violations:enclViol,power_upper_violations:pViol,
 seconds_above_diagnostic_80K:+secondsOver80.toFixed(2),
 on_seconds:+(onSteps*dt).toFixed(2),first_trip_s:trip,first_mute_s:mute,
 fault_latched:sensorFault,max_peak_displacement_mm:+maxX.toFixed(3)};
}
function runAll(cfg){
 if(cfg.dt_s>=cfg.bounds.Cc[0]*cfg.bounds.Rcm[0])throw Error("nonmonotone coil");
 if(cfg.dt_s>=cfg.bounds.Cm[0]/(1/cfg.bounds.Rcm[0]+1/cfg.bounds.Rma[0]))throw Error("nonmonotone motor");
 const rows=[];
 for(const t of Object.keys(cfg.thermal))for(const f of cfg.frequencies_hz)for(const mode of cfg.sensor_modes)
  for(const pol of cfg.policies)rows.push(simulate(cfg,t,f,mode,pol));
 const inside=rows.filter(r=>!r.model_violates_sensor_assumption);
 if(rows.length!==135||inside.length!==108)throw Error("scenario count");
 if(inside.some(r=>r.upper_enclosure_violations||r.power_upper_violations))throw Error("invalid enclosure for calibrated range");
 if(rows.some(r=>r.max_peak_displacement_mm>11.200001))throw Error("model mechanical peak");
 const stats={};
 for(const pol of cfg.policies){
  const v=inside.filter(r=>r.policy===pol);
  stats[pol]={n:v.length,exceed80:v.filter(r=>r.seconds_above_diagnostic_80K>0).length,
    max_true_coil_K:Math.max(...v.map(x=>x.max_true_coil_rise_K)),
    mean_active_s:+(v.reduce((a,x)=>a+x.on_seconds,0)/v.length).toFixed(2),
    max_upper_K:Math.max(...v.map(x=>x.max_calculated_upper_K))};
 }
 return {study:"P24G",status:"ONLY CONDITIONAL DISCRETE MODEL EVIDENCE",base_commit:"fde7d244b449762af0869321487335148b8e221a",
  cfg,scenarios:rows.length,within_assumptions:inside.length,
  valid_enclosure_failures:inside.filter(r=>r.upper_enclosure_violations).length,
  valid_power_bound_failures:inside.filter(r=>r.power_upper_violations).length,
  outside_assumptions_enclosure_failures:rows.filter(r=>r.model_violates_sensor_assumption&&r.upper_enclosure_violations).length,
  stats,rows};
}
if(require.main===module){
 const data=runAll(cfg),file=path.join(__dirname,"..","wyniki","p24g_przedzialowa_ochrona_20261031.json");
 fs.mkdirSync(path.dirname(file),{recursive:true});
 fs.writeFileSync(file,JSON.stringify(data,null,2)+"\n");
 console.log(JSON.stringify({scenarios:data.scenarios,within_assumptions:data.within_assumptions,
 stats:data.stats,valid_enclosure_failures:data.valid_enclosure_failures,
 outside_assumptions_enclosure_failures:data.outside_assumptions_enclosure_failures},null,2));
}
module.exports={cfg,transfer,envelopeStep,simulate,runAll};
