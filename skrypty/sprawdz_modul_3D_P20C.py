"""P20C: praca portów, masa, hydrostatyka i pełne równania MES+gaz.

Odniesienie hydrostatyczne dotyczy jednorodnej bryły o wspólnym E/nu.
Nie jest wynikiem rzeczywistego MDF/kleju. Kopie starych kampanii nie są uruchamiane.
"""
from pathlib import Path
from itertools import product
import hashlib,json,resource,time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
import sympy as sp
from model_modulu_3D_P20C import SolidModule,gas_port
from model_ramy_3D_P18C import skew

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def invariants(m):
    expected=m.nominal_budgets()
    for key,val in [('mdf_volume_m3',m.mdf_volume),('glue_volume_m3',m.glue_volume),('inner_air_m3',m.inner_volume),('dry_mass_kg',m.dry_mass)]:
        assert abs(val/expected[key]-1)<1e-10,(key,val,expected[key])
    rigid_force=m.R.T@m.H;rf=float(np.linalg.norm(rigid_force)/np.linalg.norm(m.H));assert rf<1e-10
    rk=float(np.linalg.norm(m.K@m.R)/np.linalg.norm(m.K.data));assert rk<1e-12
    affine=[]
    for row,column in product(range(3),repeat=2):
        q=np.zeros_like(m.xyz);q[:,row]=m.xyz[:,column];v=m.H.T@q.ravel()
        target=np.array([m.inner_volume,-m.outer_volume]) if row==column else np.zeros(2)
        affine.append(float(np.max(abs(v-target))/m.outer_volume))
    assert max(affine)<1e-10
    mass=np.zeros((6,6))
    for center,size,v,rho in zip(m.centers,m.sizes,m.volumes,m.densities):
        M=rho*v;S=skew(center);L=np.hstack([np.eye(3),-S]);mass+=M*(L.T@L)
        mass[3:,3:]+=np.diag(M/12*np.array([size[1]**2+size[2]**2,size[0]**2+size[2]**2,size[0]**2+size[1]**2]))
    mr=float(np.linalg.norm(m.mass_rigid-mass)/np.linalg.norm(mass));assert mr<1e-10
    chi,q=m.static();sr=float(np.linalg.norm(m.K@q-m.H)/np.linalg.norm(m.H));assert sr<1e-6
    reciprocity=float(np.linalg.norm(chi-chi.T)/np.linalg.norm(chi));assert reciprocity<1e-7
    assert np.linalg.eigvalsh((chi+chi.T)/2).min()>0
    return dict(ndof=m.ndof,elements=len(m.elements),analytic_budgets=expected,rigid_force_scaled_error=rf,rigid_stiffness_scaled_error=rk,
        affine_volume_errors=affine,mass_tensor_relative_error=mr,static_relative_residual=sr,reciprocity_relative_error=reciprocity)


