"""P20C: rzeczywiste objętości MDF/kleju, mechanika3D, dwa porty i gaz.

Trzy siatki × trzy E kleju × bez/ześciągiem. Zgodne zakończone rekordy
są wznawiane po hashu; odczyt nie jest nową niezależną replikacją.
"""
from pathlib import Path
from itertools import product
import gc,hashlib,json,platform,resource,time
import numpy as np
import scipy
from model_modulu_3D_P20C import SolidModule,gas_port
from sprawdz_modul_3D_P20C import invariants
from analiza_wkladow_P20A import table
from model_gazu import Medium,conductance_from_reference

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p20c_modul_pelny_3D.json'


def modal_chi(f,values,coupling,residual,beta):
    result=[]
    for freq in f:
        s=2j*np.pi*freq;result.append(np.einsum('ki,kj,k->ij',coupling,coupling,1/(values*(1+s*beta)+s*s))+residual/(1+s*beta))
    return np.array(result)


def inputs():
    cfg=json.loads(CFG.read_text());basepath=ROOT/cfg['reference_insert_config']
    names=[CFG,basepath,Path(__file__),ROOT/'skrypty/model_modulu_3D_P20C.py',ROOT/'skrypty/sprawdz_modul_3D_P20C.py',
        ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'skrypty/model_ramy_3D_P18C.py',ROOT/'skrypty/model_gazu.py',
        ROOT/'skrypty/analiza_wkladow_P20A.py',ROOT/'brief_system_audio_DIY_v0.6.md']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in names}
    run=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    return cfg,json.loads(basepath.read_text()),hashes,run


