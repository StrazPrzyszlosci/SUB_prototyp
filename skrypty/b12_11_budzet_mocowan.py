#!/usr/bin/env python3
"""B12-11: robust geometric screening, NOT physical testing or CNC.
Python 3 standard library only. Run from repository root.
"""
import itertools as it, math, json, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]; O=R/'wyniki'; O.mkdir(exist_ok=True)
BOLT=184.0
SOLIDS=[(0,22,44,403,0,500),(22,998,44,403,0,22),
(22,998,44,403,478,500),(448,470,44,54,44,456),
(448,470,44,403,22,44),(448,470,44,403,456,478)]

def polygon(cx,deg,ri,ro,w):
 a=math.radians(deg);u=(math.cos(a),math.sin(a));v=(-u[1],u[0])
 return [(cx+r*u[0]+s*v[0],250+r*u[1]+s*v[1])
         for r,s in [(ri,-w/2),(ro,-w/2),(ro,w/2),(ri,w/2)]]

def overlap(a,b):
 for p in [a,b]:
  for i,(x,z) in enumerate(p):
   X,Z=p[(i+1)%len(p)];axis=(z-Z,X-x)
   if not any(abs(t)>1e-12 for t in axis):continue
   av=[q[0]*axis[0]+q[1]*axis[1] for q in a]
   bv=[q[0]*axis[0]+q[1]*axis[1] for q in b]
   if max(av)<=min(bv)+1e-9 or max(bv)<=min(av)+1e-9:return False
 return True

def hit(p,depth,s,c):
 x0,x1,y0,y1,z0,z1=s
 if 44+depth<=y0+1e-9 or y1<=44+1e-9:return False
 return overlap(p,[(x0-c,z0-c),(x1+c,z0-c),(x1+c,z1+c),(x0-c,z1+c)])

layouts=[]
for cx,phase,ri,ro,w,depth in it.product([231,235],[0,22.5],[178,178.9,180],[205,211,217],[24,36,48],[10,20,30]):
 pads=[polygon(cx,phase+45*i,ri,ro,w) for i in range(8)]
 n={str(c):sum(any(hit(p,depth,solid,c) for solid in SOLIDS) for p in pads) for c in [0,1,2]}
 assert n['0']<=n['1']<=n['2']
 layouts.append(dict(cx=cx,phase=phase,ri=ri,ro=ro,w=w,depth=depth,collisions=n))
assert len(layouts)==324
obs={str(c):sum(x['collisions'][str(c)]==0 for x in layouts) for c in [0,1,2]}

radial=[]
for d,web,gap,rb,unc in it.product([4,6,8,10],[1,2,3],[.5,1,2],[170,175,177.9,180],[0,.5,1,2]):
 cap=BOLT-d/2-web-gap
 radial.append(dict(d=d,web=web,gap=gap,basket_radius=rb,radial_uncertainty=unc,
                    basket_radius_max=cap,slack=round(cap-rb-unc,3),robust=(rb+unc<=cap+1e-9)))
assert len(radial)==576

coupled=[]
for x,rb,unc,d,web in it.product(layouts,[175,177.9,180],[0,1,2],[6,8],[1,2]):
 good=x['collisions']['2']==0 and x['ri']>=rb+unc+1-1e-9 and BOLT-d/2-x['ri']>=web-1e-9
 coupled.append(dict(cx=x['cx'],phase=x['phase'],ri=x['ri'],ro=x['ro'],width=x['w'],depth=x['depth'],
                     basket_radius=rb,uncertainty=unc,insert_outer_d=d,wood_web_min=web,pass_screen=good))
assert len(coupled)==11664

axial=[]
for length,depth,minimum in it.product(range(60,81),[10,20,30],[6,8,10,14]):
 # Hypothetical flange 10..11, MDF 43.5..44.5, gasket 0..1.5, washer 0..1.
 emin=length-58.;emax=length-53.5;nom=length-55.75
 axial.append(dict(length=length,block_depth=depth,min_engagement=minimum,
                   engagement_range=[emin,emax],nominal_pass=nom>=minimum and nom<=depth-3,
                   robust_pass=emin>=minimum and emax<=depth-1-3))
assert len(axial)==252
summary=dict(obstacle=dict(total=324,pass_by_clearance_mm=obs),
 radial=dict(total=len(radial),robust_pass=sum(x['robust'] for x in radial),
             max_basket_radius_for_1mm_gap_and_2mm_web={str(d):BOLT-d/2-3 for d in [4,6,8,10]}),
 coupled=dict(total=len(coupled),pass_count=sum(x['pass_screen'] for x in coupled),
              pass_by_basket_radius={str(r):sum(x['pass_screen'] for x in coupled if x['basket_radius']==r) for r in [175,177.9,180]},
              pass_by_uncertainty={str(u):sum(x['pass_screen'] for x in coupled if x['uncertainty']==u) for u in [0,1,2]}),
 axial=dict(total=252,nominal_pass=sum(x['nominal_pass'] for x in axial),
            robust_pass=sum(x['robust_pass'] for x in axial),
            robust_lengths_with_min8_by_block={str(t):sorted({x['length'] for x in axial if x['block_depth']==t and x['min_engagement']==8 and x['robust_pass']}) for t in [10,20,30]}))
assert obs=={'0':234,'1':234,'2':225}
assert summary['coupled']['pass_count']==2175
assert summary['axial']['robust_pass']==62
full=dict(study='B12-11',classification='HYPOTHETICAL geometry, not measurements',summary=summary,
 sources=['P39C surrogate geometry','B12-10 research','Dayton official mounting dimensions'],
 caveats=['No verified 3D basket or terminal clearance','No actual screw/insert/wood/adhesive strength',
          'Model bounds are not manufacturer tolerances','No real tool swept volume','NOT FOR CNC'],
 obstacle_cases=layouts,radial_cases=radial,coupled_cases=coupled,axial_cases=axial)
p=O/'b12_11_pelne_obliczenia.json';p.write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n')
h=hashlib.sha256(p.read_bytes()).hexdigest()
(O/'b12_11_podsumowanie.json').write_text(json.dumps({'summary':summary,'full_json_sha256':h,
 'input_assumptions':'see skrypty/b12_11_budzet_mocowan.py and report','status':'NOT CNC'},indent=2,ensure_ascii=False)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2));print('SHA256',h)
