"""P12C: rozstrzygnięcie 17flag i wybranych świadków niezależnym solverem."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape
from model_cewki_z_pamiecia import MemoryModel,blocked_impedance,simulate_memory_sine
from analiza_cewki_z_pamiecia import dynamic_network,table

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL='RADAU_rtol3e-11_atol3e-13_1024samples_256cycles_tol1e-9'


def refine(job):
    row,raw,cfg=job
    plant=Plant.from_driver(Driver(**raw['model']))
    instant,bs,realization=dynamic_network(plant,row['profile'],cfg)
    model=MemoryModel(plant,float(row['volume_l']),instant,bs,Shape(**cfg['dynamic_shape']),
                      cfg['thermal_tau_s'],q_domain=cfg['dynamic_q_domain'],realization=realization)
    result=simulate_memory_sine(model,float(row['f_hz']),float(row['voltage_rms_v']),
                                cycles=24,max_cycles=256,samples_per_cycle=1024,
                                method='Radau',rtol=3e-11,atol=3e-13,closure_tolerance=1e-9)
    merged=row.copy();merged.update(result)
    merged.update(original_status=row['status'],refinement_protocol=PROTOCOL)
    if 'x_peak_m' in result:merged['actual_fraction_of_catalog_x']=result['x_peak_m']/plant.xref
    return merged


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    summary=json.loads((ROOT/'wyniki/p12c_podsumowanie.json').read_text())
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    by_id={r['candidate_id']:r for r in raw}
    with (ROOT/'wyniki/p12c_nieliniowa_pamiec.csv').open() as handle:rows=list(csv.DictReader(handle))
    assert len(rows)==24*3*3*2*4==summary['dynamic_rows']
    selected={r['case_id']:r for r in rows if r['status']!='PERIODIC_WITHIN_MODEL_TOLERANCE'}
    valid=[r for r in rows if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    for key in ['energy_relative_residual','h2_pressure_pct','x_dc_m']:
        r=max(valid,key=lambda x:abs(float(x[key])));selected[r['case_id']]=r
    target=ROOT/'wyniki/p12c_kontrola_pakietu.json';cache=json.loads(target.read_text()) if target.exists() else {}
    if cache.get('main_run_sha256')!=summary['run_sha256'] or cache.get('protocol')!=PROTOCOL:cache={}
    existing={r['case_id']:r for r in cache.get('refined_cases',[])}
    jobs=[(r,by_id[r['candidate_id']],cfg) for cid,r in selected.items() if cid not in existing]
    refined=dict(existing)
    with ProcessPoolExecutor(max_workers=cfg['workers']) as executor:
        for future in as_completed([executor.submit(refine,job) for job in jobs]):
            result=future.result();refined[result['case_id']]=result
            print('P12C Radau:',result['case_id'],result['original_status'],'->',result['status'],flush=True)
    checked=[refined.get(r['case_id'],r) for r in rows]
    statuses={s:sum(r['status']==s for r in checked) for s in sorted({r['status'] for r in checked})}
    table('p12c_nieliniowa_pamiec_zweryfikowana.csv',checked)
    same_ref_error=0.
    for entry in raw:
        p=Plant.from_driver(Driver(**entry['model']))
        l1,b1,_=dynamic_network(p,'FLUX_ONE',cfg);l2,b2,_=dynamic_network(p,'FLUX_TWO',cfg)
        z1=blocked_impedance([cfg['reference_hz']],p.re,l1,b1)[0]
        z2=blocked_impedance([cfg['reference_hz']],p.re,l2,b2)[0]
        same_ref_error=max(same_ref_error,float(abs(z1/z2-1)))
    assert same_ref_error<1e-11
    paired=[]
    for r in checked:
        if r['profile']!='FLUX_ONE' or r['status']!='PERIODIC_WITHIN_MODEL_TOLERANCE':continue
        other=next(x for x in checked if x['candidate_id']==r['candidate_id'] and x['volume_l']==r['volume_l']
                   and x['f_hz']==r['f_hz'] and x['reference_envelope_fraction']==r['reference_envelope_fraction'] and x['profile']=='NAIVE_ONE')
        if other['status']!='PERIODIC_WITHIN_MODEL_TOLERANCE':continue
        paired.append(dict(candidate_id=r['candidate_id'],volume_l=float(r['volume_l']),f_hz=float(r['f_hz']),
                           reference_envelope_fraction=float(r['reference_envelope_fraction']),
                           absolute_h2_difference_percentage_points=abs(float(r['h2_pressure_pct'])-float(other['h2_pressure_pct'])),
                           fundamental_difference_db=float(r['spl_fundamental_equivalent_4pi_1m_db'])-float(other['spl_fundamental_equivalent_4pi_1m_db'])))
    table('p12c_sila_FLUX_vs_NAIVE.csv',paired)
    valid=[r for r in checked if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    loss_split_error=max(abs(float(r['mean_structural_plus_eddy_loss_w'])-float(r['mean_structural_loss_w'])-float(r['mean_eddy_loss_w'])) for r in valid)
    assert loss_split_error<1e-8
    with (ROOT/'wyniki/p12c_liniowy_naped.csv').open() as handle:linear=list(csv.DictReader(handle))
    references={(r['candidate_id'],r['volume_l'],r['f_hz']):r for r in linear if r['scenario']=='SIMPLE'}
    motion_rows=0;motion_delta=0.
    for row in linear:
        ref=references[(row['candidate_id'],row['volume_l'],row['f_hz'])]
        plant=Plant.from_driver(Driver(**by_id[row['candidate_id']]['model']))
        def active_x(r):
            scale=plant.xref/float(r['x_peak_1v_m'])
            return scale<=cfg['amp_vrms']*(1+1e-12) and scale*float(r['current_1v_rms_a'])<=cfg['amp_arms']*(1+1e-12)
        if active_x(row) and active_x(ref):
            motion_rows+=1;motion_delta=max(motion_delta,abs(float(row['capacity_X1_delta_vs_simple_db'])))
    assert motion_rows>0 and motion_delta<1e-10
    max_energy=max(float(r['energy_relative_residual']) for r in valid)
    assert max_energy<1e-5
    result=dict(status='KONTROLA_TABEL_I_WYBRANYCH_ZAGESZCZEN_NIE_GLOBALNY_CERTYFIKAT',
                main_run_sha256=summary['run_sha256'],protocol=PROTOCOL,original_status_counts=summary['dynamic_status_counts'],
                refined_cases=list(refined.values()),final_status_counts=statuses,
                matched_complex_reference_max_relative_error=same_ref_error,
                paired_force_cases=len(paired),max_H2_pair_difference_pp=max(r['absolute_h2_difference_percentage_points'] for r in paired),
                max_absolute_fundamental_pair_difference_db=max(abs(r['fundamental_difference_db']) for r in paired),
                max_relative_energy_residual=max_energy,
                max_loss_split_absolute_error_w=loss_split_error,
                comparable_linear_motion_limited_rows=motion_rows,max_linear_motion_limit_change_db=motion_delta,
                scope='Wszystkie flagi i wybrane świadki. Nie badano wszystkich gałęzi ani wszystkich maksimów między próbkami. NAIVE to kontrola, nie model wybranego głośnika.')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in result.items() if k!='refined_cases'},ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
