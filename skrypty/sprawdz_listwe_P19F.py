"""Niezależne momenty masy/ciśnienia i redukcja Schura nowej drogi sił."""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy import sparse
from scipy.linalg import cho_factor,cho_solve
from model_ramy_3D_P18C import Cabinet3D,skew
from model_listwy_naroznej_P19F import add_cleat
from analiza_listwy_stalego_frontu_P19F import solve_refined,joint_fields

ROOT=Path(__file__).resolve().parents[1]


def pressure_moments(b):
    tensor=b.pressure[:3*b.nnode].reshape(-1,3).T@b.xyz
    if b.with_basket:tensor+=np.outer(b.pressure[-6:-3],b.basket_reference)
    return tensor


def main():
    b=Cabinet3D(n=4);old_nodes=b.nnode;old_dof=b.ndof
    old_mass=b.mass_rigid.copy();old_moments=pressure_moments(b)
    add_cleat(b,section=.03,cross_intervals=2)
    W,D,H=b.inside;h=b.h;length=W-.02;size=.03;mass=730*length*size**2
    center=np.array([h+W/2,h+size/2,h+size/2])
    T=np.hstack([np.eye(3),-skew(center)])
    analytic=mass*T.T@T
    analytic[3:,3:]+=mass/12*np.diag([2*size**2,length**2+size**2,length**2+size**2])
    mass_error=float(np.linalg.norm(b.mass_rigid-old_mass-analytic)/np.linalg.norm(analytic))
    pressure_error=float(np.linalg.norm(pressure_moments(b)-old_moments+length*size**2*np.eye(3))/(length*size**2))
    assert mass_error<1e-10 and pressure_error<1e-9
    b.set_floor();K=b.K+b.floor_K
    F=(-9.80665*(b.M@b.R[:,2])+1000*b.pressure)[:,None]
    full,rf=solve_refined(K,F);full=full[:,0]
    old=np.r_[np.arange(3*old_nodes),np.arange(3*b.nnode,b.ndof)]
    new=np.arange(3*old_nodes,3*b.nnode)
    Koo=K[old][:,old].tocsr();Kcc=K[new][:,new].toarray();Koc=K[old][:,new].tocsr()
    factor=cho_factor(Kcc,lower=True)
    active=np.flatnonzero(np.asarray(abs(Koc).sum(axis=1)).ravel()>0)
    coupling=Koc[active].toarray()
    update=-(coupling@cho_solve(factor,coupling.T))
    rr=np.repeat(active,len(active));cc=np.tile(active,len(active))
    condensed=Koo+sparse.coo_matrix((update.ravel(),(rr,cc)),shape=Koo.shape).tocsr()
    rhs=F[old,0]-Koc@cho_solve(factor,F[new,0])
    qold,rc=solve_refined(condensed,rhs[:,None]);qold=qold[:,0]
    reconstructed=np.zeros(b.ndof);reconstructed[old]=qold
    reconstructed[new]=cho_solve(factor,F[new,0]-Koc.T@qold)
    qerror=float(np.linalg.norm(reconstructed-full)/np.linalg.norm(full))
    a={x['joint']:x for x in joint_fields(b,full)}
    z={x['joint']:x for x in joint_fields(b,reconstructed)}
    terr=max(abs(z[n]['tensile_spatial_rms_pa']/a[n]['tensile_spatial_rms_pa']-1)
             for n in ['front_bottom','front_cleat','bottom_cleat'])
    assert qerror<1e-6 and terr<1e-5
    record=dict(status='INDEPENDENT_RIGID_MASS_PRESSURE_MOMENTS_AND_SCHUR_CONTROL_NOT_PRODUCT_VALIDATION',
        coarse_dof=b.ndof,independent_rigid_mass_6x6_relative_error=mass_error,
        independent_pressure_affine_moment_relative_error=pressure_error,
        schur_eliminated_dof=len(new),coupled_old_dof=len(active),
        schur_vs_full_displacement_relative_error=qerror,schur_vs_full_joint_rms_relative_error=terr,
        full_residual=rf,condensed_residual=rc,
        input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in [
            'skrypty/sprawdz_listwe_P19F.py','skrypty/model_listwy_naroznej_P19F.py',
            'skrypty/model_ramy_3D_P18C.py','skrypty/element_brylowy_P18C.py',
            'skrypty/analiza_listwy_stalego_frontu_P19F.py']})
    (ROOT/'wyniki/p19f_kontrola_niezalezna.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in record.items() if k!='input_sha256'},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
