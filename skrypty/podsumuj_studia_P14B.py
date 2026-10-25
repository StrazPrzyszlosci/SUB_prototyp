"""Wyniki pełnej kampanii: faza, mały sygnał, preload i limity rozruchu."""
import csv
import json
from pathlib import Path
import numpy as np
from projekcja_P14B import ROOT,OUT,read_checkpoints,write_csv
from rozstrzygnij_P14B import load_resolutions
from model_emisji_P14B import pressure_metrics
from model_gazu import Medium
from model_nieliniowy import Plant
from model_subwoofera import Driver


def main():
    raw,h=read_checkpoints()
    if len(raw)!=3312:raise RuntimeError('Kampania nadal niepełna; nie tworzyć końcowego podsumowania')
    rows=load_resolutions(raw,h);cfg=json.loads((ROOT/'dane/konfiguracje/p14b_IMD.json').read_text())
    plants={r['candidate_id']:Plant.from_driver(Driver(**r['model'])) for r in json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']}
    by_id={r['case_id']:(r,a,d) for r,a,d in rows};metrics={};line_map={};result_rows=[];medium=Medium()
    for row,arr,digest in rows:
        if arr is None:continue
        f=np.arange(arr.shape[1])*row['frequency_spacing_hz'];s=2j*np.pi*f
        pressure=medium.rho*s*s*plants[row['candidate_id']].sd*arr[0]*np.exp(-s/medium.c)/(4*np.pi)
        values,lines=pressure_metrics(pressure,f,row,cfg);metrics[row['case_id']]=values;line_map[row['case_id']]=lines
        result_rows.append({**{k:v for k,v in row.items() if k!='band_spectrum_shape'},**{k:v for k,v in values.items() if k!='status'}})
    def anchor(row):
        options=[r for r,a,d in rows if r['group']=='MAIN' and r['candidate_id']==row['candidate_id']
            and r['volume_l']==row['volume_l'] and r['frequencies_hz']==row['frequencies_hz']
            and r['level']==row['level'] and r['profile']==row['profile']]
        if len(options)!=1:raise ValueError('Niejednoznaczny punkt odniesienia')
        return options[0]
    phase=[];preload=[]
    for row,arr,digest in rows:
        if row['group'] not in ('PHASE','PRELOAD'):continue
        base=anchor(row);ba=by_id[base['case_id']][1]
        if arr is None or ba is None:
            if row['group']=='PRELOAD':preload.append(dict(case_id=row['case_id'],anchor_id=base['case_id'],status=row['status'],initial_q=row['initial_q']))
            continue
        if row['group']=='PHASE':
            reference={x['product']:x for x in line_map[base['case_id']]}
            for line in line_map[row['case_id']]:
                point=reference[line['product']]
                if not point['phase_visible'] or not line['phase_visible']:continue
                a=complex(line['phase_reference_real'],line['phase_reference_imag']);b=complex(point['phase_reference_real'],point['phase_reference_imag'])
                phase.append(dict(case_id=row['case_id'],anchor_id=base['case_id'],candidate_id=row['candidate_id'],profile=row['profile'],
                    phase_class=row['phase_class'],product=line['product'],relative_normalized_complex_change=float(abs(a-b)/abs(b)),
                    phase_difference_deg=float(np.angle(a/b,deg=True)),amplitude_change_db=float(20*np.log10(abs(a/b)))))
        else:
            relative=[float(np.linalg.norm(arr[k]-ba[k])/max(np.linalg.norm(ba[k]),1e-30)) for k in (0,1)]
            preload.append(dict(case_id=row['case_id'],anchor_id=base['case_id'],candidate_id=row['candidate_id'],profile=row['profile'],
                initial_q=row['initial_q'],status=row['status'],X_band_complex_relative_change=relative[0],I_band_complex_relative_change=relative[1],
                startup_catalog_x_fraction=row['startup_catalog_x_fraction'],steady_catalog_x_fraction=row['steady_catalog_x_fraction']))
    scaling=[]
    for cid in cfg['small_signal_candidates']:
        for profile in cfg['small_signal_profiles']:
            candidates=[r for r,a,d in rows if r['candidate_id']==cid and r['volume_l']==100 and r['profile']==profile
                and r['frequencies_hz']==[20,85] and r['phase_class']==0 and r['initial_q']==0 and r['level']<=.1 and r['case_id'] in metrics]
            candidates=sorted(candidates,key=lambda r:r['level'])
            for name in ('IM2_pct','IM3_difference_pct'):
                selected=[r for r in candidates if metrics[r['case_id']][name]>1e-6]
                if len(selected)<2:
                    scaling.append(dict(candidate_id=cid,profile=profile,metric=name,status='BELOW_DECLARED_RESOLUTION_FLOOR',points=len(selected)));continue
                x=np.array([r['level'] for r in selected]);y=np.array([metrics[r['case_id']][name] for r in selected])
                slope=float(np.polyfit(np.log(x),np.log(y),1)[0])
                scaling.append(dict(candidate_id=cid,profile=profile,metric=name,status='RESOLVED_LOG_SLOPE',points=len(x),
                                    levels=x.tolist(),slope=slope,expected_small_signal_slope=1 if name=='IM2_pct' else 2))
    write_csv(OUT/'p14b_miary_stacjonarne.csv',result_rows);write_csv(OUT/'p14b_studium_fazy.csv',phase)
    write_csv(OUT/'p14b_studium_preload.csv',preload);write_csv(OUT/'p14b_studium_malego_sygnalu.csv',scaling)
    periodic=[r for r,a,d in rows if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    linear=[r for r in periodic if r['profile']=='LINEAR']
    result=dict(status='P14B_FULL_CONDITIONAL_FAMILY_NOT_DEVICE_THD',dynamic_run_sha256=h,cases=len(rows),
        raw_status_counts={s:sum(r['status']==s for r,a,d in raw) for s in sorted({r['status'] for r,a,d in raw})},
        merged_status_counts={s:sum(r['status']==s for r,a,d in rows) for s in sorted({r['status'] for r,a,d in rows})},
        refinements=sum('resolution_method' in r for r,a,d in rows),
        phase_product_comparisons=len(phase),max_observed_phase_amplitude_change_db=max(abs(r['amplitude_change_db']) for r in phase),
        max_observed_phase_difference_deg=max(abs(r['phase_difference_deg']) for r in phase),
        preload_rows=len(preload),small_signal_fits=scaling,
        max_periodic_energy_relative_residual=max(r['energy_relative_residual'] for r in periodic),
        max_periodic_mean_voltage_identity_error_v=max(abs(r['mean_voltage_identity_error_v']) for r in periodic),
        max_periodic_current_dc_a=max(abs(r['current_dc_a']) for r in periodic),
        max_periodic_startup_X_over_catalog=max(r['startup_catalog_x_fraction'] for r in periodic),
        max_periodic_steady_X_over_catalog=max(r['steady_catalog_x_fraction'] for r in periodic),
        max_linear_stationary_noninput_pct=max(metrics[r['case_id']]['noninput_band_pct'] for r in linear),
        max_periodic_X_tail_RMS_ratio=max(r['x_tail_RMS_ratio'] for r in periodic),
        scope='Wszystkie3312punktów w zadanych rodzinach. Domena/rozruch/faza i małosygnałowe potęgi mają jawne dziedziny. Nie dowód wszystkich gałęzi, globalnych ekstremów ani THD produktów. OgonX nie ogranicza ogona ciśnienia.')
    (OUT/'p14b_studia_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
