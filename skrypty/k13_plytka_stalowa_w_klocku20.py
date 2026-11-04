#!/usr/bin/env python3
"""K13: candidate captive M5 steel plate RECESSED within a wooden 20mm pad.

Uses source-derived nominal basket and M5 standard dimensions but hypothetical
plate outline, capture screws, gasket thickness, thread fit and wood density.
No 3D basket scan, tool path, FEA, bolt proof load or bond strength calculation.
The 20mm bounding box condition does NOT imply actual K02 routes are reverified.
"""
from pathlib import Path
import json, math
R=Path(__file__).resolve().parents[1]
SRC=R/"dane"/"k13_plytka_m5_w_klocku20_zalozenia.json"
OUT=R/"wyniki"/"k13_przesiew_plytki_w_klocku20.json"

def rd(v): return round(float(v), 6)

def compute():
    s=json.loads(SRC.read_text(encoding="utf-8"))
    b=s["manufacturer_dayton"];wood=s["wood_and_pad"];pl=s["recessed_plate"]
    screw=s["screw_scenarios"];load=s["loads"]
    axis=b["mount_pcd_d_mm"]/2
    cut=b["basket_cutout_d_mm"]/2
    assert axis==184. and cut==177.9 and wood["pad_depth_mm"]==20
    assert wood["eight_pad_baseline_volume_L"]==.150336
    pi=wood["pad_radial_inner_radius_mm"]+pl["radial_inner_edge_inset_mm"]
    po=wood["pad_radial_outer_radius_mm"]-pl["radial_outer_edge_inset_mm"]
    tang=wood["pad_tangential_width_mm"]-2*pl["tangential_edge_inset_mm"]
    width=po-pi; A=width*tang
    assert abs(width-25.1)<1e-9 and tang==35
    major=pl["M5_coarse_thread_major_d_mm"]
    drill=pl["M5_tapping_drill_d_mm"]
    fastener=pl["example_retention_two_screws"]
    radial_ret=axis+fastener["positions_local_radial_offset_mm"]
    tangent_ret=fastener["positions_local_tangent_offset_abs_mm"]
    ret_clear=fastener["steel_clearance_d_mm"]/2
    ret_head=fastener["head_d_assumed_mm"]/2
    separation=math.hypot(radial_ret-axis,tangent_ret)
    geometry={
      "front_M5_example_wood_bore_mm":pl["M5_front_screw_clearance_d_mm"],
      "front_M5_wood_ligament_to_cutout_mm":rd(axis-cut-pl["M5_front_screw_clearance_d_mm"]/2),
      "manufacturer_metal_basket_hole_mm":b["metal_basket_hole_d_mm"],
      "plate_inner_radius_mm":rd(pi),
      "plate_outer_radius_mm":rd(po),
      "plate_tangential_width_mm":tang,
      "plate_face_area_mm2":rd(A),
      "plate_inner_metal_ligament_to_M5_major_thread_mm":rd(axis-pi-major/2),
      "plate_inner_metal_ligament_to_M5_tap_drill_mm":rd(axis-pi-drill/2),
      "plate_outer_metal_ligament_to_M5_major_thread_mm":rd(po-axis-major/2),
      "M5_ISO4762_head_od_mm":pl["M5_socket_head_nominal_d_mm"],
      "M5_head_radial_margin_to_basket_cutout_mm":rd(axis-cut-pl["M5_socket_head_nominal_d_mm"]/2),
      "retention_screw_count":2,
      "retention_center_radial_mm":radial_ret,
      "retention_center_tangent_abs_mm":tangent_ret,
      "retention_hole_d_mm":fastener["steel_clearance_d_mm"],
      "retention_head_nominal_d_mm":fastener["head_d_assumed_mm"],
      "retention_hole_edge_margin_inner_mm":rd(radial_ret-pi-ret_clear),
      "retention_hole_edge_margin_outer_mm":rd(po-radial_ret-ret_clear),
      "retention_hole_edge_margin_tangent_mm":rd(tang/2-tangent_ret-ret_clear),
      "retention_head_edge_margin_tangent_mm":rd(tang/2-tangent_ret-ret_head),
      "center_tap_to_retention_hole_edge_gap_mm":rd(separation-major/2-ret_clear),
      "nominal_180deg_inside_wall_at_steel_outer_edge_mm":rd(wood["global_axis_180deg_from_left_wall_mm"]-(po-axis)),
      "caveat":"Rectangular radial-tangent local model; full 3D basket, wall, plywood grain and tool rotation not checked."
    }
    assert geometry["front_M5_wood_ligament_to_cutout_mm"]==3.35
    assert geometry["plate_inner_metal_ligament_to_M5_major_thread_mm"]==2.1
    assert geometry["plate_inner_metal_ligament_to_M5_tap_drill_mm"]==2.5
    assert geometry["retention_head_edge_margin_tangent_mm"]==2.5
    assert geometry["nominal_180deg_inside_wall_at_steel_outer_edge_mm"]>0
    variants=[]
    for t in pl["plate_thickness_scenarios_mm"]:
        removed=A*t*8/1e6
        wood_left=wood["pad_depth_mm"]-t
        wood_screw_engagement=max(0.,fastener["under_head_length_mm"]-t)
        mass_steel=removed*pl["steel_density_assumed_kg_m3"]/1000
        displaced_wood=removed*wood["wood_density_assumed_kg_m3"]/1000
        variants.append({
          "plate_thickness_mm":t,"wood_remaining_behind_front_mm":wood_left,
          "plate_volume_all8_L":rd(removed),
          "steel_mass_all8_kg_gross_ignore_holes":rd(mass_steel),
          "wood_removed_all8_kg_ignore_holes":rd(displaced_wood),
          "net_mass_delta_all8_kg":rd(mass_steel-displaced_wood),
          "all8_backing_pads_with_plate_kg_ignore_holes":rd(wood["eight_pad_baseline_volume_L"]*wood["wood_density_assumed_kg_m3"]/1000+mass_steel-displaced_wood),
          "retention_wood_engagement_from_16mm_screw_mm":rd(wood_screw_engagement),
          "retention_wood_end_margin_to_MDF_glue_face_mm":rd(wood_left-wood_screw_engagement),
          "external_pad_depth_envelope_still_20mm_if_all_heads_flush":True,
          "static_bare_pad_K02_obstacle_equivalence_is_conditional":True
        })
        assert wood_left-wood_screw_engagement==wood["pad_depth_mm"]-fastener["under_head_length_mm"]==4
    assembly=[]
    for t in pl["plate_thickness_scenarios_mm"]:
        wood_left=wood["pad_depth_mm"]-t
        for g in screw["gasket_compressed_thickness_mm"]:
            first_thread=b["flange_thickness_mm"]+g+wood["MDF_front_mm"]+wood_left+screw["head_washer_underhead_extra_mm"]
            rear_face=b["flange_thickness_mm"]+g+wood["MDF_front_mm"]+wood["pad_depth_mm"]+screw["head_washer_underhead_extra_mm"]
            for L in screw["under_head_length_options_mm"]:
                raw=L-first_thread
                e=max(0.,min(t,raw))
                projection=max(0.,L-rear_face)
                assembly.append({
                   "plate_t_mm":t,"compressed_gasket_mm":g,"bolt_underhead_L_mm":L,
                   "thread_start_behind_screw_head_mm":rd(first_thread),
                   "plate_rear_face_behind_screw_head_mm":rd(rear_face),
                   "idealized_axial_thread_engagement_mm":rd(e),
                   "ratio_engagement_to_M5_d":rd(e/major),
                   "uncovered_threaded_plate_mm":rd(t-e),
                   "bolt_rear_protrusion_beyond_pad_mm":rd(projection),
                   "conditional_1d_screen_and_zero_rear_projection":e>=major-1e-8 and projection<=1e-8 and raw>0,
                   "note":"Nominal flat solid stack only; no screw lead-in/runout or real gasket tolerance, NO strength sign-off."
                })
    assert len(assembly)==45
    preferred=screw["preferred_comparison"]
    selected=next(x for x in assembly if x["plate_t_mm"]==preferred["plate_mm"] and x["compressed_gasket_mm"]==preferred["compressed_gasket_mm"] and x["bolt_underhead_L_mm"]==preferred["screw_underhead_length_mm"])
    assert selected["idealized_axial_thread_engagement_mm"]==5.5
    assert selected["bolt_rear_protrusion_beyond_pad_mm"]==0
    assert selected["conditional_1d_screen_and_zero_rear_projection"]
    # Reference P40A may have axial, tangential and moment components.
    # The equal split below is not a model of wood or glue joint strength.
    test_items=[
       {"check":"retention screws in 14mm wood left behind 6mm steel", "catalog_and_wood_pullout_verified":False},
       {"check":"steel plate thread stripping and fastener fatigue", "actual_joint_strength_verified":False},
       {"check":"pad glue face and MDF thin web under variable shear/peel", "joint_strength_verified":False},
       {"check":"pre-install plates before pad is bonded inside closed cabinet", "real_assembly_access_verified":False},
       {"check":"20 module delivery 0deg / 180deg with new plate retention", "full_3D_path_reverified":False},
       {"check":"captured plate repair after M5 thread is stripped", "service_repair_verified":False}
    ]
    return {
      "study":"K13","status":"CONCEPTUAL NO-CNC SCREEN; ZERO MANUFACTURING OR STRENGTH QUALIFICATIONS",
      "sources":s["sources"],
      "manufacturer_dimensions_not_wood_holes":b,
      "position_and_margin_screen":geometry,
      "materials":{
        "wood":"laminated beech pad candidate, actual density/shear/pullout UNKNOWN",
        "steel":"S235JR candidate with manufacturer-reported minimum yield 235 MPa, BUT thread strip and plated joint unverified",
        "steel_density_assumption_kg_m3":pl["steel_density_assumed_kg_m3"],
        "wood_density_assumption_kg_m3":wood["wood_density_assumed_kg_m3"],
        "MDF_front":"44mm MDF reference, source actual lot and face delamination unknown",
        "retention_screws":"two nominal 3mm wood-screw examples per plate, NO approved SKU",
        "fastener":"M5 ISO4762 head OD8.5, front MDF clearance 5.5, metal basket hole 6.5; NO approved bolt length"
      },
      "recessed_steel_plate_scenarios":variants,
      "axial_45_combinations":assembly,
      "illustrative_preferred_6mm_plate_1mm_gasket_M5x75":selected,
      "P40A_reference_load":{
        "one_mount_force_N":load["P40A_reference_bolt_reaction_N"],
        "two_retainer_screws_equal_share_IF_TRUE_N":load["illustrative_equal_split_between_two_retention_screws_only_N"],
        "actual_load_path_known":False,
        "material_capacity_approved":False
      },
      "unresolved_checks":test_items,
      "conditional_decision":"A flush steel plate tapped M5, held inside 20mm pad, has 2.1mm nominal steel web and need not protrude into the K02 insertion AABB for gasket 1mm / M5x75 / 6mm plate. This only repairs nominal local geometry, NOT real fatigue, strength, access, MDF edge, or acoustic service.",
      "cnc":"HOLD"
    }

def main():
    x=compute()
    OUT.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("K13: steel tapped M5 in 20mm pad; 5 plates, 45 axial variants; no CNC")
    print("Radial metal to edge",x["position_and_margin_screen"]["plate_inner_metal_ligament_to_M5_major_thread_mm"],"mm")
    print("M5x75 with 1mm gasket in 6mm steel:",x["illustrative_preferred_6mm_plate_1mm_gasket_M5x75"]["idealized_axial_thread_engagement_mm"],"mm")
    print("Added mass all8",next(a for a in x["recessed_steel_plate_scenarios"] if a["plate_thickness_mm"]==6)["net_mass_delta_all8_kg"],"kg")
if __name__=="__main__":main()
