#!/usr/bin/env python3
"""K02: replay P30E assembly routes with K01 local pads, including EXTERIOR entry.
Uses existing repository p30a_robust_geometry, p30e_mat50_geometria_montaz
and k01_mocowanie_bilans. Research geometry only; NOT real driver/CAD/CNC.
"""
import json
import math
import sys
import hashlib
import itertools
from pathlib import Path

import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"skrypty"))
import p30a_robust_geometry as p
import p30e_mat50_geometria_montaz as e
import k01_mocowanie_bilans as k

CUT_RADIUS=177.9
BOLT_RADIUS=184.0
BASKET_XZ_GLOBAL=(231.,250.)
FRONT_THICK=44.
PAD_Y=(0.,30.)  # interior y=0..30; global y=44..74
START=np.array([209.,105.,228.])  # P30A start in INTERIOR coordinates
SELECTED=e.CANDIDATES[2]
assert list(SELECTED)==[1020,425,50,120,15]

def pad_prisms():
    # P39C/P30E coordinate mapping: x_local=x_global-22,
    # y_local=y_global-44, z_local=z_global-22.
    return [[(x-22,z-22) for x,z in k.polygon(231,45*i,178.9,205.,36.)]
             for i in range(8)]

def rect_xz(b):
    x0,z0=float(b[0,0]),float(b[0,2])
    x1,z1=float(b[1,0]),float(b[1,2])
    return [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]

def collision_with_pads(swept, pads):
    # Different Y bands do not collide even for overlapping X/Z.
    if min(float(swept[1,1]),PAD_Y[1])-max(float(swept[0,1]),PAD_Y[0])<=1e-10:
        return []
    r=rect_xz(swept)
    return [i for i,poly in enumerate(pads) if k.overlap(poly,r)]

def swept(start,end,half):
    return p.segment_box(np.asarray(start,dtype=float),
                         np.asarray(end,dtype=float),half)

def pad_aabb_boxes(pads):
    return [p.box([min(x for x,z in poly),PAD_Y[0],min(z for x,z in poly)],
                  [max(x for x,z in poly),PAD_Y[1],max(z for x,z in poly)])
            for poly in pads]

def check_state(label, indices, clearance, pads):
    L,br,mods,mat=e.build(SELECTED)
    pad_boxes=pad_aabb_boxes(pads)
    placed=[]
    paths=[]
    reasons=[]
    for order,i in enumerate(indices):
        m=mods[i]
        half=(m[1]-m[0])/2+clearance
        # Unlike original P30A/P30E, new test explicitly starts OUTSIDE
        # the front plane, with whole rectangular module clear of Y=-44.
        exterior=np.array([START[0],-FRONT_THICK-half[1]-1.,START[2]])
        opening_radius=math.hypot(half[0],half[2])
        opening_margin=CUT_RADIUS-opening_radius
        entry=swept(exterior,START,half)
        pad_entry=collision_with_pads(entry,pads)
        # The front panel is intentionally represented by a circular opening
        # instead of its full (and blocking) MDF AABB.
        other_entry=[j for j,b in enumerate(br+placed+[mat]) if p.intersect(entry,b)]
        reason=[]
        if opening_margin<=0:reason.append("rectangular module does not fit circular opening")
        if pad_entry:reason.append("entry hits K01 pads "+str(pad_entry))
        if other_entry:reason.append("entry hits previously placed modules/brace/mat "+str(other_entry))
        route=p.path_to(m.mean(axis=0),L,br+placed+[mat],half)
        if route is None:
            reason.append("P30E translational graph has no path")
            route_hits=[]
            segments=0
        else:
            route_hits=sorted(set(hit for a,b in zip(route,route[1:])
                               for hit in collision_with_pads(swept(a,b,half),pads)))
            # Old P30E path is not automatically valid after new hardware!
            # Re-plan against conservative axis-aligned *envelopes* of all
            # eight pads if any original swept segment hits the actual polygon.
            detoured=False
            original_pad_hits=list(route_hits)
            if route_hits:
                alternative=p.path_to(m.mean(axis=0),L,
                          br+placed+[mat]+pad_boxes,half)
                if alternative:
                    exact=sorted(set(h for a,b in zip(alternative,alternative[1:])
                          for h in collision_with_pads(swept(a,b,half),pads)))
                    if not exact:
                        route=alternative
                        route_hits=[]
                        detoured=True
                if route_hits:
                    reason.append("No certified detour around K01 pads; original hits "+str(original_pad_hits))
            segments=len(route)-1
            for a,b in zip(route,route[1:]):
                assert not any(p.intersect(swept(a,b,half),o)
                               for o in br+placed+[mat])
        target_box=p.box(m[0]-clearance,m[1]+clearance)
        target_hits=collision_with_pads(target_box,pads)
        if target_hits:reason.append("installed module hits pads "+str(target_hits))
        paths.append({
           "module":i,"sequence_position":order,
           "module_size_mm":list(map(float,m[1]-m[0])),
           "aperture_margin_mm":round(opening_margin,4),
           "entry_from_outside_verified":not (pad_entry or other_entry or opening_margin<=0),
           "route_waypoints":len(route) if route else 0,
           "route_segments":segments,
           "used_pad_aware_detour":detoured if route is not None else False,
           "original_P30E_route_hit_pads":original_pad_hits if route is not None else [],
           "intersects_K01_pads":bool(route_hits or target_hits),
           "model_pass":not reason,"problems":reason})
        if reason:
            reasons.append(dict(module=i,problems=reason))
            # Keep going to report all 20 installed-state locations, but a
            # failed module is NOT recorded as successfully installed.
            # Subsequent states are not physically reachable in this order.
            break
        placed.append(m)
    return {"state":label,"clearance_mm":clearance,
       "requested_modules":len(indices),"routed_modules":len(paths),
       "completed_modules":len(placed),
       "passed_full_sequence":len(placed)==len(indices),
       "minimum_cutout_margin_mm":round(min(v["aperture_margin_mm"] for v in paths),4),
       "total_path_segments":sum(v["route_segments"] for v in paths),
       "pad_aware_detours":sum(v["used_pad_aware_detour"] for v in paths),
       "failures":reasons,"individual":paths}

