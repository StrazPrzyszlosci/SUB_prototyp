#!/usr/bin/env node
"use strict";
// Research-only K18 DXF generator; every output is CNC HOLD.
const fs=require("node:fs"),path=require("node:path");
function rect(x,y,w,h){return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]];}

function area(p){let s=0;for(let i=0;i<p.length;i++){let j=(i+1)%p.length;s+=p[i][0]*p[j][1]-p[j][0]*p[i][1];}return Math.abs(s/2);}

function poly(points,layer){
 const e=["0","LWPOLYLINE","8",layer,"90",String(points.length),"70","1"];
 for(const p of points)e.push("10",String(+p[0].toFixed(4)),"20",String(+p[1].toFixed(4)));
 return e;
}

function circle(x,y,r){return ["0","CIRCLE","8","FACTORY_CUTOUT_REFERENCE_NO_CAM","10",String(x),"20",String(y),"30","0","40",String(r)];}

function label(x,y,t){return ["0","TEXT","8","LABEL_NO_CAM","10",String(x),"20",String(y),"30","0","40","10","1",t];}

function layout(parts){
 let x=0,y=0,h=0;return parts.map(p=>{
 if(x && x+p.w>2300){x=0;y+=h+40;h=0;}
 const out={...p,dx:x,dy:y};x+=p.w+40;h=Math.max(h,p.h);return out;
 });
}

function railProfile(c,tabs){
 const left=c.o[1],right=left+c.s[1],bottom=c.o[2]-3,top=c.o[2]+c.s[2]+3;
 const z=[...new Set([bottom,top,...tabs.flatMap(t=>[t.o[2],t.o[2]+t.s[2]])])].sort((x,y)=>x-y);
 let pts=[[0,0]],old=0;
 for(let i=0;i<z.length-1;i++){
   const far=Math.max(right,...tabs.filter(t=>t.o[2]<=z[i]+1e-7 && t.o[2]+t.s[2]>=z[i+1]-1e-7).map(t=>t.o[1]+t.s[1]))-left;
   if(i===0||old!==far)pts.push([far,z[i]-bottom]);
   pts.push([far,z[i+1]-bottom]);old=far;
 }
 pts.push([0,top-bottom]);
 return {id:c.id,xyz:c.o,dimension:c.s,w:Math.max(...pts.map(x=>x[0])),h:top-bottom,points:pts,area_mm2:area(pts),contacts:tabs.length};
}

