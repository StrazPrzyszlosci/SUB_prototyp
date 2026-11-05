#!/usr/bin/env python3
"""Additive K31 geometry and measured-stock fit model. Does not modify K30.
All dimensions mm. Synthetic fit cases are NOT measured production inputs.
"""
import argparse,copy,csv,hashlib,itertools,json,math,sys
from pathlib import Path
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
OUT=R/'dokumentacja/cnc/K31_ZLACZE_I_PASOWANIA_HOLD'
FACES=('XL','XR','YF','YR','ZB','ZT')
def block(id,o,s):return {'id':id,'o':list(o),'s':list(s)}
def hit(a,b):return all(min(a['o'][j]+a['s'][j],b['o'][j]+b['s'][j])-max(a['o'][j],b['o'][j])>1e-7 for j in range(3))
def swept(p,a,b):return block(p['id'],[p['o'][j]+min(a[j],b[j]) for j in range(3)],[p['s'][j]+abs(a[j]-b[j]) for j in range(3)])
def profile(m,layer,u,v,w,h,r=0):
 if not r:pts=[(u,v,0),(u+w,v,0),(u+w,v+h,0),(u,v+h,0)]
 else:
  k=math.tan(math.pi/8);pts=[(u+r,v,0),(u+w-r,v,k),(u+w,v+r,0),(u+w,v+h-r,k),(u+w-r,v+h,0),(u+r,v+h,k),(u,v+h-r,0),(u,v+r,k)]
 m.add_lwpolyline(pts,format='xyb',close=True,dxfattribs={'layer':layer})
def dxf(p,path):
 d=ezdxf.new('R2010');d.units=4;d.header['$MEASUREMENT']=1
 for l in ['CUT_OUTER','CUT_INNER','DRILL_THRU','INFO_NO_CUT']:d.layers.new(l)
 m=d.modelspace();profile(m,'CUT_OUTER',0,0,*p['flat'])
 for u,v,r in p.get('holes',[]):m.add_circle((u,v),r,dxfattribs={'layer':'DRILL_THRU'})
 for u,v,U,V,r in p.get('windows',[]):profile(m,'CUT_INNER',u,v,U-u,V-v,r)
 m.add_text(p['id']+' K31 CNC HOLD',dxfattribs={'insert':(0,p['flat'][1]+7),'height':3,'layer':'INFO_NO_CUT'})
 d.saveas(path)

