"""P20A: najważniejsze kompromisy i jawne ograniczenia przestrzennego modelu."""
from pathlib import Path
import csv,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_gazu import Medium
from model_wkladu_P20A import HollowModule

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):return list(csv.DictReader((OUT/name).open()))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    cfgpath=ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json';cfg=json.loads(cfgpath.read_text());medium=Medium()
    layouts=read('p20a_dostep_i_uklad.csv');models=read('p20a_moduly_i_sciany.csv');ports=read('p20a_porty_modulow.csv')
    neck=read('p20a_kanaliki_porty.csv');peaks=read('p20a_kanaliki_piki_i_dziedzina.csv');mount=read('p20a_dynamika_mocowan.csv')
    balances=json.loads((OUT/'p20a_podsumowanie.json').read_text())['balances']
    source_geometry=json.loads((ROOT/'dane/zrodla/P18B_geometria_i_ograniczenia.json').read_text())
    driver_geometry=next(r['facts'] for r in source_geometry['sources'] if r['source_id']=='SRC03')
    frame=json.loads((ROOT/'dane/konfiguracje/p18c_rama_3D.json').read_text())
    # CSV listowy jest tylko prezentacją; do obliczeń używamy pól JSON z liczbami.
    source=json.loads((OUT/'p20a_tory_montazu.json').read_text())['layouts']
    chosen=[next(r for r in source if r['ties']==1 and r['opening_nominal_m']==.3052 and r['outer_width_length_height_m']==[.18,c,.17]) for c in [.1,.125,.2,.4]]
    xs=np.arange(4);fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    ax[0].bar(xs-.17,[r['nominal_grid_slots'] for r in chosen],width=.34,label='Pozycje geometryczne',color='#b1bdc6')
    ax[0].bar(xs+.17,[r['accepted_modules'] for r in chosen],width=.34,label='Zweryfikowana sekwencja wsuwania',color='#258299')
    ax[0].set(xticks=xs,xticklabels=['100','125','200','400'],xlabel='Długość wkładu [mm]',ylabel='Liczba wkładów',title='Przekrój 180×170 mm, otwór nominalny 305,2 mm, jeden ściąg')
    ax[0].legend(fontsize=8)
    hollow=[];solid=[]
    for r in chosen:
        c=r['outer_width_length_height_m'][1]
        m=next(x for x in models if x['outer_a_m']=='0.18' and float(x['outer_depth_m'])==c and x['wall_mm']=='8.0' and x['boundary']=='CCCC' and x['braced']=='False')
        hollow.append(r['accepted_modules']*float(m['dry_mass_kg']))
        solid.append(r['accepted_modules']*np.prod(r['outer_width_length_height_m'])*cfg['mdf_density_kg_m3_assumed'])
    ax[1].bar(xs-.17,solid,width=.34,label='Masywne MDF',color='#777')
    ax[1].bar(xs+.17,hollow,width=.34,label='Puste MDF 8 mm, bez ściągu',color='#cf7200')
    ax[1].set(xticks=xs,xticklabels=['100','125','200','400'],xlabel='Długość wkładu [mm]',ylabel='Masa zestawu na zweryfikowanym torze [kg]',title='Ta sama objętość zewnętrzna, różna masa')
    ax[1].legend(fontsize=8)
    for a in ax:a.grid(axis='y',alpha=.25)
    fig.suptitle('Nominalny układ kontrolny; translacje osiowe, bez dowodu globalnego maksimum',fontsize=11)
    save(fig,'70_P20A_dostep_i_masa_wkladow')
    outer=cfg['selected_comparison_outer_width_length_height_m']
    specs=[('SSSS',False,'8 mm SSSS','#cf7200'),('CCCC',False,'8 mm CCCC','#6956a5'),
           ('SSSS',True,'8 mm SSSS + ściąg','#258299'),('CCCC',True,'8 mm CCCC + ściąg','#222')]
    fig,ax=plt.subplots(1,2,figsize=(12,4.8));freq=np.geomspace(10,100,250)
    for bc,tied,label,color in specs:
        m=HollowModule(outer,.008,bc,cfg,braced=tied);r=m.port(freq)
        ax[0].semilogx(freq,r['effective_compliance'].real*medium.gamma*medium.p0_pa*1e6,label=label,color=color)
    ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='Równoważna podatność odzyskana przez wkład [ml]',title='Szczelny moduł 3,06 l, gaz adiabatyczny')
    ax[0].legend(fontsize=8);ax[0].grid(True,which='both',alpha=.25)
    base_air=balances['host_geometry_l']-balances['fixed_explicit_solids_l']-4-balances['liner_solid_volume_l']
    for corner,label,color in [(0.,'Szczelny','#222'),(1.,'fc_ref=1 Hz','#258299'),(10.,'fc_ref=10 Hz','#6956a5'),(100.,'fc_ref=100 Hz','#cf7200'),(np.inf,'Otwarty, formalna granica','#a95353')]:
        m=HollowModule(outer,.008,'CCCC',cfg,braced=True);C=m.port(np.array([20.]),1.4,corner)['effective_compliance'][0].real
        ns=np.arange(17);equivalent=base_air-ns*np.prod(outer)*1000+ns*medium.gamma*medium.p0_pa*C*1000
        ax[1].plot(ns,equivalent,label=label,color=color)
    ax[1].set(xlabel='Liczba modułów',ylabel='Dynamiczna objętość równoważna [l]',title='20 Hz; wyporność 4 l jako scenariusz, bez strat włókniny')
    ax[1].legend(fontsize=8);ax[1].grid(alpha=.25)
    fig.suptitle('Podatność ścian i przeciek są osobnymi składnikami bilansu; bez pomiaru wyrobu',fontsize=11)
    save(fig,'71_P20A_podatnosc_i_szczelnosc_modulu')
    fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    for radius,color in zip([.5,1.,2.],['#258299','#6956a5','#cf7200']):
        r=[x for x in neck if float(x['radius_mm'])==radius and x['end_length_in_r']=='1.0']
        ax[0].loglog([float(x['f_hz']) for x in r],[float(x['module_admittance_real']) for x in r],label=f'r={radius:g} mm',color=color)
        ax[1].loglog([float(x['f_hz']) for x in r],[float(x['screen_outer_pa_rms']) for x in r],label=f'r={radius:g} mm',color=color)
    ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='Re(Y modułu) [m³/(Pa·s)]',title='Kanał z lepką bezwładnością; dodatkowa masa końców 1r')
    ax[1].axhline(1.,ls='--',color='#b24d42',label='1 Pa RMS jako porównanie')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='Umowny ekran ciśnienia zewnętrznego [Pa RMS]',title='Mała amplituda: ξpeak/r≤0,1 i Machpeak≤0,03')
    for a in ax:a.legend(fontsize=8);a.grid(True,which='both',alpha=.25)
    fig.suptitle('Rodzina teoretyczna, nie otwór do wykonania; poza ekranem nie prognozować przepływu/SPL',fontsize=11)
    save(fig,'72_P20A_kanalik_i_dziedzina_amplitudy')
    mass=float(next(r['mass_with_sealed_air_kg'] for r in models if r['module_id']=='TIE_8_CCCC'))
    fig,ax=plt.subplots(1,2,figsize=(12,4.8));f=np.geomspace(10,500,900)
    for k,color in zip(cfg['mount_each_stiffness_n_m'],['#cf7200','#6956a5','#258299']):
        K=4*k;w0=np.sqrt(K/mass);C=2*cfg['mount_damping_ratio_assumed']*np.sqrt(K*mass);w=2*np.pi*f
        relative=mass/abs(K-mass*w*w+1j*C*w);reaction=abs(K+1j*C*w)*relative
        ax[0].loglog(f,relative*1e6,label=f'k={k:g} N/m na podporę',color=color)
        ax[1].semilogx(f,np.sqrt(2)*reaction/(mass*9.80665),label=f'k={k:g}',color=color)
    ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='Względny ruch RMS [µm]',title='Sztywne ciało na czterech podporach, ζ=0,03')
    ax[1].axhline(1,color='#b24d42',ls='--',label='Próg utraty kontaktu')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='Szczyt siły dynamicznej / ciężar',title='Flagowane wyniki nie opisują luźnego kontaktu po otwarciu')
    for a in ax:a.grid(True,which='both',alpha=.25)
    ax[0].legend(fontsize=8);ax[1].legend(fontsize=8,loc='lower left')
    fig.suptitle('Wkład referencyjny 0,703 kg; wymuszenie podstawy 1 m/s² RMS, nie rzeczywiste drgania skrzyni',fontsize=11)
    save(fig,'73_P20A_dynamika_mocowania_wkladu')
    spatial=[]
    for r in models:
        dims=np.array([float(r['outer_a_m']),float(r['outer_depth_m']),float(r['outer_b_m'])])-2*float(r['wall_mm'])*.001
        axial=medium.c/(2*max(dims));pressure=float(r['pressure_coupled_frequency_kappa14_hz'])
        spatial.append(dict(module_id=r['module_id'],empty_rigid_inner_box_axial_reference_hz=axial,
            formal_uniform_gas_pressure_mode_hz=pressure,formal_mode_geq_first_empty_inner_box_mode=bool(pressure>=axial),
            probe80_to_empty_box_axial_ratio=80/axial,
            scope='Reference only: flag excludes interpreting high formal 0D eigenfrequency as measured or validated physical resonance.'))
    path_nonzero=sum(np.linalg.norm(np.array(b)-a)>1e-12 for r in source for path in r['paths'] for a,b in zip(path[:-1],path[1:]))
    chosen_row=next(r for r in models if r['module_id']=='TIE_8_CCCC')
    p20_drive=json.loads((OUT/'p20a_naped_podsumowanie.json').read_text())
    base_fixed=balances['fixed_explicit_solids_l'];liner_mass=balances['liner_dry_mass_kg'];W,D,H=cfg['inside_width_depth_height_m'];h=cfg['host_wall_thickness_m'];rho=cfg['mdf_density_kg_m3_assumed']
    panel_volume=(W+2*h)*(D+2*h)*(H+2*h)-W*D*H-np.pi*frame['hole_radius_m']**2*h
    mass_host=rho*(panel_volume+base_fixed*.001)+driver_geometry['net_mass_kg']+liner_mass
    result=dict(status='INSERT_SELECTION_GUIDANCE_WITH_UNQUALIFIED_MATERIAL_SPATIAL_AND_MOUNT_GATES',
        constructive_nonzero_translation_segments=int(path_nonzero),selected_module_count=16,
        selected_outer_volume_l=np.prod(outer)*1000,selected_set_geometric_exclusion_l=16*np.prod(outer)*1000,
        selected_braced_dry_mass_kg=float(chosen_row['dry_mass_kg']),selected_braced_sealed_air_mass_kg=mass,
        selected_set_dry_mass_kg=16*float(chosen_row['dry_mass_kg']),solid_same_set_mass_kg=16*rho*np.prod(outer),
        conditional_nominal_host_and_filler_mass_kg=mass_host,
        conditional_nominal_mass_with_braced_insert_set_kg=mass_host+16*mass,
        conditional_nominal_mass_with_solid_insert_set_kg=mass_host+16*rho*np.prod(outer),
        mass_scope='Nominal C04 circle/geometric frame/density assumptions, no hardware/glue/rails; not weighed prototype or guaranteed bound.',
        drive_point_cases=p20_drive['point_cases'],spatial_mode_diagnostics=spatial,
        spatially_unqualified_formal_mode_count=sum(r['formal_mode_geq_first_empty_inner_box_mode'] for r in spatial),
        next='P20B:porownac szczelna przegrode wkilku pozycjach z modulem referencyjnym100mm;potem pelne3D wybranejmetody i P21. Dla modulu wymagane osobneporty cisnienia zewnetrznego/wewnetrznego.',
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            cfgpath,Path(__file__),ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/model_plyty_MITC_P18.py',ROOT/'skrypty/model_gazu.py',
            ROOT/'dane/zrodla/P18B_geometria_i_ograniczenia.json',ROOT/'dane/konfiguracje/p18c_rama_3D.json',OUT/'p20a_podsumowanie.json',
            OUT/'p20a_dostep_i_uklad.csv',OUT/'p20a_tory_montazu.json',OUT/'p20a_moduly_i_sciany.csv',OUT/'p20a_porty_modulow.csv',
            OUT/'p20a_kanaliki_porty.csv',OUT/'p20a_kanaliki_piki_i_dziedzina.csv',OUT/'p20a_dynamika_mocowan.csv',OUT/'p20a_naped_podsumowanie.json']})
    (OUT/'p20a_ocena_projektowa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20A report:16 modules,',p20_drive['point_cases'],'drive points;',result['spatially_unqualified_formal_mode_count'],'formal modes above empty-box reference.',flush=True)


if __name__=='__main__':main()
