#!/usr/bin/env python3
"""Measured shell/frame candidate, fixed external datums. No fabrication release."""
import argparse,copy,hashlib,itertools,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
KEYS=('FR1','FR2','BACK','SIDE_L','SIDE_R','BOTTOM','TOP','PORTAL','MID_PORTAL')
def model(t,g=.2,lam=.1):
 W,D,H=1080.,432.,500.;F=t['FR1']+lam+t['FR2'];rear=D-t['BACK'];low=t['BOTTOM'];high=H-t['TOP']
 y=F+g;depth=rear-F-2*g;z=low+g;height=high-low-2*g
 if min(depth,height,W-t['SIDE_L']-t['SIDE_R']-2*g)<=0:raise ValueError('Non-positive cavity')
 old=json.loads((R/'wyniki/k30_czesci.json').read_text());parts=[]
 def add(id,o,s):parts.append(dict(id=id,o=o,s=s))
 add('FR1',[0,0,0],[W,t['FR1'],H]);add('FR2',[0,t['FR1']+lam,0],[W,t['FR2'],H]);add('BACK',[0,rear,0],[W,t['BACK'],H])
 add('SIDE_L',[0,y,0],[t['SIDE_L'],depth,H]);add('SIDE_R',[W-t['SIDE_R'],y,0],[t['SIDE_R'],depth,H])
 for id,zz in [('BOTTOM',0),('TOP',high)]:add(id,[t['SIDE_L']+g,y,zz],[W-t['SIDE_L']-t['SIDE_R']-2*g,depth,t[id]])
 for id,x in [('PORTAL',448),('MID_PORTAL',750)]:
  add(id,[x,y,z],[t[id],depth,height]);p=parts[-1]
  source=next(v for v in old if v['id']==id)
  p['windows_global_yz']=[[44+u,22+v,44+U,22+V,r] for u,v,U,V,r in source['windows']]
  p['windows_local_yz']=[[u-y,v-z,U-y,V-z,r] for u,v,U,V,r in p['windows_global_yz']]
  axes=[]
  if id=='PORTAL':
   for yy in (55,347):
    for zz in (88,204,320,426):
     axes.append([yy,zz,3])
     axes.extend([[yy,zz-32,2],[yy,zz+32,2]])
  p['holes_global_yz']=axes;p['holes_local_yz']=[[yy-y,zz-z,r] for yy,zz,r in axes]
 # These interfaces are still those of K30/K32: diagnose, do not silently move boxes/rails.
 issues=[]
 if 448+t['PORTAL']+4>474+1e-9:issues.append('portal_plate_overlaps_channel_web_X')
 if 750+t['MID_PORTAL']>772+1e-9:issues.append('mid_portal_overlaps_B_rails_X')
 if low>22+1e-9:issues.append('bottom_overlaps_first_rail_or_web_Z')
 if high<478-1e-9:issues.append('top_overlaps_keeper_or_web_Z')
 if W-t['SIDE_R']<1058-1e-9:issues.append('right_wall_overlaps_backstop_X')
 if 448+t['PORTAL']<470-1e-9:issues.append('portal_to_A_rails_gap_X')
 if 750+t['MID_PORTAL']<772-1e-9:issues.append('mid_portal_to_B_rails_gap_X')
 return dict(status='GEOMETRY_ONLY_HOLD',parts=parts,cavity_bounds={'Y':[F,rear],'Z':[low,high]},g_each_mm=g,front_lamination_gap_mm=lam,bank_interface_issues=issues)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--measurements',type=Path,default=R/'dane/k35_pomiary_korpusu.json');ap.add_argument('--require-measured',action='store_true');a=ap.parse_args()
 data=json.loads(a.measurements.read_text());t=data.get('thickness_mm',{})
 good=data.get('status')=='measured' and bool(data.get('measurement_record')) and all(type(t.get(k)) in (int,float) and math.isfinite(t[k]) and 21.5<=t[k]<=22.5 for k in KEYS)
 if a.require_measured and not good:raise SystemExit('BLOCKED: actual nine sheet thicknesses and record missing; no files written.')
 sample=model(t if good else dict.fromkeys(KEYS,22.))
 sample['input_status']='MEASURED_GEOMETRY_HOLD' if good else 'SYNTHETIC_PREVIEW_NOT_CNC'
 cases=[]
 for vals in itertools.product((21.5,22.5),repeat=len(KEYS)):
  tt=dict(zip(KEYS,vals));m=model(tt);portal=next(p for p in m['parts'] if p['id']=='PORTAL')
  # Global aperture corner positions and bore axes are invariant after coordinate conversion.
  for loc,glob in zip(portal['holes_local_yz'],portal['holes_global_yz']):
   assert abs(loc[0]+portal['o'][1]-glob[0])<1e-9 and abs(loc[1]+portal['o'][2]-glob[1])<1e-9
  cases.append(dict(thickness_mm=tt,portal_yz=portal['s'][1:],issues=m['bank_interface_issues']))
 sample['corner_count']=len(cases);sample['bank_ready_corner_count']=sum(not c['issues'] for c in cases);sample['corners']=cases
 # Partial schema is intentionally NOT a DXF/CAM export: bank interfaces remain unresolved.
 (R/'wyniki/k35_korpus_z_pomiarow.json').write_text(json.dumps(sample,indent=2)+'\n')
 files=['brief_system_audio_DIY_v0.6.md','wyniki/k30_czesci.json','dane/k35_pomiary_korpusu.json','skrypty/k35_korpus_z_pomiarow.py']
 (R/'wyniki/k35_manifest.json').write_text(json.dumps({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
 print(json.dumps({k:sample[k] for k in ('input_status','corner_count','bank_ready_corner_count','bank_interface_issues')},indent=2))
if __name__=='__main__':main()
