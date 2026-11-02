#!/usr/bin/env python3
"""B12-13: 4 rib-aligned + 4 inter-rib bolt-group sensitivity.
A RIGID plate with LINEAR NORMAL SPRINGS and weighted shear is only a
conditional engineering screening model. No measured fastening stiffness,
joint strength, rib geometry, 3D contact or CNC clearance.
Run: python3 skrypty/b12_13_nierowna_sztywnosc_4plus4.py
"""
from pathlib import Path
import itertools
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wyniki"
OUT.mkdir(exist_ok=True)
R = 184.0
G = 9.80665
MASS = {"catalog_30lb": 30 * 0.45359237, "legacy_hypothesis_15kg": 15.0}
RATIO = [0.25, 0.5, 1.0, 2.0, 4.0]
G_LEVEL = [1, 3, 5, 10]
ECC = [80, 120, 160]
DIRS = ["x", "z"]
LOST = [None, *range(8)]
NOMINAL_BOND_AREA = (205-178.9)*36-math.pi*8**2/4
POINTS = [(R*math.cos(i*math.pi/4), R*math.sin(i*math.pi/4)) for i in range(8)]

def solve(a, v):
    n = len(v)
    q = [list(map(float, a[i]))+[float(v[i])] for i in range(n)]
    for i in range(n):
        row = max(range(i,n), key=lambda j:abs(q[j][i]))
        q[i],q[row] = q[row],q[i]
        if abs(q[i][i]) < 1e-12:
            raise ValueError("singular bolt-group stiffness matrix")
        factor = q[i][i]
        q[i] = [a/factor for a in q[i]]
        for j in range(n):
            if j == i: continue
            factor = q[j][i]
            q[j] = [q[j][k]-factor*q[i][k] for k in range(n+1)]
    return [q[i][-1] for i in range(n)]

def case(mass,accel,ecc,ratio,direction,lost):
    F = mass*G*accel
    # For the *drawn* rear view: indices 0,2,4,6 align to ribs.
    k = {i:(ratio if i % 2 == 0 else 1.0)
         for i in range(8) if i != lost}
    sx=sum(k.values())
    weighted=lambda fun:sum(weight*fun(*POINTS[i]) for i,weight in k.items())
    sX=weighted(lambda x,z:x)
    sZ=weighted(lambda x,z:z)
    sXX=weighted(lambda x,z:x*x)
    sZZ=weighted(lambda x,z:z*z)
    sXZ=weighted(lambda x,z:x*z)
    # Signed spring reaction: N_i=k_i(a+b*x_i+c*z_i).
    # Equivalent moment axis convention: external load along x -> Mz;
    # external load along z -> Mx. Signs reversed do not change peak magnitudes.
    # For lateral x load, the overturning moment is around z, balanced
    # by sum(x*N_y); for lateral z load it is around x, balanced by
    # sum(z*N_y). Required sums below are unsigned magnitudes.
    moment_about_z_balance=F*ecc if direction=="x" else 0.
    moment_about_x_balance=F*ecc if direction=="z" else 0.
    a,b,c=solve([[sx,sX,sZ],[sX,sXX,sXZ],[sZ,sXZ,sZZ]],
                [0,moment_about_z_balance,moment_about_x_balance])
    normals={i:k[i]*(a+b*POINTS[i][0]+c*POINTS[i][1]) for i in k}
    shears={i:F*k[i]/sx for i in k}
    tol=max(1e-8,F*ecc*1e-10)
    assert abs(sum(normals.values())) < tol
    assert abs(sum(normals[i]*POINTS[i][0] for i in k)-moment_about_z_balance) < tol
    assert abs(sum(normals[i]*POINTS[i][1] for i in k)-moment_about_x_balance) < tol
    assert abs(sum(shears.values())-F) < 1e-8
    tensile=max(max(0.0,n) for n in normals.values())
    compressive=max(max(0.0,-n) for n in normals.values())
    # Compression is credited to contact ONLY in this idealized proxy; the
    # actual basket contact has not been solved. Never a design allowables test.
    combined=max(math.hypot(max(0.0,normals[i]),shears[i]) for i in k)
    return {
        "total_lateral_force_N":round(F,5),
        "active":len(k),
        "max_tensile_normal_N":round(tensile,5),
        "max_compressive_normal_N":round(compressive,5),
        "max_inplane_shear_N":round(max(shears.values()),5),
        "max_bolt_tension_plus_shear_proxy_N":round(combined,5),
        "mean_bond_tensile_demand_MPa":round(tensile/NOMINAL_BOND_AREA,6),
        "mean_bond_shear_demand_MPa":round(max(shears.values())/NOMINAL_BOND_AREA,6),
        "normal_forces_N":{str(i):round(v,5) for i,v in normals.items()},
        "shear_forces_N":{str(i):round(v,5) for i,v in shears.items()},
    }

