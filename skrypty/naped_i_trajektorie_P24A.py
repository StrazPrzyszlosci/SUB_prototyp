"""Cena konserwatywnego obszaru i ciągły model z Re(theta) i temperaturą.

Weryfikacja numeryczna nie zastępuje dokładnego certyfikatu;oba mają
niezależne artefakty. M,K,BL,Le pozostają stałe,dodatkowe ciepło pominięto.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import csv,hashlib,json,time
import numpy as np
from scipy.integrate import solve_ivp
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import RHO,C

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p24a_weryfikacja_i_sygnaly.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def command(t,kind):
    if kind=='sine20':return np.sin(2*np.pi*20*t)
    if kind=='two20_85':return .5*(np.sin(2*np.pi*20*t)+np.sin(2*np.pi*85*t+.3))
    if kind=='step':return np.ones_like(np.asarray(t,dtype=float))
    raise ValueError(kind)


def main():
    cfg=json.loads(CFG.read_text());search_cfg=json.loads((ROOT/'dane/konfiguracje/p24a_wspolny_obszar_niezmienniczy.json').read_text())
    study=json.loads((OUT/'p24a_podsumowanie.json').read_text());exact=json.loads((OUT/'p24a_weryfikacja_dokladna_LDL.json').read_text())
    assert study['accepted']==exact['accepted']==972
    records=[json.loads(p.read_text()) for p in sorted((ROOT/study['checkpoint_folder']).glob('*.json'))];pool={cid:d for cid,pid,d,cat in candidates()}
    performance=[];thermal=[];parameter_error=0.;chosen=[]
    for r in records:
        cert=r['certificate'];p={k:float(F(v)) for k,v in cert['parameters'].items()};d=pool[r['configuration']]
        K=1/d.cms+RHO*C*C*d.sd*d.sd/(r['volume_l']*.001)
        # Odrębne powiązanie zapisanych parametrów certyfikatu z modelem puli.
        for key,target in dict(M=d.mms,K=K,Le=d.le_mh*.001,BL=d.bl,Rms=d.rms,Re0=d.re_ohm).items():
            parameter_error=max(parameter_error,abs(p[key]/target-1))
        universal=float(F(cert['source_peak_voltage_v']));rail=search_cfg['source_peak_rail_v_assumed_for_sine_comparison']
        for temperature in [0.,p['theta_limit']]:
            R=p['Re0']*(1+p['alpha']*temperature)+p['Rs']
            for f in search_cfg['sine_probes_hz']:
                s=2j*np.pi*f;zm=p['Rms']+s*p['M']+p['K']/s
                z=R+s*p['Le']+p['BL']**2/zm;i=1/z;v=p['BL']*i/zm;x=v/s
                individual=min(rail,p['Icap']/abs(i),p['Xref']/abs(x))
                spl=lambda u:20*np.log10(RHO*d.sd*abs(s*s*x)*u/(2*np.pi*np.sqrt(2)*20e-6))
                performance.append(dict(case_id=r['case_id'],configuration=r['configuration'],driver_name=d.name,
                    volume_l=r['volume_l'],Rth_assumed_k_w=r['Rth_assumed_k_w'],temperature_limit_k=r['temperature_rise_limit_k'],
                    X_reference_fraction=r['X_catalog_reference_fraction'],f_hz=f,frozen_temperature_rise_k=temperature,
                    universal_witness_source_peak_v=universal,individual_sine_source_peak_v=individual,
                    universal_witness_spl_rms_2pi_1m_db=float(spl(universal)),individual_sine_spl_rms_2pi_1m_db=float(spl(individual)),
                    conservative_level_difference_db=float(20*np.log10(individual/universal)),
                    witness_x_peak_mm=float(abs(x)*universal*1000),witness_current_peak_a=float(abs(i)*universal)))
        a=p['Re0']*p['Icap']**2;b=1/p['Rth']-p['alpha']*a;equilibrium=a/b
        assert b>0 and equilibrium<=p['theta_limit']*(1+1e-12)
        for cth,initial,t in product(cfg['thermal_upper_Cth_j_k_assumed'],[0.,p['theta_limit']],cfg['thermal_upper_times_s']):
            upper=equilibrium+(initial-equilibrium)*np.exp(-b*t/cth)
            thermal.append(dict(case_id=r['case_id'],Cth_assumed_j_k=cth,initial_theta_k=initial,time_s=t,
                theta_upper_comparison_k=float(upper),theta_limit_k=p['theta_limit'],
                interpretation='Comparison upper bound from instantaneous |i|<=Icap,not predicted device temperature.'))
        if r['configuration'] in cfg['continuous_configurations'] and r['volume_l']==cfg['volume_l'] and r['Rth_assumed_k_w']==cfg['Rth_assumed_k_w'] and r['temperature_rise_limit_k']==cfg['temperature_limit_k'] and r['X_catalog_reference_fraction']==cfg['X_catalog_reference_fraction']:
            chosen.append(r)
    assert parameter_error<1e-12 and len(chosen)==6
    write('p24a_naped_i_cena_zapasu.csv',performance);write('p24a_gorna_obwiednia_temperatury.csv',thermal)
    observations=[];retained={};start=time.monotonic();duration=cfg['duration_s'];cth=cfg['Cth_assumed_j_k']
    times=np.arange(round(duration*cfg['evaluation_rate_hz'])+1)/cfg['evaluation_rate_hz']
    for r in chosen:
        cert=r['certificate'];p={k:float(F(v)) for k,v in cert['parameters'].items()};voltage=float(F(cert['source_peak_voltage_v']))
        Q=np.linalg.inv(np.array([[float(F(v)) for v in row] for row in cert['X']]))
        scales=np.array([p['Xref'],1.,p['Icap']])
        for initial,kind in product(cfg['initial_temperature_cases'],cfg['signals']):
            theta0=0. if initial=='ambient' else p['theta_limit']
            def rhs(t,z):
                x,v,i,theta=z;u=voltage*float(command(t,kind));re=p['Re0']*(1+p['alpha']*theta)
                return [v,(p['BL']*i-p['Rms']*v-p['K']*x)/p['M'],
                    (u-(re+p['Rs'])*i-p['BL']*v)/p['Le'],(re*i*i-theta/p['Rth'])/cth]
            sol=solve_ivp(rhs,[0,duration],[0.,0.,0.,theta0],method='LSODA',rtol=2e-9,
                atol=[1e-12,1e-10,1e-10,1e-9],max_step=1/(85*48),dense_output=True)
            assert sol.success,sol.message
            Z=sol.sol(times).T;xi=Z[:,:3]/scales;W=np.einsum('ni,ij,nj->n',xi,Q,xi)
            u=voltage*command(times,kind)
            key=r['case_id']+'_'+initial+'_'+kind
            obs=dict(case_id=key,configuration=r['configuration'],signal=kind,initial_temperature_case=initial,
                duration_s=duration,Cth_assumed_j_k=cth,source_peak_voltage_bound_v=voltage,
                max_sampled_W=float(np.max(W)),max_sampled_abs_x_per_reference=float(np.max(abs(Z[:,0]))/p['Xref']),
                max_sampled_abs_i_per_bound=float(np.max(abs(Z[:,2]))/p['Icap']),
                max_sampled_theta_per_limit=float(np.max(Z[:,3])/p['theta_limit']),min_sampled_theta_k=float(np.min(Z[:,3])),
                numerical_function_calls=sol.nfev)
            assert max(obs[k] for k in ['max_sampled_W','max_sampled_abs_x_per_reference','max_sampled_abs_i_per_bound','max_sampled_theta_per_limit'])<=1+2e-6
            observations.append(obs)
            if r['configuration'] in ['C04','C26P'] and initial=='ambient':
                retained[key]=np.column_stack([times,u,Z,W])
        print('P24A coupled continuous checked',r['configuration'],flush=True)
    write('p24a_ciagle_trajektorie_z_temperatura.csv',observations)
    np.savez_compressed(OUT/'p24a_przebiegi_reference.npz',**retained)
    inputs=[Path(__file__).resolve(),CFG,ROOT/'skrypty/analiza_rozszerzenia_SB.py',ROOT/'skrypty/model_subwoofera.py',
        OUT/'p24a_podsumowanie.json',OUT/'p24a_weryfikacja_dokladna_LDL.json',ROOT/'dane/konfiguracje/p24a_wspolny_obszar_niezmienniczy.json']
    result=dict(status='COMPLETE_SCOPED_PERFORMANCE_AND_CONTINUOUS_COPPER_THERMAL_CHECKS',
        performance_rows=len(performance),thermal_comparison_rows=len(thermal),continuous_ODE_cases=len(observations),
        retained_wave_cases=len(retained),retained_columns=['time_s','source_voltage_v','x_m','velocity_m_s','current_a','theta_k','W_dimensionless'],
        max_relative_parameter_mapping_error=parameter_error,elapsed_continuous_s=time.monotonic()-start,
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},limitations=cfg['limitations']+[
            'Lyapunov W is dimensionless and is not stored physical energy in joules.',
            'Individual sine envelopes use the same instantaneous Icap and Xref but allow one separate sinus;not guaranteed all bounded signals.',
            '36 continuous trajectories confirm selected members;numerical sampling is not the proof of universal invariance.'])
    (OUT/'p24a_naped_i_ODE_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P24A cost/continuous:',len(performance),'sines;',len(thermal),'upper bounds;',len(observations),'ODE',flush=True)


if __name__=='__main__':main()
