#!/usr/bin/env node
"use strict";
// K16: independent geometry screen; no completed fastening or CNC release.
const fs=require("node:fs"),path=require("node:path");
function buildK16(input){
  const mm={wall_front_y:44,wall_rear_y:403,mat_start_y:353,body_xyz:[1020,425,500]},mounts=[],groups={},massByIdx={},fail=[];
  const density=730,modelAcc=5,gravity=9.81,halfwidth=8,plateThick=8,seatInset=12,stripWidth=16;
  const zclass=z=>{const loc=z-22;return (Math.abs(loc-62)<.01||Math.abs(loc-282)<.01||Math.abs(loc-90)<.01)?"A":"B"};
  const overlap=(a,b)=>{
    return a.o.every((v,j)=>Math.min(v+a.s[j],b.o[j]+b.s[j])-Math.max(v,b.o[j])>1e-7);
  };
  const panelBoxes=input.parts.map(p=>({id:p.id,o:p.local_origin_global_xyz_mm,s:p.box_size_xyz_mm}));
  for(const m of input.module_positions){
    const [x,y,z]=m.global_origin_xyz_mm,[sx,sy,sz]=m.dims_xyz_mm;
    const nearFront=y-mm.wall_front_y,nearRear=mm.wall_rear_y-(y+sy);
    const side=nearFront<=nearRear?"front":"rear",gap=side==="front"?nearFront:nearRear;
    if(gap<0)throw Error("module crosses front/rear wall "+m.i);
    const y0=side==="front"?mm.wall_front_y:y+sy-seatInset;
    const y1=side==="front"?y+seatInset:mm.wall_rear_y;
    const phase=zclass(z+sz/2);
    const offsetXs=phase==="A"?[18,sx-18-stripWidth]:[50,sx-50-stripWidth];
    const outerVol=sx*sy*sz,innerVol=(sx-16)*(sy-16)*(sz-16);
    const mass=(outerVol-innerVol)/1e9*density;
    massByIdx[m.i]=mass;
    const force5g=mass*gravity*modelAcc;
    const fRail=force5g/2;
    const bendingStressMpa=6*fRail*gap/(stripWidth*plateThick*plateThick);
    for(const position of ["bottom","top"])for(const [pair,xOff]of offsetXs.entries()){
      const bz=position==="bottom"?z-plateThick:z+sz;
      const rail={
        id:`K16_SLOT_${String(m.i).padStart(2,"0")}_${position==="bottom"?"SHELF":"RETAINER"}_${pair+1}`,
        module_index:m.i,position,
        o:[x+xOff,y0,bz],s:[stripWidth,y1-y0,plateThick],
        bound_wall_y_mm:side==="front"?mm.wall_front_y:mm.wall_rear_y,
        bound_module_face_y_mm:side==="front"?y:y+sy,
        wall_face:side,unsupported_reach_mm:gap,seat_overlap_under_module_mm:seatInset,
        supports_z_contact_from_below_or_above:true,
        load_assumption:"two of four support elements carry 100% of hypothetical 5g inertial force in worst vertical orientation",
        module_mdf8_mass_kg:Number(mass.toFixed(5)),
        five_g_force_module_N:Number(force5g.toFixed(4)),
        test_force_per_loaded_rail_N:Number(fRail.toFixed(4)),
        cantilever_bending_stress_screen_MPa:Number(bendingStressMpa.toFixed(5)),
        adhesive_or_fastener_qualified:false,
        service_reachable:false,
        volume_displacement_mm3:stripWidth*(y1-y0)*plateThick
      };
      const obj={o:rail.o,s:rail.s};
      if(rail.o.some((c,j)=>c<0||c+rail.s[j]>mm.body_xyz[j]))throw Error("outer bounds");
      if(panelBoxes.some(x=>overlap(obj,x))){fail.push({type:"collision_with_MDF",rail:rail.id,parts:panelBoxes.filter(x=>overlap(obj,x)).map(x=>x.id)});}
      mounts.push(rail);
    }
    if(!groups[side])groups[side]=0;groups[side]++;
  }
  if(mounts.length!==80||groups.front!==8||groups.rear!==12)throw Error("wrong fixture count");
  const collisions=[];
  for(let i=0;i<mounts.length;i++)for(let j=i+1;j<mounts.length;j++)
  if(overlap({o:mounts[i].o,s:mounts[i].s},{o:mounts[j].o,s:mounts[j].s}))
     collisions.push([mounts[i].id,mounts[j].id]);
  if(fail.length||collisions.length)throw Error("fixture AABB intersections "+JSON.stringify({fail:fail.slice(0,3),collisions:collisions.slice(0,3)}));
  const matOverlaps=mounts.filter(x=>x.o[1]<mm.wall_rear_y && x.o[1]+x.s[1]>mm.mat_start_y).map(x=>{
    const length=Math.min(x.o[1]+x.s[1],mm.wall_rear_y)-Math.max(x.o[1],mm.mat_start_y);
    return{id:x.id,module_index:x.module_index,mat_overlap_y_mm:length,intersected_mat_envelope_mm3:x.s[0]*x.s[2]*length};
  });
  const mpass=(k,m)=>k.reduce((s,i)=>s+massByIdx[i],0);
  const state={100:input.module_positions.map(m=>m.i),120:Array.from({length:12},(_,i)=>i+4),150:[4]};
  const stats={study:"K16",date:"2026-11-04",status:"GEOMETRIC REFERENCE SUPPORT/RETAINER INTERFACES ONLY; NO FASTENER, BRACKET OR CNC VALIDATION",
    source:"K15 P30E module positions and conservative four-contact front/rear wall docking concept",
    support_count:mounts.length,modules_total:input.module_positions.length,supports_per_module:4,
    front_fixed_wall_slots:groups.front,rear_fixed_wall_slots:groups.rear,
    support_section_hypothesis_mm:{width:stripWidth,thickness:plateThick,overlap_under_module:seatInset},
    support_connectivity_model:"2 bottom shelves and 2 opposing anti-inversion top retainers per module, touching an inner MDF wall at y=44 or y=403; actual screws, brackets, sliding latches, mounting clips and strength NOT modelled",
    bracket_total_nominal_displacement_l:Number((mounts.reduce((a,v)=>a+v.volume_displacement_mm3,0)/1e6).toFixed(6)),
    mat_penetration_count:matOverlaps.length,mat_envelope_displaced_by_supports_l:Number((matOverlaps.reduce((a,v)=>a+v.intersected_mat_envelope_mm3,0)/1e6).toFixed(6)),
    min_wall_gap_mm:Math.min(...mounts.map(v=>v.unsupported_reach_mm)),
    max_wall_gap_mm:Math.max(...mounts.map(v=>v.unsupported_reach_mm)),
    material_screen_hypothesis:{module_shell_thickness_mm:8,module_density_kg_m3:730,gravity_m_s2:gravity,comparison_acceleration_g:modelAcc},
    module_mass_kg:{small:Number(massByIdx[0].toFixed(6)),large_rear:Number(massByIdx[4].toFixed(6)),large_front:Number(massByIdx[8].toFixed(6))},
    examples:{largest_rear_cantilever_MPa:Math.max(...mounts.filter(v=>v.wall_face==="rear").map(v=>v.cantilever_bending_stress_screen_MPa)),largest_front_cantilever_MPa:Math.max(...mounts.filter(v=>v.wall_face==="front").map(v=>v.cantilever_bending_stress_screen_MPa))},
    no_positive_AABB_intersections_with_138_k15_MDF_parts:true,no_positive_AABB_support_support_intersections:true,
    state_audits:Object.fromEntries(Object.entries(state).map(([k,ids])=>[k,{installed_modules:ids.length,module_shell_mass_kg:Number(mpass(ids).toFixed(5)),brackets_if_removable_with_module:Number((mounts.filter(v=>ids.includes(v.module_index)).reduce((s,v)=>s+v.volume_displacement_mm3,0)/1e6).toFixed(6)),fixed_brackets_if_all_remain_l:Number((mounts.reduce((s,v)=>s+v.volume_displacement_mm3,0)/1e6).toFixed(6))}])),
    critical_problems:[
      "K15 20 modules are unsupported; K16 introduces only 80 reference docking arms touching cabinet walls and module undersides/tops. Physical attachment not designed.",
      "48 rear braces would penetrate the 50 mm rear mat envelope; must redesign anchors or cut mat and redo acoustic/volume calculation.",
      "Two bottom supports may be stressed in cantilever bending; hypothesis 5 g is NOT an acceptance load, and nominal thickness 8mm is NOT certified.",
      "Four-point preload, clamping, pull-out, joint creep and vibrational fatigue of MDF, acoustic sealing and rattle-free removable locks not modelled.",
      "Routes and screwdriver/hand access with supports and physically removable sliders not verified; do not assume K02/K07 20-of-20 remains true.",
      "Supports left installed for 150L and those removed with modules require different volume and mass balances; both are only exploratory.",
      "Gravity orientation: need 180-degree inversion and transport cases; no module can be unrestrained even when inverted.",
      "Fasteners, service access and manufacturing drawing must be defined before CNC — hold all brackets and MDF panels."
    ],
    mount_envelopes:mounts,mat_overlap_details:matOverlaps};
  const rows=mounts.map(x=>[x.id,x.module_index,x.position,...x.o,...x.s,x.wall_face,x.unsupported_reach_mm,x.cantilever_bending_stress_screen_MPa]);
  const head="id,module_index,interface,x_mm,y_mm,z_mm,size_x_mm,size_y_mm,size_z_mm,anchor_wall,rear_or_front_gap_mm,hypothetical_5g_cantilever_stress_MPa\n";
  const csv=head+rows.map(r=>r.join(",")).join("\n")+"\n";
  const scad=`// K16 REFERENCE-ONLY placeholder support seats for K15 modules.\n// Includes K15 geometry; K16 adds two bottom seats plus two upper retainers for every occupied volume module.\n// No bolt, screw, glue or sliding latch designed. No CNC eligibility; do not copy into production drawings.\ninclude <K15_p30e_zlozenie_parametryczne_NIE_CNC.scad>\nSHOW_K16_DOCKING=true;\nK16_MOUNTS=[\n${mounts.map(m=>`  [${m.module_index},${JSON.stringify(m.o)},${JSON.stringify(m.s)},${JSON.stringify(m.position)},${JSON.stringify(m.wall_face)}]`).join(",\n")}\n];\nif(SHOW_K16_DOCKING)for(a=K16_MOUNTS)if(panel_enabled(a[0])){\n color(a[3]=="bottom"?[0.15,0.76,0.26,0.98]:[0.92,0.28,0.18,0.98])translate(a[1])cube(a[2]);\n}\necho("K16 4 docking envelope seats/retainers touch each module and one of two inner walls");\necho("WARNING: 48 rear mount elements INTERSECT 50mm back MAT; no MDF attachment, latches or service is qualified");\n`;
  return{stats,csv,scad};
}
function main(){const root=path.resolve(__dirname,".."),prev=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k15_p30e_przed_CNC_zestawienie.json"),"utf8")),o=buildK16(prev); const files={"wyniki/k16_model_podparcia_20_wkladow.json":JSON.stringify(o.stats,null,2)+"\n","wyniki/k16_80_stykow_modulow_REFERENCYJNE_NIE_CNC.csv":o.csv,"dokumentacja/K16_p30e_z_mocowaniami_modulow_NIE_CNC.scad":o.scad};for(const [file,content] of Object.entries(files)){fs.writeFileSync(path.join(root,file),content)}console.log(JSON.stringify({support_count:o.stats.support_count,mat_overlap_count:o.stats.mat_penetration_count,nominal_support_volume_l:o.stats.bracket_total_nominal_displacement_l,no_cnc:true}));}
if(require.main===module)main(); module.exports={buildK16,main};
