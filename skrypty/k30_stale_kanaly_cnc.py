#!/usr/bin/env python3
"""K30: independent fixed-channel redesign; dimensioned CAD, NOT released CAM.
Coordinates mm: X long side, Y depth, Z height. Only front driver access.
Run from repository root. No network access. Python + ezdxf + matplotlib.
"""
import json, math, csv, hashlib, itertools, sys
from pathlib import Path
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'dane/k30_zalozenia.json').read_text())
OUT=ROOT/'dokumentacja/cnc/K30_STALE_KANALY_HOLD';OUT.mkdir(parents=True,exist_ok=True)
for stale in OUT.glob('*.dxf'): stale.unlink()
PARTS=[]; SOLIDS=[]; BOXES=[]; HARDWARE=[]

def box(id,o,s,kind='fixed'):
    return dict(id=id,o=list(o),s=list(s),kind=kind)
def solid(id,o,s,kind='fixed'):
    b=box(id,o,s,kind);SOLIDS.append(b);return b
def part(id,o,s,axis,kind='fixed',holes=(),windows=(),note=''):
    uv=[j for j in range(3) if j!=axis]
    p=dict(id=id,o=list(o),s=list(s),thickness=s[axis],axis=axis,uv=uv,
           flat=[s[j] for j in uv],holes=list(holes),windows=list(windows),kind=kind,note=note)
    PARTS.append(p)
    # Rounded portal openings are represented by a conservative rectangle INSIDE
    # each R4 opening; extra R4 corner material checked by dedicated corner test.
    if not windows:
        if not holes or kind!='front':solid(id,o,s,kind)
    else:
        # Four full-width rectangular openings in this frame, all same U bounds.
        u0,u1=windows[0][0],windows[0][2]
        def rect(name,u,v,a,b):
            oo=list(o);ss=list(s);oo[uv[0]]+=u;oo[uv[1]]+=v;ss[uv[0]]=a;ss[uv[1]]=b
            solid(name,oo,ss,kind)
        rect(id+'_front_web',0,0,u0,p['flat'][1]);rect(id+'_rear_web',u1,0,p['flat'][0]-u1,p['flat'][1])
        cursor=0
        for i,(_,v0,_,v1,r) in enumerate(windows):
            rect(id+'_rib_'+str(i),u0,cursor,u1-u0,v0-cursor);cursor=v1
        rect(id+'_rib_top',u0,cursor,u1-u0,p['flat'][1]-cursor)
    return p

def overlap(a,b,tol=1e-7):
    return all(min(a['o'][j]+a['s'][j],b['o'][j]+b['s'][j])-max(a['o'][j],b['o'][j])>tol for j in range(3))
def sweep(o1,o2,size):
    return box('sweep',[min(a,b) for a,b in zip(o1,o2)],[s+abs(a-b) for a,b,s in zip(o1,o2,size)])
def volume(b):return math.prod(b['s'])/1e6

def module(id,x,z,L,h):
    o=[x,70,z];sz=[L,260,h];b=box(id,o,sz,'insert');BOXES.append(b)
    # Full-height X end cheeks set assembled height; Y walls butt between cheeks;
    # top/bottom fit INSIDE walls. Stock thickness variation does not silently
    # increase nominal external height by twice the stock tolerance.
    e=8
    faces=[('XL',[x,70,z],[e,260,h],0),('XR',[x+L-e,70,z],[e,260,h],0),
           ('YF',[x+e,70,z],[L-2*e,e,h],1),('YR',[x+e,322,z],[L-2*e,e,h],1),
           ('ZB',[x+e,78,z],[L-2*e,244,e],2),('ZT',[x+e,78,z+h-e],[L-2*e,244,e],2)]
    for suffix,oo,ss,ax in faces:part(id+'_'+suffix,oo,ss,ax,'insert_panel',note='Nominal butt glue joint; regenerate from measured sheet thickness before release')
    return b

