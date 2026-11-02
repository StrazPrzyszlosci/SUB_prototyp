#!/usr/bin/env node
"use strict";
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const study=function study(drivers,presets) {
 const PI=Math.PI,RHO=1.2041,C=343,P0=2e-5,TA=25,DSP=96000,SEC=8,VRMS=Math.min(40,2*10**(25.5/20)),VRAIL=VRMS*Math.SQRT2,RR=x=>Number(x.toFixed(5));
 const catalog=Object.fromEntries(drivers.map(x=>[x.id,x.model])), preset=Object.fromEntries(presets.map(x=>[x.id,x]));
 function motor(id,th,variant={}) {
  const d=catalog[id],fs=d.fs_hz*(variant.fs||1),vas=d.vas_l*(variant.vas||1),qes=d.qes*(variant.qes||1),sd=d.sd_cm2*1e-4;
  const cms=vas*.001/(RHO*C*C*sd*sd),mms=1/((2*PI*fs)**2*cms),w=2*PI*fs;
  return{sd,cms,mms,rms:w*mms/d.qms,bl:Math.sqrt(w*mms*d.re_ohm/qes),re:d.re_ohm*(variant.re||1),le:d.le_mh*.001,xmax:d.xmax_mm*.001,rth:th.rth,cth:th.cth};
 }
 const thermal={cool:{rth:1.2,cth:35},hot:{rth:2.4,cth:15}};
 const motors=(id,t,mismatch)=>id==="C02"?[motor(id,thermal[t])]:mismatch?[
 motor(id,thermal[t],{fs:1.04,vas:1.08,qes:1.07,re:1.2}),motor(id,thermal[t],{fs:.96,vas:.92,qes:.93})
 ]:[motor(id,thermal[t]),motor(id,thermal[t])];
 const cr=(r=0,i=0)=>({r,i}),add=(a,b)=>cr(a.r+b.r,a.i+b.i),sub=(a,b)=>cr(a.r-b.r,a.i-b.i),mul=(a,b)=>cr(a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r),sc=(a,x)=>cr(a.r*x,a.i*x),div=(a,b)=>sc(mul(a,cr(b.r,-b.i)),1/(b.r*b.r+b.i*b.i)),mag=a=>Math.hypot(a.r,a.i);
 function pOne(ms,V,f) {
  const w=2*PI*f,air=cr(0,-RHO*C*C/(V*.001*w));
  const E=ms.map(m=>{const ze=cr(m.re,w*m.le),zm=cr(m.rms,w*m.mms-1/(w*m.cms));return{diag:add(zm,div(cr(m.bl*m.bl),ze)),rhs:div(cr(m.bl),ze)}});
  let vel;if(ms.length===1)vel=[div(E[0].rhs,add(E[0].diag,sc(air,ms[0].sd**2)))];
  else{
   const A=add(E[0].diag,sc(air,ms[0].sd**2)),D=add(E[1].diag,sc(air,ms[1].sd**2)),B=sc(air,ms[0].sd*ms[1].sd),den=sub(mul(A,D),mul(B,B));
   vel=[div(sub(mul(E[0].rhs,D),mul(B,E[1].rhs)),den),div(sub(mul(E[1].rhs,A),mul(B,E[0].rhs)),den)];
  }
  return mag(mul(cr(0,RHO*w/(2*PI)),vel.reduce((a,v,j)=>add(a,sc(v,ms[j].sd)),cr())));
 }
 function hfilters(sections,f){
  const w=-2*PI*f/DSP,z=cr(Math.cos(w),Math.sin(w)),zz=mul(z,z);
  return mag(sections.reduce((a,s)=>mul(a,div(add(add(cr(s.b0),sc(z,s.b1)),sc(zz,s.b2)),add(add(cr(1),sc(z,s.a1)),sc(zz,s.a2)))),cr(1)));
 }
 function wave(t,type){
  if(type==="sustained")return Math.min(1,t/.1)*(.65*Math.sin(2*PI*40*t)+.54*Math.sin(2*PI*25*t+.8)+.42*Math.sin(2*PI*20*t+1.9)+.23*Math.sin(2*PI*63*t));
  const pos=t%2,envelope=pos<.55?Math.sin(PI*pos/.55)**2:0;
  return envelope*(.65*Math.sin(2*PI*40*t)+.62*Math.sin(2*PI*25*t+.6)+.24*Math.sin(2*PI*63*t));
 }
 function slope(ms,x,v,i,T,U){
  let Q=0;for(let j=0;j<ms.length;j++)Q+=ms[j].sd*x[j];const k=RHO*C*C/(120*.001);
  const dx=[],dv=[],di=[],dT=[];
  for(let j=0;j<ms.length;j++){
   const m=ms[j],re=m.re*(1+.0039*(T[j]-TA));
   dx[j]=v[j];dv[j]=(m.bl*i[j]-m.rms*v[j]-x[j]/m.cms-m.sd*k*Q)/m.mms;
   di[j]=(U-re*i[j]-m.bl*v[j])/m.le;
   dT[j]=(i[j]*i[j]*re-(T[j]-TA)/m.rth)/m.cth;
  }
  return{dx,dv,di,dT};
 }
 function simulate(id,type,mode,heat,mismatch=false,mechHz=9600) {
  const dec=DSP/mechHz;if(!Number.isInteger(dec))throw Error("Noninteger DSP block");const dt=1/mechHz,ns=SEC*mechHz;
  const ms=motors(id,heat,mismatch),nom=motors(id,"cool",false),sections=preset[id].sections;
  const states=sections.map(()=>({z1:0,z2:0})),x=ms.map(()=>0),v=ms.map(()=>0),i=ms.map(()=>0),T=ms.map(()=>TA);
  const gain=P0*10**(103/20)*Math.SQRT2/(.65*pOne(nom,120,40)*hfilters(sections,40));
  let lg=1,pavg=0,maxX=0,maxCurrent=0,maxVolt=0,maxTemp=TA,Einput=0,Ecopper=0,Emech=0,Eheatout=0,nclip=0,overx=0,overi=0,mingain=1;
  const trace=[];
  for(let n=0;n<ns;n++){
   let u=0;
   for(let b=0;b<dec;b++){
    u=wave((n*dec+b)/DSP,type);
    for(let j=0;j<sections.length;j++){
     const s=sections[j],z=states[j],y=s.b0*u+z.z1;
     z.z1=s.b1*u-s.a1*y+z.z2;z.z2=s.b2*u-s.a2*y;u=y;
    }
   }
   const risk=Math.max(...ms.map((m,j)=>(Math.abs(x[j])+.006*Math.abs(v[j]))/(.7*m.xmax)));
   let curP=0;for(let j=0;j<ms.length;j++)curP+=i[j]**2*ms[j].re*(1+.0039*(T[j]-TA));
   pavg+=(curP-pavg)*dt/.05;
   const target=Math.min(1,1/Math.max(1,risk),Math.sqrt(50/Math.max(50,pavg)));
   if(mode==="feedback"){const tau=target<lg?.001:.18;lg+=(target-lg)*Math.min(1,dt/tau);}
   else lg=mode==="derate"?.5:1;
   mingain=Math.min(lg,mingain);
   const pre=u*gain*lg,U=Math.min(VRAIL,Math.max(-VRAIL,pre));
   if(Math.abs(pre)>VRAIL)nclip++;
   const k1=slope(ms,x,v,i,T,U),xm=x.map((a,j)=>a+.5*dt*k1.dx[j]),vm=v.map((a,j)=>a+.5*dt*k1.dv[j]),im=i.map((a,j)=>a+.5*dt*k1.di[j]),Tm=T.map((a,j)=>a+.5*dt*k1.dT[j]);
   const k2=slope(ms,xm,vm,im,Tm,U);
   let Pc=0,Pm=0,Po=0;
   for(let j=0;j<ms.length;j++){
    x[j]+=dt*k2.dx[j];v[j]+=dt*k2.dv[j];i[j]+=dt*k2.di[j];T[j]+=dt*k2.dT[j];
    const re=ms[j].re*(1+.0039*(T[j]-TA));
    Pc+=i[j]*i[j]*re;Pm+=ms[j].rms*v[j]*v[j];Po+=(T[j]-TA)/ms[j].rth;
    maxX=Math.max(maxX,Math.abs(x[j])/ms[j].xmax);maxTemp=Math.max(maxTemp,T[j]);
   }
   const totalI=i.reduce((a,b)=>a+b,0);
   maxCurrent=Math.max(maxCurrent,Math.abs(totalI));maxVolt=Math.max(maxVolt,Math.abs(U));
   if(ms.some((m,j)=>Math.abs(x[j])>.7*m.xmax))overx++;
   if(Math.abs(totalI)>12*Math.SQRT2)overi++;
   Einput+=dt*U*totalI;Ecopper+=dt*Pc;Emech+=dt*Pm;Eheatout+=dt*Po;
   if(n%mechHz===0)trace.push({s:n/mechHz,temperature_c:RR(Math.max(...T)),limit_gain:RR(lg)});
  }
  const Eth=ms.reduce((a,m,j)=>a+m.cth*(T[j]-TA),0);
  const Estore=ms.reduce((a,m,j)=>a+.5*m.mms*v[j]**2+.5*x[j]**2/m.cms+.5*m.le*i[j]**2,0)+.5*RHO*C*C/(120*.001)*ms.reduce((a,m,j)=>a+m.sd*x[j],0)**2;
  const error=(Einput-Emech-Eheatout-Eth-Estore)/Math.max(1,Math.abs(Einput));
  return{id,type,mode,heat,mismatch,mechHz,target_ref_40hz_db:103,max_catalog_x_fraction:RR(maxX),time_over_70pct_x_percent:RR(100*overx/ns),time_over_current_peak_percent:RR(100*overi/ns),time_clipped_percent:RR(100*nclip/ns),highest_coil_temp_c:RR(maxTemp),total_copper_energy_j:RR(Ecopper),energy_residual:RR(error),minimum_gain:RR(mingain),max_current_a:RR(maxCurrent),max_voltage_v:RR(maxVolt),trace};
 }
 const configs=[];
 for(const id of ["C02","C05"])for(const type of ["sustained","bursts"])for(const mode of ["none","derate","feedback"])for(const heat of ["cool","hot"])configs.push({id,type,mode,heat,mismatch:false});
 for(const mode of ["none","feedback"])configs.push({id:"C05",type:"sustained",mode,heat:"hot",mismatch:true});
 const results=configs.map(c=>simulate(c.id,c.type,c.mode,c.heat,c.mismatch));
 const convergence=[simulate("C02","sustained","none","hot",false,19200),simulate("C05","sustained","none","hot",false,19200)];
 const pairs=convergence.map(x=>{const y=results.find(r=>r.id===x.id&&r.type===x.type&&r.mode===x.mode&&r.heat===x.heat&&!r.mismatch);
  return{id:x.id,base_hz:9600,refined_hz:19200,base_max_x:y.max_catalog_x_fraction,refined_max_x:x.max_catalog_x_fraction,relative_difference_percent:RR(100*(x.max_catalog_x_fraction-y.max_catalog_x_fraction)/x.max_catalog_x_fraction),base_temp:y.highest_coil_temp_c,refined_temp:x.highest_coil_temp_c};});
 if(results.length!==26||convergence.length!==2||results.some(r=>!Number.isFinite(r.energy_residual)||Math.abs(r.energy_residual)>.025)||pairs.some(x=>Math.abs(x.relative_difference_percent)>2))throw Error("B12-04 numerical gate");
 const screens=Object.fromEntries(["C02","C05"].map(id=>[id,results.filter(r=>r.id===id&&r.type==="sustained"&&r.heat==="hot"&&!r.mismatch).map(r=>({mode:r.mode,xpeak_fraction:r.max_catalog_x_fraction,over70_percent:r.time_over_70pct_x_percent,temp_c:r.highest_coil_temp_c,clip_percent:r.time_clipped_percent}))]));
 return {schema:"b12_04_time_domain_ode_with_thermal_uncertainty",date:"2026-11-02",method:{f_dsp_hz:DSP,f_mechanical_hz:9600,simulation_s:SEC,box_l:120,reference_40hz_sine_db:103,volume_excursion_limit_fraction:.7,amp_voltage_peak_v:RR(VRAIL),amp_current_peak_screen_a:RR(12*Math.SQRT2),thermal_hypotheses:thermal,coil_temp_coefficient_re_per_k:.0039,one_channel_parallel_pair:true,nominal_hp_hz:18,algorithms:["RK2 electro-mechanical and coil RC coupled pressure","five RBJ IIR sections 96 kHz from B12-03","hard-voltage-rail amp, no current clamp","unqualified controller using true x and v with 6 ms forecast, 1 ms attack, 180 ms release","electrical energy vs copper heat, body cooling, stored thermal+mechanical+inductor energy"]},counts:{scenarios:results.length,convergence:convergence.length,per_run_mechanical_samples:SEC*9600},screens,convergence:pairs,results,limitations:["No BL(x), Cms(x), Le(x,f), THD/IMD and no physical damage modeling","Rth and Cth are invented scenario axes, not catalog or measured thermal properties; temperatures cannot certify safe operation","The feedback example requires true x and v unavailable from a normal DSP; it FAILS the 70% excursion target in tested scenarios and is NOT a recommended protective algorithm","Music-like and bursts synthetic input, no real track or certification signal","Hard voltage clipping only, no model of amplifier's current-limit behavior, SMPS sag or fault protection","No measured room SPL, no validated DSP preset or mechanical 3D design; 103 dB is arbitrary equal-40Hz calibration"]};
};
const root=path.resolve(__dirname,'..');
const models=JSON.parse(fs.readFileSync(path.join(root,'dane/przetworniki/pula_rozszerzona.json'),'utf8')).drivers.filter(d=>['C02','C05'].includes(d.candidate_id)).map(d=>({id:d.candidate_id,model:d.model}));
const presets=JSON.parse(fs.readFileSync(path.join(root,'wyniki/b12_03_iir_i_rozrzut_20261102.json'),'utf8')).presets.filter(p=>p.V===120&&p.hp===18);
const actual=study(models,presets),expected=JSON.parse(fs.readFileSync(path.join(root,'wyniki/b12_04_dynamika_termika_20261102.json'),'utf8'));
assert.deepStrictEqual(actual,expected);
console.log('B12-04 OK:',actual.counts.scenarios,'8-s transients,',actual.counts.convergence,'timestep refinements, conservative controllers may violate X');
