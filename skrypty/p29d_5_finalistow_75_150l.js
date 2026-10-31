#!/usr/bin/env node
"use strict";
// P29D: synthetic five-driver closed-box finite grid; no safety certification.
const fs=require("node:fs"),path=require("node:path");
const cfg={
  "base": "73e66b05e2d45f29c1e226ea685dcdf0ef893f36",
  "source": "dane/konfiguracje/p22c_dsp_naped_impedancja_20261031.json",
  "volumes": [
    75,
    80,
    100,
    120,
    150
  ],
  "frequencies": [
    20,
    40,
    80
  ],
  "Pcu_scenarios": [
    50,
    100,
    200
  ],
  "Umax_rms": 40,
  "Imax_rms": 12,
  "Rsource": 0.0026,
  "air_rho": 1.2,
  "speed_sound": 343,
  "pressure_reference": 0.00002,
  "drivers": [
    [
      "C02",
      "Dayton RSS390HF-4",
      19.5,
      212,
      829.6,
      3,
      0.92,
      0.5,
      3.02,
      14,
      306,
      15
    ],
    [
      "C11",
      "Dayton RSS390HE-22 series",
      29,
      71.3,
      804,
      4.3,
      2.2,
      0.58,
      4.59,
      27,
      null,
      null
    ],
    [
      "C06",
      "STX W.32.800.8.FCX",
      24,
      96,
      491,
      5.4,
      1.68,
      0.45,
      3.34,
      15,
      null,
      null
    ],
    [
      "N07",
      "PHL 6301MNd",
      36,
      140,
      871,
      5.4,
      1.616,
      0.28,
      3.39,
      10.5,
      150,
      25.5
    ],
    [
      "N05",
      "PURIFI PTT10.0X04-NAB-01",
      24,
      82,
      360,
      3.9,
      0.62,
      0.35,
      5.5,
      14.75,
      98,
      12.8
    ]
  ]
};
function f3(d,V){let fs=d[2],vas=d[3],qes=d[7],qms=d[8],qtc=(1/(1/qes+1/qms))*Math.sqrt(1+vas/V),fc=fs*Math.sqrt(1+vas/V),a=1/(qtc*qtc)-2,y=(a+Math.sqrt(a*a+4))/2;return {Qtc:qtc,fc,F3:fc*Math.sqrt(y)};}
function point(c,d,V,f,heat){
 const [id,name,fs,vas,sdcm,re,lemh,qes,qms,xmax,mms_g,bl_tm]=d;
 const sd=sdcm/10000,rho=c.air_rho,speed=c.speed_sound,w=2*Math.PI*f;
 const cms=vas*.001/(rho*speed*speed*sd*sd);
 const m=(mms_g===null)?1/((2*Math.PI*fs)**2*cms):mms_g*.001;
 const bl=(bl_tm===null)?Math.sqrt(2*Math.PI*fs*m*re/qes):bl_tm;
 const rm=2*Math.PI*fs*m/qms, xm=w*m-1/(w*cms)-sd*sd*rho*speed*speed/(w*V*.001);
 const modZ2=rm*rm+xm*xm, motReal=bl*bl*rm/modZ2,motImag=-bl*bl*xm/modZ2;
 const iOne=1/Math.hypot(re+c.Rsource+motReal,w*lemh*.001+motImag),vOne=bl*iOne/Math.sqrt(modZ2);
 const xmaxPerVolt=Math.SQRT2*vOne/w;
 const capX=(xmax/1000)/xmaxPerVolt, capCu=Math.sqrt(heat/(re*iOne*iOne)),capI=c.Imax_rms/iOne;
 const caps=[capX,capCu,capI,c.Umax_rms],U=Math.min(...caps);
 const limiting=["Xmax_peak","hypothetical_I2R","source_Irms","source_Urms"][caps.indexOf(U)];
 // magnitude of far-field pressure in halfspace for RMS membrane velocity
 const prms=rho*w*sd*vOne*U/(2*Math.PI);
 const spl=20*Math.log10(prms/c.pressure_reference);
 if(U<0||!Number.isFinite(spl))throw Error("nonphysical");
 return {id,model:name,volume_l:V,freq_hz:f,hypothetical_Pcu_W:heat,
  limit:limiting,drive_Vrms:+U.toFixed(5),Pcu_at_Xmax_W:+(re*(iOne*capX)**2).toFixed(4),
  actual_Pcu_W:+(re*(iOne*U)**2).toFixed(4),Xpeak_mm:+(xmaxPerVolt*U*1000).toFixed(5),
  ideal_spl_halfspace_1m_db:+spl.toFixed(5)};
}
function run(c){
 const rows=[],sealed=[];
 for(const d of c.drivers)for(const V of c.volumes){
  const o=f3(d,V);
  sealed.push({id:d[0],model:d[1],Vb_l:V,Qtc:+o.Qtc.toFixed(5),fc_hz:+o.fc.toFixed(5),F3_ideal_hz:+o.F3.toFixed(5),Vd_cm3:+(d[4]*d[9]/10).toFixed(2)});
  for(const f of c.frequencies)for(const heat of c.Pcu_scenarios)rows.push(point(c,d,V,f,heat));
 }
 if(rows.length!==225)throw Error("225 not met");
 for(const z of rows){if(z.Xpeak_mm>c.drivers.find(x=>x[0]===z.id)[9]+1e-4)throw Error("Xmax");
 if(z.actual_Pcu_W>z.hypothetical_Pcu_W+.0002)throw Error("heat");}
 const get=(id,V,f,P=50)=>rows.find(x=>x.id===id&&x.volume_l===V&&x.freq_hz===f&&x.hypothetical_Pcu_W===P);
 if(Math.abs(get("C02",80,20).Pcu_at_Xmax_W-188.111967)>.5||Math.abs(get("C02",120,20).Pcu_at_Xmax_W-83.661115)>.5)throw Error("P22C 80/120 l witnesses mismatched");
 const vtable=c.volumes.map(V=>{const s=sealed.find(x=>x.id==="C02"&&x.Vb_l===V);return {volume_l:V,Qtc:s.Qtc,F3_ideal_hz:s.F3_ideal_hz,copper_W_at_20Hz_Xmax:get("C02",V,20).Pcu_at_Xmax_W,ideal_spl20_Pcu50:get("C02",V,20).ideal_spl_halfspace_1m_db,ideal_spl40_Pcu50:get("C02",V,40).ideal_spl_halfspace_1m_db};});
 return {study:"P29D",date:"2026-10-31",status:"ADDITIONAL 5-DRIVER SMALL-SIGNAL SCREEN ONLY; NOT A NEW FINAL RANKING",config:c,scenarios:rows.length,box_systems:sealed.length,volume_summary:vtable,sealed_response:sealed,sinus_trials:rows,
  assumptions:["Sine stationary small signal; room, DSP boost, distortion and acoustic panel coupling absent.","Pcu=50,100,200 W are hypothetical copper dissipation caps, NOT allowable continuous power.","Same 40 V rms / 12 A rms source cap and 0.0026 ohm Rs for 4 and 8 ohm drivers; does NOT reflect real amplifier 8ohm performance.","Missing Mms and BL reconstructed from Ts identities for C11/C06; manufacturer published Mms/BL used for C02/N07/N05.","Only 5 finalists not 34; historical 27-config Sobol stress test from P29C is more comprehensive at 120l."]};
}
if(require.main===module){
 const result=run(cfg),dest=path.join(__dirname,"..","wyniki","p29d_5_finalistow_75_150l_20261031.json");
 fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,JSON.stringify(result,null,2)+"\n");
 console.log(JSON.stringify({scenarios:result.scenarios,volumes:result.volume_summary},null,2));
}
module.exports={cfg,f3,point,run};