W,D,H=C['body_xyz_mm'];F=44;T=22
for k,y in enumerate([0,22]):part('FR'+str(k+1),[0,y,0],[W,22,H],1,'front',holes=[(231,250,177.9)],note='REFERENCE bore only. Basket screw/retention not released.')
part('BACK',[0,D-22,0],[W,22,H],1,note='Terminal opening unresolved; not a complete fabrication part')
for k,x in [('L',0),('R',W-22)]:part('SIDE_'+k,[x,44,0],[22,D-66,500],0)
for k,z in [('BOTTOM',0),('TOP',478)]:part(k,[22,44,z],[W-44,D-66,22],2)
# Front of bank: single MDF22 portal, four R4 window cuts; fixed before closing shell.
wins=[]
for z,h in zip(C['row_base_z_mm'],C['row_box_height_mm']):wins.append((20,z-22-2,292,z-22+h+4,4))
part('PORTAL',[448,44,22],[22,D-66,456],0,windows=wins,
     holes=[(y-44,z+h/2-22,3) for z,h in zip(C['row_base_z_mm'],C['row_box_height_mm']) for y in (55,341)],
     note='R4 windows; face-drilled 6mm stop-bolt clearance; no edge drilling')
# A second full-height portal supports the long channels at midspan. Rails
# and side webs are split at its faces: no intersecting solid joints.
midwins=[(20,z-22,292,z-22+h+2,4) for z,h in zip(C['row_base_z_mm'],C['row_box_height_mm'])]
part('MID_PORTAL',[750,44,22],[22,D-66,456],0,windows=midwins,note='Intermediate load path, R4 window, contact with rail ends; glued full frame perimeter')
for seg,xa,xb in [('A',474,750),('B',772,1058)]:
    for k,y in [('F',60),('R',332)]:part('CHANNEL_WEB_'+seg+'_'+k,[xa,y,22],[xb-xa,8,456],1)
for seg,xa,xb in [('A',470,750),('B',772,1058)]:
    for r,z in enumerate(C['row_base_z_mm']):
        for k,y in [('F',68),('R',282)]:part(f'RAIL_{seg}_{r}_{k}',[xa,y,z-18],[xb-xa,50,18],2,note='Long-edge glue to side web, end support at portal; datum jig required')
    for k,y in [('F',68),('R',282)]:part('TOP_KEEPER_'+seg+'_'+k,[xa,y,466],[xb-xa,50,12],2)
# Contact at right wall is positive in X; replace a loose insert system by channels.
for r,(z,h,v) in enumerate(zip(C['row_base_z_mm'],C['row_box_height_mm'],C['box_volume_l'])):
    L=round(v*1e6/(260*h),1)
    module(f'M{r}N',474,z,L,h);module(f'M{r}F',474+L+8,z,L,h)
    # Separator is loose but captured BETWEEN boxes; no fastening fiction.
    part(f'SEP_{r}',[474+L,70,z],[8,260,h],0,'separator')
    part(f'BACKSTOP_{r}',[1018,70,z],[22,260,h],0,note='Bond to right wall, whole end face; hardware qualification open')
    part(f'BACKSTOP_PACK_{r}',[1040,70,z],[18,260,h],0,note='Second backstop laminate to right wall')
    if r==3:part('BACKSTOP_SMALL_EXTRA',[993,70,z],[25,260,h],0,note='Additional end spacer for short boxes; compressible pad to be sized after measurement')
    # Stop assembled after boxes. Its plane is normal X, both bolts face tool.
    part(f'STOP_{r}',[430,45,z+h/2-25],[18,306,50],0,'stop',holes=[(10,25,3),(296,25,3)],note='M5 proposed through 6mm clearance; 2 captive metal nuts behind portal; not wood-edge screws')
    part(f'NOSE_{r}',[448,160,z+h/2-25],[22,80,50],0,'stop',note='22mm bearing nose plus adjustable 4mm nominal compliant contact to box at X474')
    # Finite hardware envelopes; dimensional design assumptions, no invented product.
    for j,y in enumerate((55,341)):
        HARDWARE += [box(f'NUT_PLATE_{r}_{j}',[470,y-9,z+h/2-15],[4,18,30],'metal'),
                     box(f'M5_SHANK_{r}_{j}',[429,y-2.5,z+h/2-2.5],[45,5,5],'metal'),
                     box(f'M5_HEAD_{r}_{j}',[424,y-5,z+h/2-5],[5,10,10],'metal')]
# Mat remains porous: geometric keepout, NOT subtraction of full 50mm slab as solid.
MAT=box('MAT_50_KEEP_OUT',[22,D-72,22],[W-44,50,456],'porous')