def main():
    pads=pad_prisms()
    states={
       "100L": list(range(20)),           # P30E: 16 large + 4 small
       "120L": list(range(4,16)),         # P30E: 12 large, no small
       "150L": [4],                       # P30E: one large
    }
    rows=[]
    for state,cl in itertools.product(states,(3.,6.)):
        rows.append(check_state(state,states[state],cl,pads))
    # Re-test most crowded state at intermediate clearance, diagnostic.
    rows.append(check_state("100L",states["100L"],5.,pads))
    assert len(rows)==7
    by_state={row["state"]+"_"+str(int(row["clearance_mm"]))+"mm":{
       "complete":row["completed_modules"],"requested":row["requested_modules"],
       "pass":row["passed_full_sequence"],"min_aperture_margin_mm":row["minimum_cutout_margin_mm"],
       "segments":row["total_path_segments"],
       "pad_aware_detours":row["pad_aware_detours"],
       "failures":row["failures"]} for row in rows}
    summary={
       "assembly_sequences":len(rows),
       "total_module_translations_checked":sum(row["completed_modules"] for row in rows),
       "all_sequences_completed":all(row["passed_full_sequence"] for row in rows),
       "cases_by_state_clearance":by_state,
       "entry_pose_local_xyz_mm":START.tolist(),
       "exterior_entry_requires_speaker_removed":True,
       "pad_prisms_eight_at_interior_y_mm":list(PAD_Y),
       "manufacturer_baffle_cutout_radius_mm":CUT_RADIUS,
       "known_limits":["P30E old AABB braces and boxes, not final shop drawings",
          "K01 pad projected profile only; real ribs, terminals, hardware unknown",
          "Module bodies are sealed AABB without latches, straps, gluing, screws",
          "Paths permit axis-aligned translations only (no rotation/gravity/hand tools)",
          "Explicit frontal entrance checked as straight passage along cabinet Y",
          "Modules are inserted only with the loudspeaker removed",
          "Successful mathematical route is not certified human/tool access or CNC"] }
    out=ROOT/"wyniki";out.mkdir(exist_ok=True)
    data={"study":"K02","source":"P30E model + P30A route planner + K01 pad polygons",
       "status":"research geometry only, NOT CNC","summary":summary,"routes":rows}
    full=out/"k02_moduly_przejscia_pelne.json"
    full.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (out/"k02_moduly_manifest_odtworzony.json").write_text(json.dumps({
       "summary":summary,"sha256":hashlib.sha256(full.read_bytes()).hexdigest(),
       "generator":"skrypty/k02_dostep_modulow_i_klocki.py"},
       ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if not summary["all_sequences_completed"]:
        raise SystemExit("K02: route found blocked; see generated full report")
if __name__=="__main__":main()
