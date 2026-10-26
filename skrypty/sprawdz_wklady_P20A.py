"""P20A: Navier z ogonem szeregu, pełny układ MES/gaz i granice portu."""
from pathlib import Path
from itertools import product
import hashlib,json
import numpy as np
from scipy.linalg import block_diag,eigh
import sympy as sp
from model_wkladu_P20A import HollowModule,plate_port
from geometria_wkladow_P20A import obstacles,Box

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json'


def navier_compliance(a,b,t,E,nu,last=61):
    D=E*t**3/(12*(1-nu**2));Gs=(5/6)*E*t/(2*(1+nu));total=0.
    for m,n in product(range(1,last+1,2),repeat=2):
        k2=(m*np.pi/a)**2+(n*np.pi/b)**2
        total+=64*a*b/(m*m*n*n*np.pi**4)*(1/(D*k2*k2)+1/(Gs*k2))
    # Wszystkie pominięte składniki dodatnie; ogony sum m^-4 i m^-6
    # ograniczone całką po wszystkich liczbach całkowitych, nie tylko nieparzystych.
    bound=8*a*b*((a*a+b*b)/(Gs*np.pi**4*3*last**3)+(a**4+b**4)/(D*np.pi**6*5*last**5))
    return total,bound


def moving_collision(start,end,size,obstacle,gap):
    lo=0.;hi=1.;v=np.array(end)-start;start=np.array(start);size=np.array(size)
    # Jawna tolerancja rozstrzyga stykanie na granicy nominalnego luzu.
    gap=max(0.,gap-1e-10)
    for i in range(3):
        low=obstacle.lo[i]-gap;high=obstacle.hi[i]+gap
        if abs(v[i])<1e-15:
            if start[i]+size[i]<=low or start[i]>=high:return False
        else:
            a=(low-start[i]-size[i])/v[i];b=(high-start[i])/v[i]
            lo=max(lo,min(a,b));hi=min(hi,max(a,b))
            if lo>=hi:return False
    return lo<hi


