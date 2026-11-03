#!/usr/bin/env python3
"""K11: real catalog OD and K01 pad ligaments; independently varied shell materials.

Pure Python stdlib; uses source-bound catalog records and existing K10 register.
No pull-out capacity, glue strength, insert assembly torque, or acoustic outcome
is inferred from catalog diameters. P30E wall change is a fixed-outer-size
PERTURBATION ONLY: old braces, modules, mat and fasteners are not re-routed.
"""
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"dane"/"k11_źródłowe_wkładki_i_warianty_skrzyni.json"
K10=ROOT/"dane"/"k10_rejestr_materialow_czesci_obudowy.json"
OUT=ROOT/"wyniki"/"k11_przesiew_materialow_i_wkladek.json"

def r(x):
    return round(x, 6)

def run():
    src=json.loads(SOURCE.read_text(encoding="utf-8"))
    roles=json.loads(K10.read_text(encoding="utf-8"))["parts"]
    assert len(roles)==35
    focus=[p["id"] for p in roles if p["id"] in [f"E{i:02d}" for i in range(1,11)] + ["E18","E19","E22"]]
    assert len(focus)==13 and len(set(focus))==13

    geo=src["geometry"]
    x_bolt=geo["mount_axis_radius_mm"]
    r_cut=geo["driver_cutout_d_mm"]/2
    pad=next(p for p in src["independent_pad_variants"] if p["id"]=="K01_baseline")
    assert (x_bolt,r_cut,pad["ri_mm"],pad["ro_mm"],pad["tangent_mm"],pad["depth_mm"]) == (184.,177.9,178.9,205.,36.,20.)
    minwood=geo["user_defined_screen_radial_ligament_mm"]
    assert minwood==2.0

    ins=[]
    for p in src["insert_catalog_examples"]:
        d=p["outer_diameter_mm"]
        pad_lig=x_bolt-pad["ri_mm"]-d/2
        front_lig=x_bolt-r_cut-d/2
        drill=p.get("predrill_mm")
        ins.append({
           "id":p["id"],"internal_thread":p["internal_thread"],
           "manufacturer":p["manufacturer"],"manufacturer_source":src["sources"][p["source"]],
           "outer_diameter_mm":d,"length_mm":p["length_mm"],
           "pad_radial_inner_ligament_mm":r(pad_lig),
           "front_cutout_radial_ligament_mm":r(front_lig),
           "pad_radial_outer_ligament_mm":r(pad["ro_mm"]-x_bolt-d/2),
           "nominal_depth_fit_20mm":p["length_mm"]<=pad["depth_mm"],
           "remaining_length_20mm_mm":r(pad["depth_mm"]-p["length_mm"]),
           "predrill_diameter_mm":drill,
           "pad_predrill_inner_ligament_mm":r(x_bolt-pad["ri_mm"]-drill/2) if drill is not None else None,
           "geometry_screen_both_ligaments_at_least_2mm":pad_lig>=minwood-1e-9 and front_lig>=minwood-1e-9,
           "geometry_intersects_pad_inner_boundary":pad_lig<0,
           "is_pullout_strength_qualified":False,
           "manufacturer_board_conditions_transferable_to_20mm_pad":False
        })
    assert len(ins)==6
    assert [x["pad_radial_inner_ligament_mm"] for x in ins[:3]]==[1.1,0.1,-0.9]
    assert not any(x["geometry_screen_both_ligaments_at_least_2mm"] for x in ins)
    assert ins[2]["geometry_intersects_pad_inner_boundary"]
    limit_for_2mm=2*(x_bolt-pad["ri_mm"]-minwood)
    assert abs(limit_for_2mm-6.2)<1e-9
    pad_variants=[]
    load=src["load_screen"]["one_mount_reference_force_N"]
    lever=src["load_screen"]["lever_for_hypothetical_bond_rotation_mm"]
    for p in src["independent_pad_variants"]:
        radial=p["ro_mm"]-p["ri_mm"]
        width=p["tangent_mm"]
        depth=p["depth_mm"]
        area=radial*width
        moment=load*lever
        pad_variants.append({
           "id":p["id"],"inner_cutout_gap_mm":r(p["ri_mm"]-r_cut),
           "radial_span_mm":r(radial),"tangential_width_mm":width,"depth_mm":depth,
           "glue_face_area_mm2":r(area),
           "8_pad_volume_l":r(8*area*depth/1e6),
           "maximum_catalog_OD_for_2mm_inner_web_mm":r(2*(x_bolt-p["ri_mm"]-minwood)),
           "nominal_inner_web_for_M5_OD10_mm":r(x_bolt-p["ri_mm"]-5.0),
           "reference_151N_full_face_shear_proxy_MPa":r(load/area),
           "reference_bending_moment_151N_x_20mm_Nmm":r(moment),
           "reference_ideal_linear_peel_proxy_radial_axis_MPa":r(6*moment/(width*radial**2)),
           "reference_ideal_linear_peel_proxy_tangential_axis_MPa":r(6*moment/(radial*width**2)),
           "note":"F=151N from P40A is an assumed bolt reaction NOT a pad bond traction; shear/peel proxies use full nominal glued face, rectangular linear stress, no strength allowables or load path qualification"
        })
    assert pad_variants[0]["glue_face_area_mm2"]==939.6
    assert pad_variants[1]["nominal_inner_web_for_M5_OD10_mm"]==0.1
    assert pad_variants[2]["nominal_inner_web_for_M5_OD10_mm"]==0.1
    assert pad_variants[3]["nominal_inner_web_for_M5_OD10_mm"]==1.0
    assert pad_variants[4]["nominal_inner_web_for_M5_OD10_mm"]==0.1

    W,depth,H=geo["outer_mm"]
    front=geo["front_mm"]
    front_net_vol_l=(W*H-math.pi*r_cut**2)*front/1e6
    def shell_case(t,rho,E,nu):
        cavity=(W-2*t)*(depth-front-t)*(H-2*t)/1e6
        nonfront=(W*H*(depth-front)-(W-2*t)*(depth-front-t)*(H-2*t))/1e6
        shell=front_net_vol_l+nonfront
        # Constant braces retained from K10; this is NOT a refit of layout.
        braces_vol_l=1.60908
        mass=front_net_vol_l*730/1000+nonfront*rho/1000+braces_vol_l*730/1000
        flex=E*1e9*(t/1000)**3/(12*(1-nu**2)) if E is not None and nu is not None else None
        return cavity, nonfront, shell, mass, flex
    baseline=shell_case(22,730,2.1,.3)
    assert abs(baseline[2]-52.6001338564)<1e-8
    ref_flex=baseline[4]
    wall=[]
    for p in src["wall_scenarios"]:
        t,rho=p["thickness_mm"],p["rho_kg_m3"]
        c,other,s,m,fl=shell_case(t,rho,p["E_bending_GPa"],p["nu_screen"])
        wall.append({
           "id":p["id"],"wall_thickness_mm":t,
           "cavity_gross_l":r(c),
           "gross_cavity_delta_vs_MDF22_l":r(c-baseline[0]),
           "nonfront_wood_volume_l":r(other),
           "front_fixed_MDF44_wood_volume_l":r(front_net_vol_l),
           "total_shell_wood_volume_l":r(s),
           "front_plus_nonfront_wall_plus_original_MDF22_braces_mass_kg":r(m),
           "fixed_structure_mass_delta_vs_MDF22_kg":r(m-baseline[3]),
           "reference_isotropic_wall_bending_rigidity_ratio":r(fl/ref_flex) if fl is not None else None,
           "physical_module_route_or_net_litres_verified":False,
           "limitations":"Front MDF44 fixed, all five other panels homogeneous t; braces kept nominal MDF22 and old coordinates, true joints/refit, 20 insert paths, net volume, acoustic pressure and FEM NOT recalculated"
        })
    assert len(wall)==3
    assert wall[0]["gross_cavity_delta_vs_MDF22_l"]==0
    assert wall[1]["gross_cavity_delta_vs_MDF22_l"]<0
    assert wall[2]["gross_cavity_delta_vs_MDF22_l"]>0

    result={
      "study":"K11", "date":"2026-11-03",
      "status":"SCREEN ONLY — NO CONSTRUCTION MATERIAL, BOLT OR MDF INSERT QUALIFIED; CNC HOLD",
      "sources":src["sources"],"K10_covered_roles":focus,
      "interpretation":"K11 narrows real insert/wood ligament feasibility and independent wall material volume/mass. It does NOT predict actual 100/120/150L or load capacity.",
      "insert_screener":{
         "pads_K01_baseline":pad,
         "cutout_radius_mm":r_cut,
         "bolt_axis_radius_mm":x_bolt,
         "user_screen_2mm_is_NOT_a_strength_rule":True,
         "max_outer_insert_diameter_for_2mm_inner_pad_ligament_mm":r(limit_for_2mm),
         "catalog_examples":ins
      },
      "pad_variants":pad_variants,
      "wall_substitution_with_outer_size_fixed":{
         "reference":"P30E 1020×425×500; front MDF44 constant; original braces unchanged",
         "baseline_front_net_volume_l":r(front_net_vol_l),
         "scenarios":wall,
         "gross_change_is_not_net_change":True
      },
      "decisions":{
         "top_priority":"Do NOT freeze 8 glued pad concept merely by picking harder wood. Real M5 OD10 leaves 0.1mm K01 inner pad web and M6 OD12 breaches original pad contour.",
         "path_A":"Test redesign of local force path / insert positioning with full material and ligament criteria; preserve basket PCD",
         "path_B":"Compare captive T-nut/hurricane and load-spreading backing adapter (no detached loose nut); study position at 0° and 180°",
         "wall_material":"Keep MDF22 reference for now; 25mm MDF sacrifices cavity gross volume, birch21 changes geometry and anisotropy. Neither qualifies shell or seams.",
         "next":"Catalogue-specific insert/countersink/fastening 3D and tolerances, then model full K02/K07 entry + P33C-safe FEM and bonded coupons; no material approved"
      }
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("K11: catalog 6, pad variants 5, wall 3; 0/6 insert cases meet hypothetical 2mm screen; CNC HOLD")
    print(json.dumps({"M5_OD10_pad_inner_web_mm":ins[1]["pad_radial_inner_ligament_mm"],
      "M6_OD12_pad_inner_web_mm":ins[2]["pad_radial_inner_ligament_mm"],
      "wall_gross_deltas_L":{p["id"]:p["gross_cavity_delta_vs_MDF22_l"] for p in wall}},ensure_ascii=False))

if __name__=="__main__":
    run()
