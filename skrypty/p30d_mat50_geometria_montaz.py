#!/usr/bin/env python3
"""P30D: 50 mm rear mat, parametric shallow enclosures, rigid-body paths,
independent rectangular volume envelopes, simple plate and cavity proxies.
NO FEM cabin qualification, no hardware or safe CNC approvals.
Run: python skrypty/p30d_mat50_geometria_montaz.py
Requires numpy; imports P30A from the same repository.
"""
import json, math
from pathlib import Path
import numpy as np
import p30a_robust_geometry as p

CANDIDATES=[
 (1000,440,50,150,0),
 (1010,430,50,130,10),
 (1020,425,50,120,15),
 (1030,425,50,120,15),
 (1040,430,50,130,10),
 (1050,425,50,120,15),
 (1055,420,50,110,20)]
def build(c):
 w,d,mat_mm,rear_depth,small_shift=c
 L,br,mods,mat=p.geo(w,d,mat_mm)
 mods=[m.copy() for m in mods]
 for i,b in enumerate(mods):
  if i<4:b[:,1]-=small_shift
  elif (i-4)%8<4:
   mid=(b[0,1]+b[1,1])/2
   b[0,1]=mid-rear_depth/2
   b[1,1]=mid+rear_depth/2
 return L,br,mods,mat
def count_paths(c,clearance):
 L,br,mods,mat=build(c)
 placed=[];segments=0;static=[]
 for i,b in enumerate(mods):
  env=b+np.array([[-clearance]*3,[clearance]*3])
  if np.any(env[0]<0) or np.any(env[1]>L):static.append((i,"outside"))
  if any(p.intersect(env,x) for x in br):static.append((i,"brace"))
  if p.intersect(env,mat):static.append((i,"mat"))
  if any(p.intersect(env,x) for x in mods[:i]):static.append((i,"mod"))
 if static:return dict(passed=0,static_collisions=len(static),segments=0)
 try:
  prev=p.CLEARANCE;p.CLEARANCE=clearance
  for i,b in enumerate(mods):
   half=(b[1]-b[0])/2+clearance
   if math.hypot(half[0],half[2])>=144:raise ValueError("cutout")
   route=p.path_to(b.mean(axis=0),L,br+placed+[mat],half)
   if route is None:return dict(passed=i,static_collisions=0,segments=segments)
   for a,z in zip(route,route[1:]):
    sw=p.segment_box(np.array(a),np.array(z),half)
    assert not any(p.intersect(sw,o) for o in br+placed+[mat])
   segments+=len(route)-1;placed.append(b)
  return dict(passed=20,static_collisions=0,segments=segments)
 finally:p.CLEARANCE=prev
