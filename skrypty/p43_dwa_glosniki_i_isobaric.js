#!/usr/bin/env node
"use strict";
/** P43: identical-driver pairs with a shared closed cabinet. Pure 0D sinus model.
 *  Limits: 40Vrms/12Arms, one-way Xpeak, optional total coil loss. Does not
 *  simulate THD, room response, dynamic cooling, cavity leakage or geometry.
 *  Run from repo: node skrypty/p43_dwa_glosniki_i_isobaric.js
 */
const fs=require("fs"),path=require("path");
const ROOT=path.resolve(__dirname,"..");
const RHO=1.2041,C=343,PREF=0.00002,PI=Math.PI;
function derive(d){
  const sd=d.sd_cm2*1e-4,cms=d.vas_l*1e-3/(RHO*C*C*sd*sd),mms=1/((2*PI*d.fs_hz)**2*cms),w=2*PI*d.fs_hz;
  const re=d.re_ohm,le=d.le_mh*.001,bl=Math.sqrt(w*mms*re/d.qes),rms=w*mms/d.qms;
  return {name:d.name,fs:d.fs_hz,sd,cms,mms,re,le,bl,rms,xmax:d.xmax_mm*.001,vas:d.vas_l,qes:d.qes,qms:d.qms,nominal:d.nominal_ohm};
}

function equivalent(d,topology,connection){
  const x=derive(d);if(topology==="single")return x;
  const isNormal=topology==="normal", isSeries=connection==="series";
  return {...x,name:`${x.name} ×2 ${topology}/${connection}`,sd:x.sd*(isNormal?2:1),
    cms:x.cms/2,mms:x.mms*2,rms:x.rms*2,bl:x.bl*(isSeries?2:1),
    re:x.re*(isSeries?2:0.5),le:x.le*(isSeries?2:0.5),nominal:x.nominal*(isSeries?2:.5),
    vas:x.vas*(isNormal?2:.5)};
}

function response(x,vb,f,cap){
  const w=2*PI*f,stiff=1/x.cms+RHO*C*C*x.sd*x.sd/(vb*.001),
    zmRe=x.rms,zmIm=w*x.mms-stiff/w,zmSq=zmRe*zmRe+zmIm*zmIm,
    zRe=x.re+x.bl*x.bl*zmRe/zmSq,zIm=w*x.le-x.bl*x.bl*zmIm/zmSq,
    i1=1/Math.hypot(zRe,zIm),v1=x.bl*i1/Math.sqrt(zmSq),
    xp1=Math.SQRT2*v1/w,pcu1=i1*i1*x.re;
  let cand=[x.xmax/xp1,40,12/i1,cap===null?Infinity:Math.sqrt(cap/pcu1)];
  let min=Math.min(...cand),ix=cand.indexOf(min);
  const pressure=RHO*w*x.sd*v1*min/(2*PI);
  const pinput=i1*i1*zRe, penergy=pcu1+v1*v1*x.rms;
  if(Math.abs(pinput-penergy)>1e-9*Math.max(1,pinput))throw Error("Electrical-mechanical power balance failed");
  return {spl:20*Math.log10(pressure/PREF),u:min,i:i1*min,x:xp1*min*1000,pcu:pcu1*min*min,lim:["Xpeak","V_rms","I_rms","Pcu_assumed"][ix]};
}

