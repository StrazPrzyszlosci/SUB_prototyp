#!/usr/bin/env python3
"""K06: 8 front-only spherical gauge pathways AFTER 20 P30E inserts.

An ideal freely-translating sphere is NOT a wrench, captive nut, fixing plate,
basket, robot arm or assembly operation. Testing a continuous, three-segment
trajectory in the *existing P30E AABB geometry* advances only a spatial
necessary-access check. Real physical hardware and MDF coupons remain UNTESTED.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skrypty"))
import p30e_mat50_geometria_montaz as p30e

# Manufacturer RSS390HF-4 drawing: cut-out Ø355.8, 8-hole PCD Ø368.
R_CUT = 177.9
R_BOLT = 184.0
PAD_DEPTH = 20.0           # K02 nominal MDF reinforcement behind front
FRONT = 44.0
DRIVER_GLOBAL = (231.0, 250.0)
WALL = 22.0
RADII = (6.0, 12.0, 24.0)  # ideal free spherical gauges Ø12/Ø24/Ø48 mm, NOT selected parts
Y_TURNS = (30.0, 35.0, 45.0, 50.0, 65.0, 85.0)
EPS = 0.5                 # minimum axial gap from nominal 20mm rear face of pads
ENTRY_GAP = 1.0           # front circular aperture radial margin
CX, CZ = DRIVER_GLOBAL[0] - WALL, DRIVER_GLOBAL[1] - WALL

def square_distance_segment_aabb(a, b, box):
    """Exact squared minimum Euclidean distance (segment ↔ axis-aligned box).

    Split [0,1] at coordinates' box-face crossing parameters. In each interval
    the distance-to-box squared is a quadratic; minimize it analytically.
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    lo, hi = np.asarray(box, float)
    d = b - a
    ts = [0.0, 1.0]
    for i in range(3):
        if abs(d[i]) > 1e-12:
            for boundary in (lo[i], hi[i]):
                t = (boundary - a[i]) / d[i]
                if 0.0 < t < 1.0:
                    ts.append(float(t))
    ts = sorted(set(ts))
    best = math.inf
    for left, right in zip(ts[:-1], ts[1:]):
        middle = a + d * ((left + right) * 0.5)
        fixed = []
        for i in range(3):
            if middle[i] < lo[i]:
                fixed.append((i, lo[i]))
            elif middle[i] > hi[i]:
                fixed.append((i, hi[i]))
        denom = sum(d[i] ** 2 for i, _ in fixed)
        num = sum((boundary - a[i]) * d[i] for i, boundary in fixed)
        optimum = min(right, max(left, num / denom)) if denom > 1e-18 else left
        pt = a + optimum * d
        delta = np.maximum(np.maximum(lo - pt, pt - hi), 0.0)
        best = min(best, float(np.dot(delta, delta)))
    return best

def self_tests():
    cube = np.array([[0.,0.,0.],[2.,2.,2.]])
    assert abs(square_distance_segment_aabb([-4,1,1],[5,1,1],cube)) < 1e-10
    assert abs(square_distance_segment_aabb([-3,1,1],[-3,1,1],cube) - 9.) < 1e-10
    assert abs(square_distance_segment_aabb([-3,-3,1],[-3,-3,1],cube) - 18.) < 1e-10
    assert abs(square_distance_segment_aabb([-3,-3,1],[3,3,1],cube)) < 1e-10
    rng = np.random.default_rng(2046)
    for _ in range(80):
        a = rng.uniform(-5, 5, 3)
        b = rng.uniform(-5, 5, 3)
        exact = square_distance_segment_aabb(a, b, cube)
        samples = a[None,:] + np.linspace(0, 1, 1001)[:,None] * (b-a)[None,:]
        delta = np.maximum(np.maximum(cube[0]-samples, samples-cube[1]),0.)
        sampled = float(np.min(np.sum(delta*delta, axis=1)))
        assert exact >= -1e-10 and exact <= sampled + 1e-8
        assert abs(square_distance_segment_aabb(a,b,cube) - square_distance_segment_aabb(b,a,cube)) < 1e-8