def compute(base,cfg,n,braced,eg,case_id,state_path):
    start=time.monotonic();m=SolidModule(base,cfg,n,braced=braced,glue_E=eg);iv=invariants(m)
    static,qs=m.static();values,V,rigid=m.modes(cfg['retained_elastic_modes']);coupling=V.T@m.H
    captured=np.einsum('ki,kj,k->ij',coupling,coupling,1/values);residual=(static+static.T-captured-captured.T)/2
    minimum=float(np.linalg.eigvalsh(residual).min());assert minimum>-1e-10*np.linalg.norm(static)
    fractions=np.sum(coupling**2,axis=1)/values/np.trace(static)
    active=np.flatnonzero(fractions>1e-6);assert len(active)>0
    first=float(np.sqrt(values[0])/(2*np.pi));first_pressure=float(np.sqrt(values[active[0]])/(2*np.pi))
    f=np.array(sorted(set(cfg['probe_frequencies_hz']+[first*.98,first*1.02,first_pressure*.98,first_pressure*1.02])))
    direct=m.direct(f);predicted=modal_chi(f,values,coupling,residual,m.beta)
    modal_error=np.linalg.norm(predicted-direct['chi'],axis=(1,2))/np.linalg.norm(direct['chi'],axis=(1,2))
    common_error=abs(np.sum(predicted,axis=(1,2))/np.sum(direct['chi'],axis=(1,2))-1)
    medium=Medium();empty_cavity_ref=medium.c/(2*max(m.inner));mechanical=[];ports=[];modes=[]
    max_power=direct['power_residual'];min_dissipative_eigen=0.
    for j,freq in enumerate(f):
        c=direct['chi'][j];s=2j*np.pi*freq;hermitian=(s*c+(s*c).conj().T)/2
        emin=float(np.linalg.eigvalsh(hermitian).min());min_dissipative_eigen=min(min_dissipative_eigen,emin)
        assert emin>=-1e-9*np.linalg.norm(s*c)
        row=dict(case_id=case_id,f_hz=float(freq),is_probe=bool(freq in cfg['probe_frequencies_hz']),
            modal_matrix_relative_error=float(modal_error[j]),modal_common_pressure_relative_error=float(common_error[j]),
            below_empty_cavity_reference=bool(freq<empty_cavity_ref),minimum_dissipative_eigenvalue=emin)
        for a,b in product(range(2),repeat=2):row[f'chi_{a}{b}_re_m3_pa']=float(c[a,b].real);row[f'chi_{a}{b}_im_m3_pa']=float(c[a,b].imag)
        mechanical.append(row)
        for kappa,corner in product(cfg['gas_kappa_cases'],cfg['leak_100l_reference_corner_hz_cases']):
            Ci=m.inner_volume/(kappa*medium.p0_pa);G=conductance_from_reference(np.inf if corner=='inf' else corner,medium)
            r=gas_port([freq],direct['chi'][j:j+1],Ci,G);ratio=r['inside_to_outer_pressure'][0];delta=r['pressure_difference'][0];Y=r['admittance'][0]
            q=direct['states'][j]@np.array([ratio,1.]);loss=(2*np.pi*freq)**2*np.vdot(q,m.C@q).real
            leak_loss=0. if np.isinf(G) else G*abs(delta)**2;err=float(abs(Y.real-loss-leak_loss)/max(abs(Y),1e-30));max_power=max(max_power,err)
            assert err<1e-7 and Y.real>=-1e-9*abs(Y)
            # Usuwamy tylko numeryczny ruch sztywny; porty są od niego niezależne.
            q=q-m.R@np.linalg.solve(m.mass_rigid,m.R.T@(m.M@q))
            extra=Y/s*medium.gamma*medium.p0_pa*1000
            ports.append(dict(case_id=case_id,f_hz=float(freq),is_probe=bool(freq in cfg['probe_frequencies_hz']),gas_kappa=kappa,
                leak_100l_reference_corner_hz=corner,physical_G_m3_pa_s='inf' if np.isinf(G) else float(G),
                pressure_ratio_re=float(ratio.real),pressure_ratio_im=float(ratio.imag),
                admittance_re_m3_pa_s=float(Y.real),admittance_im_m3_pa_s=float(Y.imag),
                returned_storage_l=float(extra.real),returned_loss_l=float(-extra.imag),
                material_loss_w_per_outer_pa_rms2=float(loss),leak_loss_w_per_outer_pa_rms2=float(leak_loss),
                peak_relative_node_displacement_m_per_pa_rms=float(np.sqrt(2)*max(abs(q))),
                normalized_power_residual=err,below_empty_cavity_reference=bool(freq<empty_cavity_ref)))
    for i,(v,a,fraction) in enumerate(zip(values,coupling,fractions)):
        modes.append(dict(case_id=case_id,mode=i+1,dry_f_hz=float(np.sqrt(v)/(2*np.pi)),pressure_static_trace_fraction=float(fraction),
            coupling_inner=float(a[0]),coupling_outer=float(a[1])))
    # Mały statyczny offset zewnętrzny, gaz z linearyzowaną końcową podatnością izotermiczną.
    Ci_static=m.inner_volume/medium.p0_pa;pi=-static[0,1]/(Ci_static+static[0,0]);pressure=1000.
    qstatic=qs@np.array([pi,1.])*pressure
    joints=[dict(case_id=case_id,outer_static_pressure_offset_pa=pressure,inner_static_pressure_offset_pa=float(pi*pressure),**r) for r in m.static_glue_stress(qstatic)]
    summary=dict(case_id=case_id,mesh_resolution=n,wall_elements=m.wall_elements,glue_elements=m.glue_elements,braced=braced,glue_E_pa=eg,
        ndof=m.ndof,elements=len(m.elements),mdf_volume_l=m.mdf_volume*1000,glue_volume_l=m.glue_volume*1000,
        inner_air_l=m.inner_volume*1000,dry_mass_kg=m.dry_mass,chi_static_ii_m3_pa=float(static[0,0]),
        chi_static_io_m3_pa=float(static[0,1]),chi_static_oo_m3_pa=float(static[1,1]),common_pressure_static_compliance_m3_pa=float(static.sum()),
        first_dry_elastic_hz=first,first_of_retained_pressure_active_hz=first_pressure,empty_cavity_reference_hz=empty_cavity_ref,
        static_trace_fraction_retained=float(sum(fractions)),residual_static_minimum_eigenvalue=minimum,
        max_modal_matrix_error_at_probes=float(max(modal_error[[freq in cfg['probe_frequencies_hz'] for freq in f]])),
        max_modal_matrix_error_at_selected_frequencies=float(max(modal_error)),
        max_common_pressure_modal_error_at_selected_frequencies=float(max(common_error)),
        max_power_residual=max_power,rigid_eigenvalues=rigid.tolist(),
        elapsed_seconds=time.monotonic()-start,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    if state_path is not None:
        indices=[list(f).index(freq) for freq in cfg['probe_frequencies_hz']]
        np.savez_compressed(state_path,xyz=m.xyz,elements=m.elements,labels=m.labels,H=m.H,static_states=qs,
            frequencies_hz=cfg['probe_frequencies_hz'],direct_states=np.array([direct['states'][i] for i in indices]),
            retained_eigenvalues=values,retained_eigenvectors=V,modal_coupling=coupling,residual_static=residual,
            beta=m.beta,inner_volume=m.inner_volume,outer_volume=m.outer_volume)
    return dict(summary=summary,invariants=iv,mechanical_ports=mechanical,gas_ports=ports,modes=modes,joints=joints)


def main():
    cfg,base,hashes,run=inputs();folder=OUT/'p20c_przypadki'/run[:16];folder.mkdir(parents=True,exist_ok=True)
    results=[];fresh=0
    cases=list(product(cfg['mesh_resolution_cases'],[False,True],cfg['glue_E_pa_cases_assumed']))
    statepath=OUT/'p20c_pole_reference.npz'
    for n,braced,eg in cases:
        case_id=f"{'TIED' if braced else 'BARE'}_E{eg:g}_N{n}"
        p=folder/(case_id+'.json');is_reference=n==max(cfg['mesh_resolution_cases']) and braced and eg==max(cfg['glue_E_pa_cases_assumed'])
        if p.exists():
            r=json.loads(p.read_text());assert r['run_sha256']==run and r['input_sha256']==hashes
            if is_reference:assert statepath.exists() and hashlib.sha256(statepath.read_bytes()).hexdigest()==r['state_sha256']
            print('P20C checkpoint:',case_id,flush=True)
        else:
            r=compute(base,cfg,n,braced,eg,case_id,statepath if is_reference else None);r['run_sha256']=run;r['input_sha256']=hashes
            if is_reference:r['state_sha256']=hashlib.sha256(statepath.read_bytes()).hexdigest()
            temp=p.with_suffix('.tmp');temp.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False));temp.replace(p);fresh+=1
            print('P20C computed:',case_id,'DOF',r['summary']['ndof'],'f1',r['summary']['first_dry_elastic_hz'],'RSS',r['summary']['peak_rss_mib'],flush=True)
        results.append(r);gc.collect()
        for name,key in [('p20c_modele_3D.csv','summary'),('p20c_porty_mechaniczne.csv','mechanical_ports'),('p20c_gaz_i_przeciek.csv','gas_ports'),('p20c_mody.csv','modes'),('p20c_spoiny_statystyki.csv','joints')]:
            table(name,[v for result in results for v in ([result[key]] if key=='summary' else result[key])])
        result=dict(status='COMPLETE_SCOPED_3D_MODULE_FAMILIES' if len(results)==len(cases) else 'PARTIAL_DO_NOT_CLAIM_ALL_CASES',date='2026-10-26',
            run_sha256=run,input_sha256=hashes,cases=len(results),expected_cases=len(cases),
            mechanical_rows=sum(len(r['mechanical_ports']) for r in results),gas_rows=sum(len(r['gas_ports']) for r in results),
            joint_rows=sum(len(r['joints']) for r in results),checkpoint_folder=str(folder.relative_to(ROOT)),
            libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__),limitations=cfg['gates'])
        (OUT/'p20c_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20C COMPLETE:',len(results),'cases;',fresh,'fresh;',result['gas_rows'],'gas rows',flush=True)


if __name__=='__main__':main()
