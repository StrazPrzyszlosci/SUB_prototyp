#!/usr/bin/env python3
"""K03: physical packaging decision gate for RSS390HF-4 fasteners.
No structural capacity, no implied selected hardware, no CNC.
Run from repo root: python3 skrypty/k03_budzet_lacznika_i_sciezka_sily.py
"""
import hashlib
import itertools
import json
from pathlib import Path

R_CUT=355.8/2
R_BOLT=368/2
R_OUTER=388.4/2
R_PAD_INNER=178.9
PAD_DEPTH=20.0
FRONT=44.0

def radial_budget(interface_clearance,required_wood,tolerance,outer_opening_d):
    # Radial aperture is a manufacturer's nominal dimension. All other
    # inputs are conditional geometric requirements / hypotheses.
    max_allowed_d=2*(R_BOLT-R_CUT-interface_clearance-required_wood-tolerance)
    remaining=R_BOLT-R_CUT-interface_clearance-tolerance-outer_opening_d/2
    return {
       "clearance_cutout_mm":interface_clearance,
       "minimum_wood_web_mm":required_wood,
       "radial_position_uncertainty_mm":tolerance,
       "hole_or_insert_external_d_mm":outer_opening_d,
       "achievable_wood_web_mm":round(remaining,6),
       "maximum_allowed_external_d_mm":round(max_allowed_d,6),
       "passes_assumed_wood_web":remaining+1.e-10>=required_wood
    }

def main():
    ds=(5.0,5.5,6.0,6.5,8.0,10.0)
    grids=list(itertools.product((.5,1.,2.),(1.,2.,3.),(0.,.5,1.),ds))
    rows=[radial_budget(*v) for v in grids]
    assert len(rows)==162
    tally={str(d):sum(r["passes_assumed_wood_web"] for r in rows
                      if r["hole_or_insert_external_d_mm"]==d) for d in ds}
    assert tally=={"5.0":14,"5.5":10,"6.0":10,"6.5":6,"8.0":3,"10.0":0}
    nominal=radial_budget(1,2,.5,8)
    assert nominal["achievable_wood_web_mm"]==.6
    assert nominal["maximum_allowed_external_d_mm"]==5.2
    # Dedicated K02 20mm pad location; hole intersects only its XZ shape,
    # not a verified cast-basket and not a measured bearing strength.
    basepad={str(d):round(R_BOLT-R_PAD_INNER-d/2,4)
             for d in (5.,5.5,6.,6.5,8.,10.)}
    assert basepad["8.0"]==1.1
    assert basepad["10.0"]==.1
    # Critical: the distance from bolt axis to the cutout edge is only 6.1
    # mm, not the nominal 12mm face-to-edge EPF general recommendation.
    edge_axis=R_BOLT-R_CUT
    assert abs(edge_axis-6.1)<1e-8
    # A clearance hole in existing 44mm MDF is NOT the same as an insert
    # external cavity in the rear pad. These are separate load paths.
    panel_holes={str(d):round(edge_axis-d/2,4)
                 for d in (4.5,5.,5.5,6.,6.5)}
    trial_dimensions={
      "front_mdf_stack_thickness_mm":FRONT,
      "driver_flange_thickness_mm":10.5,
      "rear_pad_depth_mm":PAD_DEPTH,
      "unallocated_washers_gasket_nut_etc_mm":"NOT DEFINED",
      "sum_of_nominal_axial_mdf_flange_pad_mm":round(FRONT+10.5+PAD_DEPTH,4),
      "bolt_length_to_select":"NOT YET: rear nut/insert engagement and head geometry unknown"}
    summary={
      "study":"K03",
      "date":"2026-11-03",
      "type":"Geometric impossibility/decision screen ONLY: no joint strength assessment",
      "source_dim_mm":{"driver":"RSS390HF-4","cutout_d":355.8,
           "bolt_pcd":368.0,"flange_d":388.4,"flange_thickness":10.5},
      "radial_cutout_to_bolt_axis_mm":round(edge_axis,4),
      "EPF_generic_MDF_face_screw_edge_distance_mm":12.0,
      "EPF_rule_status":"general guidance for screws into MDF faces; not a tested acceptance standard for reinforced speaker joints",
      "reference_K02_rear_pad":{"radial_inner_mm":R_PAD_INNER,
          "radial_outer_mm":205.0,"tangential_width_mm":36.0,
          "depth_mm":PAD_DEPTH,"outer_cavity_distance_to_pad_inner_edge_mm":basepad},
      "radial_sensitivity_cases":len(rows),
      "assumed_grid":{"cutout_to_pad_clearance_mm":[.5,1.,2.],
          "remaining_wood_web_requirement_mm":[1.,2.,3.],
          "radial_position_uncertainty_mm":[0.,.5,1.],
          "opening_external_diameters_mm":ds},
      "geometry_pass_counts_by_d":tally,
      "benchmark_hypothesis":{"cutout_clearance":1., "wood_web":2.,
         "radial_position_uncertainty":.5,
         "max_external_diameter_that_passes_mm":5.2,
         "d8_result_wood_web_mm":.6,"d8_pass":False,
         "d5_result_wood_web_mm":2.1,"d5_pass":True},
      "radial_wood_left_from_front_cutout_by_panel_clearance_d_mm":panel_holes,
      "axial_stack_to_complete":trial_dimensions,
      "geometry_condition":"R_bolt - R_cut >= clearance_to_cutout + external_d/2 + radial_uncertainty + minimum_wood_web",
      "candidate_load_paths":[
        {"id":"S","name":"Screw directly into rear pad","status":"CONDITIONAL, pilot / major thread, MDF holding strength and repeat servicing untested"},
        {"id":"N","name":"Through bolt and captive backing element","status":"CONDITIONAL, nut/washer tool access through cutout and force transfer into reinforced MDF untested"},
        {"id":"R","name":"Local metal spreader / backing bridge to stronger MDF or braces","status":"CONDITIONAL, may bypass small local insert wood web; fastening details, real basket clearance and module route untested"}
      ],
      "decision":"Do not select a large embedded threaded insert only by 20mm pad depth; outer cavity diameter collides with conservative radial wood-web budget. No CNC approval.",
      "next_gate":"Verify real basket/terminal profile; choose actual shank and external captive-bolt/spreader geometry, measure candidate coupons on MDF44 and replay K02 20-module assembly with tools/fasteners."
    }
    result={"summary":summary,"sensitivity":rows}
    dest=Path("wyniki");dest.mkdir(exist_ok=True)
    p=dest/"k03_pelna_macierz_przeswitow.json"
    p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    (dest/"k03_manifest_odtworzony.json").write_text(
        json.dumps({"summary":summary,"generated_sha256":hashlib.sha256(p.read_bytes()).hexdigest()},
                   indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
