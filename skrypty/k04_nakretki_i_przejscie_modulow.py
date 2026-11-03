#!/usr/bin/env python3
"""K04. Conditional nut/washer physical envelopes plus K02 module-ingress replay.

Source geometry: Dayton RSS390HF-4 cutout 355.8, BCD368, K02 inner pad R178.9,
20mm nominal pad. Nut AF10 M6 and AF8 M5 from ISO4032-style tables; normal
washers M6 OD12 and M5 OD10 from ISO7089 manufacturer references.
Ideal regular hex = approximation, not a certified manufactured tolerance.
Additional fastener obstacles represented conservatively as WHOLE pad prisms,
not as exact supplier hardware. A failed path therefore does NOT prove impossible.
All claims research-only, not CNC / not a physical or material strength test.
"""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"skrypty"))
import k02_dostep_modulow_i_klocki as k02
import k01_mocowanie_bilans as k01

RB=184.
RCUT=177.9
RPAD=178.9
WOOD=20.
FLANGE=10.5
FRONT=44.
AF={"M5":8.0,"M6":10.0}
NUT_H={"M5":4.7,"M6":5.2} # source-specific nominal ISO4032 examples
WASHER_OD={"M5":10.0,"M6":12.0}
WASHER_T={"M5":1.0,"M6":1.6} # nominal normal ISO7089 example, NOT a selected washer

def inward_hex_projection(across_flats,orientation_deg):
    r=across_flats/math.sqrt(3)
    return max(-r*math.cos(math.radians(orientation_deg+60*k)) for k in range(6))

def geometry():
    rows=[]
    for size,angle,tol in itertools.product(("M5","M6"),(0,5,10,15,20,25,30),(0,.25,.5)):
        extent=inward_hex_projection(AF[size],angle)
        rows.append({"size":size,"orientation_deg":angle,"radial_uncertainty_mm":tol,
          "nominal_hex_corner_radius_mm":round(AF[size]/math.sqrt(3),6),
          "inward_projection_mm":round(extent,6),
          "nominal_available_to_pad_mm":RB-RPAD,
          "minimum_material_supported_radially_mm":round(RB-RPAD-extent-tol,6),
          "nominal_gap_to_cutout_mm":round(RB-RCUT-extent-tol,6),
          "completely_inside_nominal_pad_xz_for_this_orientation":RB-RPAD-extent-tol>=-1e-9,
          "outside_nominal_cutout_for_this_orientation":RB-RCUT-extent-tol>=-1e-9})
    assert len(rows)==42
    for size in AF:
        r=AF[size]/math.sqrt(3)
        assert abs(inward_hex_projection(AF[size],0)-r)<1e-10
        assert abs(inward_hex_projection(AF[size],30)-AF[size]/2)<1e-10
    washers=[{"size":size,"nominal_OD_mm":WASHER_OD[size],
       "radial_support_margin_on_pad_mm":round(RB-RPAD-WASHER_OD[size]/2,6),
       "radial_margin_to_baffle_cutout_mm":round(RB-RCUT-WASHER_OD[size]/2,6),
       "margin_to_cutout_with_0_5mm_offset_mm":round(RB-RCUT-WASHER_OD[size]/2-.5,6)}
       for size in AF]
    # The metal bridging piece is an unverified geometric IDEA, not a selected part.
    ring_scenario={
       "steel_spreader_inner_radius_mm":178.0,
       "steel_spreader_outer_radius_mm":202.0,
       "steel_spreader_tangential_width_mm":24.0,
       "radial_ligament_at_hypothetical_6_6mm_bore_mm":round(
           RB-178.0-6.6/2,4),
       "metal_inward_overhang_over_wood_mm":round(RPAD-178.0,4),
       "nominal_gap_from_spreader_inner_edge_to_cutout_mm":round(178.0-RCUT,4),
       "max_hex_corner_projection_M6_mm":round(AF["M6"]/math.sqrt(3),4),
       "max_hex_corner_min_radius_M6_mm":round(RB-AF["M6"]/math.sqrt(3),4),
       "M6_12mm_washer_min_radius_mm":RB-6.,
       "structural_adequacy":"UNKNOWN: required plate bending, hole-edge, nut retention, glue/MDF coupons",
       "basket_3D_clash":"UNKNOWN",
       "module_route_for_real_part":"UNKNOWN",
       "warning":"The ideal spreader may cantilever 0.9mm inward of the wood and have only 0.1mm to nominal cutout. Not a fabrication drawing."}
    return rows,washers,ring_scenario

