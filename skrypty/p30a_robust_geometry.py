#!/usr/bin/env python3
"""P30A: reproducible parametric check of P20D shallow prototypes.
Research geometry only; not CAD, FEM, hardware, or CNC approval.
Requires NumPy; no SciPy. Selected modules and braces from P20D report 057.
"""
import csv, json, math
from collections import deque
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
ROOT=(ROOT.parent/"wyniki") if ROOT.name=="skrypty" else ROOT
WALL=22.; FRONT=44.; HOUT=500.; X_START=426.; T=22.; RIM=22.; FRONT_RIM=10.
CLEARANCE=3.; DENSITY_MAT=20.; DENSITY_SOLID=1380.;
CANDIDATES=[
    (1000,440,50),    # original P20D
    (1000,435,45),    # 5mm less front mat
    (1020,435,45),    # widen 20mm
    (1040,430,40),    # widen 40mm, shave 10mm mat
    (1050,425,35),    # widen 50mm, shave 15mm mat
    (1055,420,30),    # widen 55mm, shave 20mm mat
]
def box(lo,hi):return np.array([lo,hi],dtype=float)
def volume(b):return float(np.prod(b[1]-b[0]))
def intersect(a,b):return bool(np.all(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])>1e-8))
def overlap_volume(a,b):return float(np.prod(np.maximum(0,np.minimum(a[1],b[1])-np.maximum(a[0],b[0]))))
def geo(w,d,fill):
    dims=np.array([w-44,d-FRONT-WALL,HOUT-44.]);iw,idepth,ih=dims
    x1=X_START;x2=(X_START+T+iw)/2-T/2
    braces=[]
    for x in (x1,x2):
        braces += [box([x,0,0],[x+T,idepth,T]),box([x,0,ih-T],[x+T,idepth,ih]),
           box([x,0,T],[x+T,FRONT_RIM,ih-T]),box([x,idepth-T,T],[x+T,idepth,ih-T])]
    braces += [box([198,220,0],[220,idepth,T]),box([198,220,ih-T],[220,idepth,ih]),
       box([198,idepth-T,T],[220,idepth,ih-T])]
    xs=[(X_START+T+x2)/2,(x2+T+iw)/2]
    large=[box(np.array([x,y,z])-np.array([210,150,100])/2,np.array([x,y,z])+np.array([210,150,100])/2)
       for x in xs[::-1] for y in (243,83) for z in (62,392,172,282)]
    small=[box([x-90,218,z-50],[x+90,318,z+50]) for x,z in ((99,90),(99,366),(323,90),(323,366))]
    modules=small+large
    mat=box([0,idepth-fill,0],dims)
    return dims,braces,modules,mat

def analyse(w,d,fill):
    L,br,mod,mat=geo(w,d,fill);wi,dep,hei=L
    brace_l=sum(volume(x) for x in br)/1e6
    # Braces must not overlap for this simple volume sum to be exact.
    assert not any(intersect(a,b) for i,a in enumerate(br) for b in br[i+1:])
    mat_occupied=volume(mat)-sum(overlap_volume(mat,b) for b in br)
    net0=math.prod(L)/1e6-brace_l-5-.175-(mat_occupied/1e6)*DENSITY_MAT/DENSITY_SOLID
    low=((wi-2)*(dep-2)*(hei-2))/1e6-brace_l*1.05-8-.3-(mat_occupied/1e6)*30/1300
    high=((wi+2)*(dep+2)*(hei+2))/1e6-brace_l*.95-2-.05-(mat_occupied/1e6)*10/1400
    flags=[]
    for n,b in enumerate(mod):
        env=b+np.array([[-CLEARANCE]*3,[CLEARANCE]*3])
        if np.any(env[0]<0) or np.any(env[1]>L):flags.append(f'{n}:outside')
        if any(intersect(env,a) for a in br):flags.append(f'{n}:brace')
        if intersect(env,mat):flags.append(f'{n}:mat')
        if any(intersect(env,a) for a in mod[:n]):flags.append(f'{n}:another module')
    basket=box([209-194.2,0,228-194.2],[209+194.2,178,228+194.2])
    basket_collision=sum(intersect(basket,a) for a in br+mod+[mat])
    choose_counts={
       '150_l':(2,0),'120_l':(11,1),'100_l':(16,3)
    }
    return dict(width_mm=w,body_depth_mm=d,body_height_mm=500,rear_mat_thickness_mm=fill,
      inside_mm=L.tolist(),rear_mat_start_y_mm=float(dep-fill),braces_l=round(brace_l,4),
      net_empty_nom_l=round(net0,4),net_empty_stress_l=[round(low,4),round(high,4)],
      family_p20d_counts={k:dict(large=n,small=s,net_nom_l=round(net0-n*3.15-s*1.8,4),
       net_stress_l=[round(low-n*3.15-s*1.8,4),round(high-n*3.15-s*1.8,4)]) for k,(n,s) in choose_counts.items()},
      total_depth_min_mm=d+36,total_depth_max_mm=d+56,margin_worst_mm=500-d-56,
      margin_already_includes_total_depth_allowance_mm=2,
      static_collisions=flags,basket_AABB_collisions=basket_collision,
      module_mat_front_gap_mm=float(dep-fill-max(x[1,1] for x in mod)),
      insert_clearance_after_hardware_mm=float(dep-fill-max(x[1,1] for x in mod)-CLEARANCE))

