#!/usr/bin/env python3
import itertools,json,math
from pathlib import Path
import ezdxf
from k36_bank_z_pomiarow import build,KEYS,front_hit
R=Path(__file__).resolve().parents[1];a=json.loads((R/'wyniki/k36_bank_z_pomiarow.json').read_text())
assert a['corner_count']==512 and not a['plate_static_collisions']
fail=[c for c in a['motions'] if c['collisions']]
assert len(fail)==4 and all(c['kind']=='tool' and c['diameter_mm']==20 and c['y']==55 for c in fail)
assert len([c for c in a['motions'] if c['kind']!='tool' or c['diameter_mm']==18])==25
for vals in itertools.product((21.5,22.5),repeat=9):
 t=dict(zip(KEYS,vals));m=build(t);p={x['id']:x for x in m['parts']}
 def near(x,y):assert abs(x-y)<1e-8
 near(p['RAIL_A_0_F']['o'][2]+p['RAIL_A_0_F']['s'][2],40)
 near(p['RAIL_A_0_F']['o'][2]-t['BOTTOM'],.2)
 near(p['TOP_KEEPER_A_F']['o'][2],466)
 near(500-t['TOP']-(466+p['TOP_KEEPER_A_F']['s'][2]),.2)
 near(p['RAIL_A_1_F']['o'][0]-(448+t['PORTAL']),.2)
 near(750-(p['RAIL_A_1_F']['o'][0]+p['RAIL_A_1_F']['s'][0]),.2)
 near(p['RAIL_B_1_F']['o'][0]-(750+t['MID_PORTAL']),.2)
 near(1080-t['SIDE_R']-(1018+p['BACKSTOP_0']['s'][0]),.2)
 assert p['CHANNEL_WEB_A_F']['o'][0]-(448+t['PORTAL']+4)>=.2-1e-9
 assert all(min(x['s'])>0 for x in m['parts'])
O=R/'dokumentacja/cnc/K36_KRAWEDZ_BLOKADY_HOLD'
for name,holes in [('KROTKA_CZOLO_YZ_HOLD.dxf',2),('DLUGA_CZOLO_YZ_HOLD.dxf',6)]:
 d=ezdxf.readfile(O/name);assert d.units==4
 ms=d.modelspace();assert len(ms.query('CIRCLE'))==holes
 main=[c for c in ms.query('CIRCLE') if c.dxf.layer=='DRILL_THRU']
 assert sorted(c.dxf.center.x+47 for c in main)==[55,347]
 assert all(c.dxf.center.y==25 and c.dxf.radius==3 for c in main)
 p=list(ms.query('LWPOLYLINE'))[0];assert p.closed and max(v[0] for v in p.get_points())==310
p=list(ezdxf.readfile(O/'KROTKA_OBRYS_XY_Z50_HOLD.dxf').modelspace().query('LWPOLYLINE'))[0];pts=list(p.get_points('xyb'))
for i,(x,y,b) in enumerate(pts):
 if b:
  X,Y,_=pts[(i+1)%len(pts)];assert abs(math.hypot(X-x,Y-y)*(1+b*b)/(4*abs(b))-4)<1e-9
# Explicit retained counterexample: old barY45 collides, trimmedY47 clears.
assert front_hit(dict(o=[430,45,63],s=[18,312,50]))
assert not front_hit(dict(o=[430,47,63],s=[18,310,50]))
print('PASS:512 interface corners;25 selected paths;4 expected20mm-tool failures;3 DXF/R4/axes; old-bar counterexample. CNC HOLD.')
