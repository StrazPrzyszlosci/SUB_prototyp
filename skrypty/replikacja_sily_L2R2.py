"""Risbo et al.2016, wzór18: replikacja analityki i kontrola interpretacji.

Nie odtwarza pomiarów4calowegoDUT ani symulacjiMagNet. Parametry liczbowe
są jawne; skok pokazany w bezwymiarowym czasie t/tau.
"""
import csv
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

ROOT=Path(__file__).resolve().parents[1]


def main():
    rows=[];error=0.;dc_error=0.;ode_error=0.
    phase=2*np.pi*np.arange(2048)/2048
    for tau in [.00005,.0005,.005,.05]:
        for f in [20.,40.,80.,100.,300.,1000.]:
            z=2*np.pi*f*tau
            for current_peak in [1.,4.,12.]:
                for q in [-1.,0.,1.]:
                    lj=.001*np.exp(.4*q);gradient=.4*lj/.01
                    current=current_peak*np.cos(phase)
                    filtered=current_peak*(np.cos(phase)+z*np.sin(phase))/(1+z*z)
                    force=.5*gradient*current*filtered
                    wrong=.5*gradient*filtered**2
                    cf=np.fft.rfft(force)/len(phase);cw=np.fft.rfft(wrong)/len(phase)
                    factor=.25*gradient*current_peak**2
                    predicted=factor/(1+1j*z)
                    error=max(error,float(abs(2*cf[2]/predicted-1)))
                    dc_error=max(dc_error,float(abs(cf[0].real/(factor/(1+z*z))-1)))
                    ratio=float(abs(cf[2]/cw[2]));expected=np.sqrt(1+z*z)
                    assert abs(ratio/expected-1)<1e-10
                    rows.append(dict(tau_s=tau,f_hz=f,omega_tau=z,current_peak_a=current_peak,q=q,
                                     L2_gradient_H_per_m=float(gradient),force_DC_N=float(cf[0].real),
                                     naive_force_DC_N=float(cw[0].real),force_H2_peak_N=float(2*abs(cf[2])),
                                     naive_force_H2_peak_N=float(2*abs(cw[2])),H2_amplitude_ratio=ratio,
                                     phase_difference_deg=float(np.angle(cf[2]/cw[2],deg=True)),
                                     source_role='ASSUMED_NUMBERS_REPLICATION_OF_EQUATION18_NOT_MEASURED_DEVICE'))
                    if current_peak==1 and q==0 and f in [20.,1000.]:
                        sol=solve_ivp(lambda t,y:(current_peak*np.cos(t)-y)/z,[0,2*np.pi],
                                      [current_peak/(1+z*z)],t_eval=phase,method='DOP853',
                                      rtol=2e-12,atol=2e-14,max_step=2*np.pi/256)
                        assert sol.success
                        ode_error=max(ode_error,float(max(abs(sol.y[0]-filtered))/current_peak))
    with (ROOT/'wyniki/p12c_replikacja_sily.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    u=np.linspace(-1,5,1201);current=np.where(u<0,.5,1.)
    filtered=np.where(u<0,.5,1-.5*np.exp(-u))
    step=[dict(time_over_tau=float(t),current_a=float(i),filtered_current_a=float(g),
               normalized_force_A2=float(.5*i*g),normalized_naive_force_A2=float(.5*g*g)) for t,i,g in zip(u,current,filtered)]
    with (ROOT/'wyniki/p12c_skok_pradu_i_sila.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(step[0]));w.writeheader();w.writerows(step)
    result=dict(status='PASS_REPLIKACJI_WZORU18_I_ROZNICY_OD_KONTROLI',rows=len(rows),
                max_relative_H2_complex_error=error,max_relative_DC_error=dc_error,
                max_absolute_ODE_filter_error=ode_error,
                exact_H2_ratio='sqrt(1+(omega*tau)^2)',exact_phase_difference='atan(omega*tau)',
                exact_DC_ratio=1.,max_sampled_H2_ratio=max(r['H2_amplitude_ratio'] for r in rows),
                source_url='https://purifi-audio.com/documents/content/WT1Pkt9-SxijAvNyifNN4Ao2a2',
                scope='Replikacja teorii dla zablokowanej pozycji i narzuconego prądu. Nie jest pomiarem, pełną walidacją ruchu ani rekonstrukcją danychMagNet.')
    assert error<1e-10 and dc_error<1e-9 and ode_error<1e-9
    (ROOT/'wyniki/p12c_replikacja_sily.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
