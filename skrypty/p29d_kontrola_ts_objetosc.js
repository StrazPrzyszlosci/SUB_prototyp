#!/usr/bin/env node
"use strict";
// P29D: reproducible ideal sealed high-pass T/S envelope (NO DSP or measured THD).
const fs=require("node:fs"),path=require("node:path");
const drivers=[
  {
    "id": "C02",
    "name": "Dayton RSS390HF-4",
    "fs": 19.5,
    "qts": 0.43,
    "vas": 212,
    "sd": 829.6,
    "xmax": 14,
    "source": "https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf"
  },
  {
    "id": "C11",
    "name": "Dayton RSS390HE-22 (series nominal T/S)",
    "fs": 29,
    "qts": 0.51,
    "vas": 71.3,
    "sd": 804,
    "xmax": 27,
    "source": "https://daytonaudio.vortxhosting.com/images/resources/295-292--dayton-audio-rss390he-22-spec-sheet.pdf"
  },
  {
    "id": "C19",
    "name": "Dayton RSS390HO-4",
    "fs": 21.5,
    "qts": 0.32,
    "vas": 168,
    "sd": 829.6,
    "xmax": 12,
    "source": "https://www.daytonaudio.com/images/resources/295-469-dayton-audio-rss390ho-4-specifications-46177.pdf"
  },
  {
    "id": "C06",
    "name": "STX W.32.800.8.FCX",
    "fs": 24,
    "qts": 0.39,
    "vas": 96,
    "sd": 491,
    "xmax": 15,
    "source": "https://stx.pl/manufacturer/stx/w-32-800-8-fcx.html"
  },
  {
    "id": "N07",
    "name": "PHL 6301MNd",
    "fs": 36,
    "qts": 0.26,
    "vas": 140,
    "sd": 871,
    "xmax": 10.5,
    "source": "https://www.phlaudio.com/fileadmin/user_upload/phl_audio/6301MNd_SpecSheet.pdf"
  }
];
const volumes_l=[75,80,100,120,150];
function sealed(t,v){
 const r=Math.sqrt(1+t.vas/v),fc=t.fs*r,qtc=t.qts*r,coeff=2-1/(qtc*qtc);
 const y=(-coeff+Math.sqrt(coeff*coeff+4))/2;
 const f3=fc*Math.sqrt(y);
 function db(f){const z=f/fc; return 20*Math.log10(z*z/Math.sqrt((1-z*z)**2+(z/qtc)**2));}
 const ret={id:t.id,model:t.name,volume_net_l:v,qtc:+qtc.toFixed(5),fc_hz:+fc.toFixed(4),f3_hz:+f3.toFixed(4),
  relative_gain_20Hz_db:+db(20).toFixed(4),
  Vd_cc:+(t.sd*t.xmax/10).toFixed(2)};
 if(Math.abs(db(f3)+10*Math.log10(2))>.0000001)throw Error("F3 root check");
 return ret;
}
function main(){
 const rows=drivers.flatMap(d=>volumes_l.map(v=>sealed(d,v)));
 if(rows.length!==25)throw Error("Wrong case count");
 const expected={C02:32.07,C11:40.56,C19:52.36,C06:46.88,N07:118.80};
 for(const r of rows.filter(x=>x.volume_net_l===120))
  if(Math.abs(r.f3_hz-expected[r.id])>.15)throw Error("Inconsistent manufacturer T/S estimate for "+r.id);
 const data={study:"P29D",date:"2026-10-31",model:"ideal lossless sealed second-order",
  case_count:rows.length,drivers,volumes_l,rows,
  warnings:[
  "Do not merge P29A 27-configuration stress ranking with 33-configuration linear screening as if identical methods.",
  "F3 values are relative to asymptotic high-frequency passband in lossless, infinite-baffle single-driver model, NOT measured F3, in-room F3, high-power level nor Dirac/FIR preset.",
  "PHL lower Qts strongly penalizes native deep sealed F3; amp/DSP EQ might reshape it, but power/X/THD and noise require full re-evaluation.",
  "RSS390HE-22 listed nominal series T/S from manufacturer; dual coils, gain and amplifier current require explicit wiring check.",
  "20Hz comparison of normalized response is NOT maximum clean 20Hz SPL; excursion-limited radiation depends on Sd*Xmax and distortion.",
  "Actual P29 cabinet 880x480x500 body only, depth <=500 inclusive of grill/connections; insert collisions if reducing depth."
]};
 const target=path.join(__dirname,"..","wyniki","p29d_t_s_objetosc_20261031.json");
 fs.mkdirSync(path.dirname(target),{recursive:true});
 fs.writeFileSync(target,JSON.stringify(data,null,2)+"\n");
 console.log(JSON.stringify({case_count:rows.length,volume120:rows.filter(x=>x.volume_net_l===120)},null,2));
}
if(require.main===module)main();
module.exports={sealed,drivers,volumes_l,main};
