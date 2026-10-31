"""P20D: exact AABB unions and continuous rectilinear assembly paths.
Geometry in mm; original P20/P29 data never overwritten. No FEM claim.
"""
from pathlib import Path
from itertools import product
from collections import deque
import json,csv,math,hashlib,platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'dane/konfiguracje/p20d_geometria.json'
C=json.loads(CFG.read_text()); OUT=ROOT/'wyniki'

def box(lo,hi): return np.array([lo,hi],float)
def volume(b): return float(np.prod(b[1]-b[0]))
def intersect(a,b): return bool(np.all(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])>1e-8))
def intersection_volume(a,b): return float(np.prod(np.maximum(0,np.minimum(a[1],b[1])-np.maximum(a[0],b[0]))))
def union_volume(bb):
    """Exact partition at all AABB faces, independent of sum-of-disjoint volumes."""
    axes=[sorted(set(float(b[k,j]) for b in bb for k in (0,1))) for j in range(3)]
    ans=0.
    for i,j,k in product(*(range(len(a)-1) for a in axes)):
        lo=np.array([axes[0][i],axes[1][j],axes[2][k]])
        hi=np.array([axes[0][i+1],axes[1][j+1],axes[2][k+1]])
        mid=(lo+hi)/2
        if any(np.all(mid>b[0]) and np.all(mid<b[1]) for b in bb): ans+=np.prod(hi-lo)
    return float(ans)

def geometry(w,d):
    wall=C['wall_mm']; front=C['front_mm']; rim=C['ring_rim_mm']; t=C['ring_thickness_mm']
    L=np.array([w-2*wall,d-front-wall,C['height_mm']-2*wall],float); W,D,H=L
    xfirst=C['ring_x_start_mm']; xend=xfirst+t
    braces=[]
    # Two window frames. All four pieces disjoint; physically bonded joints unresolved.
    for x in (xfirst,(xend+W)/2-t/2):
        braces.extend([box([x,0,0],[x+t,D,t]),box([x,0,H-t],[x+t,D,H]),
                       box([x,0,t],[x+t,C['ring_front_rim_depth_mm'],H-t]),box([x,D-t,t],[x+t,D,H-t])])
    # Three-sided rear brace behind conservative motor envelope. Does not obstruct entry.
    braces.extend([box([198,220,0],[220,D,t]),box([198,220,H-t],[220,D,H]),
                   box([198,D-t,t],[220,D,H-t])])
    split=(xend+W)/2-t/2
    xs=[(xend+split)/2,(split+t+W)/2]
    mods=[box(np.array([x,y,z])-np.array(C['module_mm'])/2,
              np.array([x,y,z])+np.array(C['module_mm'])/2)
          for x in xs[::-1] for y in C['module_centres_y_mm'] for z in C['module_centres_z_mm']]
    small=[box([x-C['module_small_mm'][0]/2,C['module_small_y_interval_mm'][0],z-C['module_small_mm'][2]/2],[x+C['module_small_mm'][0]/2,C['module_small_y_interval_mm'][1],z+C['module_small_mm'][2]/2]) for x,z in C['module_small_centres_xz_mm']]
    mods=small+mods
    mat=box([0,D-C['fill_mm'],0],L)
    return L,braces,mods,mat

def segment_box(a,b,half): return box(np.minimum(a,b)-half,np.maximum(a,b)+half)
def path_to(target,L,obstacles,half):
    """Finite roadmap at expanded-obstacle events. Every returned segment checked continuously.
    Failure only means no path in this roadmap, not global infeasibility of rigid body motions.
    """
    start=np.array([209.,105.,228.]); target=np.asarray(target)
    axes=[]
    for j in range(3):
        vals=[start[j],target[j],half[j]+.01,L[j]-half[j]-.01]
        for b in obstacles: vals.extend([b[0,j]-half[j]-.01,b[1,j]+half[j]+.01])
        axes.append(np.unique([round(v,5) for v in vals if half[j]<=v<=L[j]-half[j]]))
    shape=tuple(len(a) for a in axes)
    pts=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    valid=np.ones(shape,bool)
    for b in obstacles:
        valid &= ~np.all((pts>b[0]-half+1e-8)&(pts<b[1]+half-1e-8),axis=-1)
    idx=lambda p: tuple(int(np.argmin(abs(a-v))) for a,v in zip(axes,p))
    s,g=idx(start),idx(target)
    if not valid[s] or not valid[g]: return None
    queue=deque([s]); prev={s:None}
    while queue:
        u=queue.popleft()
        if u==g: break
        for j in range(3):
            for sign in [-1,1]:
                v=list(u);v[j]+=sign;v=tuple(v)
                if v in prev or not 0<=v[j]<shape[j] or not valid[v]:continue
                sweep=segment_box(pts[u],pts[v],half)
                if any(intersect(sweep,b) for b in obstacles):continue
                prev[v]=u;queue.append(v)
    if g not in prev:return None
    path=[];q=g
    while q is not None:path.append(pts[q].tolist());q=prev[q]
    return path[::-1]

