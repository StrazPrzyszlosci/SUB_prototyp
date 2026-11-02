#!/usr/bin/env python3
"""B12-12: conditional 4-rib / 8-hole angular clearance screening.
No verified rib dimensions or 3D CAD. Python standard library only.
Run: python3 skrypty/b12_12_katy_zeber_i_mocowan.py
"""
import itertools, math, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"wyniki";OUT.mkdir(exist_ok=True)
BOLT_R=184.0
PHASES=[i*.25 for i in range(181)]
RADII=[178.,178.9,180.]
WIDTHS=[24,36,48]
RIB_HALFS=[5,10,15,20]
REACHES=[175,178,180,184]
UNCERTAINTIES=[0,2,5]

def nearest_rib_angle(phase):
    """Four ribs every 90 degrees, eight bolt positions every 45 degrees."""
    a=phase%45
    return min(a,45-a)

def pad_halfwidth(radius,width):
    return math.degrees(math.atan(width/(2*radius)))

def clear(phase,ri,width,beta,reach,uncertainty):
    # Rib wedge must ALSO overlap the pad in Y depth; this is conditional.
    if reach<ri-1e-10:return True
    return nearest_rib_angle(phase)>beta+pad_halfwidth(ri,width)+uncertainty+1e-10

def independent_check(phase,threshold,uncertainty):
    """Check real eight bolt / four rib angular separations at endpoints and cusps."""
    offsets=[-uncertainty,0,uncertainty]
    for k in range(-2,3):
        cusp=45*k-phase
        if -uncertainty<=cusp<=uncertainty:offsets.append(cusp)
    for delta in offsets:
        distance=min(abs((phase+delta+45*b-90*r+180)%360-180)
                     for b in range(8) for r in range(4))
        if distance<=threshold+1e-10:return False
    return True

def calculate():
    cases=[]
    for ri,width,beta,reach,unc in itertools.product(RADII,WIDTHS,RIB_HALFS,REACHES,UNCERTAINTIES):
        passed=sum(clear(p,ri,width,beta,reach,unc) for p in PHASES)
        cases.append({"inner_radius_mm":ri,"pad_width_mm":width,
          "rib_half_angle_deg":beta,"rib_reach_mm":reach,
          "clocking_error_deg":unc,"safe_phases":passed,
          "sampled_phases":len(PHASES),"radial_overlap_possible":reach>=ri})
    assert len(cases)==432
    assert len(cases)*len(PHASES)==78192
    for phase,width,beta,unc in itertools.product(PHASES,WIDTHS,RIB_HALFS,UNCERTAINTIES):
        t=beta+pad_halfwidth(178.9,width)
        assert clear(phase,178.9,width,beta,184,unc)==independent_check(phase,t,unc)
    assert max(map(nearest_rib_angle,PHASES))==22.5
    # Manufacturer's *drawn* rear view: four rib axes appear collinear with
    # four of the eight mounting-hole axes. This is an approximate visual
    # construction observation, NOT a measured angular phase/tolerance.
    as_drawn_bolt_separations_deg=[
        min(abs(((45*b-90*k+180)%360)-180) for k in range(4))
        for b in range(8)]
    assert as_drawn_bolt_separations_deg == [0,45,0,45,0,45,0,45]
    # Two families of fasteners must therefore be checked independently.

    reference=[x for x in cases if x["inner_radius_mm"]==178.9 and x["rib_reach_mm"]==184]
    phase_counts={str(w):{str(b):{str(u):next(c["safe_phases"] for c in reference
           if c["pad_width_mm"]==w and c["rib_half_angle_deg"]==b and c["clocking_error_deg"]==u)
           for u in UNCERTAINTIES} for b in RIB_HALFS} for w in WIDTHS}
    summary={"parameter_cells":432,"angular_phase_screens":78192,"phase_step_deg":.25,
      "optimal_theoretical_min_angle_deg":22.5,
      "manufacturer_drawing_observation":{
          "nominal_relative_phase_deg":0,
          "phase_precision":"VISUAL ONLY, unmeasured",
          "bolt_rib_axis_distances_deg":as_drawn_bolt_separations_deg,
          "rib_aligned_bolts":4,"inter_rib_bolts":4,
          "cannot_rotate_driver_to_modify_relative_phase":True,
          "physical_collision_unresolved_without_rib_y_theta_profile":True},
      "max_rib_half_angle_at_ri_178_9":{str(w):round(22.5-pad_halfwidth(178.9,w),4) for w in WIDTHS},
      "phase_counts_if_reach_184_and_ri_178_9":phase_counts,
      "maximum_pad_width_for_beta":{str(b):round(2*178.9*math.tan(math.radians(22.5-b)),4) for b in RIB_HALFS},
      "rear_tool_radius_angular_halfwidth_deg":{str(t):round(math.degrees(math.asin(t/BOLT_R)),4) for t in [3,5,8,10]},
      "no_radial_overlap_parameter_cells":sum(not x["radial_overlap_possible"] for x in cases),
      "radially_overlapping_parameter_cells":sum(x["radial_overlap_possible"] for x in cases)}
    result={"study":"B12-12","date":"2026-11-02",
      "evidence":"four principal spokes visually visible in the official manufacturer rear view; eight fastener holes and PCD from specification",
      "dimensions_mm":{"bolt_pcd":368,"cutout_diameter":355.8,"flange_diameter":388.4},
      "condition":"Conservative angular sector model ONLY WHEN four hypothetical ribs extend radially to the pad and occupy the same depth. Actual rib profile and phase are unmeasured.",
      "important":"Official rear technical drawing shows four of eight flange hole axes visually aligned with the four main rib axes (nominal phase approximately 0 degrees), the others between them. Rotating the WHOLE driver does not change this. Actual rib radial reach at rear of MDF 44 mm is unknown. Swept phases are mathematical counterfactuals, not assembly adjustment.",
      "limitations":["no verified STEP or measured rib angular width, radial reach or depth profile",
        "rectangular pad angular envelope approximated conservatively by inner-edge corner",
        "unknown terminals and rear-side access path",
        "rear tool radius angular angle does not assess a FRONT-side driver tool",
        "counts are sample-grid counts, never physical probabilities",
        "no fastening, MDF, adhesive or fatigue test; NOT CNC"],"summary":summary,"parameter_cases":cases}
    full=OUT/"b12_12_katy_zeber_i_mocowan.json"
    full.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (OUT/"b12_12_podsumowanie.json").write_text(json.dumps(
      {"summary":summary,"sha256_of_generated_full_json":hashlib.sha256(full.read_bytes()).hexdigest(),
       "source":"skrypty/b12_12_katy_zeber_i_mocowan.py","status":"conditional; not CNC"},
      ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":calculate()
