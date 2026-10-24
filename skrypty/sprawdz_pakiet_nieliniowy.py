"""P12/P13: kontrola tabel i niezależne zagęszczenie znalezionych świadków."""
import csv
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape,NonlinearModel,simulate_sine

ROOT=Path(__file__).resolve().parents[1]


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p12_p13_naped_i_gaz.json').read_text())
    summary=json.loads((ROOT/'wyniki/p12_p13_podsumowanie.json').read_text())
    with (ROOT/'wyniki/p12_p13_naped_i_gaz.csv').open() as handle:rows=list(csv.DictReader(handle))
    assert len(rows)==24*4*7*2*9==summary['rows']
    assert len({r['case_id'] for r in rows})==len(rows)
    valid=[r for r in rows if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    linear=[r for r in valid if r['profile']=='LINEAR_REF']
    assert len(linear)==24*4*7*2
    assert not any(r['status']=='NUMERICAL_OR_DOMAIN_FAILURE' for r in rows)
    for r in valid:
        assert float(r['closure_error'])<=cfg['sampled_cycle_closure_tolerance']
        assert float(r['voltage_rms_v'])<=cfg['reference_amplifier_vrms']
        assert float(r['linear_current_rms_a'])<=cfg['reference_amplifier_arms']*(1+1e-12)
        assert min(float(r[k]) for k in ['mean_copper_w','mean_mechanical_loss_w','mean_thermal_exergy_loss_w'])>=0
        assert float(r['max_gas_temperature_k'])>0
    # Progi dotyczą precyzji modelu numerycznego, nie wymagań THD produktu.
    assert summary['max_linear_fundamental_relative_error']<2e-5
    assert summary['max_valid_relative_energy_residual']<1e-4
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers={r['candidate_id']:Driver(**r['model']) for r in raw}
    witnesses={}
    cache_path=ROOT/'wyniki/p12_p13_kontrola_pakietu.json'
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    if cache.get('main_run_sha256')!=summary['run_sha256']:cache={}
    previous={r['case_id']:r for r in cache.get('refinements',[])}
    for metric in ['energy_relative_residual','thd_pressure_h2_h10_pct','x_dc_m']:
        row=max(valid,key=lambda r:abs(float(r[metric])))
        witnesses.setdefault(row['case_id'],(row,[]))[1].append(metric)
    row=max(linear,key=lambda r:float(r['thd_pressure_h2_h10_pct']))
    witnesses.setdefault(row['case_id'],(row,[]))[1].append('linear_numerical_harmonic_floor')
    refinements=[]
    for row,metrics in witnesses.values():
        if row['case_id'] in previous:
            entry=previous[row['case_id']].copy();entry['metrics']=metrics;refinements.append(entry)
            continue
        profile=next(p for p in cfg['profiles'] if p['id']==row['profile'])
        model=NonlinearModel(Plant.from_driver(drivers[row['candidate_id']]),float(row['volume_l']),
                             Shape(**profile['shape']),cfg['tau_s'],profile['gas_nonlinear'],q_domain=cfg['q_domain'])
        refined=simulate_sine(model,float(row['f_hz']),float(row['voltage_rms_v']),method='Radau',
                              rtol=1e-10,atol=1e-12,samples_per_cycle=1024,closure_tolerance=1e-8)
        assert refined['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE',refined
        refinements.append(dict(case_id=row['case_id'],candidate_id=row['candidate_id'],profile=row['profile'],
                                volume_l=float(row['volume_l']),f_hz=float(row['f_hz']),metrics=metrics,
                                relative_fundamental_difference=abs(refined['x_fundamental_peak_m']/float(row['x_fundamental_peak_m'])-1),
                                absolute_h2_percentage_point_difference=abs(refined['h2_pressure_pct']-float(row['h2_pressure_pct'])),
                                absolute_h3_percentage_point_difference=abs(refined['h3_pressure_pct']-float(row['h3_pressure_pct'])),
                                absolute_x_dc_difference_m=abs(refined['x_dc_m']-float(row['x_dc_m'])),
                                coarse_thd_pct=float(row['thd_pressure_h2_h10_pct']),
                                refined_thd_pct=refined['thd_pressure_h2_h10_pct'],
                                refined_energy_relative_residual=refined['energy_relative_residual']))
        print('P12/P13 kontrola świadka:',row['case_id'],metrics,flush=True)
    domain=[]
    previous_domain={r['case_id']:r for r in cache.get('domain_crossings',[])}
    for row in rows:
        if row['status']!='MODEL_DOMAIN_EXCEEDED':continue
        if row['case_id'] in previous_domain:
            domain.append(previous_domain[row['case_id']]);continue
        profile=next(p for p in cfg['profiles'] if p['id']==row['profile'])
        model=NonlinearModel(Plant.from_driver(drivers[row['candidate_id']]),float(row['volume_l']),
                             Shape(**profile['shape']),cfg['tau_s'],profile['gas_nonlinear'],q_domain=cfg['q_domain'])
        refined=simulate_sine(model,float(row['f_hz']),float(row['voltage_rms_v']),method='DOP853',
                              rtol=1e-10,atol=1e-12,samples_per_cycle=512)
        assert refined['status']=='MODEL_DOMAIN_EXCEEDED',refined
        domain.append(dict(case_id=row['case_id'],candidate_id=row['candidate_id'],profile=row['profile'],
                           coarse_stop_cycles=float(row['end_cycles']),refined_stop_cycles=refined['end_cycles'],
                           absolute_stop_cycle_difference=abs(refined['end_cycles']-float(row['end_cycles']))))
    resolutions=[]
    for row in rows:
        if row['status']!='NOT_SETTLED':continue
        profile=next(p for p in cfg['profiles'] if p['id']==row['profile'])
        model=NonlinearModel(Plant.from_driver(drivers[row['candidate_id']]),float(row['volume_l']),
                             Shape(**profile['shape']),cfg['tau_s'],profile['gas_nonlinear'],q_domain=cfg['q_domain'])
        refined=simulate_sine(model,float(row['f_hz']),float(row['voltage_rms_v']),method='Radau',max_cycles=128,
                              rtol=1e-10,atol=1e-12,samples_per_cycle=1024,closure_tolerance=1e-8)
        resolutions.append(dict(case_id=row['case_id'],candidate_id=row['candidate_id'],
                                original_status=row['status'],original_closure_error=float(row['closure_error']),
                                refined_method='Radau_rtol1e-10_atol1e-12_1024samples_max128cycles',**refined))
        print('P12/P13 rozstrzygnięcie:',row['case_id'],refined['status'],flush=True)
    result=dict(status='PASS_TABEL_I_WYBRANYCH_ZAGESZCZEN_NIE_CERTYFIKAT_CALEJ_DZIEDZINY',
                main_run_sha256=summary['run_sha256'],rows_checked=len(rows),periodic_rows=len(valid),
                refinements=refinements,domain_crossings=domain,unsettled_resolutions=resolutions,
                max_linear_numerical_pressure_thd_pct=summary['max_linear_numerical_pressure_THD_pct'],
                limits='Kontrola znalezionych świadków, nie dowód globalnego maksimum, tolerancji produktu ani wszystkich gałęzi stabilnych.')
    (ROOT/'wyniki/p12_p13_kontrola_pakietu.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
