"""Wykresy i podsumowanie wykonanego zakresu P14B, bez rankingu THD produktów."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as h:return list(csv.DictReader(h))


def main():
    summary=json.loads((OUT/'p14b_studia_podsumowanie.json').read_text())
    if summary['merged_status_counts']!={'PERIODIC_WITHIN_MODEL_TOLERANCE':3312}:raise ValueError('Nierozstrzygnięta kampania')
    values=read('p14b_miary_stacjonarne.csv');preload=read('p14b_studium_preload.csv')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    profiles=[('GAS_ONLY','Gaz'),('NL_SIMPLE','NL prosty'),('NL_FLUX_ONE','NL FLUX1')]
    for ax,metric in zip(axes,('IM2_pct','IM3_difference_pct')):
        for color,(profile,label) in enumerate(profiles):
            for cid,style in [('C02','o-'),('C06','s--')]:
                rows=sorted([r for r in values if r['candidate_id']==cid and r['profile']==profile and float(r['volume_l'])==100
                    and r['frequencies_hz']=='[20, 85]' and float(r['phase_class'])==0 and float(r['initial_q'])==0],key=lambda r:float(r['level']))
                ax.loglog([float(r['level']) for r in rows],[float(r[metric]) for r in rows],style,color=f'C{color}',label=f'{cid} {label}',markersize=4)
        ax.axhspan(1e-12,1e-6,color='k',alpha=.07);ax.set_ylim(bottom=1e-9)
        ax.set(xlabel='Względna skala wejścia',ylabel='Własna miara / RSS podstawowych [%]',title='IM2' if metric=='IM2_pct' else 'IM3: różnice')
        ax.grid(alpha=.25,which='both');ax.legend(fontsize=7)
    fig.suptitle('20 + 85 Hz / 100 l; umowne krzywe; szare pasmo poniżej progu dopasowania')
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'39_P14B_maly_sygnal_i_potegi.{ext}',dpi=170)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,6))
    for cid,color in [('C05','C0'),('C17','C1')]:
        for initial,marker in [(-.6,'o'),(.6,'^')]:
            rows=[r for r in preload if r['candidate_id']==cid and float(r['initial_q'])==initial]
            ax.scatter([float(r['steady_catalog_x_fraction']) for r in rows],[float(r['startup_catalog_x_fraction']) for r in rows],
                       marker=marker,color=color,label=f'{cid}, q0={initial:+g}',s=50,alpha=.75)
    grid=np.linspace(0,1.3,100);ax.plot(grid,grid,'k--',lw=1,label='Rozruch = stan ustalony')
    ax.axhline(1,color='gray',ls=':');ax.axvline(1,color='gray',ls=':')
    ax.set(xlabel='Szczyt ustalony / katalogowe Xmax',ylabel='Szczyt rozruchu / katalogowe Xmax',
           title='Preload: ten sam stan ustalony, różny rozruch\nKatalogowe Xmax jest odniesieniem, nie twardym ogranicznikiem',xlim=(.35,1.15),ylim=(.35,1.3))
    ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'40_P14B_rozruch_i_preload.{ext}',dpi=170)
    plt.close(fig)
    result=dict(status='P14B_STUDIES_REPORTED',
        max_preload_X_complex_relative_difference=max(float(r['X_band_complex_relative_change']) for r in preload),
        max_preload_I_complex_relative_difference=max(float(r['I_band_complex_relative_change']) for r in preload),
        nonresolved_scaling_fits=[r for r in summary['small_signal_fits'] if r['status']!='RESOLVED_LOG_SLOPE'],
        IM2_slope_range=[min(r['slope'] for r in summary['small_signal_fits'] if r['metric']=='IM2_pct' and 'slope' in r),max(r['slope'] for r in summary['small_signal_fits'] if r['metric']=='IM2_pct' and 'slope' in r)],
        IM3_slope_range=[min(r['slope'] for r in summary['small_signal_fits'] if r['metric']=='IM3_difference_pct' and 'slope' in r),max(r['slope'] for r in summary['small_signal_fits'] if r['metric']=='IM3_difference_pct' and 'slope' in r)],
        scope='Wykonany zbiór rodzin, nie wszystkie możliwe fazy/atraktory, brak THD realnych produktów i dynamiki cieplnej wP14B.')
    (OUT/'p14b_interpretacja.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
