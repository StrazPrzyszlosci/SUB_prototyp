"""Odniesienia3D:staly strain,pure bending,masa,spoiny i zamkniecie cisnienia."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import spsolve
from element_brylowy_P18C import *
from model_ramy_3D_P18C import *

ROOT=Path(__file__).resolve().parents[1]


def traction_load(panel,tensor_function,faces=None):
    F=np.zeros(panel.ndof);center=panel.xyz.mean(axis=0)
    for face in panel.boundary if faces is None else faces:
        xyz=panel.xyz[face];qcenter=xyz.mean(axis=0)
        for N,point,w in quad_quadrature(xyz):
            xi=N@SIGNS[:4,0];eta=N@SIGNS[:4,1]
            _,der=quad_shape(xi,eta);t=der@xyz;n=np.cross(t[0],t[1]);n/=np.linalg.norm(n)
            if np.dot(n,qcenter-center)<0:n=-n
            np.add.at(F,(3*face[:,None]+np.arange(3)).ravel(),np.outer(N,tensor_function(point)@n).ravel()*w)
    return F


def main():
    E=2.1e9;nu=.3;D=isotropic_D(E,nu);rho=730.;patch=[]
    for distorted in [False,True]:
        xyz=(SIGNS+1)/2*np.array([.2,.3,.04])
        if distorted:xyz[:,0]+=.5*xyz[:,2]+.2*xyz[:,1]*xyz[:,2];xyz[6]+=[.025,.013,.005]
        K,M,meta=hex8(xyz,D,rho);A=np.array([[.001,.002,-.001],[.0003,-.0006,.0004],[.0002,.0001,.0005]])
        q=(xyz@A.T).ravel();strain=np.r_[np.diag(A),A[0,1]+A[1,0],A[1,2]+A[2,1],A[0,2]+A[2,0]];stress=D@strain
        tensor=np.array([[stress[0],stress[3],stress[5]],[stress[3],stress[1],stress[4]],[stress[5],stress[4],stress[2]]])
        p=Panel('patch',xyz,np.array([np.arange(8)]),D,rho)
        force=traction_load(p,lambda _:tensor);err=float(np.linalg.norm(K@q-force)/np.linalg.norm(force));assert err<1e-10
        rec=meta['recovery']@q;assert np.linalg.norm(rec)<1e-10
        s=gauss_stress(xyz,D,q,meta);serr=float(np.linalg.norm(s-stress)/np.linalg.norm(np.tile(stress,(8,1))));assert serr<1e-10
        eigen=np.linalg.eigvalsh(K);assert np.count_nonzero(eigen>max(eigen)*1e-10)==18
        patch.append(dict(distorted=distorted,force_relative_error=err,stress_relative_error=serr))
    beam=[]
    for n in [4,8]:
        for enhanced in [False,True]:
            L=1.;b=.1;h=.02;kappa=.001
            p=block_panel('beam',[np.linspace(0,L,n+1),np.linspace(-b/2,b/2,3),np.linspace(-h/2,h/2,3)],D,rho,enhanced)
            F=traction_load(p,lambda point:np.diag([-E*kappa*point[2],0,0]))
            x,y,z=p.xyz.T;exact=np.column_stack([-kappa*x*z,nu*kappa*y*z,kappa*x*x/2-nu*kappa*y*y/2+nu*kappa*z*z/2]).ravel()
            R=np.zeros((p.ndof,6))
            for i,r in enumerate(p.xyz):R[3*i:3*i+3,:3]=np.eye(3);R[3*i:3*i+3,3:]=-skew(r)
            from scipy.linalg import qr
            _,_,pivot=qr(R.T,pivoting=True,mode='economic');fixed=pivot[:6];free=np.setdiff1d(np.arange(p.ndof),fixed)
            q=np.zeros(p.ndof);q[fixed]=exact[fixed];q[free]=spsolve(p.K[free][:,free],(F-p.K@q)[free])
            analytic=E*kappa*kappa*(b*h**3/12)*L;ratio=float(F@q/analytic)
            if enhanced:assert abs(ratio-1)<1e-8
            beam.append(dict(n_length=n,enhanced=enhanced,computed_work_j=float(F@q),exact_work_j=analytic,compliance_ratio=ratio))
    # Odrębny patch transmisji spoiny:stale sigma/ tau i znany skokCtraction.
    D0=isotropic_D(E,0.);axes=[np.linspace(0,.1,3),np.linspace(0,.05,3),np.linspace(0,.05,3)]
    p1=block_panel('one',axes,D0,rho);p2=block_panel('two',[axes[0]+.1,*axes[1:]],D0,rho)
    p2.offset=len(p1.xyz);K=sparse.block_diag([p1.K,p2.K],format='csr');kn=1e9;ks=4e8
    sigma=100.;tau=70.;tensor=np.array([[sigma,tau,0],[tau,0,0],[0,0,0.]])
    for f1 in p1.faces(0,.1):
        center=p1.xyz[f1].mean(axis=0)
        f2=min(p2.faces(0,.1),key=lambda ids:np.linalg.norm(p2.xyz[ids].mean(axis=0)-center))
        L=np.zeros((8,8));area=0.
        for N,point,w in quad_quadrature(p1.xyz[f1]):
            N2=inverse_quad(p2.xyz[f2][:,[1,2]],point[[1,2]]);d=np.r_[N,-N2];L+=w*np.outer(d,d);area+=w
        piece=BondPiece('patch',np.r_[f1,p2.offset+f2],L,area,0,kn,ks);K+=piece.matrix(K.shape[0])
    F=np.r_[traction_load(p1,lambda _:tensor,np.array([f for f in p1.boundary if not np.allclose(p1.xyz[f,0],.1)])),
            traction_load(p2,lambda _:tensor,np.array([f for f in p2.boundary if not np.allclose(p2.xyz[f,0],.1)]))]
    fields=[]
    for i,p in enumerate([p1,p2]):
        q=np.zeros_like(p.xyz);q[:,0]=sigma/E*p.xyz[:,0]+i*sigma/kn;q[:,1]=tau/(E/2)*p.xyz[:,0]+i*tau/ks;fields.append(q.ravel())
    q=np.r_[*fields];joint_patch=float(np.linalg.norm(K@q-F)/np.linalg.norm(F));assert joint_patch<1e-9
    exact=(sigma*sigma/E+tau*tau/(E/2))*.2*.05**2+(sigma*sigma/kn+tau*tau/ks)*.05**2
    joint_work=float(F@q/exact-1);assert abs(joint_work)<1e-9
    b=Cabinet3D(n=4);W,Dp,H=b.inside;h=b.h;A=b.byname['front'].mesh2d.hole_polygon_area_m2
    expected_volume=(W+2*h)*(Dp+2*h)*(H+2*h)-W*Dp*H-A*h
    volume_error=float(sum(p.volume for p in b.panels)/expected_volume-1);assert abs(volume_error)<1e-10
    mass=730*expected_volume+b.basket_mass;assert np.allclose(b.mass_rigid[:3,:3],mass*np.eye(3),rtol=1e-10,atol=1e-9)
    pressure_balance=np.asarray(b.R.T@b.pressure);assert np.linalg.norm(pressure_balance)<1e-10
    dilation=np.r_[b.xyz.ravel(),b.basket_reference,np.zeros(3)]
    expected_air=W*Dp*H+A*h;volume_port_error=float((b.pressure@dilation)/(3*expected_air)-1);assert abs(volume_port_error)<1e-10
    rigid_error=float(np.linalg.norm(b.K@b.R)/np.linalg.norm(b.K.data));assert rigid_error<1e-12
    q,F,acc=b.balanced_static(b.pressure)
    statres=float(np.linalg.norm(b.K@q-F)/np.linalg.norm(F));assert statres<1e-7
    Fbody=np.zeros(b.ndof);Fbody[-5]=1.;qu,relief,accu=b.balanced_static(Fbody)
    assert np.linalg.norm(b.R.T@relief)<1e-10
    # Sciag nie usztywnia sztywnej bryly,masa dodana odpowiada bilansem.
    before=b.mass_rigid[0,0];b.add_ties(1);tie_mass=b.mass_rigid[0,0]-before
    assert abs(tie_mass-b.ties[0]['mass_kg'])<1e-9
    assert np.linalg.norm(b.ties[0]['K']@b.R)/np.linalg.norm(b.ties[0]['K'].data)<1e-12
    b.set_floor();gravity=-9.80665*(b.M@b.R[:,2]);qg=spsolve(b.K+b.floor_K,gravity)
    floor_balance=float(np.linalg.norm(b.R.T@(gravity-b.floor_K@qg))/np.linalg.norm(b.R.T@gravity));assert floor_balance<1e-7
    supports=[float(-foot['k'][2]*(foot['P']@qg)[2]) for foot in b.feet];assert min(supports)>0
    result=dict(status='SCOPED_3D_NUMERICAL_AND_ANALYTIC_CONTROLS_NOT_MDF_QUALIFICATION',patch=patch,pure_bending=beam,
                material_volume_relative_error=volume_error,pressure_port_volume_relative_error=volume_port_error,
                pressure_rigid_generalized_force=pressure_balance.tolist(),rigid_stiffness_relative_residual=rigid_error,
                static_relative_residual=statres,tie_mass_kg=float(tie_mass),floor_balance_relative=floor_balance,normal_gravity_reactions_n=supports,
                mixed_normal_tangential_bond_patch_relative_error=joint_patch,mixed_bond_exact_work_relative_error=joint_work,
                input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                              ['skrypty/element_brylowy_P18C.py','skrypty/model_ramy_3D_P18C.py','skrypty/sprawdz_bryly_i_rame_P18C.py']})
    (ROOT/'wyniki/p18c_kontrole.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print('P18C kontrole:',patch,beam,'volume',volume_error,'floor',floor_balance,flush=True)


if __name__=='__main__':main()
