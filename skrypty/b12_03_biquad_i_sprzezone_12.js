#!/usr/bin/env node
"use strict";
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const calculate=function calculate(models) {
 const PI=Math.PI,R=1.2041,C=343,REF=2e-5,FS=96000,rt=Math.SQRT2;
 const freqs=[20,25,31.5,40,63,80], vols=[100,120,150], hps=[18,25];
 const profiles={balanced:[1,1,1,1,.8,.55],bassheavy:[1.4,1.3,1.1,1,.8,.55],reduced20:[.45,.75,1,1,.8,.55]},phases=["aligned","quadratic"];
 const cuts=[{name:"conservative",cap:50,xf:.7},{name:"catalog_limit",cap:100,xf:1}];
 const vcap=Math.min(40,2*Math.pow(10,25.5/20)),imax=12;
 const cr=(r=0,i=0)=>({r,i}),add=(a,b)=>cr(a.r+b.r,a.i+b.i),sub=(a,b)=>cr(a.r-b.r,a.i-b.i),scale=(a,x)=>cr(a.r*x,a.i*x),mul=(a,b)=>cr(a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r),abs=x=>Math.hypot(x.r,x.i),div=(a,b)=>scale(mul(a,cr(b.r,-b.i)),1/(b.r*b.r+b.i*b.i)),polar=ang=>cr(Math.cos(ang),Math.sin(ang)),rnd=x=>Number(x.toFixed(5));
 const dict=Object.fromEntries(models.map(x=>[x.id,x.m]));
 function make(id,ds={}){
  const d=dict[id],f=d.fs_hz*(ds.fs||1),v=d.vas_l*(ds.vas||1),q=d.qes*(ds.qes||1),sd=d.sd_cm2*.0001,cm=v*.001/(R*C*C*sd*sd),mm=1/((2*PI*f)**2*cm),w=2*PI*f;
  return{sd,cm,mm,rms:w*mm/d.qms,bl:Math.sqrt(w*mm*d.re_ohm/q),re:d.re_ohm*(ds.re||1),le:d.le_mh*.001,x:d.xmax_mm*.001};
 }
 function move(id,mismatch){
  return id==="C02"?[make(id)]:mismatch?[make(id,mismatch[0]),make(id,mismatch[1])]:[make(id),make(id)];
 }
 function port(ms,V,f){
  const w=2*PI*f,back=cr(0,-R*C*C/(V*.001*w)),op=cr(0,R*w/(2*PI));
  const a=ms.map(m=>{const ze=cr(m.re,w*m.le),zm=cr(m.rms,w*m.mm-1/(w*m.cm));return{ze,diag:add(zm,div(cr(m.bl*m.bl),ze)),rhs:div(cr(m.bl),ze)}});
  let vv;
  if(ms.length===1){vv=[div(a[0].rhs,add(a[0].diag,scale(back,ms[0].sd**2)))];}
  else {const A=add(a[0].diag,scale(back,ms[0].sd**2)),D=add(a[1].diag,scale(back,ms[1].sd**2)),B=scale(back,ms[0].sd*ms[1].sd),det=sub(mul(A,D),mul(B,B));
   vv=[div(sub(mul(a[0].rhs,D),mul(B,a[1].rhs)),det),div(sub(mul(a[1].rhs,A),mul(B,a[0].rhs)),det)];}
  const ii=vv.map((v,j)=>div(sub(cr(1),scale(v,ms[j].bl)),a[j].ze));
  const I=ii.reduce(add,cr(0)),X=vv.map(v=>div(v,cr(0,w))),Q=vv.reduce((s,v,k)=>add(s,scale(v,ms[k].sd)),cr(0));
  const P=mul(op,Q),loss=ii.reduce((s,v,k)=>s+abs(v)**2*ms[k].re,0),mech=vv.reduce((s,v,k)=>s+abs(v)**2*ms[k].rms,0);
  if(Math.abs(I.r-loss-mech)>1e-8*Math.max(1,I.r))throw Error("Power balance");
  return{I,X,ii,P};
 }
 function biq(type,f,g=0,q=1) {
  const w=2*PI*f/FS,co=Math.cos(w),si=Math.sin(w),A=Math.pow(10,g/40),al=si/(2*q);let p;
  if(type==="hp")p=[(1+co)/2,-(1+co),(1+co)/2,1+al,-2*co,1-al];
  if(type==="lp")p=[(1-co)/2,1-co,(1-co)/2,1+al,-2*co,1-al];
  if(type==="peak")p=[1+al*A,-2*co,1-al*A,1+al/A,-2*co,1-al/A];
  if(type==="shelf"){const a=si*Math.SQRT2/2,k=2*Math.sqrt(A)*a;
    p=[A*((A+1)-(A-1)*co+k),2*A*((A-1)-(A+1)*co),A*((A+1)-(A-1)*co-k),(A+1)+(A-1)*co+k,-2*((A-1)+(A+1)*co),(A+1)+(A-1)*co-k];}
  if(!p)throw Error("bad biquad");const [b0,b1,b2,a0,a1,a2]=p;return{b0:b0/a0,b1:b1/a0,b2:b2/a0,a1:a1/a0,a2:a2/a0};
 }
 function resp(q,f){const z=polar(-2*PI*f/FS),zz=mul(z,z);return div(add(add(cr(q.b0),scale(z,q.b1)),scale(zz,q.b2)),add(add(cr(1),scale(z,q.a1)),scale(zz,q.a2)));}
 function ht(filters,f){return filters.reduce((x,s)=>mul(x,resp(s,f)),cr(1));}
 const sf=[25,35,45,55,70],sg=[0,3,6,9,12],pf=[28,40,55,70],pg=[-6,-3,0,3,6],pq=[.7,1.2],grid=[];
 for(const f of sf)for(const g of sg)for(const ff of pf)for(const gg of pg)for(const q of pq)grid.push({f,g,ff,gg,q,s:biq("shelf",f,g),p:biq("peak",ff,gg,q)});
 function optimize(id,V){
  const ms=move(id),fx=[20,25,31.5,40,50,63,70,80],wt=[.6,1,1.2,1.2,1.15,1,1,.2],baseline=fx.map(f=>20*Math.log10(abs(port(ms,V,f).P)));
  let best=null;
  for(const t of grid){
   const db=fx.map((f,k)=>baseline[k]+20*Math.log10(abs(ht([t.s,t.p],f))));
   const mean=db.reduce((s,d,k)=>s+d*wt[k],0)/wt.reduce((a,b)=>a+b,0);
   const variance=db.reduce((s,d,k)=>s+wt[k]*(d-mean)**2,0)/wt.reduce((a,b)=>a+b,0);
   const boost=Math.max(...[15,20,25,31.5,40,50,63,80,100,140].map(f=>20*Math.log10(abs(ht([t.s,t.p],f)))));
   if(boost>12.1)continue;
   const score=variance+.018*t.g**2+.03*t.gg**2+.004*boost**2;
   if(!best||score<best.score)best={f:t.f,g:t.g,ff:t.ff,gg:t.gg,q:t.q,score,boost,flat:Math.max(...db)-Math.min(...db),s:t.s,p:t.p};
  }
  return best;
 }
 function target(id,ms,V,filters,profile,phase){
  const v40=abs(mul(ht(filters,40),port(ms,V,40).P)),unit=REF*Math.pow(10,90/20)/v40;
  return freqs.map((f,k)=>scale(mul(ht(filters,f),polar(phase==="aligned"?0:PI*k*(k-1)/freqs.length)),unit*profiles[profile][k]));
 }
 function evaluate(ms,V,inputs,L) {
  let Vr2=0,Ir2=0,Cu=0,vpk=0,ipk=0;
  const xs=ms.map(()=>0);
  for(let k=0;k<freqs.length;k++){
   const u=inputs[k],o=port(ms,V,freqs[k]),i=mul(o.I,u);
   Vr2+=abs(u)**2;Ir2+=abs(i)**2;vpk+=abs(u);ipk+=abs(i);
   for(let j=0;j<ms.length;j++){const ix=mul(o.ii[j],u),x=mul(o.X[j],u);xs[j]+=abs(x);Cu+=abs(ix)**2*ms[j].re;}
  }
  const factors={voltage_rms:vcap/Math.sqrt(Vr2),current_rms:imax/Math.sqrt(Ir2),
    peak_voltage:vcap/vpk,peak_current:imax/ipk,copper:Math.sqrt(L.cap/Cu)};
  for(let j=0;j<xs.length;j++)factors["excursion_"+j]=ms[j].x*L.xf/(rt*xs[j]);
  const [reason,scaleF]=Object.entries(factors).sort((a,b)=>a[1]-b[1])[0];
  if(!Number.isFinite(scaleF)||scaleF<=0)throw Error("Bounds invalid");
  return {level40:rnd(90+20*Math.log10(scaleF)),reason,x_mm:rnd(Math.max(...xs)*rt*scaleF*1000),copper_w:rnd(Cu*scaleF*scaleF),v_rms:rnd(Math.sqrt(Vr2)*scaleF)};
 }
 const presets=[],nominal=[],stress=[],comparison=[],corners=[],variation=[];
 for(const f of [-.04,.04])for(const v of [-.08,.08])for(const q of [-.07,.07])for(const r of [0,.2])
  corners.push([{fs:1+f,vas:1+v,qes:1+q,re:1+r},{fs:1-f,vas:1-v,qes:1-q,re:1}]);
 for(const id of ["C02","C05"])for(const V of vols) {
  const opt=optimize(id,V);
  for(const hp of hps){
   const filters=[biq("hp",hp,0,Math.SQRT1_2),biq("lp",80,0,Math.SQRT1_2),biq("lp",80,0,Math.SQRT1_2),opt.s,opt.p];
   const spec={id,V,hp,shelf:{freq:opt.f,gain_db:opt.g},peak:{freq:opt.ff,gain_db:opt.gg,q:opt.q},
     max_eq_gain_db:rnd(opt.boost),passband_span_db:rnd(opt.flat),sections:filters};
   presets.push(spec);
   const ms=move(id);
   for(const profile of Object.keys(profiles))for(const phase of phases) {
    const inputs=target(id,ms,V,filters,profile,phase);
    for(const l of cuts) {
     const result=evaluate(ms,V,inputs,l),p40=port(ms,V,40).P,rel=freqs.map((f,k)=>rnd(20*Math.log10(abs(mul(port(ms,V,f).P,inputs[k]))/abs(mul(p40,inputs[3])))));
     nominal.push({id,V,hp,profile,phase,limit:l.name,level40_db:result.level40,reason:result.reason,x_mm:result.x_mm,copper_w:result.copper_w,v_rms:result.v_rms,rel20_db:rel[0],rel25_db:rel[1],rel80_db:rel[5]});
    }
    if(id==="C05"&&V===120)for(let ci=0;ci<corners.length;ci++){
      const act=move(id,corners[ci]),r=evaluate(act,V,inputs,cuts[0]);
      const shift=f=>rnd(20*Math.log10(abs(port(act,V,f).P)/abs(port(ms,V,f).P)));
      const v=port(act,V,40).X,delta=mul(v[0],cr(v[1].r,-v[1].i)),angleDeg=rnd(Math.atan2(delta.i,delta.r)*180/PI);
      stress.push({hp,profile,phase,corner:ci,level40_db:r.level40,reason:r.reason,level20_error_db:shift(20),level40_error_db:shift(40),phase_difference_40deg:angleDeg,x_mm:r.x_mm});
    }
   }
  }
 }
 if(presets.length!==12||nominal.length!==144||stress.length!==192)throw Error("Count mismatch");
 for(const hp of hps)for(const profile of Object.keys(profiles))for(const limit of cuts){
  const pick=id=>nominal.find(x=>x.id===id&&x.V===120&&x.hp===hp&&x.profile===profile&&x.phase==="aligned"&&x.limit===limit.name);
  const a=pick("C02"),b=pick("C05");
  comparison.push({hp,profile,limit:limit.name,dayton_db40:a.level40_db,dual_stx_db40:b.level40_db,gap_db:rnd(a.level40_db-b.level40_db),dayton_rel20_db:a.rel20_db,stx_rel20_db:b.rel20_db,limit_dayton:a.reason,limit_stx:b.reason});
 }
 const mismatchSummary=[];
 for(const hp of hps)for(const profile of Object.keys(profiles)) {
  const ss=stress.filter(x=>x.hp===hp&&x.profile===profile);
  mismatchSummary.push({hp,profile,nominal_db40:nominal.find(x=>x.id==="C05"&&x.V===120&&x.hp===hp&&x.profile===profile&&x.phase==="aligned"&&x.limit==="conservative").level40_db,worst_db40:rnd(Math.min(...ss.map(x=>x.level40_db))),max_abs_20hz_error_db:rnd(Math.max(...ss.map(x=>Math.abs(x.level20_error_db)))),max_abs_40hz_error_db:rnd(Math.max(...ss.map(x=>Math.abs(x.level40_error_db)))),max_abs_phase_40deg:rnd(Math.max(...ss.map(x=>Math.abs(x.phase_difference_40deg))))});
 }
 return{schema:"b12_03_iir_coupled_pair",date:"2026-11-02",method:{sample_rate_hz:FS,frequency_hz:freqs,volumes_l:vols,hp_hz:hps,lp_hz:80,peq_sections:2,filters_total:5,optimizer_candidates:grid.length,amplifier_volts_rms_bound:rnd(vcap),amp_current_rms:imax,nominal_copper_limits:cuts,profiles,phases,
  mismatch_hypotheses:"16 opposing Fs +-4%, Vas +-8%, Qes +-7% and Re 1.0/1.2 on one driver; NOT measured variation",
  peak_method:"phase-independent triangle bound for voltage,current and each membrane's displacement"},
 counts:{presets:presets.length,multitone_nominal:nominal.length,mismatch:stress.length},presets,nominal,comparison_120l:comparison,mismatch_cases:stress,mismatch_summary:mismatchSummary,
 caveats:["Ideal linear drivers and 2-DOF uniform-pressure cavity. No THD, IMD, radiation interference or mechanical integrity model.",
 "The 2-band finite IIR filters are modeled with RBJ coefficients at 96kHz and are NOT a validated miniDSP preset; no vendor coefficient sign convention claimed.",
 "50/100W total copper limits and 70/100% Xmax are conditional sensitivity cases, not safe thermals or validated THD thresholds.",
 "Voltage cap depends on a hypothetical 2Vrms DAC plus 25.5dB amplifier gain; a real amplifier may not deliver these levels at 20Hz.",
 "Triangle upper bounds give conservative safe envelopes for the six ideal tones; not an operational real-time limiter.",
 "No measured pair mismatch tolerance; no physical prototype or CNC approval."]};
};
const root=path.resolve(__dirname,'..'),pool=JSON.parse(fs.readFileSync(path.join(root,'dane/przetworniki/pula_rozszerzona.json'),'utf8'));
const drivers=pool.drivers.filter(x=>['C02','C05'].includes(x.candidate_id)).map(x=>({id:x.candidate_id,m:x.model}));
const out=calculate(drivers);
assert.deepStrictEqual(out,JSON.parse(fs.readFileSync(path.join(root,'wyniki/b12_03_iir_i_rozrzut_20261102.json'),'utf8')));
const cols=["hp","profile","limit","dayton_db40","dual_stx_db40","gap_db","dayton_rel20_db","stx_rel20_db","limit_dayton","limit_stx"];
const csv=cols.join(',')+'\n'+out.comparison_120l.map(x=>cols.map(k=>x[k]).join(',')).join('\n')+'\n';
assert.strictEqual(csv,fs.readFileSync(path.join(root,'wyniki/b12_03_porownanie_120l.csv'),'utf8'));
console.log('B12-03 OK',out.counts);
