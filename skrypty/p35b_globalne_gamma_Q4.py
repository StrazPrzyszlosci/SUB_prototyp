#!/usr/bin/env python3
"""P35B: P33B global Q4 rerun with shear-hourglass stabilization from P33C.

RESEARCH ONLY: local gamma removes two zero-energy free-element modes,
but cannot qualify whole enclosure, joint strength, modal accuracy or CNC.
Requires numpy and scipy; runs existing repository models unchanged
except for explicit injection of gamma into their local Q4 element.
"""
import argparse
import json
import math
from pathlib import Path

import p33b_powlokowy_fem as old_fem
from p33c_hourglass_audyt import element, rank_and_rigid, plate

def run_model(gamma, mesh, k_trans=3e7, k_rot=3e3):
    def stabilized(lx, ly, thickness, cut=1):
        return element(lx, ly, thickness, gamma)*cut
    old_fem.shell_element=stabilized
    row=old_fem.global_mesh(mesh=mesh,kTrans=k_trans,kRot=k_rot,
                            driverMass=15,insertMass=8,brace=True)
    row["gamma"]=gamma
    return row

def run():
    rows=[]
    for gamma in (0,.001,.01,.03):
        for mesh in (.15,.11,.085):
            rows.append(run_model(gamma,mesh))
    for gamma in (.001,.01):
        for kt,kr in ((3e6,3e2),(3e8,3e4)):
            rows.append(run_model(gamma,.11,kt,kr))
    assert len(rows)==16
    local=[rank_and_rigid(g) for g in (0,.001,.01,.03)]
    assert local[0]["null_modes"]==8
    assert all(x["null_modes"]==6 for x in local[1:]), local
    checks=[plate(nx,ny,g) for g in (.001,.01,.03)
            for nx,ny in ((8,4),(16,8),(32,12))]
    baseline=next(r for r in rows if r["gamma"]==0 and abs(r["mesh"]-.11)<1e-12)
    assert abs(baseline["max_static_disp_um"]-83.279)<2,baseline
    return {"study":"P35B","date":"2026-10-31","cases":len(rows),
        "status":"Numerical parametric FEM validation, NOT physical cabinet qualification",
        "free_element":local,"plate_checks":checks,"global_cases":rows,
        "limitations":[
           "Numerical gamma shearing blend is an arbitrary regularization, not real MDF material.",
           "Global P33B uses coarse nonconforming hole cut cells, theoretical braces, joints and feet.",
           "No modal assurance criterion MAC, locking/patch checks for the whole curved mesh.",
           "Scenarios not equivalent to a verified full CAD of the real cabinet.",
           "No CNC approval, no validated fatigue or stress in glue and screws."]}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="wyniki/p35b_stabilizacja_globalna_16_20261031.json")
    args=p.parse_args()
    result=run()
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":result["cases"],
                      "baseline":next(r for r in result["global_cases"]
                                       if r["gamma"]==0 and r["mesh"]==.11)},indent=2))
