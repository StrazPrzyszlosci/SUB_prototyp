#!/usr/bin/env python3
"""K13: analytical, source-bound conditional metal bridge in original K02 pad envelope.

No physical FEM/contact, actual assembly sequence, measured joint strength,
production material grade, or real tool envelope. All components of proposed
bridge are tested against the coarse 20 mm original K02 pad footprint.
"""
from pathlib import Path
import json, math, sys

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/"dane"/"k13_nośnik_mostek_i_dwie_kotwy.json"
OUTPUT = ROOT/"wyniki"/"k13_dwa_odlegle_zakotwienia_podsumowanie.json"

def R(x): return round(x, 6)

def compute():
    d=json.loads(INPUT.read_text(encoding="utf-8"))
    g=d["geometry_mm"]
    tests=d["assumed_screens"]
    rcut=g["cutout_radius"]; bolt=g["basket_mount_radius"]
    ri=g["pad_inner_radius"]; ro=g["pad_outer_radius"]
    w=g["pad_tangential_width"]; depth=g["pad_rear_depth"]
    insert_od=g["anchor_insert_OD"]; ranchor=g["two_anchor_radius"]
    tangent=sorted(g["tangential_offsets"])
    assert len(tangent)==2 and tangent==[-10,10]
    assert (bolt-rcut,bolt-ri)==(6.099999999999994,5.099999999999994) or all(abs(a-b)<1e-9 for a,b in ((bolt-rcut,6.1),(bolt-ri,5.1)))
    assert (ri,ro,w,depth)==(178.9,205,36,20)
    assert g["steel_bridge_thickness"]+g["wood_pad_depth_behind_bridge"]==depth
    metal=g["steel_bridge_thickness"]
    wood=g["wood_pad_depth_behind_bridge"]
    nut_max_across_corners = 2*g["hex_nut_M5_across_flats_max"]/math.sqrt(3)
    # ISO4032 max AF8 => ideal hex max vertex-vertex diameter 9.2376.
    metal_inner_gap=g["steel_bridge_radial_inner"]-rcut
    wall_gap=g["speaker_center_x"]-ro-g["left_interior_wall_x"]
    pad_lig_one=bolt-ri-insert_od/2
    radius_anchor=insert_od/2
    margins={
        "pad_inner_mm":R(ranchor-ri-radius_anchor),
        "pad_outer_mm":R(ro-ranchor-radius_anchor),
        "pad_tangent_mm":R(w/2-max(abs(t) for t in tangent)-radius_anchor),
        "left_wall_anchor_mm":R(g["speaker_center_x"]-ranchor-radius_anchor-g["left_interior_wall_x"]),
        "left_wall_full_pad_mm":R(wall_gap),
        "steel_inner_to_cutout_mm":R(metal_inner_gap),
        "central_M5_nut_to_pad_inner_mm":R(bolt-ri-nut_max_across_corners/2),
        "central_M5_nut_projected_to_cutout_mm":R(bolt-rcut-nut_max_across_corners/2),
        "front_M5_screw_hole_to_cutout_mm":R(bolt-rcut-g["screw_front_clearance_diameter_example"]/2)
    }
    assert margins["pad_inner_mm"]==12.1
    assert margins["pad_outer_mm"]==4
    assert margins["pad_tangent_mm"]==3
    assert margins["left_wall_anchor_mm"]==8
    assert margins["left_wall_full_pad_mm"]==4
    assert margins["steel_inner_to_cutout_mm"]==1
    assert margins["front_M5_screw_hole_to_cutout_mm"]==3.35
    assert 0<margins["central_M5_nut_to_pad_inner_mm"]<.5
    assert margins["central_M5_nut_projected_to_cutout_mm"]>1

    # The 8 pads are 45-deg rotated copies; a local r,t rectangle is
    # conserved under all eight rigid rotations.
    source_pad={'ri':ri,'ro':ro,'half_tangent':w/2,'rear_depth':depth}
    proposed_parts=[
      {'name':'steel_3mm','ri':g["steel_bridge_radial_inner"],
        'ro':g["steel_bridge_radial_outer"],
        'half_tangent':g["steel_bridge_tangential_width"]/2,
        'y_min':0.,'y_max':metal},
      {'name':'wood_17mm','ri':ri,'ro':ro,'half_tangent':w/2,
        'y_min':metal,'y_max':depth},
      {'name':'nut_M5_max_corner_envelope','ri':bolt-nut_max_across_corners/2,
        'ro':bolt+nut_max_across_corners/2,
        'half_tangent':nut_max_across_corners/2,
        'y_min':metal,'y_max':metal+g["hex_nut_M5_height_max"]}
    ]
    for t in tangent:
      proposed_parts.append({
        'name':'anchor_insert_OD10_t'+str(t),
        'ri':ranchor-radius_anchor,'ro':ranchor+radius_anchor,
        'half_tangent':abs(t)+radius_anchor,
        'y_min':metal,'y_max':metal+g["anchor_insert_length"]
      })
    contained=all(p['ri']>=ri-1e-9 and p['ro']<=ro+1e-9 and
        p['half_tangent']<=w/2+1e-9 and p['y_min']>=0 and
        p['y_max']<=depth+1e-9 for p in proposed_parts)
    assert contained
    anchor_centers_gap=abs(tangent[1]-tangent[0])-insert_od
    anchor_to_nut_dist=math.hypot(ranchor-bolt,abs(tangent[1]))
    min_gap=anchor_to_nut_dist-(insert_od+nut_max_across_corners)/2
    assert anchor_centers_gap==10 and min_gap>6

    # K02 geometry in x,z,y is a superset. Positive 20/20 route on the
    # parent obstacle survives subset replacements in that surrogate.
    # NOT a physical construction or routing test for tools + hardware.
    sys.path.insert(0,str(ROOT/"skrypty"))
    import k01_mocowanie_bilans as k01
    k01_ref=k01.evaluate(231,ri,ro,w,depth,2)
    assert k01_ref["pass_surrogate"]
    assert k01_ref["left_wall_clearance_mm"]==4
    assert abs(k01_ref["block_total_displacement_L"]-0.150336)<1e-8

    envelopes=[]
    for err in tests["center_positional_error_mm"]:
        reduced={
          "wood_pad_outer":R(margins["pad_outer_mm"]-err),
          "wood_pad_tangent":R(margins["pad_tangent_mm"]-err),
          "wood_pad_inner":R(margins["pad_inner_mm"]-err),
          "direct_wood_inner":R(pad_lig_one-err)
        }
        envelopes.append({
          "worst_axis_error_mm":err,
          "two_remote_anchor_min_web_mm":min(reduced.values()),
          "two_remote_wood_anchors_pass_arbitrary_2mm_screen":
            min(reduced[k] for k in ("wood_pad_inner","wood_pad_outer","wood_pad_tangent"))>=tests["wood_edge_min"]-1e-9,
          "direct_insert_at_basket_axis_pass_arbitrary_2mm_screen":
            reduced["direct_wood_inner"]>=tests["wood_edge_min"]-1e-9,
          "margins_after_error_mm":reduced
        })
    assert [x["two_remote_wood_anchors_pass_arbitrary_2mm_screen"] for x in envelopes]==[True,True,True]
    assert not any(x["direct_insert_at_basket_axis_pass_arbitrary_2mm_screen"] for x in envelopes)

    # Within original cutout-clearance restriction ri >= 177.9+1=178.9.
    # To get 2-mm wood web around OD10 at r184 requires ri <=177.0;
    # insertion and basket footprint no longer inherited.
    r_required = bolt-insert_od/2-tests["wood_edge_min"]
    gap_to_cutout=R(r_required-rcut)
    assert gap_to_cutout==-0.9

    mass={
      "8_baseline_wood_pad_volume_L":R(8*(ro-ri)*w*depth/1e6),
      "8_steel_plate_volume_L":R(8*(ro-ri)*w*metal/1e6),
      "8_wood_section_volume_L_before_nut_reliefs":R(8*(ro-ri)*w*wood/1e6),
      "reference_steel_density_kg_m3":7850,
      "reference_wood_density_kg_m3":700
    }
    mass["8_steel_kg"]=R(mass["8_steel_plate_volume_L"]*7.85)
    mass["8_wood_kg_before_reliefs"]=R(mass["8_wood_section_volume_L_before_nut_reliefs"]*.7)
    mass["8_stacked_steel_and_wood_kg_excluding_fasteners_adhesive_pockets"]=R(mass["8_steel_kg"]+mass["8_wood_kg_before_reliefs"])
    mass["8_all_wood_20mm_kg_at_700"]=R(mass["8_baseline_wood_pad_volume_L"]*.7)
    assert mass["8_baseline_wood_pad_volume_L"]==.150336
    assert mass["8_steel_plate_volume_L"]==.02255 or abs(mass["8_steel_plate_volume_L"]-.0225504)<1e-7

    F=tests["load_single_fastener_proxy_N"]
    arm=ranchor-bolt
    b=tests["steel_beam_effective_width_mm"]
    # Sigma=6FL/(b*t^2) for a full rectangular strip, very coarse
    # cantilever force proxy. Neither plate perforation nor actual force
    # transfer / contact is represented. Never compare to a safe allowable.
    stress=[{"plate_t_mm":t,"full_force_151N_and_12mm_arm_rectangular_beam_proxy_MPa":R(6*F*arm/(b*t*t))}
             for t in tests["steel_plate_thickness_candidates_mm"]]
    assert stress==[
       {"plate_t_mm":2,"full_force_151N_and_12mm_arm_rectangular_beam_proxy_MPa":135.9},
       {"plate_t_mm":3,"full_force_151N_and_12mm_arm_rectangular_beam_proxy_MPa":60.4},
       {"plate_t_mm":4,"full_force_151N_and_12mm_arm_rectangular_beam_proxy_MPa":33.975}
    ]
    # Basket metal flange hole is still the manufacturer's Ø6.5:
    # our M5 shank front-clearance Ø5.5 isn't derived from it.
    result={
       "study":"K13","design_status":"PARAMETRIC SCREEN ONLY / NOT CNC",
       "references":d["references"],"geometry":g,
       "readable_result":{
          "direct_M5_insert_OD10_inner_web_mm":R(pad_lig_one),
          "requires_pad_ri_for_2mm_web_mm":R(r_required),
          "intrusion_into_basket_cutout_projection_mm":R(max(0,-gap_to_cutout)),
          "existing_pad_nominal_inner_edge_to_basket_cutout_mm":R(ri-rcut),
          "two_remote_M5_OD10_anchor_positions_r_t_mm":[[ranchor,t] for t in tangent],
          "margins_nominal_mm":margins,
          "bridge_parts_wholly_contained_in_K02_20mm_pad_AABB":contained,
          "monotonic_K02_path_claim":"In original simplified K02 obstacle model, replacing each 20mm pad with solids strictly inside its envelope cannot newly block an already collision-free module route. Actual hardware, tools, basket and service NOT validated.",
          "two_anchor_separation_minus_OD_mm":R(anchor_centers_gap),
          "nearest_anchor_to_captured_nut_envelope_clearance_mm":R(min_gap),
          "steel_plate_geometry_mm":{"radial_span":R(ro-ri),"tangential_width":w,"thickness":metal},
          "wood_behind_plate_thickness_mm":wood,
          "nut_pocket_rim_in_wood_is_THIN_and_must_not_be_load_bearing":True,
          "nut_positional_error_not_qualified":True
       },
       "wood_insert_edge_sensitivity":envelopes,
       "mass_volumes_as_before_NUT_pocket":mass,
       "metal_strip_simple_bending_only":stress,
       "connection_3_path_notes":{
          "basket_factory_hole_mm":g["basket_hole_diameter"],
          "front_MDF_through_hole_for_M5_example_mm":g["screw_front_clearance_diameter_example"],
          "M5_threaded_in_captive_rear_nut_NOT_in_3mm_plate":True,
          "rear_M5x12_RAMPA_wood_pilot_requires_material_specific_CATALOG":True,
          "nut_anti_loss_requires_POSITIVE_attachment":True
       },
       "new_material_BOM":[
          {"part":"8 metal bridges","material_candidate":"steel S235 or equivalent characterized sheet, 3mm scenario, NOT selected"},
          {"part":"8 rear wooden pads","material_candidate":"characterized glued beech or birch plywood 17mm actual board, NOT selected"},
          {"part":"8 captive M5 nuts","material_candidate":"ISO4032 reference geometry only, positively restrained, NOT selected"},
          {"part":"16 wood insert anchors","material_candidate":"RAMPA SKD30 M5 OD10 length12 reference, not transferred capacity"},
          {"part":"16 bridge-to-pad screws","material_candidate":"M5 bolts, heads and assembly access unverified"},
          {"part":"8 driver screws","material_candidate":"M5 bolts, length/preload unresolved, front hole example Ø5.5"}
       ],
       "limits":[
         "2mm web and errors 0/0.5/1mm are screen hypotheses, NOT material strength or production tolerances",
         "K02 volume/path inheritance is valid only while every obstruction remains within original K02 pad envelope",
         "Central nut and plate, antirotation, insertion tooling, glue interfaces and loads not physically or 3D validated",
         "Nominal nut OD from regular ideal hex AF8; actual tolerances, washer, weld/retainer envelope not included",
         "Raw 151N plate stress is one crude beam proxy, NOT strength calculation for perforated bridge/2-anchor assembly",
         "Unknown K07 0deg ID16/180deg tool access, actual full basket, vent clearance, leakage, fatigue, thermals",
         "All hardware and panel materials are candidates only; retained CNC HOLD"
       ]
    }
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return result

if __name__=="__main__":
    d=compute()
    print("K13", json.dumps({
       "direct_wood_web_mm":d["readable_result"]["direct_M5_insert_OD10_inner_web_mm"],
       "two_anchor_wood_margins_mm":d["readable_result"]["margins_nominal_mm"],
       "nested_K02":d["readable_result"]["bridge_parts_wholly_contained_in_K02_20mm_pad_AABB"],
       "mass_8_bridges_plus_wood_kg":d["mass_volumes_as_before_NUT_pocket"]["8_stacked_steel_and_wood_kg_excluding_fasteners_adhesive_pockets"],
       "CNC":"HOLD"
    },ensure_ascii=False))
