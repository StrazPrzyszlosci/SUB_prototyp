#!/usr/bin/env python3
import itertools,json,math
from pathlib import Path
from k34_docisk_i_wrega import plate
R=Path(__file__).resolve().parents[1];a=json.loads((R/'wyniki/k34_docisk_i_wrega.json').read_text())
for c in a['preload']:
 assert math.isclose(c['bolt_N']-c['remaining_clamp_N'],c['external_N'],abs_tol=1e-10)
 assert c['remaining_clamp_N']>=0 and c['bolt_N']>=c['external_N']
for c in a['plate_cases']+a['convergence']:
 assert abs(c['reaction_sum_N']-c['applied_sum_N'])<1e-3
 assert min(c['pressure_MPa'])>=0
 assert max(abs(x-y) for x,y in zip(c['pressure_MPa'],reversed(c['pressure_MPa'])))<1e-6
assert abs(a['convergence'][-1]['peak_gross_strip_pressure_MPa']/a['convergence'][-2]['peak_gross_strip_pressure_MPa']-1)<1e-4
# Independent linear scaling check (contact set unchanged) and rigid-plate limit.
p=plate(150,200000,300,15)
assert math.isclose(p['peak_gross_strip_pressure_MPa']*2,a['convergence'][0]['peak_gross_strip_pressure_MPa'],rel_tol=1e-7)
r=plate(150,2e8,600,30)
assert abs(r['peak_gross_strip_pressure_MPa']-660/1440)<.002
w=a['loss_of_front_edge_bond'];assert abs(sum(w['support_reactions_N'])+w['applied_N'])<1e-5
for dim,n in [('depth',3),('height',2)]:
 gaps=[-sum(t)-cut for t in itertools.product((-.5,.5),repeat=n) for cut in (-.1,.1)]
 assert [min(gaps),max(gaps)]==a['frame_fit'][dim+'_total_gap_range_mm']
print('PASS:12 preload states;9 contact runs/equilibrium/symmetry; convergence, scaling, rigid limit; support equilibrium;24 stock corners. CNC HOLD.')
