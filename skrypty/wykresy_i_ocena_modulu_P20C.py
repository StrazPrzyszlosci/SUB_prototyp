"""P20C: wpływ3D na regulator, klej i napęd, z jawnymi flagami siatki."""
from pathlib import Path
import csv,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from naped_z_przegroda_P20B import ModuleReference
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as stream:return list(csv.DictReader(stream))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    cp=ROOT/'dane/konfiguracje/p20c_modul_pelny_3D.json';cfg=json.loads(cp.read_text());bp=ROOT/cfg['reference_insert_config'];base=json.loads(bp.read_text())
    ports=read('p20c_gaz_i_przeciek.csv');models=read('p20c_modele_3D.csv');joints=read('p20c_spoiny_statystyki.csv')
    roots=read('p20c_wymagany_modul_kleju.csv');curves=read('p20c_klej_ciagla_krzywa.csv');drive=read('p20c_naped_27_konfiguracji.csv')
    mesh=read('p20c_niezalezna_siatka_i_wspolne_Hz.csv');refine=read('p20c_dalsza_siatka_przy_modach.csv')
    n0,n1=cfg['mesh_resolution_cases'][-2:];last=max(cfg['mesh_resolution_cases']);probe_diff=[];joint_diff=[]
    def port(case,f):
        return next(r for r in ports if r['case_id']==case and float(r['f_hz'])==f and float(r['gas_kappa'])==1.4 and r['leak_100l_reference_corner_hz']=='0.0')
    for braced in [False,True]:
        for eg in cfg['glue_E_pa_cases_assumed']:
            key=f"{'TIED' if braced else 'BARE'}_E{eg:g}"
            for f in cfg['probe_frequencies_hz']:
                a,b=port(f'{key}_N{n0}',f),port(f'{key}_N{n1}',f)
                za=complex(float(a['admittance_re_m3_pa_s']),float(a['admittance_im_m3_pa_s']));zb=complex(float(b['admittance_re_m3_pa_s']),float(b['admittance_im_m3_pa_s']))
                probe_diff.append(dict(family=key,f_hz=f,relative_complex_admittance_change=float(abs(zb/za-1)),
                    storage_relative_change=float(float(b['returned_storage_l'])/float(a['returned_storage_l'])-1)))
            old={r['joint']:r for r in joints if r['case_id']==f'{key}_N{n0}'}
            for r in [r for r in joints if r['case_id']==f'{key}_N{n1}']:
                row=dict(family=key,joint=r['joint'])
                for field in ['spatial_normal_rms_pa','spatial_positive_normal_rms_pa','spatial_shear_rms_pa','sampled_gauss_positive_normal_max_pa']:
                    a,b=float(old[r['joint']][field]),float(r[field]);row[field+'_relative_change']=None if abs(a)<1e-20 else b/a-1
                joint_diff.append(row)
    table('p20c_ocena_siatki_w_pasmie.csv',probe_diff);table('p20c_roznice_statystyk_spoin.csv',joint_diff)
    fig,ax=plt.subplots(1,2,figsize=(12,5.5));colors=['#cf7200','#6956a5','#258299']
    for eg,color in zip(cfg['glue_E_pa_cases_assumed'],colors):
        values=[1000*float(port(f'TIED_E{eg:g}_N{n}',20.)['returned_storage_l']) for n in cfg['mesh_resolution_cases']]
        ax[0].plot(cfg['mesh_resolution_cases'],values,'o-',color=color,label=f'E kleju {eg/1e6:g} MPa')
    ax[0].set(xlabel='Parametr zagęszczenia n (geometria niezmienna)',ylabel='Odtwarzana podatność × γp₀ [ml / moduł]',title='Pełne 3D ze ściągiem; 20 Hz, szczelny gaz')
    ax[0].legend(fontsize=8)
    f=np.array(cfg['probe_frequencies_hz']);case=f'TIED_E{max(cfg["glue_E_pa_cases_assumed"]):g}_N{last}'
    full=np.array([float(port(case,v)['returned_storage_l']) for v in f]);thin=ModuleReference(base,dict(material_loss_zeta_at_reference_assumed=cfg['material_loss_zeta_at_reference_assumed'],material_loss_reference_hz=cfg['material_loss_reference_hz']),f)
    thin_return=(thin.admittance/(2j*np.pi*f)*1.4*101325*1000).real
    p20b=read('p20b_dwie_komory_i_nieszczelnosc.csv')
    part=[next(r for r in p20b if r['model_id']=='T18_PERIM_CCCC_RIGID' and r['module_count_equivalent']=='16' and r['host']=='FIXED' and r['lining']=='LINER_GEOMETRY' and r['rear_kappa']=='1.4' and r['seal_100l_reference_corner_hz']=='0.0' and r['vent_100l_reference_corner_hz']=='0.0' and float(r['f_hz'])==v) for v in f]
    ax[1].plot(f,16*full,'o-',color='#258299',label='16 modułów, pełne 3D, E kleju 1718 MPa')
    ax[1].plot(f,16*thin_return,'s--',color='#777',label='16 modułów, model płyt CCCC')
    ax[1].plot(f,[float(r['added_equivalent_storage_l']) for r in part],'^-',color='#cf7200',label='Przegroda 18 mm, nieruchomy obwód')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='Re(dodatkowej podatności) × γp₀ [l]',title='Z przodu 80,835 l; wspólne βK, szczelność')
    ax[1].legend(fontsize=8)
    for a in ax:a.grid(alpha=.25)
    fig.suptitle('Rodziny kontrolne; pojedyncze sinusy i jednolity gaz 0D; konstrukcja pozostaje otwarta',fontsize=11)
    save(fig,'78_P20C_siatka_i_porownanie_regulatorow')
    fig,ax=plt.subplots(1,2,figsize=(12,5.5))
    for n,color in [(n0,'#777'),(n1,'#258299')]:
        rr=[r for r in curves if int(r['mesh_resolution'])==n]
        ax[0].semilogx([float(r['glue_E_pa'])/1e6 for r in rr],[float(r['relative_to_stiff_reference']) for r in rr],'o-',label=f'n={n}',color=color)
    ax[0].axhline(1.05,color='#cf7200',ls='--',label='1,05 × C(Eref): kryterium porównawcze')
    r=next(r for r in roots if int(r['mesh_resolution'])==n1 and float(r['relative_allowance_vs_reference'])==.05)
    ax[0].axvline(float(r['required_glue_E_pa'])/1e6,color='#cf7200',ls=':')
    ax[0].set(xlabel='Założony moduł Younga kleju [MPa]',ylabel='Ceff / Ceff(Eref = 1718 MPa)',title='Statyka, gaz izotermiczny; kryterium porównawcze')
    ax[0].legend(fontsize=8)
    rr=[r for r in joints if r['case_id']==case];rr=sorted(rr,key=lambda r:float(r['spatial_positive_normal_rms_pa']),reverse=True)[:6]
    xs=np.arange(len(rr))
    ax[1].barh(xs-.17,[float(r['spatial_positive_normal_rms_pa'])/1000 for r in rr],height=.34,label='RMS dodatniej składowej normalnej',color='#cf7200')
    ax[1].barh(xs+.17,[float(r['spatial_shear_rms_pa'])/1000 for r in rr],height=.34,label='RMS ścinania',color='#258299')
    ax[1].set(yticks=xs,yticklabels=[r['joint'] for r in rr],xlabel='Przestrzenne statystyki naprężenia [kPa]',title='6 największych dodatnich RMS; offset 1000 Pa')
    ax[1].invert_yaxis();ax[1].legend(fontsize=7,loc='upper center',bbox_to_anchor=(.5,-.17))
    for a in ax:a.grid(alpha=.25)
    fig.suptitle('Liniowe spoiny 3D; statystyki naprężeń wymagają osobnej oceny nośności, adhezji i trwałości',fontsize=10)
    save(fig,'79_P20C_modul_kleju_i_statystyki_spoin')
    fig,ax=plt.subplots(1,2,figsize=(13,5.0));selected=[r for r in models if int(r['mesh_resolution'])==last]
    xs=np.arange(len(selected));labels=[('Ze ściągiem' if r['braced']=='True' else 'Bez ściągu')+'\n'+f"{float(r['glue_E_pa'])/1e6:g}MPa" for r in selected]
    ax[0].bar(xs-.17,[float(r['first_dry_elastic_hz']) for r in selected],width=.34,label='Pierwsza postać mechaniczna',color='#258299')
    ax[0].bar(xs+.17,[float(r['first_of_retained_pressure_active_hz']) for r in selected],width=.34,label='Pierwsza z istotnym portem wśród 24',color='#cf7200')
    ax[0].axhline(float(selected[0]['empty_cavity_reference_hz']),color='#a95353',ls='--',label='Odniesienie pustej komory,nie ścisła granica')
    ax[0].set(xticks=xs,xticklabels=labels,ylabel='Częstotliwość [Hz]',title='Gaz 0D: otwarta walidacja modów przy odniesieniu')
    ax[0].tick_params(axis='x',labelsize=7);ax[0].legend(fontsize=7)
    for eg,color in zip(cfg['glue_E_pa_cases_assumed'],colors):
        vals=[]
        for frequency in f:
            vv=[abs(float(r['difference_vs_thin_same_G_db'])) for r in drive if r['regulator_case']==f'TIED_E{eg:g}_N{last}' and float(r['f_hz'])==frequency and r['within_assumed_amplitude_screen']=='True']
            vals.append(max(vv))
        ax[1].plot(f,vals,'o-',color=color,label=f'E kleju {eg/1e6:g} MPa')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='Największe |Δ obwiedni| względem płyt [dB]',title='27 konfiguracji, 4 liczby modułów, 2 napędy, 3 przecieki')
    ax[1].legend(fontsize=8)
    for a in ax:a.grid(axis='y',alpha=.25)
    fig.suptitle('Prawy panel: punkty w umownych ekranach amplitudy; RMS 2π/1 m, osobne sinusy; termika/THD otwarte',fontsize=10)
    save(fig,'80_P20C_mody_dziedzina_gazu_i_wplyw_na_naped')
    original=[r for r in mesh if r['within_assumed_5pct_port_screen']=='False']
    resolution={(r['reference_case'],r['f_hz']):r for r in refine}
    unresolved=[r for r in original if (r['reference_case'],r['f_hz']) not in resolution or resolution[(r['reference_case'],r['f_hz'])]['within_assumed_5pct_port_screen']!='True']
    valid=[r for r in drive if r['within_assumed_amplitude_screen']=='True'];worst=max(valid,key=lambda r:abs(float(r['difference_vs_thin_same_G_db'])))
    inputs=[cp,bp,Path(__file__),ROOT/'skrypty/naped_z_przegroda_P20B.py',ROOT/'skrypty/model_wkladu_P20A.py',
        *[OUT/n for n in ['p20c_gaz_i_przeciek.csv','p20c_modele_3D.csv','p20c_spoiny_statystyki.csv','p20c_wymagany_modul_kleju.csv','p20c_klej_ciagla_krzywa.csv',
        'p20c_naped_27_konfiguracji.csv','p20c_niezalezna_siatka_i_wspolne_Hz.csv','p20c_dalsza_siatka_przy_modach.csv','p20b_dwie_komory_i_nieszczelnosc.csv']]]
    j=dict(status='SCOPED_3D_REGULATOR_FINDINGS_WITH_EXPLICIT_MESH_AND_MATERIAL_GATES',original_resonance_mesh_flags=len(original),unresolved_resonance_mesh_flags=len(unresolved),
        max_probe_complex_admittance_change=max(r['relative_complex_admittance_change'] for r in probe_diff),
        full3d_reference_returned_storage_20hz_l=float(full[0]),thin_reference_returned_storage_20hz_l=float(thin_return[0]),
        reference_relative_change_from_thin_at20hz=float(full[0]/thin_return[0]-1),
        max_within_screen_abs_driver_delta_db=abs(float(worst['difference_vs_thin_same_G_db'])),within_screen_max_driver_witness=worst,
        stress_note='Spatial RMS and Gauss samples,not a physical corner peak or strength.',
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        next='P21B: przestrzenne pole gazu wewnątrz modułu z energią i sprzężeniem do ścian3D,porównanie z0D;potem główna komora z regulacją i włókniną. W razie nierozstrzygniętych flag najpierw dalsza siatkaP20C.',
        limitations=['N12driver comparison remains a numerical approximation;N16 witnesses are separate.',
            'Matched assumed models do not supply physical glue relaxation,adhesion,Gc,S-N or actual driver THD.',
            'Same leak conductance and geometry are necessary for comparing labelled corners.'])
    (OUT/'p20c_ocena_projektowa.json').write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20C figures78–80;unresolved mesh flags',len(unresolved),'max valid driver delta',j['max_within_screen_abs_driver_delta_db'],flush=True)


if __name__=='__main__':main()
