"""Porównanie 216 wariantów LT/HP/Vb przy wspólnych ograniczeniach modelu.

Maksimum wejścia dla osobnych sinusów o stałym poziomie w przebiegu10–200Hz.
Nie jest analizą muzyki, limiterem czasowym ani gwarancją użytecznego SPL.
"""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_subwoofera import Driver, alignment, dsp_shape, linear_envelope, response

ROOT=Path(__file__).resolve().parents[1]


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/badania_wstepne.json').read_text())
    raw=json.loads((ROOT/'dane/przetworniki/kandydaci.json').read_text())
    drivers=[Driver(**d['model']) for d in raw['drivers']]
    f=np.geomspace(10,200,1800)
    probe=np.array([20.,25.,31.5,40.,63.,80.])
    rows=[]
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    for d,ax in zip(drivers,axes.flat):
        for vb in cfg['volumes_l']:
            fc,qtc,_=alignment(d,vb)
            bound=linear_envelope(d,vb,f,cfg['amp_vrms'],cfg['amp_irms'])
            for target in (20.,25.,30.):
                for hp in (12.,18.,22.):
                    filters=dict(target_hz=target,target_q=1/np.sqrt(2),hp_hz=hp,lp_hz=80.)
                    gain=abs(dsp_shape(f,fc,qtc,**filters))
                    ratios=bound['v_rms']/gain
                    index=int(np.argmin(ratios))
                    input_v=float(ratios[index])
                    out=response(d,vb,f,input_v*gain)
                    assert np.all(out['x_peak_m'] <= d.xmax_mm*1e-3*(1+1e-10))
                    assert np.all(out['i_rms'] <= cfg['amp_irms']*(1+1e-10))
                    assert np.all(input_v*gain <= cfg['amp_vrms']*(1+1e-10))
                    gp=abs(dsp_shape(probe,fc,qtc,**filters))
                    bp=response(d,vb,probe,input_v*gp)
                    row={'driver':d.name,'vb_net_l':vb,'target_hz_assumed':target,'hp_hz_assumed':hp,
                         'max_equal_sine_input_vrms':input_v,'guard_band_hz':'10-200',
                         'limiting_guard_frequency_hz':f[index],
                         'limiting_mechanism':['xmax','amp_voltage','amp_current','catalog_voltage_proxy'][bound['limit'][index]],
                         'max_filter_gain_db':20*np.log10(np.max(gain)),
                         'required_digital_pre_attenuation_db_at_least':max(0.,20*np.log10(np.max(gain)))}
                    for i,freq in enumerate(probe):
                        row[f'spl_rms_2pi_1m_{freq:g}hz_db']=bp['spl_rms_db'][i]
                        row[f'output_{freq:g}hz_vrms']=input_v*gp[i]
                    rows.append(row)
                    selected_v=100 if '390' in d.name else 60
                    if vb==selected_v and hp==18.:
                        ax.semilogx(f,out['spl_rms_db'],label=f'LT {target:g}Hz')
        ax.set(title=d.name+f' — {100 if "390" in d.name else 60} l',
               xlabel='Częstotliwość [Hz]',ylabel='SPL RMS [dB], 2π,1m')
        ax.grid(True,which='both',alpha=.3)
        ax.legend()
    plt.suptitle('Stały poziom sinusa przed filtrami, ograniczenia w paśmie10–200Hz; HP18Hz')
    plt.tight_layout()
    plt.savefig(ROOT/'wyniki/06_cele_dsp.png',dpi=160)
    plt.savefig(ROOT/'wyniki/06_cele_dsp.svg')
    plt.close()
    with (ROOT/'wyniki/cele_dsp.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f'Obliczono {len(rows)} wariantów. Limity sprawdzone w paśmie10–200Hz. Nie jest to analiza sygnału wielotonowego.')
    for r in rows:
        selected_v=100 if '390' in r['driver'] else 60
        if r['vb_net_l']==selected_v and r['hp_hz_assumed']==18.:
            print(r['driver'],r['target_hz_assumed'],round(r['max_equal_sine_input_vrms'],3),
                  round(r['spl_rms_2pi_1m_20hz_db'],2),round(r['spl_rms_2pi_1m_40hz_db'],2))


if __name__=='__main__':
    main()
