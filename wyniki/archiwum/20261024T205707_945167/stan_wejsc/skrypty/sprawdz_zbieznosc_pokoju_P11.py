"""P11: odrębna zbieżność przestrzenna dla ekstremalnych znalezionych przypadków.

Gęstsza siatka f nie weryfikuje ucięcia sumy modów. Tutaj zmieniamy kmax.
Jest to kontrola wybranych świadków; nie certyfikat całej dziedziny ciągłej.
"""
import csv
import json
from pathlib import Path
import numpy as np
from model_gazu import Medium
from model_subwoofera import Driver
from model_pokoju import ModalRoom
from analiza_scian_i_sprzezen import room_case
from analiza_promieniowania import table

ROOT=Path(__file__).resolve().parents[1]


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p11_promieniowanie.json').read_text())
    geo=json.loads((ROOT/'dane/konfiguracje/pokoj_odsluchowy.json').read_text())
    p26=json.loads((ROOT/'dane/konfiguracje/p26_scenariusze.json').read_text())
    dense=json.loads((ROOT/'wyniki/p11_pokoj_gesty_skan.json').read_text())
    with (ROOT/'wyniki/p11_pokoj_geste_podsumowania.csv').open() as h:
        summaries=list(csv.DictReader(h))
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    ds={r['candidate_id']:Driver(**r['model']) for r in raw}
    medium=Medium();room=ModalRoom((geo['width_x_m'],geo['length_y_m'],geo['height_z_m']),medium.c,medium.rho)
    sigma=cfg['room_source_sigma_m'];rows=[]
    for case in dense['refinements']:
        setup=next(r for r in p26['source_sets'] if r['id']==case['source_set'])
        matched=next(r for r in summaries if r['candidate_id']==case['candidate_id']
                     and r['source_set']==case['source_set'] and float(r['volume_l'])==case['volume_l']
                     and float(r['modal_t60_s'])==case['modal_t60_s'] and float(r['zero_tau_s'])==case['zero_tau_s']
                     and int(r['source_count'])==case['source_count'])
        peaks=[float(matched[k]) for k in ['f_max_perturbation_hz','f_max_velocity_change_hz','f_max_pressure_feedback_hz']]
        f=np.unique(np.concatenate([cfg['frequencies_hz'],peaks,np.array(peaks)+.05,np.array(peaks)-.05]))
        f=f[(f>=20)&(f<=80)];n=case['source_count'];positions=setup['positions_xyz_m'][:n]
        results=[]
        for kmax in [40.,60.]:
            port=room.transfer(f,positions,positions,case['modal_t60_s'],case['zero_tau_s'],sigma,sigma,kmax)
            observer=room.transfer(f,positions,[p26['assumed_listener_xyz_m']],case['modal_t60_s'],case['zero_tau_s'],sigma,cfg['room_receiver_sigma_m'],kmax)
            motor,out,ow,p,p0,bounds=room_case(ds[case['candidate_id']],case['volume_l'],f,port,observer,sigma,medium)
            results.append((port,p,p0,np.array([x[0] for x in bounds]),observer))
        low,high=results
        for j,frequency in enumerate(f):
            feedback_lo=20*np.log10(abs(low[1][j,0]/low[2][j,0]))
            feedback_hi=20*np.log10(abs(high[1][j,0]/high[2][j,0]))
            rows.append(dict(metric_witness=case['metric'],candidate_id=case['candidate_id'],
                             volume_l=case['volume_l'],source_set=case['source_set'],f_hz=float(frequency),
                             relative_port_difference=float(np.linalg.norm(low[0][j]-high[0][j])/np.linalg.norm(high[0][j])),
                             relative_observer_difference=float(np.linalg.norm(low[4][j]-high[4][j])/max(np.linalg.norm(high[4][j]),1e-300)),
                             relative_coupled_pressure_difference=float(abs(low[1][j,0]-high[1][j,0])/max(abs(high[1][j,0]),1e-300)),
                             absolute_coupled_SPL_difference_db=float(abs(20*np.log10(abs(low[1][j,0]/high[1][j,0])))),
                             absolute_feedback_difference_db=float(abs(feedback_hi-feedback_lo)),
                             absolute_perturbation_norm_difference=float(abs(low[3][j]-high[3][j]))))
    table('p11_pokoj_zbieznosc_przestrzenna.csv',rows)
    result=dict(status='KONTROLA_WYBRANYCH_SWIADKOW_KMAX40_60',points=len(rows),
                max_relative_port_difference=max(r['relative_port_difference'] for r in rows),
                max_relative_observer_difference=max(r['relative_observer_difference'] for r in rows),
                max_relative_coupled_pressure_difference=max(r['relative_coupled_pressure_difference'] for r in rows),
                max_abs_coupled_SPL_difference_db=max(r['absolute_coupled_SPL_difference_db'] for r in rows),
                max_abs_feedback_difference_db=max(r['absolute_feedback_difference_db'] for r in rows),
                max_abs_perturbation_difference=max(r['absolute_perturbation_norm_difference'] for r in rows),
                scope='Wybrane maksima i punkty sąsiednie; nie walidacja fizyczna ani globalny certyfikat błędu.')
    (ROOT/'wyniki/p11_pokoj_zbieznosc_przestrzenna.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
