#!/usr/bin/env node
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const b1206=function b1206(){
 const W=1.02,H=.5,nu=.30,rho=730,grav=9.81;
 const models=[
  {id:"Dayton_C02",driver_kg_assumed:13.6078,holes:[{x:.231,z:.25,r:.3558/2,pcd:.368,n:8,m:13.6078}]},
  {id:"STX_2C05",driver_kg_assumed:8,holes:[{x:.255,z:.25,r:.284/2,pcd:.316,n:8,m:4},{x:.765,z:.25,r:.284/2,pcd:.316,n:8,m:4}]}];
 const GPa=[1.5,2.1,3],thicks=[22,44],supports=[0,1e6,1e7],R=x=>+x.toFixed(7);
 const zero=n=>Array.from({length:n},()=>Array(n).fill(0)),dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
 const mult=(A,x)=>A.map(v=>dot(v,x));
 function linear(A,b){
  const n=b.length,c=A.map((x,i)=>[...x,b[i]]);
  for(let k=0;k<n;k++){
   let m=k;for(let i=k+1;i<n;i++)if(Math.abs(c[i][k])>Math.abs(c[m][k]))m=i;
   if(Math.abs(c[m][k])<1e-20)throw Error("singular");
   [c[k],c[m]]=[c[m],c[k]];let q=c[k][k];for(let j=k;j<=n;j++)c[k][j]/=q;
   for(let i=k+1;i<n;i++){let q=c[i][k];for(let j=k;j<=n;j++)c[i][j]-=q*c[k][j];}
  }
  let x=Array(n).fill(0);for(let i=n-1;i>=0;i--){let q=c[i][n];for(let j=i+1;j<n;j++)q-=c[i][j]*x[j];x[i]=q;}return x;
 }
 function integrate(model,N=5,M=4,nx=84,nz=42){
  const bas=[];for(let n=1;n<=N;n++)for(let m=1;m<=M;m++)bas.push({a:Math.PI*n/W,b:Math.PI*m/H});
  const n=bas.length,k=zero(n),mass=zero(n),support=zero(n),driverMass=zero(n),p=Array(n).fill(0),gravVector=Array(n).fill(0);
  const v=(x,z)=>bas.map(b=>{const sx=Math.sin(b.a*x),cx=Math.cos(b.a*x),sz=Math.sin(b.b*z),cz=Math.cos(b.b*z);return [sx*sz,-b.a*b.a*sx*sz,-b.b*b.b*sx*sz,b.a*b.b*cx*cz]});
  const cell=W*H/nx/nz;let area=0;
  for(let ix=0;ix<nx;ix++)for(let iz=0;iz<nz;iz++){
   let x=(ix+.5)*W/nx,z=(iz+.5)*H/nz;
   if(model.holes.some(h=>(h.x-x)**2+(h.z-z)**2<h.r**2))continue;
   const a=v(x,z);area+=cell;
   for(let i=0;i<n;i++){
    p[i]+=a[i][0]*cell;
    for(let j=0;j<=i;j++){
     mass[i][j]+=a[i][0]*a[j][0]*cell;
     k[i][j]+=(a[i][1]*a[j][1]+a[i][2]*a[j][2]+nu*(a[i][1]*a[j][2]+a[i][2]*a[j][1])+2*(1-nu)*a[i][3]*a[j][3])*cell;
    }
   }
  }
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){k[i][j]=k[j][i];mass[i][j]=mass[j][i];}
  for(let zstep=1;zstep<=21;zstep++){
   const a=v(W/2,zstep*H/22);for(let i=0;i<n;i++)for(let j=0;j<n;j++)support[i][j]+=a[i][0]*a[j][0]/21;
  }
  for(const hole of model.holes)for(let q=0;q<hole.n;q++){
   const angle=2*Math.PI*q/hole.n,a=v(hole.x+hole.pcd/2*Math.cos(angle),hole.z+hole.pcd/2*Math.sin(angle));
   for(let i=0;i<n;i++){
    gravVector[i]+=hole.m*grav/hole.n*a[i][0];
    for(let j=0;j<n;j++)driverMass[i][j]+=hole.m/hole.n*a[i][0]*a[j][0];
   }
  }
  return{bas,area,k,mass,support,driverMass,p,gravVector,v};
 }
 function solveModel(model,g,E,t,ks){
  const D=E*t**3/(12*(1-nu*nu)),n=g.bas.length;
  const K=g.k.map((row,i)=>row.map((v,j)=>D*v+ks*g.support[i][j]));
  const M=g.mass.map((row,i)=>row.map((v,j)=>rho*t*v+g.driverMass[i][j]));
  const loads=[["pressure100",g.p.map(v=>v*100)],["gravity",g.gravVector],["common100N",g.gravVector.map(v=>v*100/(model.driver_kg_assumed*grav))]];
  const cases={};
  for(let [name,force] of loads){
   let x=linear(K,force),max=0;
   for(let xi=0;xi<=24;xi++)for(let zi=0;zi<=12;zi++){
    const px=xi*W/24,pz=zi*H/12;
    if(model.holes.some(h=>(px-h.x)**2+(pz-h.z)**2<h.r*h.r))continue;
    max=Math.max(max,Math.abs(dot(g.v(px,pz).map(q=>q[0]),x)));
   }
   cases[name]={peak_mm:R(max*1000),work_Nm:R(dot(x,force))};
  }
  let x=Array.from({length:n},(_,i)=>1+.3*Math.sin(i*1.3));
  for(let j=0;j<35;j++){let y=linear(K,mult(M,x)),m=Math.sqrt(dot(y,mult(M,y)));x=y.map(v=>v/m);}
  const Hz=Math.sqrt(dot(x,mult(K,x))/dot(x,mult(M,x)))/(2*Math.PI);
  return{model:model.id,E_GPa:E/1e9,t_mm:t*1000,kbrace_N_m:ks,panel_area_m2:R(g.area),
   panel_mass_kg:R(g.area*t*rho),driver_mass_proxy_kg:model.driver_kg_assumed,
   modal_frequency_Ritz_hz:R(Hz),...cases};
 }
 const rows=[],convergence=[];
 for(const model of models){
  const g=integrate(model);
  for(const E of GPa)for(const t of thicks)for(const ks of supports)rows.push(solveModel(model,g,E*1e9,t*.001,ks));
  for(const [N,M,nx,nz] of [[3,3,64,32],[4,3,84,42],[5,4,84,42],[5,4,126,63]]){
   const m=solveModel(model,integrate(model,N,M,nx,nz),2.1e9,.044,1e6);
   convergence.push({model:model.id,basis:`${N}x${M}`,integration_grid:`${nx}x${nz}`,pressure100_peak_mm:m.pressure100.peak_mm,gravity_peak_mm:m.gravity.peak_mm,mode_Ritz_hz:m.modal_frequency_Ritz_hz});
  }
 }
 const chosen=rows.filter(x=>x.E_GPa===2.1&&x.t_mm===44&&x.kbrace_N_m===1e6);
 const room={length_m:4.6,width_m:3.7,height_m:2.5,volume_m3:42.55,one_sweet_spot:true,listening_distance_m:[2.5,3],axial_modes_hz:{length:R(343/9.2),width:R(343/7.4),height:R(343/5)},two_cabinets_width_m:2.04,front_wall_remaining_width_m:1.66,
  reference_2_cabinets:["Dayton_C02","Dayton_C02"],alternate_2_cabinets:["STX_2C05","STX_2C05"],driver_count_per_two_cabinets:{Dayton:2,STX:4},
  nominal_Vd_cm3_per_cabinet:{Dayton:R(829.6*14/10),STX_pair:R(2*491*7.5/10)},all_in_room_Vd_cm3:{Dayton_2subs:R(2*829.6*14/10),STX_2subs:R(4*491*7.5/10)},
  limits:"No actual placement, monitor cabinet dimensions, room damping, response or distorted clean SPL are measured."};
 if(rows.length!==36||convergence.length!==8||chosen.length!==2)throw Error("counts");
 return{schema:"B12-06_Ritz_front_screen_and_original_brief_gate",date:"2026-11-02",
   method:{front_width_m:W,front_height_m:H,MDF_density_assumed_kg_m3:rho,Poisson_assumed:nu,Young_moduli_test_GPa:GPa,thicknesses_mm:thicks,brace_springs_total_N_per_m:supports,solver:"Kirchhoff-Love Ritz 5x4 smooth sine trial functions, pressure and bolt rim loads, quadrature excluding circular hole interiors; simply supported outer edges; central hypothetical spring line; NOT validated conformal FE solution nor whole-box modal model",forcing:"100 Pa front panel; front-horizontal gravity normal forces per speaker; uniform common 100 N force on circular bolt locations",reference_mass:"Dayton listed manufacturer weight 30 lb (~13.61kg) is an uncertain item/package proxy; STX per driver 4kg net. Do not infer actual C02 net mass without weighing.",STX_bolt_count_assumption:8},
   n:rows.length,results:rows,convergence,representative:chosen,room,
   brief_gate:{reference:"brief_system_audio_DIY_v0.6.md + WYMAGANIA.md + dane/konfiguracje/pokoj_odsluchowy.json",
    hard_requirements:["sealed adjustable net volume initial prototype", "single driver per cabinet remains W24 design baseline; dual STX an alternative, not automatic selection", "two independent subwoofers physically placeable near active 3-way monitors in 3.7m front room","two sub DSP independent outputs 7 and 8 (six monitor channels 1..6)","full depth with front grille ≤500mm","clean useful bass 20-40Hz, headroom, low THD, IMD, noise and compression","one sweet spot 2.5-3m, no reliance on unrealistic front/rear source placement","benchmark ADAM Sub12 and Sub15; acceptance numbers not yet approved", "no enforced budget ceiling but compare total-system cost","repeatable calibration in other 17-20m² rooms"],
    open:["measured THD/IMD and compression at equal listening SPL","actual dual-sub placement and monitor/furniture floor plan","factory driver basket and mechanical fastener details","MDF elastic moduli and glue-joint rotational stiffness","full 3D FE modal/stress and panel radiation after buckling-free verified mesh","real net displacement, depth including grille/terminal and calibration 100/120/150l","headroom/delay crossover for two cabinets at the listening position"],
    decision:"Neither design can be certified against original brief. Dayton remains preliminary performance leader; two-STX remains cost counterfactual, not the primary objective. No CNC, no orders."},
   warnings:["Ritz smooth basis does not reproduce free circular hole edges or fastener-local stress and likely underestimates local flexibility","Global front-only frequencies are not whole-box resonances or acoustic radiated response","MDF E, support k and density are artificial parameter scenarios; no validated stiffness or fatigue","Pressure and force are explicit comparison loads, not real measured subwoofer forces","Front-horizontal weight loading assumes source normal to panel; vertical orientation needs basket center-of-gravity moment and screws analysis","Room axial frequencies are theoretical geometry, not measured modes or decay","Cannot rank sound quality or clean SPL from structural screening"]};
};
const result=b1206(),root=path.resolve(__dirname,"..");
const saved=JSON.parse(fs.readFileSync(path.join(root,"wyniki/b12_06_front_ritz_i_brief_20261102.json"),"utf8"));
assert.deepStrictEqual(result,saved);
if(result.n!==36||result.convergence.length!==8)throw Error("Count mismatch");
console.log("B12-06 OK",result.n,"mechanical trials",result.convergence.length,"convergence checks and room/brief gate");
