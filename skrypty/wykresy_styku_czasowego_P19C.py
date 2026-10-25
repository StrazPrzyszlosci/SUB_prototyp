"""Wykresy czasu,aktywnego styku i zbieznosci z wykonanych przebiegow."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=160);fig.savefig(OUT/(name+'.svg'));plt.close(fig)


def main():
    j=json.loads((OUT/'p19c_podsumowanie.json').read_text());r=next(x for x in j['results'] if x.get('label')=='E32')
    with (OUT/'p19c_E32_przebieg.csv').open() as f:rows=list(csv.DictReader(f))
    get=lambda k:np.array([float(x[k]) for x in rows]);theta=get('theta');t=(theta-theta[0])/(2*np.pi*80)
    linear=complex(r['linear_basket_rms_real'],r['linear_basket_rms_imag'])
    ref=np.sqrt(2)*np.real(-1j*linear*np.exp(1j*theta))
    fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    axs[0,0].plot(t*1000,ref*1e6,'--',label='Zamrożony styk');axs[0,0].plot(t*1000,get('basket')*1e6,label='Styk jednostronny w czasie')
    axs[0,0].set(xlabel='Czas w okresie [ms]',ylabel='Ruch kosza [µm]');axs[0,0].legend(fontsize=8)
    axs[0,1].plot(t*1000,get('open_fraction')*100,color='#c0392b')
    axs[0,1].set(xlabel='Czas w okresie [ms]',ylabel='Otwarte pole modelu uszczelki [%]',title='Kwadratura 4 × 128; bez wniosku o drożnym przecieku')
    power=get('input_power')-get('structural_loss')-get('gas_loss')
    work=np.r_[0,np.cumsum((power[1:]+power[:-1])*np.diff(t)/2)]
    energy=get('energy')-get('energy')[0]
    axs[1,0].plot(t*1000,energy,label='Zmiana energii');axs[1,0].plot(t*1000,work,'--',label='Całka mocy wejścia minus straty')
    axs[1,0].set(xlabel='Czas w okresie [ms]',ylabel='Energia [J]');axs[1,0].legend(fontsize=8)
    for name,offset in [('basket',-.17),('pressure',.17)]:
        p=r['phases'][name];z=np.array(p['harmonics_rms_real'])+1j*np.array(p['harmonics_rms_imag'])
        axs[1,1].bar(np.arange(2,7)+offset,abs(z[1:6])/abs(z[0])*100,.32,label='Kosz' if name=='basket' else 'Gaz 0D')
    axs[1,1].set(xlabel='Rząd harmonicznej względem 80 Hz',ylabel='Amplituda / składowa podstawowa [%]',title='Diagnostyka kontaktu; nie THD głośnika ani emisji');axs[1,1].legend(fontsize=8)
    for ax in axs.flat:ax.grid(alpha=.2)
    fig.suptitle('P19C: C04, SSSS_HARD, 80 Hz, zadany ruch stożka 1 mm RMS\nT₀=100 N, kₙ=10⁹ Pa/m; hipotetyczna uszczelka i CG, model zredukowany 43 DOF',fontsize=11)
    save(fig,'53_P19C_przebieg_styku_i_energia')

    fig,axs=plt.subplots(1,3,figsize=(14,4.7),layout='constrained')
    data=j['results'][:4];reference=data[-1]['basket_peak_m']
    axs[0].plot([x['dimension'] for x in data],[x['basket_peak_m']*1e6 for x in data],'-o')
    axs[0].set(xlabel='Liczba współrzędnych modelu',ylabel='Szczyt ruchu kosza [µm]',title='Galerkin i statyczne wzbogacenie')
    full=j['full_time_comparison'];N=np.array([r['steps_per_cycle'] for r in full])
    axs[1].plot(N,[r['basket_peak_m']*1e6 for r in full],'-o',label='Pełny MES BDF2')
    axs[1].axhline(reference*1e6,ls='--',color='#d95f02',label='43 DOF Radau')
    axs[1].set(xlabel='Kroki na okres',ylabel='Szczyt ruchu kosza [µm]',title='Pełne 2959 DOF; 3 okresy z przygotowanej historii');axs[1].legend(fontsize=7)
    err=np.array([r['relative_integrated_energy_residual'] for r in full]);axs[2].loglog(N,err,'-o',label='Reszta bilansu energii')
    axs[2].loglog(N,err[0]*(N[0]/N)**2,'--',label='Linia odniesienia N⁻²')
    axs[2].set(xlabel='Kroki na okres',ylabel='Względna reszta bilansu',title='Odrębna metoda i kontrola kroku');axs[2].legend(fontsize=8)
    for ax in axs:ax.grid(alpha=.25)
    fig.suptitle('Zbieżność badanego przypadku; pełny MES przygotowany z ROM nie jest niezależnym zimnym rozruchem',fontsize=11)
    save(fig,'54_P19C_zbieznosc_i_pelny_MES')
    print('Wykresy53/54 zapisane')


if __name__=='__main__':main()