def main():
    cfg=json.loads(CFG.read_text());navier=[]
    for a,b,t in [(.164,.154,.008),(.164,.384,.008),(.156,.146,.012)]:
        ref,tail=navier_compliance(a,b,t,cfg['mdf_E_pa_assumed'],cfg['mdf_nu_assumed'])
        errors=[]
        for n in [6,10,14]:
            p=plate_port(a,b,t,'SSSS',n,cfg['mdf_E_pa_assumed'],cfg['mdf_nu_assumed'],cfg['mdf_density_kg_m3_assumed'])
            err=abs(p.static_compliance/ref-1);errors.append(err)
            navier.append(dict(a_m=a,b_m=b,t_m=t,mesh=n,navier_lower_m3_pa=ref,analytic_tail_bound_m3_pa=tail,
                               FEM_compliance_m3_pa=p.static_compliance,relative_difference_to_partial_sum=err))
        assert errors[-1]<.03 and errors[-1]<errors[0]
    # Algebraiczna pasywność dla chi=a-j*b, b>=0, g>=0.
    w,ci,g,b=sp.symbols('w ci g b',positive=True,real=True);a=sp.symbols('a',real=True);s=sp.I*w;chi=a-sp.I*b
    Y=(g+s*chi)*s*ci/(g+s*(chi+ci))
    real_formula=w*w*ci*ci*(g+w*b)/((g+w*b)**2+w*w*(a+ci)**2)
    passive_identity=sp.simplify(sp.re(Y)-real_formula);assert passive_identity==0
    sealed=sp.simplify((Y/s).subs(g,0)-ci*chi/(ci+chi));opened=sp.simplify(sp.limit(Y/s,g,sp.oo)-ci)
    assert sealed==opened==0
    laplace,h0=sp.symbols('laplace h0',positive=True)
    cstatic=ci*(g+laplace*h0)/(g+laplace*(h0+ci))
    dc_then_seal=sp.limit(sp.limit(cstatic,laplace,0),g,0)
    seal_then_dc=sp.limit(sp.limit(cstatic,g,0),laplace,0)
    assert sp.simplify(dc_then_seal-ci)==0 and sp.simplify(seal_then_dc-ci*h0/(ci+h0))==0
    # Osobny pełny układ nodalny MES + ciśnienie wewnętrzne, bez redukcji do chi.
    full=[];mode_checks=[];outer=(.18,.1,.17)
    for braced in [False,True]:
        m=HollowModule(outer,.008,'SSSS',cfg,n=4,braced=braced)
        Ks=[];Ms=[];Cs=[];forces=[]
        for p in m.faces:
            K,M=p.K.toarray(),p.M.toarray();values,V=eigh(K,M);MV=M@V
            C=(MV*(2*m.zeta*np.sqrt(values))[None,:])@MV.T
            Ks.append(K);Ms.append(M);Cs.append(C);forces.append(np.sqrt(2)*p.plate.F)
        K=block_diag(*Ks);M=block_diag(*Ms);C=block_diag(*Cs);F=np.concatenate(forces);N=len(F)
        for kappa in [1.,1.4]:
            Ci=m.inner_volume/(kappa*101325.);l,V=eigh(K+np.outer(F,F)/Ci,M)
            weights=(V.T@F)**2
            idx=np.flatnonzero(weights>sum(weights)*1e-12)[0]
            direct=float(np.sqrt(l[idx])/(2*np.pi));secular=m.pressure_mode_frequency(kappa)
            err=abs(direct/secular-1);assert err<1e-7
            mode_checks.append(dict(braced=braced,kappa=kappa,nodal_frequency_hz=direct,secular_frequency_hz=secular,relative_error=err))
        for kappa,corner,f in product([1.,1.4],[0.,1.,100.],[20.,80.,200.]):
            ss=2j*np.pi*f;Ci=m.inner_volume/(kappa*101325.);G=2*np.pi*corner*Ci
            D=K+ss*C+ss*ss*M
            A=np.zeros((N+1,N+1),complex);A[:N,:N]=D;A[:N,-1]=-F;A[-1,:N]=ss*F;A[-1,-1]=G+ss*Ci
            rhs=np.r_[-F,G];q=np.linalg.solve(A,rhs);Q=G*(1-q[-1])-ss*(F@q[:N])
            ref=m.port(np.array([f]),kappa,corner)['admittance'][0]
            error=float(abs(Q/ref-1));loss=(2*np.pi*f)**2*np.vdot(q[:N],C@q[:N]).real+G*abs(1-q[-1])**2
            energy=float(abs(Q.real-loss)/max(abs(Q),1e-30));assert max(error,energy)<1e-8
            full.append(dict(braced=braced,kappa=kappa,corner_hz=corner,f_hz=f,relative_admittance_error=error,normalized_power_error=energy))
    module_mesh=[]
    for bc,braced,n in product(['SSSS','CCCC'],[False,True],[6,10,14]):
        m=HollowModule(outer,.008,bc,cfg,n=n,braced=braced)
        port=m.port(np.array([20.,80.]))
        module_mesh.append(dict(boundary=bc,braced=braced,mesh=n,static_wall_compliance_m3_pa=m.chi_static,
            returned_storage_20hz_l=float(port['effective_compliance'][0].real*1.4*101325*1000),
            returned_storage_80hz_l=float(port['effective_compliance'][1].real*1.4*101325*1000)))
    layouts=json.loads((OUT/'p20a_tory_montazu.json').read_text())['layouts'];segments=0
    for r in layouts:
        fixed=obstacles(cfg,r['ties']);size=r['outer_width_length_height_m'];g=cfg['geometric_clearance_m_assumed']
        for path,box in zip(r['paths'],r['final_boxes']):
            for start,end in zip(path[:-1],path[1:]):
                assert not any(moving_collision(start,end,size,o,g) for o in fixed)
                segments+=1
            fixed.append(Box(tuple(box['lo']),tuple(box['hi']),'accepted'))
    # Formalne granice gazu hermetycznego z liniową podatnością ścian.
    lam,po,temp=sp.symbols('lam po temp',positive=True)
    eps=2*lam*(temp-po)/(1+lam*po+sp.sqrt((1-lam*po)**2+4*lam*temp))
    equilibrium=sp.simplify(eps**2+(1+lam*po)*eps+lam*(po-temp));assert equilibrium==0
    zero=sp.simplify(sp.limit(eps,lam,0,dir='+'));soft=sp.simplify(sp.limit(eps,lam,sp.oo)-(temp/po-1))
    assert zero==soft==0
    static_mount=[]
    for mass,ax,ay,az in product([.7,2.3],[0.,10.],[0.,10.],[0.,-10.]):
        sx,sy,h=.14,.06,.085
        B=np.array([[1,ix*sx/2,iy*sy/2] for ix,iy in product([-1,1],repeat=2)])
        force=np.array([mass*(9.80665+az),mass*ax*h,mass*ay*h]);q=np.linalg.solve(B.T@B,force);N=B@q
        direct=np.array([mass*(9.80665+az)/4+ix*mass*ax*h/(2*sx)+iy*mass*ay*h/(2*sy) for ix,iy in product([-1,1],repeat=2)])
        error=float(max(abs(N-direct)));assert error<1e-12;static_mount.append(error)
    inputs=[CFG,Path(__file__),ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/geometria_wkladow_P20A.py',ROOT/'skrypty/model_plyty_MITC_P18.py',OUT/'p20a_tory_montazu.json']
    result=dict(status='NAVIER_FEM_GAS_PASSIVITY_CONTINUOUS_PATH_AND_MOUNT_CONTROLS_NOT_PRODUCT_QUALIFICATION',
        navier=navier,full_nodal_gas_comparisons=full,pressure_mode_checks=mode_checks,module_mesh=module_mesh,verified_continuous_segments=segments,
        algebra=dict(positive_real_identity=str(passive_identity),sealed_limit=str(sealed),open_limit=str(opened),
            dc_then_seal=str(dc_then_seal),seal_then_dc=str(seal_then_dc),thermal_equilibrium=str(equilibrium),rigid_thermal_limit=str(zero),soft_thermal_limit=str(soft)),
        max_rigid_mount_force_difference_n=max(static_mount),
        scope='Navier tail is an analytic model inequality evaluated in floating point, not an end-to-end interval certificate. Trajectory class has no rotations. SSSS/CCCC not universal bounds.',
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (OUT/'p20a_kontrole_niezalezne.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20A checks:',len(navier),'Navier/FEM,',len(full),'nodal gas,',segments,'segments.',flush=True)


if __name__=='__main__':main()
