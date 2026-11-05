#!/usr/bin/env python3
import json,math
from pathlib import Path
import ezdxf
R=Path(__file__).resolve().parents[1];O=R/'dokumentacja/cnc/K33_BLOKADA_METAL_HOLD'
a=json.loads((R/'wyniki/k33_sztywna_blokada.json').read_text())
assert len(a['checks'])==5
assert all(not c['collisions'] and c['aperture_margin_mm']>0 for c in a['checks'])
for label,n in [('KROTKA_CZOL0_YZ_HOLD.dxf',2),('DLUGA_CZOL0_YZ_HOLD.dxf',6),('KOLNIERZ_80x50x4_HOLD.dxf',4)]:
 d=ezdxf.readfile(O/label);assert d.units==4 and len(d.modelspace().query('CIRCLE'))==n
 for p in d.modelspace().query('LWPOLYLINE'):assert p.closed
 if label.startswith('DLUGA'):
  assert sorted((c.dxf.center.x,c.dxf.center.y) for c in d.modelspace().query('CIRCLE') if c.dxf.layer=='THREAD_M4_BLIND10')==[(135,10),(135,40),(175,10),(175,40)]
d=ezdxf.readfile(O/'KROTKA_OBRYS_XY_Z50_HOLD.dxf');p=list(d.modelspace().query('LWPOLYLINE'))[0]
pts=list(p.get_points('xyb'));assert p.closed and max(x for x,y,b in pts)==40 and max(y for x,y,b in pts)==312
assert len([b for x,y,b in pts if b])==2
for i,(x,y,b) in enumerate(pts):
 if b:
  X,Y,_=pts[(i+1)%len(pts)];r=math.hypot(X-x,Y-y)*(1+b*b)/(4*abs(b));assert abs(r-4)<1e-9
# Closed-form point-load + uniform-load deflection independently verifies integration.
L=292;x=145;I=50*18**3/12
for b in a['beam']:
 P,q,E=b['point_force_N'],b['uniform_N_mm'],b['E_MPa']
 exact=P*x*x*(L-x)**2/(3*E*I*L)+q*x*(L**3-2*L*x*x+x**3)/(24*E*I)
 assert math.isclose(exact,b['deflection_mm'],rel_tol=1e-8)
 assert math.isclose(sum(b['reactions_N']),P+q*L,rel_tol=1e-12)
# Flange screws: M4x12 minus4 flange =8 engagement, inside10 nominal thread depth.
assert 12-4==a['extended']['thread_nominal_engagement_mm']<a['extended']['thread_blind_depth_mm']
print('PASS: 4 DXF, R4 roots, 5 stored service routes, closed-form beam deflection, reaction balance. CNC HOLD.')
