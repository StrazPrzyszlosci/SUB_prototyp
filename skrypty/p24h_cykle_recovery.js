#!/usr/bin/env node
"use strict";
// Research P24H: analytical Cauer periodic heating, hypothetical parameters.
// Requires Node.js 18+. Temperatures are NOT safety limits.
const fs=require("node:fs"),path=require("node:path");
const c={
  "date": "2026-10-31",
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
  "periods": [
    2,
    10,
    30,
    120
  ],
  "duty": [
    0.05,
    0.1,
    0.25,
    0.5,
    1
  ],
  "diagnostic_K": 80,
  "rest_marker_K": 20,
  "burst_W_copper": 200,
  "burst_s": 30
};
function expA(t,p){
 const a=-1/(p.Cc*p.Rcm),b=1/(p.Cc*p.Rcm),d=-(1/p.Rcm+1/p.Rma)/p.Cm,q=1/(p.Cm*p.Rcm);
 const h=Math.sqrt((a-d)**2+4*b*q),u=(a+d+h)/2,v=(a+d-h)/2,eu=Math.exp(u*t),ev=Math.exp(v*t);
 if(u>=0||v>=0)throw Error("unstable");
 return [[(eu*(a-v)-ev*(a-u))/h,b*(eu-ev)/h],[q*(eu-ev)/h,(eu*(d-v)-ev*(d-u))/h]];
}
function mvec(A,x){return [A[0][0]*x[0]+A[0][1]*x[1],A[1][0]*x[0]+A[1][1]*x[1]];}
function mult(A,B){return [[A[0][0]*B[0][0]+A[0][1]*B[1][0],A[0][0]*B[0][1]+A[0][1]*B[1][1]],[A[1][0]*B[0][0]+A[1][1]*B[1][0],A[1][0]*B[0][1]+A[1][1]*B[1][1]]];}
function solve(A,y){const d=A[0][0]*A[1][1]-A[0][1]*A[1][0]; if(Math.abs(d)<1e-14)throw Error("singular");return [(A[1][1]*y[0]-A[0][1]*y[1])/d,(-A[1][0]*y[0]+A[0][0]*y[1])/d];}
function evolve(x,P,t,p){const eq=[P*(p.Rcm+p.Rma),P*p.Rma],v=mvec(expA(t,p),[x[0]-eq[0],x[1]-eq[1]]);return [eq[0]+v[0],eq[1]+v[1]];}
function periodic(p,period,duty){
 const on=period*duty,off=period-on,E=expA(on,p),F=expA(off,p),Q=mult(F,E);
 const eq=[p.Rcm+p.Rma,p.Rma],forcing=mvec(F,mvec([[1-E[0][0],-E[0][1]],[-E[1][0],1-E[1][1]]],eq));
 const x0=solve([[1-Q[0][0],-Q[0][1]],[-Q[1][0],1-Q[1][1]]],forcing);
 const x1=evolve(x0,1,on,p),xend=evolve(x1,0,off,p);
 const closure=Math.max(Math.abs(xend[0]-x0[0]),Math.abs(xend[1]-x0[1]));
 if(closure>1e-6||x0[0]<-1e-7||x0[1]<-1e-7)throw Error("nonperiodic");
 let high=-Infinity,low=Infinity,motor=-Infinity,time=null;
 for(let j=0;j<=400;j++){
  const t=period*j/400,z=t<=on?evolve(x0,1,t,p):evolve(x1,0,t-on,p);
  if(z[0]>high){high=z[0];time=t;}
  low=Math.min(low,z[0]);motor=Math.max(motor,z[1]);
 }
 const maxP=80/high;
 return {period_s:period,duty,coil_peak_K_per_W:high,coil_min_K_per_W:low,motor_peak_K_per_W:motor,
 peak_at_s:time,illustrative_Pcu_ON_W_for_peak_80K:maxP,illustrative_Pcu_MEAN_W:maxP*duty,
 mean_coil_rise_K:maxP*duty*(p.Rcm+p.Rma),cycle_closure_K_per_W:closure};
}
function cooldown(p,c){
 const x=evolve([0,0],c.burst_W_copper,c.burst_s,p);
 let tcoil=null,tboth=null;
 for(let t=0;t<=15000;t++){
  const y=evolve(x,0,t,p);
  if(tcoil===null&&y[0]<c.rest_marker_K)tcoil=t;
  if(tboth===null&&y.every(z=>z<c.rest_marker_K))tboth=t;
  if(tcoil!==null&&tboth!==null)break;
 }
 if(tboth===null)throw Error("cooldown exceeded duration");
 return {heat_copper_W:c.burst_W_copper,heat_duration_s:c.burst_s,
 at_burst_end_coil_K:x[0],at_burst_end_motor_K:x[1],
 rest_s_to_coil_below_20K:tcoil,rest_s_to_both_below_20K:tboth,
 coil_K_after_600s_rest:evolve(x,0,600,p)[0]};
}
function euler(p){
 const dt=.02,n=Math.round(30/dt),on=Math.round(n*.2),cycles=1000;
 let tc=0,tm=0,maxLast=-Infinity;
 for(let k=0;k<cycles*n;k++){
  const pow=k%n<on?1:0;
  const nc=tc+dt*(pow-(tc-tm)/p.Rcm)/p.Cc;
  const nm=tm+dt*((tc-tm)/p.Rcm-tm/p.Rma)/p.Cm;
  tc=nc;tm=nm;
  if(k>=(cycles-1)*n)maxLast=Math.max(maxLast,tc);
 }
 const exact=periodic(p,30,.2).coil_peak_K_per_W;
 return {dt_s:dt,cycles,approx_K_per_W:maxLast,exact_K_per_W:exact,abs_error_K_per_W:Math.abs(maxLast-exact)};
}
function evaluate(c){
 const rows=[],rests={},audit={};
 for(const [name,p] of Object.entries(c.thermal)){
  for(const period of c.periods)for(const duty of c.duty)rows.push({thermal:name,...periodic(p,period,duty)});
  if(Math.abs(periodic(p,30,1).coil_peak_K_per_W-(p.Rcm+p.Rma))>1e-7)throw Error("DC fixed point error");
  rests[name]=cooldown(p,c);audit[name]=euler(p);
 }
 if(rows.length!==60||Object.values(audit).some(x=>x.abs_error_K_per_W>.005))throw Error("audit failure "+JSON.stringify(audit));
 return {study:"P24H",status:"exact within hypothetical LTI Cauer model only",
  base_commit:"8980bc6ede3cdb23070a5e39921098e35db7379d",configuration:c,
  n_periodic_cases:rows.length,rows,recovery:rests,euler_cross_checks:audit,
  selection_30s_25pct:rows.filter(x=>x.period_s===30&&x.duty===.25),
  limitations:["80K/20K are arbitrary comparison markers, not speaker safe limits",
    "Input is COPPER heat power, NOT audio amplifier power; Re(T) and impedance not coupled",
    "Cycle state propagation exact for constant R/C, sampled maxima over 401 time points; no hardware data",
    "Does not validate DSP, current sensing, temperature limits, restart policy or operational full power"]};
}
if(require.main===module){
const data=evaluate(c);
const p=path.join(__dirname,"..","wyniki","p24h_cykle_recovery_20261031.json");
fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(data,null,2)+"\n");
console.log(JSON.stringify({cases:data.n_periodic_cases,selection:data.selection_30s_25pct,
recovery:data.recovery,euler_cross_checks:data.euler_cross_checks},null,2));
}
module.exports={c,expA,evolve,periodic,cooldown,euler,evaluate};