def fit_panels(L,B,H,t,g):
 """Measured-stock sizing; g is EACH nominal bond gap, not total clearance."""
 xl,xr,yf,yr,zb,zt=[t[k] for k in FACES]
 x=L-xl-xr-2*g;y=B-yf-yr-2*g
 if min(x,y,H-zb-zt)<=0:raise ValueError('Invalid panel/cavity dimensions')
 return [dict(id='XL',o=[0,0,0],s=[xl,B,H],axis=0),dict(id='XR',o=[L-xr,0,0],s=[xr,B,H],axis=0),
  dict(id='YF',o=[xl+g,0,0],s=[x,yf,H],axis=1),dict(id='YR',o=[xl+g,B-yr,0],s=[x,yr,H],axis=1),
  dict(id='ZB',o=[xl+g,yf+g,0],s=[x,y,zb],axis=2),dict(id='ZT',o=[xl+g,yf+g,H-zt],s=[x,y,zt],axis=2)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--measurements',type=Path);ap.add_argument('--require-measured',action='store_true');args=ap.parse_args()
 source=R/'wyniki/k30_czesci.json';old=json.loads(source.read_text());audit=json.loads((R/'wyniki/k30_stale_kanaly_audyt.json').read_text())
 data=json.loads((args.measurements or R/'dane/k31_pomiary_szablon.json').read_text())
 complete=data.get('status')=='measured' and bool(data.get('measurement_record')) and all(isinstance(data['thickness_mm'][k],(int,float)) and math.isfinite(data['thickness_mm'][k]) and 7.5<=data['thickness_mm'][k]<=8.5 for k in FACES)
 if args.require_measured and not complete:raise SystemExit('BLOCKED: actual thickness measurements and record are missing; no files generated.')
 t=data['thickness_mm'] if complete else dict.fromkeys(FACES,8.0)
 g=.2 # HYPOTHETICAL target per side; adhesive qualification remains open.
 OUT.mkdir(parents=True,exist_ok=True)
 ps=copy.deepcopy(old)
 for p in ps:
  if p['id']=='PORTAL':p['holes']=[(u+6 if u>200 else u,v,r) for u,v,r in p['holes']]
  if p['id'].startswith('STOP_'):
   p['s'][1]=312;p['flat'][0]=312;p['holes']=[(10,25,3),(302,25,3)]
 changed=[p for p in ps if p['id']=='PORTAL' or p['id'].startswith('STOP_')]
 for p in changed:dxf(p,OUT/(p['id']+'_K31_HOLD.dxf'))
 # Extract actual rectangular solids and exact flat web edges from the persisted CAD.
 solids=[]
 for p in ps:
  if p['kind']!='fixed':continue
  if not p['windows']:solids.append(block(p['id'],p['o'],p['s']));continue
  u0,u1=p['windows'][0][0],p['windows'][0][2];uv=p['uv'];O=p['o'];S=p['s']
  def add(id,u,v,w,h):
   o=list(O);s=list(S);o[uv[0]]+=u;o[uv[1]]+=v;s[uv[0]]=w;s[uv[1]]=h;solids.append(block(id,o,s))
  add(p['id']+'_webF',0,0,u0,p['flat'][1]);add(p['id']+'_webR',u1,0,p['flat'][0]-u1,p['flat'][1]);v=0
  for j,(_,v0,_,v1,_) in enumerate(p['windows']):add(p['id']+'_rib'+str(j),u0,v,u1-u0,v0-v);v=v1
  add(p['id']+'_ribTop',u0,v,u1-u0,p['flat'][1]-v)
 mat=block('MAT',[22,360,22],[1036,50,456]);solids.append(mat)
 boxes=[]
 for r,(z,h,L) in enumerate(zip([40,156,272,388],[96,96,96,76],[267.1]*3+[253.0])):
  for suffix,x in [('N',474),('F',474+L+8)]:boxes.append(block(f'M{r}{suffix}',[x,70,z],[L,260,h]))
 # Bolt protrusion OLD vs NEW: only material BEHIND plate, not intentional bore contact.
 bolt_tests=[];plates=[]
 for r,(z,h) in enumerate(zip([40,156,272,388],[96,96,96,76])):
  for y in (55,341,347):
   nose=block('bolt_protrusion',[474,y-2.5,z+h/2-2.5],[5,5,5])
   hits=[s['id'] for s in solids+boxes if hit(nose,s)]
   bolt_tests.append(dict(row=r,y=y,collisions=hits))
  for y in (55,347):plates.append(block(f'PLATE_{r}_{y}',[470,y-9,z+h/2-15],[4,18,30]))
 # Conservative sensitivity envelope: bore axis +/-0.1, shank radius +0.05,
 # permanent obstacles expanded by 0.7 in every axis; not a manufacturer stack.
 robust_bolts=[]
 for r,(z,h) in enumerate(zip([40,156,272,388],[96,96,96,76])):
  for y in (55,347):
   b=block('protrusion_stress',[472.8,y-2.65,z+h/2-2.65],[8.2,5.3,5.3]);hits=[]
   for ob in solids+boxes:
    expanded=block(ob['id'],[q-.7 for q in ob['o']],[q+1.4 for q in ob['s']])
    if hit(b,expanded):hits.append(ob['id'])
   robust_bolts.append(dict(row=r,y=y,collisions=hits))
 # Rigid tool translations and finite keepers, using the previous sequences but new widths.
 motion=[]
 for row in audit['tool_paths']:
  o=copy.deepcopy(row);dy=6 if o['y']==341 else 0
  for p in o['waypoints'][1:]:p[1]+=dy
  path=o['waypoints'];b=block('tool',[0,0,0],[60,20,20]);hits=[]
  for j,(a,c) in enumerate(zip(path,path[1:])):
   for ob in solids+boxes:
    if hit(swept(b,a,c),ob):hits.append([j,ob['id']])
  motion.append(dict(kind='tool',row=o['row'],y=o['y']+dy,collisions=hits))
 for row in audit['keeper_paths']:
  pieces=copy.deepcopy(row['pieces']);pieces[0]['s'][1]=312
  obs=solids+plates+[b for b in boxes if not(row['extended'] and b['id']=='M1N')];hits=[]
  for j,(a,c) in enumerate(zip(row['shifts'],row['shifts'][1:])):
   for p in pieces:
    for ob in obs:
     if hit(swept(p,a,c),ob):hits.append([j,p['id'],ob['id']])
  motion.append(dict(kind='keeper',row=row['row'],extended=row['extended'],collisions=hits))
 # Recheck all eight stored insert paths with the corrected permanent plates.
 for row in audit['box_paths']:
  b=next(b for b in boxes if b['id']==row['id']);hits=[]
  for j,(a,c) in enumerate(zip(row['waypoints_origin_mm'],row['waypoints_origin_mm'][1:])):
   bb=block(b['id'],[0,0,0],b['s'])
   for ob in plates:
    if hit(swept(bb,a,c),ob):hits.append([j,ob['id']])
  motion.append(dict(kind='insert_vs_new_plates',id=row['id'],collisions=hits))
 # Stack uncertainty (chosen bolt-length/washer/plate ranges are model assumptions).
 stacks=[]
 for length in (45,50):
  rows=[]
  for dl,stop,frame,washer,plate in itertools.product((-.25,.25),(17.5,18.5),(21.5,22.5),(.9,1.1),(3.8,4.2)):
   travel=length+dl-stop-frame-washer
   rows.append(dict(thread_travel=travel,plate=plate,full=travel>=plate,projection=travel-plate))
  stacks.append(dict(length=length,full_thread_cases=sum(x['full'] for x in rows),total=len(rows),
   travel_range=[min(x['thread_travel'] for x in rows),max(x['thread_travel'] for x in rows)],
   projection_range=[min(x['projection'] for x in rows),max(x['projection'] for x in rows)]))
 # Bearing overlap with the actual front/rear web bands: plate rectangle minus Ø6 bore.
 bearing=[]
 for y,lo,hi,label in [(55,44,64,'front'),(341,336,410,'old_rear'),(347,336,410,'new_rear')]:
  width=max(0,min(y+9,hi)-max(y-9,lo));area=width*30-math.pi*3**2
  bearing.append(dict(location=label,contact_width=width,area_mm2=area,ligament_mm=min(y-lo,hi-y)-3,
   pressure_MPa=[{'assumed_total_axial_force_N':F,'mean_pressure':F/area} for F in (100,300,500)]))
 # All 64 stock corners; nominal outer envelope unchanged, bond surfaces disjoint.
 fitcases=[]
 for vals in itertools.product((7.5,8.5),repeat=6):
  tt=dict(zip(FACES,vals))
  for L,H in ((267.1,96),(253,76)):
   fp=fit_panels(L,260,H,tt,g)
   assert not any(hit(a,b) for a,b in itertools.combinations(fp,2))
   assert all(min(p['s'])>0 for p in fp)
   assert abs(fp[2]['o'][0]-tt['XL']-g)<1e-9
   fitcases.append(dict(thickness=tt,L=L,H=H,panel_x=fp[4]['s'][0],panel_y=fp[4]['s'][1]))
 # Residual errors AFTER measurement: independent outer/panel XY ±0.1,
 # each actual sheet local thickness vs entered measurement ±0.05.
 totalclear=[]
 for outer,panel,tl,tr in itertools.product((-.1,.1),(-.1,.1),(-.05,.05),(-.05,.05)):
  totalclear.append(2*g+outer-panel-tl-tr)
 # Independent stock corners without measurement are still capable of interference.
 unmeasured_min=2*g-.1-.1-.5-.5
 assert min(totalclear)>0 and unmeasured_min<0
 # Preview all 48 replacement box panels; explicit no real measurements status.
 cut=[]
 for b in boxes:
  L,B,H=b['s']
  for p in fit_panels(L,B,H,t,g):
   p['id']=b['id']+'_'+p['id'];p['flat']=[p['s'][j] for j in range(3) if j!=p['axis']]
   p['o']=[p['o'][j]+b['o'][j] for j in range(3)];p['status']='MEASURED_GEOMETRY_HOLD' if complete else 'SYNTHETIC_PREVIEW_NOT_CNC'
   cut.append(p)
 # Corrected assembly preview: preserved unmodified K30 body, five new parts,
 # stock-aware panels and nominal bolt/plate envelopes; all CNC HOLD.
 sc=['// K31 corrected assembly, synthetic stock unless measurement flag in JSON.',
     '// CNC HOLD: glue, plate retention and real driver/terminal interfaces unqualified.',
     '$fn=64; state=100;']
 middle={'M0N','M0F','M1F','M3N','M3F'}
 preview=[p for p in ps if p['kind']!='insert_panel']
 for p in cut:
  q=copy.deepcopy(p);q['kind']='insert_panel';q['uv']=[j for j in range(3) if j!=p['axis']];q['thickness']=p['s'][p['axis']];q['holes']=[];q['windows']=[];preview.append(q)
 for p in preview:
  pre=''
  if p['kind']=='insert_panel':pre='if(state==100'+(' || state==120' if p['id'][:3] in middle else '')+') '
  elif p['kind']=='separator':pre='if(state==100'+(' || state==120' if p['id'] in ('SEP_0','SEP_3') else '')+') '
  elif p['id']=='NOSE_1':pre='if(state!=120) '
  col='[0.7,0.45,0.2,0.6]' if p['kind']=='insert_panel' else ('[0.8,0.2,0.2]' if p['id'].startswith('STOP') else '[0.65,0.65,0.7,0.35]')
  sc.append(pre+'color('+col+') difference(){translate('+str(p['o'])+') cube('+str(p['s'])+');')
  for u,v,rad in p['holes']:
   pos=list(p['o']);pos[p['uv'][0]]+=u;pos[p['uv'][1]]+=v;pos[p['axis']]-=1
   rot=[[0,90,0],[90,0,0],[0,0,0]][p['axis']]
   if p['axis']==1:pos[1]+=p['thickness']+2
   sc.append(f'translate({pos}) rotate({rot}) cylinder(h={p["thickness"]+2},r={rad});')
  for u,v,U,V,rad in p['windows']:
   sc.append('hull(){')
   for yy,zz in itertools.product((u+rad,U-rad),(v+rad,V-rad)):
    sc.append(f'translate([{p["o"][0]-1},{p["o"][1]+yy},{p["o"][2]+zz}]) rotate([0,90,0]) cylinder(h=24,r={rad});')
   sc.append('}')
  sc.append('}')
 for plate in plates:sc.append('color([0.4,0.4,0.5]) translate('+str(plate['o'])+') cube('+str(plate['s'])+');')
 for z,h in zip((40,156,272,388),(96,96,96,76)):
  for y in (55,347):
   sc.append(f'color([0.4,0.4,0.5]) translate([429,{y},{z+h/2}]) rotate([0,90,0]) cylinder(h=50,r=2.5);')
   sc.append(f'color([0.4,0.4,0.5]) translate([424,{y},{z+h/2}]) rotate([0,90,0]) cylinder(h=5,r=5);')
 # Use the existing finite sealed extended-keeper design; no attachment qualification.
 sc.append('if(state==120) color([0.8,0.2,0.2]) {translate([448,160,179]) cube([4,80,50]); difference(){translate([452,190,194]) cube([295.1,20,20]);translate([454,192,196]) cube([291.1,16,16]);}}')
 (OUT/'K31_ZLOZENIE_HOLD.scad').write_text('\n'.join(sc)+'\n')
 # No 48 misleading replacement DXFs for absent thickness measurements: CSV shows
 # calculated proposal, release gate refuses --require-measured before any write.
 with (OUT/'PANELE_WKLADOW_PODGLAD.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['ID','U_mm','V_mm','actual_thickness_mm','status'])
  for p in cut:w.writerow([p['id'],*p['flat'],p['s'][p['axis']],p['status']])
 (R/'wyniki/k31_panele_wkladow.json').write_text(json.dumps(cut,indent=2)+'\n')
 result=dict(study='K31',status='CNC_HOLD',changed_parts=[p['id'] for p in changed],bolt_protrusion=bolt_tests,
  motions=motion,robust_bolts=robust_bolts,thread_stack=stacks,bearing=bearing,stock_corner_cases=len(fitcases),stock_corners=fitcases,
  fit=dict(measurements_real=complete,gap_per_side_mm=g,total_clearance_after_measurement_range=[min(totalclear),max(totalclear)],
   worst_total_clearance_without_measurement=unmeasured_min,measurement_local_uncertainty_assumed_mm=.05,
   note='Total positive clearance does not guarantee equal gaps: centred assembly/jig required; glue-gap qualification OPEN.'),
  volume_delta_stop_bars_l=4*18*6*50/1e6,
  limits=['No plate retention mechanism qualified; bearing calculation is not material allowable.',
  'M5x50 is dimensional candidate; bolt/head/washer/plate tolerances require source confirmation.',
  'New rear axis and larger stop do not fix unqualified nose bond, extended keeper attachment or rattle.',
  'Stock correction covers insert panels only, not shell/frame fit or final driver/terminal mounting.',
  'Existing K30 assembly and DXFs remain historical; apply five changed parts only as reviewed K31 proposal.'])
 assert all(not m['collisions'] for m in motion)
 assert all(not m['collisions'] for m in robust_bolts)
 assert all(not x['collisions'] for x in bolt_tests if x['y'] in (55,347))
 assert all(x['collisions'] for x in bolt_tests if x['y']==341)
 for p in changed:
  doc=ezdxf.readfile(OUT/(p['id']+'_K31_HOLD.dxf'));assert doc.units==4 and not doc.audit().errors
  assert all(e.closed for e in doc.modelspace().query('LWPOLYLINE'))
 (R/'wyniki/k31_zlacze_pasowania.json').write_text(json.dumps(result,indent=2)+'\n')
 fig,axs=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
 axs[0].bar(['Stara oś Y341','Nowa oś Y347'],[bearing[1]['area_mm2'],bearing[2]['area_mm2']],color=['#ba694d','#418776'])
 axs[0].set(ylabel='Pole podparcia płytki [mm²]',title='Tylna płytka 18×30 mm, otwór Ø6')
 axs[1].errorbar([0,1],[0,2*g],yerr=[1.2,.3],fmt='o',capsize=8,color='#176faa');axs[1].axhline(0,color='black',linewidth=.8)
 axs[1].set(xticks=[0,1],xticklabels=['K30: nominalne 8 mm','K31: po pomiarze*'],ylabel='Łączny luz panelu [mm]',title='*Założono błąd grubości ±0,05 mm')
 fig.suptitle('K31 — geometria złącza i pasowania; CNC HOLD, brak walidacji materiałowej')
 for ext in ('png','svg'):fig.savefig(R/f'wyniki/k31_zlacze_pasowania.{ext}',dpi=150)
 plt.close(fig)
 files=[source,R/'wyniki/k30_stale_kanaly_audyt.json',R/'skrypty/k31_zlacze_i_pasowania.py',args.measurements or R/'dane/k31_pomiary_szablon.json']
 (R/'wyniki/k31_manifest.json').write_text(json.dumps({'inputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'python':sys.version,'ezdxf':ezdxf.__version__},indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['stock_corners','motions','bolt_protrusion']},indent=2))
if __name__=='__main__':main()