def main():
    start=time.monotonic();cp=ROOT/'dane/konfiguracje/p20c_modul_pelny_3D.json';cfg=json.loads(cp.read_text());bp=ROOT/cfg['reference_insert_config'];base=json.loads(bp.read_text())
    geometry=[];hydro=[];full=[];dc_limits=[]
    for braced in [False,True]:
        h=SolidModule(base,cfg,4,braced=braced,homogeneous=True);geometry.append(invariants(h))
        Kbulk=h.E/(3*(1-2*h.nu));F=h.H.sum(axis=1);exact=(-h.xyz/(3*Kbulk)).ravel()
        force_error=float(np.linalg.norm(h.K@exact-F)/np.linalg.norm(F));assert force_error<1e-7
        chi,q=h.static();Q=q.sum(axis=1);value=F@Q;target=h.material_volume/Kbulk
        compliance_error=float(abs(value/target-1));assert compliance_error<1e-6
        work_exact=float(F@exact);assert abs(work_exact/target-1)<1e-10
        hydro.append(dict(braced=braced,solid_bulk_compliance_exact_m3_pa=target,computed_m3_pa=float(value),relative_error=compliance_error,affine_force_relative_error=force_error))
    for braced,eg in product([False,True],[1e7,1.718e9]):
        m=SolidModule(base,cfg,4,braced=braced,glue_E=eg);geometry.append(invariants(m));Ci=m.inner_volume/(1.4*101325.)
        f=np.array([20.,80.]);direct=m.direct(f);chi=direct['chi'];N=m.ndof
        assert direct['power_residual']<1e-7
        for G,frequency in product([0.,2*np.pi*Ci,2*np.pi*100*Ci],[20.,80.]):
            j=list(f).index(frequency);s=2j*np.pi*frequency;D=(1+s*m.beta)*m.K+s*s*m.M
            A=sparse.bmat([[D,-sparse.csr_matrix(m.H[:,0,None])],[s*sparse.csr_matrix(m.H[:,0][None,:]),sparse.csr_matrix([[G+s*Ci]])]],format='csc')
            rhs=np.r_[m.H[:,1],G].astype(complex);x=spsolve(A,rhs);q,pi=x[:-1],x[-1]
            Y=s*(m.H[:,1]@q)+G*(1-pi)
            r=gas_port([frequency],chi[j:j+1],Ci,G);ref=r['admittance'][0]
            err=float(abs(Y-ref)/abs(ref));p_err=float(abs(pi-r['inside_to_outer_pressure'][0]));assert max(err,p_err)<1e-7
            dissipated=(2*np.pi*frequency)**2*np.vdot(q,m.C@q).real+G*abs(1-pi)**2
            power=float(abs(Y.real-dissipated)/abs(Y));assert power<1e-7
            full.append(dict(braced=braced,glue_E_pa=eg,f_hz=frequency,G_m3_pa_s=G,admittance_relative_error=err,pressure_ratio_error=p_err,power_residual=power))
        c=m.static()[0][None,:,:];r=gas_port([1.],c,Ci,np.inf)['admittance'][0]/(2j*np.pi)
        expected=Ci+float(c.sum());assert abs(r/expected-1)<1e-12
        dc_limits.append(dict(braced=braced,glue_E_pa=eg,open_returned_compliance_m3_pa=float(r.real),Ci_m3_pa=Ci,common_material_compliance_m3_pa=float(c.sum())))
        del m
    # Ogólna wzajemna macierz cii,cio,coo: granice oraz niezamienność DC/G.
    s,g,a,b,c,ci=sp.symbols('s g a b c ci',positive=True)
    ratio=(g-s*b)/(g+s*(ci+a));Y=s*(c+b*ratio)+g*(1-ratio)
    opened=sp.simplify(sp.limit(Y/s,g,sp.oo)-(ci+a+2*b+c));sealed=sp.simplify((Y/s).subs(g,0)-(c-b*b/(ci+a)))
    assert opened==sealed==0
    gap=sp.simplify(sp.limit(sp.limit(Y/s,s,0),g,0)-sp.limit((Y/s).subs(g,0),s,0))
    assert sp.simplify(gap-(ci+a+b)**2/(ci+a))==0
    # Cienkie ściany: a=c=h,b=-h; to oddzielna granica modelu, nie założenie3D.
    h=sp.symbols('h',positive=True);thin=sp.simplify(Y.subs({a:h,b:-h,c:h})-(g+s*h)*s*ci/(g+s*(ci+h)));assert thin==0
    inputs=[cp,bp,Path(__file__),ROOT/'skrypty/model_modulu_3D_P20C.py',ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'skrypty/model_ramy_3D_P18C.py']
    result=dict(status='3D_MASS_VOLUME_WORK_HYDROSTATIC_AND_INDEPENDENT_COUPLED_GAS_CONTROLS',geometry=geometry,hydrostatic=hydro,full_nodal_gas=full,open_limit_witnesses=dc_limits,
        algebra=dict(open_limit_error=str(opened),sealed_limit_error=str(sealed),dc_noncommuting_gap=str(gap),thin_wall_reduction_error=str(thin)),
        elapsed_seconds=time.monotonic()-start,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Homogeneous hydrostatic benchmark does not identify real MDF or glue.',
            'Full nodal gas solve is independent elimination on the same mesh,not physical validation.',
            'No strength,fatigue,creep,contact opening or exterior radiation identification.'])
    (OUT/'p20c_kontrole_niezalezne.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20C checks:',len(geometry),'geometry/mass;',len(hydro),'hydrostatic;',len(full),'full nodal gas;',result['peak_rss_mib'],'MiB',flush=True)


if __name__=='__main__':main()
