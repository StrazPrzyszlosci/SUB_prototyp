#!/usr/bin/env python3
"""K36 propagated bank geometry; corner-envelope motion validation, CNC HOLD."""
import copy,hashlib,itertools,json,math
import ezdxf
from pathlib import Path
from k35_korpus_z_pomiarow import model,KEYS
from k33_sztywna_blokada import fixed_solids
from k31_zlacze_i_pasowania import block,hit,swept
R=Path(__file__).resolve().parents[1]
OLD=json.loads((R/'wyniki/k30_czesci.json').read_text())
K32=json.loads((R/'wyniki/k32_retencja.json').read_text())
K33=json.loads((R/'wyniki/k33_sztywna_blokada.json').read_text())
def build(t,g=.2):
 shell=model(t,g);ps=copy.deepcopy(OLD);sp={p['id']:p for p in shell['parts']}
 # K30 front ids are FR1/FR2. All planes remain in global cabinet datums.
 for p in ps:
  if p['id'] in sp:
   n=sp[p['id']];p['o']=n['o'];p['s']=n['s'];p['flat']=[p['s'][j] for j in p['uv']]
   if 'windows_local_yz' in n:p['windows']=n['windows_local_yz'];p['holes']=n['holes_local_yz']
 endA=448+t['PORTAL'];startB=750+t['MID_PORTAL'];right=1080-t['SIDE_R'];lo=t['BOTTOM'];hi=500-t['TOP']
 changed=[]
 for p in ps:
  id=p['id']
  if id.startswith(('RAIL_','TOP_KEEPER_','CHANNEL_WEB_')):
   seg=id.split('_')[2] if id.startswith(('TOP_KEEPER_','CHANNEL_WEB_')) else id.split('_')[1]
   a=(max(474,endA+4+g) if id.startswith('CHANNEL_WEB') else endA+g) if seg=='A' else startB+g
   b=750-g if seg=='A' else right-g;p['o'][0]=a;p['s'][0]=b-a
   if id.startswith('CHANNEL_WEB'):
    p['o'][2]=lo+g;p['s'][2]=hi-lo-2*g
   elif id.startswith('TOP_KEEPER'):
    p['o'][2]=466;p['s'][2]=hi-g-466;p['note']='Face-machine from measured stock >= final thickness; nominal18 blank proposed.'
   elif '_0_' in id:
    p['o'][2]=lo+g;p['s'][2]=40-lo-g;p['note']='Face-machine from measured stock >= final thickness; nominal22 blank proposed.'
   p['flat']=[p['s'][j] for j in p['uv']];p['thickness']=p['s'][p['axis']];changed.append(id)
  if id.startswith('BACKSTOP_') and not id.startswith(('BACKSTOP_PACK','BACKSTOP_SMALL')):
   p['o'][0]=1018;p['s'][0]=right-g-1018;p['thickness']=p['s'][0];p['note']='Finished laminate25+18 with assumed0.2 bond, face-machined; not nominal solid stock.';changed.append(id)
 ps=[p for p in ps if not p['id'].startswith('BACKSTOP_PACK')]
 plates=copy.deepcopy(K32['plates'])
 for p in plates:p['o'][0]=endA
 return dict(parts=ps,plates=plates,changed=changed,box_datums='unchanged',status='SYNTHETIC_GEOMETRY_HOLD',assumed_bank_stock='web8, intermediate rails18, plate4, spacer25 unchanged; not measured')

def union(observations):
 out=[]
 for id,items in observations.items():
  lo=[min(p['o'][j] for p in items) for j in range(3)];hi=[max(p['o'][j]+p['s'][j] for p in items) for j in range(3)]
  out.append(block(id,lo,[hi[j]-lo[j] for j in range(3)]))
 return out

def front_hit(b):
 # Conservative maximum front stack45.1mm, circular bore kept at X231/Z250.
 if b['o'][1]>=45.1-1e-9 or b['o'][1]+b['s'][1]<=0:return False
 return max(math.hypot(b['o'][0]+x-231,b['o'][2]+z-250) for x in (0,b['s'][0]) for z in (0,b['s'][2]))>355.8/2+1e-9

def keeper_parts(ass):
 parts=copy.deepcopy(ass['parts'])
 bar=next(p for p in parts if p['id']=='bar');bar['o'][1]=47;bar['s'][1]=310
 return parts

