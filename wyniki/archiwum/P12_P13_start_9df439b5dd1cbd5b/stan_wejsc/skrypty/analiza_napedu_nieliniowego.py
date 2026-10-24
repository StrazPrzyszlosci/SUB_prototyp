"""P12/P13: 24 bazy T/S i jawne hipotetyczne rodziny nieliniowości.

Przypadki niezależne w procesach (LSODA nie jest reentrant w wątkach).
Dziennik wyników jest dopisywany; zgodne przypadki nie są liczone ponownie.
"""
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from model_subwoofera import Driver
from model_gazu import ThermalSpectrum,gas_response
from model_nieliniowy import Plant,Shape,NonlinearModel,simulate_sine

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'


def worker(job):
    cid,entry,volume,f,level,profile,cfg=job
    d=Driver(**entry['model']);plant=Plant.from_driver(d)
    linear=gas_response(d,volume,[f],ThermalSpectrum((cfg['tau_s'],),(1.,)),vrms=1.,solid_angle=4*np.pi)
    limits=[cfg['reference_amplifier_vrms'],cfg['reference_amplifier_arms']/linear['i_rms_a'][0],
            d.xmax_mm*1e-3/linear['x_peak_m'][0]]
    voltage=float(level*min(limits))
    model=NonlinearModel(plant,volume,Shape(**profile['shape']),cfg['tau_s'],profile['gas_nonlinear'],q_domain=cfg['q_domain'])
    row=dict(case_id=cid,candidate_id=entry['candidate_id'],driver=d.name,volume_l=volume,f_hz=f,
             reference_envelope_fraction=level,profile=profile['id'],voltage_rms_v=voltage,
             linear_reference_limit=['voltage','current','catalog_x'][int(np.argmin(limits))],
             linear_x_peak_m=float(linear['x_peak_m'][0]*voltage),
             linear_current_rms_a=float(linear['i_rms_a'][0]*voltage),
             linear_SPL_4pi_1m_rms_db=float(linear['spl_equivalent_db'][0]+20*np.log10(voltage)),
             family_scope='HYPOTHETICAL_SHAPE_NOT_PRODUCT_MEASUREMENT',initial_branch='ZERO_INITIAL_STATE_SINE_PHASE_ZERO')
    try:
        result=simulate_sine(model,f,voltage,cycles=cfg['cycles_initial'],max_cycles=cfg['cycles_maximum'],
                             samples_per_cycle=cfg['samples_per_cycle'],method=cfg['solver'],
                             rtol=cfg['rtol'],atol=cfg['atol'],closure_tolerance=cfg['sampled_cycle_closure_tolerance'])
        row.update(result)
        if 'x_peak_m' in result:
            row['actual_fraction_of_catalog_x']=result['x_peak_m']/(d.xmax_mm*1e-3)
            row['actual_current_to_reference_budget']=result['current_rms_a']/cfg['reference_amplifier_arms']
            row['exceeds_reference_catalog_x']=bool(row['actual_fraction_of_catalog_x']>1)
            row['exceeds_reference_current_budget']=bool(row['actual_current_to_reference_budget']>1)
            row['fundamental_compression_relative_to_linear_db']=result['spl_fundamental_equivalent_4pi_1m_db']-row['linear_SPL_4pi_1m_rms_db']
    except (ValueError,RuntimeError,OverflowError,FloatingPointError) as error:
        row.update(status='NUMERICAL_OR_DOMAIN_FAILURE',error=str(error))
    return row


