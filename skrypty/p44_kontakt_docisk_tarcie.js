#!/usr/bin/env node
'use strict';
/* P44: research-only 3DOF unilateral-contact/friction screening. NOT CNC or a safety assessment.
 * Reproduce: node skrypty/p44_kontakt_docisk_tarcie.js
 * Pure Node.js, no dependencies. P38/P42/P43 source geometry and load scenarios.
 */
const C={
  "date": "2026-11-01",
  "center": [
    231,
    250
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
  "k": 1000,
  "g0": 9.80665,
  "masses": [
    13.61,
    15
  ],
  "accels": [
    1,
    5,
    10
  ],
  "eccs": [
    90,
    120,
    180
  ],
  "patterns": [
    "equal",
    "left_half"
  ],
  "axes": [
    "X",
    "Z",
    "Y"
  ],
  "lost": [
    0,
    1,
    2,
    3,
    4
  ],
  "preloads": [
    0,
    100,
    250,
    500,
    1000
  ],
  "mus": [
    0.2,
    0.4,
    0.6
  ]
};

function solve3(A,b) {
 const a=A.map((v,i)=>[...v,b[i]]);
 for(let j=0;j<3;j++){
  let p=j;
  for(let i=j+1;i<3;i++)if(Math.abs(a[i][j])>Math.abs(a[p][j]))p=i;
  if(Math.abs(a[p][j])<1e-8)return null;
  [a[j],a[p]]=[a[p],a[j]];
  const d=a[j][j];
  for(let h=j;h<4;h++)a[j][h]/=d;
  for(let i=0;i<3;i++)if(i!==j){
   const f=a[i][j];
   for(let h=j;h<4;h++)a[i][h]-=f*a[j][h];
  }
 }
 return a.map(v=>v[3]);
}

function dot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]}

function round4(n){return Math.round(n*1e4)/1e4}

function calculate(v,axis,mass,g,e,pattern,failed,P){
 const p=C.anchors[v].map((x,i)=>({
  id:i+1,k:C.k*(pattern==="left_half"&&x[0]<C.center[0]?0.5:1),
  vec:[1,x[0]-C.center[0],x[1]-C.center[1]]
 })).filter(x=>x.id!==failed);
 const F=mass*g*C.g0,Q=[axis==="Y"?F:0,axis==="X"?-e*F:0,axis==="Z"?e*F:0];
 function mat(items){
  const A=[[0,0,0],[0,0,0],[0,0,0]];
  for(const t of items)for(let i=0;i<3;i++)for(let j=0;j<3;j++)A[i][j]+=t.k*t.vec[i]*t.vec[j];
  return A;
 }
 const bilat=solve3(mat(p),Q);
 if(!bilat)throw Error("bilateral model singular");
 const threshold=Math.max(0,...p.map(t=>-t.k*dot(t.vec,bilat)));
 let winner=null;
 for(let mask=1;mask<(1<<p.length);mask++){
  const active=p.filter((t,i)=>(mask>>i)&1);
  const inactive=p.filter((t,i)=>!((mask>>i)&1));
  if(active.length<3)continue;
  const rhs=Q.map((q,i)=>q+inactive.reduce((s,t)=>s+P*t.vec[i],0));
  const u=solve3(mat(active),rhs);
  if(!u)continue;
  const n=p.map((t,i)=>({t,on:!!((mask>>i)&1),N:P+t.k*dot(t.vec,u)}));
  if(n.some(x=>x.on?x.N < -1e-6:x.N > 1e-6))continue;
  const got=[0,0,0];
  for(const x of n){
   const delta=(x.on?Math.max(0,x.N):0)-P;
   for(let i=0;i<3;i++)got[i]+=delta*x.t.vec[i];
  }
  const residual=Math.max(...Q.map((q,i)=>Math.abs(got[i]-q)/(1+Math.abs(q))));
  if(residual>1e-8)throw Error("equilibrium failure");
  const c=n.filter(x=>x.on&&x.N>1e-7),K=c.reduce((s,x)=>s+x.t.k,0);
  let mu=0;
  if(axis!=="Y"){
   if(K===0)mu=Infinity;
   for(const x of c)mu=Math.max(mu,F*x.t.k/K/x.N);
  }
  const trial={contacts:c.length,residual,mu};
  if(!winner||trial.contacts>winner.contacts)winner=trial;
 }
 return {variant:v,axis,mass_kg:mass,accel_g:g,e_mm:e,pattern,failed:failed||"none",preload_N:P,
  full_contact_preload_threshold_N:round4(threshold),
  status:winner?"solved":"unresolved_full_rank",contacts:winner?winner.contacts:null,
  opened:winner?p.length-winner.contacts:null,
  mu_required:winner&&Number.isFinite(winner.mu)?round4(winner.mu):null,
  mu_infinite:!!winner&&!Number.isFinite(winner.mu),
  friction_ok_02:!!winner&&winner.mu<=0.2+1e-10,
  friction_ok_04:!!winner&&winner.mu<=0.4+1e-10,
  friction_ok_06:!!winner&&winner.mu<=0.6+1e-10,
  residual:winner?winner.residual:null,_mu:winner?winner.mu:null};
}

