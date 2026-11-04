#!/usr/bin/env node
"use strict";
// K15 single source of truth: P30E provisional envelope, eleven brace AABBs and twenty 6-face MDF8 module assemblies.
// NEVER issue the generated dimensions as a CNC fabrication order; print/reference only.
const fs=require("node:fs"),path=require("node:path");
function generateK15(){
  const cfg={study:"K15",revision:"2026-11-04",body_mm:{W:1020,D:425,H:500},front_mm:44,wall_mm:22,module_wall_mm:8,cutout_factory_reference_d_mm:355.8,basket_factory_hole_d_mm:6.5,flange_hole_pcd_mm:368,driver_axis_xz_mm:[231,250],rear_mat_mm:50,pad_reference_mm:{inner_r:178.9,outer_r:205,tangential:36,depth:20},total_depth_scenario_max_mm:481,driver_displacement_hypothesis_l:5,hardware_displacement_hypothesis_l:0.175};
  const {W,D,H}=cfg.body_mm,F=cfg.front_mm,T=cfg.wall_mm,mt=cfg.module_wall_mm;
  const inner=[W-2*T,D-F-T,H-2*T];
  const parts=[],mods=[],braces=[];
  const rnd=v=>Number(v.toFixed(6));
  function add(id,type,thickness_mm,flatA_mm,flatB_mm,origin,size,module_index,notes,source_id){
    if(Math.abs(size[0]*size[1]*size[2]-flatA_mm*flatB_mm*thickness_mm)>0.00001)throw Error("invalid planar stock "+id);
    if(size.some(v=>v<=0)||origin.some(v=>v<-1e-9)||origin.some((v,j)=>v+size[j]>[W,D,H][j]+1e-9))throw Error("invalid cabinet bounds "+id);
    parts.push({id,type,material_candidate:thickness_mm===8?"MDF8_UNVERIFIED":"MDF22_UNVERIFIED",thickness_mm,blank_a_mm:flatA_mm,blank_b_mm:flatB_mm,local_origin_global_xyz_mm:origin.map(rnd),box_size_xyz_mm:size.map(rnd),module_index,notes,source_id,manufacturing_status:"REFERENCE_ONLY_NOT_CNC"});
  }
  function shell(id,origin,size,blankA,blankB,notes){
    add(id,id.startsWith("FR")?"front":"shell",T,blankA,blankB,origin,size,-1,notes,"P30E");
  }
  shell("FR1",[0,0,0],[W,T,H],W,H,"front laminate ply 1; reference cutout; no fastener drilling");
  shell("FR2",[0,T,0],[W,T,H],W,H,"front laminate ply 2; reference cutout; bond not specified");
  shell("BACK",[0,D-T,0],[W,T,H],W,H,"full width full height back; terminal opening not defined");
  shell("SIDE_L",[0,F,0],[T,D-F-T,H],D-F-T,H,"full height butt joint; joinery and adhesive not qualified");
  shell("SIDE_R",[W-T,F,0],[T,D-F-T,H],D-F-T,H,"full height butt joint; joinery and adhesive not qualified");
  shell("BOTTOM",[T,F,0],[W-2*T,D-F-T,T],W-2*T,D-F-T,"between sides");
  shell("TOP",[T,F,H-T],[W-2*T,D-F-T,T],W-2*T,D-F-T,"between sides");
  const braceBox=(id,origin,size)=>{
    // braces modeled as MDF22 plates with X direction equal to panel thickness
    add(id,"brace",T,size[1],size[2],origin,size,-1,"P30A/P30E AABB surrogate; no dado/mitre/joint dimensions","P30E/P30A");
    braces.push({id,origin,size});
  };
  for(const [which,xlocal] of [[1,426],[2,701]]){
    const x=T+xlocal;
    braceBox(`B${which}_LOW`,[x,F,T],[T,inner[1],T]);
    braceBox(`B${which}_UP`,[x,F,H-2*T],[T,inner[1],T]);
    braceBox(`B${which}_FRONT_WEB`,[x,F,2*T],[T,10,H-4*T]);
    braceBox(`B${which}_REAR_WEB`,[x,D-2*T,2*T],[T,T,H-4*T]);
  }
  const thirdX=T+198;
  braceBox("B3_LOW",[thirdX,F+220,T],[T,inner[1]-220,T]);
  braceBox("B3_UP",[thirdX,F+220,H-2*T],[T,inner[1]-220,T]);
  braceBox("B3_REAR_WEB",[thirdX,D-2*T,2*T],[T,T,H-4*T]);
  function moduleBox(i,center,dims){
    const origin=center.map((c,j)=>c-dims[j]/2+[T,F,T][j]);
    const [x,y,z]=origin,[a,b,c]=dims;
    const base=`M${String(i).padStart(2,"0")}`;
    const e=mt;
    const specs=[
      ["XL",[x,y,z],[e,b,c],b,c],
      ["XR",[x+a-e,y,z],[e,b,c],b,c],
      ["YF",[x+e,y,z],[a-2*e,e,c],a-2*e,c],
      ["YR",[x+e,y+b-e,z],[a-2*e,e,c],a-2*e,c],
      ["ZB",[x+e,y+e,z],[a-2*e,b-2*e,e],a-2*e,b-2*e],
      ["ZT",[x+e,y+e,z+c-e],[a-2*e,b-2*e,e],a-2*e,b-2*e]
    ];
    for(const [face,loc,size,da,db] of specs){
      add(`${base}_${face}`,"module_panel",e,da,db,loc,size,i,"6-face butt-joint concept; all latches, gaskets, and closure methods unqualified","P30E/P30A");
    }
    mods.push({i,global_center_xyz_mm:center.map((c,j)=>rnd(c+[T,F,T][j])),local_center_xyz_mm:center,dims_xyz_mm:dims,global_origin_xyz_mm:origin.map(rnd),candidate_state_inclusion:i<4?["100"]:(i===4?["100","120","150"]:(i<16?["100","120"]:["100"]))});
  }
  for(let i=0;i<20;i++){
    let center,dims;
    if(i<4){center=[i<2?99:323,253,i%2===0?90:366];dims=[180,100,100];}
    else{
      const k=i-4,bank=Math.floor(k/8),group=Math.floor((k%8)/4);
      center=[bank===0?849.5:574.5,group===0?243:83,[62,392,172,282][k%4]];
      dims=[210,group===0?120:150,100];
    }
    moduleBox(i,center,dims);
  }
  if(parts.length!==138||braces.length!==11||mods.length!==20||parts.filter(x=>x.type==="front").length!==2)throw Error("part count");
  const contact=(a,b)=>{
    const o1=a.local_origin_global_xyz_mm,o2=b.local_origin_global_xyz_mm,s1=a.box_size_xyz_mm,s2=b.box_size_xyz_mm;
    return o1.every((v,j)=>Math.min(v+s1[j],o2[j]+s2[j])-Math.max(v,o2[j])>1e-7);
  };
  const collisions=[];
  for(let i=0;i<parts.length;i++)for(let j=i+1;j<parts.length;j++)if(contact(parts[i],parts[j]))collisions.push([parts[i].id,parts[j].id]);
  if(collisions.length)throw Error("Solid AABB clashes: "+JSON.stringify(collisions.slice(0,8)));
  const quantities={structural_shell:7,braces:11,modular_box_panels:120,all_reference_blanks:138,modules:20};
  const getVol=arr=>arr.reduce((acc,p)=>acc+p.box_size_xyz_mm.reduce((a,b)=>a*b,1),0)/1e6;
  const panelGross=getVol(parts.filter(x=>x.type!=="module_panel")),frontBoreL=Math.PI*(cfg.cutout_factory_reference_d_mm/2)**2*F/1e6;
  const shellL=getVol(parts.filter(x=>x.type==="front"||x.type==="shell"))-frontBoreL;
  const brL=getVol(parts.filter(x=>x.type==="brace"));
  const modShellL=getVol(parts.filter(x=>x.type==="module_panel"));
  if(Math.abs(shellL-52.6001338564)>1e-8||Math.abs(brL-1.60908)>1e-8)throw Error("P30E/K10 volume mismatch: "+shellL+" "+brL);
  const small=mods.filter(m=>m.dims_xyz_mm[0]===180).length,rear=mods.filter(m=>m.dims_xyz_mm[1]===120).length,forward=mods.filter(m=>m.dims_xyz_mm[1]===150).length;
  if(JSON.stringify([small,rear,forward])!==JSON.stringify([4,8,8]))throw Error("wrong P30E module grouping");
  const areaByThickness={};
  for(const p of parts)areaByThickness[p.thickness_mm]=rnd((areaByThickness[p.thickness_mm]||0)+(p.blank_a_mm*p.blank_b_mm)/1e6);
  // Derive empty net L from precisely P30A/P30E rigid displacement assumptions.
  const fillBox={o:[T,D-T-cfg.rear_mat_mm,T],s:[inner[0],cfg.rear_mat_mm,inner[2]]};
  let matEnv=fillBox.s[0]*fillBox.s[1]*fillBox.s[2];
  for(const p of parts.filter(x=>x.type==="brace")){
    const b=fillBox;
    matEnv-=p.local_origin_global_xyz_mm.reduce((acc,v,j)=>
      acc*Math.max(0,Math.min(v+p.box_size_xyz_mm[j],b.o[j]+b.s[j])-Math.max(v,b.o[j])),1);
  }
  const solidMatHypL=matEnv/1e6*20/1380;
  const volumePerModuleL=mods.map(m=>m.dims_xyz_mm.reduce((a,b)=>a*b,1)/1e6);
  const padDisplacementL=8*(205-178.9)*36*20/1e6;
  const netEmpty=inner.reduce((a,b)=>a*b,1)/1e6-brL-cfg.driver_displacement_hypothesis_l-cfg.hardware_displacement_hypothesis_l-solidMatHypL;
  const selected={100:[...Array(20).keys()],120:[...Array(12).keys()].map(i=>i+4),150:[4]};
  const netNominal={},netIf8Pads={};
  for(const k of [100,120,150]){netNominal[k]=rnd(netEmpty-selected[k].reduce((sum,i)=>sum+volumePerModuleL[i],0));netIf8Pads[k]=rnd(netNominal[k]-padDisplacementL);}
  if(!(Math.abs(netNominal[100]-100.12)<.05&&Math.abs(netNominal[120]-119.92)<.05&&Math.abs(netNominal[150]-150.16)<.05))throw Error("volume mismatch with P30E "+JSON.stringify(netNominal));
  const zvol=(p)=>p.box_size_xyz_mm.reduce((a,b)=>a*b,1);
  const density=730;
  const allMdfMass=(panelGross-frontBoreL+modShellL)*density/1000;
  const assembly={study:"K15",date:cfg.revision,status:"NOMINAL PARAMETRIC 3D RESEARCH MODEL + CUTLIST; NOT A FABRICATION RELEASE — CNC HOLD",
    source_links:["raporty/078_P30E_mata50_montaz_robustnosc.md","skrypty/p30a_robust_geometry.py","skrypty/p30e_mat50_geometria_montaz.py","skrypty/k10_audyt_materialow_obudowy.py","raporty/K14_docisk_tolerancje_plytki_M5_w_klocku20.md"],
    cfg,inside_mm:inner,quantities,nominal_panel_area_m2_by_material_thickness:areaByThickness,
    nominal_cavity_enclosure_shell_l:rnd(shellL),nominal_11_braces_l:rnd(brL),reference_mdf7plus11_mass_kg_at_730:rnd((panelGross-frontBoreL)*density/1000),
    nominal_module_shell_mdf8_l:rnd(modShellL),total_MDF_mass_all_20_modules_kg_ignoring_hardware:rnd(allMdfMass),
    modelled_mat_solid_hypothesis_l:rnd(solidMatHypL),reference_module_count_by_size:{small,rear,front:forward},
    reference_net_l_P30E_no_new_pads:netNominal,
    exploratory_net_l_if_K01_8pads_NOT_previously_counted:netIf8Pads,
    pad_displacement_l_only_if_new_and_full_eight_present:rnd(padDisplacementL),
    reference_visible_driver_basket_metal_hole_d_mm:6.5,
    front_MDF_mounting_holes_have_NOT_been_defined:true,
    example_M5_MDF_through_hole_mm_ONLY_NONAPPROVED:5.5,
    reference_front_large_cutout_d_mm_NOT_MACHINE_PROGRAM:355.8,
    solid_AABB_clashes_in_provisional_nominal_box_elements:collisions,
    module_positions:mods,
    parts,critical_missing_before_CNC:[
      "Real driver basket/hole templates, cutout clearance tolerance, phase and terminals",
      "M5 Ø5.5 is only a scenario, neither Ø6.5 basket nor an approval for MDF drilling",
      "Qualified driver mounting force-path after K14, gasket size, screw choice, accessible service",
      "Front bonding 2×MDF22, joinery rabbets/dados/adhesive choice and test coupon",
      "Brace termination and fasteners: 10-mm thin front strips vulnerable to machining damage",
      "Module 6-face butt-joint closure, handling, latch, test pressure and retention at every orientation",
      "Recheck all 20 module insertion/exit paths with latches, screwdrivers, handles, wiring and real driver basket",
      "Actual material stock and tolerances, cutter diameter, kerf, nesting, grain and machining allowances",
      "Sealed terminal cutout, plate amp mounting, wiring, grille and full 500mm external allowance",
      "Geometric tolerances, non-overlap and clash test using true 3D meshes; no actual fastener collision",
      "Material calibrated strength, adhesive, fatigue and acoustic re-verification for all states",
      "Before fab release require reviewed 2D DXF/STEP and CNC quotation plus production approval"
    ]};
  const csvHead=["id","type","material_candidate","thickness_mm","blank_a_mm","blank_b_mm","x_global_mm","y_global_mm","z_global_mm","size_x_mm","size_y_mm","size_z_mm","module_index","manufacturing_status","remarks"];
  function csvQ(v){const s=String(v??"");return /[,"\n]/.test(s)?`"${s.replace(/"/g,'""')}"`:s;}
  const csv=[csvHead.join(","),...parts.map(p=>[p.id,p.type,p.material_candidate,p.thickness_mm,p.blank_a_mm,p.blank_b_mm,...p.local_origin_global_xyz_mm,...p.box_size_xyz_mm,p.module_index,p.manufacturing_status,p.notes].map(csvQ).join(","))].join("\n")+"\n";
  const scadParts=parts.map(p=>`  [${JSON.stringify(p.id)},${JSON.stringify(p.local_origin_global_xyz_mm)},${JSON.stringify(p.box_size_xyz_mm)},${JSON.stringify(p.type)},${p.module_index}]`).join(",\n");
  const scad=`// AUTOGENERATED from skrypty/k15_pre_cnc_model.js; edit source, not this export.\n// K15 — 1020×425×500 MDF prototype assembly as RESEARCH GEOMETRY, NOT CNC.\n// IMPORTANT: 8×Ø6.5mm exists IN METAL BASKET ONLY. FRONT MDF screw holes NOT MODELLED.\n// Center reference PCD=368, front large cutout Ø355.8 nominal from manufacturer.\n// Coordinate: x left-to-right; y outside front to rear; z floor-to-ceiling; all mm.\n$fn=120;\nstate_liters=100; // [100,120,150]\nshow_shell=true;\nshow_braces=true;\nshow_modular_boxes=true;\nshow_unqualified_pad_envelopes=true;\nshow_factory_basket_reference=true;\nshow_module_labels=false;\nassert(state_liters==100||state_liters==120||state_liters==150);\nCUTOUT_D=355.8;CX=231;CZ=250;\n// Unqualified K01 pad box: not a designed mounting interface.\nPAD_IN_R=178.9;PAD_OUT_R=205;PAD_WIDTH=36;PAD_DEPTH=20;\nPARTS=[\n${scadParts}\n];\nfunction panel_enabled(idx) = idx<0 || state_liters==100 || (state_liters==120 && idx>=4 && idx<16) || (state_liters==150 && idx==4);\nmodule box_solid(p){translate(p[1])cube(p[2]);}\nmodule panel(p){\n if(p[3]==\"front\") color([0.77,0.56,0.34,0.75]) difference(){box_solid(p);translate([CX,21,CZ])rotate([90,0,0])cylinder(d=CUTOUT_D,h=48,center=true);}\n else if(p[3]==\"shell\")color([0.71,0.62,0.47,0.68])box_solid(p);\n else if(p[3]==\"brace\")color([0.13,0.53,0.69,0.9])box_solid(p);\n else if(p[3]==\"module_panel\")color([0.85,0.60,0.26,0.6])box_solid(p);\n}\nfor(p=PARTS){\n if((p[3]==\"shell\"||p[3]==\"front\") && show_shell)panel(p);\n if(p[3]==\"brace\"&&show_braces)panel(p);\n if(p[3]==\"module_panel\"&&show_modular_boxes&&panel_enabled(p[4]))panel(p);\n}\nif(show_unqualified_pad_envelopes)\n for(i=[0:7]) color([0.95,0.20,0.22,0.38])\n translate([CX,44,CZ])rotate([0,-i*45,0])translate([PAD_IN_R,0,-PAD_WIDTH/2])\n cube([PAD_OUT_R-PAD_IN_R,PAD_DEPTH,PAD_WIDTH]);\nif(show_factory_basket_reference){\n // Only visualization of factory basket flange footprint: NOT a true basket 3D CAD.\n color([0.2,0.3,0.6,0.15])difference(){\n translate([CX,-8,CZ])rotate([90,0,0])cylinder(d=388.4,h=10.5,center=true);\n translate([CX,-8,CZ])rotate([90,0,0])cylinder(d=355.8,h=11.5,center=true);\n }\n // 8 markers belong to Dayton METAL BASKET ONLY; NEVER subtract from wood.\n for(i=[0:7])color([0.9,0.1,0.1,1])\n translate([CX+184*cos(45*i),-15,CZ+184*sin(45*i)])sphere(d=4);\n}\necho(\"K15 research assembly ONLY. Not all parts are machinable; no cut/drill order permitted.\");\necho(\"Basket factory holes Ø6.5 are marker positions only; no MDF mounting holes defined.\");\necho(\"Unqualified K13/K14 pads red; need redesigned load path and service geometry.\");\n`;
  return {assembly,csv,scad};
}
function main(){const out=generateK15();const root=path.resolve(__dirname,"..");const files={
 "wyniki/k15_p30e_przed_CNC_zestawienie.json":JSON.stringify(out.assembly,null,2)+"\n",
 "wyniki/k15_p30e_przed_CNC_138_elementow.csv":out.csv,
 "dokumentacja/K15_p30e_zlozenie_parametryczne_NIE_CNC.scad":out.scad
};for(const [f,s]of Object.entries(files)){const p=path.join(root,f);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,s);}console.log(JSON.stringify({study:"K15",parts:out.assembly.quantities,volumes:out.assembly.reference_net_l_P30E_no_new_pads,reference_all_modules_mdf_kg:out.assembly.total_MDF_mass_all_20_modules_kg_ignoring_hardware,status:out.assembly.status}));}
if(require.main===module)main();module.exports={generateK15,main};
