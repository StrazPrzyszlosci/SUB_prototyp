#!/usr/bin/env python3
"""K14: demonstrate K13 20mm-pad geometry bottleneck, eccentric compression
and tolerance/preload sensitivity using simple independent closed-form checks.

NO materials allowables, NO S235JR/thread stripping certification, NO CAD/FEA.
Preload examples use NASA T/(K*d) as a rough equation, NOT an approved torque.
P40 vector resultant 151.11N ≠ axial normal component 119.92N.
"""
from pathlib import Path
from itertools import product
import json, math

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"dane"/"k14_scieranie_styku_tolerancje_i_docisk.json"
K13=ROOT/"dane"/"k13_plytka_m5_w_klocku20_zalozenia.json"
OUT=ROOT/"wyniki"/"k14_docisk_tolerancje_64.json"

def rd(v): return round(float(v),6)

def radial_contact(plate_inner,outer,axis,width,F):
    """Rigid no-tension linear radial pressure model: NOT physical 3D contact.

    With force eccentric outside b/6, compressive triangular strip spans c,
    its resultant at c/3 from the loaded edge, and pmax=2F/(c*width).
    """
    b=outer-plate_inner
    e=axis-(plate_inner+outer)/2
    assert F>=0 and plate_inner<axis<outer and width>0
    if abs(e)<=b/6:
        a=b
        mean=F/(b*width)
        peak=mean*(1+6*abs(e)/b)
        mode="full_linear"
    else:
        a=3*(axis-plate_inner if e<0 else outer-axis)
        assert 0<a<b
        peak=2*F/(a*width)
        mode="partial_triangular"
        assert abs((a*width*peak/2)-F)<1e-8
        assert abs((plate_inner+a/3 if e<0 else outer-a/3)-axis)<1e-10
    return {"mode":mode,"span_mm":rd(a),"full_face_average_MPa_ignoring_holes":rd(F/(b*width)),
            "ideal_contact_pmax_MPa_ignoring_holes":rd(peak),
            "pressure_peak_over_full_average":rd(peak/(F/(b*width))) if F else None}

