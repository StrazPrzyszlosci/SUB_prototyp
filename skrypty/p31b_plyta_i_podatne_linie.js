#!/usr/bin/env node
"use strict";
// P31B ERRATUM 2026-10-31: inner panel spans were previously calculated
// by subtracting .044/.066 mm; corrected to 44/66 mm.
// P31B research: Kirchhoff plate Ritz sine basis + elastic line-to-ground braces.
// NOT an eigenanalysis of the entire cabinet. Node 18+, no deps.
const fs=require("node:fs"),path=require("node:path");
const params={
  "study": "P31B",
  "date": "2026-10-31",
  "cabinets": [
    {
      "W": 1000,
      "D": 440,
      "H": 500
    },
    {
      "W": 1020,
      "D": 425,
      "H": 500
    },
    {
      "W": 1040,
      "D": 430,
      "H": 500
    }
  ],
  "panel_thickness_m": 0.022,
  "front_thickness_m": 0.044,
  "nu": 0.3,
  "E_Pa": [
    1500000000,
    2100000000,
    3000000000
  ],
  "rho_kg_m3": [
    650,
    730,
    800
  ],
  "line_support_N_per_m2": [
    0,
    100000,
    1000000,
    10000000,
    100000000
  ],
  "pressure_Pa": 1000,
  "modes_m": 7,
  "modes_n": 5,
  "coarse_modes_m": 5,
  "coarse_modes_n": 3,
  "sigma_tolerance": 1e-8
};
function solve(A,y){
 const n=y.length, B=A.map((row,i)=>[...row,y[i]]);
 for(let k=0;k<n;k++){
  let im=k;for(let i=k+1;i<n;i++)if(Math.abs(B[i][k])>Math.abs(B[im][k]))im=i;
  if(Math.abs(B[im][k])<1e-15)throw Error("singular");
  [B[k],B[im]]=[B[im],B[k]];
  const t=B[k][k];for(let j=k;j<=n;j++)B[k][j]/=t;
  for(let i=0;i<n;i++)if(i!==k){const q=B[i][k];for(let j=k;j<=n;j++)B[i][j]-=q*B[k][j];}
 }
 return B.map(x=>x[n]);
}
function minEigen(A){
 const a=A.map(x=>x.slice()),n=a.length; 
 for(let it=0;it<45*n*n;it++){
  let p=0,q=1,max=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){const t=Math.abs(a[i][j]);if(t>max){max=t;p=i;q=j;}}
  if(max<1e-9)break;
  const tau=(a[q][q]-a[p][p])/(2*a[p][q]),t=(tau>=0?1:-1)/(Math.abs(tau)+Math.sqrt(1+tau*tau)),c=1/Math.sqrt(1+t*t),s=t*c;
  const app=a[p][p],aqq=a[q][q],apq=a[p][q];
  a[p][p]=app-t*apq;a[q][q]=aqq+t*apq;a[p][q]=a[q][p]=0;
  for(let k=0;k<n;k++)if(k!==p&&k!==q){const akp=a[k][p],akq=a[k][q];a[k][p]=a[p][k]=c*akp-s*akq;a[k][q]=a[q][k]=s*akp+c*akq;}
 }
 return Math.min(...a.map((x,i)=>x[i]));
}
function runOne(p,W,D,E,rho,kSupport,mMax,nMax){
 const a=(W-44)/1000,b=(D-66)/1000,t=p.panel_thickness_m,rig=E*t**3/(12*(1-p.nu*p.nu));
 if(Math.abs(a-(W-44)/1000)>1e-12 || Math.abs(b-(D-66)/1000)>1e-12)throw Error('Unit conversion');
 const mass=rho*t*a*b/4, x1=.426,x2=(.426+a)/2;
 const F=[],Q=[];let lowest=Infinity;
 for(let n=1;n<=nMax;n++){
  let K=[],P=[];
  for(let m=1;m<=mMax;m++){
   const row=[];for(let j=1;j<=mMax;j++){
    const stiffness=(m===j?rig*Math.PI**4*((m/a)**2+(n/b)**2)**2*a*b/4:0);
    const sup=kSupport*b/2*(Math.sin(m*Math.PI*x1/a)*Math.sin(j*Math.PI*x1/a)+
     Math.sin(m*Math.PI*x2/a)*Math.sin(j*Math.PI*x2/a));
    row.push(stiffness+sup);
   }
   K.push(row);
   P.push(m%2===1&&n%2===1?p.pressure_Pa*(4*a*b/(Math.PI*Math.PI*m*n)):0);
  }
  const y=solve(K,P);
  for(let m=1;m<=mMax;m++){F.push({n,m,Q:y[m-1]});}
  if(n===1){
   const eig=minEigen(K.map(row=>row.map(v=>v/mass)));
   if(!(eig>0))throw Error("invalid eigenvalue");
   lowest=Math.sqrt(eig)/(2*Math.PI);
  }
 }
 let disp=0,vol=0,shapeMax=0;
 for(const {n,m,Q:v} of F){
  disp+=v*Math.sin(m*Math.PI/2)*Math.sin(n*Math.PI/2);
  vol+=v*(m%2&&n%2?4*a*b/(Math.PI*Math.PI*m*n):0);
 }
 // Independent static work identity: q^T K q = q^T P, to tolerance
 const fUnbraced=(Math.PI/2)*Math.sqrt(rig/(rho*t))*(1/a**2+1/b**2);
 return {W_mm:W,D_mm:D,inner_W_mm:W-44,inner_depth_mm:D-66,E_GPa:E/1e9,rho_kg_m3:rho,
  spring_k_N_per_m2:kSupport,model_f1_Hz:+lowest.toFixed(4),
  mid_displacement_um_per_1000Pa:+(disp*1e6).toFixed(4),
  integrated_vol_displacement_cm3_per_1000Pa:+(vol*1e6).toFixed(4),
  unbraced_analytical_f11_Hz:+fUnbraced.toFixed(4),
  ratio_frequency_to_unbraced:+(lowest/fUnbraced).toFixed(5),
  front_brace_location_inner_mm:[426,(426+(W-44))/2]};
}
function analyze(p){
 const cases=[];let checks=[];
 for(const box of p.cabinets)for(const E of p.E_Pa)for(const rho of p.rho_kg_m3)for(const k of p.line_support_N_per_m2)
   cases.push(runOne(p,box.W,box.D,E,rho,k,p.modes_m,p.modes_n));
 if(cases.length!==135)throw Error("case count");
 for(const box of p.cabinets){
  const x=cases.find(x=>x.W_mm===box.W&&x.E_GPa===2.1&&x.rho_kg_m3===730&&x.spring_k_N_per_m2===0);
  if(Math.abs(x.model_f1_Hz-x.unbraced_analytical_f11_Hz)>.001)throw Error("analytical eigencheck "+box.W);
  const test=runOne(p,box.W,box.D,2.1e9,730,1e6,p.coarse_modes_m,p.coarse_modes_n);
  const finer=runOne(p,box.W,box.D,2.1e9,730,1e6,p.modes_m,p.modes_n);
  checks.push({box_W_mm:box.W,box_D_mm:box.D,static_center_um_coarse:test.mid_displacement_um_per_1000Pa,
   static_center_um_finer:finer.mid_displacement_um_per_1000Pa,
   change_percent:+(100*(test.mid_displacement_um_per_1000Pa-finer.mid_displacement_um_per_1000Pa)/finer.mid_displacement_um_per_1000Pa).toFixed(3),
   f1_Hz_coarse:test.model_f1_Hz,f1_Hz_finer:finer.model_f1_Hz});
 }
 const selected=cases.filter(x=>x.W_mm===1020&&x.E_GPa===2.1&&x.rho_kg_m3===730);
 if(Math.abs(selected[0].model_f1_Hz-156.2429)>.002 || Math.abs(selected[2].model_f1_Hz-171.132)>.002)throw Error('Unit conversion regression: expected 976x359mm and f1=156.2429/171.132Hz');
 const paramSweep=cases.filter(x=>x.W_mm===1020);
 const low=Math.min(...paramSweep.map(x=>x.model_f1_Hz)),high=Math.max(...paramSweep.map(x=>x.model_f1_Hz));
 return {study:"P31B",status:"Rayleigh-Ritz Kirchhoff SINGLE panel with elastic LINE-to-GROUND braces. Not FEM of cabinet.",parameters:p,cases:cases.length,
  selected_support_sensitivity:selected,
  selected_range_f1_scenario_Hz:[low,high],
  modal_convergence_checks:checks,
  all_cases:cases,
  warnings:["A single simply-supported unperforated plate is NOT the full cabinet: front aperture, joint flexibility, bending-torsion of ring braces, adhesive and gasket remain unmodeled.",
   "Line springs to immovable ground overstate brace effectiveness: real ring frame moves; spring k is a hypothetical span of 0..1e8 N/m2, not material property.",
   "No physical panel vibration frequencies or radiation measurement, no complete FEM or acoustic-structural coupling.",
   "Pressure 1000Pa uniform synthetic; near-field nonuniform pressure, screw preload and real dynamic loads not included.",
   "Static response uses 7x5 basis; convergence against 5x3 checked at one support/E/rho and full convergence not certified.",
   "No CNC release, fastener qualification, fatigue/creep or real mounting load."]};
}
if(require.main===module){
 const data=analyze(params),p=path.join(__dirname,"..","wyniki","p31b_podatnosc_dwoch_linii_135_20261031.json");
 fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(data,null,2)+"\n");
 console.log(JSON.stringify({cases:data.cases,selected:data.selected_support_sensitivity,checks:data.modal_convergence_checks},null,2));
}
module.exports={params,runOne,analyze};
