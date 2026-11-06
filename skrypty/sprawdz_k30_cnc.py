#!/usr/bin/env python3
"""Independent DXF re-read, geometric boundary checks and stock-fit counterexamples."""
from pathlib import Path
import json, math, itertools
import ezdxf
from ezdxf import bbox
R=Path(__file__).resolve().parents[1]
c=json.loads((R/'dane/k30_zalozenia.json').read_text());ps=json.loads((R/'wyniki/k30_czesci.json').read_text());r=json.loads((R/'wyniki/k30_stale_kanaly_audyt.json').read_text())
folder=R/'dokumentacja/cnc/K30_STALE_KANALY_HOLD'
assert len(list(folder.glob('*.dxf')))==len(ps)==102
checks=[]
for p in ps:
 d=ezdxf.readfile(folder/(p['id']+'.dxf'));m=d.modelspace()
 outer=list(m.query('*[layer=="CUT_OUTER"]'));assert len(outer)==1
 b=bbox.extents(outer);a,v=p['flat']
 assert abs(b.extmin.x)<1e-8 and abs(b.extmin.y)<1e-8
 assert abs(b.extmax.x-a)<1e-7 and abs(b.extmax.y-v)<1e-7
 assert d.units==4 and not d.audit().errors
 assert min(a,v)>=50 and max(a,v)<=1400 and a+v<=2700
 assert a*v*p['thickness']/1e9*730<30
 assert p['thickness'] in c['manufacturer']['mdf_thickness_mm']
 for e in m.query('CIRCLE'):
  u,vv,rr=e.dxf.center.x,e.dxf.center.y,e.dxf.radius
  assert rr<=u<=a-rr and rr<=vv<=v-rr,(p['id'],u,vv,rr)
 for e in m.query('LWPOLYLINE'):
  assert e.closed
  xy=list(e.get_points('xy'))
  assert all(math.dist(xy[i],xy[(i+1)%len(xy)])>1e-8 for i in range(len(xy)))
  if e.dxf.layer=='CUT_INNER':
   pts=list(e.get_points('xyb'))
   for i,(x,y,bulge) in enumerate(pts):
    if bulge:
     X,Y,_=pts[(i+1)%len(pts)];chord=math.hypot(X-x,Y-y)
     radius=chord*(1+bulge**2)/(4*abs(bulge))
     assert abs(radius-4)<1e-6
 checks.append(p['id'])
for k in ('box_paths','keeper_paths','separator_paths','tool_paths'):
 assert all(x['pass_nominal'] for x in r[k]),k
assert not r['fixed_box_collisions'] and not r['keeper_mat_collisions']
# Independent circumscribed-rectangle entry check for each component.
assert min(x['entry_margin_mm'] for x in r['box_paths'])>30
assert min(x['entry_margin_mm'] for x in r['keeper_paths'])>15
# Manufacturing counterexample: a nominal 244mm bottom between two nominal
# 8mm walls in 260mm end cheeks. Supplier tolerance is not a zero-clearance fit.
fits=[]
for outer,inner,t1,t2 in itertools.product((259.9,260.1),(243.9,244.1),(7.5,8.5),(7.5,8.5)):
 fits.append(dict(outer=outer,inner_panel=inner,left_stock=t1,right_stock=t2,clearance=outer-t1-t2-inner))
minfit=min(x['clearance'] for x in fits);maxfit=max(x['clearance'] for x in fits)
assert minfit<0<maxfit
# Independent pressure: uniform closed-box pressure has zero whole-body resultant;
# panel/joint pressure stress still requires its own check. Do not add p*A to rail load.
# Two planes + thickness datum stack for 2mm nominal vertical play.
vertical_min=2-2*.2-.5-.1
assert abs(vertical_min-1.0)<1e-10
out=dict(status='NOMINAL_CAD_CHECKS_PASS_PRODUCTION_HOLD',checked_dxf=len(checks),
  paths={k:len(r[k]) for k in ('box_paths','keeper_paths','separator_paths','tool_paths')},
  box_entry_margin_min_mm=min(x['entry_margin_mm'] for x in r['box_paths']),
  keeper_entry_margin_min_mm=min(x['entry_margin_mm'] for x in r['keeper_paths']),
  nominal_244_panel_fit_corners=fits,nominal_244_panel_clearance_extrema_mm=[minfit,maxfit],
  vertical_clearance_min_assumed_jig_mm=vertical_min,
  conclusions=['No machining approval: nominal 244mm box bottom can interfere by 1.2mm with permitted stock thickness.',
   'Regenerate box panel widths from measured batch thickness and qualified glue gap.',
   'The 1mm vertical reserve depends on +/-0.2mm assembly datums, not supplier CNC tolerance alone.',
   'No material allowable, fastener torque, terminal cutout or real driver fit has been fabricated or tested.'])
(R/'wyniki/k30_niezalezna_kontrola.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='nominal_244_panel_fit_corners'},indent=2))
