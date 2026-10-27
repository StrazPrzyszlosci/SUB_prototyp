"""Niezależne wzorce P21B:Kronecker,sztywny prostopadłościan,piston1D.

Pełny blok vs rozdzielony mod średni,praca/pęd i granica0D. Weryfikacja
modelu numerycznego,nie pomiar parametrów materiału lub gotowego urządzenia.
"""
from pathlib import Path
from itertools import product
import gc,hashlib,json,resource,time
import numpy as np
from scipy.sparse.linalg import splu,spsolve
from model_modulu_3D_P20C import SolidModule
from model_gazu_3D_P21B import AcousticCavity,scalar_hex
from element_brylowy_P18C import quad_quadrature

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def scalar_analytic(length,rho,bulk):
    mass=[v/6*np.array([[2.,1.],[1.,2.]]) for v in length]
    stiffness=[1/v*np.array([[1.,-1.],[-1.,1.]]) for v in length]
    def kron(z,y,x):return np.kron(z,np.kron(y,x))
    C=kron(*mass[::-1])/bulk
    A=(kron(mass[2],mass[1],stiffness[0])+kron(mass[2],stiffness[1],mass[0])+kron(stiffness[2],mass[1],mass[0]))/rho
    order=[0,1,3,2,4,5,7,6]
    return A[np.ix_(order,order)],C[np.ix_(order,order)]


def rigid_rectangular_frequencies(length,c,count):
    f=[c/2*np.sqrt(sum((k/L)**2 for k,L in zip(m,length))) for m in product(range(5),repeat=3) if any(m)]
    return sorted(f)[:count]


def zero_dimensional(gas,f):
    m=gas.solid;s=2j*np.pi*f;D=((1+s*m.beta)*m.K+s*s*m.M).tocsc()
    u=splu(D).solve(np.column_stack([m.H[:,0],gas.Hext]).astype(complex))
    cii=m.H[:,0]@u[:,0];cie=m.H[:,0]@u[:,1:];pi=-cie/(gas.Ci+cii)
    U=u[:,1:]+u[:,0,None]*pi[None,:]
    return s*gas.Hext.T@U,pi,U