# Nominal fabrication DXFs: one part, one local datum, no nesting or path compensation.
def rounded_rect(m,layer,u,v,w,h,r):
    if r==0:
        m.add_lwpolyline([(u,v),(u+w,v),(u+w,v+h),(u,v+h)],close=True,dxfattribs={'layer':layer})
        return
    k=math.tan(math.pi/8)
    pts=[(u+r,v,0),(u+w-r,v,k),(u+w,v+r,0),(u+w,v+h-r,k),
         (u+w-r,v+h,0),(u+r,v+h,k),(u,v+h-r,0),(u,v+r,k)]
    m.add_lwpolyline(pts,format='xyb',close=True,dxfattribs={'layer':layer})
for p in PARTS:
    d=ezdxf.new('R2010');d.units=4;d.header['$MEASUREMENT']=1
    for name,col in [('CUT_OUTER',7),('CUT_INNER',1),('DRILL_THRU',3),('INFO_NO_CUT',8)]:d.layers.new(name,dxfattribs={'color':col})
    m=d.modelspace();a,b=p['flat'];rounded_rect(m,'CUT_OUTER',0,0,a,b,0)
    for u,v,r in p['holes']:m.add_circle((u,v),r,dxfattribs={'layer':'CUT_INNER' if r>12 else 'DRILL_THRU'})
    for u0,v0,u1,v1,r in p['windows']:rounded_rect(m,'CUT_INNER',u0,v0,u1-u0,v1-v0,r)
    m.add_text(p['id']+' / '+str(p['thickness'])+'mm / CNC HOLD',dxfattribs={'height':3,'insert':(0,b+8),'layer':'INFO_NO_CUT'})
    d.saveas(OUT/(p['id']+'.dxf'))

# Scene, assembly & literal CAD limits.
fixed=[b for b in SOLIDS if b['kind']=='fixed']
collisions=[]
for a,b in itertools.combinations(fixed+BOXES,2):
    if overlap(a,b):collisions.append([a['id'],b['id']])
# All stock sheets are dimensioned as nominal; do not conceal shell intersections.
# No shell front AABB in path obstacles: entry circle checked independently.
paths=[];installed=[]
order=[f'M{r}{side}' for r in range(4) for side in ('F','N')]
for id in order:
    b=next(b for b in BOXES if b['id']==id);L,Y,h=b['s'];z=b['o'][2]
    startx=231-L/2
    pts=[[startx,-Y-10,250-h/2],[startx,70,250-h/2],[startx,70,z+0.6],[b['o'][0],70,z+0.6],b['o']]
    hits=[]
    for j,(a,c) in enumerate(zip(pts,pts[1:])):
        sw=sweep(a,c,b['s'])
        for ob in fixed+installed+[MAT]+[q for q in HARDWARE if 'NUT_PLATE' in q['id']]:
            if overlap(sw,ob):hits.append([j,ob['id']])
    radius=math.hypot(L/2,h/2)
    # R4 corner constraint for actual box cross-section through PORTAL yz aperture.
    # Bounds: Y64..336, Zbase-2..base+h+4. Min left/bottom corner offsets6,2.
    # At 6mm from side, point is outside corner arc zone of R4, so exact square
    # box corners fit. Positive Z insertion reserve independent of tool radius.
    rec=dict(id=id,waypoints_origin_mm=pts,entry_corner_radius_mm=radius,
             entry_margin_mm=177.9-radius,swept_collisions=hits,portal_R4_square_corner_clear=True,
             pass_nominal=len(hits)==0 and radius<177.9)
    paths.append(rec);installed.append(b)

# Static stop/mat collision check, separate from the moving-tool envelope.
stop_mat_hits=[]
for b in SOLIDS:
    if b['kind']=='stop' and overlap(b,MAT):stop_mat_hits.append(b['id'])
# Access test of tool box 60x20x20 about X axis; excludes intentional tool/head contact.
tool_checks=[]
for r,(z,h) in enumerate(zip(C['row_base_z_mm'],C['row_box_height_mm'])):
    for y in (55,341):
        size=[60,20,20];target=[364,y-10,z+h/2-10]
        pts=[[201,-30,240],[201,y-10,240],[201,y-10,target[2]],target]
        hits=[]
        for j,(a,c) in enumerate(zip(pts,pts[1:])):
            for ob in fixed+BOXES+[MAT]:
                if overlap(sweep(a,c,size),ob):hits.append([j,ob['id']])
        tool_checks.append(dict(row=r,y=y,waypoints=pts,collisions=hits,pass_nominal=not hits))

