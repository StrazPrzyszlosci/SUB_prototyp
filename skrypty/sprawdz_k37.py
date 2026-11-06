#!/usr/bin/env python3
import hashlib,json,subprocess,sys
from pathlib import Path
from k37_material_i_operacje import NOM,model,KEYS
R=Path(__file__).resolve().parents[1];a=json.loads((R/'wyniki/k37_material_i_operacje.json').read_text())
assert len(a['per_part_sweep'])==50 and all(x['all_dimensions_positive'] for x in a['per_part_sweep'])
assert len(a['operations'])==16 and all(x['minimum_nominal_removal_mm']>0 for x in a['operations'])
assert all(not x['collisions'] for x in a['plate_checks'])
for sign in (-1,1):
 b={k:v+sign*(.2 if k.startswith('P') else .5) for k,v in NOM.items()};m=model(dict.fromkeys(KEYS,22),b)
 for p in m['parts']:
  if p['id'].startswith('CHANNEL_WEB'):
   assert abs((p['o'][1]+p['s'][1] if p['id'].endswith('_F') else p['o'][1])-(68 if p['id'].endswith('_F') else 332))<1e-8
  if p['id'].startswith('RAIL') and '_0_' not in p['id']:
   row=int(p['id'].split('_')[2]);assert abs(p['o'][2]+p['s'][2]-[40,156,272,388][row])<1e-8
x=a['tolerances']['end_bond_gap'];e=x['cut_error_mm']+x['position_error_mm']+x['measurement_error_mm']
assert abs(x['target_mm']-e-x['range_mm'][0])<1e-9 and x['range_mm'][0]<0
files=list((R/'wyniki').glob('k37*'));before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
r=subprocess.run([sys.executable,str(R/'skrypty/k37_material_i_operacje.py'),'--require-measured'],capture_output=True,text=True)
assert r.returncode!=0 and 'BLOCKED' in r.stderr
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
print('PASS:50 per-part perturbations,16 operation allowances,4 plate cases, invariant supports, residual-gap counterexample, no-write measurement refusal. CNC HOLD.')
