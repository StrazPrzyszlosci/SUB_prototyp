"""Odrębny Radau i zbieżność emisji wybranych dużych odpowiedzi P14B."""
import hashlib
import json
from pathlib import Path
import numpy as np
from projekcja_P14B import ROOT,OUT,read_checkpoints
from rozstrzygnij_P14B import load_resolutions
from analiza_P14B import create_model
from model_wymuszen_P14B import integrate_forcing
from sygnaly_P14 import TonePair
from model_emisji_P14B import moving_monopole,pressure_metrics
from model_subwoofera import Driver
from model_nieliniowy import Plant
from model_gazu import Medium


def main():
    rows,h=read_checkpoints()
    if len(rows)!=3312:raise RuntimeError('P14B nie jest zakończone')
    rows=load_resolutions(rows,h)
    cfg=json.loads((ROOT/'dane/konfiguracje/p14b_IMD.json').read_text());g=json.loads((ROOT/'dane/konfiguracje/p14b_emisja.json').read_text());memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    entries={r['candidate_id']:r for r in json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']}
    valid=[(r,a,d) for r,a,d in rows if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    selected=[max(valid,key=lambda t:t[0]['steady_catalog_x_fraction']),max(valid,key=lambda t:t[0]['energy_relative_residual']),
              max(valid,key=lambda t:t[0]['startup_catalog_x_fraction']),next(t for t in valid if t[0]['case_id']=='000223')]
    selected={r['case_id']:(r,a,d) for r,a,d in selected};comparisons=[];convergence=[];arrays=[];medium=Medium()
    verifier_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    cache=OUT/'p14b_wybrane_radau'/verifier_sha[:16];cache.mkdir(exist_ok=True,parents=True)
    for cid,(row,arr,digest) in selected.items():
        checkpoint=cache/(cid+'.json');saved=cache/(cid+'.npz')
        if checkpoint.exists() and saved.exists():
            prior=json.loads(checkpoint.read_text())
            assert prior['dynamic_run_sha256']==h and prior['raw_spectrum_sha256']==digest
            assert prior['verifier_sha256']==verifier_sha
            assert hashlib.sha256(saved.read_bytes()).hexdigest()==prior['array_file_sha256']
            comparisons.append(prior['comparison']);convergence.append(prior['convergence']);arrays.append(np.load(saved,allow_pickle=False)['spectrum'])
            print('P14B zgodny checkpointRadau:',cid,flush=True);continue
        print('P14B rozpoczynamRadau:',cid,row['candidate_id'],row['profile'],flush=True)
        entry=entries[row['candidate_id']];p=Plant.from_driver(Driver(**entry['model']))
        model=create_model(entry,row['volume_l'],row['profile'],cfg,memory)
        pair=TonePair(tuple(row['frequencies_hz']),tuple(row['weights_rms']),(0.,row['phase2_rad']))
        refined,other=integrate_forcing(model,pair,row['voltage_scale'],cfg,method='Radau',initial_q=row['initial_q'],refine=True)
        if refined['status']!='PERIODIC_WITHIN_MODEL_TOLERANCE':raise AssertionError((cid,refined))
        error=[float(np.linalg.norm(arr[k]-other[k])/max(np.linalg.norm(other[k]),1e-30)) for k in (0,1)]
        f=np.arange(arr.shape[1])*row['frequency_spacing_hz'];s=2j*np.pi*f
        transfer=medium.rho*s*s*p.sd*np.exp(-s/medium.c)/(4*np.pi)
        first,_=pressure_metrics(transfer*arr[0],f,row,cfg);second,_=pressure_metrics(transfer*other[0],f,row,cfg)
        delta=max(abs(first[key]-second[key]) for key in ('IM2_pct','IM3_difference_pct','noninput_band_pct'))
        assert max(error)<5e-6 and delta<1e-4,(cid,error,delta)
        comparisons.append(dict(case_id=cid,candidate_id=row['candidate_id'],profile=row['profile'],raw_spectrum_sha256=digest,
            X_band_complex_relative_error=error[0],I_band_complex_relative_error=error[1],max_IM_difference_percentage_points=delta,
            refined=refined))
        arrays.append(other)
        pressures=[];diagnostics=[]
        for factor in (2,4,8):
            pressure,diag=moving_monopole(other[0],f,p.sd,g,oversampling=factor);pressures.append(pressure);diagnostics.append(diag)
        e24=float(np.linalg.norm(pressures[0]-pressures[1])/np.linalg.norm(pressures[1]));e48=float(np.linalg.norm(pressures[1]-pressures[2])/np.linalg.norm(pressures[2]))
        vals=[pressure_metrics(pr,f,row,cfg)[0] for pr in pressures]
        im24=max(abs(vals[0][key]-vals[1][key]) for key in ('IM2_pct','IM3_difference_pct'))
        im48=max(abs(vals[1][key]-vals[2][key]) for key in ('IM2_pct','IM3_difference_pct'))
        assert e24<2e-5 and e48<2e-6 and im48<1e-3,(cid,e24,e48,im48)
        convergence.append(dict(case_id=cid,relative_pressure_difference_2to4=e24,relative_pressure_difference_4to8=e48,
            max_IM_delta_2to4_pp=im24,max_IM_delta_4to8_pp=im48,diagnostics=diagnostics))
        np.savez_compressed(saved,spectrum=other)
        record=dict(dynamic_run_sha256=h,raw_spectrum_sha256=digest,verifier_sha256=verifier_sha,
                    array_file_sha256=hashlib.sha256(saved.read_bytes()).hexdigest(),comparison=comparisons[-1],convergence=convergence[-1])
        temporary=checkpoint.with_suffix('.tmp');temporary.write_text(json.dumps(record,indent=2,ensure_ascii=False,allow_nan=False));temporary.replace(checkpoint)
        print('P14B niezależnyRadau:',cid,error,'emisja',e24,e48,flush=True)
    np.savez_compressed(OUT/'p14b_niezalezny_Radau.npz',case_id=np.array(list(selected)),spectra=np.stack(arrays))
    result=dict(status='SELECTED_RADAU_AND_LARGE_RESPONSE_EMISSION_CONTROLS',dynamic_run_sha256=h,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),comparisons=comparisons,emission_convergence=convergence,
        scope='Wybrane świadki największego ruchu/rozruchu/bilansu oraz5Hz. Nie certyfikat wszystkich3312punktów ani całego pola rzeczywistego subwoofera.')
    (OUT/'p14b_weryfikacja_wybranych.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));return result


if __name__=='__main__':main()
