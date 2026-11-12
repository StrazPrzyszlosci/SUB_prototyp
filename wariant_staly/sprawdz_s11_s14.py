"""Regression of independent primary sources and screening-only guards."""
from s11_s14 import calculate, load
d=load()
r=calculate(d)
g=r["S12_geometria"];m=r["S13_material"];a=r["S14_naped"]
assert d["driver"]["vas_l"]==212 and d["driver"]["xmax_one_way_mm"]==14
assert 36.44<g["ring_pocket_margin_mm"]<36.46
assert 3.29<g["mdf_bridge_to_trial_fr1_hole_mm"]<3.31
assert 0.2606<g["lamination_nominal_wood_contact_m2"]<0.2608
assert 26.0<g["glue_spread_estimate_g_per_front"][0]<26.2
assert 33.8<g["glue_spread_estimate_g_per_front"][1]<34.0
assert g["bracket_flange_edge_margin_horizontal_mm"]==9.6 or abs(g["bracket_flange_edge_margin_horizontal_mm"]-9.6)<1e-8
assert 11.49<g["minimum_FR2_residual_beneath_extra_4mm_relief_mm"]<11.51
assert g["CNC"]=="HOLD"
assert m["thickness_range_mm"]==[21.7,22.3]
assert 0.039<m["isolated_clamped_A_deflection_1kPa_mm_range_at_catalog_E"][0]<0.040
assert 0.042<m["isolated_clamped_A_deflection_1kPa_mm_range_at_catalog_E"][1]<0.043
assert 118<m["isolated_pinned_A_f1_Hz_range_same_assumed_density"][0]<119
assert 121<m["isolated_pinned_A_f1_Hz_range_same_assumed_density"][1]<122
assert len(a["channels"])==8
assert a["attenuation_to_match_typical_peak_dB"]< -3.3
assert 1.35<a["max_dsp_input_for_50Vpeak_typ_Vrms"]<1.37
assert 25.9<a["hypothetical_amplifier_out_at_full_dsp_signal_Vrms"]<26.2
assert a["previous_study_nominal_40Vrms_not_reachable_as_clean_sine_300AS1"] is True
assert a["status"].startswith("HOLD")
print("S11-S14 OK - sources, geometry, plate scaling, gain and HOLD")
