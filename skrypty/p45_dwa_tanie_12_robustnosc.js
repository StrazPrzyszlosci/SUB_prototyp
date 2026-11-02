#!/usr/bin/env node
"use strict";
/**
 * P45 - dual affordable 12in sealed driver comparative linear 0D model.
 * Run: node skrypty/p45_dwa_tanie_12_robustnosc.js
 * Verify published datasets: node skrypty/p45_dwa_tanie_12_robustnosc.js --check
 * Full 12870-point CSV: node skrypty/p45_dwa_tanie_12_robustnosc.js --full
 * Built-in Node only. No empirical THD/temperature/CNC claims.
 */
const fs=require("node:fs"),path=require("node:path");
const ROOT=path.resolve(__dirname,"..");
function rn(x,p=5){return Number(x.toFixed(p))}
function nominalPairOhms(d,v){
 let n=d.model.nominal_ohm;
 return v.topology==="single"?n:v.connection==="series"?2*n:v.connection==="parallel"?n/2:n;
}
function point(d,v,vb,f,pcuCap,xFraction,reFactor,cfg){
 const t=d.model; const rho=1.2041,c=343,ref=2e-5,pi=Math.PI,w=2*pi*f;
 const sd=t.sd_cm2*1e-4,cms=t.vas_l*1e-3/(rho*c*c*sd*sd),mms=1/((2*pi*t.fs_hz)**2*cms);
 const BL=Math.sqrt(2*pi*t.fs_hz*mms*t.re_ohm/t.qes),rms=2*pi*t.fs_hz*mms/t.qms;
 const n=v.topology==="single"?1:2;
 let mm=n*mms,cc=cms/n,rr=n*rms, ss=v.topology==="isobaric"?sd:n*sd;
 let re=t.re_ohm,le=t.le_mh*1e-3,bl=BL;
 if(n===2){if(v.connection==="series"){re*=2;le*=2;bl*=2;}else {re/=2;le/=2;}}
 re*=reFactor;
 const mechX=w*mm-(1/cc+rho*c*c*ss*ss/(vb*1e-3))/w;
 const den=rr*rr+mechX*mechX;
 const zRe=re+bl*bl*rr/den,zIm=w*le-bl*bl*mechX/den;
 const i1=1/Math.hypot(zRe,zIm),vel1=bl*i1/Math.sqrt(den);
 const xPeak1=Math.SQRT2*vel1/w;
 const copperOne=i1*i1*re;
 const maxI=v.channels===2?2*cfg.amp.separate_amp_each_current_a_rms:cfg.amp.total_current_a_rms;
 const cap=[
  {name:"Xcatalog",value:t.xmax_mm*1e-3*xFraction/xPeak1},
  {name:"voltage",value:cfg.amp.voltage_v_rms},
  {name:"current",value:maxI/i1},
  {name:"Cu_assumed",value:Math.sqrt(pcuCap/copperOne)}
 ];
 cap.sort((a,b)=>a.value-b.value);
 const U=cap[0].value,I=i1*U,V=vel1*U,X=xPeak1*U,Pcu=copperOne*U*U;
 const p=rho*w*ss*V/(2*pi),spl=20*Math.log10(p/ref);
 const pin=U*U*zRe/(zRe*zRe+zIm*zIm),psloss=rr*V*V;
 const balance=Math.abs(pin-(Pcu+psloss))/Math.max(pin,1e-30);
 const Qms0=2*pi*t.fs_hz*mm/rr,Qes0=2*pi*t.fs_hz*mm*re/(bl*bl),qts=1/(1/Qes0+1/Qms0);
 const fc=t.fs_hz*Math.sqrt(1+(v.topology==="normal"?2:v.topology==="isobaric"?.5:1)*t.vas_l/vb);
 const qtc=qts*fc/t.fs_hz;
 const B=2-1/(qtc*qtc),y=B>=0?2/(B+Math.hypot(B,2)):(-B+Math.hypot(B,2))/2;
 const F3=fc*Math.sqrt(y);
 if(![U,I,V,X,Pcu,p,spl,fc,qtc,F3].every(Number.isFinite))throw Error("non-finite "+v.key);
 if(U>cfg.amp.voltage_v_rms+1e-8 || I>maxI+1e-8 ||X>t.xmax_mm*.001*xFraction+1e-8||Pcu>pcuCap+1e-8||balance>1e-10)throw Error("constraint violation "+v.key);
 return {variant:v.key,vb_l:vb,f_hz:f,pcu_cap_w:pcuCap,xfrac:xFraction,re_factor:reFactor,
 nominal_load_ohm:nominalPairOhms(d,v),spl_db:rn(spl),u_rms_v:rn(U),i_rms_a:rn(I),
 xpeak_mm:rn(X*1e3),copper_w:rn(Pcu),limit:cap[0].name,fc_hz:rn(fc),qtc:rn(qtc),f3_Le0_hz:rn(F3),
 balance_error:balance};
}
function run(models,config){
 const names=new Map(models.map(d=>[d.candidate_id,d]));
 const rows=[], summaries=[],cases={};
 let maxEnergyError=0;
 for(const v of config.variants){
  const d=names.get(v.driver_id);
  if(!d || !d.model || d.model.nominal_ohm==null)throw Error("missing model "+v.driver_id);
  for(const vb of config.volumes_net_air_l){
   for(const cap of config.aggregate_copper_w){
    for(const xf of config.xmax_catalog_fraction){
     for(const re of config.re_multiplier_hot_sensitivity){
      let points=[];
      for(const f of config.frequencies_hz){
       const p=point(d,v,vb,f,cap,xf,re,config);
       rows.push(p);points.push(p);
       maxEnergyError=Math.max(maxEnergyError,p.balance_error);
      }
      const F=[20,25,40,63,80].map(hz=>points.find(x=>x.f_hz===hz)).filter(Boolean);
      summaries.push({variant:v.key,vb_l:vb,pcu_cap_w:cap,xfrac:xf,re_factor:re,
       nominal_ohm:F[0].nominal_load_ohm,
       results:F.map(x=>({f_hz:x.f_hz,spl_db:x.spl_db,limit:x.limit,u_rms_v:x.u_rms_v,
        i_rms_a:x.i_rms_a,x_peak_mm:x.xpeak_mm,cu_w:x.copper_w})),
       qtc:F[0].qtc,f3_Le0_hz:F[0].f3_Le0_hz});
     }
    }
   }
  }
 }
 const baseline=summaries.filter(s=>s.vb_l===120&&s.pcu_cap_w===50&&s.xfrac===1&&s.re_factor===1);
 const conservative=summaries.filter(s=>s.vb_l===120&&s.pcu_cap_w===50&&s.xfrac===.7&&s.re_factor===1.4);
 const ref20=baseline.find(x=>x.variant==="D15_C02").results[0].spl_db;
 const compare=baseline.map(x=>{
  const at=f=>x.results.find(k=>k.f_hz===f);
  const matched=conservative.find(k=>k.variant===x.variant);
  return {variant:x.variant,nominal_load_ohm:x.nominal_ohm,qtc:x.qtc,f3_Le0_hz:x.f3_Le0_hz,
   baseline_spl_20_db:at(20).spl_db,baseline_spl_40_db:at(40).spl_db,active_limit_20:at(20).limit,
   delta_vs_dayton_db20:rn(at(20).spl_db-ref20,3),
   conservative_spl20_db:matched.results.find(k=>k.f_hz===20).spl_db,
   conservative_delta_db20:rn(matched.results[0].spl_db-conservative.find(k=>k.variant==="D15_C02").results[0].spl_db,3)};
 });
 const money={dayton_pln:1613.33,stx500_two_pln:430,stx800_two_pln:1980,
  stx500_saving_pln:rn(1613.33-430,2),stx500_relative_cost_pct:rn(100*430/1613.33,2)};
 const geometry={stx_two_center_separation_mm:530,outer_diameter_mm:332,left_edge_mm:79,right_edge_mm:79,
  between_flange_mm:198,vertical_edge_each_mm:84,cutout_diameter_mm:284,
  mounting_bcd_mm:316,scope:"Kontrola rzutu 2D; nie badanie wręg, terminali, kleju, przenoszenia sił ani CNC."};
 const fullSample=rows.filter(r=>r.pcu_cap_w===50&&r.xfrac===1&&r.re_factor===1);
 return {summary:{study:config.study,date:config.date,
   num_drivers:config.variants.length,grid_count:rows.length,group_count:summaries.length,
   max_relative_energy_balance_error:maxEnergyError,cost_examples:money,geometry,
   comparisons_120l_20_40hz:compare,scenarios:summaries,
   interpretation:["SPL monopola 2π/1m dla osobnego sinusa; nie pokój ani pomiar THD",
    "xfrac=0.7 jest ostrożnościowym budżetem skoku, nie granicą niskiego THD",
    "Re mnożnik to test wrażliwości, nie obliczona temperatura ani kompresja dynamiczna",
    "Pcu=50/100/200 W to wspólne hipotetyczne pułapy strat cewkowych na całą jednostkę",
    "Dwa głośniki normalnie promieniują dwiema membranami; izobaryczny jedną",
    "Dwie membrany w tej samej obudowie nie oznaczają dwóch oddzielnie rozstawionych subwooferów",
    "W przypadku separate wymagane są dwa kanały mocy: napięcie 40V i prąd 12A każdy, limit Pcu nadal łączny",
    "Dane katalogowe nie zastępują BL(x), Cms(x), Le(x,f), termiki, zniekształceń i geometrii"]},
    csvRows:fullSample, allRows:rows};
}
function csvOut(rows){
 const keys=["variant","vb_l","f_hz","pcu_cap_w","xfrac","re_factor","nominal_load_ohm","spl_db","u_rms_v","i_rms_a","xpeak_mm","copper_w","limit","qtc","f3_Le0_hz"];
 return [keys.join(","),...rows.map(x=>keys.map(k=>x[k]).join(","))].join("\n")+"\n";
}
const config=JSON.parse(fs.readFileSync(path.join(ROOT,"dane/konfiguracje/p45_dual12_20261102.json"),"utf8"));
const drivers=JSON.parse(fs.readFileSync(path.join(ROOT,config.source_catalog),"utf8")).drivers;
const outcome=run(drivers,config);
const outputs=[
 ["wyniki/p45_dual12_odpornosc_20261102.json",JSON.stringify(outcome.summary,null,2)+"\n"],
 ["wyniki/p45_dual12_bazowe_715.csv",csvOut(outcome.csvRows)]
];
if(process.argv.includes("--full"))outputs.push(["wyniki/p45_dual12_pelne_12870.csv",csvOut(outcome.allRows)]);
for(const [file,content] of outputs){
 const target=path.join(ROOT,file);
 if(process.argv.includes("--check")){
  if(!fs.existsSync(target)||fs.readFileSync(target,"utf8")!==content)throw Error("Reproduction differs: "+file);
 }else fs.writeFileSync(target,content);
}
console.log("P45 OK",outcome.summary.grid_count,"punktow, maksymalna reszta bilansu",outcome.summary.max_relative_energy_balance_error);