# Check full finite keeper assembly (bar + nose), not an infinitesimal axis.
# Standard and extended variants enter centred in the driver circle, translate Y,
# then Z, then X. All row bolts removed first. No fixed supports are removed.
keeper_paths=[]
for r,(z,h) in enumerate(zip(C['row_base_z_mm'],C['row_box_height_mm'])):
    for extended in ([False,True] if r==1 else [False]):
        bar=box('bar',[430,45,z+h/2-25],[18,306,50])
        end=next(b for b in BOXES if b['id']=='M1F')['o'][0]-2 if extended else 470
        nose=box('reach',[448,190,z+h/2-10],[end-448,20,20]) if extended else box('nose',[448,160,z+h/2-25],[22,80,50])
        # Base/end plates are inside conservative nose envelope except broad base.
        pieces=[bar,nose]
        if extended:pieces.append(box('base',[448,160,z+h/2-25],[4,80,50]))
        xmin=430;xmax=end;dx=231-(xmin+xmax)/2;dz=250-(z+h/2)
        shifts=[[dx,-400,dz],[dx,0,dz],[dx,0,0],[0,0,0]]
        obs=fixed+[MAT]+[q for q in HARDWARE if 'NUT_PLATE' in q['id']]+[b for b in BOXES if not(extended and b['id']=='M1N')]
        hits=[]
        for j,(a,c) in enumerate(zip(shifts,shifts[1:])):
            for p in pieces:
                o1=[p['o'][k]+a[k] for k in range(3)];o2=[p['o'][k]+c[k] for k in range(3)]
                for ob in obs:
                    if overlap(sweep(o1,o2,p['s']),ob):hits.append([j,p['id'],ob['id']])
        keeper_paths.append(dict(row=r,extended=extended,shifts=shifts,pieces=pieces,
            entry_margin_mm=177.9-math.hypot((xmax-xmin)/2,25),collisions=hits,pass_nominal=not hits))
# Separator insertion after far box, before near box; removable in reverse order.
separator_paths=[]
for r,(z,h) in enumerate(zip(C['row_base_z_mm'],C['row_box_height_mm'])):
    p=next(b for b in SOLIDS if b['id']==f'SEP_{r}')
    pts=[[227,-270,250-h/2],[227,70,250-h/2],[227,70,z+0.6],[p['o'][0],70,z+0.6],p['o']]
    obs=fixed+[MAT]+[b for b in BOXES if b['id']!=f'M{r}N'];hits=[]
    for j,(a,c) in enumerate(zip(pts,pts[1:])):
        for ob in obs:
            if overlap(sweep(a,c,p['s']),ob):hits.append([j,ob['id']])
    separator_paths.append(dict(row=r,waypoints=pts,collisions=hits,pass_nominal=not hits))

# Nominal displacement accounting (metal envelopes and other hardware approximate) of disjoint interior rectangles, frame R4 correction,
# and 8 closed boxes; sleeve void air cannot be counted twice.
inner=(W-44)*(D-66)*456/1e6
interior=[p for p in PARTS if p['kind']=='fixed' and p['id'] not in ['BACK','SIDE_L','SIDE_R','BOTTOM','TOP']]
perm=0
for p in interior:
    vol=math.prod(p['s'])
    for u,v,U,V,r in p['windows']:vol-=((U-u)*(V-v)-(4-math.pi)*r*r)*p['thickness']
    for u,v,r in p['holes']:vol-=math.pi*r*r*p['thickness']
    perm+=vol/1e6
