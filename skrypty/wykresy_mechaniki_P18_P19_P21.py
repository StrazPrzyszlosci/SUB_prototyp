"""Własne wykresy naukowe; bez wizualnego udawania wykonanego prototypu."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as h:return list(csv.DictReader(h))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/(name+'.'+ext),dpi=170)
    plt.close(fig)


def tie_label(number):return ['0 ściągów','1 ściąg','2 ściągi'][number]


def main():
    plates=read('p18a_plyty_i_sciagi.csv');dynamic=read('p18a_dynamika.csv');joints=read('p19a_normalne_naprezenia.csv')
    sound=read('p21a_para_scian_z_reakcja_powietrza.csv');slips=read('p19a_zespolenie_i_wymagane_G.csv');leaks=read('p19a_otwarte_szczeliny_i_dziedzina.csv')
    base=[r for r in plates if r['geometry_id']=='K2_side' and r['material_id']=='REFERENCE' and not r.get('edge_beta') and not r.get('joint_factor') and float(r['zeta'])==.03]
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for ties in [0,1,2]:
        for boundary,style in [('SSSS','o--'),('CCCC','s-')]:
            rows=sorted([r for r in base if int(r['tie_count'])==ties and r['boundary']==boundary],key=lambda r:float(r['thickness_mm']))
            x=[float(r['thickness_mm']) for r in rows];label=f'{tie_label(ties)}, {boundary}'
            axes[0].plot(x,[float(r['first_mode_hz']) for r in rows],style,color=f'C{ties}',label=label)
            axes[1].semilogy(x,[float(r['static_max_w_m'])*1e6 for r in rows],style,color=f'C{ties}',label=label)
    axes[0].set(xlabel='Grubość MDF [mm]',ylabel='Pierwsza częstotliwość własna [Hz]',title='Panel 460 × 640 mm; symetryczne rozsuwanie ścian')
    axes[1].set(xlabel='Grubość MDF [mm]',ylabel='Maksimum węzłowego ugięcia [µm]',title='Zadane 1 kPa statyczne; materiał referencyjny')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=7,ncol=2)
    save(fig,'43_P18A_grubosc_sciagi_i_ugiecie')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for ties in [0,1,2]:
        row=next(r for r in base if r['boundary']=='SSSS' and int(r['tie_count'])==ties and float(r['thickness_mm'])==22)
        part=sorted([r for r in dynamic if r['case_id']==row['case_id']],key=lambda r:float(r['f_hz']))
        axes[0].loglog([float(r['f_hz']) for r in part],[float(r['peak_w_at_given_pressure_m'])*1e6 for r in part],label=tie_label(ties))
        part=[r for r in sound if r['boundary']=='SSSS' and int(r['tie_count'])==ties and float(r['f_hz']) in [20.,40.,80.]]
        part=sorted(part,key=lambda r:float(r['f_hz']))
        axes[1].plot([float(r['f_hz']) for r in part],[float(r['maximum_node_displacement_ratio_with_to_without_air']) for r in part],'o-',label=tie_label(ties))
    axes[0].axvspan(20,80,color='gray',alpha=.1);axes[0].set(xlabel='f [Hz]',ylabel='Szczyt ugięcia [µm]',title='Sucha płyta; 1 kPa RMS w każdym OSOBNYM tonie')
    axes[1].axhline(1,color='gray',ls=':');axes[1].set(xlabel='f [Hz]',ylabel='Amplituda z reakcją powietrza / sucha',title='Ta sama jednostkowa presja; zakres 20–80 Hz')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    save(fig,'44_P18A_dynamika_i_reakcja_powietrza')
    summary=json.loads((OUT/'p18a_podsumowanie.json').read_text());cache=ROOT/summary['checkpoint_folder']
    fig,axes=plt.subplots(1,3,figsize=(11,5.5))
    for ties,ax in zip([0,1,2],axes):
        row=next(r for r in base if r['boundary']=='SSSS' and int(r['tie_count'])==ties and float(r['thickness_mm'])==22)
        arrays=np.load(cache/(row['case_id']+'.npz'),allow_pickle=False);vec=arrays['modes'][:,0];full=np.zeros(3*len(arrays['xy']));full[arrays['free']]=vec
        field=full[0::3];field=field/np.max(abs(field));field*=np.sign(field[np.argmax(abs(field))])
        nx=int(row['mesh_nx']);ny=int(row['mesh_ny']);X=arrays['xy'][:,0].reshape(ny+1,nx+1);Y=arrays['xy'][:,1].reshape(ny+1,nx+1)
        im=ax.pcolormesh(X,Y,field.reshape(ny+1,nx+1),cmap='coolwarm',vmin=-1,vmax=1,shading='auto')
        if ties:
            for y in ([.32] if ties==1 else [.64/3,2*.64/3]):ax.add_patch(Rectangle((.23-.04,y-.04),.08,.08,fill=False,edgecolor='black',lw=1.2))
        participation=json.loads(row['modal_uniform_pressure_static_compliance_fractions'])[0]
        pct='~0% (symetria)' if participation<1e-10 else f'{participation*100:.2g}%'
        ax.set_aspect('equal');ax.set(xlabel='u panelu [m]',ylabel='v panelu [m]' if ties==0 else '')
        ax.set_title(f"{tie_label(ties)}; f1={float(row['first_mode_hz']):.1f} Hz\nUdział p: {pct}",fontsize=11)
    # Ręczny układ rezerwuje miejsce na wspólną skalę,bez ściskania etykiet.
    fig.subplots_adjust(left=.06,right=.84,wspace=.38,top=.82,bottom=.12)
    cax=fig.add_axes([.89,.23,.02,.5]);fig.colorbar(im,cax=cax,label='Względne w: znak arbitralny')
    for ext in ['png','svg']:fig.savefig(OUT/f'45_P18A_postacie_drgan.{ext}',dpi=170)
    plt.close(fig)
    relaxed=read('p19a_relaksacja_wymagania.csv');fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for boundary in ['SSSS','CCCC']:
        part=sorted([r for r in relaxed if r['boundary']==boundary and float(r['gap_m'])==.0002],key=lambda r:float(r['assumed_relaxed_E_pa']))
        x=[float(r['assumed_relaxed_E_pa'])/1e6 for r in part]
        axes[0].semilogx(x,[float(r['normal_peak_at1kpa_pa'])/1000 for r in part],'o-',label=boundary)
        axes[1].semilogx(x,[float(r['compliance_to_reference']) for r in part],'o-',label=boundary)
    axes[0].set(xlabel='Hipotetyczny moduł długoczasowy [MPa]',ylabel='Nominalny szczyt naprężenia normalnego [kPa]',title='Nakładka 80 × 80 × 18 mm; zadane 1 kPa')
    axes[1].axhline(1.1,color='gray',ls=':',label='Umowna bramka +10%');axes[1].set(xlabel='Hipotetyczny moduł długoczasowy [MPa]',ylabel='Podatność objętościowa / odniesienie',title='Wrażliwość na moduł długoczasowy')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    save(fig,'46_P19A_normalna_podatnosc_i_odrywanie')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for thickness in [.012,.018,.022]:
        part=sorted([r for r in joints if r['boundary']=='SSSS' and r['E_profile']=='EA9466_FILM_TYPICAL' and float(r['gap_m'])==.0002 and float(r['Ez_factor'])==.15 and float(r['t_m'])==thickness and float(r['eccentricity_m'])==0 and r['defect']=='NONE'],key=lambda r:float(r['size_m']))
        x=[float(r['size_m'])*1000 for r in part];label=f'h nakładki = {thickness*1000:g} mm'
        axes[0].plot(x,[float(r['maximum_to_mean_normal_stress_factor']) for r in part],'o-',label=label)
        axes[1].plot(x,[float(r['maximum_static_normal_stress_pa'])/1000 for r in part],'o-',label=label)
    axes[0].set(xlabel='Bok nakładki [mm]',ylabel='Maksimum naprężenia normalnego / średnia',title='Podatność nakładki zmienia rozkład naprężeń')
    axes[1].set(xlabel='Bok nakładki [mm]',ylabel='Szczyt modelowego naprężenia normalnego [kPa]',title='Ciśnienie wewnętrzne 1 kPa; podatna nakładka')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    save(fig,'47_P19A_nakladka_i_koncentracja_naprezen')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for gap in [.0002,.0005]:
        part=sorted([r for r in slips if float(r['length_m'])==.5 and float(r['glue_gap_m'])==gap and float(r['modulus_retention_stress'])==1],key=lambda r:int(r['mode']))
        axes[0].semilogy([int(r['mode']) for r in part],[float(r['required_G_for_95pct_composite_pa'])/1e6 for r in part],'o-',label=f'h spoiny={gap*1e6:g} µm')
    axes[0].axhline(1718/(2*1.35),color='gray',ls=':',label='G z typowego E; nu=0,35 założone')
    axes[0].set(xlabel='Nr półfali osiowej m; długość pasa 0,5 m',ylabel='Wymagane G [MPa]',title='95% idealnego zespolenia dwóch pełnych 18 mm')
    for f in [20.,80.]:
        part=sorted([r for r in leaks if float(r['width_m'])==.005 and float(r['path_length_m'])==.022 and float(r['pressure_amplitude_pa'])==1000 and float(r['f_hz'])==f],key=lambda r:float(r['open_gap_height_m']))
        x=np.array([float(r['open_gap_height_m'])*1e6 for r in part]);v=np.array([float(r['AC_peak_mean_speed_m_s']) for r in part]);valid=np.array([r['in_declared_conservative_flow_domain']=='True' for r in part])
        axes[1].loglog(x[valid],v[valid],'o-',label=f'{f:g} Hz, dziedzina liniowa')
        axes[1].loglog(x[~valid],v[~valid],'x',label=f'{f:g} Hz, formalne poza dziedziną')
    axes[1].set(xlabel='Wysokość PUSTEJ szczeliny [µm]',ylabel='Średnia prędkość szczytowa w kanale [m/s]',title='1 kPa peak; otwarty kanał, nie wypełniony klej')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=7)
    save(fig,'48_P19A_zespolenie_i_otwarta_szczelina')
    print('Wygenerowano wykresy43–48: modele,nie pomiary obudowy.')


if __name__=='__main__':main()
