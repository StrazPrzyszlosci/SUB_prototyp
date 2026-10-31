#!/usr/bin/env node
"use strict";
// P31A: fair electrical caps, 2pi ideal SPL, arbitrary X/heat scenarios.
// NOT a measurement of distortion quality. Node.js >=18, no packages.
const fs=require("node:fs"),path=require("node:path");
const input={
  "drivers": [
    {
      "name": "Dayton RSS315HF-4",
      "fs_hz": 24.2,
      "qes": 0.45,
      "qms": 2.83,
      "vas_l": 84.1,
      "sd_cm2": 514.7,
      "re_ohm": 3.1,
      "le_mh": 0.96,
      "xmax_mm": 14.3,
      "nominal_ohm": 4,
      "rated_w": 400,
      "id": "C01",
      "manufacturer": "Dayton Audio",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Dayton RSS390HF-4",
      "fs_hz": 19.5,
      "qes": 0.5,
      "qms": 3.02,
      "vas_l": 212,
      "sd_cm2": 829.6,
      "re_ohm": 3,
      "le_mh": 0.92,
      "xmax_mm": 14,
      "nominal_ohm": 4,
      "rated_w": 500,
      "id": "C02",
      "manufacturer": "Dayton Audio",
      "price_pln": 1613.33,
      "price_source": "https://loudspeakershop.eu/glosnik-dayton-audio-rss390hf-4-15-reference-sub-p-7660.html"
    },
    {
      "name": "Dayton RSS315HFA-8",
      "fs_hz": 22.2,
      "qes": 0.54,
      "qms": 2.5,
      "vas_l": 97.2,
      "sd_cm2": 506.7,
      "re_ohm": 6.5,
      "le_mh": 1.56,
      "xmax_mm": 14.3,
      "nominal_ohm": 8,
      "rated_w": 400,
      "id": "C03",
      "manufacturer": "Dayton Audio",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "SB Acoustics SB34SWPL76-4",
      "fs_hz": 19,
      "qes": 0.33,
      "qms": 7.7,
      "vas_l": 79,
      "sd_cm2": 458,
      "re_ohm": 3.5,
      "le_mh": 5.3,
      "xmax_mm": 15,
      "nominal_ohm": 4,
      "rated_w": 300,
      "id": "C04",
      "manufacturer": "SB Acoustics",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "STX W.32.500.8.MC_v2",
      "fs_hz": 24,
      "qes": 0.3,
      "qms": 2.48,
      "vas_l": 199,
      "sd_cm2": 491,
      "re_ohm": 5.6,
      "le_mh": 1.27,
      "xmax_mm": 7.5,
      "nominal_ohm": 8,
      "rated_w": 300,
      "id": "C05",
      "manufacturer": "STX",
      "price_pln": 215,
      "price_source": "https://stx.pl/"
    },
    {
      "name": "STX W.32.800.8.FCX",
      "fs_hz": 24,
      "qes": 0.45,
      "qms": 3.34,
      "vas_l": 96,
      "sd_cm2": 491,
      "re_ohm": 5.4,
      "le_mh": 1.68,
      "xmax_mm": 15,
      "nominal_ohm": 8,
      "rated_w": 400,
      "id": "C06",
      "manufacturer": "STX",
      "price_pln": 990,
      "price_source": "https://stx.pl/"
    },
    {
      "name": "STX W.38.500.8.MC",
      "fs_hz": 32,
      "qes": 0.48,
      "qms": 3.17,
      "vas_l": 315,
      "sd_cm2": 855,
      "re_ohm": 5.1,
      "le_mh": 0.74,
      "xmax_mm": 5,
      "nominal_ohm": 8,
      "rated_w": 250,
      "id": "C07",
      "manufacturer": "STX",
      "price_pln": null,
      "price_source": "https://stx.pl/"
    },
    {
      "name": "STX W.38.800.8.MC",
      "fs_hz": 28,
      "qes": 0.27,
      "qms": 3.71,
      "vas_l": 247,
      "sd_cm2": 850,
      "re_ohm": 5.7,
      "le_mh": 3.68,
      "xmax_mm": 8,
      "nominal_ohm": 8,
      "rated_w": 500,
      "id": "C08",
      "manufacturer": "STX",
      "price_pln": 578,
      "price_source": "https://stx.pl/"
    },
    {
      "name": "Scan-Speak 30W/4558T00",
      "fs_hz": 17,
      "qes": 0.34,
      "qms": 5.01,
      "vas_l": 197,
      "sd_cm2": 466,
      "re_ohm": 2.6,
      "le_mh": 0.83,
      "xmax_mm": 12.5,
      "nominal_ohm": 4,
      "rated_w": 150,
      "id": "C09",
      "manufacturer": "Scan-Speak",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Scan-Speak 32W/4878T00",
      "fs_hz": 18,
      "qes": 0.33,
      "qms": 7,
      "vas_l": 203.9,
      "sd_cm2": 526,
      "re_ohm": 3.1,
      "le_mh": 0.5,
      "xmax_mm": 14,
      "nominal_ohm": 4,
      "rated_w": 200,
      "id": "C10",
      "manufacturer": "Scan-Speak",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Dayton RSS390HE-22 seria",
      "fs_hz": 29,
      "qes": 0.58,
      "qms": 4.59,
      "vas_l": 71.3,
      "sd_cm2": 804,
      "re_ohm": 4.3,
      "le_mh": 2.2,
      "xmax_mm": 27,
      "nominal_ohm": 4,
      "rated_w": 800,
      "id": "C11",
      "manufacturer": "Dayton Audio",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "SEAS L26RO4Y XM004-04",
      "fs_hz": 26,
      "qes": 0.29,
      "qms": 3.94,
      "vas_l": 40,
      "sd_cm2": 342,
      "re_ohm": 3.5,
      "le_mh": 2.33,
      "xmax_mm": 15,
      "nominal_ohm": 4,
      "rated_w": 250,
      "id": "C12",
      "manufacturer": "SEAS",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "BMS 12N630 8ohm",
      "fs_hz": 28.6,
      "qes": 0.35,
      "qms": 6.24,
      "vas_l": 85.5,
      "sd_cm2": 498,
      "re_ohm": 6,
      "le_mh": 0.68,
      "xmax_mm": 8,
      "nominal_ohm": 8,
      "rated_w": 600,
      "id": "C13",
      "manufacturer": "BMS",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "BMS 15S430v2",
      "fs_hz": 39.8,
      "qes": 0.27,
      "qms": 6.6,
      "vas_l": 135,
      "sd_cm2": 897,
      "re_ohm": 5,
      "le_mh": 0.73,
      "xmax_mm": 7.5,
      "nominal_ohm": 8,
      "rated_w": 1200,
      "id": "C14",
      "manufacturer": "BMS",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "FaitalPRO 15XL1400 8ohm",
      "fs_hz": 38,
      "qes": 0.34,
      "qms": 10.4,
      "vas_l": 91.2,
      "sd_cm2": 841,
      "re_ohm": 5.4,
      "le_mh": 1.6,
      "xmax_mm": 12.92,
      "nominal_ohm": 8,
      "rated_w": 1400,
      "id": "C15",
      "manufacturer": "FaitalPRO",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "LaVoce WAF154.00",
      "fs_hz": 38,
      "qes": 0.31,
      "qms": 5.74,
      "vas_l": 109.68,
      "sd_cm2": 855,
      "re_ohm": 5.8,
      "le_mh": 1.88,
      "xmax_mm": 12.1,
      "nominal_ohm": 8,
      "rated_w": 1500,
      "id": "C16",
      "manufacturer": "LaVoce",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Peerless XXLS 830844 4ohm",
      "fs_hz": 17.7,
      "qes": 0.2,
      "qms": 8.21,
      "vas_l": 156.5,
      "sd_cm2": 466,
      "re_ohm": 2.8,
      "le_mh": 4.2,
      "xmax_mm": 12.5,
      "nominal_ohm": 4,
      "rated_w": 175,
      "id": "C17",
      "manufacturer": "Peerless",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "PURIFI PTT10.0X04-NAB-01",
      "fs_hz": 24,
      "qes": 0.35,
      "qms": 5.5,
      "vas_l": 82,
      "sd_cm2": 360,
      "re_ohm": 3.9,
      "le_mh": 0.62,
      "xmax_mm": 14.75,
      "nominal_ohm": 4,
      "rated_w": 135,
      "id": "C18",
      "manufacturer": "PURIFI",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Dayton RSS390HO-4",
      "fs_hz": 21.5,
      "qes": 0.35,
      "qms": 3.69,
      "vas_l": 168,
      "sd_cm2": 829.6,
      "re_ohm": 3.2,
      "le_mh": 1.79,
      "xmax_mm": 12,
      "nominal_ohm": 4,
      "rated_w": 800,
      "id": "C19",
      "manufacturer": "Dayton Audio",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Dayton UMII12-22 seria",
      "fs_hz": 31,
      "qes": 0.71,
      "qms": 2.75,
      "vas_l": 53,
      "sd_cm2": 528,
      "re_ohm": 4.2,
      "le_mh": 0.66,
      "xmax_mm": 22,
      "nominal_ohm": 4,
      "rated_w": 800,
      "id": "C20",
      "manufacturer": "Dayton Audio",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Dayton UMII15-22 seria",
      "fs_hz": 29,
      "qes": 1,
      "qms": 2.34,
      "vas_l": 96,
      "sd_cm2": 791,
      "re_ohm": 4.2,
      "le_mh": 0.7,
      "xmax_mm": 24,
      "nominal_ohm": 4,
      "rated_w": 900,
      "id": "C21",
      "manufacturer": "Dayton Audio",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Dayton RSS315HO-4",
      "fs_hz": 26.2,
      "qes": 0.33,
      "qms": 3.63,
      "vas_l": 53.7,
      "sd_cm2": 514.7,
      "re_ohm": 3.2,
      "le_mh": 1.75,
      "xmax_mm": 12.3,
      "nominal_ohm": 4,
      "rated_w": 700,
      "id": "C22",
      "manufacturer": "Dayton Audio",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Eminence LAB12 6ohm",
      "fs_hz": 22,
      "qes": 0.39,
      "qms": 13.32,
      "vas_l": 125.2,
      "sd_cm2": 506.7,
      "re_ohm": 4.29,
      "le_mh": 1.48,
      "xmax_mm": 13,
      "nominal_ohm": 6,
      "rated_w": 400,
      "id": "C23",
      "manufacturer": "Eminence",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "Eminence LAB15 6ohm",
      "fs_hz": 28,
      "qes": 0.37,
      "qms": 5.36,
      "vas_l": 103.61,
      "sd_cm2": 823.7,
      "re_ohm": 4.9,
      "le_mh": 3.23,
      "xmax_mm": 11.8,
      "nominal_ohm": 6,
      "rated_w": 600,
      "id": "C24",
      "manufacturer": "Eminence",
      "price_pln": null,
      "price_source": null
    },
    {
      "name": "SB Acoustics SB34SWNRX-S75-6",
      "fs_hz": 19,
      "qes": 0.34,
      "qms": 5,
      "vas_l": 164,
      "sd_cm2": 508,
      "re_ohm": 4.5,
      "le_mh": 3,
      "xmax_mm": 11.25,
      "nominal_ohm": 6,
      "id": "C25",
      "manufacturer": "SB Acoustics",
      "price_pln": null
    },
    {
      "fs_hz": 27.5,
      "qes": 0.52,
      "qms": 5.62,
      "vas_l": 43,
      "sd_cm2": 458,
      "xmax_mm": 15,
      "configuration_id": "C26P",
      "connection": "parallel",
      "name": "SB Acoustics SB34SWPL76-3-DV parallel",
      "re_ohm": 1.25,
      "nominal_ohm": 1.5,
      "le_mh": 1.4,
      "catalog_bl_tm": 9.7,
      "id": "C26P",
      "manufacturer": "SB Acoustics",
      "price_pln": null
    },
    {
      "fs_hz": 27.5,
      "qes": 0.52,
      "qms": 5.62,
      "vas_l": 43,
      "sd_cm2": 458,
      "xmax_mm": 15,
      "configuration_id": "C26S",
      "connection": "series",
      "name": "SB Acoustics SB34SWPL76-3-DV series",
      "re_ohm": 5,
      "nominal_ohm": 6,
      "le_mh": 6.1,
      "catalog_bl_tm": 19.5,
      "id": "C26S",
      "manufacturer": "SB Acoustics",
      "price_pln": null
    },
    {
      "id": "N01",
      "manufacturer": "Great Plains Audio (GPA)",
      "name": "416-8B",
      "fs_hz": 22.88,
      "vas_l": 517.7,
      "sd_cm2": 823.7,
      "re_ohm": 7.27,
      "le_mh": null,
      "qes": 0.336,
      "qms": 8.188,
      "xmax_mm": 4,
      "nominal_ohm": 8,
      "price_pln": null,
      "source_note": "https://greatplainsacoustics.com/products/416-8b-alnico-16-in-low-frecuency-loudspeaker-each"
    },
    {
      "id": "N02",
      "manufacturer": "VOLT Loudspeakers",
      "name": "RV3863 8 ohm",
      "fs_hz": 29,
      "vas_l": 205,
      "sd_cm2": 760,
      "re_ohm": 5.8,
      "le_mh": 3.1,
      "qes": 0.33,
      "qms": 4.03,
      "xmax_mm": 7.5,
      "nominal_ohm": 8,
      "price_pln": null,
      "source_note": "https://voltloudspeakers.co.uk/speaker/rv3863-15inch/"
    },
    {
      "id": "N06",
      "manufacturer": "Kartesian",
      "name": "Wom265_vKi-6",
      "fs_hz": 30,
      "vas_l": 114.6,
      "sd_cm2": 390,
      "re_ohm": 4,
      "le_mh": 0.11,
      "qes": 0.37,
      "qms": 4.8,
      "xmax_mm": 10,
      "nominal_ohm": 6,
      "price_pln": null,
      "source_note": "https://www.kartesian-acoustic.com/products"
    },
    {
      "id": "N07",
      "manufacturer": "PHL Audio",
      "name": "6301MNd",
      "fs_hz": 36,
      "vas_l": 140,
      "sd_cm2": 871,
      "re_ohm": 5.4,
      "le_mh": 1.616,
      "qes": 0.28,
      "qms": 3.39,
      "xmax_mm": 10.5,
      "nominal_ohm": 8,
      "price_pln": null,
      "source_note": "https://phlaudio.com/products/index.html"
    },
    {
      "id": "N08",
      "manufacturer": "ETON Soundsysteme",
      "name": "Symphony II 12-212/C8/62 HEX",
      "fs_hz": 24,
      "vas_l": 176,
      "sd_cm2": 515,
      "re_ohm": 6.2,
      "le_mh": 1.57,
      "qes": 0.32,
      "qms": 7.15,
      "xmax_mm": 8.5,
      "nominal_ohm": 8,
      "price_pln": null,
      "source_note": "https://eton-hifi.com/en/products/symphony-ii-12-212-c8-62-hex"
    },
    {
      "id": "N09",
      "manufacturer": "Davis Acoustics",
      "name": "39 GPA 15 (paper)",
      "fs_hz": 27.75,
      "vas_l": 360,
      "sd_cm2": 892,
      "re_ohm": 4.93,
      "le_mh": null,
      "qes": 0.366,
      "qms": 6.49,
      "xmax_mm": 4,
      "nominal_ohm": 6.5,
      "price_pln": null,
      "source_note": "https://davis-acoustics.com/en/15-inches-loudspeakers/"
    }
  ],
  "volumes_l": [
    100,
    120
  ],
  "frequencies_hz": [
    20,
    25,
    30,
    35,
    40,
    50,
    60,
    70,
    80
  ],
  "x_fractions": [
    0.5,
    0.7,
    1
  ],
  "thermal_budgets_copper_W": [
    50,
    100
  ],
  "voltage_limit_vrms": 40,
  "current_limit_arms": 12,
  "thermal_variations": [
    {
      "name": "nominal",
      "bl": 1,
      "re": 1,
      "mms": 1,
      "cms": 1
    },
    {
      "name": "BL-10pct",
      "bl": 0.9,
      "re": 1,
      "mms": 1,
      "cms": 1
    },
    {
      "name": "Re+5pct",
      "bl": 1,
      "re": 1.05,
      "mms": 1,
      "cms": 1
    },
    {
      "name": "Mms+10pct Cms-15pct",
      "bl": 1,
      "re": 1,
      "mms": 1.1,
      "cms": 0.85
    },
    {
      "name": "BL+10pct",
      "bl": 1.1,
      "re": 1,
      "mms": 1,
      "cms": 1
    }
  ],
  "price_snapshot_date": "2026-10-31"
};
function pre(d,v,variation){
 const rho=1.2,c=343,fs=d.fs_hz,sd=d.sd_cm2/1e4,re=d.re_ohm*variation.re,Le=(d.le_mh??0)/1000;
 if(![fs,sd,re,d.qes,d.qms,d.vas_l,d.xmax_mm].every(x=>x>0))return null;
 const Cms0=(d.vas_l/1000)/(rho*c*c*sd*sd);
 const Mms0=1/((2*Math.PI*fs)**2*Cms0);
 const Mms=(d.mms_g_published??d.mms_g??Mms0*1000)/1000*variation.mms;
 const Cms=Cms0*variation.cms, Rms=2*Math.PI*fs*Mms/d.qms;
 const BL=(d.bl_tm_published??d.bl_tm??Math.sqrt(2*Math.PI*fs*Mms0*d.re_ohm/d.qes))*variation.bl;
 return {rho,c,fs,sd,re,Le,Cms,Mms,Rms,BL,v,missingLe:d.le_mh==null};
}
function mm(x){return x*1000;}
function response(d,v,f,xfrac,Pcu,variation){
 const x=pre(d,v,variation);if(!x)return null;
 const w=2*Math.PI*f,react=w*x.Mms-1/(w*x.Cms)-x.sd*x.sd*x.rho*x.c*x.c/(w*v/1000),mech=Math.hypot(x.Rms,react);
 const zre=x.re+x.BL*x.BL*x.Rms/(mech*mech),zim=w*x.Le-x.BL*x.BL*react/(mech*mech);
 const Iper=1/Math.hypot(zre,zim);const Vper=x.BL*Iper/mech;const peakXper=Math.SQRT2*Vper/w;
 const maxU=Math.min(40,12/Iper,(xfrac*d.xmax_mm/1000)/peakXper,Math.sqrt(Pcu/(x.re*Iper*Iper)));
 const I=Iper*maxU,vel=Vper*maxU;
 const spl=20*Math.log10((x.rho*f*x.sd*vel)/20e-6);
 const splTarget=95,reqU=maxU*10**((splTarget-spl)/20);
 return {spl:spl,f,limU:maxU,I,copperW:I*I*x.re,peakX:mm(peakXper*maxU),meets95:spl>=95,
  reqU95:reqU,reqCopper95:(reqU*Iper)**2*x.re,
  reqX95:mm(peakXper*reqU)};
}
function run(inp){
 const scenarios=[],rows=[],num=inp.drivers.length;
 for(const d of inp.drivers)for(const v of inp.volumes_l){
  const by=[];
  for(const xf of inp.x_fractions)for(const P of inp.thermal_budgets_copper_W)for(const variation of inp.thermal_variations){
   const bands=inp.frequencies_hz.map(f=>response(d,v,f,xf,P,variation));
   if(bands.some(x=>!x))throw Error("invalid profile "+d.id);
   const min=Math.min(...bands.map(x=>x.spl)),low=bands[0],freqAtMin=bands.reduce((a,b)=>b.spl<a.spl?b:a);
   const sc={id:d.id,name:d.name,volume_l:v,X_fraction:xf,P_copper_W:P,stress:variation.name,
    min_20_80_db:+min.toFixed(3),limiting_f_hz:freqAtMin.f,
    spl20_db:+low.spl.toFixed(3),spl40_db:+bands[4].spl.toFixed(3),
    meets_95_20Hz:low.spl>=95,
    copper_to_reach_95at20_W:+low.reqCopper95.toFixed(3),
    xpk_to_reach_95at20_mm:+low.reqX95.toFixed(3)};
   scenarios.push(sc);by.push(sc);
  }
  const subset=by.filter(s=>s.X_fraction===.7&&s.P_copper_W===50);
  const nominal=subset.find(s=>s.stress==="nominal");
  const stressMin=Math.min(...subset.map(s=>s.min_20_80_db));
  const stress20=Math.min(...subset.map(s=>s.spl20_db));
  rows.push({id:d.id,name:d.name,manufacturer:d.manufacturer,volume_l:v,price_pln:d.price_pln,
   nominal_min_20_80_db:nominal.min_20_80_db,
   stress_min_20_80_db:+stressMin.toFixed(3),
   nominal_spl20_db:nominal.spl20_db,
   stress_spl20_db:+stress20.toFixed(3),
   nominal_copper95W:nominal.copper_to_reach_95at20_W,
   nominal_xpk95mm:nominal.xpk_to_reach_95at20_mm,
   Vd_cm3:+(d.sd_cm2*d.xmax_mm/10).toFixed(2),
   missing_Le:d.le_mh==null,
   other_invalid: false
  });
 }
 if(rows.length!==66||scenarios.length!==1980)throw Error("grid count "+rows.length+" "+scenarios.length);
 const ranked120=rows.filter(x=>x.volume_l===120).sort((a,b)=>b.stress_min_20_80_db-a.stress_min_20_80_db);
 const budget120=rows.filter(x=>x.volume_l===120&&x.price_pln!=null).sort((a,b)=>a.price_pln-b.price_pln);
 const best=ranked120.slice(0,12);
 return {study:"P31A",date:"2026-10-31",status:"MODEL-ONLY NOT THD/QUALITY RANKING",parameters:{...inp,drivers:undefined},driver_count:num,scenarios:scenarios.length,
  inputs:inp.drivers,rows,ranked120:best,budget120,scenarios_table:scenarios,
  caveats:["No measured THD/IMD or loudspeaker distortion quality; Xmax margin 0.5/0.7/1.0 is arbitrary proxy, not product-confirmed linearity.",
  "Common 40V/12A electrical caps assume same amplifier across 4/6/8/1.5Ω; real module performance may differ, especially C26P parallel 1.5Ω.",
  "Copper heat budget 50/100W is a study assumption, not actual allowable heating.",
  "Missing Le is set to zero as provisional, cases N01/N09 unsuitable for authoritative ranking.",
  "The 5 stress cases are correlated synthetic parameter choices, not uncertainty bounding or real manufacturing distribution.",
  "2pi 1m RMS piston output is NOT actual SPL in room or pure bass 20Hz.",
  "Price samples snapshot from individual PL retailers/manufacturer, excluding costs of amplifier, power and enclosure."]};
}
if(require.main===module){
 const out=run(input),p=path.join(__dirname,"..","wyniki","p31a_33_konfiguracje_1980_przypadkow_20261031.json");
 fs.mkdirSync(path.dirname(p),{recursive:true});
 fs.writeFileSync(p,JSON.stringify(out,null,2)+"\n");
 console.log(JSON.stringify({drivers:out.driver_count,scenarios:out.scenarios,ranked:out.ranked120.slice(0,10),budget:out.budget120},null,2));
}
module.exports={input,pre,response,run};
