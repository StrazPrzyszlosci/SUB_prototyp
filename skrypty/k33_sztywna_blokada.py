#!/usr/bin/env python3
"""K33: machined-metal keeper candidate; nominal geometry, not production approval."""
import json,math,hashlib
from pathlib import Path
import ezdxf
from k31_zlacze_i_pasowania import block,hit,swept,profile
R=Path(__file__).resolve().parents[1];O=R/'dokumentacja/cnc/K33_BLOKADA_METAL_HOLD'
def fixed_solids(ps):
 out=[]
 for p in ps:
  if p['kind']!='fixed':continue
  if not p['windows']:out.append(block(p['id'],p['o'],p['s']));continue
  uv=p['uv'];u0,u1=p['windows'][0][0],p['windows'][0][2]
  def add(u,v,w,h):
   o=p['o'][:];s=p['s'][:];o[uv[0]]+=u;o[uv[1]]+=v;s[uv[0]]=w;s[uv[1]]=h;out.append(block(p['id'],o,s))
  add(0,0,u0,p['flat'][1]);add(u1,0,p['flat'][0]-u1,p['flat'][1]);v=0
  for _,v0,_,v1,_ in p['windows']:add(u0,v,u1-u0,v0-v);v=v1
  add(u0,v,u1-u0,p['flat'][1]-v)
 out.append(block('MAT',[22,360,22],[1036,50,456]));return out