def plate(width_mm,depth_mm,E=2.1e9,n=33):
 a=width_mm/1000;b=depth_mm/1000;h=.022;rho=730;nu=.3
 rigidity=E*h**3/(12*(1-nu**2))
 f=math.pi/2*math.sqrt(rigidity/(rho*h))*(1/a**2+1/b**2)
 disp=0
 for m in range(1,n+1,2):
  for j in range(1,n+1,2):
   qmn=16*1000/(math.pi**2*m*j)
   wmn=qmn/(rigidity*math.pi**4*((m/a)**2+(j/b)**2)**2)
   disp+=(-1)**((m-1)//2+(j-1)//2)*wmn
 return dict(ssss_f11_Hz=f,ssss_center_um_1000Pa=disp*1e6)
def inside_modes(L):
 return sorted([dict(indices=[i,j,k],frequency_hz=343/2*math.sqrt(
      (i/(L[0]/1000))**2+(j/(L[1]/1000))**2+(k/(L[2]/1000))**2))
   for i in range(4) for j in range(4) for k in range(4)
   if (i,j,k)!=(0,0,0)],key=lambda x:x["frequency_hz"])[:5]
def net_calcs(c):
 L,br,mods,mat=build(c);w,d,*_=c
 br_l=sum(p.volume(x) for x in br)/1e6
 fill_env_l=(p.volume(mat)-sum(p.overlap_volume(mat,b) for b in br))/1e6
 v0=math.prod(L)/1e6-br_l-5-.175-fill_env_l*20/1380
 vol=[p.volume(x)/1e6 for x in mods]
 res={}
 for target in (100,120,150):
  possibilities=[(abs(v0-sum(vol[4:4+n])-sum(vol[:s])-target),n,s,
         v0-sum(vol[4:4+n])-sum(vol[:s]))
         for n in range(17) for s in range(5)]
  _,n,s,v=min(possibilities,key=lambda x:(x[0],x[1]+x[2]))
  # Independent extreme stress corners; not calibration or statistical tolerances.
  def extremal(upper):
   gross=math.prod(L+(2 if upper else -2))/1e6
   braces=br_l*(.95 if upper else 1.05)
   driver=2 if upper else 8;hardware=.05 if upper else .3
   fill=fill_env_l*(10/1400 if upper else 30/1300)
   deviation=-.5 if upper else +.5
   elements=mods[:s]+mods[4:4+n]
   displaced=sum(math.prod((x[1]-x[0])+deviation)/1e6 for x in elements)
   return gross-braces-driver-hardware-fill-displaced
  res[str(target)]=dict(large=n,small=s,nominal_l=v,low_l=extremal(False),high_l=extremal(True))
 # MDF panel material volume: shell minus cylindrical bore; 8mm closed insert shells.
 shell=(w*d*500-math.prod(L)-math.pi*(355.8/2)**2*44)/1e6
 mass={}
 for key,v in res.items():
  included=mods[:v["small"]]+mods[4:4+v["large"]]
  inner_shell=lambda z:math.prod(z[1]-z[0]-16)
  inserts_l=sum((p.volume(z)-inner_shell(z))/1e6 for z in included)
  mass[key]=((shell+br_l+inserts_l)*730/1000)
 return res,mass,br_l,v0
def main():
 rows=[]
 for c in CANDIDATES:
  L,br,mods,mat=build(c)
  select,mass,br_l,v0=net_calcs(c)
  check=count_paths(c,3)
  assert check["passed"]==20,c
  rows.append(dict(candidate=list(c),net_empty_l=v0,brace_l=br_l,
   volume=select,mdf_mass_kg_at_730_by_volume=mass,
   total_depth_max_mm=c[1]+56,depth_margin_mm=500-c[1]-56,
   mat_mm=c[2],paths_at_3mm=check,
   empty_cavity_first_modes=inside_modes(L),
   isolated_plate_bay_proxy=plate(426,L[1])))
 tests=[]
 for c,values in [
  (CANDIDATES[0],[3,4]),
  (CANDIDATES[1],[3,6]),
  (CANDIDATES[2],[3,4,5,6,8])]:
  for clearance in values:tests.append(dict(candidate=list(c),
      clearance_mm=clearance,**count_paths(c,clearance)))
 assert len(tests)==9
 selected=rows[2]
 assert abs(selected["volume"]["120"]["nominal_l"]-119.919)<.01
 assert abs(selected["volume"]["100"]["nominal_l"]-100.119)<.01
 assert all(t["passed"]==20 for t in tests if t["candidate"]==list(CANDIDATES[2]) and t["clearance_mm"]<=6)
 assert any(t["passed"]<20 for t in tests if t["candidate"]==list(CANDIDATES[0]) and t["clearance_mm"]==4)
 # Series convergence check, independent analytical truncations.
 L=build(CANDIDATES[2])[0]
 delta=abs(plate(426,L[1],n=17)["ssss_center_um_1000Pa"]-
   plate(426,L[1],n=33)["ssss_center_um_1000Pa"])
 assert delta<.0001
 out=dict(study="P30D",date="2026-10-31",cases=rows,clearance_tests=tests,
  navier_convergence_um_1000Pa=delta,
  conclusion="1020x425x500mm 50mm rear mat, shorter rear 120mm inserts, translated small inserts; CONDITIONAL candidate, no CNC approval",
  caveats=["Model uses old P20D basket AABB and unverified 5l nominal driver displacement.",
   "Volume stress includes independent ranges; these are not measured tolerances or probability intervals.",
   "Routes are axis-aligned translations in predefined roadmap; tool, fasteners, hands, wiring and gravity omitted.",
   "SSSS plate mode is one isolated UNPERFORATED bay proxy, not measured cabinet f1; P18E coupled f1 near 143Hz.",
   "Rigid EMPTY box mode is not 3D field including changed braces, real insert walls, acoustic mat and panel motion.",
   "Same rear mat 50mm does NOT certify unchanged absorption; all updated geometry must be recalculated by P21G FV/FEM.",
   "Max device depth assumes unknown rest projection, clearance, deflection and rear protrusion within P20D scenario.",
   "No qualified isolation/mains PCB amplifier or active transducer protection can be inferred."])
 target=Path(__file__).resolve().parents[1]/"wyniki"/"p30d_50mm_multimodel_20261031.json"
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(dict(selected=selected,clearance_tests=tests,
    navier_convergence_um_1000Pa=delta),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
