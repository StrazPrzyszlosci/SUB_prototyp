#!/usr/bin/env node
"use strict";
/* P43: research-only 2D shortest paths around aperture and 3DOF elastic support-loss.
 * No 3D basket model, no contact FEM, no structural certification, NOT CNC.
 * Regenerate: node skrypty/p43_trasy_i_awarie_podpor.js
 * Inputs: P38 dimensions and P42 support stations, revision 6a42868cbec6d85bbbee0d1a05a1e7d06df41f57.
 * No third-party modules. JS deterministic IEEE-754 arithmetic.
 */
const fs=require("node:fs"),path=require("node:path");
const cfg={
  "date": "2026-11-01",
  "parent_commit": "6a42868cbec6d85bbbee0d1a05a1e7d06df41f57",
  "units": {
    "length": "mm",
    "force": "N",
    "stiffness": "N/mm",
    "angle": "rad"
  },
  "center": [
    231,
    250
  ],
  "aperture_r": 177.9,
  "bcd_r": 184,
  "flange_r": 194.2,
  "front": [
    1020,
    500
  ],
  "anchors": {
    "A": [
      [
        75,
        45
      ],
      [
        425,
        45
      ],
      [
        75,
        455
      ],
      [
        425,
        455
      ]
    ],
    "B": [
      [
        176,
        37
      ],
      [
        286,
        37
      ],
      [
        176,
        463
      ],
      [
        286,
        463
      ]
    ]
  },
  "width": [
    4,
    8,
    10
  ],
  "margin": [
    0,
    1,
    2
  ],
  "masses": [
    13.61,
    15
  ],
  "accel": [
    1,
    5,
    10
  ],
  "ecc": [
    90,
    120,
    180
  ],
  "pattern": [
    "equal",
    "left_half",
    "first_quarter"
  ],
  "dirs": [
    "X",
    "Z",
    "Y"
  ],
  "k": 1000,
  "g0": 9.80665
};
function r4(x){return Math.round(x*10000)/10000}
function len(a,b){return Math.hypot(a[0]-b[0],a[1]-b[1])}
function centerDistSeg(a,b,c){const dx=b[0]-a[0],dz=b[1]-a[1],l=dx*dx+dz*dz,t=Math.max(0,Math.min(1,-((a[0]-c[0])*dx+(a[1]-c[1])*dz)/(l||1)));return Math.hypot(a[0]+t*dx-c[0],a[1]+t*dz-c[1])}
function route(a,b,c,w,m){
 const R=c.aperture_r+w/2+m,center=c.center,da=len(a,center),db=len(b,center);
 if(da<R-1e-9||db<R-1e-9)return {ok:false,reason:"endpoint_inside_clearance_disk",R};
 const inside=(p)=>p[0]>=w/2+m-1e-8&&p[0]<=c.front[0]-w/2-m+1e-8&&p[1]>=w/2+m-1e-8&&p[1]<=c.front[1]-w/2-m+1e-8;
 if(!inside(a)||!inside(b))return {ok:false,reason:"endpoint_outside_face",R};
 if(centerDistSeg(a,b,center)>=R-1e-8)return {ok:true,kind:"straight",length:len(a,b),R,points:[a,b],arc_length:0};
 const angA=Math.atan2(a[1]-center[1],a[0]-center[0]),angB=Math.atan2(b[1]-center[1],b[0]-center[0]);
 const aa=Math.acos(Math.max(-1,Math.min(1,R/da))),ab=Math.acos(Math.max(-1,Math.min(1,R/db)));
 const mod=x=>(x%(2*Math.PI)+2*Math.PI)%(2*Math.PI);
 const candidates=[];
 for(const dir of [1,-1]){
   const tA=angA+dir*aa,tB=angB-dir*ab,delta=dir===1?mod(tB-tA):mod(tA-tB);
   const pts=[a,[center[0]+R*Math.cos(tA),center[1]+R*Math.sin(tA)]];
   const steps=Math.max(1,Math.ceil(R*delta/1.5));
   for(let j=1;j<=steps;j++){const t=tA+dir*delta*j/steps;pts.push([center[0]+R*Math.cos(t),center[1]+R*Math.sin(t)]);}
   pts.push(b);
   if(!pts.every(inside))continue;
   const d=Math.sqrt(Math.max(0,da*da-R*R))+Math.sqrt(Math.max(0,db*db-R*R))+R*delta;
   candidates.push({ok:true,kind:"tangent_arc_tangent",length:d,R,points:pts,arc_length:R*delta,direction:dir});
 }
 if(!candidates.length)return {ok:false,reason:"detour_outside_face",R};
 return candidates.sort((x,y)=>x.length-y.length)[0];
}
function studyRoutes(c){
 const bolts=Array.from({length:8},(_,i)=>[c.center[0]+c.bcd_r*Math.cos(i*Math.PI/4),c.center[1]+c.bcd_r*Math.sin(i*Math.PI/4)]);
 const selected=[],groups=[],candidates=576;
 for(const variant of ["A","B"])for(const w of c.width)for(const m of c.margin){
   const rows=[];
   for(let i=0;i<8;i++){
     const cand=c.anchors[variant].map((a,j)=>{const rt=route(bolts[i],a,c,w,m);return {anchor:j+1,direct_length:len(bolts[i],a),ok:rt.ok,reason:rt.reason||"",route_type:rt.kind||"",length:rt.ok?rt.length:null,arc_length:rt.ok?rt.arc_length:null,points:rt.ok?rt.points:null};});
     const optimal=cand.filter(r=>r.ok).sort((a,b)=>a.length-b.length)[0];
     const nearest=cand.slice().sort((a,b)=>a.direct_length-b.direct_length)[0];
     const row={variant,width_mm:w,clearance_mm:m,bolt:i+1,
       nearest_straight_violates_disk:centerDistSeg(bolts[i],c.anchors[variant][nearest.anchor-1],c.center)<c.aperture_r+w/2+m-1e-8,
       nearest_anchor:nearest.anchor,selected_anchor:optimal?.anchor||null,
       selected_path_kind:optimal?.route_type||"infeasible",
       selected_path_length_mm:optimal?r4(optimal.length):null,
       direct_euclid_mm:optimal?r4(optimal.direct_length):null,
       excess_length_mm:optimal?r4(optimal.length-optimal.direct_length):null,
       selected_arc_length_mm:optimal?r4(optimal.arc_length):null,
       reason:optimal?"":cand.every(q=>q.reason==="endpoint_inside_clearance_disk")?"endpoint_inside_clearance_disk":"no_clear_route"};
     if(optimal){for(const p of optimal.points){if(len(p,c.center)<c.aperture_r+w/2+m-1e-6)throw Error("route violates disk");}}
     rows.push(row);
   }
   const feasible=rows.filter(x=>x.selected_anchor!==null);
   groups.push({variant,width_mm:w,clearance_mm:m,feasible_bolts:feasible.length,
     nearest_direct_collisions:rows.filter(x=>x.nearest_straight_violates_disk).length,
     routed_detours:feasible.filter(x=>x.selected_path_kind!=="straight").length,
     max_excess_length_mm:feasible.length?r4(Math.max(...feasible.map(x=>x.excess_length_mm))):null,
     mean_excess_length_mm:feasible.length?r4(feasible.reduce((s,x)=>s+x.excess_length_mm,0)/feasible.length):null});
   selected.push(...rows);
 }
 if(selected.length!==144||groups.length!==18)throw Error("route counts wrong");
 return {bolts,selected,groups,candidates,selected_count:144,geometry_source:"P38/P42 (manufacturer-sourced flange, bolt circle, cutout; A/B hypothetical anchors)",notes:["Only 2D clearance of ideal continuous links (centerlines with radius width/2), not physical connections.","All 8 start centers lie INSIDE the manufacturer flange projected disk (R194.2mm), so a planar viable path is not a 3D fastening solution.","No real screw head/washer, flange fixing, cabinet panel load transfer, basket profile, module/brace collision or tool access.","Margins 0/1/2mm are hypothetical screens, not manufacturing tolerances."]};
}
function gauss(A,b){
 const M=A.map((r,i)=>[...r,b[i]]);for(let i=0;i<3;i++){let pivot=i;for(let j=i+1;j<3;j++)if(Math.abs(M[j][i])>Math.abs(M[pivot][i]))pivot=j;
 if(Math.abs(M[pivot][i])<1e-9)return null;
 [M[i],M[pivot]]=[M[pivot],M[i]];let k=M[i][i];for(let h=i;h<4;h++)M[i][h]/=k;
 for(let j=0;j<3;j++){if(j===i)continue;const q=M[j][i];for(let h=i;h<4;h++)M[j][h]-=q*M[i][h];}}
 return M.map(r=>r[3]);
}
function support(c,variant,mass,acc,e,pattern,axis,failed){
 const pts=c.anchors[variant].map((p,i)=>({i:i+1,x:p[0]-c.center[0],z:p[1]-c.center[1],k:c.k*(pattern==="equal"?1:pattern==="left_half"?(p[0]<c.center[0]?0.5:1):(i===0?0.25:1))})).filter(p=>p.i!==failed);
 const force=mass*acc*c.g0,Fx=axis==="X"?force:0,Fz=axis==="Z"?force:0,Fn=axis==="Y"?force:0;
 const Q=[Fn,-e*Fx,e*Fz],K=Array.from({length:3},()=>[0,0,0]);
 for(const p of pts){const v=[1,p.x,p.z];for(let i=0;i<3;i++)for(let j=0;j<3;j++)K[i][j]+=p.k*v[i]*v[j];}
 const U=gauss(K,Q);if(!U)throw Error("singular support set");
 const ksum=pts.reduce((s,p)=>s+p.k,0);
 const rows=pts.map(p=>{const N=p.k*(U[0]+U[1]*p.x+U[2]*p.z),T=Math.hypot(Fx,Fz)*p.k/ksum;return {i:p.i,N,T,R:Math.hypot(N,T)};});
 const eq=[rows.reduce((s,r)=>s+r.N,0),rows.reduce((s,r,j)=>s+r.N*pts[j].x,0),rows.reduce((s,r,j)=>s+r.N*pts[j].z,0)];
 const resid=Math.max(...eq.map((v,i)=>Math.abs(v-Q[i])));
 if(resid>1e-6)throw Error(`equilibrium residual ${resid}`);
 const r=c.flange_r;return {variant,axis,mass_kg:mass,accel_g:acc,e_mm:e,pattern,failed:failed===0?"none":failed,
  active_supports:pts.length,max_resultant_N:r4(Math.max(...rows.map(x=>x.R))),
  min_signed_normal_N:r4(Math.min(...rows.map(x=>x.N))),
  max_signed_normal_N:r4(Math.max(...rows.map(x=>x.N))),
  min_uniform_preload_for_no_liftoff_N:r4(Math.max(0,...rows.map(x=>-x.N))),
  ring_disp_bound_mm:r4(Math.abs(U[0])+r*Math.hypot(U[1],U[2])),
  residual_N_or_Nmm:resid,
 };
}
function studyFailures(c){
 const rows=[],groups=[];
 for(const variant of ["A","B"])for(const axis of c.dirs)for(const accel of c.accel)for(const ecc of c.ecc)for(const mass of c.masses)for(const pattern of c.pattern){
   const base=support(c,variant,mass,accel,ecc,pattern,axis,0),cases=[base,...[1,2,3,4].map(j=>support(c,variant,mass,accel,ecc,pattern,axis,j))];
   rows.push(...cases);const worst=cases.slice(1).sort((a,b)=>b.max_resultant_N-a.max_resultant_N)[0];
   groups.push({variant,axis,accel_g:accel,e_mm:ecc,mass_kg:mass,pattern,baseline_max_N:base.max_resultant_N,worst_failure_N:worst.max_resultant_N,
     worst_failed:worst.failed,amplification:r4(worst.max_resultant_N/base.max_resultant_N),
     baseline_preload_N:base.min_uniform_preload_for_no_liftoff_N,
     worst_preload_N:Math.max(...cases.slice(1).map(x=>x.min_uniform_preload_for_no_liftoff_N)),
     baseline_disp_mm:base.ring_disp_bound_mm,worst_disp_mm:Math.max(...cases.slice(1).map(x=>x.ring_disp_bound_mm))});
 }
 if(rows.length!==1620||groups.length!==324)throw Error("failure counts wrong "+rows.length);
 return {cases:rows.length,groups:groups.length,rows,paired:groups,
  reference:groups.filter(x=>x.mass_kg===13.61&&x.accel_g===5&&x.e_mm===120&&x.pattern==="equal"),
  max_amplification:groups.slice().sort((a,b)=>b.amplification-a.amplification)[0],
  notes:["Uniform pre-load is only a mathematical contact-sign threshold: does not predict real bolt preload or avoid material failure.","Loss of one of four points is modeled by k=0; remaining three non-collinear points in both topologies; no progressive rupture/contact.","Assumed point stiffness 1000N/mm; the model omits flexible load-links, joint bending, fatigue, fastener/MDF capacity.","In-plane shear proportional to stiffness and independent of friction, so resultant R is an assumed reaction metric.","g=1/5/10 and e=90/120/180 mm are artificial stress loads, NOT defined transport standard."]};
}
function csv(data,keys){const esc=v=>String(v??"").replace(/"/g,'""');return keys.join(",")+"\n"+data.map(x=>keys.map(k=>'"'+esc(x[k])+'"').join(",")).join("\n")+"\n";}
function main(){
const R=studyRoutes(cfg),F=studyFailures(cfg),d=path.join(__dirname,"..","wyniki");
fs.mkdirSync(d,{recursive:true});
const rkeys=["variant","width_mm","clearance_mm","bolt","nearest_straight_violates_disk","nearest_anchor","selected_anchor","selected_path_kind","selected_path_length_mm","direct_euclid_mm","excess_length_mm","selected_arc_length_mm","reason"];
const fkeys=["variant","axis","mass_kg","accel_g","e_mm","pattern","failed","active_supports","max_resultant_N","min_signed_normal_N","max_signed_normal_N","min_uniform_preload_for_no_liftoff_N","ring_disp_bound_mm","residual_N_or_Nmm"];
fs.writeFileSync(path.join(d,"p43a_trasy_144.csv"),csv(R.selected,rkeys));
fs.writeFileSync(path.join(d,"p43b_awarie_1620.csv"),csv(F.rows,fkeys));
fs.writeFileSync(path.join(d,"p43_podsumowanie_20261101.json"),JSON.stringify({study:"P43",date:cfg.date,source_commit:cfg.parent_commit,inputs:cfg,route:{combinations:R.candidates,selected:R.selected_count,groups:R.groups,notes:R.notes},failure:{cases:F.cases,paired_scenarios:F.groups,reference:F.reference,max_amplification:F.max_amplification,notes:F.notes}},null,2)+"\n");
console.log(JSON.stringify({route_groups:R.groups,failure_reference:F.reference,max_failure:F.max_amplification},null,2));
}
if(require.main===module)main();
module.exports={cfg,route,studyRoutes,support,studyFailures};
