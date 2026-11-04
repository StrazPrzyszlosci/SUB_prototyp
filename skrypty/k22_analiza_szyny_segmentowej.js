#!/usr/bin/env node
"use strict";
// K22 corridor and divided-spine necessary conditions only; no 3D route or CNC release.
const fs=require("fs"),path=require("path");
function buildK22(k15,k17,k21){
 const rails=k17.spines.filter(x=>x.row!=="front").sort((a,b)=>a.o[0]-b.o[0]);
 const selected=k17.spines.find(x=>x.id==="G17_COLUMN_10");
 if(!selected||selected.row!=="rear_large"||selected.o[0]!==661.5||selected.s[0]!==16||selected.s[1]!==12||selected.o[2]!==22||selected.s[2]!==456)throw Error("K17 selected spine changed");
 const after=rails.filter(x=>x.id!==selected.id);
 const widthX=k15.cfg.body_mm.W-2*k15.cfg.wall_mm;
 if(widthX!==976)throw Error("Unexpected cabinet");
 const spans=[];let left=k15.cfg.wall_mm,prev="cabinet";
 for(const r of after){
   const gap=r.o[0]-left;
   if(gap<0)throw Error("rails overlap");
   spans.push({x0:left,x1:r.o[0],gap_mm:gap,left_boundary:prev,right_boundary:r.id});
   prev=r.id;left=r.o[0]+r.s[0];
 }
 spans.push({x0:left,x1:k15.cfg.body_mm.W-k15.cfg.wall_mm,gap_mm:k15.cfg.body_mm.W-k15.cfg.wall_mm-left,left_boundary:prev,right_boundary:"cabinet"});
 const largest=spans.reduce((a,b)=>b.gap_mm>a.gap_mm?b:a,spans[0]);
 if(Math.abs(largest.gap_mm-259)>1e-7||largest.x0!==531.5||largest.x1!==790.5)throw Error("Chosen service corridor changed");
 const inserts=[];
 for(const module of k15.module_positions.filter(x=>x.global_origin_xyz_mm[1]>=227)){
   const w=module.dims_xyz_mm[0],nominalClearance=6,adjusted=w+2*nominalClearance;
   const xLeftMin=largest.x0+nominalClearance, xLeftMax=largest.x1-nominalClearance-w;
   if(xLeftMax<=xLeftMin)throw Error("No basic corridor for module "+module.i);
   inserts.push({module_index:module.i,module_width_x_mm:w,module_depth_y_mm:module.dims_xyz_mm[1],
    nominal_x_clearance_on_each_side_mm:nominalClearance,
    free_x0_for_module_min_mm:xLeftMin,free_x0_for_module_max_mm:xLeftMax,
    available_x_travel_window_width_mm:+(xLeftMax-xLeftMin).toFixed(6),
    corridor_cross_section_condition_passes:true,
    full_3d_swept_path_proven:false});
 }
 if(inserts.length!==12||!inserts.every(x=>x.corridor_cross_section_condition_passes))throw Error("Unexpected modules");
 // Compare axis-aligned centered 2-piece rail front aperture only; does NOT establish transit to location.
 const rad=k15.cfg.cutout_factory_reference_d_mm/2;
 const hypotheticEdgeMargin=6;
 const railWidth=selected.s[0],full=selected.s[2],lengthEach=full/2;
 const fullProjectedRad=Math.hypot(railWidth/2+hypotheticEdgeMargin,full/2+hypotheticEdgeMargin);
 const segmentProjectedRad=Math.hypot(railWidth/2+hypotheticEdgeMargin,lengthEach/2+hypotheticEdgeMargin);
 const fullFits=fullProjectedRad<=rad,segmentFits=segmentProjectedRad<=rad;
 if(fullFits||!segmentFits)throw Error("Aperture comparison changed");
 const split={pieces:2,nominal_segment_lengths_z_mm:[lengthEach,lengthEach],
  split_global_z_mm:selected.o[2]+lengthEach,full_spine_z_length_mm:full,
  aperture_radius_mm:rad,assumed_clearance_in_projection_mm:hypotheticEdgeMargin,
  full_spine_rectangle_projected_radius_mm:+fullProjectedRad.toFixed(6),full_spine_fits_direct_upright_presentation:false,
  each_segment_rectangle_projected_radius_mm:+segmentProjectedRad.toFixed(6),each_segment_can_cross_front_opening_upright_if_centered:true,
  joining_faces_at_split_have_zero_overlap_and_no_fasteners:true,splice_detail_verified:false,
  bearing_transfer_across_split:false};
 const supportedModules=selected.module_indices;
 const boxPlanes=k15.module_positions.filter(x=>supportedModules.includes(x.i)).map(x=>({id:x.i,z0:x.global_origin_xyz_mm[2],z1:x.global_origin_xyz_mm[2]+x.dims_xyz_mm[2]}));
 const zJoint=split.split_global_z_mm;
 const lipAtJoint=k17.contact_lips.filter(t=>t.group===selected.group&&t.o[0]===selected.o[0]&&t.o[2]<=zJoint&&t.o[2]+t.s[2]>=zJoint)
 .map(t=>({id:t.id,z0:t.o[2],z1:t.o[2]+t.s[2]}));
 const state={study:"K22",date:"2026-11-04",status:"CNC HOLD — sectional rail corridor proposal, not physically connected or assembly-verified",
  previous_proof:"K21: all twelve rear K15 modules cannot traverse existing 130mm K17 rear rail wall with unrotated translation",
  temporary_removed_rail:selected.id,affected_modules_losing_one_of_two_supports:supportedModules,
  available_corridor_after_remove:{x0:largest.x0,x1:largest.x1,opening_width_mm:largest.gap_mm,
    original_largest_passage_mm:k21.max_open_gap_x_mm,selected_clearance_each_side_mm:6,
    axis_aligned_rear_insert_projection_screens:inserts,
    continuous_y_and_full_route_verified:false},
  two_part_spine_entry_screen:split,spine_target_module_planes:boxPlanes,
  existing_lips_touched_by_split_plane:lipAtJoint,
  missing_required_connection_design:["positive rail-to-rail structural splice with bending, buckling, joint torsion, impact and fatigue proof",
    "resolvable temporary support of four affected rear modules until rail is reconnected",
    "actual screws/fasteners and tool approach inside finished cavity, with min radii and gluing",
    "individual 3D path from Ø355.8 opening for both rail pieces AND twelve boxes in a valid temporal order",
    "full 3D rigidity, 50mm mat and true Dayton frame clearance, cabinet support, 100/120/150l air union",
    "actual material batch and tolerance test coupons; no CNC instructions"],
  status_of_existing_rail_DXF:"K18 only includes integral upper lips and monolithic rails: invalid for segmented proposal. Do not machine."};
 const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="930" height="380" viewBox="0 0 930 380"><rect width="930" height="380" fill="#f7fafb"/><text x="20" y="30" font-size="20" fill="#253849" font-weight="bold">K22 – removable service corridor (CONCEPT, NOT CNC)</text><text x="20" y="53" font-size="13" fill="#54677a">View along front-to-rear direction, X cross-section. Green corridor opens only with R10 removed.</text>
<rect x="40" y="100" width="851" height="110" fill="#edf2f5" stroke="#5e7282"/>${after.map(r=>`<rect x="${(40+(r.o[0]-22)*.872).toFixed(1)}" y="100" width="${(r.s[0]*.872).toFixed(1)}" height="110" fill="#ba5148"/>`).join("\n")}
<rect x="${(40+(largest.x0-22)*.872).toFixed(1)}" y="112" width="${(largest.gap_mm*.872).toFixed(1)}" height="86" fill="#9bd8bd" fill-opacity=".75"/>
<text x="${(40+((largest.x0+largest.x1)/2-22)*.872).toFixed(1)}" y="145" text-anchor="middle" font-size="16" font-weight="bold">259 mm</text>
<text x="${(40+((largest.x0+largest.x1)/2-22)*.872).toFixed(1)}" y="165" text-anchor="middle" font-size="12">210 + 2 × 6 = 222</text>
<text x="20" y="250" font-size="14" font-weight="bold" fill="#304c5d">Condition met only in a single X-projection at the rear-rail barrier.</text>
<text x="20" y="278" font-size="13">One candidate 456 mm rail becomes 2 × 228 mm research segments.</text>
<text x="20" y="305" font-size="13">Physical splice, tool access, support while open, full path and volume: NOT verified.</text>
<text x="20" y="339" font-size="16" font-weight="bold" fill="#ac3e35">No new production DXF. CNC HOLD.</text></svg>\n`;
 return {state,svg};
}
function main(){const root=path.resolve(__dirname,"..");const a=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k15_p30e_przed_CNC_zestawienie.json"),"utf8"));const b=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k17_prowadnice_boczne_wkladow.json"),"utf8"));const c=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k21_przesmyk_montazowy.json"),"utf8"));const o=buildK22(a,b,c);for(const [filename,s] of [["wyniki/k22_dzielona_szyna_przesmyk.json",JSON.stringify(o.state,null,2)+"\n"],["wyniki/k22_wariant_szyny_dzielonej_NIE_CNC.svg",o.svg]]){const p=path.join(root,filename);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,s);}console.log(JSON.stringify({opening:o.state.available_corridor_after_remove.opening_width_mm,rail_split:o.state.two_part_spine_entry_screen.pieces,approval:false}));}
if(require.main===module)main();module.exports={buildK22};