def segment_box(a,b,half):return box(np.minimum(a,b)-half,np.maximum(a,b)+half)
def path_to(target,L,obs,half):
    start=np.array([209.,105.,228.]);target=np.asarray(target,dtype=float)
    axes=[]
    for j in range(3):
        values=[start[j],target[j],half[j]+.01,L[j]-half[j]-.01]
        for b in obs:values.extend([b[0,j]-half[j]-.01,b[1,j]+half[j]+.01])
        axes.append(np.unique([round(v,5) for v in values if half[j]<=v<=L[j]-half[j]]))
    shape=tuple(len(a) for a in axes)
    mesh=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    valid=np.ones(shape,bool)
    for b in obs:valid&=~np.all((mesh>b[0]-half+1e-8)&(mesh<b[1]+half-1e-8),axis=-1)
    idx=lambda p:tuple(int(np.argmin(abs(a-v))) for a,v in zip(axes,p))
    source,dest=idx(start),idx(target)
    if not valid[source] or not valid[dest]:return None
    q=deque([source]);back={source:None}
    while q:
        cur=q.popleft()
        if cur==dest:break
        for j in range(3):
            for sign in (-1,1):
                nextidx=list(cur);nextidx[j]+=sign;nextidx=tuple(nextidx)
                if nextidx in back or not 0<=nextidx[j]<shape[j] or not valid[nextidx]:continue
                sw=segment_box(mesh[cur],mesh[nextidx],half)
                if any(intersect(sw,b) for b in obs):continue
                back[nextidx]=cur;q.append(nextidx)
    if dest not in back:return None
    result=[];cur=dest
    while cur is not None:
        result.append(mesh[cur].tolist());cur=back[cur]
    return result[::-1]

def test_paths(w,d,fill):
    L,br,mods,mat=geo(w,d,fill)
    placed=[];res=[]
    for j,m in enumerate(mods):
        half=(m[1]-m[0])/2+CLEARANCE
        p=path_to(m.mean(axis=0),L,br+placed+[mat],half)
        if p is None:
            res.append(dict(module=j,passed=False));break
        assert all(not any(intersect(segment_box(np.array(a),np.array(b),half),o) for o in br+placed+[mat]) for a,b in zip(p,p[1:]))
        assert math.hypot(half[0],half[2]) < 288/2
        res.append(dict(module=j,passed=True,segments=len(p)-1));placed.append(m)
    return dict(tested_modules=len(res),paths_passed=sum(x['passed'] for x in res),
       total_segments=sum(x.get('segments',0) for x in res),first_failure=next((x['module'] for x in res if not x['passed']),None),
       verdict=('20_of_20_in_translational_roadmap' if len(res)==20 and all(x['passed'] for x in res) else 'NOT_VALIDATED'))

def main():
    rows=[analyse(*c) for c in CANDIDATES]
    assert rows[0]['static_collisions']==[],rows[0]
    assert abs(rows[0]['net_empty_nom_l']-155.9073)<1e-3
    assert rows[0]['total_depth_max_mm']==496
    # Original P20D module ingress path test, plus alternatives to preserve kinematic feasibility.
    paths={}
    for w,d,fill in ((1000,440,50),(1020,435,45),(1040,430,40),(1050,425,35)):
        paths[f'{w}x{d}_mat{fill}']=test_paths(w,d,fill)
        print(f'paths {w}x{d} mat{fill}: {paths[f"{w}x{d}_mat{fill}"]}',flush=True)
    assert paths['1000x440_mat50']['paths_passed']==20
    for row in rows:
        if row['static_collisions']:
            print('Collision in '+str(row['width_mm'])+': '+str(row['static_collisions'][:5]),flush=True)
    answer={'study':'P30A','status':'P20D geometric sensitivity and translation-only assembly checks, NOT CAD/FEA/CNC signoff',
      'source':'P20D repository report 057 and configuration p20d_geometria.json',
      'design_parameters':{'outer_height_mm':500,'wall_mm':22,'front_mm':44,'nominal_driver_effective_displacement_l':5,
       'nominal_other_hardware_l':.175,'fill_density_kg_m3':20,'fill_solid_density_kg_m3':1380,
       'large_module_dimensions_mm':[210,150,100],'small_module_dimensions_mm':[180,100,100],
       'candidate_variable_mat_thickness':'50 mm baseline; 45/40/35/30 mm alternative; acoustic equivalence not established'},
      'tested_variants':rows,'route_tests':paths,
      'limitations':['No real grille outline, driver resting projection, 3D basket shape, module locking detail or tool/hand clearance.',
       'Assembly path proofs cover only axis-aligned rigid translations and selected waypoint roadmap, with 3mm envelope; gravity, bolt tool, wiring omitted.',
       'Reducing the rear mat from 50mm to 35/40mm invalidates carrying forward the acoustic port results for 50mm without recalculation.',
       'The P20D low/high volume stress bounds describe scenarios, not verified manufacturing tolerances or probability.',
       'Rounded nominal dimensions do not certify target net Vb; actual driver/brace/hardware displacement must be measured.',
       'No FEM structural stiffness at the 10mm front brace rim, no gasket/clamping/long-term humidity or fatigue validation.',
       'Calculated depth bound includes separate nominal 2mm tolerance budget, but unknown actual grille geometry can exceed it.',
       'No material purchase or CNC approval.']}
    out=ROOT/'p30a_geometria_przeglad_20261031.json'
    out.write_text(json.dumps(answer,ensure_ascii=False,indent=2)+'\n')
    print('TABLE')
    for row in rows:
        print(row['width_mm'],row['body_depth_mm'],row['rear_mat_thickness_mm'],row['net_empty_nom_l'],row['family_p20d_counts']['120_l']['net_nom_l'],row['margin_worst_mm'],row['module_mat_front_gap_mm'],len(row['static_collisions']))
    return answer
if __name__=='__main__':main()
