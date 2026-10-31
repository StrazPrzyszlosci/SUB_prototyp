#!/usr/bin/env python3
"""Read-only audit of manufacturer-verified numerical facts.
For original PDF snapshots use odtworz_dokumentacje_producentow.py.
This is CONSISTENCY CONTROL, not external measurement.
"""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'dane/karty_producentow/2026-10-31_9_marek_weryfikacja.json'
RHO=1.2;C=343
def run():
 d=json.loads(F.read_text());assert d['schema']=='sub_prototyp_verified_sources_v1'
 assert len(d['models'])==9
 ids=set();r=[]
 for item in d['models']:
  assert item['id'] not in ids;ids.add(item['id'])
  assert item['official_product_url'].startswith('https://')
  s=item['spec']
  if not all(s.get(k) is not None for k in
      ('fs_hz','vas_l','sd_cm2','qms','qes','qts','re_ohm')):
    r.append({'id':item['id'],'model':item['model'],'status':'BLOCKED_missing_manufacturer_TS'})
    continue
  qts_calculated=1/(1/s['qes']+1/s['qms'])
  cms=s['vas_l']*.001/(RHO*C*C*(s['sd_cm2']*.0001)**2)
  mms_calculated=1/((2*math.pi*s['fs_hz'])**2*cms)
  mass=s.get('mms_g')
  # Eton Mmd is NOT Mms and cannot be treated as such.
  if mass is not None:
   mass_ratio=mass/1000/mms_calculated-1
  else:mass_ratio=None
  if s.get('bl_tm') is not None:
   bl_expected=math.sqrt(2*math.pi*s['fs_hz']*
                        (mass/1000 if mass else mms_calculated)*
                        s['re_ohm']/s['qes'])
   bl_ratio=s['bl_tm']/bl_expected-1
  else:bl_ratio=None
  x=s.get('xmax_one_way_mm')
  vd=round(x*s['sd_cm2']*.1,3) if x is not None else None
  r.append({'id':item['id'],'model':item['model'],'status':'CHECKED',
    'qts_from_qes_qms':qts_calculated,
    'qts_rel_diff':qts_calculated/s['qts']-1,
    'mms_derived_g':mms_calculated*1000,'mms_rel_diff':mass_ratio,
    'bl_rel_diff':bl_ratio,
    'vd_from_sd_xmax_cm3':vd,
    'claimed_vd_cm3':s.get('vd_cm3'),
    'manufacturer_documentation_status':item['documentation_status']})
  assert abs(qts_calculated/s['qts']-1)<.12, item['model']
 print(json.dumps({'count':len(r),'results':r},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