# Keep empty-bank stops installed; loose separators removed with boxes.
stop_volume=sum(math.prod(p['s']) for p in PARTS if p['kind']=='stop')/1e6
metal_volume=sum(volume(b) for b in HARDWARE if 'SHANK' not in b['id']) # conservative heads/plates only; other hardware provisional below
base=inner-perm-stop_volume-metal_volume-5-.175
# Replace row1 standard nose with a sealed 20x20 metal reach tube and base plate.
long_stop_length=next(b for b in BOXES if b['id']=='M1F')['o'][0]-2-452
long_keeper_extra_l=long_stop_length*20*20/1e6+4*80*50/1e6-22*80*50/1e6
state_ids={'max_150_target':[], 'middle_120_target':['M0N','M0F','M1F','M3N','M3F'], 'min_100_target':order}
volumes={}
for state,ids in state_ids.items():
    displacement=sum(volume(b) for b in BOXES if b['id'] in ids)
    sep=sum(volume(b) for b in SOLIDS if b['kind']=='separator' and all(f'M{b["id"][-1]}{s}' in ids for s in ('N','F')))
    volumes[state]=dict(insert_ids=ids,closed_box_displacement_l=displacement,separator_displacement_l=sep,
        provisional_free_air_l=base-displacement-sep-(long_keeper_extra_l if state=='middle_120_target' else 0),
        unresolved='Provisional metal envelope accounting; real basket, glue, sealing, pads and fastener union remain unmeasured.')

# Basic rail bending screen: conservative end-only point load at midspan.
masses=[]
for b in BOXES:
    shell=math.prod(b['s'])-math.prod([s-16 for s in b['s']]);masses.append(shell/1e9*730)
Fpair=max(masses)*2*5*9.81/2;L=286;b=50;t=18;E=2700;I=b*t**3/12
stress=1.5*Fpair*L/(b*t*t);defl=Fpair*L**3/(48*E*I)
# Independent drawing reload and actual tool radius checks.
dxf_errors=[];small_blanks=[]
for p in PARTS:
    d=ezdxf.readfile(OUT/(p['id']+'.dxf'))
    if d.units!=4 or d.audit().errors:dxf_errors.append(p['id'])
    for e in d.modelspace().query('LWPOLYLINE'):
        if not e.closed:dxf_errors.append(p['id']+':open')
    if min(p['flat'])<50:small_blanks.append(p['id'])

result=dict(revision=C['revision'],status='CNC_HOLD',parts=len(PARTS),fixed_box_collisions=collisions,
    box_paths=paths,keeper_paths=keeper_paths,separator_paths=separator_paths,reverse_paths='Reverse exact segments valid if reverse order and all row stops removed; unsupported handling is not certified',
    keeper_mat_collisions=stop_mat_hits,tool_paths=tool_checks,inner_gross_l=inner,
    fixed_wood_displacement_l=perm,stop_displacement_l=stop_volume,volume_states=volumes,
    rail_end_only_screen=dict(load_per_rail_N=Fpair,stress_MPa=stress,deflection_mm=defl,allowable=None),
    dxf_readback_errors=dxf_errors,below_supplier_minimum_blanks=small_blanks,
    manufacturing_blocks=['Real driver / mounting / terminal geometry absent',
      'Nominal box assembly ignores glue-line and real stock thickness: regenerate after metrology',
      'Measured hand / tool envelope and stop removal assembly must be validated',
      'Extended keeper geometry provided; its metal/MDF attachment and bending require qualification',
      'MDF bond, captive metal plates, stop loading and rail deflection unqualified',
      'Full cabinet bending and acoustic models must be recomputed after redesign'])