def main():
    start=time.monotonic();cp=ROOT/'dane/konfiguracje/p21b_gaz_przestrzenny_modulu.json';cfg=json.loads(cp.read_text())
    spath=ROOT/cfg['solid_config'];scfg=json.loads(spath.read_text());bp=ROOT/scfg['reference_insert_config'];base=json.loads(bp.read_text())
    scalar=[];eigen=[];duct=[];affine=[];split=[];limit=[];coupled=[]
    for lengths in [[.164,.084,.154],[.01,.0002,.02],[.1,.1,.1]]:
        a,c,meta=scalar_hex(lengths,1.2,141855.);ar,cr=scalar_analytic(lengths,1.2,141855.)
        ae=float(np.linalg.norm(a-ar)/np.linalg.norm(ar));ce=float(np.linalg.norm(c-cr)/np.linalg.norm(cr));assert max(ae,ce)<1e-12
        scalar.append(dict(length_m=lengths,stiffness_relative_error=ae,mass_relative_error=ce))
    # Tłok o zadanym ruchu na prawej ścianie sztywnego pustego prostopadłościanu.
    for n in cfg['mesh_resolution_cases']:
        solid=SolidModule(base,scfg,n,braced=False);gas=AcousticCavity(solid,kappa=cfg['gas_kappa']);L,D,H=solid.inner
        values,V,zero=gas.modes(12);computed=np.sqrt(values)/(2*np.pi);exact=np.array(rigid_rectangular_frequencies(solid.inner,gas.c,12))
        eigen.append(dict(mesh_resolution=n,fluid_dof=gas.ndof,zero_eigenvalue=zero,computed_hz=computed.tolist(),exact_hz=exact.tolist(),
            max_relative_frequency_error=float(max(abs(computed/exact-1)))))
        b=np.zeros(gas.ndof);area=0.
        for face,axis,value,sign in gas.boundary:
            if axis!=0 or abs(value-(solid.outer[0]-solid.wall))>1e-12:continue
            for N,point,w in quad_quadrature(gas.xyz[face],order=2):b[face]+=N*w;area+=w
        assert abs(area/(D*H)-1)<1e-10
        for f in [20.,80.,400.,float(gas.c/(4*L))]:
            w=2*np.pi*f;k=w/gas.c;u=1e-6
            p=spsolve(gas.A-w*w*gas.C,w*w*b*u)
            amplitude=-gas.rho*w*w*u/(k*np.sin(k*L));pexact=amplitude*np.cos(k*(gas.xyz[:,0]-solid.wall))
            wall=float(b@p/area);wall_exact=float(-gas.rho*gas.c*w*u/np.tan(k*L))
            nodal_error=float(np.sqrt(((p-pexact)@gas.C@(p-pexact))/(pexact@gas.C@pexact)))
            pressure_scale=gas.bulk*u/L;scaled_wall=float(abs(wall-wall_exact)/pressure_scale)
            mean=float(gas.mean_weights@p);mean_exact=-area*u/gas.Ci
            assert abs(mean/mean_exact-1)<1e-7
            duct.append(dict(mesh_resolution=n,f_hz=f,wall_displacement_rms_m=u,wall_pressure_rms_signed_pa=wall,
                exact_wall_pressure_pa=wall_exact,wall_error_scaled_by_static_pressure=scaled_wall,nodal_C_norm_relative_error=nodal_error,
                mean_pressure_pa=mean,exact_mean_pressure_pa=mean_exact,quarterwave_input_pressure_zero=bool(abs(k*L-np.pi/2)<1e-10)))
        for axis in range(3):
            p=gas.xyz[:,axis];a=np.eye(3)[axis];expected=np.r_[gas.volume*a,np.cross(solid.outer/2,a)*gas.volume]
            error=float(np.linalg.norm(gas.G@p-expected)/gas.volume);assert error<1e-9
            affine.append(dict(mesh_resolution=n,axis=axis,gradient_and_angular_integral_scaled_error=error))
        print('P21B analytical cavity:',n,'fluid',gas.ndof,'max mode error',eigen[-1]['max_relative_frequency_error'],flush=True)
        del solid,gas;gc.collect()
    assert eigen[-1]['max_relative_frequency_error']<.03
    for f in [20.,80.,400.]:
        selected=[r for r in duct if r['f_hz']==f]
        assert selected[-1]['wall_error_scaled_by_static_pressure']<selected[0]['wall_error_scaled_by_static_pressure']
    # Dwa warianty pełnej mechaniki; inne równania eliminacji średniej ciśnienia.
    for braced in [False,True]:
        solid=SolidModule(base,scfg,4,braced=braced);gas=AcousticCavity(solid,kappa=cfg['gas_kappa'])
        for f in [20.,80.]:
            r=gas.solve(f);raw=gas.solve(f,split_mean=False)
            eu=np.linalg.norm(r['solid_states']-raw['solid_states'],axis=0)/np.linalg.norm(r['solid_states'],axis=0)
            ep=np.linalg.norm(r['pressure_states']-raw['pressure_states'],axis=0)/np.linalg.norm(r['pressure_states'],axis=0)
            assert max(max(eu),max(ep))<1e-6
            split.append(dict(braced=braced,f_hz=f,solid_column_relative_errors=eu.tolist(),pressure_column_relative_errors=ep.tolist()))
            keys=['energy_residual','mechanical_residual','acoustic_residual','mean_volume_residual','momentum_residual','reciprocity_residual']
            checks={k:r[k] for k in keys};assert max(checks.values())<1e-7
            emin=float(np.linalg.eigvalsh((r['admittance']+r['admittance'].conj().T)/2).min())
            assert emin>-1e-9*np.linalg.norm(r['admittance'])
            coupled.append(dict(braced=braced,f_hz=f,minimum_dissipative_eigenvalue=emin,**checks))
            ref,pi,U=zero_dimensional(gas,f);errors=[]
            for scale in cfg['formal_spatial_stiffness_scale_cases']:
                value=r if scale==1. else gas.solve(f,spatial_scale=scale)
                error=float(np.linalg.norm(value['admittance']-ref)/np.linalg.norm(ref));errors.append(error)
                limit.append(dict(braced=braced,f_hz=f,spatial_scale=scale,relative_admittance_matrix_error_to0D=error,
                    uniform_port_relative_error=float(abs(value['admittance'][0,0]/ref[0,0]-1)),
                    pressure_std_per_unit_outer_pa=value['pressure_deviation_rms'].tolist(),mean_volume_residual=value['mean_volume_residual']))
            assert errors[-1]<errors[1]<errors[0] and errors[-1]<1e-5
        print('P21B coupled controls:',braced,flush=True);del solid,gas;gc.collect()
    inputs=[cp,spath,bp,Path(__file__),ROOT/'skrypty/model_gazu_3D_P21B.py',ROOT/'skrypty/model_modulu_3D_P20C.py',
        ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'skrypty/model_ramy_3D_P18C.py',ROOT/'skrypty/model_gazu.py']
    j=dict(status='KRONECKER_RIGID_CAVITY_PISTON_FULL_COUPLING_AND0D_LIMIT_CONTROLS',scalar_kronecker=scalar,rigid_eigenmodes=eigen,prescribed_piston=duct,
        affine_volume_gradient=affine,mean_split_comparisons=split,full_coupled_checks=coupled,formal0D_limit=limit,
        elapsed_seconds=time.monotonic()-start,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Analytical rigid-cavity tests do not identify damping or real material parameters.',
            'Formal A-scale limit changes effective gas inertia;not physical heating or an uncertainty distribution.',
            'Physical full gas retains body/gas momentum;solid rigid-mode removal used only inside strain-energy evaluation.'])
    (OUT/'p21b_kontrole_niezalezne.json').write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False))
    print('P21B checks complete:',len(duct),'piston,',len(coupled),'coupled,',len(limit),'limit;RSS',j['peak_rss_mib'],flush=True)


if __name__=='__main__':main()
