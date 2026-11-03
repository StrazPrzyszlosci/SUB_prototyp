#!/usr/bin/env python3
"""K05 — sequencing analysis, NOT a verified assembly of real parts or CNC.

Derived from versioned, Actions-verified K02/K04 evidence. Recomputes circular
front-aperture ingress bounds for loose nominal washers; it does NOT solve
tool-access, structural retention, module reconfiguration or arbitrary 3D paths.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "wyniki" / "k04_podsumowanie.json"
OUT = ROOT / "wyniki" / "k05_podsumowanie.json"

def analyze(src):
    v = src["assembly_research"]["verified_from_actions"]
    cases = v["completions_100L_by_clearance_3_6"]
    assert v["conclusion"] == "success"
    assert src["assembly_research"]["path_tests_defined"] == 22
    assert cases["C20_no_fastener"] == [20, 20]
    assert cases["C20_plate2_washer_nutM6"] == [16, 16]
    final = v["static_final_module_positions_100L"]
    assert final["module_count"] == 20 and final["collisions"] == 0
    assert final["clearance"] == 6
    geom = src["manufacturer_dimensions"]
    rb = float(geom["bolt_PCD_radius_mm"])
    rcut = float(geom["cutout_radius_mm"])
    assert math.isclose(rb - rcut, 6.1, abs_tol=1e-9)
    # Perpendicular ingress of a CIRCULAR loose part centered in the aperture:
    # before crossing the baffle it needs center radius <= Rcut - r_part;
    # to arrive on a bolt circle radius RB, it must then move radially at
    # least RB - (Rcut - r_part). No tools, ribs, pads, or trajectory modeled.
    parts = [
        ("podkladka_M5_OD10", 5.0),
        ("podkladka_M6_OD12", 6.0),
        ("idealny_naroznik_nakretki_M6_AF10", 10.0 / math.sqrt(3.0)),
    ]
    entry = []
    for name, radius in parts:
        max_center_at_aperture = rcut - radius
        shift = rb - max_center_at_aperture
        assert shift > 0
        entry.append({
            "part": name,
            "nominal_bounding_radius_mm": round(radius, 5),
            "maximum_center_radius_during_straight_front_ingress_mm": round(max_center_at_aperture, 5),
            "necessary_radial_repositioning_for_bolt_circle_mm": round(shift, 5),
            "note": "2D necessary condition for an ideal perpendicular entry; not a collision-free 3D route"
        })
    # All 8 axes share the same theoretical circular opening bound; actual
    # access is anisotropic because of basket ribs, braces and the cabinet.
    data = {
        "study": "K05",
        "date": "2026-11-03",
        "source_file": "wyniki/k04_podsumowanie.json",
        "source_actions_run": v["run_id"],
        "status": "RESEARCH, no physical assembly, no proven rear-fastener installation",
        "configuration": {
            "driver": geom["driver"],
            "baffle_mdf_mm": 44,
            "local_pad_depth_mm": 20,
            "modules_for_100_l": 20,
            "full_fastener_rear_envelope_mm": 28.8,
            "number_of_bolt_axes": 8
        },
        "order_before_modules": {
            "description": "Complete nominal M6 rear stack preinstalled; conservative full-pad prism, existing K04/K02 route planner",
            "clearances_mm": [3, 6],
            "modules_reached": cases["C20_plate2_washer_nutM6"],
            "complete_sequence": False,
            "interpretation": "No path found in this surrogate, not proof of real impossibility"
        },
        "modules_before_rear_hardware": {
            "description": "Move all 20 modules with bare 20mm pads; only then hypothesize installing rear M6 hardware",
            "clearances_mm": [3, 6],
            "modules_reached_with_bare_pads": cases["C20_no_fastener"],
            "static_final_module_positions_colliding_with_full_M6_envelope": final["collisions"],
            "final_module_count": final["module_count"],
            "final_position_clearance_mm": final["clearance"],
            "large_module_axis_gap_after_clearance_mm": final["remaining_X_mm"],
            "small_module_axis_gap_after_clearance_mm": final["remaining_Y_mm"],
            "hardware_delivery_behind_baffle_verified": False,
            "tool_and_hand_access_verified": False,
            "captive_nut_retention_verified": False,
            "joint_strength_verified": False,
            "complete_real_sequence_verified": False,
            "interpretation": "Two necessary geometric checks passed separately; no complete post-install hardware path was computed"
        },
        "front_aperture_necessary_entry_bounds": {
            "opening_radius_mm": rcut,
            "bolt_circle_radius_mm": rb,
            "bolt_axis_outside_opening_radius_mm": round(rb - rcut, 5),
            "perpendicular_ingress_to_bolt_circle": entry,
            "note": "Does not establish any real 3D route or tool reach for a washer, nut, or clamping plate"
        },
        "next_gates": [
            "Verify actual basket ribs/terminals and accessible installation positions at all 8 axes",
            "Prove hardware can be delivered and captured from the speaker aperture AFTER 20 real volume modules are installed",
            "Prove front-only disassembly/reassembly with hands and actual tools",
            "Make at least 3 comparable real MDF44 + pad20 coupons per joint/condition and measure strength and relaxation",
            "Dry-fit 20 real modules including closures, latches, clearances and two cabinet orientations",
            "Only after those gates update net volume and real <=500mm full external depth"
        ],
        "decision": "Test stage order as a physical mockup hypothesis, not a release of N1, a new material strength claim or CNC permission",
        "cnc": "HOLD"
    }
    assert len(entry) == 3
    assert data["modules_before_rear_hardware"]["modules_reached_with_bare_pads"] == [20, 20]
    return data

def main():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    data = analyze(source)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("K05", json.dumps({
        "preinstalled_M6": data["order_before_modules"]["modules_reached"],
        "modules_first": data["modules_before_rear_hardware"]["modules_reached_with_bare_pads"],
        "final_collisions": data["modules_before_rear_hardware"]["static_final_module_positions_colliding_with_full_M6_envelope"],
        "M6_washer_radial_reposition_mm": data["front_aperture_necessary_entry_bounds"]["perpendicular_ingress_to_bolt_circle"][1]["necessary_radial_repositioning_for_bolt_circle_mm"],
        "hardware_delivery_verified": False,
        "cnc": "HOLD"
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
