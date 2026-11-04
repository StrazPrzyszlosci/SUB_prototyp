#!/usr/bin/env node
"use strict";
// K21 K15/K17 topological necessary-condition proof. NOT FULL 3D and NOT CNC.
const fs=require("node:fs"),path=require("node:path");
function buildK21(k15,k17){
 const xmax=998,xmin=22,rails=k17.spines.filter(r=>r.row!=="front").sort((a,b)=>a.o[0]-b.o[0]);
 if(rails.length!==8||k17.spines.length!==12)throw Error("K17 geometry changes; recalculate projection families");
 const rects=rails.map(r=>({id:r.id,row:r.row,module_indices:r.module_indices,x0:r.o[0],x1:r.o[0]+r.s[0],y0:r.o[1],y1:r.o[1]+r.s[1],z0:r.o[2],z1:r.o[2]+r.s[2]}));
 function gaps(rows){
   const out=[];let start=xmin;
   for(const r of rows){
     if(r.x0<start-1e-8)throw Error("Overlapping spines");
     out.push({x0:start,x1:r.x0,width_mm:+(r.x0-start).toFixed(6),left_boundary_rail:"",right_boundary_rail:r.id});
     start=r.x1;
   }
   out.push({x0:start,x1:xmax,width_mm:+(xmax-start).toFixed(6),left_boundary_rail:"",right_boundary_rail:"cabinet"});
   for(let i=0;i<out.length;i++)out[i].left_boundary_rail=i===0?"cabinet":rows[i-1].id;
   return out;
 }
 const xgaps=gaps(rects),largest=Math.max(...xgaps.map(g=>g.width_mm));
 if(largest!==130)throw Error("Reference geometry drift "+largest);
 const samples=[];
 for(const m of k15.module_positions.filter(m=>m.global_origin_xyz_mm[1]>220)){
   const [w,d,h]=m.dims_xyz_mm;
   const topological_y0=180;
   const yPass=[topological_y0,topological_y0+d];
   const allSimultaneous=rects.every(r=>Math.min(yPass[1],r.y1)-Math.max(yPass[0],r.y0)>0);
   const crossesByContinuity=topological_y0<m.global_origin_xyz_mm[1];
   const fullHeight=rects.every(r=>r.z0<=22&&r.z1>=478);
   if(!allSimultaneous||!crossesByContinuity||!fullHeight)throw Error("Proof premises false for module "+m.i);
   const minPlanarYawProjection=Math.min(w,d);
   samples.push({module:m.i,width_mm:w,depth_mm:d,height_mm:h,final_y0_mm:m.global_origin_xyz_mm[1],
     mandatory_y0_reference_mm:topological_y0,simultaneous_8_rail_y_intersection:true,
     unchanged_orientation_translation_clearance_without_margin_mm:+(largest-w).toFixed(6),
     axis_aligned_pure_translation_blocked:true,
     minimum_x_projection_over_planar_yaw_deg_0_to_90_mm:minPlanarYawProjection,
     planar_yaw_with_6mm_each_side_required_mm:minPlanarYawProjection+12,
     planar_yaw_with_6mm_each_side_blocked:(minPlanarYawProjection+12)>largest,
     full_3d_rotation_or_rail_reassembly_validated:false});
 }
 if(samples.length!==12)throw Error("Twelve rear modules expected");
 const alternative=rects.map(r=>{
   const reduced=rects.filter(z=>z.id!==r.id);
   const gs=gaps(reduced);
   const max=Math.max(...gs.map(x=>x.width_mm));
   return {removed_spine:r.id,max_gap_after_removal_mm:max,unrotated_210mm_box_plus_6mm_each_side_clearance_possible_in_projection:max>=222,
    active_box_supports_lost:r.module_indices,not_an_approved_redesign:true};
 }).sort((a,b)=>b.max_gap_after_removal_mm-a.max_gap_after_removal_mm||a.removed_spine.localeCompare(b.removed_spine));
 const model={
  study:"K21",date:"2026-11-04",status:"CNC HOLD — impossible rigid unrotated rearward passage for all 12 rear modules under existing full-height K17 guide arrangement",
  source:"K15 target volumes and K17 12 full-height rail solids; no assumptions about motor basket beyond source location",
  assumptions:{reference_cabinet_interior_x_mm:[xmin,xmax],full_height_rails_z_mm:[22,478],original_K17_back_rail_count:8,
   critical_box_front_y_mm:180,uniform_nominal_clearance_for_planar_yaw_screen_mm:6,
   rectangle_topological_crossing:"A continuous from-front insertion must pass the box near face Y=180 before reaching rear-box final Y>=227. At that point an unrotated box of depth 100/120mm simultaneously overlaps both rear rail bands Y208–220 and Y224–236."},
  back_rail_rectangles:rects,available_x_intervals_at_required_y_crossing:xgaps,max_open_gap_x_mm:largest,
  rear_module_count:samples.length,per_rear_module:samples,
  global_invariants:{all_12_rear_modules_unrotated_axis_aligned_trajectory_BLOCKED:true,
   all_8_large_rear_modules_planar_yaw_with_6mm_clearance_BLOCKED:true,
   small_rear_modules_planar_yaw_with_6mm_clearance_NOT_GEOMETRICALLY_PROVEN_BLOCKED:true,
   true_swept_3D_rotation_feasibility:"NOT TESTED; do not claim impossibility of every conceivable 3D motion",
   current_K18_K20_reference_DXF_approved_for_CNC:false},
  one_spine_removal_gap_screens:alternative,
  critical_next_decision:"Redesign support architecture to preserve full-load two-point support and create a proven service corridor, or prove swept 3D rotational insertion. Removing a spine loses part of its associated module support and cannot be treated as approved."
 };
 const scale=1.02,translateX=x=>20+(x-xmin)*scale;
 const width=1040,height=380;
 const bars=rects.map(r=>{
   const y=r.row==="rear_small"?82:170;
   return `<rect x="${translateX(r.x0).toFixed(1)}" y="${y}" width="${(r.x1-r.x0)*scale}" height="42" fill="#c15543"/><text x="${translateX((r.x0+r.x1)/2).toFixed(1)}" y="${y-9}" text-anchor="middle" font-size="10">${r.id.replace("G17_COLUMN_","R")}</text>`;
 }).join("\n");
 const gapHi=xgaps.filter(x=>x.width_mm===largest).map(g=>`<rect x="${translateX(g.x0).toFixed(1)}" y="214" width="${(g.width_mm*scale).toFixed(1)}" height="24" fill="#a1d9be" fill-opacity=".85"/><text x="${translateX((g.x0+g.x1)/2).toFixed(1)}" y="230" text-anchor="middle" font-size="12">${largest} mm</text>`).join("\n");
 const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
<rect width="${width}" height="${height}" fill="#f8fafb"/>
<text x="20" y="28" font-size="19" font-weight="bold" fill="#203544">K21 — full-height rear guide corridor: NO CNC RELEASE</text>
<text x="20" y="49" font-size="12" fill="#455766">X projection of rear rails. Y=180 mm box-front crossing intersects both bands simultaneously.</text>
<rect x="20" y="69" width="${(976*scale).toFixed(1)}" height="143" fill="#e9eef1" stroke="#617781"/>
${bars}
<text x="22" y="78" font-size="10" fill="#52677b">small-rear rail row Y224–236</text>
<text x="22" y="166" font-size="10" fill="#52677b">large-rear rail row Y208–220</text>
${gapHi}
<text x="20" y="265" font-size="15" font-weight="bold" fill="#9d392e">Max opening: 130 mm. Rear box widths: 180 or 210 mm.</text>
<text x="20" y="289" font-size="13" fill="#2c4659">Rigid, non-rotating front-to-rear insertion: 12/12 rear boxes BLOCKED in this model.</text>
<text x="20" y="313" font-size="13" fill="#2c4659">90-degree planar yaw, large 120-mm-deep box + 6 mm each edge = 132 mm: BLOCKED.</text>
<text x="20" y="344" font-size="13" font-weight="bold" fill="#9d392e">Rotating/tilting in 3D, fastening, or redesign has NOT been validated.</text>
</svg>\n`;
 return {model,svg};
}
function main(){const root=path.resolve(__dirname,"..");const a=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k15_p30e_przed_CNC_zestawienie.json"),"utf8"));const b=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k17_prowadnice_boczne_wkladow.json"),"utf8"));const o=buildK21(a,b);for(const [file,content] of [["wyniki/k21_przesmyk_montazowy.json",JSON.stringify(o.model,null,2)+"\n"],["wyniki/k21_przesmyk_prowadnic_NIE_CNC.svg",o.svg]]){const p=path.join(root,file);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,content);}console.log(JSON.stringify({rear_modules:o.model.rear_module_count,max_free_gap_mm:o.model.max_open_gap_x_mm,axis_aligned_blocked:o.model.global_invariants.all_12_rear_modules_unrotated_axis_aligned_trajectory_BLOCKED,approval:false}));}
if(require.main===module)main();module.exports={buildK21};