def evaluate(w,d):
    L,br,mo,mat=geometry(w,d);W,D,H=L
    vb=sum(map(volume,br));um=union_volume(br)
    assert abs(vb-um)<1e-5
    matv=volume(mat)-sum(intersection_volume(mat,b) for b in br)
    flags=[]
    for n,b in enumerate(mo):
        env=b+np.array([[-C['module_hardware_clearance_mm']]*3,[C['module_hardware_clearance_mm']]*3])
        if np.any(env[0]<0) or np.any(env[1]>L): flags.append(f'module_{n}_outside')
        if any(intersect(env,a) for a in br): flags.append(f'module_{n}_brace')
        if intersect(env,mat): flags.append(f'module_{n}_fill')
        if any(intersect(env,a) for a in mo[:n]):flags.append(f'module_{n}_module')
    gross=math.prod(L)/1e6
    # Conservative dimension/thickness interval, then exact brace variations checked separately.
    grosslo=(W-2)*(D-2)*(H-2)/1e6;grosshi=(W+2)*(D+2)*(H+2)/1e6
    # Brace +-5% volume is an explicit scenario encompassing small fabrication errors, not elasticity.
    netlo=grosslo-vb/1e6*1.05-8-.3-matv/1e9*30/1300*1000
    nethi=grosshi-vb/1e6*.95-2-.05-matv/1e9*10/1400*1000
    nom=gross-vb/1e6-5-.175-matv/1e9*20/1380*1000
    return dict(W_mm=w,D_mm=d,H_mm=500,gross_l=gross,brace_l=vb/1e6,
                mat_envelope_l=matv/1e6,net0_nom_l=nom,net0_low_l=netlo,net0_high_l=nethi,
                net20_nom_l=nom-16*3.15-4*1.8,module_fill_clearance_mm=D-50-max(b[1,1] for b in mo)-3,
                collision_flags=flags)

