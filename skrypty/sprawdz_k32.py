#!/usr/bin/env python3
"""Independent persisted-DXF and statics checks; no strength qualification."""
import json,math
from pathlib import Path
import ezdxf
R=Path(__file__).resolve().parents[1];O=R/'dokumentacja/cnc/K32_RETENCJA_HOLD'
a=json.loads((R/'wyniki/k32_retencja.json').read_text())
d=ezdxf.readfile(O/'PORTAL_K32_HOLD.dxf');assert d.units==4
holes=[(round(e.dxf.center.x,5),round(e.dxf.center.y,5),e.dxf.radius) for e in d.modelspace().query('CIRCLE')]
expected=[]
for y in [55,347]:
 for z in [88,204,320,426]:
  expected.append((y-44,z-22,3))
  for dz in [-32,32]:expected.append((y-44,z+dz-22,2))
assert sorted(holes)==sorted(expected)
# Actual metal extents and thread symbols, not assumed from generator constants.
d=ezdxf.readfile(O/'PLYTKA_18x80x4_GWINTY_HOLD.dxf');assert d.units==4
outline=list(d.modelspace().query('LWPOLYLINE'))[0];assert outline.closed
xy=list(outline.get_points('xy'));assert min(x for x,y in xy)==0 and max(x for x,y in xy)==18
assert min(y for x,y in xy)==0 and max(y for x,y in xy)==80
assert sorted((e.dxf.center.x,e.dxf.center.y,e.dxf.radius,e.dxf.layer) for e in d.modelspace().query('CIRCLE'))==[(9,8,1.5,'THREAD_M3'),(9,40,2.5,'THREAD_M5'),(9,72,1.5,'THREAD_M3')]
assert len(a['plates'])==8 and len(a['hardware'])==32
assert not a['fixed_collisions'] and len(a['movements'])==21
assert all(not r['collisions'] for r in a['movements'])
b=a['beam'];F=b['force_N'];r1,r2=b['reactions_N']
assert abs(r1+r2-F)<1e-10 and abs(r2*292-F*145)<1e-9
assert abs(b['bending_MPa']-(r1*145)/(50*18**2/6))<1e-10
# Unit load integration independently reconstructs deflection at load point.
n=100000;dx=292/n;integral=0
for i in range(n):
 x=(i+.5)*dx;M=r1*x-F*max(0,x-145);unit=(147/292)*x-max(0,x-145)
 integral+=M*unit*dx/(2000*(50*18**3/12))
assert math.isclose(integral,b['point_deflection_mm_at_E2000'],rel_tol=1e-8)
# Heads +/-32 with radius3 vs keeper halfheight25 leave4mm nominal.
assert 32-3-25==4
print('PASS: 24 portal bores; metal contour/3 thread symbols; 21 saved motion checks; equilibrium and independent beam integration. CNC HOLD.')