(ROOT/'wyniki/k30_stale_kanaly_audyt.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
(ROOT/'wyniki/k30_czesci.json').write_text(json.dumps(PARTS,indent=2,ensure_ascii=False)+'\n')
with (OUT/'LISTA_CZESCI.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['ID','MDF_mm','U_mm','V_mm','qty','global_X','global_Y','global_Z','normal_axis','status','notes'])
    for p in PARTS:w.writerow([p['id'],p['thickness'],*p['flat'],1,*p['o'],'XYZ'[p['axis']],'CNC_HOLD',p['note']])
# SCAD, including R4 frame approximation disclosed in label; DXF is analytic R4.
sc=['// K30 nominal research assembly, CNC HOLD. Axes X width Y depth Z height.', '$fn=96;', 'state=100; // choose 100,120,150; targets, not measured volumes']
for p in PARTS:
    if p['kind']=='insert_panel':color=[0.75,0.47,0.2,0.65]
    elif p['kind']=='stop':color=[0.8,0.2,0.2,1]
    else:color=[0.65,0.65,0.72,0.4]
    prefix=''
    if p['kind']=='insert_panel':
        keep=p['id'][:3] in state_ids['middle_120_target']
        prefix='if(state==100'+(' || state==120' if keep else '')+') '
    elif p['kind']=='separator':prefix='if(state==100'+(' || state==120' if p['id'] in ['SEP_0','SEP_3'] else '')+') '
    elif p['id']=='NOSE_1':prefix='if(state!=120) '
    sc.append(prefix+'color('+str(color)+') difference(){translate('+str(p['o'])+') cube('+str(p['s'])+');')
    for u,v,r in p['holes']:
        pos=list(p['o']);pos[p['uv'][0]]+=u;pos[p['uv'][1]]+=v;pos[p['axis']]-=1
        rot=[[0,90,0],[90,0,0],[0,0,0]][p['axis']]
        if p['axis']==1:pos[1]+=p['thickness']+2
        sc.append(f'translate({pos}) rotate({rot}) cylinder(h={p["thickness"]+2},r={r});')
    for u,v,U,V,r in p['windows']:
        # Exact rounded rectangle via four corner cylinders along X.
        sc.append('hull(){')
        for yy,zz in itertools.product([u+r,U-r],[v+r,V-r]):
            sc.append(f'translate([{p["o"][0]-1},{p["o"][1]+yy},{p["o"][2]+zz}]) rotate([0,90,0]) cylinder(h=24,r={r});')
        sc.append('}')
    sc.append('}')
for b in HARDWARE:
    sc.append('color([0.4,0.45,0.5]) translate('+str(b['o'])+') cube('+str(b['s'])+');')
sc.append(f'if(state==120) color([0.6,0.2,0.2]) {{translate([448,160,179]) cube([4,80,50]); difference(){{translate([452,190,194]) cube([{long_stop_length},20,20]); translate([454,192,196]) cube([{long_stop_length-4},16,16]);}}}}')
(OUT/'K30_ZLOZENIE_HOLD.scad').write_text('\n'.join(sc)+'\n')
fig,ax=plt.subplots(2,1,figsize=(13,9),constrained_layout=True)
for a in ax:a.set_aspect('equal');a.grid(alpha=.15)
for b in fixed:
    if b['id'] not in ['BACK','SIDE_L','SIDE_R','BOTTOM','TOP']:
        ax[0].add_patch(Rectangle((b['o'][0],b['o'][2]),b['s'][0],b['s'][2],fill=False,edgecolor='#697688',alpha=.5))
for b in BOXES:
    ax[0].add_patch(Rectangle((b['o'][0],b['o'][2]),b['s'][0],b['s'][2],facecolor='#d7aa67',alpha=.65,edgecolor='#674d2d'))
    ax[0].text(b['o'][0]+b['s'][0]/2,b['o'][2]+b['s'][2]/2,b['id'],ha='center')
ax[0].add_patch(Circle((231,250),177.9,fill=False,color='#176faa'))
ax[0].set(xlim=(-10,W+10),ylim=(0,510),xlabel='X [mm]',ylabel='Z [mm]',title='K30 | Stałe kanały, 8 wkładów | widok z przodu | CNC HOLD')
for b in BOXES[:2]:ax[1].add_patch(Rectangle((b['o'][0],b['o'][1]),b['s'][0],b['s'][1],facecolor='#d7aa67',edgecolor='#674d2d'))
p=paths[0];pts=p['waypoints_origin_mm'];ax[1].plot([q[0]+BOXES[1]['s'][0]/2 for q in pts],[q[1]+130 for q in pts],'-o',color='#176faa',label='Tor środka pierwszego wkładu')
ax[1].add_patch(Rectangle((22,D-72),W-44,50,facecolor='#96b39b',alpha=.5,label='Mata 50 mm'))
ax[1].set(xlim=(-10,W+10),ylim=(-200,430),xlabel='X [mm]',ylabel='Y [mm]',title='Widok z góry: wejście przez front, następnie przesunięcie w bok')
ax[1].legend(loc='lower right')
fig.savefig(ROOT/'wyniki/k30_stale_kanaly_HOLD.png',dpi=150);fig.savefig(ROOT/'wyniki/k30_stale_kanaly_HOLD.svg');plt.close(fig)
manifest={'inputs':{},'python':sys.version,'ezdxf':ezdxf.__version__,'matplotlib':matplotlib.__version__}
for p in ['dane/k30_zalozenia.json','skrypty/k30_stale_kanaly_cnc.py','brief_system_audio_DIY_v0.6.md']:
    manifest['inputs'][p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
(ROOT/'wyniki/k30_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['box_paths','tool_paths','keeper_paths','separator_paths']},indent=2))