def passage():
    # This is a bounding envelope: hardware is assumed to fill the pad's
    # WHOLE XZ projection from front Y44 to the total rear-most axial depth.
    # It overstates most metal obstacle volumes. It does not include real ribs
    # or tool swept geometry. It is a conservative success test, not failure proof.
    cases=[
       ("C20_no_fastener",20.,178.9),
       ("C20_plus_plate_2",22.,178.0),
       ("C20_plate2_washer_nutM5",20.+2.+WASHER_T["M5"]+NUT_H["M5"],178.0),
       ("C20_plate2_nutM6_no_washer",20.+2.+NUT_H["M6"],178.0),
       ("C20_plate2_washer_nutM6",20.+2.+WASHER_T["M6"]+NUT_H["M6"],178.0),
       ("C20_plate4_washer_nutM6",20.+4.+WASHER_T["M6"]+NUT_H["M6"],178.0),
       ("C30_no_fastener",30.,178.9),
    ]
    configs=[]
    states=[("100L",list(range(20)))]
    # Additional 120/150L checks only for baseline and M6 stack, so
    # we prioritize the constraining 100L assembly state.
    for name,depth,rin in cases:
        for clearance in (3.,6.):
            for label,indices in states:
                pads=[[(x-22,z-22) for x,z in k01.polygon(231,45*i,rin,205.,36.)]
                      for i in range(8)]
                r=k02.check_state(label,indices,clearance,pads,depth)
                configs.append({"case":name,"total_obstacle_depth_mm":round(depth,4),
                      "radial_interior_of_obstacle_mm":rin,
                      "assumed_clearance_mm":clearance,
                      "state":label,"modules_completed":r["completed_modules"],
                      "modules_required":r["requested_modules"],
                      "passed_conservative_bounding_prism":r["passed_full_sequence"],
                      "detours":r["pad_aware_detours"],
                      "first_failure":r["failures"][0] if r["failures"] else None})
                print("K04_ROUTE",name,clearance,r["completed_modules"],"/",
                      r["requested_modules"],flush=True)
    assert len(configs)==14
    bare=[x for x in configs if x["case"]=="C20_no_fastener"]
    assert all(x["modules_completed"]==20 for x in bare)
    for state,indices in (("120L",list(range(4,16))),("150L",[4])):
        for clearance in (3.,6.):
            for name,depth,rin in (cases[0],cases[3]):
                pads=[[(x-22,z-22) for x,z in k01.polygon(231,45*i,rin,205.,36.)]
                       for i in range(8)]
                r=k02.check_state(state,indices,clearance,pads,depth)
                configs.append({"case":name,"total_obstacle_depth_mm":round(depth,4),
                      "radial_interior_of_obstacle_mm":rin,
                      "assumed_clearance_mm":clearance,"state":state,
                      "modules_completed":r["completed_modules"],
                      "modules_required":r["requested_modules"],
                      "passed_conservative_bounding_prism":r["passed_full_sequence"],
                      "detours":r["pad_aware_detours"],
                      "first_failure":r["failures"][0] if r["failures"] else None})
                print("K04_ROUTE",name,clearance,state,r["completed_modules"],
                      "/",r["requested_modules"],flush=True)
    assert len(configs)==22
    return configs