def run():
    self_tests()
    selected = p30e.CANDIDATES[2]
    assert list(selected) == [1020, 425, 50, 120, 15]
    L, braces, modules, mat = p30e.build(selected)
    assert len(modules) == 20
    obstacles = [("wrega_%02d" % i, bx) for i,bx in enumerate(braces)]
    obstacles += [("wklad_%02d" % i, bx) for i,bx in enumerate(modules)]
    obstacles += [("mata", mat)]
    records = []
    for radius in RADII:
        for theta in range(0, 360, 45):
            rad = math.radians(theta)
            v = np.array([math.cos(rad), 0., math.sin(rad)])
            center = np.array([CX, 0., CZ])
            entry_r = R_CUT - radius - ENTRY_GAP
            # One geometry to cover all cases: front cut-out with the speaker out.
            assert entry_r > 0
            start = center + v*entry_r + [0., -FRONT-radius-1., 0.]
            best = None
            for turn_y in Y_TURNS:
                # Sphere stays wholly behind 20mm pads during sideways sweep.
                if turn_y < PAD_DEPTH + radius + EPS:
                    continue
                entry = center + v*entry_r + [0., turn_y, 0.]
                shifted = center + v*R_BOLT + [0., turn_y, 0.]
                seated = center + v*R_BOLT + [0., PAD_DEPTH+radius+EPS, 0.]
                # Throughout the front (global y=-44..0), a full sphere fits
                # through the circular opening: max radial extent = Rcut-1.
                assert entry_r + radius <= R_CUT - ENTRY_GAP + 1e-8
                # Interior side/bottom/top walls; x/z are monotone for radial leg.
                wall_space = min(float(seated[0]), float(L[0]-seated[0]),
                                 float(seated[2]), float(L[2]-seated[2]))
                if wall_space + 1e-8 < radius:
                    continue
                points = [start,entry,shifted,seated]
                blockers=[]
                min_clearance=math.inf
                for name, bx in obstacles:
                    distance=min(math.sqrt(square_distance_segment_aabb(a,b,bx))
                                 for a,b in zip(points,points[1:]))
                    min_clearance=min(min_clearance, distance-radius)
                    if distance < radius-1e-7:
                        blockers.append(name)
                if not blockers:
                    best = {
                        "turn_y_mm": turn_y,
                        "entry_center_radial_mm": round(entry_r,4),
                        "final_center_y_mm": round(float(seated[1]),4),
                        "smallest_wall_clearance_after_gauge_mm": round(wall_space-radius,4),
                        "minimum_clearance_to_modelled_braces_modules_mat_mm": round(min_clearance,4),
                        "segments": 3,
                        "waypoints_local_xyz_mm": [[round(float(n),3) for n in row] for row in points],
                    }
                    break
            records.append({"axis_deg":theta, "gauge_radius_mm":radius,
                            "full_path_found_in_P30E":best is not None,
                            "path":best})
    by_radius = {
        str(int(radius)): {
            "passed_axes":sum(1 for row in records if row["gauge_radius_mm"]==radius and row["full_path_found_in_P30E"]),
            "out_of_axes":8,
            "minimum_model_wall_margin_mm":min(row["path"]["smallest_wall_clearance_after_gauge_mm"]
                for row in records if row["gauge_radius_mm"]==radius and row["path"] is not None),
        } for radius in RADII
    }
    assert len(records)==24
    assert all(data["passed_axes"]==8 for data in by_radius.values()), by_radius
    left_bolt_wall_distance = CX - R_BOLT  # nominal axis at 180° to left inner sidewall
    assert math.isclose(left_bolt_wall_distance, 25., abs_tol=1e-8)
    out={
      "study":"K06", "date":"2026-11-03", "cnc":"HOLD", "physical_testing":False,
      "source_geometry":"P30E p30e_mat50_geometria_montaz.py + P30A braces/modules, 20 inserted; K02 20mm nominal pad",
      "nominal_manufacturer":"Dayton RSS390HF-4, cutout Ø355.8, bolt PCD Ø368",
      "model":"Fully translating SPHERICAL probe: front cutout ingress, rear turn, radial relocation, axial approach, 3 continuous straight segments",
      "conditions":{"outer_mm":[1020,425,500],"driver_global_xz_mm":[231,250],
                    "opening_radius_mm":R_CUT,"bolt_radius_mm":R_BOLT,
                    "front_thickness_mm":FRONT,"pad_depth_mm":PAD_DEPTH,
                    "inserts_present":20,"probe_diameters_mm":[12,24,48],
                    "turn_y_candidates_mm":list(Y_TURNS),
                    "gap_front_radial_mm":ENTRY_GAP,"gap_behind_pad_axial_mm":EPS},
      "results":by_radius,
      "routes":records,
      "leftmost_bolt_axis_distance_to_left_inside_wall_mm":left_bolt_wall_distance,
      "spherical_probe_radius_at_leftmost_axis_must_not_exceed_mm":left_bolt_wall_distance,
      "decision":"A full ideal spherical-gauge path is exhibited for all 8 bolt axes in the P30E model with 20 volume inserts. Test a real captured fastening and tool-access mockup next.",
      "unknowns":["Real Dayton basket ribs, terminals and 3D dimensions", "Real plate/washer/nut orientation and insertion order",
          "Real tool/hand swept volume, rotations and attachment; a sphere passing is not a wrench passing",
          "Real removable module latches, fastener retention, MDF/adhesive pullout strength, gasket and front-only service",
          "No production signoff, no CAD/cutting file"]
    }
    target=ROOT/"wyniki"/"k06_pelne_trasy_wygenerowane.json"
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    compact = {
      "study":"K06", "date":"2026-11-03",
      "source_model":"P30E with all 20 volume inserts and nominal K02 pads",
      "physical_testing":False,"cnc":"HOLD",
      "gauge_diameters_mm":[12,24,48],
      "results":by_radius,
      "leftmost_bolt_axis_distance_to_inside_wall_mm":left_bolt_wall_distance,
      "maximum_ideal_spherical_radius_at_leftmost_bolt_axis_mm":left_bolt_wall_distance,
      "full_real_fastener_assembly_verified":False,
      "routes_generated_not_committed":"wyniki/k06_pelne_trasy_wygenerowane.json"
    }
    (ROOT/"wyniki"/"k06_podsumowanie.json").write_text(
        json.dumps(compact,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
    print("K06_RESULTS", json.dumps({
        "gauges":by_radius,
        "left_wall_bolt_axis_mm":left_bolt_wall_distance,
        "spherical_radius_at_left_axis_limit_mm":left_bolt_wall_distance,
        "physical_joint_tested":False, "cnc":"HOLD"
    },ensure_ascii=False))
    return out

if __name__=="__main__":
    run()
