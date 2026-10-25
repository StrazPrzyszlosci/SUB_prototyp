"""Niezależne odniesienia P18B: element, annulus, siły, energia i zbieżność."""
import json
import hashlib
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from model_frontu_z_otworem_P18B import PlateMaterial,element,FrontWithHole,MountedFront,operators,axisymmetric_kirchhoff
from model_plyty_MITC_P18 import element_matrices

ROOT=Path(__file__).resolve().parents[1]


def main():
    material=PlateMaterial(2.1e9,.3,730,.022)
    xy=np.array([[0.,0],[.2,0],[.2,.3],[0,.3]])
    K,M,F=element(xy,material);k0,m0,f0=element_matrices(.2,.3,material)
    rectangle_error=float(np.linalg.norm(K-k0)/np.linalg.norm(k0));assert rectangle_error<1e-13
    assert np.allclose(M,m0,rtol=1e-13,atol=1e-16) and np.allclose(F,f0,rtol=1e-13)
    angle=.421;R=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    kr,_,_=element(xy@R.T,material);T=np.kron(np.eye(4),np.block([[np.ones((1,1)),np.zeros((1,2))],[np.zeros((2,1)),R]]))
    rotation_error=float(np.linalg.norm(T.T@kr@T-K)/np.linalg.norm(K));assert rotation_error<1e-13
    irregular=np.array([[0,0],[.24,.02],[.19,.29],[-.03,.23]])
    ki,mi,fi=element(irregular,material);rigid=[]
    for mode in [np.tile([1.,0,0],4),np.ravel(np.column_stack([irregular[:,0],np.ones(4),np.zeros(4)])),np.ravel(np.column_stack([irregular[:,1],np.zeros(4),np.ones(4)]))]:
        err=float(np.linalg.norm(ki@mode)/(np.linalg.norm(ki)*np.linalg.norm(mode)));rigid.append(err);assert err<1e-13
    values=np.linalg.eigvalsh(ki);assert np.count_nonzero(values>max(values)*1e-10)==9
    curvature=np.array([.3,-.2,.15])
    x,y=irregular.T
    field=np.ravel(np.column_stack([.5*curvature[0]*x*x+.5*curvature[1]*y*y+.5*curvature[2]*x*y,
                                    curvature[0]*x+.5*curvature[2]*y,curvature[1]*y+.5*curvature[2]*x]))
    bending_errors=[]
    for xi,eta in [(-.6,-.3),(.2,.7),(.6,-.7)]:
        _,Bb,_,_=operators(irregular,xi,eta)
        err=float(max(abs(Bb@field-curvature)));bending_errors.append(err);assert err<1e-13
    annulus=[]
    for boundary in ['CCCC','SSSS_HARD']:
        thin=PlateMaterial(2.1e9,.3,730,.001)
        for n in [8,16,32]:
            plate=FrontWithHole(.46,.46,.15,thin,n,n//2,boundary,True)
            Kp,Mp,Fp,Tp=plate.continuous_inner()
            for p,fc in [(1.,np.pi*.15**2),(0.,1.)]:
                load=Fp*p;load[-3]+=fc
                q=spsolve(Kp,load);ref=axisymmetric_kirchhoff(.15,.23,thin.rigidity_nm,.3,p,fc,boundary)
                err=float(q[-3]/ref['inner_displacement_m']-1)
                annulus.append(dict(boundary=boundary,angular_per_side=n,radial=n//2,pressure_pa=p,cap_force_n=fc,
                                    displacement_m=float(q[-3]),kirchhoff_m=ref['inner_displacement_m'],relative_error=err))
        for p in [0.,1.]:
            sequence=[r for r in annulus if r['boundary']==boundary and r['pressure_pa']==p]
            assert abs(sequence[-1]['relative_error'])<.01
            assert abs(sequence[-1]['relative_error'])<abs(sequence[0]['relative_error'])
    # Granica małego sztywnego centrum wraca do środka pełnego dysku Kirchhoffa.
    D=thin.rigidity_nm;ref=axisymmetric_kirchhoff(1e-6,.23,D,.3,1,np.pi*1e-12)
    full_disk=.23**4/(64*D);disk_error=float(ref['inner_displacement_m']/full_disk-1);assert abs(disk_error)<1e-7
    real_mesh=[];states=[]
    for n,nr in [(12,8),(20,12),(28,16)]:
        p=FrontWithHole(.46,.46,.1526,material,n,nr)
        system=p.mounted(.1621,8,7.68,.1,1e7)
        load=system.load(pressure_pa=1000,pressure_cap=True,basket_force_n=100)
        q=system.static(load);qr,force=system.independent_static(load)
        independent=float(max(abs(q-qr))/max(abs(q)));assert independent<1e-8
        assert np.allclose(system.G.T@force,load[-3:],rtol=1e-8,atol=1e-8)
        real_mesh.append(dict(angular_per_side=n,radial=nr,basket_m=float(q[-3]),
                             maximum_joint_n=float(max(abs(force))),first_hz=float(system.modes(3)[0][0]),
                             independent_error=independent,hole_area_error=float(p.hole_polygon_area_m2/(np.pi*p.r*p.r)-1)))
        assert abs(p.actual_solid_area_m2+p.hole_polygon_area_m2-.46**2)<1e-12
        if n==20:states=[p,system]
    convergence={key:abs(real_mesh[-1][key]/real_mesh[-2][key]-1) for key in ['basket_m','maximum_joint_n','first_hz']}
    assert max(convergence.values())<.03
    p,system=states;F1=system.load(basket_force_n=1);F2=system.load(moment_x_nm=1)
    q1=system.static(F1);q2=system.static(F2)
    reciprocity=float(abs(F1@q2-F2@q1)/np.sqrt((F1@q1)*(F2@q2)));assert reciprocity<1e-10
    # Zwiększamy wyłącznie kwadraturę skończonego dysku,nie siatkę lub promień.
    B=np.stack([p.disk_patch(x,y,.004,8,32) for x,y in system.positions],axis=1)
    DD=sparse.csr_matrix(np.column_stack([B.T,-system.G]))
    KK=sparse.block_diag([p.K,sparse.csr_matrix((3,3))],format='csr')+system.k*(DD.T@DD)
    alternative=MountedFront(p,KK,system.M,B,system.G,DD,system.k,system.mass,system.positions)
    load=system.load(pressure_pa=1000,pressure_cap=True,basket_force_n=100)
    qa=alternative.static(load);qb=system.static(load)
    patch_change=float(abs(qa[-3]/qb[-3]-1));assert patch_change<.01
    coupled=[]
    for f in [20.,40.,80.,200.]:
        q,row=system.prescribed_cone(f,.001,.25,.0458)
        coupled.append(row);assert row['relative_power_residual']<1e-8
        assert row['source_power_w']>=0 and row['gas_power_w']>=0
    bad=0
    for kwargs in [dict(hole_radius_m=0),dict(hole_radius_m=.24)]:
        try:FrontWithHole(.46,.46,kwargs['hole_radius_m'],material)
        except ValueError:bad+=1
    assert bad==2
    result=dict(status='CONTROLS_WITHIN_SCOPED_LINEAR_MODEL_NOT_PHYSICAL_VALIDATION',
                rectangle_relative_error=rectangle_error,rotation_relative_error=rotation_error,rigid_errors=rigid,
                constant_curvature_errors=bending_errors,patch_quadrature_basket_relative_change=patch_change,
                annulus=annulus,small_inner_disk_error=disk_error,real_geometry_mesh=real_mesh,
                last_mesh_relative_changes=convergence,reciprocity_error=reciprocity,coupled_energy=coupled,
                limitations=['Kirchhoff reference is thin-limit only;1mm plate,not22mm validation against3D.',
                             'Finite patch is regularized;stress of screw holes/contact3D not provided.',
                             'Damping,gasket stiffness and payload inertias are hypotheses.'])
    result['input_sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
                           ['skrypty/model_frontu_z_otworem_P18B.py','skrypty/model_plyty_MITC_P18.py','skrypty/sprawdz_front_z_otworem_P18B.py']}
    (ROOT/'wyniki/p18b_weryfikacja.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print('P18B kontrole:',rectangle_error,rotation_error,'ostatnia siatka:',convergence)


if __name__=='__main__':main()
