#!/usr/bin/env python3
"""P33A exploratory whole-enclosure energy mesh, NOT validated 3-D shell FEM.
Every panel is a displacement-only membrane+bending grillage; corner ties and
internal ring braces are elastic. Requires numpy, scipy, matplotlib.
Reproduce: python skrypty/p33a_global_shell_network.py --out wyniki/p33a
"""
import argparse, json, math, pathlib, time
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve, eigsh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

W,D,H=1.020,.425,.500
R=.3558/2; cx=.231; cz=.250
rho=730.; nu=.30

def sections(breaks,h):
    a=[breaks[0]]
    for x,y in zip(breaks[:-1],breaks[1:]):
        n=int(math.ceil((y-x)/h))
        a.extend(np.linspace(x,y,n+1)[1:])
    return np.array(a)

def model(mesh=.09,E=2.1e9,kjoint=1e8,kbrace=1e8,driver_kg=15.,insert_kg=8.,brace_on=True):
    xs=sections([0,.426,.701,W],mesh)
    ys=sections([0,D],mesh)
    zs=sections([0,H],mesh)
    definitions=[('top','xy',xs,ys,H,.022),('bottom','xy',xs,ys,0.,.022),
        ('front','xz',xs,zs,0.,.044),('back','xz',xs,zs,D,.022),
        ('left','yz',ys,zs,0.,.022),('right','yz',ys,zs,W,.022)]
    nodes=[]; faces={}; masses=[]; labels=[]
    def new(point,label):
        idx=len(nodes);nodes.append(point);masses.append(0.);labels.append(label);return idx
    for name,typ,u,v,const,t in definitions:
        table={};valid={}
        for i,x in enumerate(u):
            for j,y in enumerate(v):
                pt=(x,y,const) if typ=='xy' else ((x,const,y) if typ=='xz' else (const,x,y))
                active=True  # front cut-cells carry fractional material; nodes with zero assembled mass are eliminated
                if active:table[i,j]=new(pt,name)
                valid[i,j]=active
        faces[name]=dict(grid=table,valid=valid,u=u,v=v,typ=typ,t=t)
    # Braces have independent displacement DOFs, coupled to panel nodes by elastic shear/normal attachments.
    braces=[]
    if brace_on:
        for xx in [.426,.701]:
            for kind,vals,fix,face,A in [
                ('top',ys,H,'top',.022*.022),('bottom',ys,0.,'bottom',.022*.022),
                ('front',zs,0.,'front',.022*.010),('back',zs,D,'back',.022*.022)]:
                strand=[]
                for v in vals:
                    pt=(xx,v,fix) if kind in ('top','bottom') else (xx,fix,v)
                    idx=new(pt,'brace_'+kind)
                    strand.append(idx)
                braces.append((strand,A,kind,xx,face))
    n=len(nodes);coord=np.asarray(nodes);masses=np.asarray(masses)
    rows=[];cols=[];vals=[];spring_count=0
    def add_energy(parts,k):
        nonlocal spring_count
        if not math.isfinite(k) or k<=0:raise ValueError(('bad stiffness',k))
        spring_count+=1
        dofs,cs=zip(*parts)
        for a,va in zip(dofs,cs):
            for b,vb in zip(dofs,cs):
                rows.append(a);cols.append(b);vals.append(k*va*vb)
    def unit(axis):return tuple(float(i==axis) for i in range(3))
    def grad_pair(i,j,d,k):
        for ax in range(3):
            if d[ax]:add_energy([(3*i+ax,-float(d[ax])),(3*j+ax,float(d[ax]))],k)
    F=np.zeros(3*n);surface_area={};front_cells=0.;front_removed=0.
    face_edges=[]
    for name,face in faces.items():
        u,v=face['u'],face['v'];gr=face['grid'];typ=face['typ'];t=face['t']
        ax1,ax2,normal= ('x','y',2) if typ=='xy' else (('x','z',1) if typ=='xz' else ('y','z',0))
        ax_u={'x':0,'y':1,'z':2}[ax1];ax_v={'x':0,'y':1,'z':2}[ax2]
        Dflex=E*t**3/(12*(1-nu**2))
        surface_area[name]=0
        for i in range(len(u)-1):
          for j in range(len(v)-1):
            ids=[gr.get((i,j)),gr.get((i+1,j)),gr.get((i+1,j+1)),gr.get((i,j+1))]
            area=(u[i+1]-u[i])*(v[j+1]-v[j]); midU=(u[i]+u[i+1])/2;midV=(v[j]+v[j+1])/2
            if name=='front':
                # sub-cell integration 10x10 for the circular aperture.
                cuts=[((u[i]+(aa+.5)*(u[i+1]-u[i])/10-cx)**2 +
                       (v[j]+(bb+.5)*(v[j+1]-v[j])/10-cz)**2)>=R*R
                      for aa in range(10) for bb in range(10)]
                fraction=sum(cuts)/100
                front_removed+=area*(1-fraction)
            else:fraction=1.0
            if fraction==0:continue
            area_mat=area*fraction
            surface_area[name]+=area_mat
            # Uniform comparison pressure, not the real coupled acoustic field.
            normalSign={'top':1,'bottom':-1,'front':-1,'back':1,'left':-1,'right':1}[name]
            for q in ids:
                masses[q]+=rho*t*area_mat/4
                F[3*q+normal]+=1000*area_mat*normalSign/4
            # Cell edges, half assigned to each of the two adjacent cells.
            for p,q,axis,L,perp in [(ids[0],ids[1],ax_u,u[i+1]-u[i],v[j+1]-v[j]),
                                   (ids[3],ids[2],ax_u,u[i+1]-u[i],v[j+1]-v[j]),
                                   (ids[0],ids[3],ax_v,v[j+1]-v[j],u[i+1]-u[i]),
                                   (ids[1],ids[2],ax_v,v[j+1]-v[j],u[i+1]-u[i])]:
                grad_pair(p,q,unit(axis),E*t*perp/L*.5*fraction)
            for p,q in [(ids[0],ids[2]),(ids[1],ids[3])]:
                vec=coord[q]-coord[p];length=np.linalg.norm(vec);vdir=vec/length
                grad_pair(p,q,vdir, .11*E*t*area_mat/(length**2))
            mixed=[(3*ids[0]+normal,1),(3*ids[1]+normal,-1),
                   (3*ids[2]+normal,1),(3*ids[3]+normal,-1)]
            add_energy(mixed,2*Dflex*(1-nu)/area*fraction)
        # Discrete bending curvatures, including nonuniform x partitions.
        for direction in [0,1]:
          A=u if direction==0 else v;B=v if direction==0 else u
          for i in range(1,len(A)-1):
            L=A[i]-A[i-1];Rr=A[i+1]-A[i];avg=(L+Rr)/2
            q0,q1,q2= 1/(L*avg),-(1/L+1/Rr)/avg,1/(Rr*avg)
            for j in range(len(B)):
                trip=[gr.get((i-1,j)),gr.get((i,j)),gr.get((i+1,j))] if direction==0 else [gr.get((j,i-1)),gr.get((j,i)),gr.get((j,i+1))]
                if any(q is None for q in trip):continue
                if name=='front':
                    pts=coord[trip][:,[0,2]]
                    if min(np.linalg.norm(pts-(cx,cz),axis=1))<R:continue
                width=(B[min(j+1,len(B)-1)]-B[max(j-1,0)])/ (1 if j in (0,len(B)-1) else 2)
                if width<=0:continue
                add_energy([(3*trip[z]+normal,c) for z,c in enumerate((q0,q1,q2))],Dflex*width*avg)
    # Face-specific nodes: translational elastic ties along cabinet edges.
    from collections import defaultdict
    groups=defaultdict(list)
    for idx,p in enumerate(coord):
        if labels[idx].startswith('brace'):continue
        if sum(abs(p[k]-b)<1e-8 for k,b in enumerate((W,D,H)))+sum(abs(p[k])<1e-8 for k in range(3))<2:continue
        groups[tuple(round(x,6) for x in p)].append(idx)
    tie_count=0
    for pt,ids in groups.items():
        if len(ids)<2:continue
        for q in ids[1:]:
            for ax in range(3):add_energy([(3*ids[0]+ax,1),(3*q+ax,-1)],kjoint*mesh)
            tie_count+=1
    # Two internal brace rings, represented by axial/bending beams.
    for strand,A,kind,xx,face in braces:
        for q,p in zip(strand[:-1],strand[1:]):
            vec=coord[p]-coord[q];L=np.linalg.norm(vec);vdir=vec/L
            grad_pair(q,p,vdir,E*A/L)
            masses[q]+=rho*A*L/2;masses[p]+=rho*A*L/2
        I=A*.022**2/12
        for s in range(1,len(strand)-1):
            q,p,r=strand[s-1:s+2];L=np.linalg.norm(coord[q]-coord[p]);RR=np.linalg.norm(coord[r]-coord[p]);av=(L+RR)/2
            c0,c1,c2=1/(L*av),-(1/L+1/RR)/av,1/(RR*av)
            vec=coord[r]-coord[q];axis=np.argmax(np.abs(vec))
            for normal in range(3):
                if normal!=axis:add_energy([(3*q+normal,c0),(3*p+normal,c1),(3*r+normal,c2)],E*I*av)
        for q in strand:
            pt=coord[q];other=faces[face]['grid']
            cand=min(other.values(),key=lambda z:np.linalg.norm(pt-coord[z]));gap=np.linalg.norm(pt-coord[cand])
            if gap>1e-7:raise RuntimeError('brace node lacks matching face mesh')
            for ax in range(3):add_energy([(3*q+ax,1),(3*cand+ax,-1)],kbrace*mesh)
    front=faces['front']['grid']
    rim=[q for q in front.values() if abs(np.linalg.norm(coord[q][[0,2]]-np.array([cx,cz]))-R)<mesh*.85]
    if len(rim)<6:raise RuntimeError('too few front mounting nodes')
    for q in rim:masses[q]+=driver_kg/len(rim)
    # Assumed cone load path: deliberately illustrative, not a driver/mechanical impedance model.
    for q in rim:F[3*q+1]-=1000*math.pi*R*R/len(rim)
    back=faces['back']['grid'];targets=[q for q in back.values() if coord[q][0]>.45*W]
    for q in targets:masses[q]+=insert_kg/len(targets)
    contacts=[q for q in faces['bottom']['grid'].values()
              if (abs(coord[q][0])<1e-8 or abs(coord[q][0]-W)<1e-8)
              and (abs(coord[q][1])<1e-8 or abs(coord[q][1]-D)<1e-8)]
    for q in contacts:
        for ax in range(3):add_energy([(3*q+ax,1)],1.5e6)
    active=np.flatnonzero(masses>0)
    dofs=np.concatenate([3*active+i for i in range(3)]).reshape(3,-1).T.ravel()
    K=coo_matrix((vals,(rows,cols)),shape=(3*n,3*n)).tocsr()[dofs,:][:,dofs].tocsr()
    m=np.repeat(masses[active],3)
    A=K.tocsc();M=diags(m,format='csc')
    load=F[dofs];static=spsolve(A,load)
    energy=float(static@(K@static));input_work=float(static@load)
    if not np.isfinite(energy) or abs(energy-input_work)/max(1,abs(energy))>1e-8:
        raise RuntimeError('energy check')
    ev,vec=eigsh(K,k=min(18,len(m)-2),M=M,sigma=0,which='LM',tol=8e-6,maxiter=4000)
    freqs=np.sqrt(np.maximum(0,ev))/(2*np.pi)
    modeinds=np.argsort(freqs);freqs=freqs[modeinds];vec=vec[:,modeinds]
    normaldisp=np.zeros(len(active));positions=coord[active]
    for z,q in enumerate(active):
        nm=labels[q]
        ax={'top':2,'bottom':2,'front':1,'back':1,'left':0,'right':0}.get(nm)
        if ax is not None:normaldisp[z]=static[3*z+ax]
    return dict(mesh=mesh,n_nodes=len(active),ndof=len(m),elements=spring_count,
        face_area_m2=surface_area,front_removed_m2=front_removed,
        front_hole_area_analytic_m2=math.pi*R**2,braces=brace_on,
        driver_kg=driver_kg,insert_kg=insert_kg,
        Ejoint_N_m2=kjoint,Ebrace_N_m2=kbrace,
        face_joint_ties=tie_count,front_rim_nodes=len(rim),
        MDF_mass_kg=float(np.sum(masses[active])-driver_kg-insert_kg),
        mass_total_kg=float(np.sum(masses[active])),
        f_modes_Hz=[float(x) for x in freqs],
        freq_gt_50_Hz=[float(x) for x in freqs if x>50][:9],
        energy_J=float(energy),load_N_norm=float(np.linalg.norm(load)),
        max_static_normal_um=float(np.max(np.abs(normaldisp))*1e6),
        rms_static_normal_um=float(np.sqrt(np.mean(normaldisp**2))*1e6),
        static_volume_compliance_l_per_kPa=float(input_work/1000)*1000,
        coords=positions,displacements=static.reshape(-1,3),normal=normaldisp,
        labels=[labels[q] for q in active],
        modal_shape=vec[:,8] if vec.shape[1]>8 else vec[:,0])

