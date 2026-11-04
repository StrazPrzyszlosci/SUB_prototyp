#!/usr/bin/env node
"use strict";
// K20 reusable geometry-only research generator (no mechanically qualified keeper).
const fs=require("node:fs"),path=require("node:path");
function buildK20(k15,k17){
  const cub=p=>({id:p.id||"",o:p.o||p.local_origin_global_xyz_mm,s:p.s||p.box_size_xyz_mm});
  const mm3=p=>p.s[0]*p.s[1]*p.s[2];
  const overlap=(a,b)=>a.o.reduce((v,x,i)=>v*Math.max(0,Math.min(x+a.s[i],b.o[i]+b.s[i])-Math.max(x,b.o[i])),1);
  const spine=k17.spines, low=k17.contact_lips.filter(x=>x.position==="shelf"), high=k17.contact_lips.filter(x=>x.position==="retainer");
  if(spine.length!==12||low.length!==40||high.length!==40||k15.parts.length!==138||k15.module_positions.length!==20) throw Error("unexpected upstream");
  const keeper=high.map(t=>{
    const parent=spine.find(c=>c.group===t.group&&Math.abs(c.o[0]-t.o[0])<1e-7);
    const mod=k15.module_positions.find(m=>m.i===t.module_index);
    if(!parent||!mod||Math.abs(t.o[1]-(parent.o[1]+parent.s[1]-1))>1e-7)throw Error("K17 interface assumptions changed");
    const y=parent.o[1]+parent.s[1],z=mod.global_origin_xyz_mm[2]+mod.dims_xyz_mm[2]+2;
    return {id:"K20_UPPER_"+t.id,module_index:mod.i,parent_spine:parent.id,
      o:[t.o[0],y,z],s:[16,t.o[1]+t.s[1]-y,4],
      nominal_box_top_gap_mm:2,mounting_method:"UNRESOLVED BUTT JOINT ONLY — NOT A FASTENER",
      cnc_approved:false};
  });
  const fixed=k15.parts.map(cub);
  const railCubes=spine.map(cub),lowerCubes=low.map(cub),keeperCubes=keeper.map(cub);
  const mat={id:"mat",o:[22,353,22],s:[976,50,456]};
  const errors=[];
  for(let i=0;i<keeper.length;i++){
    const a=keeperCubes[i];
    for(const b of [...fixed,...railCubes,...lowerCubes])if(overlap(a,b)>1e-7)errors.push([a.id,b.id]);
    for(let j=0;j<i;j++)if(overlap(a,keeperCubes[j])>1e-7)errors.push([a.id,keeperCubes[j].id]);
    if(overlap(a,mat)>1e-7)errors.push([a.id,"mat"]);
  }
  for(const a of [...railCubes,...lowerCubes])if(overlap(a,mat)>1e-7)errors.push([a.id,"mat"]);
  if(errors.length)throw Error("collision "+JSON.stringify(errors.slice(0,5)));
  const upperK17Volume=high.reduce((s,t)=>s+mm3(cub(t))-16*4*1,0)/1e6;
  const fixedVolume=k17.fixed_support_volume_l-upperK17Volume;
  const states={};
  for(const state of ["100","120","150"]){
    const selected=k15.module_positions.filter(m=>m.candidate_state_inclusion.includes(state)).map(m=>m.i);
    const active=keeper.filter(k=>selected.includes(k.module_index));
    const activeL=active.reduce((s,k)=>s+mm3(k),0)/1e6;
    states[state]={box_count:selected.length,upper_keeper_envelopes:active.length,
      fixed_fixture_displacement_l:+fixedVolume.toFixed(6),
      removable_envelope_displacement_l:+activeL.toFixed(6),
      total_fixture_displacement_l:+(fixedVolume+activeL).toFixed(6),
      conditional_net_l_before_actual_hardware:+(k15.reference_net_l_P30E_no_new_pads[state]-fixedVolume-activeL).toFixed(6)};
  }
  const slots=spine.map(c=>({id:c.id,row:c.row,cut_y0:Math.max(44,c.o[1]-.25),
    opens_at_y44:Math.max(44,c.o[1]-.25)<=44+1e-7}));
  if(slots.filter(x=>x.opens_at_y44).length!==4)throw Error("pocket count changed");
  const ap=[180,210].map(w=>({module_width_mm:w,
    reference_circle_radius_mm:177.9,hypothetical_clearance_per_side_mm:6,
    centered_individual_entry_margin_mm:+(177.9-Math.hypot(w/2+6,50+6)).toFixed(6)}));
  const result={study:"K20",date:"2026-11-04",status:"CNC HOLD — geometry-only proposed removable keeper, no real attachment or swept path",
    upstream:"K15 shell, K17 spines/tabs, K19 lever corrections",
    reference_counts:{fixed_spines:12,fixed_bottom_lips:40,detachable_upper_envelopes:40,modules:20,positive_static_AABB_collisions:0,mat_envelope_positive_collisions:0,edge_breaking_pockets_top_and_bottom_total:8},
    nominal_unloaded_keeper_to_box_gap_mm:2,
    verified_keeper_fastener_count:0,detachable_keeper_force_path_proved:false,assembly_path_3D_proved:false,
    K18_integral_upper_rail_DXF_superseded_for_this_concept:true,
    baseline_K17_all_fixed_support_l:k17.fixed_support_volume_l,
    baseline_K17_upper_integral_l:+upperK17Volume.toFixed(6),
    permanent_spine_and_lower_lip_displacement_l:+fixedVolume.toFixed(6),
    conditional_volume_states:states,isolated_centered_aperture_screen:ap,
    individual_keeper_envelopes:keeper,
    detected_front_edge_pocket_rows:slots.filter(x=>x.opens_at_y44),
    unresolved:["Butt-end of keeper contacts spine with nominal 16x4mm area; unfastened part CANNOT retain an inverted box.",
      "2 mm gap requires compressible pad, captive screw and tested preload; geometric clearance alone has no anti-rattle force.",
      "K18 integral upper lips are not detachable and their DXFs cannot be machined for this architecture.",
      "8 reference top/bottom pockets open at the front MDF edge, and are not enclosed blind grooves.",
      "AABB static endpoint checks do not demonstrate through-cutout insertion, hand access or driver basket clearance.",
      "No real corner-tool-radius, structural strength, fatigue, adhesive or press-fit validation.",
      "Nominal volume accounting omits actual keeper screws, adhesive, seals, gasket and tested displacement."]
  };
  const scad=`// K20: RESEARCH assembly, 40 positional removable keeper envelopes without fasteners; CNC HOLD.\n// NOTE: the fixed-upper-tongue shapes of K18 are NOT valid production patterns for this K20 option.\ninclude <K15_p30e_zlozenie_parametryczne_NIE_CNC.scad>\nshow_K20_spines=true;\nshow_K20_lower=true;\nshow_K20_upper=true;\nK20_SPINES=[\n${spine.map(v=>` [${JSON.stringify(v.o)},${JSON.stringify(v.s)}]`).join(",\n")}\n];\nK20_LOWER=[\n${low.map(v=>` [${v.module_index},${JSON.stringify(v.o)},${JSON.stringify(v.s)}]`).join(",\n")}\n];\nK20_UPPER=[\n${keeper.map(v=>` [${v.module_index},${JSON.stringify(v.o)},${JSON.stringify(v.s)}]`).join(",\n")}\n];\nif(show_K20_spines) for(a=K20_SPINES) color([0.12,0.6,0.4,0.85]) translate(a[0])cube(a[1]);\nif(show_K20_lower) for(a=K20_LOWER)color([0.15,0.8,0.25,0.85])translate(a[1])cube(a[2]);\nif(show_K20_upper) for(a=K20_UPPER)if(panel_enabled(a[0]))color([0.98,0.4,0.17,0.9])translate(a[1])cube(a[2]);\necho("UPPER: Unattached face-contact research placeholders. NO fasteners, NO lock, NO proof of assembly, NOT CNC.");\n`;
  return {result,scad};
}
function main(){const root=path.resolve(__dirname,"..");const K15=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k15_p30e_przed_CNC_zestawienie.json"),"utf8"));const K17=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k17_prowadnice_boczne_wkladow.json"),"utf8"));const x=buildK20(K15,K17);const out={"wyniki/k20_rozbieralne_rygle_audyt.json":JSON.stringify(x.result,null,2)+"\n","dokumentacja/K20_p30e_rozbieralne_zabezpieczenia_NIE_CNC.scad":x.scad};for(const [file,content]of Object.entries(out)){const p=path.join(root,file);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,content);}console.log(JSON.stringify({status:x.result.status,volumes:x.result.conditional_volume_states}));}
if(require.main===module)main(); module.exports={buildK20};
