#!/usr/bin/env node
"use strict";
// K25 source-data-driven splice keep-out and normal tool-access screening. NO bolt holes, NO CNC.
const fs=require("node:fs"),path=require("node:path");
function buildK25(K15,K17,K24) {
 const assert=(x,msg)=>{if(!x)throw Error(msg)};
 const candidateIds=["G17_COLUMN_02","G17_COLUMN_10"];
 const allRail=K17.spines;
 assert(K15.parts.length===138&&K15.module_positions.length===20&&allRail.length===12,"K15/K17 drift");
 assert(K24.releasePhase100to120.missing_spines?.includes(candidateIds[0])&&K24.releasePhase120to150.missing_spines?.includes(candidateIds[1]),"K24 data mismatch");
 const pocket=K15.parts.filter(x=>x.module_index===-1&&!["FR1","FR2"].includes(x.id)).map(x=>({id:x.id,o:x.local_origin_global_xyz_mm,s:x.box_size_xyz_mm,kind:"cabinet"}));
 const modules=K15.module_positions.map(x=>({id:"MODULE_"+x.i,o:x.global_origin_xyz_mm,s:x.dims_xyz_mm,kind:"insert"}));
 const rails=allRail.map(x=>({id:x.id,o:x.o,s:x.s,kind:"rail"}));
 const lips=K17.contact_lips.map(x=>({id:x.id,o:x.o,s:x.s,kind:"existing K17 lip",group:x.group}));
 const mat={id:"MAT_50",o:[22,353,22],s:[976,50,456],kind:"mat"};
 const solids=[...pocket,...modules,...rails,...lips,mat];
 const overlap=(a,b)=>a.o.every((v,i)=>Math.min(v+a.s[i],b.o[i]+b.s[i])-Math.max(v,b.o[i])>1e-7);
 const round=v=>Math.round(v*1e6)/1e6;
 const R=K15.cfg.cutout_factory_reference_d_mm/2;
 const assumed={
   front_aperture_radius_mm:R,
   baseline_rail_width_x_mm:16,
   hypothetical_joint_plate_face_height_mm:50,
   hypothetical_plate_half_height_mm:25,
   hypothetical_minimum_clear_Z_to_original_lip_mm:8,
   hypothetical_front_or_back_plate_y_thickness_mm:2,
   hypothetical_module_tool_envelope_diameter_mm:12,
   hypothetical_tool_margin_each_side_mm:1,
   needed_tool_envelope_width_mm:14,
   hypothetical_segment_entrance_margin_xz_each_side_mm:6,
   scan_grid_z_step_mm:1,
   disclaimer:"None of these are material supplier specifications, fastener dimensions, rated loads, approved machining tolerances or fabrication instructions."
 };
 const selected={};
 const getLips=rail=>K17.contact_lips.filter(x=>x.group===rail.group && Math.abs(x.o[0]-rail.o[0])<1e-7).map(x=>({id:x.id,position:x.position,from:x.o[2],to:x.o[2]+x.s[2]})).sort((a,b)=>a.from-b.from);
 for(const [id,chosen]of [[candidateIds[0],250],[candidateIds[1],194]]) {
  const rail=allRail.find(x=>x.id===id);assert(rail,"Missing "+id);
  const ends=[rail.o[2],rail.o[2]+rail.s[2]],lipList=getLips(rail),eligible=[];
  for(let z=ends[0]+1;z<ends[1];z++){
   const segmentLen=[z-ends[0],ends[1]-z];
   const rho=segmentLen.map(len=>Math.hypot(rail.s[0]/2+6,len/2+6));
   const aperture=rho.every(x=>x<R);
   const zone=[z-25,z+25];
   const minDist=Math.min(...lipList.map(x=>zone[1]<=x.from?x.from-zone[1]:zone[0]>=x.to?zone[0]-x.to:-Math.min(zone[1]-x.from,x.to-zone[0])));
   if(aperture&&minDist>=8)eligible.push(z);
  }
  const groups=[];
  for(const z of eligible) {
   const last=groups.at(-1);
   if(last&&last.to+1===z)last.to=z;
   else groups.push({from:z,to:z,count:1});
   if(last&&last.to===z)last.count++;
  }
  assert(eligible.includes(chosen),"Selected split is not permitted in reference geometry "+id);
  const len=[chosen-ends[0],ends[1]-chosen];
  const plate=[
   {id:id+"_PLATE_FRONT_2MM_HOLD",o:[rail.o[0],rail.o[1]-2,chosen-25],s:[rail.s[0],2,50],orientation:"toward smaller Y"},
   {id:id+"_PLATE_REAR_2MM_HOLD",o:[rail.o[0],rail.o[1]+rail.s[1],chosen-25],s:[rail.s[0],2,50],orientation:"toward larger Y"}
  ];
  const byPlate=plate.map(p=>{
   const own=solids.filter(s=>s.id!==id&&overlap(p,s)).map(x=>({id:x.id,kind:x.kind}));
   const related=modules.filter(m=>m.o[0]<p.o[0]+p.s[0]&&m.o[0]+m.s[0]>p.o[0]&&m.o[2]<p.o[2]+p.s[2]&&m.o[2]+m.s[2]>p.o[2]);
   const limits=related.map(m=>({
     module_id:m.id,
     Ygap_mm:(m.o[1]+m.s[1]<=p.o[1])?round(p.o[1]-(m.o[1]+m.s[1])):(p.o[1]+p.s[1]<=m.o[1]?round(m.o[1]-(p.o[1]+p.s[1])):null)
   }));
   const nearest=limits.length?Math.min(...limits.map(x=>x.Ygap_mm??0)):null;
   const straightToolEnvelope14mm=nearest===null?null:nearest>=14;
   return {plate:p,static_unintentional_solid_overlaps:own,nearby_modules_in_XZ:limits,
    available_front_back_normal_Y_gap_mm:nearest,
    hypothetical_14mm_tool_fits_that_local_gap:straightToolEnvelope14mm};
  });
  const front=plate[0],cx=front.o[0]+front.s[0]/2,cz=chosen,toolHalf=7;
  const projectedD=Math.hypot(cx-K15.cfg.driver_axis_xz_mm[0],cz-K15.cfg.driver_axis_xz_mm[1])+toolHalf;
  const directTool={tool_centre_xz_mm:[cx,cz],tool_envelope_radius_mm:toolHalf,
    straight_tool_projection_outer_radius_from_basket_center_mm:round(projectedD),
    passes_nominal_D355_8mm_cutout_projection:projectedD<R,
    cylinder_swept_y_from_front_inner_face_to_front_plate_mm:[44,front.o[1]],
    test_prism:{o:[cx-toolHalf,44,cz-toolHalf],s:[14,Math.max(0,front.o[1]-44),14]}};
  directTool.model_solid_collisions=solids.filter(s=>s.id!==id&&overlap(directTool.test_prism,s)).map(s=>({id:s.id,kind:s.kind}));
  directTool.straight_front_normal_access_geometrically_clear_in_reference_model=directTool.passes_nominal_D355_8mm_cutout_projection&&directTool.model_solid_collisions.length===0;
  selected[id]={
   rail:{id,group:rail.group,box_module_indices:rail.module_indices,o:rail.o,s:rail.s},
   original_lip_spans_z_mm:lipList,
   split_scan:{qualifying_integer_mm_intervals:groups,qualifying_integer_mm_count:eligible.length,
     filters:"Each segmented rail upright XZ projection fits the nominal front opening with hypothetical 6mm margin; 50mm splice zone clears all original lips by >=8mm in Z; no real material tolerance."},
   chosen_research_split_global_z_mm:chosen,segment_reference_lengths_mm:len,
   chosen_max_segment_rectangle_corner_radius_in_cutout_projection_mm:round(Math.max(...len.map(L=>Math.hypot(rail.s[0]/2+6,L/2+6)))),
   chosen_splice_zone_global_z_mm:[chosen-25,chosen+25],
   hypothetical_2mm_face_plates:byPlate,
   straight_tool_14mm_front_axial_Y_screen:directTool,
   structural_reality:{plate_is_only_a_contact_footprint_with_no_holes:true,bolt_count:0,
      retention_qualified:false,plate_root_or_screw_approved:false,
      true_two_part_splice_3D_install_route_proven:false,
      functional_load_when_one_rail_removed_unqualified:true}
  };
 }
 assert(selected[candidateIds[0]].straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model,"Guide02 not front-accessible at chosen split");
 assert(!selected[candidateIds[1]].straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model,"Guide10 unexpectedly accessible");
 for(const [id,v]of Object.entries(selected))if(v.hypothetical_2mm_face_plates.some(p=>p.static_unintentional_solid_overlaps.length!==0))throw Error("Plate overlap "+id);
 assert(selected[candidateIds[1]].hypothetical_2mm_face_plates[0].available_front_back_normal_Y_gap_mm===4&&selected[candidateIds[1]].hypothetical_2mm_face_plates[1].available_front_back_normal_Y_gap_mm===5,"Guide10 near-box gap mismatch");
 const load=K24.supportRiskScreen.structural_demand_if_one_side_support_removed.map(x=>{
  const part=A.parts.filter(v=>v.module_index===x.id);
  const mass=part.reduce((s,p)=>s+p.box_size_xyz_mm.reduce((t,z)=>t*z,1),0)*730/1e9;
  const F=(mass+.2)*5*9.81;
  return {rail:x.rail,example_module:x.id,assumed_shell_mass_kg:round(mass),hypothetical_extra_hardware_kg:0.2,
   assumed_inertial_load_5g_on_one_surviving_side_N:round(F),
   corrected_guide_tip_span_mm:x.L,
   idealized_single_side_4mm_root_MPa:round(6*F*x.L/(16*4*4)),
   idealized_single_side_3_5mm_root_MPa:round(6*F*x.L/(16*3.5*3.5)),
   material_allowable_MPa:null,safety_factor:null,real_bearing_and_joint_not_modelled:true};
 });
 const result={study:"K25",date:"2026-11-04",
  status:"CNC HOLD — reference split windows / tool access and structural load demand, no real joinery approved",
  source:"Actual K15 MDF solids, K17 rail and lip spans, K24 service phase orders and risk conditions",
  hypotheses:assumed,
  selected_guide_studies:selected,
  one_remaining_support_5g_hypothetical_demand_with_0_2kg_allowance:load,
  key_findings:[
   "Guide02 split at Z250 has a 50mm nominal plate zone that is clear of all original lips; its front-facing hypothetical 14mm tool envelope is aligned with nominal Ø355.8 driver opening and intersects no other modeled permanent solid or box.",
   "Guide10 split at Z250 hits lip Z250–254 and is disallowed. Alternative Z194 is in a valid lip-free 50mm band and its segments fit the opening in XZ projection, but local plate-to-front/rear large boxes gaps are only 4mm / 5mm.",
   "The guide10 tool centre X669.5 is far outside the driver opening centred X231, so a straight front-to-rear (Y-axis) tool path through the driver aperture cannot reach it. A kinematic 6DOF tool route, remote control or alternate access panel remains untested.",
   "These proposed 2mm plate cuboids are solid-volume KEEP-OUT ENVELOPES only: no bolt threads, shear slip bearing, preload, fatigue, screw pullout, MDF edge distance, anchoring or physical assembly path qualified.",
   "5g single-side demand with hypothetical extra 0.2kg raises local 4mm ideal stress indicators; no strength allowables, coupon test or safety factor available.",
   "K24 state-switching passes at zero clearance with all lips/locks removed, but fails to complete at 1mm sensitivity; real CNC must not be ordered from K18 DXF."
  ],
  release_gates:{guide02_full_contact_joint_approved:false,guide10_full_contact_joint_approved:false,
   guide10_straight_Y_tool_from_front_accessible:false,release_during_box_supported:false,
   full_6dof_insert_guide_and_tool_path_approved:false,
   scaled_cutter_fillet_and_stock_tolerances_measured:false,cnc_release:false}
 };
 return result;
}
function main(){
 const root=path.resolve(__dirname,"..");
 const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
 const model=buildK25(read("wyniki/k15_p30e_przed_CNC_zestawienie.json"),
    read("wyniki/k17_prowadnice_boczne_wkladow.json"),read("wyniki/k24_drogi_serwisowe_i_podpory.json"));
 const out=path.join(root,"wyniki/k25_zlacza_prowadnic_i_dostep.json");
 fs.mkdirSync(path.dirname(out),{recursive:true});
 fs.writeFileSync(out,JSON.stringify(model,null,2)+"\n","utf8");
 console.log(JSON.stringify({CNC_HOLD:true,splits:Object.fromEntries(Object.entries(model.selected_guide_studies).map(([k,v])=>[k,v.chosen_research_split_global_z_mm])),toolAccess02:model.selected_guide_studies.G17_COLUMN_02.straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model,toolAccess10:model.selected_guide_studies.G17_COLUMN_10.straight_tool_14mm_front_axial_Y_screen.straight_front_normal_access_geometrically_clear_in_reference_model}));
}
if(require.main===module)main();
module.exports={buildK25};