def main():
 observations={};ranges={};bad=[];count=0
 for vals in itertools.product((21.5,22.5),repeat=9):
  t=dict(zip(KEYS,vals));m=build(t);count+=1
  # fixed_solids duplicates IDs for ribs; give stable occurrence indices.
  solids=fixed_solids(m['parts']);ids={}
  for p in solids+m['plates']:
   id=p['id'];idx=ids.get(id,0);ids[id]=idx+1;p=copy.deepcopy(p);p['id']=f'{id}:{idx}';observations.setdefault(p['id'],[]).append(p)
  for p in m['parts']:
   if p['id'] in m['changed']:ranges.setdefault(p['id'],[]).append(p['s'])
  # Plate contact with own portal intentional. No other plate/fixed overlap.
  for plate in m['plates']:
   for ob in solids:
    if ob['id']!='PORTAL' and hit(plate,ob):bad.append([count,plate['id'],ob['id']])
 hull=union(observations);paths=json.loads((R/'wyniki/k30_stale_kanaly_audyt.json').read_text());checks=[]
 for row in paths['box_paths']:
  l,h=(253,76) if row['id'].startswith('M3') else (267.1,96)
  b=block(row['id'],[0,0,0],[l,260,h]);hits=[]
  for i,(a,c) in enumerate(zip(row['waypoints_origin_mm'],row['waypoints_origin_mm'][1:])):
   for ob in hull:
    if hit(swept(b,a,c),ob):hits.append([i,ob['id']])
   if front_hit(swept(b,a,c)):hits.append([i,'FRONT_MAX_STACK'])
  checks.append(dict(kind='box',id=row['id'],collisions=hits))
 for row in paths['separator_paths']:
  h=76 if row['row']==3 else 96;b=block('separator',[0,0,0],[8,260,h]);hits=[]
  for i,(a,c) in enumerate(zip(row['waypoints'],row['waypoints'][1:])):
   for ob in hull:
    if hit(swept(b,a,c),ob):hits.append([i,ob['id']])
   if front_hit(swept(b,a,c)):hits.append([i,'FRONT_MAX_STACK'])
  checks.append(dict(kind='separator',row=row['row'],collisions=hits))
 for row in paths['keeper_paths']:
  ass=next(a for a in K33['assemblies'] if a['row']==row['row'] and a['extended']==row['extended']);hits=[]
  for i,(a,c) in enumerate(zip(row['shifts'],row['shifts'][1:])):
   for b in keeper_parts(ass):
    for ob in hull+K32['hardware']:
     if hit(swept(b,a,c),ob):hits.append([i,b['id'],ob['id']])
    if front_hit(swept(b,a,c)):hits.append([i,b['id'],'FRONT_MAX_STACK'])
  checks.append(dict(kind='keeper',row=row['row'],extended=row['extended'],collisions=hits))
 for diameter in (20,18):
  for row in paths['tool_paths']:
   path=copy.deepcopy(row['waypoints'])
   if row['y']==341:
    for v in path[1:]:v[1]+=6
   offset=(20-diameter)/2
   for v in path:v[1]+=offset;v[2]+=offset
   hits=[]
   for i,(a,c) in enumerate(zip(path,path[1:])):
    sw=swept(block('tool',[0,0,0],[60,diameter,diameter]),a,c)
    for ob in hull:
     if hit(sw,ob):hits.append([i,ob['id']])
    if front_hit(sw):hits.append([i,'FRONT_MAX_STACK'])
   checks.append(dict(kind='tool',diameter_mm=diameter,row=row['row'],y=row['y'],collisions=hits))
 # Three paired replacement metal views, same axes, trimmed front edgeY47.
 O=R/'dokumentacja/cnc/K36_KRAWEDZ_BLOKADY_HOLD';O.mkdir(parents=True,exist_ok=True)
 def drawing():
  d=ezdxf.new('R2010');d.units=4
  for l in ('CUT_OUTER','DRILL_THRU','THREAD_M4_BLIND10','INFO_NO_CUT'):d.layers.new(l)
  return d,d.modelspace()
 from k31_zlacze_i_pasowania import profile
 for name,extended in [('KROTKA',False),('DLUGA',True)]:
  d,ms=drawing();profile(ms,'CUT_OUTER',0,0,310,50)
  for yy in (8,300):ms.add_circle((yy,25),3,dxfattribs={'layer':'DRILL_THRU'})
  if extended:
   for yy in (133,173):
    for zz in (10,40):ms.add_circle((yy,zz),2,dxfattribs={'layer':'THREAD_M4_BLIND10'})
  ms.add_text('K36 METAL FACE Y47..357; HOLD',dxfattribs={'insert':(0,57),'height':3,'layer':'INFO_NO_CUT'})
  d.saveas(O/(name+'_CZOLO_YZ_HOLD.dxf'))
 d,ms=drawing();k=-math.tan(math.pi/8)
 ms.add_lwpolyline([(0,0,0),(18,0,0),(18,109,k),(22,113,0),(40,113,0),(40,193,0),(22,193,k),(18,197,0),(18,310,0),(0,310,0)],format='xyb',close=True,dxfattribs={'layer':'CUT_OUTER'})
 ms.add_text('K36 SHORT XY extrude Z50; paired face drawing; HOLD',dxfattribs={'insert':(0,318),'height':3,'layer':'INFO_NO_CUT'});d.saveas(O/'KROTKA_OBRYS_XY_Z50_HOLD.dxf')
 result=dict(status='CNC_HOLD',corner_count=count,plate_static_collisions=bad,motions=checks,
  hull_method='Per stable obstacle AABB union over512 corners; global R4 windows unchanged. Explicit max45.1mm front stack and circular bore check; not hand clearance.',keeper_assemblies=[dict(row=a['row'],extended=a['extended'],parts=keeper_parts(a)) for a in K33['assemblies']],
  changed_size_ranges={id:[[min(s[j] for s in sizes),max(s[j] for s in sizes)] for j in range(3)] for id,sizes in ranges.items()},
  nominal=build(dict.fromkeys(KEYS,22.)),limitations=['Bank stock thickness remains nominal','Face machining and adhesive not qualified','No actual hardware/stock measurements','Other box/keeper mutual occupancy inherited from K30/K33; incremental fixed-scene check'])
 (R/'wyniki/k36_bank_z_pomiarow.json').write_text(json.dumps(result,indent=2)+'\n')
 files=['brief_system_audio_DIY_v0.6.md','wyniki/k30_czesci.json','wyniki/k30_stale_kanaly_audyt.json','wyniki/k32_retencja.json','wyniki/k33_sztywna_blokada.json','skrypty/k35_korpus_z_pomiarow.py','skrypty/k36_bank_z_pomiarow.py']
 (R/'wyniki/k36_manifest.json').write_text(json.dumps({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
 print(json.dumps({'corners':count,'plate_failures':bad[:8],'motion_failures':[c for c in checks if c['collisions']],'motion_count':len(checks)},indent=2))
if __name__=='__main__':main()
