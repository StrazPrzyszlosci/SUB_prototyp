"""P19A:656statycznych podmodeli klej/MDF,podatność i piki naprężeń."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import eigsh,spsolve
from model_plyty_MITC_P18 import PlateMaterial,RectangularPlate
from model_normalnego_polaczenia_P19 import normal_joint,solve_joint
from model_gazu import Medium,ThermalSpectrum

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def cases(cfg):
    rows=[]
    for boundary in cfg['boundaries']:
        for size in cfg['pad_size_m']:
            for t in cfg['pad_thickness_m']:
                for E in cfg['glue_E_profiles']:
                    for gap in cfg['glue_gap_m']:
                        for Ez in cfg['Ez_to_bending_E']:
                            rows.append(dict(case_id=f'{len(rows):04d}',boundary=boundary,size_m=size,t_m=t,E_profile=E['id'],glue_E_pa=E['E_pa'],gap_m=gap,Ez_factor=Ez,eccentricity_m=0.,defect='NONE'))
    for boundary in cfg['boundaries']:
        base=next(r for r in rows if r['boundary']==boundary and r['size_m']==.08 and r['t_m']==.018 and r['E_profile']=='EA9466_FILM_TYPICAL' and r['gap_m']==.0002 and r['Ez_factor']==.15)
        for e in cfg['eccentricity_controls_m']:rows.append(dict(base,case_id=f'{len(rows):04d}',eccentricity_m=e))
        for defect in cfg['defect_controls']:rows.append(dict(base,case_id=f'{len(rows):04d}',defect=defect))
    return rows


def build(case,cfg):
    panel=RectangularPlate(cfg['panel_a_m'],cfg['panel_b_m'],*cfg['panel_mesh'],PlateMaterial(cfg['panel_E_pa'],cfg['nu'],cfg['rho_kg_m3'],cfg['panel_thickness_m']),case['boundary'])
    Epad=cfg['pad_E_lookup_pa'][str(case['t_m'])]
    system=normal_joint(panel,case['size_m'],case['t_m'],Epad,case['glue_E_pa'],case['gap_m'],case['Ez_factor'],cfg['rod_E_pa'],cfg['rod_area_m2'],cfg['rod_length_m'],cfg['pad_mesh'],case['eccentricity_m'],case['defect'])
    return panel,system


def worker(job):
    case,cfg=job;panel,system=build(case,cfg);q,metrics=solve_joint(system);pressure=cfg['static_pressure_peak_pa'];peak=metrics['maximum_normal_traction_per_pa']*pressure
    row=dict(**case,**metrics,bond_area_m2=system['bond_area_m2'],effective_normal_foundation_n_m3=system['kn_n_m3'],
        normal_glue_compliance_fraction=system['c_glue_m_pa']/(system['c_glue_m_pa']+system['c_mdf_m_pa']),
        static_tie_force_n=metrics['tie_force_per_pa_n']*pressure,maximum_static_normal_stress_pa=peak,
        maximum_static_glue_opening_m=metrics['maximum_glue_opening_per_pa_m']*pressure,
        maximum_static_MDF_normal_deformation_m=metrics['maximum_MDF_normal_deformation_per_pa_m']*pressure,
        nominal_IB_reference_utilization=peak/cfg['IB_reference_pa'],
        required_normal_static_strength_pa=cfg['stress_requirement_multiplier']*peak,
        scope='NORMALNE_POLACZENIE;NIE_DOPUSZCZALNA_NOSNOSC_ZMECZENIOWA_KLEJU_MDF')
    dynamic=[];arrays=None
    selected=(case['size_m']==.08 and case['t_m']==.018 and case['E_profile']=='EA9466_FILM_TYPICAL' and case['gap_m']==.0002 and case['Ez_factor']==.15 and case['eccentricity_m']==0 and case['defect']=='NONE')
    if selected:
        K=system['K'];M=system['M'];eigen,modes=eigsh(K,k=8,M=M,sigma=0.,which='LM');order=np.argsort(eigen);eigen=eigen[order];modes=modes[:,order];freq=np.sqrt(eigen)/(2*np.pi)
        w1=2*np.pi*freq[0];w2=5*w1;zeta=cfg['dynamic_zeta'];alpha=2*zeta*w1*w2/(w1+w2);beta=2*zeta/(w1+w2);C=alpha*M+beta*K
        frequencies=np.unique(np.r_[cfg['dynamic_base_hz'],freq[freq<=1000],freq[freq<=1000]*.97,freq[freq<=1000]*1.03]);frequencies=frequencies[(frequencies>0)&(frequencies<=1000)]
        med=Medium()
        for f in frequencies:
            w=2*np.pi*f;u=spsolve(K-w*w*M+1j*w*C,system['force']);compliance=system['force']@u
            supplied=-w*compliance.imag;dissipation=w*w*np.vdot(u,C@u).real;residual=abs(supplied-dissipation)/max(abs(supplied),1e-30)
            stress=np.sqrt(2)*float(max(abs(system['traction_probe']@u)));force=np.sqrt(2)*abs(2*system['krod']*(system['b']@u))
            r=dict(case_id=case['case_id'],boundary=case['boundary'],f_hz=float(f),compliance_m3_pa_real=float(compliance.real),compliance_m3_pa_imag=float(compliance.imag),
                normal_stress_peak_per_PaRMS=stress,tie_force_peak_per_PaRMS_n=float(force),relative_power_residual=float(residual))
            if f in [20.,40.,80.]:
                bulk=ThermalSpectrum((.005,),(1.,)).bulk_modulus(np.array([f]),med)[0];Cab=.1/bulk;s=1j*w;ext=20e-6*10**(95/20)
                inflow=-ext*4*np.pi*np.exp(s/med.c)/(med.rho*s)
                inside=inflow/(s*(Cab+2*compliance))
                r.update(reference_cone_SPL_4pi1m_rms_db=95.,reference_air_l=100.,coupled_uniform_inner_pressure_rms_pa=float(abs(inside)),
                    reference_normal_stress_peak_pa=float(stress*abs(inside)),reference_tie_force_peak_n=float(force*abs(inside)),
                    required_fatigue_strength_at_reference_pa=float(cfg['stress_requirement_multiplier']*stress*abs(inside)),
                    cycles_1000h_continuous=float(f*3600*1000),cycles_5000h_10percent_duty=float(f*3600*5000*.1))
            dynamic.append(r)
        row['first_8_modes_hz']=freq.tolist();arrays=dict(static=q,first_modes=modes[:,:4],panel_xy=panel.xy,pad_xy=system['pad'].xy,nmain=system['nmain'],panel_free=panel.free)
    return row,dynamic,arrays


def table(name,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    cfgp=ROOT/'dane/konfiguracje/p19a_normalne_polaczenia.json';cfg=json.loads(cfgp.read_text());specs=cases(cfg)
    sources=[cfgp,ROOT/'dane/materialy/kleje_P19_mechanika_v1.json',ROOT/'dane/materialy/mdf_i_kleje_P18_P19.json',Path(__file__),ROOT/'skrypty/model_normalnego_polaczenia_P19.py',ROOT/'skrypty/model_plyty_MITC_P18.py',ROOT/'skrypty/model_gazu.py',ROOT/'brief_system_audio_DIY_v0.6.md']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};run=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    lockdir=ROOT/'.p19_locks';lockdir.mkdir(exist_ok=True);guard=(lockdir/(run+'.lock')).open('a')
    try:fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:guard.close();raise RuntimeError('P19nadal działa; sprawdzić bieżącą sesję')
    cache=OUT/'p19a_checkpoint'/run[:16];cache.mkdir(exist_ok=True,parents=True)
    snapshot=OUT/'archiwum'/('P19A_start_'+run[:16])/'stan_wejsc'
    for p in sources:
        dest=snapshot/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():dest.write_bytes(p.read_bytes())
        assert dest.read_bytes()==p.read_bytes()
    completed={}
    for spec in specs:
        p=cache/(spec['case_id']+'.json')
        if p.exists():completed[spec['case_id']]=json.loads(p.read_text())
    print('P19A:',len(specs),'przypadków,',len(completed),'checkpointów',flush=True)
    with ProcessPoolExecutor(max_workers=cfg['workers']) as executor:
        futures=[executor.submit(worker,(spec,cfg)) for spec in specs if spec['case_id'] not in completed]
        for future in as_completed(futures):
            row,dynamic,arrays=future.result();case_id=row['case_id']
            if arrays is not None:np.savez_compressed(cache/(case_id+'.npz'),**arrays)
            record=dict(row=row,dynamic=dynamic);tmp=cache/(case_id+'.tmp');tmp.write_text(json.dumps(record,ensure_ascii=False,allow_nan=False));tmp.replace(cache/(case_id+'.json'));completed[case_id]=record
            if len(completed)%50==0:print('P19A:',len(completed),'/',len(specs),flush=True)
    for p in sources:assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(ROOT))]
    rows=[completed[r['case_id']]['row'] for r in specs];dynamic=[d for r in specs for d in completed[r['case_id']]['dynamic']]
    table('p19a_normalne_naprezenia.csv',rows);table('p19a_dynamika_i_wymagania_SN.csv',dynamic)
    result=dict(status='P19A_NORMALNE_POLACZENIA_NIE_FINALNY_DOBOR_KLEJU',run_sha256=run,input_sha256=hashes,cases=len(rows),dynamic_rows=len(dynamic),checkpoint_folder=str(cache.relative_to(ROOT)),
        max_force_relative_residual=max(r['force_balance_relative_error'] for r in rows),max_moment_relative_residual=max(r['moment_balance_relative_error'] for r in rows),
        max_Sherman_relative_error=max(r['independent_Sherman_Morrison_relative_error'] for r in rows),
        max_dynamic_power_residual=max(r['relative_power_residual'] for r in dynamic),
        scope=cfg['scope'],strength_scope=cfg['strength_scope'])
    (OUT/'p19a_podsumowanie.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));guard.close();print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
