#!/usr/bin/env node
"use strict";
/* B12-01: two normal 12-inch woofers vs one Dayton 15-inch. Verified against committed CSV/JSON. */
const fs=require('fs'),path=require('path'),assert=require('assert');
const compute=function compute(pool,extra) {
  const RHO=1.2041,C=343,PREF=2e-5,PI=Math.PI;
  const drivers=Object.fromEntries(pool.map(r=>[r.candidate_id,r.model]));drivers[extra.candidate_id]=extra.model;
  const configs=[{id:"C02",n:1,connection:"single"},{id:"C05",n:2,connection:"parallel"},{id:"C05",n:2,connection:"series"},{id:"C06",n:2,connection:"parallel"},{id:"C06",n:2,connection:"series"},{id:"C32",n:2,connection:"parallel"},{id:"C32",n:2,connection:"series"}];
  const frequencies=[...new Set([...Array.from({length:31},(_,i)=>20+2*i),31.5])].sort((a,b)=>a-b);
  const volumes=[80,100,120,150], caps=[50,100], xfractions=[0.7,1];
  function motor(d,n,conn){
    const sd=d.sd_cm2*1e-4,cms=d.vas_l*.001/(RHO*C*C*sd*sd),w=2*PI*d.fs_hz,mms=1/(w*w*cms),bl=Math.sqrt(w*mms*d.re_ohm/d.qes),rms=w*mms/d.qms;
    if(n===1)return {sd,cms,mms,bl,rms,re:d.re_ohm,le:d.le_mh*.001,xmax:d.xmax_mm*.001,fs:d.fs_hz,qes:d.qes,qms:d.qms,vas:d.vas_l,nominal:d.nominal_ohm};
    return {sd:2*sd,cms:cms/2,mms:2*mms,bl:bl*(conn==="series"?2:1),rms:2*rms,re:d.re_ohm*(conn==="series"?2:.5),le:d.le_mh*.001*(conn==="series"?2:.5),xmax:d.xmax_mm*.001,fs:d.fs_hz,qes:d.qes,qms:d.qms,vas:2*d.vas_l,nominal:d.nominal_ohm*(conn==="series"?2:.5)};
  }
  function alignment(m,vb){
    const qts=1/(1/m.qes+1/m.qms),k=Math.sqrt(1+m.vas/vb),qtc=qts*k,fc=m.fs*k,b=2-1/(qtc*qtc),y=b>=0?2/(b+Math.hypot(b,2)):(-b+Math.hypot(b,2))/2;
    return {fc_hz:fc,qtc,f3_hz:fc*Math.sqrt(y)};
  }
  function calc(m,vb,f,pcap,xfraction){
    const w=2*PI*f,K=1/m.cms+RHO*C*C*m.sd*m.sd/(vb*.001),zr=m.rms,zi=w*m.mms-K/w,zsq=zr*zr+zi*zi,
    zre=m.re+m.bl*m.bl*zr/zsq,zim=w*m.le-m.bl*m.bl*zi/zsq,zmag=Math.hypot(zre,zim),i1=1/zmag,v1=m.bl*i1/Math.sqrt(zsq),x1=Math.SQRT2*v1/w,
    pcu1=i1*i1*m.re,p1=RHO*w*m.sd*v1/(2*PI);
    const lims={Xpeak:m.xmax*xfraction/x1,Vrms:40,Irms:12/i1,Pcu:Math.sqrt(pcap/pcu1)};
    const name=Object.keys(lims).reduce((a,b)=>lims[a]<=lims[b]?a:b),u=lims[name],i=u*i1,pcu=u*u*pcu1,xpk=u*x1;
    const pin=u*u*i1*i1*zre, me=u*u*v1*v1*m.rms;
    if(!(Number.isFinite(u)&&u>0&&i<=12+1e-9&&u<=40+1e-9&&pcu<=pcap+1e-9&&xpk<=m.xmax*xfraction+1e-9))throw Error("Constraint violation");
    if(Math.abs(pin-(pcu+me))>1e-9*Math.max(1,pin))throw Error("Power balance violation");
    return {spl:20*Math.log10(p1*u/PREF),v:u,i,xpk_mm:xpk*1000,pcu,limit:name,spl_per_1v:20*Math.log10(p1/PREF),i_per_1v:i1,x_per_1v_mm:x1*1000,pcu_per_1v:pcu1};
  }
  const round=(v)=>Number(v.toFixed(5));
  const rows=[], aggregates=[];
  for(const conf of configs){
    const m=motor(drivers[conf.id],conf.n,conf.connection);
    for(const vol of volumes){
      const a=alignment(m,vol);
      for(const cap of caps)for(const frac of xfractions){
        const vals=frequencies.map(f=>({f,...calc(m,vol,f,cap,frac)}));
        const min=vals.reduce((p,v)=>v.spl<p.spl?v:p,vals[0]);
        aggregates.push({id:conf.id,connection:conf.connection,volume_l:vol,copper_cap_w_total:cap,xmax_fraction:frac,fc_hz:round(a.fc_hz),qtc:round(a.qtc),f3_hz:round(a.f3_hz),nominal_ohm:m.nominal,min_20_80_db:round(min.spl),limiting_frequency_hz:min.f,min_limit:min.limit,spl20_db:round(vals[0].spl),spl40_db:round(vals.find(v=>v.f===40).spl),spl80_db:round(vals.at(-1).spl),x20_mm:round(vals[0].xpk_mm),v20_rms:round(vals[0].v),i20_rms:round(vals[0].i)});
        for(const v of vals)rows.push([conf.id,conf.n,conf.connection,vol,round(v.f),cap,frac,round(v.spl),round(v.v),round(v.i),round(v.xpk_mm),round(v.pcu),v.limit]);
      }
    }
  }
  const get=(id,conn,vol,cap=50,frac=1)=>aggregates.find(x=>x.id===id&&x.connection===conn&&x.volume_l===vol&&x.copper_cap_w_total===cap&&x.xmax_fraction===frac);
  const ref=get("C02","single",120);
  const matched=[];
  for(const conf of configs.filter(c=>c.id!=="C02")){
    const m=motor(drivers[conf.id],conf.n,conf.connection),z=calc(m,120,20,50,1),f=Math.pow(10,(ref.spl20_db-z.spl_per_1v)/20);
    matched.push({id:conf.id,connection:conf.connection,target_ref_spl_db:ref.spl20_db,required_v_rms:round(f),required_i_rms:round(f*z.i_per_1v),required_xpeak_mm:round(f*z.x_per_1v_mm),catalog_xmax_mm:drivers[conf.id].xmax_mm,required_total_Pcu_w:round(f*f*z.pcu_per_1v),possible_with_catalog_xmax:f*z.x_per_1v_mm<=drivers[conf.id].xmax_mm,possible_with_cap_50_w:f*f*z.pcu_per_1v<=50});
  }
  const header="candidate_id,drivers,connection,net_volume_l,frequency_hz,total_copper_limit_w,xmax_fraction,spl_2pi_1m_db,voltage_rms_v,current_rms_a,xpeak_each_mm,copper_total_w,limiter\n";
  const csv=header+rows.map(r=>r.join(",")).join("\n")+"\n";
  if(rows.length!==3584||aggregates.length!==112||!matched.every(v=>Number.isFinite(v.required_v_rms)))throw Error("Count/finiteness test failed");
  const summary={schema:"b12_01_screening_v1",date:"2026-11-02",row_count:rows.length,config_count:configs.length,volumes_l:volumes,frequency_hz:frequencies,pcu_w_total:caps,xmax_fraction:xfractions,reference_20hz_120l_50w_db:ref.spl20_db,aggregate:aggregates,matched_dayton_20hz:matched,note:"Ideal coherent normal pairs, single power channel, fixed small-signal T/S and Le, max voltage 40Vrms, max total current 12Arms, no room/DSP crossover transfer/THD/thermal dynamics; Pcu is assumed total copper loss ceiling. Level min over 20–80 Hz is theoretical full-band ceiling with arbitrary per-frequency equalization, not an implemented DSP curve."};
  return {csv,summary};
};
const root=path.resolve(__dirname,'..');
const pool=JSON.parse(fs.readFileSync(path.join(root,'dane/przetworniki/pula_rozszerzona.json'),'utf8'));
const reg=JSON.parse(fs.readFileSync(path.join(root,'dane/przetworniki/b12_01_rozszerzenie_20261102.json'),'utf8'));
const out=compute(pool.drivers,reg.added_candidate);
assert.strictEqual(out.csv,fs.readFileSync(path.join(root,'wyniki/b12_01_wspolne_scenariusze_3584.csv'),'utf8'));
assert.deepStrictEqual(out.summary,JSON.parse(fs.readFileSync(path.join(root,'wyniki/b12_01_podsumowanie_20261102.json'),'utf8')));
console.log('B12-01 OK: 3584 sinus scenarios, 112 aggregate cases, power balance and V/I/X/Pcu limits verified');
