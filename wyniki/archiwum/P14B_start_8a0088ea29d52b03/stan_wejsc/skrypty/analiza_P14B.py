"""P14B: porównywalne przypadki puli, pasmowe fazory i atomowe checkpointySQLite."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv
import fcntl
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import shutil
import sqlite3
import zlib
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape,NonlinearModel
from model_cewki_z_pamiecia import MemoryModel,linear_memory_response
from analiza_cewki_z_pamiecia import dynamic_network
from sygnaly_P14 import TonePair,joint_reference,mixing_collisions
from model_wymuszen_P14B import integrate_forcing

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def create_model(entry,volume,profile,cfg,memory):
    p=Plant.from_driver(Driver(**entry['model']))
    if profile=='LINEAR':return NonlinearModel(p,volume,tau_s=cfg['tau_gas_s'],gas_nonlinear=False,q_domain=cfg['q_domain'])
    if profile=='GAS_ONLY':return NonlinearModel(p,volume,tau_s=cfg['tau_gas_s'],q_domain=cfg['q_domain'])
    shape=Shape(**memory['dynamic_shape'])
    if profile=='NL_SIMPLE':return NonlinearModel(p,volume,shape,tau_s=cfg['tau_gas_s'],q_domain=cfg['q_domain'])
    name='FLUX_TWO' if profile=='NL_FLUX_TWO' else 'FLUX_ONE'
    instant,branches,_=dynamic_network(p,name,memory)
    return MemoryModel(p,volume,instant,branches,shape,cfg['tau_gas_s'],q_domain=cfg['q_domain'])


def jobs_list(pool,cfg):
    specs=[]
    def add(entry,volume,pair,level,profile,phase_class,initial_q,group):
        specs.append(dict(case_id=f'{len(specs):06d}',candidate_id=entry['candidate_id'],volume_l=volume,
                          frequencies_hz=pair,level=level,profile=profile,phase_class=phase_class,
                          initial_q=initial_q,group=group))
    for entry in pool:
        for volume in cfg['volumes_l']:
            for pair in cfg['tone_pairs_hz']:
                for level in cfg['levels']:
                    for profile in cfg['profiles']:add(entry,volume,pair,level,profile,0.,0.,'MAIN')
    for entry in pool:
        if entry['candidate_id'] in cfg['phase_study_candidates']:
            for phi in cfg['phase_study_classes']:
                for profile in cfg['phase_study_profiles']:add(entry,cfg['phase_study_volume_l'],cfg['phase_study_pair_hz'],cfg['phase_study_level'],profile,phi,0.,'PHASE')
        if entry['candidate_id'] in cfg['small_signal_candidates']:
            for level in cfg['small_signal_levels']:
                for profile in cfg['small_signal_profiles']:add(entry,100,[20,85],level,profile,0.,0.,'SMALL_SIGNAL')
        if entry['candidate_id'] in cfg['preload_candidates']:
            for pair in cfg['preload_pairs_hz']:
                for profile in cfg['preload_profiles']:
                    for q in cfg['preload_q']:add(entry,cfg['preload_volume_l'],pair,1.,profile,0.,q,'PRELOAD')
    return specs


def worker(job):
    spec,entry,cfg,memory=job;p=Plant.from_driver(Driver(**entry['model']))
    pair0=TonePair(tuple(spec['frequencies_hz']),tuple(cfg['weights_rms']))
    phase2=spec['phase_class']*pair0.phase_period_second_tone()
    pair=TonePair(pair0.frequencies_hz,pair0.weights_rms,(0.,phase2))
    if mixing_collisions(pair.frequencies_hz,3):raise ValueError('Kolizje metryk do3rzędu')
    ref=linear_memory_response(p,spec['volume_l'],pair.frequencies_hz,p.le0,[])
    cap=joint_reference(p,pair0,ref,cfg['amp_vrms'],cfg['amp_arms'])['scale_phase_independent']
    scale=float(spec['level']*cap);model=create_model(entry,spec['volume_l'],spec['profile'],cfg,memory)
    row=dict(**spec,driver=entry['model']['name'],phase2_rad=float(phase2),voltage_scale=scale,
             weights_rms=cfg['weights_rms'],base_hz=pair.base_hz,
             physical_scope='ASSUMED_CURVES_FROZEN_TS_NO_THERMAL_COIL_NO_CLIPPING',
             input_data_gate=entry.get('final_selection_gate','NOT_IDENTIFIED'))
    try:
        result,spectrum=integrate_forcing(model,pair,scale,cfg,initial_q=spec['initial_q'])
        row.update(result)
        if 'x_peak_sampled_m' in result:
            row['steady_catalog_x_fraction']=result['x_peak_sampled_m']/p.xref
            row['startup_catalog_x_fraction']=result['startup_x_observed_m']/p.xref
            row['current_rms_to_reference_budget']=result['current_rms_a']/cfg['amp_arms']
        return row,spectrum
    except (ValueError,RuntimeError,FloatingPointError,OverflowError) as error:
        row.update(status='NUMERICAL_OR_DOMAIN_FAILURE',error=str(error));return row,None


def open_db(path,run_hash):
    connection=sqlite3.connect(path)
    connection.execute('CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS cases(case_id TEXT PRIMARY KEY,row_json TEXT NOT NULL,spectrum BLOB,spectrum_sha256 TEXT)')
    previous=connection.execute('SELECT value FROM metadata WHERE key=?',('run_sha256',)).fetchone()
    if previous:assert previous[0]==run_hash
    else:connection.execute('INSERT INTO metadata VALUES(?,?)',('run_sha256',run_hash));connection.commit()
    return connection


def main():
    config=ROOT/'dane/konfiguracje/p14b_IMD.json';pool_path=ROOT/'dane/przetworniki/pula_rozszerzona.json'
    memory_path=ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json'
    cfg=json.loads(config.read_text());memory=json.loads(memory_path.read_text());pool=json.loads(pool_path.read_text())['drivers']
    by_id={r['candidate_id']:r for r in pool};specs=jobs_list(pool,cfg)
    files=[config,pool_path,memory_path,ROOT/'brief_system_audio_DIY_v0.6.md',Path(__file__),
           ROOT/'skrypty/model_wymuszen_P14B.py',ROOT/'skrypty/model_nieliniowy.py',ROOT/'skrypty/model_cewki_z_pamiecia.py',
           ROOT/'skrypty/sygnaly_P14.py',ROOT/'skrypty/analiza_cewki_z_pamiecia.py',ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_subwoofera.py']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    run_hash=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    lock_dir=ROOT/'.p14b_locks';lock_dir.mkdir(exist_ok=True)
    guard=(lock_dir/f'{run_hash}.lock').open('a')
    try:fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        guard.close();raise RuntimeError('Koordynator tego przebiegu jest nadal aktywny; nie uruchamiać równoległego wznowienia.')
    snapshot=OUT/'archiwum'/f'P14B_start_{run_hash[:16]}'/'stan_wejsc'
    for source in files:
        target=snapshot/source.relative_to(ROOT)
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==hashes[str(source.relative_to(ROOT))]
    dbs={cid:open_db(OUT/f'p14b_{cid}_{run_hash[:12]}.sqlite3',run_hash) for cid in by_id}
    completed={}
    for connection in dbs.values():
        for cid,text in connection.execute('SELECT case_id,row_json FROM cases'):completed[cid]=json.loads(text)
    pending=[s for s in specs if s['case_id'] not in completed]
    print('P14B:',len(specs),'przypadków;',len(completed),'z checkpointów;',len(pending),'nowych',flush=True)
    try:
        # Spawn nie dziedziczy otwartych połączeńSQLite ani stanu integratorów.
        with ProcessPoolExecutor(max_workers=cfg['workers'],mp_context=mp.get_context('spawn')) as executor:
            futures=[executor.submit(worker,(s,by_id[s['candidate_id']],cfg,memory)) for s in pending]
            for future in as_completed(futures):
                row,spectrum=future.result();blob=None;digest=None
                if spectrum is not None:
                    data=np.ascontiguousarray(spectrum,dtype='<c16').tobytes();digest=hashlib.sha256(data).hexdigest();blob=zlib.compress(data,6)
                connection=dbs[row['candidate_id']]
                connection.execute('INSERT INTO cases VALUES(?,?,?,?)',(row['case_id'],json.dumps(row,ensure_ascii=False,allow_nan=False),blob,digest));connection.commit()
                completed[row['case_id']]=row
                if len(completed)%100==0 or len(completed)==len(specs):print('P14B:',len(completed),'/',len(specs),row['candidate_id'],row['status'],flush=True)
    finally:
        for connection in dbs.values():connection.close()
        guard.close()
    rows=[completed[s['case_id']] for s in specs]
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/'p14b_przypadki.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=fields);w.writeheader();w.writerows(rows)
    statuses={s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}
    valid=[r for r in rows if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    result=dict(status='P14B_WYKONANE_RODZINY_NIE_POMIAR_PRODUKTOW',run_sha256=run_hash,input_sha256=hashes,
                cases=len(rows),groups={s:sum(r['group']==s for r in rows) for s in sorted({r['group'] for r in rows})},
                status_counts=statuses,spectral_convention='[X,I]RMSfazorydla f>0; DCbezsqrt2. freqk=k*base/4;0–1000Hz.',
                database_pattern=f'wyniki/p14b_Cxx_{run_hash[:12]}.sqlite3',
                max_periodic_energy_relative_error=max(r['energy_relative_residual'] for r in valid),
                max_periodic_mean_voltage_identity_error_v=max(abs(r['mean_voltage_identity_error_v']) for r in valid),
                max_periodic_current_Parseval_relative_error=max(r['current_Parseval_relative_error'] for r in valid),
                scope='SQLite zawiera atomowo wiersz i pasmowe fazory; hash widma dotyczy niekompresowanych bajtówcomplex128. Działanie checkpointów nie jest niezależnym nowym rachunkiemODE.')
    (OUT/'p14b_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    if statuses.get('NUMERICAL_OR_DOMAIN_FAILURE'):raise RuntimeError('Nierozstrzygnięte błędy numeryczne; sprawdzić zapisane wiersze')
    return result


if __name__=='__main__':main()
