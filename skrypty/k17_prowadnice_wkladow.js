#!/usr/bin/env node
"use strict";
// K17 reference side-support alternative that preserves the 50mm rear acoustic mat envelope.
const fs=require("node:fs"),path=require("node:path");
function buildK17(k15){
  const q=v=>Number(v.toFixed(6)),cols=[],tabs=[],clashes=[],body=k15.cfg.body_mm;
  const all=k15.parts.map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm}));
  const clash=(a,b)=>a.o.every((v,j)=>Math.min(v+a.s[j],b.o[j]+b.s[j])-Math.max(v,b.o[j])>1e-7);
  const groups=new Map();
  for(const m of k15.module_positions){
    const [x,y,z]=m.global_origin_xyz_mm,[sx,sy,sz]=m.dims_xyz_mm;
    const type=y===52?"front_large":(sx===180?"rear_small":"rear_large");
    const key=`${type}_${x}`;
    if(!groups.has(key))groups.set(key,[]);
    groups.get(key).push(m);
  }
  if(groups.size!==6)throw Error("group count "+groups.size);
  let colindex=0;
  for(const [key,group]of groups){
    const first=group[0],[x,y,z]=first.global_origin_xyz_mm,[sx,sy,sz]=first.dims_xyz_mm;
    const type=key.startsWith("front")?"front":(key.startsWith("rear_small")?"rear_small":"rear_large");
    const lane=type==="front"?[44,52]:(type==="rear_small"?[224,236]:[208,220]);
    const xset=[x+24,x+sx-24-16];
    if(sx===180){xset[0]=x+20;xset[1]=x+sx-20-16;}
    for(const [pair,xx]of xset.entries()){
      const col={id:`G17_COLUMN_${String(++colindex).padStart(2,"0")}`,group:key,row:type,module_indices:group.map(m=>m.i),
        o:[xx,lane[0],22],s:[16,lane[1]-lane[0],456],
        anchored_onto_bottom_and_top_faces:true,attachment_joint_qualified:false};
      cols.push(col);
      for(const m of group){
        const [mx,my,mz]=m.global_origin_xyz_mm,[a,b,c]=m.dims_xyz_mm;
        for(const side of ["shelf","retainer"]){
          const tz=side==="shelf"?mz-4:mz+c;
          const t={id:`G17_${m.i}_${side}_${pair+1}`,module_index:m.i,group:key,position:side,
            o:[xx,lane[1]-1,tz],s:[16,(my+12)-(lane[1]-1),4],
            nominal_contact_overlap_y_mm:12,unbraced_gap_y_mm:my-lane[1],
            qualified_fastener:false};
          if(t.s[1]<=0)throw Error("incorrect module bound");
          tabs.push(t);
        }
      }
    }
  }
  if(cols.length!==12||tabs.length!==80)throw Error("expected columns and tabs");
  // Check disjoint solids except intended bonded column/tongue overlap at y-end minus 1 mm.
  for(const c of cols){
    if(all.some(x=>clash(c,x)))clashes.push(["column MDF collision",c.id,all.filter(x=>clash(c,x)).map(x=>x.id)]);
  }
  for(const t of tabs){
    if(all.some(x=>clash(t,x)))clashes.push(["tongue MDF collision",t.id,all.filter(x=>clash(t,x)).map(x=>x.id)]);
  }
  for(let i=0;i<cols.length;i++)for(let j=i+1;j<cols.length;j++)if(clash(cols[i],cols[j]))clashes.push(["column column",cols[i].id,cols[j].id]);
  for(let i=0;i<tabs.length;i++)for(let j=i+1;j<tabs.length;j++)if(clash(tabs[i],tabs[j]))clashes.push(["tongue tongue",tabs[i].id,tabs[j].id]);
  const matClashes=cols.concat(tabs).filter(a=>a.o[1]<403&&a.o[1]+a.s[1]>353);
  if(clashes.length||matClashes.length)throw Error("K17 collision "+JSON.stringify({clashes:clashes.slice(0,6),matClashes:matClashes.slice(0,6)}));
  // conservative motor obstacle from P30A = X[36.8,425.2], Y[44,222], Z[55.8,444.2]
  const driverBox={o:[231-194.2,44,250-194.2],s:[388.4,178,388.4]};
  const driverHits=cols.concat(tabs).filter(a=>clash(a,driverBox));
  if(driverHits.length)throw Error("Conservative driver AABB clash "+driverHits.map(x=>x.id).slice(0,5));
  const fvol=a=>a.reduce((v,z)=>v+z.s.reduce((s,x)=>s*x,1),0)/1e6;
  const colvol=fvol(cols),tabvol=fvol(tabs);
  // Every tab intentionally enters its column by 1 mm in Y.
  const intentionalOverlap=80*16*4*1/1e6;
  const total=colvol+tabvol-intentionalOverlap;
  const groupCounts={};
  for(const g of groups.values())groupCounts[g[0].dims_xyz_mm[0]===180?"small":g[0].global_origin_xyz_mm[1]===52?"front_large":"rear_large"]=(groupCounts[g[0].dims_xyz_mm[0]===180?"small":g[0].global_origin_xyz_mm[1]===52?"front_large":"rear_large"]||0)+1;
  const s={study:"K17",date:"2026-11-04",status:"ALTERNATIVE NOMINAL SUPPORT TRACK MODEL — NOT MECHANICALLY OR ASSEMBLY QUALIFIED; CNC HOLD",
    source:"K15 model P30E 20 module locations; K16 48 overlaps in rear 50mm mat",
    design_intent:"12 full-height vertical load-path spine profiles between bottom and top cabinet MDF, each with 4-mm integrated ledges and retainer lips; no 50mm mat penetration; module guides may slide through 10mm vertical gaps",
    spine_count:cols.length,integrated_contact_lips_count:tabs.length,nominal_spine_plus_lips_envelope_count:92,
    groups:groupCounts,material_candidate:"wood/plywood/metal UNSPECIFIED; 16mm x-thickness only clearance candidate; no demonstrated strength",
    per_module_lips:4,
    no_clashes_with_k15_reference_parts:true,no_clashes_between_12_spines_or_80_lips:true,
    no_overlap_with_50mm_rear_mat:true,no_overlap_with_CONSERVATIVE_P30A_basket_AABB:true,
    fixed_support_volume_l:q(total),spine_volume_l:q(colvol),lip_volume_l_including_1mm_overlap:q(tabvol),
    intentional_union_overlap_l:q(intentionalOverlap),
    potential_nominal_reference_state_volumes_if_ALL_rails_present:Object.fromEntries(Object.entries(k15.reference_net_l_P30E_no_new_pads).map(([state,v])=>[state,q(v-total)])),
    nominal_module_positions_retain_their_reference_k15_geometry:true,
    expected_issues:[
      "Fitting 4-mm lips into 10-mm gaps is only geometric; real fitting/clearance for modules, latches and screwdriver not tested",
      "12 long narrow spines each spanning 456 mm must be joined physically to bottom and top MDF; no screw, adhesive or buckling strength yet specified",
      "Positive hold-down remains unqualified; module may rattle and slide in Y, X without a separately designed locking and anti-rattle clip",
      "No true solid full 3D basket collision or module insertion/removal paths; conservative P30A basket AABB only",
      "50-mm acoustic mat preserved geometrically, but added rails perturb cavity flow and modal behaviour, require P34/P21 rerun",
      "Reference rail 16mm cross section may not be manufacturable from chosen MDF22/MDF8 stock or CNC bit",
      "Reference volume change is NOT a certified net volume; hardware/driver, K01 pads and mat overlap could require overlap-aware union volume",
      "No acoustic sealing, vibration fatigue, transportation inversion, temperature/humidity cycling or pull-out tests"
    ],
    spines:cols,contact_lips:tabs
  };
  const scad=`// K17 CONCEPTUAL integrated vertical spine supports and retaining lips.\n// It includes K15 cabinet bodies. Unlike K16 rear-wall pads it does NOT cross rear 50mm acoustic mat.\n// No physical screws, latches, adhesive selection, strength, module service or CNC fabrication approved.\ninclude <K15_p30e_zlozenie_parametryczne_NIE_CNC.scad>\nshow_K17_rails=true;\nshow_K17_lips=true;\nK17_COLUMNS=[\n${cols.map(c=>` [${JSON.stringify(c.id)},${JSON.stringify(c.o)},${JSON.stringify(c.s)}]`).join(",\n")}\n];\nK17_CONTACTS=[\n${tabs.map(t=>` [${t.module_index},${JSON.stringify(t.o)},${JSON.stringify(t.s)},${JSON.stringify(t.position)}]`).join(",\n")}\n];\nif(show_K17_rails)for(c=K17_COLUMNS)color([0.09,0.62,0.39,0.9])translate(c[1])cube(c[2]);\nif(show_K17_lips)for(c=K17_CONTACTS)color(c[3]==\"shelf\"?[0.10,0.8,0.22,1]:[0.96,0.38,0.21,1])translate(c[1])cube(c[2]);\necho(\"K17: 12 full-height support profiles with 80 integrated geometrical lips, 0 nominal overlaps with mat or P30A basket AABB\");\necho(\"NOT CNC: 12 spines and lips untested; no screw, latch, anti-rattle or inversion qualification\");\n`;
  return {stats:s,scad};
}
function main(){const root=path.resolve(__dirname,".."),a=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k15_p30e_przed_CNC_zestawienie.json"),"utf8")),o=buildK17(a); const files={"wyniki/k17_prowadnice_boczne_wkladow.json":JSON.stringify(o.stats,null,2)+"\n","dokumentacja/K17_p30e_prowadnice_i_zabezpieczenia_NIE_CNC.scad":o.scad};for(const [p,content] of Object.entries(files))fs.writeFileSync(path.join(root,p),content);console.log(JSON.stringify({spines:o.stats.spine_count,lips:o.stats.integrated_contact_lips_count,mat_clear:o.stats.no_overlap_with_50mm_rear_mat,basket_AABB_clear:o.stats.no_overlap_with_CONSERVATIVE_P30A_basket_AABB,status:o.stats.status}));}
if(require.main===module)main();module.exports={buildK17,main};