function align(x,vb){
  const qts=1/(1/x.qes+1/x.qms), scale=Math.sqrt(1+x.vas/vb),qtc=qts*scale,fc=x.fs*scale;
  const bi=2-1/(qtc*qtc),di=Math.hypot(bi,2),y=bi>=0?2/(bi+di):(-bi+di)/2;
  return {fc,qtc,f3:fc*Math.sqrt(y)};
}
function main(){
 const base=JSON.parse(fs.readFileSync(path.join(ROOT,"dane/przetworniki/pula_rozszerzona.json"),"utf8"));
 const ext=JSON.parse(fs.readFileSync(path.join(ROOT,"dane/przetworniki/rozszerzenie_FB_20261102_i_pary.json"),"utf8"));
 const dict=new Map(base.drivers.map(p=>[p.candidate_id,p.model]));
 for(const p of ext.new_candidates){if(dict.has(p.candidate_id))throw Error("duplicate id");dict.set(p.candidate_id,p.model);}
 const singles=["C02","C01","C27","C28","C29","C30","C31","C05","C06","C04","C12","C18"],pairs=["C30","C31","C05","C06","C04","C01","C12","C18"];
 const combos=singles.map(id=>({id,topology:"single",connection:"single"}));
 for(const id of pairs)for(const topology of ["normal","isobaric"])for(const connection of ["series","parallel"])combos.push({id,topology,connection});
 const round=(v,n=4)=>Number(v.toFixed(n));const rows=[],alignments=[];
 for(const k of combos){
 const eq=equivalent(dict.get(k.id),k.topology,k.connection);
 for(const volume of ext.comparison.volumes_net_air_l){
 const a=align(eq,volume);
 alignments.push({candidate_id:k.id,topology:k.topology,connection:k.connection,volume_l:volume,fc_hz:round(a.fc),qtc:round(a.qtc),f3_Le0_hz:round(a.f3),vd_catalog_l:round(eq.sd*eq.xmax*1000),nominal_pair_ohm:round(eq.nominal,2)});
 for(const f of ext.comparison.frequencies_hz)for(const power of ext.comparison.copper_power_caps_total_w){
 const z=response(eq,volume,f,power);
 if(z.u>40+1e-8||z.i>12+1e-8||z.x>eq.xmax*1000+1e-8||(power!==null&&z.pcu>power+1e-8))throw Error("limit violation");
 rows.push([k.id,k.topology,k.connection,volume,f,power===null?"none":power,round(z.spl),round(z.u),round(z.i),round(z.x),round(z.pcu),z.lim]);
 }
 }}
 if(rows.length!==3168||alignments.length!==176)throw Error("scenario count mismatch");
 const csv="candidate_id,topology,connection,vb_air_net_l,f_hz,copper_budget_total_w,spl_2pi_1m_db,amp_u_rms_v,amp_i_rms_a,x_peak_mm,p_copper_total_w,limiting_factor\n"+rows.map(z=>z.join(",")).join("\n")+"\n";
 const csvPath=path.join(ROOT,"wyniki/p43_wspolne_scenariusze_3168_20261102.csv");
 fs.writeFileSync(csvPath,csv);
 const summaryPath=path.join(ROOT,"wyniki/p43_duze_vs_para_i_isobaric_20261102.json");
 const old=JSON.parse(fs.readFileSync(summaryPath,"utf8"));
 const pick=(id,top,conn,f)=>rows.find(r=>r[0]===id&&r[1]===top&&r[2]===conn&&r[3]===120&&r[4]===f&&r[5]===50);
 const same=combos.map(k=>({id:k.id,topology:k.topology,connection:k.connection,nominal_pair_ohm:round(equivalent(dict.get(k.id),k.topology,k.connection).nominal,2),vd_catalog_l:round(equivalent(dict.get(k.id),k.topology,k.connection).sd*equivalent(dict.get(k.id),k.topology,k.connection).xmax*1000),spl_db:[20,40,80].map(f=>pick(k.id,k.topology,k.connection,f)[6]),lim:[20,40,80].map(f=>pick(k.id,k.topology,k.connection,f)[11])}));
 if(JSON.stringify(same)!==JSON.stringify(old.selected_120l_50w_20_40_80))throw Error("published numeric summary mismatch");
 if(JSON.stringify(alignments)!==JSON.stringify(old.alignments))throw Error("published alignment mismatch");
 console.log("P43 OK: "+rows.length+" scenarios, "+combos.length+" electric/topology configurations, "+alignments.length+" alignments");
}
if(require.main===module)main();
