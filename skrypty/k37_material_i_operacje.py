#!/usr/bin/env python3
"""K37 per-part bank stock and manufacturing operations; research geometry only."""
import argparse,copy,hashlib,itertools,json,math
from pathlib import Path
from k35_korpus_z_pomiarow import KEYS
from k36_bank_z_pomiarow import build
from k31_zlacze_i_pasowania import hit
R=Path(__file__).resolve().parents[1]
def required():
 m=build(dict.fromkeys(KEYS,22.));d={}
 for p in m['parts']:
  id=p['id']
  if id.startswith('CHANNEL_WEB'):d[id]=8.
  elif id.startswith('RAIL') and '_0_' not in id:d[id]=18.
  elif id=='BACKSTOP_SMALL_EXTRA':d[id]=25.
 for p in m['plates']:d[p['id']]=4.
 return d
NOM=required()
def model(t,bank):
 m=build(t);g=.2
 for p in m['plates']:p['s'][0]=bank[p['id']]
 maxplate=max(bank[p['id']] for p in m['plates']);end=448+t['PORTAL']
 for p in m['parts']:
  id=p['id']
  if id.startswith('CHANNEL_WEB'):
   th=bank[id];p['s'][1]=th;p['o'][1]=68-th if id.endswith('_F') else 332
   if '_A_' in id:
    stop=p['o'][0]+p['s'][0];p['o'][0]=max(474,end+maxplate+g);p['s'][0]=stop-p['o'][0]
  elif id.startswith('RAIL'):
   if '_0_' not in id:
    top=p['o'][2]+p['s'][2];p['s'][2]=bank[id];p['o'][2]=top-bank[id]
   p['o'][1]=68+g if id.endswith('_F') else 282-g
  elif id.startswith('TOP_KEEPER'):p['o'][1]=68+g if id.endswith('_F') else 282-g
  elif id=='BACKSTOP_SMALL_EXTRA':p['s'][0]=bank[id];p['o'][0]=1018-bank[id]
  elif id.startswith('SEP_'):
   # Finish from10 stock to7.8; centred in fixed8 gap. Explicit sliding clearance.
   p['o'][0]+=.1;p['s'][0]=7.8
  p['thickness']=p['s'][p['axis']];p['flat']=[p['s'][j] for j in p['uv']]
 return m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--require-measured',action='store_true');a=ap.parse_args()
 src=R/'dane/k37_pomiary_banku.json';data=json.loads(src.read_text());vals=data['thickness_mm']
 measured=data.get('status')=='measured' and bool(data.get('measurement_record')) and all(type(vals.get(k)) in (int,float) and math.isfinite(vals[k]) and abs(vals[k]-v)<= (.2 if k.startswith('P') else .5) for k,v in NOM.items())
 if a.require_measured and not measured:raise SystemExit('BLOCKED: bank thickness measurements missing; no output written.')
 bank=vals if measured else NOM;t=dict.fromkeys(KEYS,22.);m=model(t,bank)
 # Independent parameter sweep, not exponential full combination claim.
 cases=[]
 for id,v in NOM.items():
  for sign in (-1,1):
   b=dict(NOM);b[id]=v+sign*(.2 if id.startswith('P') else .5);mm=model(t,b)
   cases.append(dict(part=id,value=b[id],all_dimensions_positive=all(min(p['s'])>0 for p in mm['parts']),
    box_datums=mm['box_datums']))
 operations=[]
 for p in m['parts']:
  id=p['id'];op=None
  if id.startswith('RAIL') and '_0_' in id:op=('face_machine',22,[17.3,18.3])
  elif id.startswith('TOP_KEEPER'):op=('face_machine',18,[11.3,12.3])
  elif id.startswith('BACKSTOP_') and id!='BACKSTOP_SMALL_EXTRA':op=('laminate_then_face_machine',43.2,[39.3,40.3])
  elif id.startswith('SEP_'):op=('face_machine_separator',10,[7.8,7.8])
  if op:
   lower=op[1]-(1. if op[0].startswith('laminate') else .5)
   operations.append(dict(part=id,operation=op[0],nominal_blank_thickness_mm=op[1],finished_range_mm=op[2],minimum_nominal_removal_mm=lower-op[2][1],release='HOLD: actual blank, flatness, final thickness and adhesive required'))
 # Explicit interval arithmetic for residual errors AFTER thickness propagation.
 tol=dict(end_bond_gap=dict(target_mm=.2,cut_error_mm=.1,position_error_mm=.1,measurement_error_mm=.05,range_mm=[-.05,.45],pass_positive=False),
  proposed_tighter_process=dict(target_mm=.2,cut_error_mm=.05,position_error_mm=.05,measurement_error_mm=.05,range_mm=[.05,.35],verified_by_supplier=False),
  separator=dict(channel_gap_mm=8,finished_target_mm=7.8,finished_error_mm=.1,remaining_gap_range_mm=[.1,.3],note='Assumes fixed exact8 mating gap; box dimensional errors NOT included.'),
  metal_front_ligament=dict(nominal_mm=5,edge_error_mm=.1,axis_error_mm=.1,radius_error_mm=.05,min_mm=4.75,qualified_strength=False),
  tool_front_reserve=dict(nominal_mm=.9,residual_front_mm=.15,axis_mm=.1,tool_radius_mm=.1,min_mm=.55,note='Assumed residual budget, no actual tool verification.'))
 # Longitudinal local geometry checks of thicker plates vs front webs.
 platechecks=[]
 for tp in (21.5,22.5):
  for metal in (3.8,4.2):
   tt=dict(t);tt['PORTAL']=tp;bb=dict(NOM)
   for k in bb:
    if k.startswith('P'):bb[k]=metal
   mm=model(tt,bb);webs=[p for p in mm['parts'] if p['id'].startswith('CHANNEL_WEB_A')]
   platechecks.append(dict(portal=tp,plate=metal,collisions=[[p['id'],w['id']] for p in mm['plates'] for w in webs if hit(p,w)]))
 out=dict(status='CNC_HOLD',input_status='measured_bank_only' if measured else 'synthetic_bank',nominal_model=m,per_part_sweep=cases,operations=operations,tolerances=tol,plate_checks=platechecks,
  limits=['No full combined tolerance motion certification','Shell still synthetic22 here; K35 measurement gate separate','No actual machining capability, tool, adhesive or strength evidence','Insert panel dimensions still governed separately by K31'])
 (R/'wyniki/k37_material_i_operacje.json').write_text(json.dumps(out,indent=2)+'\n')
 files=['brief_system_audio_DIY_v0.6.md','skrypty/k36_bank_z_pomiarow.py','skrypty/k37_material_i_operacje.py','dane/k37_pomiary_banku.json']
 (R/'wyniki/k37_manifest.json').write_text(json.dumps({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
 print(json.dumps({'bank_inputs':len(NOM),'single_parameter_cases':len(cases),'machining_operations':len(operations),'residual_gap':tol['end_bond_gap']['range_mm']},indent=2))
if __name__=='__main__':main()