function build(k15,k17){
 const shell=k15.parts.filter(p=>p.thickness_mm===22),modules=k15.parts.filter(p=>p.thickness_mm===8);
 if(shell.length!==18||modules.length!==120||k17.spines.length!==12||k17.contact_lips.length!==80)throw Error("Source geometry mismatch");
 const rails=k17.spines.map(c=>railProfile(c,k17.contact_lips.filter(t=>t.group===c.group&&Math.abs(t.o[0]-c.o[0])<1e-8)));
 const railSum=rails.reduce((s,r)=>s+r.area_mm2*16/1e6,0);
 if(Math.abs(railSum-k17.fixed_support_volume_l-0.012288)>1e-8)throw Error("K17 union area disagreement: "+railSum);
 const family=[
  {path:"dokumentacja/cnc/K18_korpus_i_wregi_MDF22_NIE_CNC.dxf",items:shell.map(p=>({id:p.id,w:p.blank_a_mm,h:p.blank_b_mm,thickness:22,type:p.type,area_mm2:p.blank_a_mm*p.blank_b_mm})),kind:1},
  {path:"dokumentacja/cnc/K18_skrzynki_regulacji_MDF8_NIE_CNC.dxf",items:modules.map(p=>({id:p.id,w:p.blank_a_mm,h:p.blank_b_mm,thickness:8,type:p.type,area_mm2:p.blank_a_mm*p.blank_b_mm})),kind:2},
  {path:"dokumentacja/cnc/K18_prowadnice_laminat_MDF8_NIE_CNC.dxf",items:rails.flatMap(r=>["A","B"].map(layer=>({id:r.id+"_"+layer,w:r.w,h:r.h,thickness:8,type:"K17_RAIL_CONCEPT",area_mm2:r.area_mm2,points:r.points}))),kind:3}
 ];
 const files={}, rows=[];let socketCount=0,removedMDF=0;
 for(const f of family){
  let d=["0","SECTION","2","HEADER","9","$ACADVER","1","AC1015","9","$INSUNITS","70","4","0","ENDSEC","0","SECTION","2","ENTITIES"];
  for(const p of layout(f.items)){
    const outline=p.points||rect(0,0,p.w,p.h);
    d.push(...poly(outline.map(q=>[q[0]+p.dx,q[1]+p.dy]),"REFERENCE_PROFILE_HOLD"));
    d.push(...label(p.dx,p.dy+p.h+14,p.id+" "+p.thickness+"mm NO CAM"));
    if(p.id==="FR1"||p.id==="FR2")d.push(...circle(p.dx+231,p.dy+250,177.9));
    if(p.id==="TOP"||p.id==="BOTTOM"){
      for(const r of rails){
        const px=r.xyz[0]-22-0.25;
        const py=Math.max(44,r.xyz[1]-0.25)-44;
        const w=16.5,h=r.dimension[1]+0.5;
        if(px<0||py<0||px+w>p.w||py+h>p.h)throw Error("socket overhang "+r.id);
        d.push(...poly(rect(p.dx+px,p.dy+py,w,h),"POCKET_3MM_CONCEPT_HOLD"));
        socketCount++;removedMDF+=w*h*3;
      }
    }
    rows.push([p.id,p.thickness,p.w,p.h,+p.area_mm2.toFixed(5),p.type,f.path,"CNC_HOLD"]);
  }
  d.push("0","ENDSEC","0","EOF");files[f.path]=d.join("\n")+"\n";
 }
 if(rows.length!==162||socketCount!==24)throw Error("Invalid part totals "+rows.length+" "+socketCount);
 const load=[];
 for(const [name,dims] of [["small",[180,100,100]],["rear_large",[210,120,100]],["front_large",[210,150,100]]]){
   const [x,y,z]=dims,m=(x*y*z-(x-16)*(y-16)*(z-16))/1e9*730;
   const F=m*5*9.81/2,sig=6*F*12/(16*4**2),bend=4*F*12**3/(2700*16*4**3);
   load.push({module:name,shell_mass_kg:+m.toFixed(6),model_5g_support_N:+F.toFixed(4),lip_bending_MPa:+sig.toFixed(5),lip_tip_mm:+bend.toFixed(5)});
 }
 const v={};for(const [key,n]of Object.entries(k15.reference_net_l_P30E_no_new_pads))v[key]={P30E_l:n,K17_l:+(n-k17.fixed_support_volume_l).toFixed(6),K17_and_K01_conditional_l:+(n-k17.fixed_support_volume_l-k15.pad_displacement_l_only_if_new_and_full_eight_present).toFixed(6)};
 const m={
 study:"K18",date:"2026-11-04",release:"CNC_HOLD_RESEARCH_CONTOURS_ONLY",
 input_geometry:"K15 + K17; no change to 20 module boxes or 11 initial braces",
 mdf22_contours:18,mdf8_module_contours:120,mdf8_rail_lamina_contours:24,
 rail_count:12,assembled_rail_width_x_mm:16,assembled_rail_length_z_mm:462,
 proposed_top_and_bottom_socket_depth_mm:3,proposed_socket_total_clearance_xy_mm:0.5,
 socket_outlines:socketCount,total_dxf_profiles:rows.length,
 M5_wood_fastener_holes_defined:false,dayton_factory_cutout_diameter_mm:355.8,actual_CNC_toolpaths:false,
 rail_lip_height_z_mm:4,nominal_gap_between_adjacent_modules_z_mm:10,
 nominal_module_clearance_with_rigid_top_bottom_lips_mm:0,
 rail_displacement_in_air_l:k17.fixed_support_volume_l,
 nominal_rail_total_solid_with_extra_socket_tenons_l:+railSum.toFixed(6),
 mdf_removed_by_socket_concept_l:+(removedMDF/1e6).toFixed(6),
 nominal_net_volumes_l:v,model_5g_lip_demand:load,
 major_issues:["No actual serviceable upper latch; K17 rigid lips contact both box faces with zero nominal play","4mm lips cannot be qualified from ideal beam result; local fracture and joint need tests","Bare spines simply touching panels do not establish a dependable attachment; proposed 3mm sockets require material and insertion tests","Full 462mm rails and all twenty boxes must be insertion-proven through Ø355.8 opening with bracing present","Real driver fastener, actual basket solid, cable, grill and terminal remain absent","10mm brace web and cutter radii not verified","DXF sheets are reference display, not material nesting; no CAM release"]
 };
 files["wyniki/k18_lista_162_konturow_CNC_HOLD.csv"]="id,thickness_mm,blank_w_mm,blank_h_mm,profile_area_mm2,part_type,DXF_file,release\n"+rows.map(r=>r.join(",")).join("\n")+"\n";
 files["wyniki/k18_mocowania_i_CNC_podsumowanie.json"]=JSON.stringify(m,null,2)+"\n";
 files["dokumentacja/cnc/K18_README.md"]=`# K18 | CNC contour review — DO NOT MACHINE\n\nAll dimensions in **mm**. These three AutoCAD-2015 DXF files are **shape-reference drawings, not CNC orders or CAM toolpaths**. All cut profiles are on \`REFERENCE_PROFILE_HOLD\`; optional 3mm mounting recess envelopes are on \`POCKET_3MM_CONCEPT_HOLD\`; Ø355.8 factory reference cutouts use \`FACTORY_CUTOUT_REFERENCE_NO_CAM\`; labels are \`LABEL_NO_CAM\`. There are **no MDF screw holes** on the front; the Dayton factory flange uses 8×Ø6.5 on PCD Ø368 and must not be treated as wood drill diameters.\n\n- [MDF22 cabinet and provisional ribs](K18_korpus_i_wregi_MDF22_NIE_CNC.dxf): 18 contours, 2 reference driver bores and 24 proposed 3mm grooves in top/bottom panels. The 10mm web is exceptionally slender.\n- [MDF8 modular displacement boxes](K18_skrzynki_regulacji_MDF8_NIE_CNC.dxf): 120 faces for twenty six-panel boxes.\n- [MDF8 hypothetical laminated rail profiles](K18_prowadnice_laminat_MDF8_NIE_CNC.dxf): 24 faces of 12 two-ply rails, with 3mm extra tongue at each end. Upper solid retainer lips are **NOT ASSEMBLY QUALIFIED** and should be redesigned.\n\nProfiles are placed apart **for viewing only**, not on stock sheets; cutter diameter, radii, tool compensation, machine, part tabs, glue, material tolerances, sealing and fit are unselected. Mounting screws, locking clips, MDF inserts, terminals, grille, cable fixtures and gasket details do not exist in this package. Full [K18 report](../../raporty/K18_projekt_CNC_mocowania_wkladow.md) and [numerical audit](../../wyniki/k18_mocowania_i_CNC_podsumowanie.json). Regenerate from repo root: \`node skrypty/k18_cnc_kontury.js\`. **CNC HOLD.**\n`;
 files["raporty/K18_projekt_CNC_mocowania_wkladow.md"]=`# K18 — module mounting calculation and full MDF CNC profile audit\n\n**4 November 2026 — research drawing package, not production release. CNC HOLD.** This study advances K15/K16/K17 and retains their existing cabinet 1020×425×500mm, MDF22 shell (2×22 front), MDF8 closed displacement modules, nominal basket opening Ø355.8 and 50mm rear mat. The electronics remain outside the cabinet.\n\n## 1. What is dimensioned, and what is not?\n\nK15 defined 7 shell panels, 11 provisional braces and 120 faces for 20 removable sealed volume boxes. K17 introduced 12 full-height rail spines with 80 geometric support/retainer contacts. K18 now derives **162 distinct reference blank profiles**: 18 MDF22, 120 MDF8 box panels and 24 MDF8 laminates for twelve 16mm rails. It also places 24 **hypothetical 3mm socket outlines** in the MDF22 top and bottom. The original 456mm rails between Z=22 and Z=478 are extended by 3mm at each end to 462mm, notionally engaging the top/bottom sockets. Nominal socket clearance totals 0.5mm in each flat dimension (no fit or glue approval). Pocket dimensions and depth are not CNC-approved; all profiles remain CNC HOLD.\n\nThe drawings [MDF22](../dokumentacja/cnc/K18_korpus_i_wregi_MDF22_NIE_CNC.dxf), [MDF8 boxes](../dokumentacja/cnc/K18_skrzynki_regulacji_MDF8_NIE_CNC.dxf), [laminated rail profiles](../dokumentacja/cnc/K18_prowadnice_laminat_MDF8_NIE_CNC.dxf) and [162-item cutlist](../wyniki/k18_lista_162_konturow_CNC_HOLD.csv) are generated by the [K18 script](../skrypty/k18_cnc_kontury.js). Unlike an actual manufacturing drawing, they do not define end-mill, dog-bones, holding tabs, machining compensation, tolerances, available stock, adhesive, locking hardware or approved joints. In particular the two front boards have the **factory basket cutout only as a reference**; the factory Ø6.5 steel-flange holes are NOT MDF holes. Material thickness, glue and fasteners need proof before manufacturing.\n\n## 2. How would each insert be supported?\n\nAs in K17, two rail spines run beside each group; each module is geometrically supported by two 16mm-wide × 4mm-high lip ledges extending 12mm under its shell, plus two nominal upper lips. The nominal top/bottom 3mm sockets are a proposal for transferring load to MDF panels instead of leaving rails floating. They would require assembly before the top cabinet panel is closed, physical rail-end retention and structural adhesive/joint qualification. **No screw, latch or pull-out capacity is implied by a socket outline.**\n\nThe **critical assembly defect remains:** K17's rigid upper and lower lips nominally contact both faces of each 100mm-high insert. There is **zero designed installation clearance** for an insert in a completed pair of lips. The 10mm gaps between neighbouring module boxes leave only 2mm between adjacent 4mm-high lip envelopes, which does not provide an insertion path. Thus the literal integral upper lips in the DXF are **for geometry review only; do not manufacture them**. Prefer an adjustable, **removable positive upper keeper** after inserting a box, with non-rattling compliant bearing and a defined release tool. The exact keeper and fastener geometry is still to be designed.\n\n## 3. Explicit mechanical screening (not strength certification)\n\nA single module at hypothetical 5g, load shared by two lower (or two upper) lips, has force per lip F=m×5×9.81/2. For ideal 12mm unsupported length, width b=16mm, thickness t=4mm, and notional MDF8 E=2700MPa: bending stress = 6FL/(b t²), deflection = 4FL³/(E b t³). Only the module's **shell** mass was counted. No payload, fasteners, tolerance, notch concentration, fatigue, creep, laminate seam, shear block, impact or strength allowables are included.\n\n| Module | Shell mass kg | Hypothetical 5g force per lip N | Ideal stress MPa | Tip deflection mm |\n|---|---:|---:|---:|---:|\n${load.map(x=>`| ${x.module} | ${x.shell_mass_kg.toFixed(3)} | ${x.model_5g_support_N.toFixed(2)} | ${x.lip_bending_MPa.toFixed(2)} | ${x.lip_tip_mm.toFixed(4)} |`).join("\n")}\n\nThese results cannot justify a 4mm MDF lip. A positive retaining mechanism must be engineered to withstand inversion, transportation, service cycles, pressure excitation and vibration in all mounting orientations. Each rail's two end joints and any independent locks need fatigue/adhesive/pull-out test coupons.\n\n## 4. Correct net-volume accounting\n\nThe K17 **permanent in-air** support union displaces ${k17.fixed_support_volume_l.toFixed(6)}l. Extra K18 3mm tenons would be embedded into the cabinet's MDF panels, not suspended in free air; the proposal adds ${(railSum-k17.fixed_support_volume_l).toFixed(6)}l of wood in nominal sockets created by removing ${(removedMDF/1e6).toFixed(6)}l of MDF. These are *not* automatic additional free-air displacements. Existing K15 assumes 5l for the real basket and 0.175l for hardware, not measured values.\n\n| State | P30E reference l | Minus existing K17 rails l | Also minus eight possible K01 pad envelopes l |\n|---|---:|---:|---:|\n${Object.entries(v).map(([state,x])=>`| ${state} | ${x.P30E_l.toFixed(3)} | ${x.K17_l.toFixed(3)} | ${x.K17_and_K01_conditional_l.toFixed(3)} |`).join("\n")}\n\nThe K01 last column is conditional on **non-overlapping, newly installed** pad solid volumes, not a settled Dayton screw connection; no rail bolt, gaskets, glue or keeper displacement has yet been included. The 100/120/150l labels remain *target settings*, not measured final net volumes.\n\n## 5. Manufacturing closure requirements\n\n1. Finalize actual 3D Dayton basket and load path at all 8 flange axes. Separately calculate screw clearance and threaded metal/carrier interfaces; do not drill MDF at factory Ø6.5.\n2. Replace the 4mm integral upper retaining lips by an **installable removable clamp/keeper**, then verify actual 20 insert paths, one by one through the front opening with all surrounding parts and tools present. Repeat 100→120→150 and reverse.\n3. Verify each rail and proposed 3mm top/bottom pocket in laminated MDF22: bonding, bearing, pull-out, bending, shear, fatigue, acoustic seal and inversion; ensure tool radii and 10mm-thin K15 brace are producible.\n4. Test adhesive and real MDF8 panels, closed-box air-tightness, real mass, removable clamp vibrations and damping-mat clearance. Redo volume and acoustic calculation with full physical fasteners and adhesive.\n5. Specify connector plate and cable, feet, grille, whole-device depth no more than 500mm, exact stock, machining tolerances, nesting, cutters, two-side operations, dimensions and inspection samples. Conduct independent fabrication review before generating any CAM-ready DXF/STEP.\n\n**Conclusion:** Every currently defined reference MDF piece now has a corresponding inspectable DXF contour, but the **actual final CNC design is blocked by unqualified support/retention, insertion and structural joinery**. The next task is the removable keeper + swept-volume service proof, not cutting these files.\n`;
 return {files,m};
}
function main(){const root=path.resolve(__dirname,".."),a=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k15_p30e_przed_CNC_zestawienie.json"),"utf8")),b=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k17_prowadnice_boczne_wkladow.json"),"utf8")),v=build(a,b);for(const [p,t] of Object.entries(v.files)){const target=path.join(root,p);fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,t);}console.log(JSON.stringify({parts:v.m.total_dxf_profiles,pockets:v.m.socket_outlines,rail_volume_l:v.m.rail_displacement_in_air_l,release:v.m.release}));}
if(require.main===module)main();module.exports={build};