def main():
    cfg_path=ROOT/'dane/konfiguracje/p12_p13_naped_i_gaz.json'
    cfg=json.loads(cfg_path.read_text())
    pool_path=ROOT/'dane/przetworniki/pula_rozszerzona.json'
    raw=json.loads(pool_path.read_text())['drivers']
    inputs=[cfg_path,pool_path,ROOT/'brief_system_audio_DIY_v0.6.md',Path(__file__),
            ROOT/'skrypty/model_nieliniowy.py',ROOT/'skrypty/model_subwoofera.py',ROOT/'skrypty/model_gazu.py']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    run_hash=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    snapshot=OUT/'archiwum'/f'P12_P13_start_{run_hash[:16]}'/'stan_wejsc'
    for source in inputs:
        target=snapshot/source.relative_to(ROOT)
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==hashes[str(source.relative_to(ROOT))]
    journal=OUT/f'p12_p13_przebieg_{run_hash[:16]}.jsonl'
    completed={}
    if journal.exists():
        with journal.open() as handle:
            for line in handle:
                record=json.loads(line)
                assert record['run_sha256']==run_hash
                row=record['row'];completed[row['case_id']]=row
    jobs=[];index=0
    for entry in raw:
        for volume in cfg['volumes_l']:
            for frequency in cfg['frequencies_hz']:
                for level in cfg['reference_envelope_fractions']:
                    for profile in cfg['profiles']:
                        cid=f'{index:06d}';index+=1
                        if cid not in completed:jobs.append((cid,entry,volume,frequency,level,profile,cfg))
    print('P12/P13:',index,'przypadków;',len(completed),'z dziennika;',len(jobs),'do obliczenia',flush=True)
    with journal.open('a') as handle:
        with ProcessPoolExecutor(max_workers=cfg['workers']) as executor:
            futures=[executor.submit(worker,job) for job in jobs]
            for future in as_completed(futures):
                row=future.result();completed[row['case_id']]=row
                handle.write(json.dumps(dict(run_sha256=run_hash,row=row),ensure_ascii=False,allow_nan=False)+'\n')
                handle.flush()
                if len(completed)%100==0 or len(completed)==index:
                    print('P12/P13:',len(completed),'/',index,'ostatni',row['candidate_id'],row['status'],flush=True)
    assert len(completed)==index
    rows=[completed[f'{j:06d}'] for j in range(index)]
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/'p12_p13_naped_i_gaz.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    statuses={status:sum(r['status']==status for r in rows) for status in sorted({r['status'] for r in rows})}
    valid=[r for r in rows if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    linear=[r for r in valid if r['profile']=='LINEAR_REF']
    nonlinear=[r for r in valid if r['profile']!='LINEAR_REF']
    result=dict(status='WYKONANE_RODZINY_WARUNKOWE_NIE_RANKING_THD_PRODUKTOW',run_sha256=run_hash,
                input_sha256=hashes,journal=str(journal.relative_to(ROOT)),drivers=len(raw),rows=len(rows),
                profiles=len(cfg['profiles']),status_counts=statuses,
                max_valid_relative_energy_residual=max(r['energy_relative_residual'] for r in valid),
                max_linear_fundamental_relative_error=max(abs(r['x_fundamental_peak_m']/r['linear_x_peak_m']-1) for r in linear),
                max_linear_numerical_pressure_THD_pct=max(r['thd_pressure_h2_h10_pct'] for r in linear),
                nonlinear_cases_exceed_catalog_x=sum(r['exceeds_reference_catalog_x'] for r in nonlinear),
                nonlinear_cases_exceed_reference_current=sum(r['exceeds_reference_current_budget'] for r in nonlinear),
                max_absolute_dc_offset_mm=max(abs(r['x_dc_m'])*1000 for r in nonlinear),
                max_hypothetical_pressure_THD_pct=max(r['thd_pressure_h2_h10_pct'] for r in nonlinear),
                scope='24 katalogowe bazy i umowne kształty. Nie zidentyfikowano BL/Kms/Le/Rms(v) tych egzemplarzy. Punktowy skan i start od zera nie badają wszystkich gałęzi ani stabilności Floqueta.',
                coupling_scope='Brak dodatkowej reakcji frontu, przecieku i termiki cewki. Pole monopola jest normalizacją diagnostyczną, nie modelem faktycznej kierunkowości harmonicznych.')
    (OUT/'p12_p13_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    if statuses.get('NUMERICAL_OR_DOMAIN_FAILURE'):raise RuntimeError('Są nierozstrzygnięte błędy solvera/dziedziny; sprawdzić zapisane przypadki')
    return result


if __name__=='__main__':main()
