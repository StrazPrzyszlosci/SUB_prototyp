#!/usr/bin/env node
"use strict";
// P34B research-grade simplified 3D gas FV geometry. NO acoustic damping or panel coupling.
// npm dependencies: none. Node 18+.
const fs=require("node:fs"),path=require("node:path");
// The legacy cfg.source_xz_mm=[231,250] is retained for historical output reproduction.
// P38B transforms the external P31C center [231,250] to cavity-local [209,228].
const cfg={
  "date": "2026-10-31",
  "inside_mm": [
    976,
    359,
    456
  ],
  "brace1_x_mm": 426,
  "brace2_x_mm": 701,
  "rear_mat_mm": 50,
  "material_density_mat_kgm3": 20,
  "nominal_basket_displacement_l": 5,
  "module_sets": [
    {
      "id": "100",
      "large": 16,
      "small": 4,
      "nominal_l": 100.12
    },
    {
      "id": "120",
      "large": 12,
      "small": 0,
      "nominal_l": 119.92
    },
    {
      "id": "150",
      "large": 1,
      "small": 0,
      "nominal_l": 150.16
    }
  ],
  "frequency_Hz": [
    20,
    40,
    60,
    80
  ],
  "coarse_h_mm": [
    80,
    55
  ],
  "fine_h_mm": 36,
  "air_density_kgm3": 1.2,
  "air_sound_speed_ms": 343,
  "source_xz_mm": [
    231,
    250
  ],
  "source_radius_mm": 177.9,
  "speed_sensitivity_ms": [
    330,
    355
  ],
  "max_iterations": 2000,
  "relative_tolerance": 1e-9
};
function box(lo,hi){return [lo,hi]}
function geometry(c){
 const [W,D,H]=c.inside_mm, t=22,x1=426,x2=701;
 const bars=[];
 for(const x of [x1,x2]) {
  bars.push(box([x,0,0],[x+t,D,t]),box([x,0,H-t],[x+t,D,H]));
  bars.push(box([x,0,t],[x+t,10,H-t]),box([x,D-t,t],[x+t,D,H-t]));
 }
 bars.push(box([198,220,0],[220,D,t]),box([198,220,H-t],[220,D,H]),box([198,D-t,t],[220,D,H-t]));
 const xs=[(426+22+701)/2,(701+22+W)/2],small=[];
 for(const [x,z] of [[99,90],[99,366],[323,90],[323,366]])small.push(box([x-90,203,z-50],[x+90,303,z+50]));
 const large=[];
 for(const x of xs.slice().reverse())for(const cy of [243,83])for(const z of [62,392,172,282]){
  const depth=cy===243?120:150;
  large.push(box([x-105,cy-depth/2,z-50],[x+105,cy+depth/2,z+50]));
 }
 if(bars.length!==11||large.length!==16||small.length!==4)throw Error("geometry wrong");
 return {bars,large,small};
}
function insideBox(x,y,z,b){return x>=b[0][0]&&x<=b[1][0]&&y>=b[0][1]&&y<=b[1][1]&&z>=b[0][2]&&z<=b[1][2];}
function geometryAir(x,y,z,blocks,c,hasBasket=true){
 for(const b of blocks)if(insideBox(x,y,z,b))return false;
 // Placeholder 5 L displacement, not physical driver contour.
 if(hasBasket){
  const dx=x-c.source_xz_mm[0],dz=z-c.source_xz_mm[1];
  if(y>=0&&y<=94 && dx*dx+dz*dz<=130*130)return false;
 }
 return true;
}
function buildGrid(c,geom,state,h,speed=343,source="offset"){
 const [W,D,H]=c.inside_mm,nx=Math.ceil(W/h),ny=Math.ceil(D/h),nz=Math.ceil(H/h);
 const dx=W/nx,dy=D/ny,dz=H/nz,volumeCell=(dx/1000)*(dy/1000)*(dz/1000);
 const modules=state==="empty"?[]:geom.small.slice(0,c.module_sets.find(x=>x.id===state).small).concat(geom.large.slice(0,c.module_sets.find(x=>x.id===state).large));
 const solid=[...geom.bars,...modules],idx=(i,j,k)=>((i*ny+j)*nz+k),N=nx*ny*nz;
 const fluid=new Float64Array(N),fluidVolume=new Float64Array(N),srcWeight=new Float64Array(N);
 let sumFluid=0,srcArea=0;
 for(let i=0;i<nx;i++)for(let j=0;j<ny;j++)for(let k=0;k<nz;k++){
  const id=idx(i,j,k),nsub=3;let count=0;
  for(let a=0;a<nsub;a++)for(let b=0;b<nsub;b++)for(let d=0;d<nsub;d++){
   const X=(i+(a+.5)/nsub)*dx,Y=(j+(b+.5)/nsub)*dy,Z=(k+(d+.5)/nsub)*dz;
   if(geometryAir(X,Y,Z,solid,c,c.nominal_basket_displacement_l>0))count++;
  }
  fluid[id]=count/27;fluidVolume[id]=fluid[id]*volumeCell;sumFluid+=fluidVolume[id];
  if(j===0){
   let count2=0;
   const X0=source==="offset"?c.source_xz_mm[0]:W/2,Z0=source==="offset"?c.source_xz_mm[1]:H/2;
   for(let a=0;a<5;a++)for(let b=0;b<5;b++){
    const x=(i+(a+.5)/5)*dx,z=(k+(b+.5)/5)*dz;
    if((x-X0)**2+(z-Z0)**2<c.source_radius_mm**2)count2++;
   }
   const w=count2/25*dx*dz/1e6;
   // Speaker diaphragm is inlet boundary, but basket occupies interior behind it.
   srcWeight[id]=w;srcArea+=w;
  }
 }
 if(sumFluid<=0||srcArea<=0)throw Error("Empty fluid/source");
 const edges=[],m=[],active=[];
 for(let id=0;id<N;id++){
  if(fluid[id]>=1/27){active.push(id);m.push(fluidVolume[id]);}
 }
 const remap=new Int32Array(N).fill(-1);
 active.forEach((id,pos)=>remap[id]=pos);
 let actualSource=0;
 const q=new Float64Array(active.length);
 for(let a=0;a<active.length;a++){q[a]=srcWeight[active[a]];actualSource+=q[a];}
 if(actualSource<=0)throw Error("no source on active nodes");
 for(let i=0;i<nx;i++)for(let j=0;j<ny;j++)for(let k=0;k<nz;k++){
  const id=idx(i,j,k),a=remap[id];if(a<0)continue;
  for(const [ii,jj,kk,side,area,spacing] of [
   [i+1,j,k,0,dy*dz/1e6,dx/1000],
   [i,j+1,k,1,dx*dz/1e6,dy/1000],
   [i,j,k+1,2,dx*dy/1e6,dz/1000]]){
   if(ii>=nx||jj>=ny||kk>=nz)continue;
   const next=idx(ii,jj,kk),b=remap[next];if(b<0)continue;
   // Porosity near blocked cells: face transmissivity approximate, not exact cut-cell FV.
   const airFace=Math.min(fluid[id],fluid[next]),conductance=area/spacing*airFace;
   if(conductance>0)edges.push([a,b,conductance]);
  }
 }
 const mass=Float64Array.from(m),sqrtm=Float64Array.from(m,Math.sqrt);
 const L=active.length;const vtotal=sumFluid;const e=sqrtm.map(z=>z/Math.sqrt(vtotal));
 const k2=(2*Math.PI*(1)/speed)**2;
 const sel={state,step_h_mm:h,speed_ms:speed,source,volume_m3:sumFluid,volume_l:sumFluid*1000,
  expected_nominal_volume_l:state==="empty"?null:c.module_sets.find(x=>x.id===state).nominal_l,
  model_air_cells:L,grid_cells:N,edges:edges.length,nx,ny,nz,dx,dy,dz,
  mat_treated_as_rigid:false,mat_damping_enabled:false,basket_placeholder:"cylinder radius130mm depth94mm (~4.99 L), hypothetical",
  src_area_m2:srcArea,source_total:actualSource};
 return {sel,edges,mass,sqrtm,e,q,sourceTotal:actualSource,V:vtotal};
}
function simulate(c,geom,state,h,f,speed=343,source="offset"){
 const g=buildGrid(c,geom,state,h,speed,source),n=g.mass.length,k2=(2*Math.PI*f/speed)**2;
 const rhs=new Float64Array(n),tmp=new Float64Array(n);
 let sr=0;
 for(let i=0;i<n;i++){rhs[i]=(g.q[i]-g.mass[i]*g.sourceTotal/g.V)/g.sqrtm[i];sr+=rhs[i]*g.e[i];}
 for(let i=0;i<n;i++)rhs[i]-=sr*g.e[i];
 function project(x){let s=0;for(let i=0;i<n;i++)s+=x[i]*g.e[i];for(let i=0;i<n;i++)x[i]-=s*g.e[i];}
 function A(x,out){
  for(let i=0;i<n;i++)out[i]=-k2*x[i];
  for(const [a,b,conductance] of g.edges){
   const va=x[a]/g.sqrtm[a],vb=x[b]/g.sqrtm[b],d=conductance*(va-vb);
   out[a]+=d/g.sqrtm[a];out[b]-=d/g.sqrtm[b];
  }
  project(out);
 }
 let x=new Float64Array(n),r=Float64Array.from(rhs),p=Float64Array.from(rhs);
 let rr=0;for(let i=0;i<n;i++)rr+=r[i]*r[i];const rr0=rr;
 let it=0,Ap=new Float64Array(n);
 for(;it<c.max_iterations&&rr>rr0*c.relative_tolerance*c.relative_tolerance;it++){
  A(p,Ap);let den=0;for(let i=0;i<n;i++)den+=p[i]*Ap[i];
  if(den<=0)throw Error("Non-SPD (above first mode?) "+JSON.stringify({state,h,f,den,it}));
  const alpha=rr/den;
  for(let i=0;i<n;i++){x[i]+=alpha*p[i];r[i]-=alpha*Ap[i];}
  project(r);
  let rr2=0;for(let i=0;i<n;i++)rr2+=r[i]*r[i];
  const beta=rr2/rr;
  for(let i=0;i<n;i++)p[i]=r[i]+beta*p[i];
  project(p);rr=rr2;
 }
 if(rr>rr0*1e-12)throw Error("CG unconverged "+it+" "+Math.sqrt(rr/rr0));
 const meanPressure=-g.sourceTotal/(k2*g.V);
 let min=Infinity,max=-Infinity,minDb=Infinity,maxDb=-Infinity,variance=0,maxAbs=0;
 let cavityAverage=0,sourceP=0;
 for(let i=0;i<n;i++){
  const pressure=meanPressure+x[i]/g.sqrtm[i],rel=pressure/meanPressure;
  // below first nonzero resonance, sign should remain same at low freq.
  const db=20*Math.log10(Math.max(1e-12,Math.abs(rel)));
  minDb=Math.min(db,minDb);maxDb=Math.max(db,maxDb);min=Math.min(rel,min);max=Math.max(rel,max);
  variance+=g.mass[i]*(rel-1)**2/g.V;
  cavityAverage+=g.mass[i]*pressure/g.V;
  sourceP+=g.q[i]*pressure/g.sourceTotal;
  maxAbs=Math.max(maxAbs,Math.abs(rel-1));
 }
 if(Math.abs((cavityAverage-meanPressure)/meanPressure)>1e-7)throw Error("mean consistency");
 const sol={...g.sel,freq_Hz:f,solver:"projected conjugate gradient for zero-mean Helmholtz FV, hard walls",
  iterations:it,relative_residual:Math.sqrt(rr/rr0),relative_min:min,relative_max:max,field_min_db:minDb,field_max_db:maxDb,peak_nonuniformity_pct:100*maxAbs,
  rms_nonuniformity_pct:100*Math.sqrt(variance),source_pressure_relative_to_mean:sourceP/meanPressure};
 return sol;
}
function main(){
 const geom=geometry(cfg),jobs=[];
 for(const state of ["empty","100","120","150"])for(const h of [80,55])
  for(const f of cfg.frequency_Hz)jobs.push({state,h,f});
 for(const state of ["100","120","150"])for(const f of [40,80])jobs.push({state,h:36,f});
 for(const f of [20,40,60,80])jobs.push({state:"120",h:55,f,source:"center"});
 for(const speed of cfg.speed_sensitivity_ms)for(const f of [20,80])jobs.push({state:"120",h:55,f,speed});
 const rows=jobs.map(z=>simulate(cfg,geom,z.state,z.h,z.f,z.speed??343,z.source??"offset"));
 if(rows.length!==46)throw Error("wrong number of cases");
 const out={study:"P34B",date:"2026-10-31",cases:rows.length,cfg,rows,
  warnings:["Pressure field relative to its own spatial mean; not actual SPL or frequency response of diaphragm.","Neumann rigid boundaries and real-valued no-loss Helmholtz; no porous absorption or compliant wall coupling.","Internal AABB from P30E; subcell fluid-volume approximation and face conductance min-air heuristic, not exact cut-cell FV.","Driver 5-L basket represented by cylinder only, no 3D basket CAD.","Each nominal state and FV fluid volume use different geometric assumptions; treat mismatch as model diagnostic.","The zero mode is solved exactly, spatial deviations by projected conjugate gradient; intended below first nonuniform resonance.","Uncertainty of mat absorption, pressure source pattern and physical damping is unbounded."]};
 const dest=path.join(__dirname,"..","wyniki","p34b_przestrzenne_pole_p30e_20261031.json");
 fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,JSON.stringify(out,null,2)+"\n");
 console.log(JSON.stringify({cases:rows.length,at80:rows.filter(x=>x.step_h_mm===55&&x.freq_Hz===80&&x.source==="offset"&&x.speed_ms===343)},null,2));
}
if(require.main===module)main();
module.exports={cfg,geometry,simulate,main};