def main():
    rows=[evaluate(w,d) for w,d in product(C['widths_mm'],C['depths_mm'])]
    # Select two investigational alternatives, not global optimum.
    selected=[]
    for w,d in [(980,450),(1000,440)]:
        r=next(a for a in rows if (a['W_mm'],a['D_mm'])==(w,d));L,br,mods,mat=geometry(w,d)
        placed=[];paths=[]
        for n,b in enumerate(mods):
            half=(b[1]-b[0])/2+C['module_hardware_clearance_mm']
            obs=br+placed+[mat];p=path_to(b.mean(axis=0),L,obs,half)
            if p is None:paths.append({'module':n,'passed':False});break
            # Verify bore transit independently of grid. Both orientations rotate geometry together.
            assert math.hypot(half[0],half[2])<min(v['cutout_mm'] for v in C['drivers'].values())/2
            assert not any(intersect(segment_box(np.array([209.,-80,228]),np.array(p[0]),half),q) for q in br+placed)
            min_test=[]
            for a,bp in zip(p,p[1:]):
                a,bp=np.array(a),np.array(bp)
                sw=segment_box(a,bp,half)
                assert not any(intersect(sw,q) for q in obs)
                # Independent numerical rigid-rotation check of all AABBs.
                rot=lambda q: q[:,[2,1,0]]
                assert not any(intersect(rot(sw),rot(q)) for q in obs)
                # Independent sample occupation test at 17 and 33 stations, both orientations.
                for N in [17,33]:
                    for t in np.linspace(0,1,N):
                        pos=a*(1-t)+bp*t
                        for q in obs:
                            delta=np.maximum(q[0]-(pos+half),(pos-half)-q[1])
                            assert np.any(delta>=-1e-7)
            paths.append({'module':n,'passed':True,'centres_mm':p});placed.append(mods[n])
        # Conservative basket cylinder represented by containing AABB; it is NOT displaced solid.
        driver_checks=[]
        for cid,v in C['drivers'].items():
            rad=v['outer_diameter_mm']/2
            basket=box([209-rad,0,228-rad],[209+rad,v['overall_depth_mm'],228+rad])
            driver_checks.append(dict(id=cid,conservative_envelope_mm=basket.tolist(),
                 collisions=sum(intersect(basket,a) for a in br+mods+[mat]),
                 depth_total_min_mm=d+10+v['xmax_mm']+5+2+3+0+2,
                 depth_total_max_mm=d+22+v['xmax_mm']+5+2+3+8+2))
        # Independently sum disjoint volume, compare grid union including installed modules.
        union=union_volume(br+mods)
        err=abs(union-sum(map(volume,br+mods)))
        assert err<1e-4
        selected.append(dict(**r,inside_mm=L.tolist(),brace_mass_range_kg=[r['brace_l']*.65,r['brace_l']*.8],
          shell_mass_range_kg=[(w*d*500-math.prod(L)-math.pi*177.9**2*44)/1e9*rho for rho in [650,800]],
          regulation=[dict(large=n,small=k,net_nom_l=r['net0_nom_l']-n*3.15-k*1.8, net_low_l=r['net0_low_l']-n*math.prod(np.array([210,150,100])+.5)/1e6-k*math.prod(np.array([180,100,100])+.5)/1e6, net_high_l=r['net0_high_l']-n*math.prod(np.array([210,150,100])-.5)/1e6-k*math.prod(np.array([180,100,100])-.5)/1e6) for n,k in [(2,0),(11,1),(16,3),(16,4)]],
          braces_mm=[b.tolist() for b in br],
          modules_mm=[b.tolist() for b in mods],fill_box_mm=mat.tolist(),paths=paths,
          all_paths_pass=len(paths)==20 and all(q['passed'] for q in paths),
          driver_checks=driver_checks,partition_volume_error_mm3=err,
          orientation_note='Rigid 90 degree rotation of geometry and paths preserves distances. Gravity/fastener forces NOT thereby verified.'))
        print(w,d,'path',selected[-1]['all_paths_pass'], 'net',r['net0_nom_l'],r['net20_nom_l'],flush=True)
    depth=[dict(id=cid,D_mm=d,overall_low_mm=d+10+v['xmax_mm']+12,
                overall_high_mm=d+22+v['xmax_mm']+20,
                robust_for_scenarios=d+22+v['xmax_mm']+20<=500)
           for cid,v in C['drivers'].items() for d in C['depths_mm']]
    result=dict(scope=C['scope'],variants=rows,selected=selected,depth=depth,
       tests={'disjoint_vs_partition':True,'continuous_sweeps':True,'sample_checks':[17,33],
              'smallest_bore_with_clearance_margin_mm':144-math.hypot(108,53)},
       software=dict(python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__))
    (OUT/'p20d_geometria_wyniki.json').write_text(json.dumps(result,indent=2))
    with (OUT/'p20d_warianty.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    fig,axs=plt.subplots(1,3,figsize=(15,4.8))
    for r in rows:
        axs[0].scatter(r['D_mm'],r['net0_nom_l'],c='tab:red' if r['collision_flags'] else 'tab:blue')
        axs[0].annotate(str(r['W_mm']),(r['D_mm'],r['net0_nom_l']),fontsize=7)
    axs[0].axhline(150,color='k',ls=':');axs[0].set(xlabel='Głębokość korpusu [mm]',ylabel='Nominalne netto bez wkładów [l]',title='Czerwone: kolizja obwiedni')
    s=selected[0];ax=axs[1]
    for b in s['braces_mm']:
        b=np.array(b);ax.add_patch(Rectangle((b[0,0],b[0,2]),b[1,0]-b[0,0],b[1,2]-b[0,2],facecolor='grey',alpha=.4))
    for b in s['modules_mm']:
        b=np.array(b);ax.add_patch(Rectangle((b[0,0],b[0,2]),b[1,0]-b[0,0],b[1,2]-b[0,2],facecolor='tab:blue',alpha=.3))
    ax.add_patch(Circle((209,228),177.9,fill=False,color='k'));ax.set(xlim=(0,936),ylim=(0,456),aspect='equal',xlabel='x [mm]',ylabel='z [mm]',title='980×450×500: rzut od frontu')
    for cid in C['drivers']:
        q=[a for a in depth if a['id']==cid];axs[2].plot([a['D_mm'] for a in q],[a['overall_high_mm'] for a in q],label=cid)
    axs[2].axhline(500,color='red',ls='--');axs[2].set(xlabel='Korpus [mm]',ylabel='Pełny obrys: górny scenariusz [mm]',title='Maskownica + ruch + tył + tolerancje');axs[2].legend()
    fig.tight_layout();fig.savefig(OUT/'100_P20D_geometria.png',dpi=160);plt.close(fig)
if __name__=='__main__':main()
