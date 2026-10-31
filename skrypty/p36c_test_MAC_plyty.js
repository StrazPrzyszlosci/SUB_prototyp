#!/usr/bin/env node
"use strict";
// P36C MAC verification on an independently solvable SSSS finite-difference plate.
// THIS IS NOT GLOBAL CABINET MAC. 12 modes, three discretizations, 2^12 assignment.
const fs=require('node:fs'),path=require('node:path');
const cfg={
  "date": "2026-10-31",
  "panel_a_mm": 976,
  "panel_b_mm": 359,
  "h_mm": 22,
  "E_GPa": 2.1,
  "rho_kgm3": 730,
  "nu": 0.3,
  "modes_m": [
    1,
    2,
    3,
    4
  ],
  "modes_n": [
    1,
    2,
    3
  ],
  "mesh": [
    [
      8,
      4
    ],
    [
      16,
      8
    ],
    [
      32,
      12
    ]
  ],
  "common_probe": [
    17,
    13
  ],
  "accept_MAC": 0.9
};
function mode(c,nx,ny,m,n){
 const a=c.panel_a_mm/1000,b=c.panel_b_mm/1000,h=c.h_mm/1000,E=c.E_GPa*1e9;
 const dx=a/(nx+1),dy=b/(ny+1);
 const eigFD=4*Math.sin(m*Math.PI/(2*(nx+1)))**2/dx**2+4*Math.sin(n*Math.PI/(2*(ny+1)))**2/dy**2;
 const rig=E*h**3/(12*(1-c.nu*c.nu)),freq=Math.sqrt(rig/(c.rho_kgm3*h))*eigFD/(2*Math.PI);
 const cont=Math.sqrt(rig/(c.rho_kgm3*h))*((m*Math.PI/a)**2+(n*Math.PI/b)**2)/(2*Math.PI);
 function sinGrid(i,j){if(i<1||i>nx||j<1||j>ny)return 0;return Math.sin(m*Math.PI*i/(nx+1))*Math.sin(n*Math.PI*j/(ny+1));}
 const samples=[];
 for(let iu=1;iu<=c.common_probe[0];iu++)for(let iv=1;iv<=c.common_probe[1];iv++){
  const x=iu/(c.common_probe[0]+1)*a, y=iv/(c.common_probe[1]+1)*b;
  const tx=x/dx,ty=y/dy,i0=Math.floor(tx),j0=Math.floor(ty),u=tx-i0,v=ty-j0;
  const val=(1-u)*(1-v)*sinGrid(i0,j0)+u*(1-v)*sinGrid(i0+1,j0)+(1-u)*v*sinGrid(i0,j0+1)+u*v*sinGrid(i0+1,j0+1);
  samples.push(val);
 }
 return {m,n,nx,ny,freq_Hz:freq,continuum_Hz:cont,samples};
}
function mac(a,b){
 let dot=0,aa=0,bb=0;for(let i=0;i<a.length;i++){dot+=a[i]*b[i];aa+=a[i]*a[i];bb+=b[i]*b[i];}
 return dot*dot/(aa*bb);
}
function assign(score){
 // Dynamic assignment maximizes sum MAC over all permutation of 12 modes, 2^12 DP.
 const n=score.length,dp=new Float64Array(1<<n).fill(-Infinity),prev=new Int32Array(1<<n).fill(-1);dp[0]=0;
 for(let mask=0;mask<(1<<n);mask++){
  if(!Number.isFinite(dp[mask]))continue;let row=0;for(let k=0;k<n;k++)row+=(mask>>k)&1;
  if(row>=n)continue;
  for(let j=0;j<n;j++)if(!(mask&(1<<j))){
   const next=mask|(1<<j),v=dp[mask]+score[row][j];
   if(v>dp[next]){dp[next]=v;prev[next]=j;}
  }
 }
 const matched=Array(n),used=(1<<n)-1;
 let mask=used;
 for(let i=n-1;i>=0;i--){const j=prev[mask];matched[i]=j;mask^=1<<j;}
 return {match:matched,mean_MAC:dp[used]/n,minimum_MAC:Math.min(...matched.map((j,i)=>score[i][j]))};
}
function run(c){
 const catalog=[];
 for(const [nx,ny] of c.mesh){
  let arr=[];for(const m of c.modes_m)for(const n of c.modes_n)arr.push(mode(c,nx,ny,m,n));
  arr.sort((a,b)=>a.freq_Hz-b.freq_Hz);catalog.push({nx,ny,arr});
 }
 const comparisons=[];
 for(let i=0;i<catalog.length-1;i++){
  const a=catalog[i],b=catalog[i+1],S=a.arr.map(x=>b.arr.map(y=>mac(x.samples,y.samples))),matches=assign(S);
  const sameIds=matches.match.filter((j,k)=>a.arr[k].m===b.arr[j].m&&a.arr[k].n===b.arr[j].n).length;
  comparisons.push({pair:`${a.nx}x${a.ny} to ${b.nx}x${b.ny}`,mean_MAC:matches.mean_MAC,min_MAC:matches.minimum_MAC,
   id_match_count:sameIds,all_modes:a.arr.length,
   matched:a.arr.map((x,k)=>({from:`${x.m},${x.n}`,to:`${b.arr[matches.match[k]].m},${b.arr[matches.match[k]].n}`,mac:S[k][matches.match[k]],freq_from:x.freq_Hz,freq_to:b.arr[matches.match[k]].freq_Hz}))});
 }
 const conv=catalog.map(({nx,ny,arr})=>({grid:`${nx}x${ny}`,f11:arr.find(x=>x.m===1&&x.n===1).freq_Hz,
  f11_exact:arr.find(x=>x.m===1&&x.n===1).continuum_Hz,relative_error_pct:100*(arr.find(x=>x.m===1&&x.n===1).freq_Hz/arr.find(x=>x.m===1&&x.n===1).continuum_Hz-1)}));
 if(comparisons.some(x=>x.min_MAC<c.accept_MAC||x.id_match_count!==x.all_modes))throw Error("MAC invalid");
 return {study:"P36C",date:"2026-10-31",status:"INDEPENDENT PLATE-MODE MAC BENCHMARK, NOT GLOBAL 6DOF ENCLOSURE MAC",cfg:c,
  tests:catalog.length*12,comparisons,frequency_convergence:conv,
  warnings:["Eigenmodes from separable finite-difference simply-supported plate, not the global Q4 cabinet FEM; method tests matching and sampling only.","Fixed common probe interpolation and 12 selected low-order modes, not a proof for near-degenerate complex cabinet modes.","MAC>0.9 criterion is chosen for the benchmark only; global acceptable threshold and mode classification need independent definition.","Global P33B still has nonconforming hole and unmeasured joint stiffness."]};
}
if(require.main===module){
 const v=run(cfg),p=path.join(__dirname,'..','wyniki','p36c_plate_mode_MAC_20261031.json');
 fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
 console.log(JSON.stringify({comparisons:v.comparisons.map(x=>({pair:x.pair,mean_MAC:x.mean_MAC,min_MAC:x.min_MAC})),frequency_convergence:v.frequency_convergence},null,2));
}
module.exports={cfg,mode,mac,assign,run};
