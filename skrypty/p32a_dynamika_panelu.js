#!/usr/bin/env node
"use strict";
// P32A: corrected panel force-response model; not full cabinet FEM.
const fs=require('node:fs'),path=require('node:path');
const cfg={"date":"2026-10-31","boxes":[[1000,440],[1020,425]],"E_GPa":[1.5,2.1,3],"rho":730,"h":0.022,"nu":0.3,"peakPressurePa":1000,"k":[0,1000000,10000000],"zeta":[0.02,0.05],"f":[20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180],"m":7,"n":5};
function solve(A,b){let n=b.length,v=A.map((x,i)=>[...x,b[i]]);for(let k=0;k<n;k++){let p=k;for(let j=k+1;j<n;j++)if(Math.abs(v[j][k])>Math.abs(v[p][k]))p=j;if(Math.abs(v[p][k])<1e-17)throw Error("singular");[v[k],v[p]]=[v[p],v[k]];let q=v[k][k];for(let j=k;j<=n;j++)v[k][j]/=q;for(let i=0;i<n;i++)if(i!==k){q=v[i][k];for(let j=k;j<=n;j++)v[i][j]-=q*v[k][j]}}return v.map(x=>x[n])}
function eig(K,mass){let a=K.map(r=>r.map(x=>x/mass)),n=a.length;for(let h=0;h<50*n*n;h++){let p=0,q=1,max=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)if(Math.abs(a[i][j])>max){max=Math.abs(a[i][j]);p=i;q=j}if(max<1e-9)break;let t=(a[q][q]-a[p][p])/(2*a[p][q]),z=(t>=0?1:-1)/(Math.abs(t)+Math.sqrt(1+t*t)),c=1/Math.sqrt(1+z*z),s=z*c,P=a[p][p],Q=a[q][q],R=a[p][q];a[p][p]=P-z*R;a[q][q]=Q+z*R;a[p][q]=a[q][p]=0;for(let j=0;j<n;j++)if(j!==p&&j!==q){let u=a[j][p],v=a[j][q];a[j][p]=a[p][j]=c*u-s*v;a[j][q]=a[q][j]=s*u+c*v;}}return Math.sqrt(Math.min(...a.map((r,i)=>r[i])))/(2*Math.PI);}
function simulate(c,box,E,k,zeta,frequency,mMax=c.m,nMax=c.n){
 const a=(box[0]-44)/1000,b=(box[1]-66)/1000,rig=E*1e9*c.h**3/(12*(1-c.nu**2)),mass=c.rho*c.h*a*b/4,lines=[.426,(a+.426)/2],w=2*Math.PI*frequency;
 if(a<.9||b<.3||b>.40)throw Error("dimension conversion");
 const block=n=>Array.from({length:mMax},(_,i)=>Array.from({length:mMax},(_,j)=>(i===j?rig*Math.PI**4*(((i+1)/a)**2+(n/b)**2)**2*a*b/4:0)+k*b/2*lines.reduce((v,x)=>v+Math.sin((i+1)*Math.PI*x/a)*Math.sin((j+1)*Math.PI*x/a),0)));
 const f1=eig(block(1),mass),w1=2*Math.PI*f1,w3=3*w1,alpha=2*zeta*w1*w3/(w1+w3),beta=2*zeta/(w1+w3);
 let real=0,imag=0,volR=0,volI=0,inp=0,loss=0,resid=0;
 for(let n=1;n<=nMax;n++){
  const K=block(n),F=Array.from({length:mMax},(_,i)=>i%2===0&&n%2===1?4*a*b*c.peakPressurePa/(Math.PI**2*(i+1)*n):0),N=2*mMax;
  const M=Array.from({length:N},()=>Array(N).fill(0)),rhs=[...F,...Array(mMax).fill(0)];
  for(let i=0;i<mMax;i++)for(let j=0;j<mMax;j++){
   let re=K[i][j]-(i===j?w*w*mass:0),im=w*((i===j?alpha*mass:0)+beta*K[i][j]);
   M[i][j]=re;M[i][j+mMax]=-im;M[i+mMax][j]=im;M[i+mMax][j+mMax]=re;
  }
  const x=solve(M,rhs);
  for(let i=0;i<N;i++){let v=0;for(let j=0;j<N;j++)v+=M[i][j]*x[j];resid=Math.max(resid,Math.abs(v-rhs[i])/Math.max(1,...F.map(Math.abs)))}
  for(let i=0;i<mMax;i++){
   const m=i+1,s=Math.sin(m*Math.PI/2)*Math.sin(n*Math.PI/2),integr=m%2&&n%2?4*a*b/(Math.PI**2*m*n):0;
   real+=s*x[i];imag+=s*x[i+mMax];volR+=integr*x[i];volI+=integr*x[i+mMax];inp+=-.5*w*F[i]*x[i+mMax];
  }
  let diss=0;for(let i=0;i<mMax;i++)for(let j=0;j<mMax;j++){let C=(i===j?alpha*mass:0)+beta*K[i][j];diss+=C*(x[i]*x[j]+x[i+mMax]*x[j+mMax])}
  loss+=.5*w*w*diss;
 }
 if(resid>1e-7 || Math.abs(inp-loss)/Math.max(1e-10,inp,loss)>1e-7)throw Error("dynamic energy/residual invalid");
 return {f:frequency,f1:+f1.toFixed(4),um:+(1e6*Math.hypot(real,imag)).toFixed(5),vol_cm3:+(1e6*Math.hypot(volR,volI)).toFixed(5),power_in_W:+inp.toFixed(8),power_diss_W:+loss.toFixed(8)};
}
function run(c){
 const rows=[],summ=[];
 for(const box of c.boxes)for(const E of c.E_GPa)for(const k of c.k)for(const zeta of c.zeta){
  const data=c.f.map(f=>simulate(c,box,E,k,zeta,f));
  const low=data.filter(d=>d.f<=80),top=data.reduce((a,b)=>a.um>b.um?a:b);
  rows.push({box,E,k,zeta,data});summ.push({box,E,k,zeta,f1:data[0].f1,max20_80:Math.max(...low.map(x=>x.um)),max20_180:top.um,peak_at:top.f});
 }
 const selected=rows.filter(x=>x.box[0]===1020&&x.E===2.1&&x.zeta===.02);
 const convergence=[20,80,130,160].map(f=>{const a=simulate(c,[1020,425],2.1,1e6,.02,f,7,5),b=simulate(c,[1020,425],2.1,1e6,.02,f,9,7);return {f,base_um:a.um,finer_um:b.um,rel_percent:+(100*(b.um-a.um)/b.um).toFixed(4)}});
 if(rows.length!==36||rows.reduce((n,r)=>n+r.data.length,0)!==612||selected.length!==3)throw Error("grid");
 if(Math.abs(selected[0].data[0].f1-156.2429)>.002||convergence.some(x=>Math.abs(x.rel_percent)>5))throw Error("test convergence / erratum");
 return {study:"P32A",status:"SIMULATION ONLY — SINGLE PANEL, NO COMPLETE CABINET FEM",cfg:c,studied_models:36,frequency_points:612,selected,convergence,summary:summ,rows,warnings:["Corrected mm/m conversion, span 976×359 mm","Springs are anchored to immovable ground; real braces and joints can move","1000 Pa harmonic peak pressure and damping ratios 2%/5% are assumed","Values are not measured panel motion, radiation, or safe loads","Full CAD/CNC, coupled FEM and material validation still required"]};
}
if(require.main===module){const v=run(cfg),p=path.join(__dirname,'..','wyniki','p32a_dynamika_panelu_612_20261031.json');fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');console.log(JSON.stringify({models:v.studied_models,points:v.frequency_points,convergence:v.convergence},null,2))}
module.exports={cfg,simulate,run};