def main():
    raw = []
    for m_key,accel,ecc,ratio,direction,lost in itertools.product(
         MASS,G_LEVEL,ECC,RATIO,DIRS,LOST):
        r = case(MASS[m_key],accel,ecc,ratio,direction,lost)
        raw.append({"mass_source":m_key,"accel_g":accel,
           "eccentricity_mm":ecc,"rib_to_interrib_stiffness_ratio":ratio,
           "lateral_force_direction":direction,
           "lost_bolt_index":lost, **r})
    assert len(raw)==2*4*3*5*2*9==2160
    ref=case(MASS["catalog_30lb"],5,120,1,"x",None)
    assert abs(ref["total_lateral_force_N"]-MASS["catalog_30lb"]*G*5)<1e-4
    # Exact eight equal rigid springs: 4 springs with lever arm R.
    assert abs(ref["max_tensile_normal_N"]-
               MASS["catalog_30lb"]*G*5*120/(4*R))<1e-4
    assert abs(ref["max_inplane_shear_N"]-
               MASS["catalog_30lb"]*G*5/8)<1e-4
    # The scaled historical 15 kg model should reproduce B12-09 at 5g.
    legacy=case(15,5,120,1,"x",None)
    assert abs(legacy["max_tensile_normal_N"]-119.91856)<0.01
    assert abs(legacy["max_inplane_shear_N"]-91.93734)<0.01
    selected={}
    for ratio in RATIO:
        intact=case(MASS["catalog_30lb"],5,120,ratio,"x",None)
        losses=[(i,case(MASS["catalog_30lb"],5,120,ratio,"x",i))
                for i in range(8)]
        lost, worst=max(losses,key=lambda x:x[1]["max_bolt_tension_plus_shear_proxy_N"])
        selected[str(ratio)]={
             "intact":{k:intact[k] for k in (
               "max_tensile_normal_N","max_compressive_normal_N",
               "max_inplane_shear_N","max_bolt_tension_plus_shear_proxy_N",
               "mean_bond_tensile_demand_MPa","mean_bond_shear_demand_MPa")},
             "single_bolt_loss_worst":{"bolt_index":lost,**{
                 k:worst[k] for k in (
                    "max_tensile_normal_N","max_inplane_shear_N",
                    "max_bolt_tension_plus_shear_proxy_N")}},
             "change_worst_after_loss_pct":round(
                 100*(worst["max_bolt_tension_plus_shear_proxy_N"]/
                      intact["max_bolt_tension_plus_shear_proxy_N"]-1),3)
        }
    worst = max((r for r in raw if r["mass_source"]=="catalog_30lb"
             and r["accel_g"]==5 and r["eccentricity_mm"]==120),
             key=lambda r:r["max_bolt_tension_plus_shear_proxy_N"])
    summary={
      "source":"Manufacturer product page nominal weight 30 lb -> 13.6077711 kg",
      "mass_kg":{"catalog_30lb":MASS["catalog_30lb"],
                 "legacy_hypothesis_15kg":15},
      "cases":len(raw),"equal_stiffness_nominal_5g_120mm":ref,
      "by_rib_to_interrib_stiffness_ratio_at_5g_120mm":selected,
      "worst_catalog_case_5g_120mm":{k:worst[k] for k in (
         "rib_to_interrib_stiffness_ratio","lateral_force_direction",
         "lost_bolt_index","max_tensile_normal_N",
         "max_inplane_shear_N","max_bolt_tension_plus_shear_proxy_N")},
      "bond_area_mm2":round(NOMINAL_BOND_AREA,4),
      "mechanical_status":"NOT validated against actual material, fastening, or basket contact",
      "safety_factor":"NONE: 1g..10g are comparison excitations, not standards"
    }
    data={
       "id":"B12-13","date":"2026-11-02",
       "provenance":{"repo_main_parent":"057f302ed504aab752394ba4368bfc8abc2a6838",
          "manufacturer":"https://www.daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm",
          "design_bolt_circle_mm":368,
          "rib_alignment":"four even bolts on rib axes, four odd bolts inter-rib (visual drawing observation)"},
       "model":"rigid flange; independent normal linear springs with signed reactions; shear apportioned proportionally to relative stiffness; no contact/nonlinearity",
       "assumptions":{"mount_circle_radius_mm":184,
          "rib_to_interrib_stiffness_ratio":RATIO,
          "eccentricity_mm":ECC,"accel_g":G_LEVEL,
          "force_direction":DIRS,"lost_bolt":LOST,
          "bond_area_example_mm2":NOMINAL_BOND_AREA},
       "no_physical_evidence":["Relative stiffnesses and joint preload unknown",
          "Actual compression should transfer through rim contact; signed spring compression is only a proxy",
          "No test of MDF rupture, fatigue, threads, adhesive peel, shear, humidity",
          "No actual moment lever arm or drop loading characterized",
          "No CAD path 8 bolts to braces and no comparison with qualified frame A",
          "No FEA qualification or CNC approval"],
       "summary":summary,"scenarios":raw
    }
    p=OUT/"b12_13_scenariusze_4plus4.json"
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    manifest={"id":"B12-13","source":"skrypty/b12_13_nierowna_sztywnosc_4plus4.py",
              "full_file":"wyniki/b12_13_scenariusze_4plus4.json",
              "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
              "summary":summary}
    (OUT/"b12_13_podsumowanie.json").write_text(
         json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