def compute():
    inp=json.loads(SRC.read_text(encoding="utf8"))
    src=json.loads(K13.read_text(encoding="utf8"))
    g=inp["research_model"];m=src["manufacturer_dayton"]
    pad=src["wood_and_pad"];pl=src["recessed_plate"]
    assert (g["axis_radius_mm"],g["pad_inner_radius_mm"],g["plate_outer_radius_mm"]) == (184,178.9,204.5)
    assert (m["mount_pcd_d_mm"]/2,src["recessed_plate"]["M5_coarse_thread_major_d_mm"]) == (184,5)
    axis=g["axis_radius_mm"];ri=g["pad_inner_radius_mm"];ro=g["plate_outer_radius_mm"]
    rthread=g["metal_thread_major_d_mm"]/2
    width=g["assumed_retaining_plate_tangential_width_mm"]
    available=axis-ri-rthread
    assert abs(available-2.6)<1e-9
    assert abs((axis-m["basket_cutout_d_mm"]/2-rthread)-3.6)<1e-9
    reference_axial=g["reference_P40_resolved_axial_max_N"]
    web=[]
    for wood_lip in g["example_inner_wood_pocket_lips_mm"]:
        plate_inner=ri+wood_lip
        steel_lip=axis-plate_inner-rthread
        pressures={str(F):radial_contact(plate_inner,ro,axis,width,F) for F in g["force_probe_axial_N"]}
        web.append({
         "wood_pocket_inner_lip_mm":rd(wood_lip),
         "steel_thread_inner_lip_mm":rd(steel_lip),
         "two_2mm_hypothesis_passed":wood_lip>=g["illustrative_separate_web_screen_mm"] and steel_lip>=g["illustrative_separate_web_screen_mm"],
         "plate_inner_edge_radial_mm":rd(plate_inner),
         "plate_radial_span_mm":rd(ro-plate_inner),
         "axial_contact_indicators":pressures
        })
    assert len(web)==6
    assert web[1]["steel_thread_inner_lip_mm"]==2.1
    assert web[3]["steel_thread_inner_lip_mm"]==1.3
    assert not any(x["two_2mm_hypothesis_passed"] for x in web)

    torque=[]
    for T,K in product(inp["torque_probes"]["Nm"],inp["torque_probes"]["K"]):
        F=T/(K*inp["torque_probes"]["bolt_d_m"])
        torque.append({"illustrative_torque_Nm":T,"hypothetical_K":K,
          "axial_preload_N_from_T_over_Kd_NOT_prescribed":rd(F),
          "ratio_to_P40A_axial_external_119_92":rd(F/reference_axial),
          "peak_MPa_nominal_K13_rigid_no_tension":radial_contact(ri+0.5,ro,axis,width,F)["ideal_contact_pmax_MPa_ignoring_holes"]})
    assert len(torque)==12

    nominal=inp["tolerance_probe"]["nominal_mm"]
    errors=inp["tolerance_probe"]["perturbation_plus_minus_mm"]
    keys=list(nominal)
    assert set(keys)==set(errors) and len(keys)==6
    combinations=[]
    for directions in product((-1,1),repeat=len(keys)):
        v={k:nominal[k]+directions[i]*errors[k] for i,k in enumerate(keys)}
        start=v["flange"]+v["gasket_compressed"]+v["front"]+v["pad"]-v["plate"]
        rear=v["flange"]+v["gasket_compressed"]+v["front"]+v["pad"]
        engaged=max(0,min(v["plate"],v["bolt_L"]-start))
        protrudes=max(0,v["bolt_L"]-rear)
        combinations.append({"signs":"".join("-" if d<0 else "+" for d in directions),
             "ideal_thread_engagement_mm":rd(engaged),
             "rear_protrusion_mm":rd(protrudes),
             "hypothetical_5mm_engagement_no_rear_projection":engaged>=5-1e-8 and protrudes<=1e-8})
    assert len(combinations)==64
    pass_cnt=sum(c["hypothetical_5mm_engagement_no_rear_projection"] for c in combinations)
    assert pass_cnt==24
    assert min(c["ideal_thread_engagement_mm"] for c in combinations)==3.3
    assert max(c["rear_protrusion_mm"] for c in combinations)==1.5

    pocket=[]
    for delta in inp["pocket_tolerance_probe"]["error_mm_each_independently"]:
        pocket.append({"assumed_independent_adverse_each_mm":delta,
          "0_5mm_nominal_pocket_wood_lip_worst_mm":rd(0.5-2*delta),
          "2_1mm_nominal_steel_web_worst_mm":rd(2.1-2*delta),
          "wood_lip_positive_all_adverse_cases":0.5-2*delta>0})
    clearance=(g["hole_d_mm"]["wood_screw_clearance_front"]-g["metal_thread_major_d_mm"])/2
    registration=[]
    for err in inp["coaxiality_screen"]["x_z_center_offsets_each_mm"]:
        radial=math.hypot(err,err)
        registration.append({"example_axis_error_each_x_z_mm":err,"combined_radial_mm":rd(radial),
          "nominal_front_screw_radial_clearance_mm":rd(clearance),
          "passes_nominal_clearance_in_2D":radial<=clearance+1e-9,
          "threaded_plate_coaxiality_and_3D_tool_access_verified":False})
    assert clearance==.25

    return {
      "study":"K14","date":inp["date"],
      "status":"UNCALIBRATED RIGID PLATE / SYNTHETIC TOLERANCE AND PRELOAD SCREENS — CNC HOLD",
      "sources":inp["sources"],
      "key_conservation":{"axis_to_pad_inner_mm":rd(axis-ri),
         "M5_major_thread_radius_mm":rd(rthread),
         "total_wood_plus_steel_radial_lip_budget_mm":rd(available),
         "maximum_equal_wood_and_steel_lips_mm":rd(available/2),
         "total_available_even_if_pad_touches_factory_cutout_mm":rd(axis-m["basket_cutout_d_mm"]/2-rthread),
         "two_2mm_lips_with_original_geometry_possible":False,
         "two_2mm_lips_if_pad_inner_at_cutout_possible":False,
         "wood_lip_at_K13_mm":0.5,"steel_lip_at_K13_mm":2.1,
         "criterion_2mm_is_a_hypothetical_screen_NOT_safety_standard":True},
      "P40A_force_decomposition":{"original_resultant_N":g["reference_P40_resultant_N"],
         "original_axial_component_max_N":reference_axial,
         "original_shear_component_N":g["reference_P40_shear_component_N"],
         "151_11N_is_not_axial_preload":True,
         "axial_component_still_is_ideal_model_and_not_clamp_force":True},
      "contact_model":g["rectangular_rigid_plate_one_dimensional_model"],
      "pocket_lip_pressure_comparisons":web,
      "torque_is_NOT_a_recommended_procedure":inp["torque_probes"]["warning"],
      "torque_scenarios":torque,
      "worst_case_synthetic_axial_stack":{
        "source_assumptions":inp["tolerance_probe"],
        "dimension_order":keys,
        "combinations":combinations,
        "tested_independent_endpoint_cases":64,
        "cases_meeting_only_K13_hypothetical_1xM5_zero_protrusion_screen":pass_cnt,
        "min_engagement_mm":min(c["ideal_thread_engagement_mm"] for c in combinations),
        "max_rear_protrusion_mm":max(c["rear_protrusion_mm"] for c in combinations),
        "nominal_K13_75mm_is_robust_under_these_synthetic_intervals":False},
      "nominal_pocket_edge_adverse_tolerances":pocket,
      "front_M5_wood_hole_vs_axis_registration":registration,
      "critical_limitations":[
       "Rigid linear pressure model is not contact FEM, ignores center bore and retainer holes and may understate peak",
       "Steel thread external edge and beech thin pocket wall cannot both meet arbitrary 2mm screen with original K01 block",
       "NASA T/(Kd) used only as equation identifying preload significance, NOT applying NASA acceptance standards to subwoofer",
       "Tightening torque without measured bolt/thread friction and wood bearing must NOT be specified",
       "Axial stack input ranges are synthetic assumptions, NOT factory or machining tolerances",
       "P40 151.11 N resultant includes 91.94 N shear and 119.92 N axial; not comparable to preload directly",
       "Wood interface glue peel/creep, steel thread strip, locally bending plate, retainer screws and access unqualified",
       "No 3D contact/no real K02 route and no CNC"]
    }
def main():
    o=compute()
    OUT.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("K14: 6 lips; 12 hypothetical preload cases; 64 tolerance corners; 0 manufacturing approvals.")
    print("Total lip budget",o["key_conservation"]["total_wood_plus_steel_radial_lip_budget_mm"])
    print("Tolerance endpoints pass",o["worst_case_synthetic_axial_stack"]["cases_meeting_only_K13_hypothetical_1xM5_zero_protrusion_screen"])
if __name__=="__main__":main()
