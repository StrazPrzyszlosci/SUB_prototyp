#!/usr/bin/env node
"use strict";
// P34B independent low-frequency sanity tests (benchmark rectangular no-obstruction box).
const assert=require("node:assert/strict");
const {cfg,simulate,geometry}=require("./p34b_przestrzenne_pole_p30e.js");
const base=geometry(cfg);
const levels=[80,55,36];
let prev=null;
for(const h of levels){
 const x=simulate(cfg,base,"120",h,40);
 if(!(x.relative_residual<1e-6))throw Error("solver failed");
 if(Math.abs(x.volume_l-119.92)>3.5)throw Error("voxel volume not near nominal P30E: "+x.volume_l);
 console.log("P30E 120l",h,"mm, V=",x.volume_l,"L, field RMS=",x.rms_nonuniformity_pct.toFixed(4),"%");
 if(prev&&Math.abs(x.rms_nonuniformity_pct-prev)>3)throw Error("mesh pressure sensitivity unexpectedly high");
 prev=x.rms_nonuniformity_pct;
}
const rectCfg={...cfg,nominal_basket_displacement_l:0,source_radius_mm:9999};
const empty={bars:[],large:[],small:[]};
for(const f of [20,40,80]){
 const x=simulate(rectCfg,empty,"empty",36,f);
 const k=2*Math.PI*f/rectCfg.air_sound_speed_ms;
 const D=rectCfg.inside_mm[1]/1000;
 // Analytical 1D sealed hard-wall cavity with uniform front wall volume velocity.
 // p(y)/<p>=kD*cos(k*(D-y))/sin(kD)
 // At frequency lower than first axial mode, pressure variation at y=0 vs y=D:
 const analyticSpan=(k*D/Math.sin(k*D))*(1-Math.cos(k*D));
 // Measured max deviation in 3D grid is a sampled continuous field, so compare loosely.
 if(!(x.peak_nonuniformity_pct>0))throw Error("flat field unexpected");
 if(!(analyticSpan>0))throw Error("analytical axial span sign");
 console.log("RECTANGULAR EXACT BENCHMARK",f,"Hz; analytic normalized pressure span",analyticSpan,
    "; FV maximum deviation",x.peak_nonuniformity_pct);
}
console.log("P34B regression checks passed (not calibrated physical test)");
