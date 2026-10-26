"""Niezależne eliminacje nodalne, geometria, granice i siatka P20B.

Rozwiązanie macierzowe nie używa zredukowanego portu chi ani Woodbury.
Sprawdza dyskretyzowany model; nie kwalifikuje uszczelki/MDF/śrub.
"""
from pathlib import Path
from itertools import product
import hashlib,json
import numpy as np
import sympy as sp
from scipy.optimize import brentq
from model_przegrody_P20B import Partition,two_chamber
from geometria_przegrody_P20B import matched_geometry
from geometria_wkladow_P20A import obstacles,Box,intersects
from sprawdz_wklady_P20A import navier_compliance

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    config=ROOT/'dane/konfiguracje/p20b_przegroda_vs_moduly.json'
    cfg=json.loads(config.read_text());basepath=ROOT/cfg['reference_insert_config'];base=json.loads(basepath.read_text())
    # Dwie niezależne zmienne ciśnienia i wszystkie DOF mechaniczne.
    full=[];mechanical=[];static=[];p0=101325.;Ca=.1/(1.4*p0)*(1-.05j);Cb=.02/(1.4*p0)
    specs=[('PERIM','CCCC',np.inf),('PERIM','CCCC',1e4),('PERIM','SSSS',1e6),('PATCH4','FREE',1e6)]
    for kind,bc,k in specs:
        m=Partition(base,cfg,.018,kind,bc,k,n=4);N=len(m.F)
        frequencies=[20.,40.,80.,float(np.sqrt(m.values[0])/(2*np.pi))]
        for f in frequencies:
            s=2j*np.pi*f;D=m.K+s*m.C+s*s*m.M
            q=np.linalg.solve(D,m.F);reduced=m.response([f]);qr=reduced['states'][:,0]
            err=float(np.linalg.norm(q-qr)/np.linalg.norm(q));assert err<1e-7
            power=float(abs((s*(m.F@q)).real-(2*np.pi*f)**2*np.vdot(q,m.C@q).real)/abs(s*(m.F@q)))
            assert power<1e-8
            mechanical.append(dict(kind=kind,boundary=bc,k_each='inf' if np.isinf(k) else k,f_hz=f,state_relative_error=err,power_residual=power))
            for Gs,Gv in [(0.,0.),(2e-7,0.),(2e-5,4e-6),(0.,4e-4)]:
                A=np.zeros((N+2,N+2),complex);A[:N,:N]=D;A[:N,N]=-m.F;A[:N,N+1]=m.F
                A[N,:N]=s*m.F;A[N,N]=s*Ca+Gs;A[N,N+1]=-Gs
                A[N+1,:N]=-s*m.F;A[N+1,N]=-Gs;A[N+1,N+1]=s*Cb+Gv+Gs
                rhs=np.zeros(N+2);rhs[N]=1.;x=np.linalg.solve(A,rhs);pa,pb=x[-2:]
                ref=two_chamber([f],Ca,Cb,reduced['compliance'],Gs,Gv)
                z=ref['input_impedance'][0];err_z=float(abs(pa-z)/abs(z))
                err_b=float(abs(pb-ref['rear_pressure_per_input'][0])/abs(z))
                loss=(2*np.pi*f)**2*np.vdot(x[:N],m.C@x[:N]).real+Gs*abs(pa-pb)**2+Gv*abs(pb)**2+(s*Ca).real*abs(pa)**2
                err_power=float(abs(pa.real-loss)/abs(pa));assert max(err_z,err_b,err_power)<1e-7
                full.append(dict(kind=kind,boundary=bc,k_each='inf' if np.isinf(k) else k,f_hz=f,
                    Gseal_m3_pa_s=Gs,Gvent_m3_pa_s=Gv,input_relative_error=err_z,rear_scaled_error=err_b,power_residual=err_power))
        # Hermetyczna masa gazu z tyłu, zadane końcowe T i ciśnienie z przodu.
        # Mechanika nadal liniowa. To nie wynik grzania cewki lub zamkniętego frontu.
        q_unit=np.linalg.solve(m.K,m.F);chi0=m.F@q_unit
        for n,delta_pa,dT in product([4,16],[-cfg['static_front_pressure_pa_case'],0.,cfg['static_front_pressure_pa_case']],base['temperature_inside_shifts_k']):
            geo=matched_geometry(base,cfg,n,.018,'LINER_GEOMETRY');vb=geo['rear_geometric_air_l']*.001
            lam=chi0*p0/vb;pn=1+delta_pa/p0;theta=1+dT/293.15
            eps=2*lam*(pn-theta)/(1+lam*pn+np.sqrt((1-lam*pn)**2+4*lam*theta))
            fun=lambda e:e/lam-pn+theta/(1-e)
            root=brentq(fun,-max(2.,4*lam*(1+theta+pn)),1-1e-12,xtol=1e-14)
            error=abs(eps-root);assert error<1e-11 and eps<1
            rear_pa=p0*theta/(1-eps);dp=p0+delta_pa-rear_pa;qq=q_unit*dp
            if kind=='PATCH4':
                absolute=m.p.transverse_displacements(qq);A=np.column_stack([np.ones(len(m.p.xy)),m.p.xy])
                relative=absolute-A@np.linalg.lstsq(A,absolute,rcond=None)[0]
            elif m.moving_frame:
                relative=m.p.transverse_displacements(qq[1:]);absolute=relative+qq[0]
            else:absolute=relative=m.p.transverse_displacements(qq)
            volume_error=abs(m.F@qq/vb-eps);assert volume_error<1e-12
            bend=float(np.max(abs(relative))/.018);motion=float(np.max(abs(absolute)))
            gas=max(abs(delta_pa),abs(rear_pa-p0))/p0
            travel=min(geo['rear_length_m'],geo['matched_position_from_inner_front_m']-.392)
            static.append(dict(kind=kind,boundary=bc,k_each='inf' if np.isinf(k) else k,n=n,front_pressure_offset_pa=delta_pa,
                prescribed_rear_temperature_shift_k=dT,rear_fractional_volume_decrease=float(eps),rear_pressure_offset_pa=float(rear_pa-p0),
                gas_root_absolute_error=error,mechanical_volume_scaled_error=float(volume_error),
                bending_over_t=bend,absolute_motion_m=motion,max_gas_pressure_offset_fraction=float(gas),
                within_assumed_screen=bool(bend<=.2 and motion<travel and gas<=.01)))
    # Algebra dla quasistatycznej podatności przegrody h, nie pełnej dynamiki płyty.
    s,a,b,h,g=sp.symbols('s a b h g',positive=True)
    M=sp.Matrix([[s*a+g+s*h,-g-s*h],[-g-s*h,s*b+g+s*h]])
    solution=M.inv()*sp.Matrix([1,0]);den=s*(g*(a+b)+s*(a*b+h*(a+b)))
    identities=[sp.factor(solution[0]-(g+s*(b+h))/den),sp.factor(solution[1]-(g+s*h)/den)]
    ceff=sp.factor(1/(s*solution[0]));dc=sp.limit(ceff,s,0)
    sealed=sp.simplify(ceff.subs(g,0)-(a+b*h/(b+h)))
    noncommuting=sp.simplify(sp.limit(dc,g,0)-sp.limit(ceff.subs(g,0),s,0))
    pole=-g*(a+b)/(a*b+h*(a+b))
    assert identities==[0,0] and sealed==0 and sp.simplify(noncommuting-b*b/(b+h))==0
    assert sp.simplify((den/s).subs(s,pole))==0
    lam,pn,theta=sp.symbols('lam pn theta',positive=True)
    eps=2*lam*(pn-theta)/(1+lam*pn+sp.sqrt((1-lam*pn)**2+4*lam*theta))
    static_identity=sp.simplify(eps**2-(1+lam*pn)*eps+lam*(pn-theta))
    static_rigid=sp.simplify(sp.limit(eps,lam,0,dir='+'))
    static_soft=sp.simplify(sp.limit(eps,lam,sp.oo)-(1-theta/pn))
    assert static_identity==static_rigid==static_soft==0
    # Formalne granice w zadanych, niezerowych częstotliwościach; oba otwarcia są idealne.
    f=np.array([.001,20.,80.,1e4]);ss=2j*np.pi*f;aa=.1/(1.4*p0);bb=.02/(1.4*p0);chi=np.full(4,1e-8-1e-10j)
    limits=[]
    for label,ca,cb,c,gs,gv,expected in [
        ('rigid_sealed',aa,bb,0.,0.,0.,1/(ss*aa)),
        ('back_compliance_zero',aa,0.,chi,0.,0.,1/(ss*aa)),
        ('seal_open',aa,bb,chi,np.inf,0.,1/(ss*(aa+bb))),
        ('back_open',aa,bb,chi,0.,np.inf,1/(ss*(aa+chi))),
        ('both_open',aa,bb,chi,np.inf,np.inf,np.zeros(4))]:
        r=two_chamber(f,ca,cb,c,gs,gv)
        err=float(np.max(abs(r['input_impedance']-expected)/np.maximum(abs(1/(ss*aa)),1e-30)))
        assert err<1e-12;limits.append(dict(case=label,max_scaled_error=err))
    assert np.all(two_chamber(f,aa,bb,chi,np.inf,np.inf)['vent_flow_per_input']==1)
    # Duża sztywność ramy redukuje się do nieruchomego obwodu, poza granicą rezonansu.
    fixed=Partition(base,cfg,.018,'PERIM','CCCC',np.inf,n=4)
    stiff=Partition(base,cfg,.018,'PERIM','CCCC',1e14,n=4)
    stiff_error=float(np.max(abs(stiff.compliance([20.,80.])/fixed.compliance([20.,80.])-1)))
    assert stiff_error<1e-5
    # Geometria i niezależny bilans: przód + tył + cały plaster przegrody + bryły + włókna.
    geometry=[];hard=obstacles(base,1);Vhard=sum(x.volume for x in hard);W,D,H=base['inside_width_depth_height_m']
    for n,t,lining,host in product(cfg['equivalent_removed_module_counts'],cfg['partition_thickness_m'],['AIR_ONLY','LINER_GEOMETRY'],['FIXED','EXTENDED_FOR_BASELINE']):
        q=matched_geometry(base,cfg,n,t,lining,host=host)
        if not q['feasible_with_rear_gap']:continue
        fibres=0. if lining=='AIR_ONLY' else (1-base['lining_geometric_porosity_assumed'])*q['front_liner_envelope_l']*.001
        total=(q['matched_active_air_l']+q['rear_geometric_air_l'])*.001+W*H*t+Vhard+.004+fibres
        err=abs(total-W*H*q['inside_depth_m']);assert err<1e-12
        # Narzędzie jako prosty walec ujęty AABB, nie cała ręka/uchwyt.
        for ix,iz in product([-1,1],repeat=2):
            x=W/2+ix*cfg['support_offset_from_center_m'][0];z=H/2+iz*cfg['support_offset_from_center_m'][1];r=.005
            tool=Box((x-r,0,z-r),(x+r,q['matched_position_from_inner_front_m'],z+r),'tool-envelope')
            assert not any(intersects(tool,o) for o in hard)
        assert not q['whole_rigid_plate_aperture_possible']
        geometry.append(dict(n=n,t_m=t,lining=lining,host=host,volume_residual_m3=err))
    # Zbieżność świadków oddzielona od tożsamości macierzowych.
    mesh=[]
    for kind,bc,k,t in [('PERIM','CCCC',np.inf,.018),('PERIM','CCCC',1e4,.018),('PATCH4','FREE',1e6,.018),('PATCH4','FREE',1e7,.025)]:
        for n in [6,10,14]:
            m=Partition(base,cfg,t,kind,bc,k,n=n);c=m.compliance([20.,40.,80.])
            mesh.append(dict(kind=kind,boundary=bc,k_each='inf' if np.isinf(k) else k,t_m=t,n=n,
                static_m3_pa=m.static_compliance,chi20_re=float(c[0].real),chi20_im=float(c[0].imag),
                chi40_re=float(c[1].real),chi40_im=float(c[1].imag),chi80_re=float(c[2].real),chi80_im=float(c[2].imag)))
    navier=[]
    for t in [.012,.018,.025]:
        m=Partition(base,cfg,t,'PERIM','SSSS',np.inf,n=14)
        ref,tail=navier_compliance(m.a,m.b,t,base['mdf_E_pa_assumed'],base['mdf_nu_assumed'])
        diff=m.static_compliance/ref-1;assert abs(diff)<.03
        navier.append(dict(t_m=t,n=14,navier_partial_sum_m3_pa=ref,positive_tail_bound_m3_pa=tail,FEM_m3_pa=m.static_compliance,relative_difference=diff))
    inputs=[config,basepath,Path(__file__),ROOT/'skrypty/model_przegrody_P20B.py',ROOT/'skrypty/geometria_przegrody_P20B.py',
        ROOT/'skrypty/geometria_wkladow_P20A.py',ROOT/'skrypty/model_plyty_MITC_P18.py',ROOT/'skrypty/sprawdz_wklady_P20A.py']
    result=dict(status='INDEPENDENT_NODAL_REDUCTION_ALGEBRA_GEOMETRY_AND_SELECTED_MESH_WITNESSES',
        full_nodal_coupled=full,mechanical_direct=mechanical,static_hermetic_gas=static,limits=limits,stiff_frame_limit_relative_error=stiff_error,
        geometry=geometry,selected_mesh=mesh,navier=navier,
        algebra=dict(two_node_identities=[str(x) for x in identities],sealed_identity=str(sealed),
            noncommuting_dc_gap=str(noncommuting),unforced_differential_pressure_pole=str(pole),
            static_equilibrium_identity=str(static_identity),static_rigid_limit_error=str(static_rigid),static_soft_limit_error=str(static_soft),
            note='Quasistatic h,closed rear; this is a pole of transient differential pressure/input impedance, not necessarily the admittance-branch pole.'),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Same assembly with independent full solves is a numerical cross-check, not independent physical data.',
            'Static rear gas uses prescribed final temperature and front pressure,not a coil-heating prediction; linear plate results outside screens retained as formal.',
            'Selected mesh witnesses and positive Navier tail do not certify all continuous-frequency extrema.',
            'Central inscribed disk gives a necessary aperture condition for a rigid continuous passage only.',
            'Tool-envelope clearance excludes handle,hands,driver basket,wires and undeveloped permanent rods.'])
    (OUT/'p20b_kontrole_niezalezne.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20B checks:',len(full),'full nodal coupled,',len(mechanical),'mechanical,',len(static),'static gas,',len(geometry),'geometry,',len(mesh),'mesh,',len(navier),'Navier',flush=True)


if __name__=='__main__':main()
