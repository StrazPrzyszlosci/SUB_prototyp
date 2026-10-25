"""Analityczne stany styku i odrebna dyskretyzacja wirtualnego defektu."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from kontakt_brylowy_P19 import solve_hinges
from model_ramy_3D_P18C import Cabinet3D
from rozwarstwienie_spoiny_P19D import cut_front_bottom

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    K=np.array([[3.,-.4],[-.4,2.]]);D=np.array([[1.,-.3],[-.2,1.],[-1.,.3]])
    a=np.array([2.,4.,3.]);off=np.array([0.,0.,.2]);checks=[]
    for F in [np.array([2.,-1.]),np.array([1.,3.]),np.array([-3.,-2.])]:
        solutions=[]
        for bits in range(8):
            active=np.array([bool(bits&(1<<i)) for i in range(3)])
            q=np.linalg.solve(K+D.T@np.diag(a*active)@D,F-D.T@(a*active*off))
            if np.array_equal(D@q+off>0,active):solutions.append(q)
        assert len(solutions)==1
        q,J,active,meta=solve_hinges(sparse.csr_matrix(K),sparse.csr_matrix(D),a,off,F)
        error=float(max(abs(q-solutions[0])));assert error<1e-9
        checks.append(dict(error=error,residual=meta['residual']))
    bregman_error=0.
    for z in [-2.,-.1,0.,.1,2.]:
        for d in [-3.,-.1,0.,.1,3.]:
            zn=z+d
            if z>0 and zn>0:b=.5*d*d
            elif z<=0 and zn>0:b=.5*zn*zn
            elif z>0 and zn<=0:b=-.5*z*z-z*d
            else:b=0.
            exact=.5*(max(zn,0)**2-max(z,0)**2)-max(z,0)*d
            bregman_error=max(bregman_error,abs(b-exact));assert b>=0
    assert bregman_error<1e-13
    with (OUT/'p19d_wirtualne_rozwarstwienie.csv').open() as f:old=list(csv.DictReader(f))
    b=Cabinet3D(n=14);b.set_floor()
    gravity=-9.80665*(b.M@b.R[:,2]);rows=[]
    Kc,Dc,w,area,pieces=cut_front_bottom(b,.010)
    for label,F in [('GRAVITY',gravity),('GRAVITY_PLUS_STATIC_1KPA',gravity+1000*b.pressure)]:
        reference=spsolve(b.K+b.floor_K,F);q,J,active,meta=solve_hinges(Kc,Dc,w*b.bond_kn,np.zeros(len(w)),F)
        release=float(.5*F@(q-reference));previous=next(x for x in old if x['load']==label and float(x['crack_length_m'])==.01)
        oldG=float(previous['total_potential_release_j'])/float(previous['removed_area_m2']);G=release/area
        row=dict(load=label,mesh_n=14,dof=b.ndof,removed_area_m2=area,total_release_j=release,
                 average_0_to_10mm_release_j_m2=G,N10_average_0_to_10mm_release_j_m2=oldG,
                 relative_change=float(G/oldG-1),residual=meta['residual'])
        rows.append(row);print('P19D kontrola',row,flush=True)
    result=dict(status='INDEPENDENT_ACTIVE_SET_CHECKS_AND_FINITE_DEFECT_MESH_COMPARISON',
                independent_enumeration=checks,bregman_identity_max_error=bregman_error,mesh_comparisons=rows,
                scope='Porownanie skonczonego defektu;nie certyfikat pochodnej G ani materialowegoGc.',
                input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                              ['skrypty/sprawdz_styk_i_defekt_P19D.py','skrypty/kontakt_brylowy_P19.py',
                               'skrypty/rozwarstwienie_spoiny_P19D.py','skrypty/model_ramy_3D_P18C.py','skrypty/element_brylowy_P18C.py',
                               'wyniki/p19d_wirtualne_rozwarstwienie.csv']})
    (OUT/'p19d_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))


if __name__=='__main__':main()
