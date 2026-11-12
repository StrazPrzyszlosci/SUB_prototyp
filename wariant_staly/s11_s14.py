"""S11-S14: manufacturer-source geometry, plate sensitivity, amplifier/dsp headroom.
Catalogue facts are NOT measured acceptance and this script never approves CNC.
"""
import json
import math
from pathlib import Path
HERE = Path(__file__).resolve().parent

def load():
    return json.loads((HERE/"s11_parametry_zrodel.json").read_text(encoding="utf-8"))

def calculate(data):
    d=data["driver"]; m=data["mdf_reference"]; c=data["connector"]; g=data["glue"]
    dsp=data["dsp"]; a=data["amplifier_candidate"]
    W,H,D=816.8,473.3,394.0  # S06
    ring_pocket_d=400.4       # K42/S10; nominal, NOT producer dimension
    trial_screw_d=5.6         # K42 trial clearance, not Daytona factory bore
    plate_w,plate_h=70.0,72.0 # S05 bracket placeholder
    area_face_m2=W*H/1e6
    actual_possible_glue_m2=area_face_m2-math.pi*(ring_pocket_d/2)**2/1e6
    if actual_possible_glue_m2<=0: raise ValueError("Ring pocket consumes entire front")
    s12={
        "front_flange_margin_mm":(H-d["outer_d_mm"])/2,
        "ring_pocket_margin_mm":(H-ring_pocket_d)/2,
        "mdf_bridge_to_trial_fr1_hole_mm":(d["pcd_mm"]-d["cutout_d_mm"]-trial_screw_d)/2,
        "minimum_FR2_residual_beneath_pocket_mm":m["nominal_t_mm"]-m["stock_thickness_tolerance_mm"]-6.2,
        "minimum_FR2_residual_beneath_extra_4mm_relief_mm":m["nominal_t_mm"]-m["stock_thickness_tolerance_mm"]-6.2-4.0,
        "lamination_nominal_wood_contact_m2":actual_possible_glue_m2,
        "glue_spread_estimate_g_per_front":[actual_possible_glue_m2*g["surface_spread_min_g_m2"],actual_possible_glue_m2*g["surface_spread_max_g_m2"]],
        "glue_spread_estimate_g_pair":[2*actual_possible_glue_m2*g["surface_spread_min_g_m2"],2*actual_possible_glue_m2*g["surface_spread_max_g_m2"]],
        "bracket_flange_edge_margin_horizontal_mm":(plate_w-c["flange_d_mm"])/2,
        "bracket_flange_edge_margin_vertical_mm":(plate_h-c["flange_d_mm"])/2,
        "bracket_mounting_hole_edge_margin_horizontal_mm":plate_w/2-c["holes_distance_mm"]/2-c["hole_d_min_mm"]/2,
        "bracket_mounting_hole_edge_margin_vertical_mm":plate_h/2-c["holes_distance_mm"]/2-c["hole_d_min_mm"]/2,
        "bracket_cutout_radius_mm":c["cutout_d_min_mm"]/2,
        "CNC":"HOLD"
    }
    # Isolated-plate Kirchhoff scaling ONLY. Not full finite element solution.
    base_E=2000.0
    E=m["bending_E_mean_MPa"]
    t0=m["nominal_t_mm"]
    defl0=0.043 # S03/A clamped reference at 1 kPa, 22 mm/2000 MPa
    f0=117.0    # S03/A pinned reference at 22 mm, E=2000 MPa
    tmin=t0-m["stock_thickness_tolerance_mm"]
    tmax=t0+m["stock_thickness_tolerance_mm"]
    s13={
        "nominal_E_MPa_in_original_S03":base_E,
        "catalog_E_mean_MPa":E,
        "thickness_range_mm":[tmin,tmax],
        "isolated_clamped_A_deflection_1kPa_mm_range_at_catalog_E":[defl0*(base_E/E)*(t0/tmax)**3, defl0*(base_E/E)*(t0/tmin)**3],
        "isolated_pinned_A_f1_Hz_range_same_assumed_density":[f0*math.sqrt(E/base_E)*(tmin/t0), f0*math.sqrt(E/base_E)*(tmax/t0)],
        "validity":"Skalowanie pojedynczej plyty z zachowanymi podporami i stalym rho, nie walidacja MES ani charakterystyka materialu dostarczonego."
    }
    gain_hi=10**(a["gain_max_db"]/20)
    max_sine_vrms=a["output_vpeak_typ"]/math.sqrt(2)
    full_input_limit=max_sine_vrms/gain_hi
    proposed_trim=-6.0
    out_after_trim=dsp["output_max_vrms"]*10**(proposed_trim/20)*gain_hi
    s14={
        "channels":["monitor_L_low","monitor_L_mid","monitor_L_high","monitor_R_low","monitor_R_mid","monitor_R_high","sub_L","sub_R"],
        "dsp_analog_out_vrms":dsp["output_max_vrms"],
        "amplifier_gain_worst_db":a["gain_max_db"],
        "amplifier_gain_worst_linear":gain_hi,
        "amplifier_typical_Vpeak_to_sine_Vrms":max_sine_vrms,
        "dsp_full_scale_undamped_amplifier_predicted_Vrms":dsp["output_max_vrms"]*gain_hi,
        "max_dsp_input_for_50Vpeak_typ_Vrms":full_input_limit,
        "attenuation_to_match_typical_peak_dB":20*math.log10(full_input_limit/dsp["output_max_vrms"]),
        "hypothetical_trim_dB":proposed_trim,
        "hypothetical_amplifier_out_at_full_dsp_signal_Vrms":out_after_trim,
        "hypothetical_amplifier_out_at_full_dsp_signal_Vpeak":out_after_trim*math.sqrt(2),
        "remaining_headroom_to_typical_peak_at_hypothetical_trim_dB":20*math.log10(max_sine_vrms/out_after_trim),
        "previous_study_nominal_40Vrms_not_reachable_as_clean_sine_300AS1":40.0>max_sine_vrms,
        "status":"HOLD: 2V RCA -> zbalansowany input wymaga poprawnego interfejsu; nie weryfikowano ochrony X/T, transjentow, impedancji Z(f), termiki ani limitera."
    }
    return {"stan":"PRZESIEW_KATALOGOWY_NIE_DOPUSZCZENIE","S12_geometria":s12,"S13_material":s13,"S14_naped":s14}
if __name__=="__main__":
    print(json.dumps(calculate(load()),ensure_ascii=False,indent=2))
