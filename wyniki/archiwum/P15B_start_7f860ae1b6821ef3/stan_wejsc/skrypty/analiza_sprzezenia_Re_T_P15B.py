"""Porównywalna rodzina24baz: Re(T),miejsce strat i obwiednia600s."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant
from model_termiczny_P15 import indistinguishable_cooling_family
from model_sprzezony_Re_T_P15B import AveragedCoupledModel,simulate_thermal
from analiza_cewki_z_pamiecia import dynamic_network
from model_cewki_z_pamiecia import linear_memory_response
from sygnaly_P14 import TonePair,joint_reference

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def make_coupled(entry,frequencies,b,eta,kv,cfg,memory):
    p=Plant.from_driver(Driver(**entry['model']));frequencies=np.array(frequencies,float)
    simple=linear_memory_response(p,cfg['volume_l'],frequencies,p.le0,[])
    if len(frequencies)==1:
        cap=min(cfg['amp_vrms'],cfg['amp_arms']/abs(simple['current'][0]),p.xref/simple['x_peak_m'][0])
    else:
        pair=TonePair(tuple(int(f) for f in frequencies),(1.,1.))
        cap=joint_reference(p,pair,simple,cfg['amp_vrms'],cfg['amp_arms'])['scale_phase_independent']
    volts=np.full(len(frequencies),cfg['drive_fraction']*cap)
    instant,branches,_=dynamic_network(p,cfg['profile'],memory)
    thermal=indistinguishable_cooling_family(cfg['Cv_j_k'],cfg['a_w_k'],cfg['D_per_s'],cfg['E_w_per_k_s'],b)
    return AveragedCoupledModel(p,cfg['volume_l'],frequencies,volts,instant,branches,thermal,cfg['alpha_per_k'],eta,kv)


def worker(job):
    entry,frequencies,b,eta,kv,envelope,cfg,memory=job
    model=make_coupled(entry,frequencies,b,eta,kv,cfg,memory)
    cold=model.response(0.);equilibrium=model.equilibrium(cfg['temperature_domain_rise_k'])
    trace,status=simulate_thermal(model,cfg['envelopes'][envelope],cfg)
    active=[r for r in trace if r['on']];max_r=max(active,key=lambda r:r['coil_rise_k'])
    warm=model.response(max_r['coil_rise_k']);motion_ratio=np.linalg.norm(warm['velocity'])/np.linalg.norm(cold['velocity'])
    tau_fast=min(model.thermal.foster_port().time_constants_s)
    fbase=int(frequencies[0]) if len(frequencies)==1 else int(np.gcd.reduce(np.array(frequencies,int)))
    row=dict(candidate_id=entry['candidate_id'],driver=entry['model']['name'],input_data_gate=entry.get('final_selection_gate','NOT_IDENTIFIED'),
        frequencies_hz=frequencies,volume_l=cfg['volume_l'],gvm_w_k=b,eta_eddy_to_coil=eta,forced_g_per_velocity=kv,envelope=envelope,
        voltage_each_rms_v=float(model.voltage_rms[0]),**status,
        max_sampled_coil_rise_k=max(r['coil_rise_k'] for r in trace),max_sampled_magnet_rise_k=max(r['magnet_rise_k'] for r in trace),
        last_coil_rise_k=trace[-1]['coil_rise_k'],last_magnet_rise_k=trace[-1]['magnet_rise_k'],
        cold_pcu_w=cold['pcu_w'],cold_peddy_w=cold['peddy_w'],cold_pcu_slope_w_k=cold['pcu_slope_w_k'],
        max_sampled_pcu_w=max(r['pcu_w'] for r in trace),
        delta_motion_at_hottest_active_db=float(20*np.log10(motion_ratio)),
        pcu_at_hottest_to_cold=float(warm['pcu_w']/cold['pcu_w']),
        total_heat_in_j=trace[-1]['heat_in_j'],total_heat_out_j=trace[-1]['heat_out_j'],
        max_heat_balance_relative_error=max(abs(r['heat_balance_error_j']) for r in trace)/max(trace[-1]['heat_in_j'],1.),
        cold_tau_fast_s=float(tau_fast),cold_tau_fast_over_forcing_period=float(tau_fast*fbase),
        maximum_sampled_motion_triangle_over_catalog_X=max(r['motion_triangle_peak_m'] for r in trace)/model.plant.xref,
        maximum_sampled_current_rms_to_budget=max(r['current_rms_a'] for r in trace)/cfg['amp_arms'],
        equilibrium=equilibrium,
        physical_scope='LINEAR_HARMONIC_PLANT_PLUS_ASSUMED_SLOW_THERMAL_NETWORK_NOT_MEASURED_TEMPERATURE')
    return row,trace if entry['candidate_id']=='C02' and frequencies==[20,85] else None


def table(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    cfgpath=ROOT/'dane/konfiguracje/p15b_sprzezenie_Re_T.json';mpath=ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json';ppath=ROOT/'dane/przetworniki/pula_rozszerzona.json'
    cfg=json.loads(cfgpath.read_text());memory=json.loads(mpath.read_text());pool=json.loads(ppath.read_text())['drivers']
    sources=[cfgpath,mpath,ppath,ROOT/'brief_system_audio_DIY_v0.6.md',Path(__file__),ROOT/'skrypty/model_sprzezony_Re_T_P15B.py',ROOT/'skrypty/model_termiczny_P15.py',ROOT/'skrypty/model_cewki_z_pamiecia.py',ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_subwoofera.py',ROOT/'skrypty/model_nieliniowy.py',ROOT/'skrypty/analiza_cewki_z_pamiecia.py',ROOT/'skrypty/sygnaly_P14.py']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    digest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    lockdir=ROOT/'.p15b_locks';lockdir.mkdir(exist_ok=True);guard=(lockdir/(digest+'.lock')).open('a')
    try:fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:guard.close();raise RuntimeError('KoordynatorP15B nadal działa; sprawdzić istniejącą sesję.')
    cache=OUT/'p15b_checkpoint'/digest[:16];cache.mkdir(parents=True,exist_ok=True)
    frozen=OUT/'archiwum'/('P15B_start_'+digest[:16])/'stan_wejsc'
    for p in sources:
        target=frozen/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes(p.read_bytes())
        assert target.read_bytes()==p.read_bytes()
    jobs=[]
    for entry in pool:
        for frequencies in cfg['frequencies_hz']:
            for b in cfg['gvm_family_w_k']:
                for eta in cfg['eddy_fraction_to_coil']:
                    for kv in cfg['forced_convection_w_s_per_k_m']:
                        for envelope in cfg['envelopes']:jobs.append((entry,frequencies,b,eta,kv,envelope,cfg,memory))
    completed={}
    for k in range(len(jobs)):
        p=cache/(f'{k:04d}.json')
        if p.exists():completed[k]=json.loads(p.read_text())
    print('P15B:',len(jobs),'przypadków,',len(completed),'checkpointów',flush=True)
    with ProcessPoolExecutor(max_workers=cfg['workers']) as executor:
        futures={executor.submit(worker,j):k for k,j in enumerate(jobs) if k not in completed}
        for future in as_completed(futures):
            k=futures[future];row,trace=future.result();record=dict(row=row,trace=trace);tmp=cache/(f'{k:04d}.tmp')
            tmp.write_text(json.dumps(record,ensure_ascii=False,allow_nan=False));tmp.replace(cache/(f'{k:04d}.json'));completed[k]=record
            if len(completed)%50==0:print('P15B:',len(completed),'/',len(jobs),row['candidate_id'],flush=True)
    rows=[completed[k]['row'] for k in range(len(jobs))];traces=[]
    for k,r in completed.items():
        if r['trace'] is not None:
            for point in r['trace']:
                traces.append(dict(case_index=k,gvm_w_k=r['row']['gvm_w_k'],eta_eddy_to_coil=r['row']['eta_eddy_to_coil'],
                    forced_g_per_velocity=r['row']['forced_g_per_velocity'],envelope=r['row']['envelope'],**point))
    table(OUT/'p15b_sprzezenie_i_obwiednie.csv',rows);table(OUT/'p15b_przebiegi_C02.csv',traces)
    result=dict(status='P15B_WARUNKOWA_WOLNA_TERMIKA_NIE_MODELE_ZIDENTYFIKOWANYCH_PRODUKTOW',run_sha256=digest,
        input_sha256=hashes,cases=len(rows),trace_rows=len(traces),checkpoint_folder=str(cache.relative_to(ROOT)),
        status_counts={s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})},
        positive_cold_Pcu_slopes=sum(r['cold_pcu_slope_w_k']>0 for r in rows),
        max_heat_balance_relative_error=max(r['max_heat_balance_relative_error'] for r in rows),
        min_cold_time_scale_ratio=min(r['cold_tau_fast_over_forcing_period'] for r in rows),
        scope=cfg['scope'])
    (OUT/'p15b_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));guard.close();return result


if __name__=='__main__':main()