function csv(rows){
 const cols=["variant","axis","mass_kg","accel_g","e_mm","pattern","failed","preload_N","full_contact_preload_threshold_N","status","contacts","opened","mu_required","mu_infinite","friction_ok_02","friction_ok_04","friction_ok_06"];
 return cols.join(",")+"\n"+rows.map(r=>cols.map(c=>'"'+String(r[c]??"").replace(/"/g,'""')+'"').join(",")).join("\n")+"\n";
}

function chart1(groups){
 const s=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 400"><rect width="900" height="400" fill="#f8fafc"/><g font-family="Arial" fill="#162d42"><text x="20" y="32" font-size="20" font-weight="bold">P44A — pełny kontakt podpór</text><text x="20" y="56" font-size="12">Udział przypadków bez rozwarcia. 540 przypadków na wariant i docisk; wyłącznie model.</text>`];
 for(let j=0;j<=4;j++){
  const y=322-j*59;
  s.push(`<line x1="80" y1="${y}" x2="860" y2="${y}" stroke="#a5b7c7"/><text x="70" y="${y+5}" font-size="12" text-anchor="end">${j*25}%</text>`);
 }
 for(let i=0;i<C.preloads.length;i++){
  const P=C.preloads[i],x=104+151*i;
  s.push(`<text x="${x+34}" y="350" font-size="13" text-anchor="middle">${P} N</text>`);
  for(const [j,v,color] of [[0,"A","#3169ba"],[1,"B","#ce7627"]]){
   const row=groups.find(z=>z.variant===v&&z.preload_N===P),pct=row.full_contact/row.total;
   const h=pct*236,px=x+j*34;
   s.push(`<rect x="${px}" y="${322-h}" width="28" height="${h}" rx="3" fill="${color}"/><text x="${px+14}" y="${315-h}" font-size="11" text-anchor="middle">${(pct*100).toFixed(1)}%</text>`);
  }
 }
 s.push(`<rect x="620" y="72" width="15" height="15" fill="#3169ba"/><text x="640" y="85" font-size="12">Rama A</text><rect x="725" y="72" width="15" height="15" fill="#ce7627"/><text x="745" y="85" font-size="12">Belki B</text><text x="450" y="389" font-size="12" text-anchor="middle">Hipotetyczny docisk początkowy na punkt [N]</text></g></svg>\n`);
 return s.join("");
}

function chart2(ref){
 const out=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 420"><rect width="940" height="420" fill="#f8fafc"/><g font-family="Arial" fill="#162d42"><text x="20" y="31" font-size="20" font-weight="bold">P44B — warunkowe progi współczynnika tarcia μ</text><text x="20" y="54" font-size="12">13,61 kg; 5g; 120 mm; oś X; równe sztywności. Zadany rozkład ścinania, nie pomiar.</text>`];
 for(let i=0;i<C.preloads.length;i++)out.push(`<text x="${232+141*i}" y="92" font-size="13" text-anchor="middle">${C.preloads[i]} N</text>`);
 const cases=[["A",false],["A",true],["B",false],["B",true]];
 for(let j=0;j<cases.length;j++){
  const [v,lost]=cases[j],y=110+j*69;
  out.push(`<text x="12" y="${y+22}" font-size="13">${v} — ${lost?"utrata 1 punktu":"4 punkty"}</text>`);
  for(let i=0;i<C.preloads.length;i++){
   const P=C.preloads[i],a=ref.filter(r=>r.variant===v&&r.axis==="X"&&r.preload_N===P&&(lost?r.failed!=="none":r.failed==="none"));
   const valid=a.length>0&&a.every(r=>r.status==="solved"&&!r.mu_infinite);
   const req=valid?Math.max(...a.map(r=>r._mu)):null;
   const color=req!==null&&req<=0.4?"#cbe9d4":req!==null&&req<=0.6?"#f6e2b5":"#f2c6c6";
   const x=175+i*141;
   out.push(`<rect x="${x}" y="${y}" width="112" height="43" rx="4" stroke="#adbccc" fill="${color}"/><text x="${x+56}" y="${y+27}" font-size="13" text-anchor="middle">${req===null?"brak rozwiąz.":req>5?">5":req.toFixed(2)}</text>`);
  }
 }
 out.push(`<text x="20" y="408" font-size="11">Po utracie 1 punktu pokazano najgorszy z 4 wariantów; brak rozwiązania nie oznacza fizycznej awarii.</text></g></svg>\n`);
 return out.join("");
}

function build(){
 const rows=[],reference=[],groups=[];
 for(const v of ["A","B"])for(const axis of C.axes)for(const g of C.accels)for(const e of C.eccs)for(const m of C.masses)for(const pat of C.patterns)for(const lost of C.lost)for(const P of C.preloads){
  const row=calculate(v,axis,m,g,e,pat,lost,P);rows.push(row);
  if(m===13.61&&g===5&&e===120&&pat==="equal")reference.push(row);
 }
 if(rows.length!==5400||reference.length!==150)throw Error("bad grid");
 for(const v of ["A","B"])for(const P of C.preloads){
  const a=rows.filter(r=>r.variant===v&&r.preload_N===P);
  groups.push({variant:v,preload_N:P,total:a.length,solved:a.filter(r=>r.status==="solved").length,
    full_contact:a.filter(r=>r.status==="solved"&&r.opened===0).length,
    with_contact_release:a.filter(r=>r.status==="solved"&&r.opened>0).length,
    friction_ok_02:a.filter(r=>r.friction_ok_02).length,
    friction_ok_04:a.filter(r=>r.friction_ok_04).length,
    friction_ok_06:a.filter(r=>r.friction_ok_06).length});
 }
 const ref=(v,lost)=>reference.find(r=>r.variant===v&&r.axis==="X"&&r.failed===lost&&r.preload_N===0).full_contact_preload_threshold_N;
 const checks={A4:ref("A","none"),A3:ref("A",1),B4:ref("B","none"),B3:ref("B",1)};
 if(Math.abs(checks.A4-114.4016)>0.01||Math.abs(checks.A3-228.8032)>0.01||Math.abs(checks.B4-364.005)>0.01||Math.abs(checks.B3-728.01)>0.01)throw Error("P43 control mismatch");
 const maxR=Math.max(...rows.filter(r=>r.status==="solved").map(r=>r.residual));
 if(maxR>1e-8)throw Error("equilibrium residual exceeded");
 const summary={study:"P44A/P44B",date:C.date,inputs:C,grid:{contact_cases:rows.length,friction_checks:rows.length*C.mus.length,reference_cases:reference.length},
  controls:{p43_thresholds_N:checks,max_scaled_equilibrium_residual:maxR},
  groups,reference:reference.map(({_mu,...r})=>r),
  limitations:["Rigid 3DOF plate and linear unilateral normal springs; not nonlinear contact FEM.","Preload is an ideal constant internal compression force per surviving support, not torque or real clamp force.","Friction: T_i=F_t*k_i/sum(k_active) is assumed, not computed from tangent stiffness or stick-slip.","Full-rank active-set search ignores possible lower-rank neutral equilibrium; unresolved != physical failure.","No real basket 3D geometry, screw design, joint relaxation, bolt tension, insert pull-out, MDF strength, or material friction measurements."]};
 return {rows,reference,summary,allCsv:csv(rows),svgA:chart1(groups),svgB:chart2(reference)};
}

if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const o=build(),dir=path.join(__dirname,'..','wyniki');fs.mkdirSync(dir,{recursive:true});
 fs.writeFileSync(path.join(dir,'p44_kontakt_5400.csv'),o.allCsv);
 fs.writeFileSync(path.join(dir,'p44_podsumowanie_20261101.json'),JSON.stringify(o.summary,null,2)+'\n');
 fs.writeFileSync(path.join(dir,'p44a_pelny_kontakt.svg'),o.svgA);
 fs.writeFileSync(path.join(dir,'p44b_wymagany_wspolczynnik_tarcia.svg'),o.svgB);
 console.log('P44 '+o.rows.length+' cases, '+(o.rows.length*C.mus.length)+' friction checks, residual '+o.summary.controls.max_scaled_equilibrium_residual);
}
module.exports={C,calculate,build};
