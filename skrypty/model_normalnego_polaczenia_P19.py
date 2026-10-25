"""P19A: panel+nakładkaMITC,normalna warstwa klej/MDF i ściąg osiowy.

Jawnie ograniczony submodel: brak ścinania spoiny,pękania,pełzania w czasie,
ortotropii3D i niejednorodnych naprężeń przez grubość. Normalna podatność
MDF jest parametremstresowym. Nie zastępuje pełnej kwalifikacji połączenia.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from model_plyty_MITC_P18 import RectangularPlate,PlateMaterial,shape


def wmap(plate,x,y):
    i=min(int(np.floor(x/plate.dx)),plate.nx-1);j=min(int(np.floor(y/plate.dy)),plate.ny-1)
    i=max(i,0);j=max(j,0);xi=2*(x-i*plate.dx)/plate.dx-1;eta=2*(y-j*plate.dy)/plate.dy-1
    N,_,_=shape(xi,eta,plate.dx,plate.dy);full=plate.dofs[j*plate.nx+i][0::3]
    # Każda lokalna waga jest przeniesiona na zredukowany układ.
    inverse=np.full(len(plate.full_F),-1,int);inverse[plate.free]=np.arange(len(plate.free));reduced=inverse[full]
    valid=reduced>=0
    return reduced[valid],N[valid]


def normal_joint(panel,pad_size_m,pad_thickness_m,pad_E_pa,glue_E_pa,glue_gap_m,Ez_factor,rod_E_pa,rod_area_m2,rod_length_m,
                 pad_mesh=8,eccentricity_m=0.,defect='NONE'):
    if min(pad_size_m,pad_thickness_m,pad_E_pa,glue_E_pa,glue_gap_m,Ez_factor,rod_E_pa,rod_area_m2,rod_length_m)<=0:raise ValueError('Dodatnie parametry')
    size=pad_size_m;origin=np.array([panel.a/2-size/2,panel.b/2-size/2])
    if min(origin)<0:raise ValueError('Nakładka poza panelem')
    pad=RectangularPlate(size,size,pad_mesh,pad_mesh,PlateMaterial(pad_E_pa,panel.material.nu,panel.material.density_kg_m3,pad_thickness_m),'FREE')
    # Równoważna normalna podatność warstwy i dwóch połówek grubościMDF.
    c_glue=glue_gap_m/glue_E_pa
    c_mdf=panel.material.thickness_m/(2*Ez_factor*panel.material.E_pa)+pad_thickness_m/(2*Ez_factor*pad_E_pa)
    kn=1/(c_glue+c_mdf)
    nmain=len(panel.F);n=nmain+len(pad.F)
    K=sparse.block_diag([panel.K,pad.K],format='csr');M=sparse.block_diag([panel.M,pad.M],format='csr')
    rows=[];cols=[];values=[];probe_rows=[];probe_cols=[];probe_values=[];qrows=[];qcols=[];qvalues=[];weights=[];positions=[]
    Fmain_patch=np.zeros(nmain)
    # Podział po liniach obu siatek zapewnia dokładność całki wielomianów.
    xs=np.r_[np.linspace(0,size,pad_mesh+1),np.arange(panel.nx+1)*panel.dx-origin[0]]
    ys=np.r_[np.linspace(0,size,pad_mesh+1),np.arange(panel.ny+1)*panel.dy-origin[1]]
    if defect=='EDGE_5MM':xs=np.r_[xs,.005]
    if defect=='CENTER_30PCT':
        hole=size*np.sqrt(.3);lo=(size-hole)/2;hi=(size+hole)/2;xs=np.r_[xs,lo,hi];ys=np.r_[ys,lo,hi]
    elif defect not in ['NONE','EDGE_5MM']:raise ValueError('Nieznany defekt')
    xs=np.unique(np.clip(xs,0,size));ys=np.unique(np.clip(ys,0,size));g=np.array([-1.,1.])/np.sqrt(3)
    pidx=0;qidx=0;area=0.
    for xl,xr in zip(xs[:-1],xs[1:]):
        if xr-xl<1e-12:continue
        for yl,yr in zip(ys[:-1],ys[1:]):
            if yr-yl<1e-12:continue
            midx=(xl+xr)/2;midy=(yl+yr)/2
            bonded=not (defect=='EDGE_5MM' and midx<.005)
            if defect=='CENTER_30PCT' and lo<midx<hi and lo<midy<hi:bonded=False
            for gx in g:
                for gy in g:
                    x=(xl+xr)/2+(xr-xl)*gx/2;y=(yl+yr)/2+(yr-yl)*gy/2;weight=(xr-xl)*(yr-yl)/4
                    im,vm=wmap(panel,x+origin[0],y+origin[1]);ip,vp=wmap(pad,x,y)
                    Fmain_patch[im]+=vm*weight
                    if not bonded:continue
                    ids=np.r_[im,nmain+ip];vector=np.r_[vm,-vp]
                    rows.extend(np.repeat(ids,len(ids)));cols.extend(np.tile(ids,len(ids)));values.extend((kn*weight*np.outer(vector,vector)).ravel())
                    qrows.extend([qidx]*len(ids));qcols.extend(ids);qvalues.extend(vector*kn)
                    weights.append(weight);positions.append([x-size/2,y-size/2]);qidx+=1;area+=weight
            if bonded:
                # Na każdym wielomianowym prostokącie maksimum|traction|jest w wierzchołku.
                for x,y in [(xl,yl),(xr,yl),(xr,yr),(xl,yr)]:
                    im,vm=wmap(panel,x+origin[0],y+origin[1]);ip,vp=wmap(pad,x,y)
                    ids=np.r_[im,nmain+ip];vec=np.r_[vm,-vp]
                    probe_rows.extend([pidx]*len(ids));probe_cols.extend(ids);probe_values.extend(vec*kn);pidx+=1
    Kfoundation=sparse.coo_matrix((values,(rows,cols)),shape=(n,n)).tocsr();K0=K+Kfoundation
    # Cavity pressure on exposed panel area and pad; the covered panel is not loaded twice.
    pressure_force=np.r_[panel.F-Fmain_patch,pad.F]
    # Rod footprint22x40mm approximated as distributed normal load; not a nodal point.
    bpad=pad.patch_average((size/2+eccentricity_m,size/2),(.04,.022));b=np.r_[np.zeros(nmain),bpad]
    krod=rod_E_pa*rod_area_m2/rod_length_m
    bs=sparse.csr_matrix(b[:,None]);Kclosed=K0+2*krod*(bs@bs.T)
    rod_mass=panel.material.density_kg_m3*rod_area_m2*rod_length_m
    Mclosed=M+rod_mass/6*(bs@bs.T)
    traction_probe=sparse.coo_matrix((probe_values,(probe_rows,probe_cols)),shape=(pidx,n)).tocsr()
    traction_quad=sparse.coo_matrix((qvalues,(qrows,qcols)),shape=(qidx,n)).tocsr()
    return dict(K0=K0,K=Kclosed,M=Mclosed,force=pressure_force,b=b,krod=krod,pad=pad,nmain=nmain,
        traction_probe=traction_probe,traction_quad=traction_quad,weights=np.array(weights),positions=np.array(positions),
        kn_n_m3=kn,c_glue_m_pa=c_glue,c_mdf_m_pa=c_mdf,bond_area_m2=area,
        pad_area_m2=size*size,pad_size_m=size,eccentricity_m=eccentricity_m)


def solve_joint(system):
    q=spsolve(system['K'],system['force']);q0=spsolve(system['K0'],system['force']);z=spsolve(system['K0'],system['b'])
    d=system['b']@q0;c=system['b']@z;k=system['krod']
    oracle=q0-z*(2*k*d/(1+2*k*c));difference=np.linalg.norm(q-oracle)/max(np.linalg.norm(q),1e-30)
    rod_force=2*k*(system['b']@q)
    traction=system['traction_quad']@q
    resultant=float(traction@system['weights']);expected=float(rod_force-system['pad_area_m2'])
    force_error=abs(resultant-expected)/max(abs(expected),abs(rod_force),1e-30)
    # Moment względem środka nakładki uwzględnia mimośród rozłożonej siły pręta.
    moment=float(traction@(system['weights']*system['positions'][:,0]))
    expected_moment=float(rod_force*system['eccentricity_m'])
    moment_error=abs(moment-expected_moment)/max(abs(rod_force)*system['pad_size_m'],1e-30)
    principal=float(max(abs(system['traction_probe']@q)))
    mainq=q[:system['nmain']];padq=q[system['nmain']:]
    return q,dict(tie_force_per_pa_n=float(rod_force),maximum_normal_traction_per_pa=float(principal),
        maximum_glue_opening_per_pa_m=float(principal*system['c_glue_m_pa']),
        maximum_MDF_normal_deformation_per_pa_m=float(principal*system['c_mdf_m_pa']),
        mean_contact_stress_per_pa=float(resultant/system['bond_area_m2']),
        maximum_to_mean_normal_stress_factor=float(principal/max(abs(resultant/system['bond_area_m2']),1e-30)),
        independent_Sherman_Morrison_relative_error=float(difference),force_balance_relative_error=float(force_error),
        moment_balance_relative_error=float(moment_error),pad_peak_principal_stress_per_pa=system['pad'].peak_principal_bound(padq),
        volume_compliance_m3_pa=float(system['force']@q),rod_end_compliance_without_rod_m_n=float(c))
