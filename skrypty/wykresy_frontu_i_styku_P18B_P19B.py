"""Własne wykresy P18B/P19B; dane nominalne i hipotezy opisane w podpisach."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from model_frontu_z_otworem_P18B import FrontWithHole,PlateMaterial

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))


def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=160);fig.savefig(OUT/(name+'.svg'));plt.close(fig)


def main():
    rows=read('p18b_fronty_i_mocowania.csv');coupled=read('p18b_ruch_zadany_i_komora.csv')
    pre=read('p19b_docisk_i_styk.csv');dyn=read('p19b_dynamika_i_bramki_styku.csv')
    fig,axs=plt.subplots(1,2,figsize=(11,5),layout='constrained')
    for ax,cid,r,rb in zip(axs,['C04 / SB34','C02 / RSS390'],[.1526,.1779],[.1621,.184]):
        p=FrontWithHole(.46,.46,r,PlateMaterial(2.1e9,.3,730,.022),12,6)
        segments=[p.xy[np.r_[nodes,nodes[0]]]*1000 for nodes in p.elements]
        ax.add_collection(LineCollection(segments,colors='#718096',linewidths=.35))
        for phi in np.arange(8)*2*np.pi/8:
            ax.add_patch(Circle((rb*np.cos(phi)*1000,rb*np.sin(phi)*1000),4,color='#d94801'))
        ax.set(xlim=(-240,240),ylim=(-240,240),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',
               title=f'{cid}: nominalny otwór Ø{r*2000:g} mm')
    fig.suptitle('P18B: siatka frontu; rozpiętość podpór 460 × 460 mm\nPomarańczowe łaty Ø8 mm są założeniem modelu mocowań; bez frezu i otworów śrubowych',fontsize=11)
    save(fig,'49_P18B_siatka_frontu_z_otworem')

    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    colors={'C02':'#2166ac','C04':'#b2182b','C06':'#238b45'}
    for cid in colors:
        for bc,style in [('CCCC','-'),('SSSS_HARD','--')]:
            data=sorted([r for r in rows if r['candidate_id']==cid and r['group']=='COMMON_PAYLOAD' and float(r['span_a_m'])==.46 and float(r['spring_each_n_m'])==1e6 and r['boundary']==bc],key=lambda r:float(r['thickness_m']))
            h=[float(r['thickness_m'])*1000 for r in data]
            axs[0].plot(h,[float(r['first_mode_hz']) for r in data],style+'o',color=colors[cid],label=cid+' '+bc)
            axs[1].plot(h,[float(r['force_basket_w_m'])*1e6 for r in data],style+'o',color=colors[cid])
    axs[0].set(ylabel='Pierwsza częstotliwość [Hz]',xlabel='Grubość frontu [mm]');axs[0].legend(fontsize=8,ncol=2)
    axs[1].set(ylabel='Ruch kosza przy osobnym 100 N [µm]',xlabel='Grubość frontu [mm]')
    for ax in axs:ax.grid(alpha=.25);ax.set_xticks([18,22,25])
    fig.suptitle('Porównanie geometrii przy wspólnym umownym ładunku 10 kg\nPodpory 460 × 460 mm, k = 10⁶ N/m na mocowanie; pierwszy mod może być przechyłem kosza',fontsize=11)
    save(fig,'50_P18B_grubosc_i_ruch_kosza')

    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for k,col in [(1e5,'#d73027'),(1e6,'#4575b4'),(1e7,'#1a9850')]:
        data=sorted([r for r in coupled if r['boundary']=='CCCC' and float(r['spring_each_n_m'])==k and float(r['reference_faces'])==2],key=lambda r:float(r['f_hz']))
        f=[float(r['f_hz']) for r in data]
        axs[0].plot(f,[float(r['pressure_pa_rms']) for r in data],'-o',color=col,label=f'k={k:g} N/m')
        axs[1].plot(f,[float(r['basket_motion_rms_m'])/.001*100 for r in data],'-o',color=col)
    for ax in axs:
        ax.set_xscale('log');ax.set_xticks([20,40,80,150,300],labels=['20','40','80','150','300']);ax.grid(alpha=.25)
        ax.axvspan(80,320,color='#dddddd',alpha=.4);ax.set(xlim=(18,320),xlabel='Częstotliwość [Hz]')
    axs[0].set_ylabel('Ciśnienie wewnętrzne [Pa RMS]');axs[0].legend(fontsize=8)
    axs[1].set_ylabel('|ruch kosza / względny ruch stożka| [%]')
    fig.suptitle('C04 / 7,68 kg: zadany względny ruch stożka 1 mm RMS, komora 100 l, front CCCC\n5 próbek częstotliwości; szare tło: ekstrapolacja komory 0D; bez zewnętrznej radiacji i uszczelki',fontsize=10)
    save(fig,'51_P18B_stozek_i_komora_0D')

    fig,axs=plt.subplots(2,2,figsize=(13,9),layout='constrained')
    for ax,kn in zip(axs[0],[1e8,1e9]):
        for bc,col in [('CCCC','#2166ac'),('SSSS_HARD','#b2182b')]:
            data=sorted([r for r in pre if r['boundary']==bc and float(r['contact_kn_pa_m'])==kn],key=lambda r:float(r['initial_force_parameter_n']))
            x=np.array([float(r['initial_force_parameter_n']) for r in data]);lo=np.array([float(r['retained_bolt_min_n']) for r in data]);hi=np.array([float(r['retained_bolt_max_n']) for r in data])
            ax.plot(x,lo,'-o',color=col,label=bc+' min');ax.plot(x,hi,'--o',color=col,label=bc+' max')
        ax.set(title=f'kₙ={kn:g} Pa/m',xlabel='T₀ = kśruby·δ₀ [N] — parametr skrócenia',ylabel='Zachowana siła śruby [N]');ax.grid(alpha=.25);ax.legend(fontsize=8)
    labels=[];values=[]
    for bc in ['CCCC','SSSS_HARD']:
        for kn in [1e8,1e9]:
            for T0 in [25.,100.,400.]:
                labels.append(f'{bc}\n{kn:.0e}/{T0:g}')
                points=[next(r for r in dyn if r['boundary']==bc and float(r['contact_kn_pa_m'])==kn and float(r['initial_force_parameter_n'])==T0 and float(r['reference_faces'])==2 and float(r['f_hz'])==f) for f in [20,40,80]]
                values.append([float(r['opening_area_fraction'])*100 for r in points])
    heat=axs[1,0].imshow(np.array(values).T,aspect='auto',vmin=0,vmax=100,cmap='YlOrRd')
    axs[1,0].set(yticks=[0,1,2],yticklabels=['20','40','80'],xticks=np.arange(12),xticklabels=labels,
                 ylabel='Częstotliwość [Hz]',title='Obszar z flagą możliwego otwierania [%]\nZamrożony styk, 1 mm RMS; nie wynik nieliniowej ODE')
    axs[1,0].tick_params(axis='x',labelsize=6,rotation=90);fig.colorbar(heat,ax=axs[1,0],label='% umownego pola uszczelki')
    for bc,style in [('CCCC','-'),('SSSS_HARD','--')]:
        for kn,col in [(1e8,'#2166ac'),(1e9,'#b2182b')]:
            data=sorted([r for r in pre if r['boundary']==bc and float(r['contact_kn_pa_m'])==kn],key=lambda r:float(r['initial_force_parameter_n']))
            axs[1,1].plot([float(r['initial_force_parameter_n']) for r in data],[float(r['gasket_compression_max_m'])/.003*100 for r in data],style+'o',color=col,label=f'{bc}, {kn:g}')
    axs[1,1].set(xlabel='T₀ [N]',ylabel='Maks. nominalne ściśnięcie / 3 mm [%]',title='Założona grubość 3 mm; brak identyfikacji materiału');axs[1,1].legend(fontsize=7);axs[1,1].grid(alpha=.25)
    fig.suptitle('P19B: jednostronna uszczelka i śruby pracujące tylko na rozciąganie\nC04, front 460 × 460 × 22 mm; grawitacyjny moment dla założonego CG = 80 mm',fontsize=11)
    save(fig,'52_P19B_docisk_i_bramki_styku')
    print('Wykresy49–52 zapisane')


if __name__=='__main__':main()
