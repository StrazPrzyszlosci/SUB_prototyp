#!/usr/bin/env python3
import hashlib,itertools,json,subprocess,sys
from pathlib import Path
from k35_korpus_z_pomiarow import model,KEYS
R=Path(__file__).resolve().parents[1]
for values in itertools.product((21.5,22.5),repeat=9):
 t=dict(zip(KEYS,values));m=model(t);p={x['id']:x for x in m['parts']};eps=1e-9
 def near(a,b):assert abs(a-b)<eps,(a,b)
 near(p['BACK']['o'][1]+p['BACK']['s'][1],432);near(p['TOP']['o'][2]+p['TOP']['s'][2],500)
 near(p['SIDE_R']['o'][0]+p['SIDE_R']['s'][0],1080)
 near(p['FR2']['o'][1]-t['FR1'],.1)
 for k in ('SIDE_L','SIDE_R','TOP','BOTTOM','PORTAL','MID_PORTAL'):
  near(p[k]['o'][1]-(p['FR2']['o'][1]+t['FR2']),.2)
  near(p['BACK']['o'][1]-(p[k]['o'][1]+p[k]['s'][1]),.2)
 for k in ('PORTAL','MID_PORTAL'):
  near(p[k]['o'][2]-t['BOTTOM'],.2);near(p['TOP']['o'][2]-(p[k]['o'][2]+p[k]['s'][2]),.2)
  for l,g in zip(p[k]['windows_local_yz'],p[k]['windows_global_yz']):
   for j in range(4):near(l[j]+p[k]['o'][1+j%2],g[j])
 near(p['BOTTOM']['o'][0]-t['SIDE_L'],.2)
 near(p['SIDE_R']['o'][0]-(p['BOTTOM']['o'][0]+p['BOTTOM']['s'][0]),.2)
 assert m['bank_interface_issues']
# Deliberately asymmetric, non-corner measurements preserve all24 global hole axes.
t={k:21.6+.1*i for i,k in enumerate(KEYS)};m=model(t);p=next(p for p in m['parts'] if p['id']=='PORTAL')
assert len(p['holes_local_yz'])==24
for l,g in zip(p['holes_local_yz'],p['holes_global_yz']):
 assert abs(l[0]+p['o'][1]-g[0])<1e-9 and abs(l[1]+p['o'][2]-g[1])<1e-9
files=list((R/'wyniki').glob('k35*'));before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
r=subprocess.run([sys.executable,str(R/'skrypty/k35_korpus_z_pomiarow.py'),'--require-measured'],capture_output=True,text=True)
assert r.returncode!=0 and 'BLOCKED' in r.stderr
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
print('PASS:512 corners, shell extents/glue gaps, invariant global windows and24 axes, missing-measurement refusal without output changes. CNC HOLD.')
