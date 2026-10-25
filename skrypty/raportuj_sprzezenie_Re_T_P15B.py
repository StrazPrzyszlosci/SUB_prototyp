"""Interpretacja pełnej rodziny P15B z zachowaniem warunkowości parametrów."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from analiza_sprzezenia_Re_T_P15B import make_coupled

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    with (OUT/name).open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    with (OUT/'p15b_sprzezenie_i_obwiednie.csv').open() as h:rows=list(csv.DictReader(h))
    with (OUT/'p15b_przebiegi_C02.csv').open() as h:traces=list(csv.DictReader(h))
    cfg=json.loads((ROOT/'dane/konfiguracje/p15b_sprzezenie_Re_T.json').read_text());memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    pool=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers'];entry=next(r for r in pool if r['candidate_id']=='C02')
    def select_trace(b,eta,kv,envelope):
        return [r for r in traces if float(r['gvm_w_k'])==b and float(r['eta_eddy_to_coil'])==eta and float(r['forced_g_per_velocity'])==kv and r['envelope']==envelope]
    paired=[];lookup={}
    for r in rows:
        key=tuple(r[k] for k in ('candidate_id','frequencies_hz','gvm_w_k','eta_eddy_to_coil','forced_g_per_velocity'))
        lookup.setdefault(key,{})[r['envelope']]=r
    for key,values in lookup.items():
        a=values['CONTINUOUS'];b=values['THREE_PULSES']
        paired.append(dict(candidate_id=key[0],frequencies_hz=key[1],gvm_w_k=float(key[2]),eta_eddy_to_coil=float(key[3]),forced_g_per_velocity=float(key[4]),
            peak_coil_pulses_minus_continuous_k=float(b['max_sampled_coil_rise_k'])-float(a['max_sampled_coil_rise_k']),
            final_coil_pulses_minus_continuous_k=float(b['last_coil_rise_k'])-float(a['last_coil_rise_k']),
            heat_in_pulses_minus_continuous_j=float(b['total_heat_in_j'])-float(a['total_heat_in_j'])))
    table('p15b_porownanie_obwiedni.csv',paired)
    families={}
    for r in rows:
        if float(r['eta_eddy_to_coil'])!=1.:continue
        key=tuple(r[k] for k in ('candidate_id','frequencies_hz','forced_g_per_velocity','envelope'))
        families.setdefault(key,[]).append(r)
    maximum_equal_port_coil_spread=max(max(float(r['max_sampled_coil_rise_k']) for r in group)-min(float(r['max_sampled_coil_rise_k']) for r in group) for group in families.values())
    assert maximum_equal_port_coil_spread<1e-6
    distinct={}
    for r in rows:distinct.setdefault((r['candidate_id'],r['frequencies_hz']),float(r['cold_pcu_slope_w_k']))
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for kv,color in [(0.,'C0'),(2.,'C1')]:
        for envelope,style in [('CONTINUOUS','-'),('THREE_PULSES','--')]:
            part=select_trace(1.,0.,kv,envelope);t=np.array([float(r['time_s']) for r in part])
            label=f'kv={kv:g}; '+('ciągły' if style=='-' else '3 impulsy')
            axes[0].plot(t,[float(r['coil_rise_k']) for r in part],style,color=color,label=label)
            axes[1].plot(t,[float(r['magnet_rise_k']) for r in part],style,color=color,label=label)
    axes[0].set(ylabel='Umowny przyrost T cewki [K]',title='C02 / 100 l / 20 + 85 Hz / po 15 Vrms')
    axes[1].set(ylabel='Umowny przyrost T magnesu [K]',title='To samo 300 s aktywności; inny przebieg grzania')
    for ax in axes:ax.set_xlabel('Czas [s]');ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'36_P15B_obwiednia_i_chlodzenie.{ext}',dpi=170)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8));temperature=np.linspace(0,150,301)
    for frequencies in ([20],[40],[80]):
        model=make_coupled(entry,frequencies,1.,0.,0.,cfg,memory);cold=model.response(0.)
        warm=[model.response(tv) for tv in temperature]
        axes[0].plot(temperature,[np.linalg.norm(r['current'])/np.linalg.norm(cold['current']) for r in warm],label=f'{frequencies[0]} Hz')
        axes[1].plot(temperature,[r['pcu_w']/cold['pcu_w'] for r in warm],label=f'{frequencies[0]} Hz')
    axes[0].set(ylabel='I RMS / I RMS zimne',title='Stałe napięcie: prąd maleje')
    axes[1].set(ylabel='Pcu / Pcu zimne',title='Grzanie zależy także od impedancji')
    for ax in axes:ax.set_xlabel('Narzucony przyrost T [K]; alpha = 0,004 /K');ax.grid(alpha=.25);ax.legend()
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'37_P15B_prad_i_grzanie.{ext}',dpi=170)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for eta,ax in zip((1.,0.),axes):
        for b in cfg['gvm_family_w_k']:
            part=select_trace(b,eta,0.,'CONTINUOUS')
            ax.plot([float(r['time_s']) for r in part],[float(r['coil_rise_k']) for r in part],label=f'gvm = {b:g} W/K')
        ax.set(xlabel='Czas [s]',ylabel='Umowny przyrost T cewki [K]',title='Całe Peddy do cewki' if eta==1 else 'Peddy do magnesu');ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.suptitle('Trzy różne wnętrza o tym samym zimnym porcie; C02 / 20 + 85 Hz / 100 l')
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'38_P15B_miejsce_strat_i_niejednoznacznosc.{ext}',dpi=170)
    plt.close(fig)
    result=dict(status='FULL_CONDITIONAL_P15B_ANALYSIS_NOT_PRODUCT_TEMPERATURES',cases=len(rows),distinct_cold_driver_frequency_cases=len(distinct),
        distinct_positive_cold_Pcu_slopes=sum(value>0 for value in distinct.values()),envelope_pairs=len(paired),
        max_equal_port_coil_spread_k=maximum_equal_port_coil_spread,
        pulse_minus_continuous_peak_range_k=[min(r['peak_coil_pulses_minus_continuous_k'] for r in paired),max(r['peak_coil_pulses_minus_continuous_k'] for r in paired)],
        pulse_minus_continuous_residual_range_k=[min(r['final_coil_pulses_minus_continuous_k'] for r in paired),max(r['final_coil_pulses_minus_continuous_k'] for r in paired)],
        max_sampled_coil_rise_in_assumed_family_k=max(float(r['max_sampled_coil_rise_k']) for r in rows),
        velocity_RSS_compression_range_db=[min(float(r['delta_motion_at_hottest_active_db']) for r in rows),max(float(r['delta_motion_at_hottest_active_db']) for r in rows)],
        scope='Liczby dotyczą wskazanej rodziny, nie rozkładu populacji. RSSprędkości dla pary nie jest automatycznie SPL. Temperatury, alpha, R/C i chłodzenie są scenariuszami.')
    (OUT/'p15b_interpretacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
