#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const run=function run(cfg,room,drivers,presets) {
 const pi=Math.PI,c=343,rho=1.2041,Fs=96000,Vb=.120,dim=[room.width_x_m,room.length_y_m,room.height_z_m],F=[20,25,31.5,40,50,63,80,100],T=[.2,.4,.8],TAU=[.02,.2,2],D=[0,2,5,10],G=[.8,1,1.2],W=1.02,DEPTH=.45;
 const round=x=>Number(x.toFixed(5)),cz=(r=0,i=0)=>({r,i}),ca=(a,b)=>cz(a.r+b.r,a.i+b.i),cm=(a,b)=>cz(a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r),cs=(a,v)=>cz(a.r*v,a.i*v),cd=(a,b)=>cs(cm(a,cz(b.r,-b.i)),1/(b.r*b.r+b.i*b.i)),cc=a=>Math.hypot(a.r,a.i),e=x=>cz(Math.cos(x),Math.sin(x));
 const model=Object.fromEntries(drivers.map(d=>[d.id,d.model])),sects=Object.fromEntries(presets.map(p=>[p.id,p.sections]));
 function hIir(id,f) {const z=e(-2*pi*f/Fs),z2=cm(z,z);return sects[id].reduce((h,b)=>cm(h,cd(ca(ca(cz(b.b0),cs(z,b.b1)),cs(z2,b.b2)),ca(ca(cz(1),cs(z,b.a1)),cs(z2,b.a2)))),cz(1));}
 function volpervolt(id,f) {
  const a=model[id],w=2*pi*f,n=id==="C02"?1:2,sd=a.sd_cm2*1e-4,cms=(a.vas_l/1000)/(rho*c*c*sd*sd),mms=1/((2*pi*a.fs_hz)**2*cms),rms=2*pi*a.fs_hz*mms/a.qms,BL=Math.sqrt(2*pi*a.fs_hz*mms*a.re_ohm/a.qes);
  const Ze=cz(a.re_ohm,w*a.le_mh/1000),Zm=cz(rms,w*mms-1/(w*cms)-n*rho*c*c*sd*sd/(w*Vb));
  return cs(cm(cd(cz(BL),ca(cm(Ze,Zm),cz(BL*BL))),hIir(id,f)),n*sd);
 }
 const tonal={};for(const id of ["C02","C05"]){const q=F.map(f=>volpervolt(id,f)),ref=q[3];tonal[id]={q40_m3s_per_vrms:Number(cc(ref).toPrecision(12)),relative_complex:q.map(x=>{let v=cd(x,ref);return{re:round(v.r),im:round(v.i),rel_db:round(20*Math.log10(cc(v)))}})};}
 const kcut=12,modes=[];
 for(let nx=0;nx<=Math.floor(kcut*dim[0]/pi);nx++)for(let ny=0;ny<=Math.floor(kcut*dim[1]/pi);ny++)for(let nz=0;nz<=Math.floor(kcut*dim[2]/pi);nz++){
  let ksq=(pi*nx/dim[0])**2+(pi*ny/dim[1])**2+(pi*nz/dim[2])**2;if(ksq>kcut*kcut)continue;
  modes.push({n:[nx,ny,nz],ksq,amp:Math.pow(2,(nx>0)+(ny>0)+(nz>0))*Math.exp(-.5*(.12**2+.03**2)*ksq)});
 }
 const bs=(n,pos)=>Math.cos(pi*n[0]*pos[0]/dim[0])*Math.cos(pi*n[1]*pos[1]/dim[1])*Math.cos(pi*n[2]*pos[2]/dim[2]);
 const listener=cfg.assumed_listener_xyz_m,receivers=cfg.diagnostic_neighbor_offsets_xyz_m.map(p=>listener.map((v,i)=>v+p[i]));
 const sets=cfg.source_sets.map(set=>{const positions=set.positions_xyz_m;return{id:set.id,positions,note:set.note,fit_2_cabinets:positions.every(p=>p[0]>=W/2&&p[0]<=dim[0]-W/2&&p[1]>=DEPTH/2&&p[1]<=dim[1]-DEPTH/2)&&Math.abs(positions[1][0]-positions[0][0])>=W,unused_monitor_fit:"NOT VERIFIED"};});
 function roomTransfer(positions,t60,tau) {
  const pref=rho*c*c/(dim[0]*dim[1]*dim[2]),damp=3*Math.log(10)/t60;
  const src=positions.map(p=>modes.map(m=>bs(m.n,p)));
  const rec=receivers.map(p=>modes.map(m=>bs(m.n,p)));
  return F.map(f=>{
   const omega=2*pi*f,kn=modes.map(m=>cs(m.ksq===0?cd(cz(pref),cz(1/tau,omega)):cd(cz(0,pref*omega),cz(c*c*m.ksq-omega*omega,2*damp*omega)),m.amp));
   const out=[];
   for(let j=0;j<rec.length;j++){let pair=[cz(),cz()];for(let k=0;k<kn.length;k++){let b=cs(kn[k],rec[j][k]);pair[0]=ca(pair[0],cs(b,src[0][k]));pair[1]=ca(pair[1],cs(b,src[1][k]));}out.push(pair);}
   return out;
  });
 }
 function trial(H,id,g,delay) {
  const response=H.map((slice,i)=>slice.map(pair=>{const right=cm(pair[1],cs(e(-2*pi*F[i]*delay/1000),g));const q=tonal[id].relative_complex[i];return cm(cz(q.re,q.im),ca(pair[0],right));}));
  const base40=cc(H[3][0][0]); // not used for constraints; comparing pair below
  const at40=cc(response[3][0]), db=response.map(slice=>20*Math.log10(cc(slice[0])/at40));
  const span=Math.max(...db.slice(0,7))-Math.min(...db.slice(0,7));
  const neighbor=Math.max(...response.slice(0,7).flatMap(s=>s.slice(1).map(z=>Math.abs(20*Math.log10(cc(z)/cc(s[0]))))));
  return{g,delay_ms:delay,room_at40:at40,span_db:span,max_neighbor_db:neighbor,relative_db:db};
 }
 const cases=[],summary=[],nominal=[];
 for(const set of sets){
  if(!set.fit_2_cabinets){cases.push({set_id:set.id,status:"REJECT_RECTANGULAR_CABINET_ENVELOPE"});continue;}
  for(const t60 of T)for(const tau of TAU){
   const H=roomTransfer(set.positions,t60,tau),by=[];
   for(const id of ["C02","C05"]){
    const base=trial(H,id,1,0);
    const sorted=[];
    for(const g of G)for(const delay of D){
     const tr=trial(H,id,g,delay);
     const relative40=20*Math.log10(tr.room_at40/base.room_at40);
     const neighborChange=tr.max_neighbor_db-base.max_neighbor_db;
     const permissible=relative40>=-3&&neighborChange<=3;
     if(permissible)sorted.push({...tr,room40_vs_equal_db:relative40,neighbor_increase_db:neighborChange,score:tr.span_db+Math.max(0,neighborChange)*.1});
    }
    sorted.sort((x,y)=>Math.abs(x.score-y.score)<1e-7 ? (Math.abs(x.g-1)-Math.abs(y.g-1) || x.delay_ms-y.delay_ms) : x.score-y.score);
    const best=sorted[0]||{...base,room40_vs_equal_db:0,neighbor_increase_db:0};
    by.push({id,unity:{span_db:round(base.span_db),neighbor_max_abs_db:round(base.max_neighbor_db),response_20_to_100_relative_40_db:base.relative_db.map(round)},
      robust_grid:{right_gain:best.g,right_delay_ms:best.delay_ms,span_db:round(best.span_db),neighbor_max_abs_db:round(best.max_neighbor_db),relative_40_level_change_db:round(best.room40_vs_equal_db),response_20_to_100_relative_40_db:best.relative_db.map(round)},valid_trials:sorted.length});
   }
   cases.push({set_id:set.id,modal_t60_s:t60,zero_tau_s:tau,models:by});
  }
 }
 const accepted=cases.filter(x=>x.models),rejected=cases.filter(x=>!x.models);
 for(const set of sets){
  const rs=accepted.filter(x=>x.set_id===set.id);if(!rs.length){summary.push({id:set.id,geometry_accepted:false});continue}
  const item={id:set.id,geometry_accepted:true,environmental_cases:rs.length};
  for(const id of ["C02","C05"]){const m=rs.map(x=>x.models.find(a=>a.id===id));
   item[id]={unity_span_range_db:[round(Math.min(...m.map(x=>x.unity.span_db))),round(Math.max(...m.map(x=>x.unity.span_db)))],
     robust_grid_span_range_db:[round(Math.min(...m.map(x=>x.robust_grid.span_db))),round(Math.max(...m.map(x=>x.robust_grid.span_db)))],
     worst_diagnostic_neighbor_db:round(Math.max(...m.map(x=>x.unity.neighbor_max_abs_db)))};
  }summary.push(item);
 }
 for(const cse of accepted)if(cse.modal_t60_s===.4&&cse.zero_tau_s===.2)nominal.push(cse);
 const symmetryTest=roomTransfer(sets[0].positions,.4,.2);
 const mirrorError=Math.max(...symmetryTest.map(x=>cc(ca(x[0][0],cs(x[0][1],-1)))/Math.max(1,cc(x[0][0]))));
 if(cases.length!==28||accepted.length!==27||rejected[0]?.set_id!=="C"||mirrorError>1e-9)throw Error("room regression failed");
 return{schema:"B12-07_original_brief_two_separate_subs_modal_room",date:"2026-11-02",
  config:{room_xyz_m:dim,room_m3:dim.reduce((x,y)=>x*y,1),frequencies_hz:F,modal_t60_s:T,zero_relax_tau_s:TAU,source_sets:sets,
    reference_listener_xyz_m:listener,neighbor_offsets_xyz_m:cfg.diagnostic_neighbor_offsets_xyz_m,cabinet_width_m:W,cabinet_body_depth_m:DEPTH,
    mode_count:modes.length,mode_kcut_m_inverse:kcut,smooth_source_m:.12,smooth_receiver_m:.03,
    delays_ms:D,gain_grid:G,
    volume_l_each_sub:120,biquad_fs_hz:Fs,model:"P26 Neumann rectangular box and 2-source transfer p/U; each cabinet one pressure lumped source. T/S C02 / C05 + fixed B12-03 five IIR, no dynamic room loading",
    optimization:"At sweet spot, 20-80Hz relative span minimization with >=-3dB at 40Hz vs equal undelayed channels and <=+3dB change of diagnostic neighbor deviation. Still NOT real calibration."},
  counts:{position_sets:sets.length,screened_room_cases:cases.length,accepted_room_cases:accepted.length,geometry_rejected:rejected.map(x=>x.set_id),two_sub_configurations:accepted.length*2},
  room_axes_hz:{x_width:round(c/(2*dim[0])),y_length:round(c/(2*dim[1])),z_height:round(c/(2*dim[2]))},
  drivers_tonal_normalized:tonal,profiles:cases,summary,central_cases:nominal,
  adamaudio_specs:{Sub12:{freq_from_hz:22,freq_to_hz:150,max_peak_spl_1m_gte_db:115,thd_above_60hz_lte_percent:1,depth_mm:450,source:"https://www.adam-audio.com/en/subwoofers/sub12/"},Sub15:{freq_from_hz:20,freq_to_hz:150,max_spl_1m_gte_db:120,thd_above_60hz_lte_percent:1,depth_mm:525,source:"https://www.adam-audio.com/en/subwoofers/sub15/"}},
  controls:{mirror_symmetry_relative:round(mirrorError),room_model_source:"P26 preexisting methods",selectivity:"No user-verified cabinet coordinates; optimization not installation recommendation",
    comparative_headroom:"not assessed; normalized at 40Hz; consult B12-04 and measured driver THD/compression"},
  limitations:["Even 30-50dB modal troughs are artifacts of unverified rectangular rigid-room damping and null locations, NOT guaranteed real measured equalization","T60 and uniform mode relaxation are artificial independent scenarios, no absorption boundaries or openings","Room transfer normalized by 40Hz; no absolute SPL in room, no measured room gain and no benchmarking clean 20Hz SPL against ADAM official 1m maximum","No measured monitor/sub crossover phase, no 8-channel integrated-system tuning, no geometry of furniture or confirmed exact source positions","A-C symmetric source placement may be impractical; C excluded for cabinet width; source points represent diaphragm face, not exact cabinet center","Two STX in one sealed sub not the user's baseline one-driver per-sub; two sub cabinets require four STX and two amplifiers","DSP protection not evaluated, mathematical gain/delay is a screening grid only; NEVER import into miniDSP without measurements","ADAM Sub15 525mm depth exceeds 500mm prototype limit but serves as performance reference"]};
};
const root=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const cfg=read('dane/konfiguracje/p26_scenariusze.json'),room=read('dane/konfiguracje/pokoj_odsluchowy.json');
const drivers=read('dane/przetworniki/pula_rozszerzona.json').drivers.filter(d=>['C02','C05'].includes(d.candidate_id)).map(d=>({id:d.candidate_id,model:d.model}));
const presets=read('wyniki/b12_03_iir_i_rozrzut_20261102.json').presets.filter(x=>x.V===120&&x.hp===18).map(x=>({id:x.id,sections:x.sections}));
const result=run(cfg,room,drivers,presets);
assert.deepStrictEqual(result,read('wyniki/b12_07_dwa_suby_pokoj_20261102.json'));
console.log('B12-07 OK',result.counts,'model modes=',result.config.mode_count);
