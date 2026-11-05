#!/usr/bin/env python3
"""Independent regression of K31 hole axes, envelope invariance and metrology gate."""
import hashlib,importlib.util,itertools,json,math,subprocess,sys
from pathlib import Path
import ezdxf
from ezdxf import bbox
R=Path(__file__).resolve().parents[1];P=R/'skrypty/k31_zlacze_i_pasowania.py';O=R/'dokumentacja/cnc/K31_ZLACZE_I_PASOWANIA_HOLD'
spec=importlib.util.spec_from_file_location('k31',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for f in sorted(O.glob('*.dxf')):
 d=ezdxf.readfile(f);assert d.units==4 and not d.audit().errors
 outer=list(d.modelspace().query('*[layer=="CUT_OUTER"]'));assert len(outer)==1
 ext=bbox.extents(outer)
 holes=list(d.modelspace().query('CIRCLE'))
 if f.name.startswith('STOP'):
  assert math.isclose(ext.size.x,312) and math.isclose(ext.size.y,50)
  assert sorted((h.dxf.center.x,h.dxf.center.y,h.dxf.radius) for h in holes)==[(10,25,3),(302,25,3)]
 else:
  assert f.name.startswith('PORTAL') and len(holes)==8
  assert sorted(set(round(h.dxf.center.x,8) for h in holes))==[11,303]
 for e in d.modelspace().query('LWPOLYLINE'):
  assert e.closed
  xy=list(e.get_points('xy'));assert all(math.dist(xy[i],xy[(i+1)%len(xy)])>1e-8 for i in range(len(xy)))
# Analytically reconstruct the cavity and actual TWO distinct gaps, independent
# of collision routine; test nominal, extrema and mixed arbitrary decimal stock.
cases=[dict.fromkeys(m.FACES,8),dict(zip(m.FACES,[7.57,8.31,8.12,7.91,8.07,7.88]))]
cases += [dict(zip(m.FACES,t)) for t in itertools.product((7.5,8.5),repeat=6)]
for ts in cases:
 for L,B,H in ((267.1,260,96),(253,260,76)):
  parts={p['id']:p for p in m.fit_panels(L,B,H,ts,.2)}
  assert [max(p['o'][j]+p['s'][j] for p in parts.values()) for j in range(3)]==[L,B,H]
  bot=parts['ZB'];front=parts['YF'];rear=parts['YR'];left=parts['XL'];right=parts['XR']
  for gap in [bot['o'][0]-left['s'][0],right['o'][0]-bot['o'][0]-bot['s'][0],bot['o'][1]-front['s'][1],rear['o'][1]-bot['o'][1]-bot['s'][1]]:
   assert abs(gap-.2)<1e-10
# Failed release gate must not replace existing drawings or outputs.
tracked=list(O.glob('*'))+list((R/'wyniki').glob('k31_*'))
before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in tracked if f.is_file()}
r=subprocess.run([sys.executable,str(P),'--require-measured'],capture_output=True,text=True)
assert r.returncode!=0 and 'BLOCKED' in r.stderr
assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in before.items())
a=json.loads((R/'wyniki/k31_zlacze_pasowania.json').read_text())
assert all(not x['collisions'] for x in a['motions']+a['robust_bolts'])
assert all(x['collisions'] for x in a['bolt_protrusion'] if x['y']==341)
assert len(a['motions'])==21
assert a['thread_stack'][1]['full_thread_cases']==32 and a['thread_stack'][0]['full_thread_cases']==16
assert not a['fit']['measurements_real']
print('K31 PASS: 5 DXF, 132 stock/envelope cases, 21 motion checks, 8 bolt sensitivity checks; unmeasured export rejected without writes. CNC HOLD.')
