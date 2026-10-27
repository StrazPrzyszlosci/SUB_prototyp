"""P21B:18rodzin mechaniki ze przestrzennym gazem i dwoma polami zewnętrznymi.

Atomowe rekordy przypadków i blokada rzeczywistego procesu. Checkpoint
odtwarza zgodne liczby,nie jest niezależną fizyczną walidacją.
"""
from pathlib import Path
from itertools import product
import fcntl,gc,hashlib,json,os,platform,resource,time
import numpy as np
import scipy
from model_modulu_3D_P20C import SolidModule
from model_gazu_3D_P21B import AcousticCavity
from sprawdz_gaz_3D_P21B import zero_dimensional
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p21b_gaz_przestrzenny_modulu.json'


def inputs():
    cfg=json.loads(CFG.read_text());sp=ROOT/cfg['solid_config'];scfg=json.loads(sp.read_text());bp=ROOT/scfg['reference_insert_config']
    paths=[CFG,sp,bp,Path(__file__),ROOT/'skrypty/model_gazu_3D_P21B.py',ROOT/'skrypty/sprawdz_gaz_3D_P21B.py',
        ROOT/'skrypty/model_modulu_3D_P20C.py',ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'skrypty/model_ramy_3D_P18C.py',
        ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/analiza_wkladow_P20A.py',ROOT/'brief_system_audio_DIY_v0.6.md']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    run=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    return cfg,scfg,json.loads(bp.read_text()),hashes,run


def velocity_bound(gas,pressure,f):
    # Grad p jest trójliniową funkcją na prostokątnym Q1:jej norma jest
    # ograniczona normami w wierzchołkach elementu. To granica interpolantuFE.
    dev=pressure-gas.ones[:,None]*(gas.mean_weights@pressure);maximum=np.zeros(pressure.shape[1])
    for size,ids in zip(gas.sizes,gas.elements):
        meta=gas.cache[tuple(np.round(size,12))][2]
        grad=np.einsum('abc,cd->abd',np.array(meta['corner_derivatives']),dev[ids])
        speed=np.sqrt(np.sum(abs(grad)**2,axis=1))/(gas.rho*2*np.pi*f)
        maximum=np.maximum(maximum,np.max(speed,axis=0))
    return maximum


def compute(base,scfg,cfg,n,braced,eg,case_id,modes_cache,state_path):
    start=time.monotonic();solid=SolidModule(base,scfg,n,braced=braced,glue_E=eg);gas=AcousticCavity(solid,kappa=cfg['gas_kappa'])
    geometry_key=(n,braced)
    if geometry_key not in modes_cache:
        values,V,zero=gas.modes(cfg['retained_acoustic_modes']);modes_cache[geometry_key]=dict(f_hz=(np.sqrt(values)/(2*np.pi)).tolist(),zero_eigenvalue=zero)
    mode_record=modes_cache[geometry_key]
    diagnostic=eg==max(cfg['glue_E_pa_cases_assumed']) and n in cfg['mesh_resolution_cases'][-2:]
    frequencies=sorted(set(cfg['probe_frequencies_hz']+(cfg['diagnostic_frequencies_hz'] if diagnostic else [])))
    rows=[];matrices=[];comparison=[];fields=[];max_checks={k:0. for k in ['energy_residual','mechanical_residual','acoustic_residual','momentum_residual','reciprocity_residual']};flags=0
    for f in frequencies:
        r=gas.solve(f);old,pi0,u0=zero_dimensional(gas,f);Y=r['admittance'];s=2j*np.pi*f;uniform_delta=float(abs(Y[0,0]/old[0,0]-1))
        bound=velocity_bound(gas,r['pressure_states'],f)
        loss_eigen=float(np.linalg.eigvalsh((Y+Y.conj().T)/2).min())
        local_gate=True
        for key in max_checks:
            max_checks[key]=max(max_checks[key],r[key]);local_gate &= r[key]<=1e-6
        local_gate &= loss_eigen>=-1e-8*np.linalg.norm(Y)
        flags+=not local_gate
        for j,name in enumerate(gas.port_names):
            U=r['solid_states'][:,j];P=r['pressure_states'][:,j];mean=r['mean_pressure'][j];prms=r['pressure_volume_rms'][j]
            vol=gas.Ci*mean+solid.H[:,0]@U
            normscale=gas.Ci*prms+np.linalg.norm(solid.H[:,0])*np.linalg.norm(U)
            scaled_volume=float(abs(vol)/max(normscale,1e-30));local_gate &= scaled_volume<1e-6
            rigid=solid.R@np.linalg.solve(solid.mass_rigid,solid.R.T@(solid.M@U));relative=U-rigid
            phi_max=1. if j==0 else 1.5
            pressure_limit=.01*gas.medium.p0_pa/(np.sqrt(2)*max(phi_max,r['maximum_nodal_pressure_rms'][j]))
            speed_limit=.03*gas.c/(np.sqrt(2)*max(bound[j],1e-300))
            rows.append(dict(case_id=case_id,mesh_resolution=n,braced=braced,glue_E_pa=eg,field=name,f_hz=f,is_probe=bool(f in cfg['probe_frequencies_hz']),
                imposed_outer_modal_pressure_rms_pa=1.,mean_inner_pressure_re_pa=float(mean.real),mean_inner_pressure_im_pa=float(mean.imag),
                pressure_deviation_volume_rms_pa=float(r['pressure_deviation_rms'][j]),pressure_volume_rms_pa=float(prms),
                bounded_relative_pressure_variation=float(r['pressure_deviation_rms'][j]/prms),
                maximum_nodal_pressure_rms_pa=float(r['maximum_nodal_pressure_rms'][j]),FE_corner_velocity_rms_upper_m_s=float(bound[j]),
                assumed_outer_modal_pressure_limit_rms_pa=float(min(pressure_limit,speed_limit)),
                mean_volume_velocity_re_m3_s=float((s*solid.H[:,1]@U).real),mean_volume_velocity_im_m3_s=float((s*solid.H[:,1]@U).imag),
                generalized_work_admittance_re_m3_pa_s=float(Y[j,j].real),generalized_work_admittance_im_m3_pa_s=float(Y[j,j].imag),
                input_power_w=float(Y[j,j].real),solid_loss_w=float(r['solid_loss_matrix'][j,j].real),fluid_average_power_w=float(r['fluid_average_power'][j]),
                solid_strain_energy_avg_j=float(r['solid_strain_energy_avg'][j]),solid_kinetic_energy_avg_j=float(r['solid_kinetic_energy_avg'][j]),
                fluid_potential_energy_avg_j=float(r['fluid_potential_energy_avg'][j]),fluid_kinetic_energy_avg_j=float(r['fluid_kinetic_energy_avg'][j]),
                max_solid_rigid_component_peak_m=float(np.sqrt(2)*max(abs(rigid))),max_solid_relative_component_peak_m=float(np.sqrt(2)*max(abs(relative))),
                mean_volume_balance_absolute_m3=float(abs(vol)),mean_volume_balance_scaled=scaled_volume,
                within_numerical_screen=bool(local_gate),
                scope='RMS1Pa of specified outer field;free body,inviscid sealed gas;gradient work flux is not net volume alone.'))
        comparison.append(dict(case_id=case_id,f_hz=f,is_probe=bool(f in cfg['probe_frequencies_hz']),uniform_admittance_relative_change_to0D=uniform_delta,
            full_admittance_matrix_relative_change_to0D=float(np.linalg.norm(Y-old)/np.linalg.norm(old)),
            returned_storage_uniform_l=float((Y[0,0]/s).real*1.4*gas.medium.p0_pa*1000),returned_loss_uniform_l=float(-(Y[0,0]/s).imag*1.4*gas.medium.p0_pa*1000),
            minimum_dissipative_eigenvalue=loss_eigen,within_numerical_screen=bool(local_gate),**{k:r[k] for k in max_checks}))
        for a,b in product(range(2),repeat=2):
            matrices.append(dict(case_id=case_id,f_hz=f,output_port=a,input_port=b,admittance_re_m3_pa_s=float(Y[a,b].real),admittance_im_m3_pa_s=float(Y[a,b].imag),
                zero_dimensional_re_m3_pa_s=float(old[a,b].real),zero_dimensional_im_m3_pa_s=float(old[a,b].imag)))
        if state_path is not None and f in [20.,80.,1200.]:fields.append((f,r['solid_states'],r['pressure_states']))
        print('P21B frequency:',case_id,f,'dY0',uniform_delta,'energy',r['energy_residual'],flush=True)
    summary=dict(case_id=case_id,mesh_resolution=n,braced=braced,glue_E_pa=eg,solid_dof=solid.ndof,fluid_dof=gas.ndof,total_unknowns=solid.ndof+gas.ndof+2,
        solid_elements=len(solid.elements),fluid_elements=len(gas.elements),gas_volume_l=gas.volume*1000,dry_solid_mass_kg=solid.dry_mass,
        gas_mass_kg=gas.rho*gas.volume,boundary_work_relative_error=gas.boundary_work_error,volume_boundary_gradient_relative_error=gas.gradient_boundary_error,
        first_rigid_gas_mode_hz=mode_record['f_hz'][0],frequency_cases=len(frequencies),flagged_frequency_cases=int(flags),
        max_uniform_admittance_change_in_band=max(r['uniform_admittance_relative_change_to0D'] for r in comparison if r['is_probe']),
        max_checks=max_checks,elapsed_seconds=time.monotonic()-start,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    if state_path is not None:
        assert len(fields)==3
        np.savez_compressed(state_path,frequencies_hz=np.array([r[0] for r in fields]),solid_xyz=solid.xyz,solid_elements=solid.elements,
            fluid_xyz=gas.xyz,fluid_elements=gas.elements,fluid_full_ids=gas.full_ids,axes_x=solid.axes[0],axes_y=solid.axes[1],axes_z=solid.axes[2],
            solid_states=np.array([r[1] for r in fields]),pressure_states=np.array([r[2] for r in fields]),Hext=gas.Hext)
    return dict(summary=summary,acoustic_modes=mode_record,rows=rows,admittance_matrices=matrices,comparison=comparison)


def main():
    cfg,scfg,base,hashes,run=inputs();folder=OUT/'p21b_przypadki'/run[:16];folder.mkdir(parents=True,exist_ok=True)
    lockdir=ROOT/'.p21b_locks';lockdir.mkdir(exist_ok=True);fd=(lockdir/(run[:16]+'.lock')).open('a+')
    try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise RuntimeError('P21B already holds this run lock;inspect the live process/session before resuming.')
    results=[];modes_cache={};fresh=0;cases=list(product(cfg['mesh_resolution_cases'],cfg['braced_cases'],cfg['glue_E_pa_cases_assumed']))
    state=OUT/f'p21b_pole_reference_{run[:16]}.npz'
    for n,braced,eg in cases:
        case_id=f"{'TIED' if braced else 'BARE'}_E{eg:g}_N{n}";p=folder/(case_id+'.json');reference=braced and eg==max(cfg['glue_E_pa_cases_assumed']) and n==max(cfg['mesh_resolution_cases'])
        if p.exists():
            r=json.loads(p.read_text());assert r['run_sha256']==run and r['input_sha256']==hashes
            modes_cache[(n,braced)]=r['acoustic_modes']
            if reference:assert state.exists() and hashlib.sha256(state.read_bytes()).hexdigest()==r['state_sha256']
            print('P21B checkpoint:',case_id,flush=True)
        else:
            available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
            if n>=12 and available<2_500_000_000:raise RuntimeError('Available RAM guard before large P21B case;finished records preserved.')
            r=compute(base,scfg,cfg,n,braced,eg,case_id,modes_cache,state if reference else None);r['run_sha256']=run;r['input_sha256']=hashes
            if reference:r['state_sha256']=hashlib.sha256(state.read_bytes()).hexdigest()
            temporary=p.with_suffix('.tmp');temporary.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False));temporary.replace(p);fresh+=1
        results.append(r);gc.collect()
        table('p21b_modele_i_geometria.csv',[r['summary'] for r in results])
        for name,key in [('p21b_pola_i_energia.csv','rows'),('p21b_porownanie_z0D.csv','comparison'),('p21b_macierze_admitancji.csv','admittance_matrices')]:
            table(name,[row for r in results for row in r[key]])
        table('p21b_mody_sztywnego_gazu.csv',[dict(mesh_resolution=n,braced=b,mode=i+1,f_hz=v) for (n,b),mr in sorted(modes_cache.items()) for i,v in enumerate(mr['f_hz'])])
        summary=dict(status='COMPLETE_CONFIGURED_SPATIAL_FAMILIES' if len(results)==len(cases) else 'PARTIAL_ACTIVE_DO_NOT_CLAIM_ALL_CASES',
            date='2026-10-26',run_sha256=run,input_sha256=hashes,cases=len(results),expected_cases=len(cases),
            checkpoint_folder=str(folder.relative_to(ROOT)),reference_state_file=str(state.relative_to(ROOT)),
            field_rows=sum(len(r['rows']) for r in results),frequency_cases=sum(r['summary']['frequency_cases'] for r in results),
            flagged_frequency_cases=sum(r['summary']['flagged_frequency_cases'] for r in results),
            libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__),limitations=cfg['gates'])
        (OUT/'p21b_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
        print('P21B progress:',len(results),'/',len(cases),'RSS',r['summary']['peak_rss_mib'],flush=True)
    print('P21B COMPLETE:',len(results),'cases;',fresh,'fresh;',summary['frequency_cases'],'frequency systems',flush=True)


if __name__=='__main__':main()
