#!/usr/bin/env python3
"""P30F: 324 quasi-static rigid-body stability scenarios for P30E geometry.
References P30D (mass model) and P30E (modified insert geometry).
Requires numpy. NO real-world anti-tip safety threshold or qualified support.
Run python skrypty/p30f_stabilnosc_nowego_korpusu.py
"""
from pathlib import Path
from itertools import product
import json,math
import numpy as np
from p30e_mat50_geometria_montaz import build
from p30d_stabilnosc_pionowa import cabinet_shell,mass_elem

CABINET=(1020,425,500,50,120,15)  # W,D,H,mat,rear_large_depth,small_forward_shift
MODES={"100":(16,4),"120":(12,0),"150":(1,0)}
def simulate(mode,rho,driver_mass,driver_y,driver_up,feet_inset):
 W,D,H,mat,rear_depth,shift=CABINET
 L,br,modules,mat_box=build((W,D,mat,rear_depth,shift))
 bodies=cabinet_shell(W,D,H,rho)
 for brace in br:
  shifted=brace+np.array([[22,44,22],[22,44,22]])
  bodies.append(mass_elem(shifted,rho)+("brace",))
 nlarge,nsmall=MODES[mode]
 for mod in modules[:nsmall]+modules[4:4+nlarge]:
  dim=mod[1]-mod[0]
  solid=math.prod(dim)-math.prod(dim-16)
  assert solid>0
  bodies.append((solid*1e-9*rho,tuple(mod.mean(axis=0)+[22,44,22]),"insert"))
 bodies.append((L[0]*L[2]*mat*1e-9*20,
                (W/2,D-22-mat/2,H/2),"mat"))
 bodies.append((driver_mass,(231,driver_y,250),"driver"))
 mass=sum(part[0] for part in bodies)
 com=sum(part[0]*np.asarray(part[1]) for part in bodies)/mass
 height=W-com[0] if driver_up else com[0]
 edges={"front":com[1]-feet_inset,"rear":D-feet_inset-com[1],
        "left":com[2]-feet_inset,"right":H-feet_inset-com[2]}
 assert min(edges.values())>0
 arm=min(edges.values())
 return dict(mode=mode,rho=rho,driver_mass_kg=driver_mass,driver_y_mm=driver_y,
    driver_up=driver_up,feet_inset_mm=feet_inset,
    mass_kg=round(mass,5),height_com_mm=round(height,5),
    com_depth_mm=round(com[1],5),com_side_mm=round(com[2],5),
    most_vulnerable_edge=min(edges,key=edges.get),
    arm_mm=round(arm,5),angle_deg=round(math.degrees(math.atan2(arm,height)),5),
    hypothetical_push_at_top_N=round(mass*9.81*arm/W,5))
def main():
 rows=[simulate(*z) for z in product(("100","120","150"),(650,800),
      (10,15,20),(90,130,170),(False,True),(0,10,25))]
 assert len(rows)==324
 summary=[]
 for inset in (0,10,25):
  for up in (False,True):
   items=[x for x in rows if x["feet_inset_mm"]==inset and x["driver_up"]==up]
   summary.append(dict(feet_inset_mm=inset,driver_up=up,n=len(items),
      min_angle_deg=min(x["angle_deg"] for x in items),
      max_angle_deg=max(x["angle_deg"] for x in items),
      min_hypothetical_push_N=min(x["hypothetical_push_at_top_N"] for x in items)))
 orientation={}
 for mode in MODES:
  n_low_better=0
  for rho,m,dy,inset in product((650,800),(10,15,20),(90,130,170),(0,10,25)):
   a=next(x for x in rows if x["mode"]==mode and x["rho"]==rho and x["driver_mass_kg"]==m and x["driver_y_mm"]==dy and x["feet_inset_mm"]==inset and not x["driver_up"])
   b=next(x for x in rows if x["mode"]==mode and x["rho"]==rho and x["driver_mass_kg"]==m and x["driver_y_mm"]==dy and x["feet_inset_mm"]==inset and x["driver_up"])
   assert a["mass_kg"]==b["mass_kg"]
   assert abs(a["height_com_mm"]+b["height_com_mm"]-1020)<1e-4
   if a["angle_deg"]>b["angle_deg"]:n_low_better+=1
  orientation[mode]=n_low_better
 assert orientation=={"100":45,"120":45,"150":54},orientation
 assert abs(summary[0]["min_angle_deg"]-19.69894)<.001
 assert abs(summary[1]["min_angle_deg"]-15.26532)<.001
 result=dict(study="P30F",date="2026-10-31",status="rigid-body model only",
      n_scenarios=len(rows),cabinet_mm=[1020,425,500],mat_mm=50,
      module_counts=MODES,summary=summary,low_driver_preferable_of_54=orientation,
      warnings=["Feet inset range 0/10/25mm is hypothetical and does not model foot friction or real floor contact.",
       "Driver center of mass and mass are assumed, not measured.",
       "Top push and tip angles are NOT allowed forces or a safety certification.",
       "Real impact loads, dynamic resonance, anchors, handling, children and pets omitted."],
      rows=rows)
 path=Path(__file__).resolve().parents[1]/"wyniki"/"p30f_1020_425_stabilnosc_20261031.json"
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"n":len(rows),"summary":summary,"orientation":orientation},
           ensure_ascii=False,indent=2))
if __name__=="__main__":main()