def installed_module_static_check():
    """Independent of route planner: all FINAL box positions after inserting 20.
    This says nothing about the swept entry corridor, tools or real fasteners.
    """
    L,br,mods,mat=k02.e.build(k02.SELECTED)
    assert len(mods)==20
    pads=[[(x-22,z-22) for x,z in k01.polygon(231,45*i,178.0,205.,36.)]
          for i in range(8)]
    clearance=6.
    failures=[i for i,m in enumerate(mods) if k02.collision_with_pads(
       k02.p.box(m[0]-clearance,m[1]+clearance),pads,28.8)]
    assert not failures,failures
    # Independent axial/normal bounding separation witnesses:
    # large modules (indices 4-19) are at x >= 469.5 mm; pad <= 414 mm.
    # small modules (indices 0-3) are at y >= 203 mm; hardware <=28.8 mm.
    min_big_x=min(float(m[0,0]) for m in mods[4:])
    min_small_y=min(float(m[0,1]) for m in mods[:4])
    assert abs(min_big_x-469.5)<1e-6
    assert abs(min_small_y-203.)<1e-6
    assert abs((min_big_x-6)-(209+205)-49.5)<1e-6
    assert abs((min_small_y-6)-28.8-168.2)<1e-6
    return {"modules_in_final_100L_positions":20,
      "model_clearance_mm":6.,
      "collisions_with_fastener_full_pad_prism":0,
      "lowest_large_module_x_mm":min_big_x,
      "highest_pad_x_mm":414.,
      "lowest_small_module_y_mm":min_small_y,
      "highest_fastener_y_mm":28.8,
      "minimum_axis_box_gap_large_modules_with_6mm_mm":49.5,
      "minimum_axis_box_gap_small_modules_with_6mm_mm":168.2,
      "interpretation":"STATIC TARGET ONLY, NOT MODULE INSERTION OR REAL TOOL ACCESS"}

def main():
    rows,washers,spreader=geometry()
    static=installed_module_static_check()
    passage_tests=passage()
    summary={
       "study":"K04","date":"2026-11-03",
       "evidence":"source-grounded nominal nut and washer geometry and conservative P30E/K02 assembly replay; NOT actual fastener or basket CAD",
       "manufacturer_driver":"Dayton RSS390HF-4",
       "radial_distance_axis_to_cutout_mm":round(RB-RCUT,4),
       "radial_distance_axis_to_K02_pad_inner_mm":round(RB-RPAD,4),
       "ideal_hex_nut_size_by_flats_mm":AF,
       "ideal_hex_nut_height_model_mm":NUT_H,
       "nominal_normal_washer_thickness_mm":WASHER_T,
       "nut_rotations_checked":7,
       "ideal_hex_cases":len(rows),
       "nominal_hex_0deg_vs30deg":[x for x in rows if x["radial_uncertainty_mm"]==0 and x["orientation_deg"] in (0,30)],
       "washer_budgets":washers,
       "metal_spreader_conditional_hypothesis":spreader,
       "static_positions_final_100L_check":static,
       "route_checks":len(passage_tests),
       "module_path_results":passage_tests,
       "hard_constraints":[
         "The 20mm wooden pad alone passed K02 but real captive nut and plate protrude beyond it",
         "A plate whose footprint extends inward beyond wood may obstruct actual Dayton basket/ribs (not measured)",
         "Nominal M6 washer OD12 has negative radial support margin on the K02 wooden pad",
         "Hex corner 11.05mm in secondary catalog is a MINIMUM, not a maximum envelope; program idealizes AF=10 regular hex",
         "A failed conservative prism path does not disprove all real compact fastener geometries or insertion orders",
         "Plate stiffness, bending, bearing, hold-down, MDF splitting and bolt shank strength not proven",
         "Do not select screws, torque, components, CNC or cabinet production on this evidence"],
       "next_action":"Dry-fit one real driver/accurate manufacturer CAD and actual fastener/plate sample; record eight distinct 3D clearances; run the same 20-module insertion with hands/tool envelopes and compare joint coupons N/S"
    }
    path=ROOT/"wyniki";path.mkdir(exist_ok=True)
    full={"summary":summary,"nut_sensitivity":rows}
    f=path/"k04_pelne_analizy_geometryczne.json"
    f.write_text(json.dumps(full,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (path/"k04_manifest_odtworzony.json").write_text(json.dumps(
       {"summary":summary,"generated_file_sha256":hashlib.sha256(f.read_bytes()).hexdigest()},
       ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("K04_SUMMARY",json.dumps({
       "hex_count":len(rows),"paths_count":len(passage_tests),
       "paths":[(r["case"],r["state"],r["assumed_clearance_mm"],
                  r["modules_completed"],r["modules_required"]) for r in passage_tests]},
       ensure_ascii=False))
if __name__=="__main__":
    main()
