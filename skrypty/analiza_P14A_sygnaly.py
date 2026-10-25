"""P14A: wspólny headroom i pilot nieliniowych obliczeń dwutonowych."""
import csv
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape,NonlinearModel
from model_cewki_z_pamiecia import MemoryModel,linear_memory_response
from analiza_cewki_z_pamiecia import dynamic_network
from sygnaly_P14 import TonePair,joint_reference,mixing_collisions,sampled_peak_enclosure

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=fields);w.writeheader();w.writerows(rows)


def two_tone(model,pair,scale,cfg,method='LSODA'):
    if mixing_collisions(pair.frequencies_hz,3):
        raise ValueError('Wybrana para ma kolizje linii do3rzędu; ten pilot nie przypisuje im jednoznacznego IMD.')
    omega=2*np.pi*pair.base_hz;phase_period=2*np.pi
    def rhs(phase,state):
        # phase występuje w dotychczasowym RHS wyłącznie w porcie napięciowym.
        return model.scalar_rhs(np.pi/2,state,omega,float(scale*pair.value(phase)))
    def obs(phase,state):
        return model.observables(np.full_like(phase,np.pi/2),state,omega,scale*pair.value(phase))
    def domain(phase,state):return min(model.q_domain-abs(state[0]),1+model.eta*state[0]-.05)
    domain.terminal=True;domain.direction=-1
    current_scale=max(scale*np.sqrt(2)*sum(pair.weights_rms)/model.p.re,1.)
    scales=np.ones(model.size)
    if model.has_current:scales[2]=current_scale
    state=np.zeros(model.size);start=0.;cycles=cfg['pilot_cycles_initial'];nfev=0
    while True:
        end=cycles*phase_period
        solution=solve_ivp(rhs,[start,end],state,method=method,rtol=2e-10,atol=2e-12*scales,
                           dense_output=True,max_step=phase_period/(32*max(pair.orders)),events=domain)
        nfev+=solution.nfev
        if not solution.success:raise RuntimeError(solution.message)
        if len(solution.t_events[0]):return dict(status='MODEL_DOMAIN_EXCEEDED',end_cycles=float(solution.t[-1]/phase_period))
        probe=np.linspace(end-phase_period,end,129)
        closure=float(np.max(abs((solution.sol(probe)-solution.sol(probe-phase_period))/scales[:,None])))
        if closure<1e-8 or cycles>=cfg['pilot_cycles_maximum']:break
        start=end;state=solution.y[:,-1];cycles+=8
    samples=4*cfg['pilot_samples_per_period'];first=end-4*phase_period
    phase=first+np.arange(samples)*4*phase_period/samples
    data=obs(phase,solution.sol(phase));xcoef=np.fft.rfft(data['x'])/samples
    freq=np.fft.rfftfreq(samples,d=1/(pair.base_hz*cfg['pilot_samples_per_period']))
    pressure=-model.medium.rho*model.p.sd*(2*np.pi*freq)**2*xcoef*np.exp(-2j*np.pi*freq/model.medium.c)/(4*np.pi)
    rms=np.sqrt(2)*abs(pressure)
    def index(f):return int(round(f/(pair.base_hz/4)))
    f1,f2=pair.frequencies_hz;funds=[index(f1),index(f2)]
    denominator=float(np.linalg.norm(rms[funds]))
    im2=[abs(f2-f1),f1+f2];im3=[abs(2*f1-f2),abs(2*f2-f1)]
    band=(freq>=cfg['pilot_band_hz'][0])&(freq<=cfg['pilot_band_hz'][1]);band[funds]=False
    boundary_phase=np.array([first,end]);boundary=obs(boundary_phase,solution.sol(boundary_phase))
    net=np.mean(data['input_power']-data['copper_power']-data['mechanical_loss']-data['thermal_exergy_loss'])
    delta=(boundary['energy'][1]-boundary['energy'][0])*omega/(end-first)
    output=dict(status='PERIODIC_WITHIN_MODEL_TOLERANCE' if closure<1e-8 else 'NOT_SETTLED',end_cycles=cycles,
                closure_error=closure,nfev=nfev,
                IM2_diagnostic_pct=float(100*np.linalg.norm(rms[[index(f) for f in im2]])/denominator),
                IM3_difference_diagnostic_pct=float(100*np.linalg.norm(rms[[index(f) for f in im3]])/denominator),
                all_noninput_lines_in_band_pct=float(100*np.linalg.norm(rms[band])/denominator),
                fundamental1_rms_pa=float(rms[funds[0]]),fundamental2_rms_pa=float(rms[funds[1]]),
                x_peak_sampled_m=float(max(abs(data['x']))),x_dc_m=float(np.mean(data['x'])),
                voltage_rms_v=float(np.sqrt(np.mean(data['voltage']**2))),voltage_peak_sampled_v=float(max(abs(data['voltage']))),
                current_rms_a=float(np.sqrt(np.mean(data['current']**2))),
                energy_relative_residual=float(abs(net-delta)/max(np.mean(data['input_power']),1.)))
    return output


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p14a_sygnaly_i_pilot.json').read_text())
    memory_cfg=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    pool=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    rows=[]
    for entry in pool:
        p=Plant.from_driver(Driver(**entry['model']))
        for volume in cfg['reference_volumes_l']:
            for frequencies in cfg['tone_pairs_hz']:
                for profile in cfg['reference_profiles']:
                    instant,branches,_=dynamic_network(p,profile,memory_cfg)
                    response=linear_memory_response(p,volume,frequencies,instant,branches)
                    for weights in cfg['amplitude_ratios']:
                        basic=TonePair(tuple(frequencies),tuple(weights))
                        for k in range(cfg['phase_classes']):
                            phase2=k*basic.phase_period_second_tone()/cfg['phase_classes']
                            pair=TonePair(tuple(frequencies),tuple(weights),(0.,phase2))
                            result=joint_reference(p,pair,response,cfg['amp_reference_vrms'],cfg['amp_reference_arms'],cfg['reference_samples_per_period'])
                            rows.append(dict(candidate_id=entry['candidate_id'],volume_l=volume,profile=profile,
                                             f1_hz=frequencies[0],f2_hz=frequencies[1],weight1=weights[0],weight2=weights[1],
                                             phase2_rad=phase2,**result))
        print('P14A odniesienie:',entry['candidate_id'],flush=True)
    table('p14a_wspolne_ograniczenia.csv',rows)
    pilot=[]
    for entry in pool:
        if entry['candidate_id'] not in cfg['pilot_candidates']:continue
        p=Plant.from_driver(Driver(**entry['model']));pair0=TonePair(tuple(cfg['pilot_pair_hz']),tuple(cfg['pilot_weights']))
        ref=linear_memory_response(p,cfg['pilot_volume_l'],pair0.frequencies_hz,p.le0,[])
        drive=joint_reference(p,pair0,ref,cfg['amp_reference_vrms'],cfg['amp_reference_arms'])
        scale=cfg['pilot_reference_fraction']*drive['scale_phase_independent']
        for phase2 in cfg['pilot_phases_rad']:
            pair=TonePair(pair0.frequencies_hz,pair0.weights_rms,(0.,phase2))
            for profile in cfg['pilot_profiles']:
                if profile=='LINEAR':model=NonlinearModel(p,cfg['pilot_volume_l'],tau_s=cfg['tau_gas_s'],gas_nonlinear=False)
                elif profile=='NL_SIMPLE':model=NonlinearModel(p,cfg['pilot_volume_l'],Shape(**memory_cfg['dynamic_shape']),tau_s=cfg['tau_gas_s'])
                else:
                    instant,bs,_=dynamic_network(p,'FLUX_ONE',memory_cfg)
                    model=MemoryModel(p,cfg['pilot_volume_l'],instant,bs,Shape(**memory_cfg['dynamic_shape']),cfg['tau_gas_s'])
                result=two_tone(model,pair,scale,cfg)
                pilot.append(dict(candidate_id=entry['candidate_id'],profile=profile,phase2_rad=phase2,voltage_scale=scale,**result))
                print('P14A pilot:',entry['candidate_id'],phase2,profile,result['status'],flush=True)
    table('p14a_pilot_IMD.csv',pilot)
    collisions={str(pair):mixing_collisions(pair) for pair in [[20,85],[25,95],[20,80]]}
    result=dict(status='P14A_ODNIESIENIE_I_12_PILOTOW_NIE_ZAMKNIETY_P14',reference_cases=len(rows),pilot_cases=len(pilot),
                minimum_joint_vs_separate_db=min(r['change_from_separate_db'] for r in rows),
                maximum_joint_vs_separate_db=max(r['change_from_separate_db'] for r in rows),
                collisions_through_order3=collisions,
                pilot_status_counts={s:sum(r['status']==s for r in pilot) for s in sorted({r['status'] for r in pilot})},
                scope='IM2: f2-f1,f2+f1; IM3difference:|2f1-f2|,|2f2-f1|. Mianownik RSS dwóch podstawowych ciśnień. Nie deklarujemy standardowej normowej miary, rzeczywistego THD ani zamknięcia wielotonówP25.')
    (OUT/'p14a_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
