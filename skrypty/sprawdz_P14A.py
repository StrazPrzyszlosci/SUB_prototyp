"""P14A: fazy, kolizje, osłona szczytu, oracle LTI i niezależne Radau."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape
from model_cewki_z_pamiecia import MemoryModel,linear_memory_response
from analiza_cewki_z_pamiecia import dynamic_network
from analiza_P14A_sygnaly import two_tone
from sygnaly_P14 import TonePair,mixing_collisions,sampled_peak_enclosure

ROOT=Path(__file__).resolve().parents[1]


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p14a_sygnaly_i_pilot.json').read_text())
    memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    pool=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers={r['candidate_id']:Driver(**r['model']) for r in pool}
    phase=np.linspace(0,2*np.pi,4096,endpoint=False)
    equivalent=0.
    for freqs in cfg['tone_pairs_hz']:
        pair=TonePair(tuple(freqs));n1,n2=map(int,pair.orders)
        shift=2*np.pi*pow(n2,-1,n1)/n1
        other=TonePair(tuple(freqs),phases_rad=(0.,pair.phase_period_second_tone()))
        equivalent=max(equivalent,float(max(abs(other.value(phase)-pair.value(phase+shift)))))
        assert not mixing_collisions(freqs)
    assert equivalent<1e-11 and mixing_collisions([20,80])
    random=np.random.default_rng(20261025);peak_checks=0
    for _ in range(24):
        phasors=np.exp(1j*random.uniform(0,2*np.pi,2))*random.uniform(.1,2,2)
        low,upper,_=sampled_peak_enclosure(phasors,[4,17],1024)
        dense,_,_=sampled_peak_enclosure(phasors,[4,17],16384)
        assert low<=dense*(1+1e-12) and dense<=upper*(1+1e-12)
        peak_checks+=1
    with (ROOT/'wyniki/p14a_pilot_IMD.csv').open() as h:rows=list(csv.DictReader(h))
    assert len(rows)==12 and all(r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE' for r in rows)
    linear_error=0.
    for r in rows:
        if r['profile']!='LINEAR':continue
        p=Plant.from_driver(drivers[r['candidate_id']])
        ref=linear_memory_response(p,cfg['pilot_volume_l'],cfg['pilot_pair_hz'],p.le0,[])
        for k in [0,1]:
            expected=abs(ref['pressure_equivalent_pa'][k])*float(r['voltage_scale'])*cfg['pilot_weights'][k]
            linear_error=max(linear_error,abs(float(r[f'fundamental{k+1}_rms_pa'])/expected-1))
    assert linear_error<1e-6,linear_error
    original=next(r for r in rows if r['candidate_id']=='C02' and r['profile']=='NL_FLUX_ONE' and float(r['phase2_rad'])==0)
    p=Plant.from_driver(drivers['C02']);instant,branches,_=dynamic_network(p,'FLUX_ONE',memory)
    model=MemoryModel(p,cfg['pilot_volume_l'],instant,branches,Shape(**memory['dynamic_shape']),cfg['tau_gas_s'])
    pair=TonePair(tuple(cfg['pilot_pair_hz']),tuple(cfg['pilot_weights']))
    refined=two_tone(model,pair,float(original['voltage_scale']),cfg,method='Radau')
    assert refined['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE'
    diff=max(abs(refined[k]-float(original[k])) for k in ['IM2_diagnostic_pct','IM3_difference_diagnostic_pct'])
    assert diff<2e-4,diff
    input_files=[ROOT/'brief_system_audio_DIY_v0.6.md',ROOT/'dane/konfiguracje/p14a_sygnaly_i_pilot.json',
                 ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'skrypty/sygnaly_P14.py',
                 ROOT/'skrypty/analiza_P14A_sygnaly.py',ROOT/'skrypty/model_nieliniowy.py',
                 ROOT/'skrypty/model_cewki_z_pamiecia.py']
    result=dict(status='PASS_PILOTU_I_ODNIESIENIA_NIE_ZAMKNIECIE_P14',
                input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_files},
                max_equivalent_phase_waveform_error=equivalent,peak_enclosure_checks=peak_checks,
                max_linear_oracle_relative_error=linear_error,independent_Radau_IM_difference_pp=diff,
                max_pilot_relative_energy_residual=max(float(r['energy_relative_residual']) for r in rows),
                linear_numerical_distortion_floor_pct=max(float(r['all_noninput_lines_in_band_pct']) for r in rows if r['profile']=='LINEAR'),
                scope='Osłona błędu próbkowania dotyczy ustalonych współczynników LTI, nie całej niepewności fizycznej. IMD to jawnie zdefiniowana diagnostyka, nie deklaracja zgodności z normą.')
    (ROOT/'wyniki/p14a_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
