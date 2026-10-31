"""5184wspólne testy pasmowe; objętość ciągła, poziomy diagnostyczne."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from model_nieliniowy import Plant
from model_subwoofera import Driver
from analiza_cewki_z_pamiecia import dynamic_network
from synteza_granic_P17 import requirements,feasible,at_volume,Interval

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    config=ROOT/'dane/konfiguracje/p17_synteza_V_I_X_cieplo.json';poolpath=ROOT/'dane/przetworniki/pula_rozszerzona.json';mempath=ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json'
    cfg=json.loads(config.read_text());memory=json.loads(mempath.read_text());pool=json.loads(poolpath.read_text())['drivers']
    paths=[config,poolpath,mempath,Path(__file__),ROOT/'skrypty/synteza_granic_P17.py',ROOT/'skrypty/model_nieliniowy.py',ROOT/'skrypty/model_subwoofera.py',ROOT/'skrypty/model_cewki_z_pamiecia.py',ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/analiza_cewki_z_pamiecia.py',ROOT/'brief_system_audio_DIY_v0.6.md',ROOT/'dane/konfiguracje/pokoj_odsluchowy.json',ROOT/'dane/konfiguracje/pokoj_rzut_scenariusze_v2.json']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    run=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    snapshot=OUT/'archiwum'/('P17_start_'+run[:16])/'stan_wejsc'
    for p in paths:
        dest=snapshot/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():dest.write_bytes(p.read_bytes())
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==hashes[str(p.relative_to(ROOT))]
    points=[];bands=[]
    for entry in pool:
        p=Plant.from_driver(Driver(**entry['model']))
        for profile in cfg['profiles']:
            instant,branches,_=dynamic_network(p,profile,memory)
            for level in cfg['target_sine_spl_rms_db']:
                pressure=20e-6*10**(level/20)
                for rise in cfg['temperature_rise_scenarios_k']:
                    reqs=[requirements(p,f,pressure,instant,branches,rise,cfg['alpha_per_k'],cfg['distance_m'],cfg['gas_tau_s']) for f in cfg['frequencies_hz']]
                    for amp in cfg['amplifier_budgets']:
                        for rth in cfg['thermal_resistance_test_k_w']:
                            base=dict(candidate_id=entry['candidate_id'],driver=entry['model']['name'],role=entry.get('role'),
                                final_selection_gate=entry['final_selection_gate'],profile=profile,target_sine_SPL_rms_db=level,
                                rise_scenario_k=rise,thermal_Rth_test_k_w=rth,amp_vrms=amp['voltage_rms_v'],amp_arms=amp['current_rms_a'])
                            total=Interval();statuses=[]
                            for req in reqs:
                                interval,status=feasible(req,p,amp['voltage_rms_v'],amp['current_rms_a'],rise,rth,cfg['eddy_heat_factor_worst_case'])
                                total=total.intersect(interval);statuses.append(status);vlo,vhi=interval.volume_l()
                                reference=at_volume(req,cfg['reference_volume_l'],p,rise,cfg['alpha_per_k'])
                                points.append(dict(**base,f_hz=req['f_hz'],status=status,Vb_min_l=vlo,Vb_max_l=vhi,
                                    required_X_to_catalogue=req['x_required_peak_m']/p.xref,**reference))
                            vlo,vhi=total.volume_l()
                            status='NO_COMMON_VOLUME' if total.empty else 'COMMON_CONDITIONAL_VOLUME_INTERVAL'
                            if 'CATALOGUE_X_REFERENCE_EXCEEDED' in statuses:status='X_REFERENCE_PRECLUDES_TARGET_AT_SOME_FREQUENCY'
                            band=dict(**base,status=status,Vb_min_l=vlo,Vb_max_l=vhi,
                                scope='KONIECZNE_TESTY6ODDZIELNYCH_SINUSOW_NIE_MUZYKA_NIE_SPL_W_POKOJU')
                            if not total.empty:
                                u=float(np.clip(1000/cfg['reference_volume_l'],total.lower,total.upper))
                                if u==0:u=total.upper/2 if np.isfinite(total.upper) else 10.
                                probe=1000/u
                                at=[at_volume(r,probe,p,rise,cfg['alpha_per_k']) for r in reqs]
                                band.update(reference_feasible_volume_l=probe,
                                    illustrative_30_150l_overlap=not total.intersect(Interval(1000/cfg['illustrative_volume_window_l'][1],1000/cfg['illustrative_volume_window_l'][0])).empty,
                                    maximum_required_voltage_rms_v=max(r['voltage_rms_v'] for r in at),maximum_required_current_rms_a=max(r['current_rms_a'] for r in at),
                                    minimum_Rth_max_at_reference_k_w=min(r['Rth_max_all_heat_to_coil_k_w'] for r in at))
                            bands.append(band)
        print('P17:',entry['candidate_id'],flush=True)
    table('p17_punkty_i_wymagania.csv',points);table('p17_wspolny_przedzial_Vb.csv',bands)
    for p in paths:assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(ROOT))],'Wejście zmieniło się w czasie przebiegu'
    summary=dict(status='P17_WARUNKOWA_SYNTEZA_ODDZIELNYCH_SINUSOW_NIE_FINALNY_WYBOR',point_cases=len(points),band_cases=len(bands),
        band_status_counts={s:sum(r['status']==s for r in bands) for s in sorted({r['status'] for r in bands})},
        input_sha256=hashes,run_sha256=run,
        room=dict(dimensions_m=[4.6,3.7,2.5],front_width_m=3.7,layout='RTVleft_sofaright_U020',room_transfer_applied=False),
        geometry='Monopol4pi/1m/RMS,sinusdługotrwały;poziomy85/90/95/100dBto diagnostyka,nie progi użytkownika.',
        limitations=['Wspólny zakres dla6częstotliwości nie certyfikuje całego ciągłego pasma ani sumy tonów.',
            'Rth_test i limityT to scenariusze,nie pomiary. Xmax katalogowe nie gwarantujeTHD.',
            'Nie przenosić na sweetspot2.5–3m,roomgain ani realny zysk dwóch subwooferów.',
            'Przedział po wszystkichVb>0 nie oznacza możliwości ustawienia dwóch skrzyń w pokoju; geometria/masa/klej pozostają P18/P19.'])
    (OUT/'p17_podsumowanie.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2,ensure_ascii=False));return summary


if __name__=='__main__':main()