def safe(s):
    return {k:v for k,v in s.items()
            if not isinstance(v,(np.ndarray,list)) or k in ['f_modes_Hz','freq_gt_50_Hz']}

def plot(out,folder):
    folder.mkdir(parents=True,exist_ok=True)
    fig=plt.figure(figsize=(12,7));ax=fig.add_subplot(111,projection='3d')
    for tag in ['front','top','bottom','left','right','back']:
        m=np.asarray([a==tag for a in out['labels']]);p=out['coords'][m];d=out['displacements'][m]
        if len(p):
            norm=np.linalg.norm(d,axis=1)
            sc=ax.scatter(p[:,0]*1000,p[:,1]*1000,p[:,2]*1000,
               c=norm*1e6,cmap='inferno',s=19,alpha=.85,vmin=0,vmax=200)
    ax.set(xlabel='szerokość X [mm]',ylabel='głębokość Y [mm]',
           zlabel='wysokość Z [mm]',
           title='P33A · ugięcia zespołu przy umownym nacisku 1000 Pa (µm)')
    ax.set_box_aspect((1020,425,500))
    fig.colorbar(sc,ax=ax,shrink=.65,label='amplituda przemieszczenia [µm]')
    fig.tight_layout()
    fig.savefig(folder/'p33a_globalne_ugiecia.png',dpi=150)
    plt.close(fig)

