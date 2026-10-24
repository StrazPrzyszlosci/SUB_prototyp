"""Dwa jawne scenariusze fizyczne: nieliniowość gazu i wzrost rezystancji.

Nie oblicza THD akustycznego ani temperatury cewki. Ruch membrany w części
gazowej jest zadany, a nie rozwiązany z nieliniowego równania ruchu.
"""
import csv
from dataclasses import replace
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_subwoofera import Driver, response

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'wyniki'


def save_table(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def gas_force_harmonics(d, vb_l, fraction=1., gamma=1.4, p0=101325., samples=16384):
    """p*V^gamma=const; x dodatnie zmniejsza V; F jest modułem przeciwdziałania."""
    phase = 2*np.pi*np.arange(samples)/samples
    amplitude = d.xmax_mm*1e-3*fraction
    ratio = d.sd*amplitude/(vb_l*1e-3)
    if not 0 < ratio < 1:
        raise ValueError('Objętość chwilowa musi być dodatnia i ruch niezerowy')
    pressure = p0*((1-ratio*np.cos(phase))**(-gamma)-1)
    force = d.sd*pressure
    fft = np.fft.rfft(force)/samples
    harmonics = 2*abs(fft[1:4])
    linear_force = gamma*p0*d.sd**2/(vb_l*1e-3)*amplitude
    return {'driver':d.name,'vb_net_l':vb_l,'x_fraction_of_catalog':fraction,
            'x_peak_mm':amplitude*1000,'sd_x_over_vb':ratio,
            'gamma_assumed':gamma,'p0_pa_assumed':p0,
            'pressure_max_pa':float(np.max(pressure)), 'pressure_min_pa':float(np.min(pressure)),
            'air_force_dc_n':float(np.mean(force)), 'air_force_fundamental_peak_n':harmonics[0],
            'air_force_h2_percent':100*harmonics[1]/harmonics[0],
            'air_force_h3_percent':100*harmonics[2]/harmonics[0],
            'fundamental_to_linear_ratio':harmonics[0]/linear_force,
            'h2_small_ratio_percent':100*(gamma+1)/4*ratio,
            'h3_small_ratio_percent':100*(gamma+1)*(gamma+2)/24*ratio**2}


def main():
    OUT.mkdir(exist_ok=True)
    raw=json.loads((ROOT/'dane/przetworniki/kandydaci.json').read_text())
    drivers=[Driver(**r['model']) for r in raw['drivers']]
    gas=[]
    for d in drivers:
        # Kontrola granicy małego ruchu i zgodności FFT ze wzorem szeregowym.
        small=gas_force_harmonics(d,60,fraction=.01)
        np.testing.assert_allclose(small['air_force_h2_percent'],small['h2_small_ratio_percent'],rtol=1e-5)
        np.testing.assert_allclose(small['air_force_h3_percent'],small['h3_small_ratio_percent'],rtol=1e-4)
        doubled=gas_force_harmonics(d,60,fraction=.02)
        np.testing.assert_allclose(doubled['air_force_h2_percent']/small['air_force_h2_percent'],2.,rtol=1e-5)
        for vb in (30,45,60,80,100,120):
            for fraction in (.25,.5,1.):
                row=gas_force_harmonics(d,vb,fraction)
                check=gas_force_harmonics(d,vb,fraction,samples=32768)
                np.testing.assert_allclose(row['air_force_h2_percent'],check['air_force_h2_percent'],rtol=1e-9)
                np.testing.assert_allclose(row['air_force_h3_percent'],check['air_force_h3_percent'],rtol=1e-8)
                gas.append(row)
    save_table('nieliniowosc_sprezyny_powietrznej.csv',gas)
    f=np.geomspace(10,200,1200)
    probes=np.array([20.,25.,31.5,40.,63.,80.])
    thermal=[]
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    for d,ax in zip(drivers,axes.flat):
        base=response(d,60,f,vrms=10.)
        for scale in (1.,1.25,1.5):
            # Qes~Re, a BL/Mms/Cms/Rms pozostają stałe; nie rekonstruujemy
            # nowego silnika przez nieprawidłowe niezależne zwiększenie Re.
            warm=replace(d,re_ohm=d.re_ohm*scale,qes=d.qes*scale)
            np.testing.assert_allclose([warm.bl,warm.cms,warm.mms,warm.rms],
                                       [d.bl,d.cms,d.mms,d.rms],rtol=1e-12)
            out=response(warm,60,f,vrms=10.)
            delta=out['spl_rms_db']-base['spl_rms_db']
            ax.semilogx(f,delta,label=f'Re × {scale:g}')
            cold=response(d,60,probes,vrms=10.)
            point=response(warm,60,probes,vrms=10.)
            for i,freq in enumerate(probes):
                thermal.append({'driver':d.name,'vb_net_l':60,'input_vrms':10.,'re_multiplier':scale,
                                'temperature_c':None,'f_hz':freq,
                                'spl_change_from_reference_db':point['spl_rms_db'][i]-cold['spl_rms_db'][i],
                                'current_rms_a':point['i_rms'][i],
                                'copper_loss_w':point['p_copper_w'][i],
                                'status':'scenariusz_Re_nie_model_temperatury'})
        ax.set(title=d.name,xlabel='Częstotliwość [Hz]',ylabel='Zmiana SPL przy tym samym V [dB]')
        ax.grid(True,which='both',alpha=.3)
        ax.legend()
    plt.tight_layout()
    plt.savefig(OUT/'04_wzrost_rezystancji.png',dpi=160)
    plt.savefig(OUT/'04_wzrost_rezystancji.svg')
    plt.close()
    save_table('scenariusze_wzrostu_Re.csv',thermal)
    plt.figure(figsize=(10,5))
    for d in drivers:
        rows=[r for r in gas if r['driver']==d.name and r['x_fraction_of_catalog']==1.]
        plt.plot([r['vb_net_l'] for r in rows],[r['air_force_h2_percent'] for r in rows],'o-',label=d.name)
    plt.xlabel('Objętość netto [l]')
    plt.ylabel('H2/H1 siły powietrza [%]')
    plt.title('Zadany sinus ruchu przy katalogowym wychyleniu; to nie THD akustyczne')
    plt.grid(True,alpha=.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT/'05_sprezyna_powietrzna.png',dpi=160)
    plt.savefig(OUT/'05_sprezyna_powietrzna.svg')
    plt.close()
    print(f'Kontrole: szereg Taylora, skalowanie, zbieżność FFT, stałe mechaniczne przy zmianie Re: OK. Gaz: {len(gas)}, Re: {len(thermal)} scenariuszy pasmowych.')
    for r in gas:
        if r['vb_net_l']==60 and r['x_fraction_of_catalog']==1.:
            print(r['driver'],f"epsilon={r['sd_x_over_vb']:.6f}; H2 siły powietrza={r['air_force_h2_percent']:.3f}%; H3={r['air_force_h3_percent']:.4f}%")


if __name__=='__main__':
    main()
