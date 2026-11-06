#!/usr/bin/env python3
"""K32 nominal captive-plate candidate. mm, N, MPa. No production release."""
import copy, hashlib, json, math
from pathlib import Path
import ezdxf
from k31_zlacze_i_pasowania import block, hit, swept, profile
R=Path(__file__).resolve().parents[1]
O=R/'dokumentacja/cnc/K32_RETENCJA_HOLD'

def main():
 O.mkdir(parents=True,exist_ok=True)
 ps=json.loads((R/'wyniki/k30_czesci.json').read_text())
 audit=json.loads((R/'wyniki/k30_stale_kanaly_audyt.json').read_text())
 portal=copy.deepcopy(next(p for p in ps if p['id']=='PORTAL'))
 portal['holes']=[(u+6 if u>200 else u,v,r) for u,v,r in portal['holes']]
 plates=[];hardware=[];centres=[]
 for row,(z,h) in enumerate(zip([40,156,272,388],[96,96,96,76])):
  for y in (55,347):
   mid=z+h/2;centres.append([y,mid])
   plates.append(block(f'P{row}_{y}',[470,y-9,mid-40],[4,18,80]))
   for dz in (-32,32):
    portal['holes'].append((y-44,mid+dz-22,2))
    hardware += [block(f'H{row}_{y}_{dz}',[445,y-3,mid+dz-3],[3,6,6]),block(f'S{row}_{y}_{dz}',[448,y-1.5,mid+dz-1.5],[30,3,3])]
 # All face holes are through. Metal THREAD_* circles are major diameters,
 # NEVER tapping drill instructions; taps/material and thread tolerances unresolved.
 d=ezdxf.new('R2010');d.units=4;m=d.modelspace()
 for layer in ('CUT_OUTER','CUT_INNER','DRILL_THRU','INFO_NO_CUT'):d.layers.new(layer)
 profile(m,'CUT_OUTER',0,0,*portal['flat'])
 for u,v,U,V,r in portal['windows']:profile(m,'CUT_INNER',u,v,U-u,V-v,r)
 for u,v,r in portal['holes']:m.add_circle((u,v),r,dxfattribs={'layer':'DRILL_THRU'})
 m.add_text('K32 MDF22 PORTAL HOLD',dxfattribs={'insert':(0,465),'height':3,'layer':'INFO_NO_CUT'})
 d.saveas(O/'PORTAL_K32_HOLD.dxf')
 d=ezdxf.new('R2010');d.units=4;m=d.modelspace()
 for layer in ('CUT_OUTER','THREAD_M5','THREAD_M3','INFO_NO_CUT'):d.layers.new(layer)
 profile(m,'CUT_OUTER',0,0,18,80)
 for u,v,r,l in [(9,40,2.5,'THREAD_M5'),(9,8,1.5,'THREAD_M3'),(9,72,1.5,'THREAD_M3')]:m.add_circle((u,v),r,dxfattribs={'layer':l})
 m.add_text('8x METAL t4 HOLD; THREAD SYMBOLS NOT DRILLS',dxfattribs={'insert':(0,86),'height':2,'layer':'INFO_NO_CUT'})
 d.saveas(O/'PLYTKA_18x80x4_GWINTY_HOLD.dxf')
 # Decompose window frames to conservative rectangles; added parts all lie
 # beside window straight edges, far from rounded corners.
 solids=[]
 for p in ps:
  if p['kind']!='fixed':continue
  if not p['windows']:solids.append(block(p['id'],p['o'],p['s']));continue
  u0,u1=p['windows'][0][0],p['windows'][0][2];uv=p['uv']
  def add(label,u,v,w,h):
   oo=list(p['o']);ss=list(p['s']);oo[uv[0]]+=u;oo[uv[1]]+=v;ss[uv[0]]=w;ss[uv[1]]=h;solids.append(block(label,oo,ss))
  add(p['id']+'_front',0,0,u0,p['flat'][1]);add(p['id']+'_rear',u1,0,p['flat'][0]-u1,p['flat'][1]);v=0
  for _,v0,_,v1,_ in p['windows']:add(p['id']+'_rib',u0,v,u1-u0,v0-v);v=v1
  add(p['id']+'_top',u0,v,u1-u0,p['flat'][1]-v)
 solids.append(block('MAT',[22,360,22],[1036,50,456]))
 # Shafts intentionally cross the portal and their own threaded plate.
 fixed_hits=[]
 for b in plates+hardware:
  for ob in solids:
   if b['id'].startswith('S') and ob['id'].startswith('PORTAL'):continue
   if hit(b,ob):fixed_hits.append([b['id'],ob['id']])
 movements=[]
 for row in audit['box_paths']:
  L,H=(253,76) if row['id'].startswith('M3') else (267.1,96)
  b=block(row['id'],[0,0,0],[L,260,H]);hits=[]
  for a,c in zip(row['waypoints_origin_mm'],row['waypoints_origin_mm'][1:]):
   for ob in plates+hardware:
    if hit(swept(b,a,c),ob):hits.append(ob['id'])
  movements.append(dict(kind='box',id=row['id'],collisions=hits))
 for row in audit['keeper_paths']:
  pieces=copy.deepcopy(row['pieces']);pieces[0]['s'][1]=312;hits=[]
  for a,c in zip(row['shifts'],row['shifts'][1:]):
   for b in pieces:
    for ob in plates+hardware:
     if hit(swept(b,a,c),ob):hits.append(ob['id'])
  movements.append(dict(kind='keeper',row=row['row'],extended=row['extended'],collisions=hits))
 for row in audit['tool_paths']:
  path=copy.deepcopy(row['waypoints'])
  if row['y']==341:
   for a in path[1:]:a[1]+=6
  hits=[]
  for a,c in zip(path,path[1:]):
   for ob in plates+hardware:
    if hit(swept(block('tool',[0,0,0],[60,20,20]),a,c),ob):hits.append(ob['id'])
  movements.append(dict(kind='tool',row=row['row'],y=row['y'],collisions=hits))
 # Screening model, not dynamic certification: two sealed large inserts + separator.
 # Nominal solid volume excludes bond gap; density/hardware allowance/5g invented scenarios.
 V=(267.1*260*96-(267.1-16)*(260-16)*(96-16))*1e-9
 mass=2*(V*800+.2)+8*260*96*1e-9*800
 F=mass*5*9.80665
 a=200-55;b=347-200;L=a+b;I=50*18**3/12
 reactions=[F*b/L,F*a/L];moment=F*a*b/L
 beam=dict(mass_kg=mass,force_N=F,reactions_N=reactions,max_moment_Nmm=moment,
  bending_MPa=moment*9/I,point_deflection_mm_at_E2000=F*a*a*b*b/(3*2000*I*L),
  nose_mean_pressure_MPa=F/(80*50),note='Simply supported linear beam; E=2000 MPa assumed, no allowable.')
 # Main screw torque must be reacted even before an axial joint is fully clamped.
 torque=[dict(assumed_torque_Nm=T,pair_force_N=T*1000/64,mean_MDF_bearing_MPa=T*1000/64/(3*22)) for T in (.5,1,2)]
 result=dict(status='CNC_HOLD',units='mm N MPa',centres=centres,plates=plates,hardware=hardware,
  fixed_collisions=fixed_hits,movements=movements,beam=beam,anti_rotation=torque,
  added_plate_gross_volume_l=8*18*50*4/1e6,
  assumptions={'density_kg_m3':800,'extra_mass_per_box_kg':.2,'acceleration_g':5,'E_MPa':2000,
   'M3_head_diameter_mm':6,'M3_head_height_mm':3,'M3_length_under_head_mm':30},
  blockers=['Thread material and tolerance, screw locking against vibration','Nose and long tube positive connection','MDF creep, preload and frame-to-shell load transfer','Actual stock, driver and terminal'])
 (R/'wyniki/k32_retencja.json').write_text(json.dumps(result,indent=2)+'\n')
 sc=['// K32 nominal DETAIL only. CNC HOLD. axes X,Y,Z in mm.','$fn=48;']
 for p in plates:
  sc.append('color("silver") difference(){translate('+str(p['o'])+') cube('+str(p['s'])+');')
  y=p['o'][1]+9;z=p['o'][2]+40
  for dz,r in [(0,2.5),(-32,1.5),(32,1.5)]:sc.append(f'translate([469,{y},{z+dz}]) rotate([0,90,0]) cylinder(h=6,r={r});')
  sc.append('}')
 for p in hardware:sc.append('color("orange") translate('+str(p['o'])+') cube('+str(p['s'])+'); // conservative screw envelope')
 (O/'K32_DETAL_HOLD.scad').write_text('\n'.join(sc)+'\n')
 inputs=['brief_system_audio_DIY_v0.6.md','wyniki/k30_czesci.json','wyniki/k30_stale_kanaly_audyt.json','skrypty/k32_retencja_plytek.py']
 (R/'wyniki/k32_manifest.json').write_text(json.dumps({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in inputs},indent=2)+'\n')
 print(json.dumps({'fixed_hits':fixed_hits,'motion_failures':[x for x in movements if x['collisions']],'beam':beam},indent=2))
if __name__=='__main__':main()