def run(folder):
    folder=pathlib.Path(folder);folder.mkdir(parents=True,exist_ok=True)
    scenarios=[];nominal=None
    for h in [.14,.105,.08]:
        for joint in [3e6,3e7,3e8]:
            start=time.monotonic()
            x=model(mesh=h,kjoint=joint,kbrace=joint,driver_kg=15.,insert_kg=8.)
            if h==.08 and joint==3e7:nominal=x
            row=safe(x);row['seconds']=round(time.monotonic()-start,3)
            scenarios.append(row)
            print(f"mesh={h} k={joint:.1e} DOF={x['ndof']} freq>50={x['freq_gt_50_Hz'][:3]} disp={x['max_static_normal_um']:.3f} time={row['seconds']}s",flush=True)
    for driver,insert in [(0.,0.),(12.,0.),(18.,0.),(15.,14.)]:
        x=model(mesh=.105,kjoint=3e7,kbrace=3e7,driver_kg=driver,insert_kg=insert)
        y=safe(x);y['sensitivity_case']=True;scenarios.append(y)
    x=model(mesh=.105,kjoint=3e7,kbrace=3e7,brace_on=False)
    y=safe(x);y['sensitivity_case']=True;scenarios.append(y)
    if nominal:plot(nominal,folder)
    fig,axs=plt.subplots(1,2,figsize=(11,4.5))
    for k in [3e6,3e7,3e8]:
        s=sorted([r for r in scenarios if 'sensitivity_case' not in r and r['Ejoint_N_m2']==k],
                 key=lambda r:r['mesh'],reverse=True)
        axs[0].plot([r['mesh']*1000 for r in s],
                    [r['max_static_normal_um'] for r in s],marker='o',label=f'k={k:.0e} N/m²')
        axs[1].plot([r['mesh']*1000 for r in s],
                    [r['freq_gt_50_Hz'][0] if r['freq_gt_50_Hz'] else np.nan for r in s],
                    marker='o',label=f'k={k:.0e} N/m²')
    axs[0].set(xlabel='docelowy krok siatki [mm]',ylabel='maks. ugięcie [µm]',
               title='Wpływ siatki na odpowiedź statyczną')
    axs[1].set(xlabel='docelowy krok siatki [mm]',ylabel='pierwsza f >50 Hz',
               title='Przykładowa wrażliwość częstości')
    for ax in axs:ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(folder/'p33a_siatka_i_spoiny.png',dpi=160)
    plt.close(fig)
    raw={'study':'P33A','date':'2026-10-31',
        'status':'EXPLORATORY whole-shell elastic grillage, NOT validated 3D continuum/shell FEM',
        'geometry_mm':{'external':[1020,425,500],'panel_mm':22,'front_mm':44,
            'driver_aperture_mm':355.8,'driver_center_xz_mm':[231,250],
            'ring_x_mm':[426,701]},
        'cases':len(scenarios),'scenarios':scenarios,
        'limitations':[
            'Simplified 3-DOF/node energy grillage with discrete curvatures, not a C3D8/MITC shell FEM.',
            'Elastic corner ties omit rotations and local adhesive peel and failure.',
            'Two ring braces represented by slender bars; local U brace omitted.',
            'Front aperture uses 10x10 cut-cell quadrature and approximate rim curvature.',
            'Driver mass 0/12/15/18 kg and inserts 0/8/14 kg hypothetical.',
            'Foot-to-ground springs arbitrary 1.5 MN/m, not calibrated.',
            'E=2.1GPa MDF, density 730kg/m3, isotropic, no moisture/creep.',
            'Uniform 1000Pa pressure and hypothetical load transfer through driver basket.',
            'No validated physical acoustic radiation, joint strength, fatigue or CNC release.']}
    with open(folder/'p33a_global_shell_results.json','w') as f:
        json.dump(raw,f,ensure_ascii=False,indent=2)
    return raw

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',default='wyniki/p33a')
    args=ap.parse_args()
    run(args.out)