def main():
 O.mkdir(parents=True,exist_ok=True)
 old=json.loads((R/'wyniki/k30_czesci.json').read_text());paths=json.loads((R/'wyniki/k30_stale_kanaly_audyt.json').read_text());k32=json.loads((R/'wyniki/k32_retencja.json').read_text())
 obs=fixed_solids(old)+k32['plates']+k32['hardware'];boxes=[]
 for row,(z,h,l) in enumerate(zip([40,156,272,388],[96,96,96,76],[267.1]*3+[253])):
  for suffix,x in [('N',474),('F',474+l+8)]:boxes.append(block(f'M{row}{suffix}',[x,70,z],[l,260,h]))
 assemblies=[];checks=[]
 for path in paths['keeper_paths']:
  row=path['row'];ext=path['extended'];z=[88,204,320,426][row]
  parts=[block('bar',[430,45,z-25],[18,312,50])]
  if not ext:
   parts += [block('integral_nose',[448,160,z-25],[22,80,50]),block('root_F_envelope',[448,156,z-25],[4,4,50]),block('root_R_envelope',[448,240,z-25],[4,4,50])]
  else:
   parts += [block('flange',[448,160,z-25],[4,80,50]),block('tube_envelope',[452,190,z-10],[295.1,20,20]),block('weld_envelope',[452,188,z-12],[2,24,24])]
   for y in (180,220):
    for dz in (-15,15):parts.append(block('M4_head',[452,y-4,z+dz-4],[4,8,8]))
  hits=[]
  obstacles=obs+[b for b in boxes if not(ext and b['id']=='M1N')]
  for seg,(a,b) in enumerate(zip(path['shifts'],path['shifts'][1:])):
   for p in parts:
    for ob in obstacles:
     if hit(swept(p,a,b),ob):hits.append([seg,p['id'],ob['id']])
  # At front crossing, orientation fixed: evaluate extreme X/Z corners of all pieces.
  shift=path['shifts'][0];rad=355.8/2
  margin=min(rad-math.hypot(p['o'][0]+shift[0]+dx-231,p['o'][2]+shift[2]+dz-250) for p in parts for dx in (0,p['s'][0]) for dz in (0,p['s'][2]))
  assemblies.append(dict(row=row,extended=ext,parts=parts))
  checks.append(dict(row=row,extended=ext,collisions=hits,aperture_margin_mm=margin))
 # Metal contours, NOT MDF jobs. Short one-piece part extruded Z50, XY contour R4 roots.
 def doc():
  d=ezdxf.new('R2010');d.units=4
  for l in ('CUT_OUTER','DRILL_THRU','THREAD_M4_BLIND10','INFO_NO_CUT'):d.layers.new(l)
  return d,d.modelspace()
 d,m=doc();k=-math.tan(math.pi/8)
 m.add_lwpolyline([(0,0,0),(18,0,0),(18,111,k),(22,115,0),(40,115,0),(40,195,0),(22,195,k),(18,199,0),(18,312,0),(0,312,0)],format='xyb',close=True,dxfattribs={'layer':'CUT_OUTER'})
 m.add_text('SHORT XY tZ50; R4 ROOTS; FACE BORES SEE FACE DXF; HOLD',dxfattribs={'insert':(0,320),'height':3,'layer':'INFO_NO_CUT'});d.saveas(O/'KROTKA_OBRYS_XY_Z50_HOLD.dxf')
 for name,ext in [('KROTKA',False),('DLUGA',True)]:
  d,m=doc();profile(m,'CUT_OUTER',0,0,312,50)
  for y in (10,302):m.add_circle((y,25),3,dxfattribs={'layer':'DRILL_THRU'})
  if ext:
   for y in (135,175):
    for z in (10,40):m.add_circle((y,z),2,dxfattribs={'layer':'THREAD_M4_BLIND10'})
  m.add_text('YZ FACE; X430..448; M5 bores thru18; M4 from X448 if present; HOLD',dxfattribs={'insert':(0,57),'height':3,'layer':'INFO_NO_CUT'});d.saveas(O/(name+'_CZOL0_YZ_HOLD.dxf'))
 d,m=doc();profile(m,'CUT_OUTER',0,0,80,50)
 for y in (20,60):
  for z in (10,40):m.add_circle((y,z),2.5,dxfattribs={'layer':'DRILL_THRU'})
 m.add_text('FLANGE t4; tube20x20 at40,25; weld throat2 assumption; HOLD',dxfattribs={'insert':(0,57),'height':2,'layer':'INFO_NO_CUT'});d.saveas(O/'KOLNIERZ_80x50x4_HOLD.dxf')
 # Model deflection with own bar inertia, plus nose inertia. Unit-load integration.
 F=k32['beam']['force_N'];L=292;a=145;I=50*18**3/12;acc=5*9.80665;results=[]
 for label,E,rho in [('MDF_reference',2000,800),('metal_candidate',70000,2700)]:
  bar_mass=18*312*50*1e-9*rho;nose_mass=(22*80*50+2*(16-math.pi*4)*50)*1e-9*rho
  P=F+nose_mass*acc;q=bar_mass*acc/L;ra=P*(L-a)/L+q*L/2;rb=P*a/L+q*L/2
  dx=L/100000;de=0;Mmax=0
  for j in range(100000):
   x=(j+.5)*dx;M=ra*x-q*x*x/2-P*max(0,x-a);u=(L-a)/L*x-max(0,x-a);de+=M*u*dx/(E*I);Mmax=max(Mmax,M)
  results.append(dict(label=label,E_MPa=E,density_kg_m3=rho,bar_mass_kg=bar_mass,nose_mass_kg=nose_mass,point_force_N=P,uniform_N_mm=q,reactions_N=[ra,rb],deflection_mm=de,max_bending_MPa=Mmax*9/I))
 # Extended stop axial compression load path. Same F is a conservative transferred-load scenario.
 tubeA=20**2-16**2;tubeI=(20**4-16**4)/12;ll=295.1;E=70000
 ext=dict(axial_force_N=F,area_mm2=tubeA,compression_MPa=F/tubeA,shortening_mm=F*ll/(E*tubeA),
  euler_pinned_N=math.pi**2*E*tubeI/ll**2,assumed_weld_throat_mm=2,weld_nominal_stress_MPa=F/(80*2),
  reverse_force_per_M4_N=F/4,thread_nominal_engagement_mm=8,thread_blind_depth_mm=10,
  note='No strength allowables; Euler ideal not assembly rating; local buckling, weld HAZ and eccentricity open.')
 out=dict(status='CNC_HOLD',assemblies=assemblies,checks=checks,beam=results,extended=ext,assumptions='E70000 and rho2700 are model inputs, not certified selected alloy properties.')
 (R/'wyniki/k33_sztywna_blokada.json').write_text(json.dumps(out,indent=2)+'\n')
 # Keep conservative envelopes obvious: this is a service-volume model, not manufacture solid.
 sc=['// K33 SERVICE ENVELOPES ONLY, CNC HOLD. ext=true selects long row1.','ext=false;']
 for ass in assemblies:
  cond='ext' if ass['extended'] else ('!ext' if ass['row']==1 else 'true')
  for p in ass['parts']:sc.append('if('+cond+') translate('+str(p['o'])+') cube('+str(p['s'])+'); // '+p['id'])
 (O/'K33_OBWIEDNIE_SERWISOWE.scad').write_text('\n'.join(sc)+'\n')
 files=['brief_system_audio_DIY_v0.6.md','wyniki/k30_czesci.json','wyniki/k30_stale_kanaly_audyt.json','wyniki/k32_retencja.json','skrypty/k33_sztywna_blokada.py']
 (R/'wyniki/k33_manifest.json').write_text(json.dumps({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
 print(json.dumps({'checks':checks,'beam':results,'extended':ext},indent=2))
if __name__=='__main__':main()
