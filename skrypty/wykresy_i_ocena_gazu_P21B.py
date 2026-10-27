"""P21B: porównanie pola,portów i siatek; bez rankinguTHDproduktów."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np
from model_ramy_3D_P18C import FACES
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as stream:return list(csv.DictReader(stream))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    cp=ROOT/'dane/konfiguracje/p21b_gaz_przestrzenny_modulu.json';cfg=json.loads(cp.read_text());status=json.loads((OUT/'p21b_podsumowanie.json').read_text())
    assert status['cases']==status['expected_cases']==18
    models=read('p21b_modele_i_geometria.csv');fields=read('p21b_pola_i_energia.csv');comp=read('p21b_porownanie_z0D.csv');mat=read('p21b_macierze_admitancji.csv')
    checks=json.loads((OUT/'p21b_kontrole_niezalezne.json').read_text());n0,n1=cfg['mesh_resolution_cases'][-2:];nmax=max(cfg['mesh_resolution_cases'])
    fine=f'TIED_E{max(cfg["glue_E_pa_cases_assumed"]):g}_N{nmax}';mesh=[]
    for b in [False,True]:
        for eg in cfg['glue_E_pa_cases_assumed']:
            stem=f"{'TIED' if b else 'BARE'}_E{eg:g}"
            for f in cfg['probe_frequencies_hz']:
                a=next(r for r in mat if r['case_id']==f'{stem}_N{n0}' and float(r['f_hz'])==f and r['input_port']=='0' and r['output_port']=='0')
                z=next(r for r in mat if r['case_id']==f'{stem}_N{n1}' and float(r['f_hz'])==f and r['input_port']=='0' and r['output_port']=='0')
                ya=complex(float(a['admittance_re_m3_pa_s']),float(a['admittance_im_m3_pa_s']));yb=complex(float(z['admittance_re_m3_pa_s']),float(z['admittance_im_m3_pa_s']))
                for name in ['uniform','uniform_plus_x_gradient']:
                    ra=next(r for r in fields if r['case_id']==f'{stem}_N{n0}' and float(r['f_hz'])==f and r['field']==name)
                    rb=next(r for r in fields if r['case_id']==f'{stem}_N{n1}' and float(r['f_hz'])==f and r['field']==name)
                    pa=complex(float(ra['mean_inner_pressure_re_pa']),float(ra['mean_inner_pressure_im_pa']));pb=complex(float(rb['mean_inner_pressure_re_pa']),float(rb['mean_inner_pressure_im_pa']))
                    sa,sb=float(ra['pressure_deviation_volume_rms_pa']),float(rb['pressure_deviation_volume_rms_pa'])
                    mesh.append(dict(family=stem,f_hz=f,field=name,uniform_admittance_relative_change=float(abs(yb/ya-1)),
                        mean_pressure_relative_change=float(abs(pb/pa-1)),deviation_absolute_change_pa_per_unit_outer_pa=abs(sb-sa),
                        deviation_relative_change=None if abs(sa)<1e-20 else abs(sb/sa-1)))
    table('p21b_porownanie_siatek_w_pasmie.csv',mesh)
    f=np.array(cfg['probe_frequencies_hz']);fig,ax=plt.subplots(1,2,figsize=(12,5.2));colors=['#cf7200','#6956a5','#258299']
    for b in [False,True]:
        for eg,color in zip(cfg['glue_E_pa_cases_assumed'],colors):
            cid=f"{'TIED' if b else 'BARE'}_E{eg:g}_N{nmax}"
            vals=[float(next(r for r in comp if r['case_id']==cid and float(r['f_hz'])==fr)['uniform_admittance_relative_change_to0D'])*100 for fr in f]
            ax[0].plot(f,vals,ls='-' if b else '--',color=color,label=f"{'Ze ściągiem' if b else 'Bez ściągu'}, E={eg/1e6:g} MPa")
    ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='Zmiana odpowiedzi objętościowej względem 0D [%]',title='Jednorodny nacisk: korekta wewnętrznej bezwładności gazu')
    ax[0].legend(fontsize=7)
    for name,label,color in [('uniform','Różnice przy nacisku równomiernym','#258299'),('uniform_plus_x_gradient','Różnice przy polu z gradientem','#cf7200')]:
        rr=[next(r for r in fields if r['case_id']==fine and r['field']==name and float(r['f_hz'])==fr) for fr in f]
        ax[1].plot(f,[1000*float(r['pressure_deviation_volume_rms_pa']) for r in rr],'o-',color=color,label=label)
    rr=[next(r for r in fields if r['case_id']==fine and r['field']=='uniform' and float(r['f_hz'])==fr) for fr in f]
    ax[1].plot(f,[1000*abs(complex(float(r['mean_inner_pressure_re_pa']),float(r['mean_inner_pressure_im_pa']))) for r in rr],color='#222',ls=':',label='Amplituda średniego ciśnienia')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='Ciśnienie wewnętrzne [mPa RMS]',title='Model odniesienia; zewnętrzna amplituda modalna 1 Pa RMS')
    ax[1].legend(fontsize=7)
    for a in ax:a.grid(alpha=.25)
    fig.suptitle('Szczelny gaz bez strat przyściennych; pole z gradientem jest scenariuszem, zróżnicowanie przestrzenne nie jest THD',fontsize=10)
    save(fig,'81_P21B_0D_3D_i_zroznicowanie_cisnienia')
    # Ściany rzeczywistych komórek gazu na wybranej płaszczyźnie,bez wypełniania pręta triangulacją.
    state=ROOT/status['reference_state_file']
    with np.load(state,allow_pickle=False) as data:
        xyz=data['fluid_xyz'];cells=data['fluid_elements'];ys=data['axes_y'];selected_y=float(ys[np.argmin(abs(ys-.05))])
        index=list(data['frequencies_hz']).index(80.);P=data['pressure_states'][index]
        faces={}
        for cell in cells:
            for face in FACES:
                ids=cell[face]
                if np.all(abs(xyz[ids,1]-selected_y)<1e-12):faces[tuple(sorted(ids))]=ids
        polygons=[xyz[ids][:,[0,2]]*1000 for ids in faces.values()]
        values=[np.array([np.mean(P[ids,j].real)*1000 for ids in faces.values()]) for j in range(2)]
        low=min(v.min() for v in values);high=max(v.max() for v in values)
        fig,ax=plt.subplots(1,2,figsize=(11.5,5.4))
        for j,a in enumerate(ax):
            pc=PolyCollection(polygons,array=values[j],cmap='viridis',edgecolors='#ffffff25',linewidths=.2,clim=(low,high));a.add_collection(pc)
            a.set_facecolor('#b4b8bc');a.set(xlim=(0,180),ylim=(0,170),xlabel='x modułu [mm]',ylabel='z modułu [mm]',
                title='Nacisk równomierny' if j==0 else 'Pole z gradientem: 1+(x−W/2)/W')
            a.set_aspect('equal');fig.colorbar(pc,ax=a,label='Re(fazora RMS ciśnienia) [mPa]',shrink=.83)
        fig.suptitle(f'Moduł 180×100×170 mm, 80 Hz; przekrój y={selected_y*1000:.2f} mm; amplituda modalna 1 Pa RMS',fontsize=10)
        save(fig,'82_P21B_pole_cisnienia_w_module')
    fig,ax=plt.subplots(1,2,figsize=(12,4.9));modes=checks['rigid_eigenmodes']
    ax[0].plot([r['mesh_resolution'] for r in modes],[100*r['max_relative_frequency_error'] for r in modes],'o-',color='#258299')
    ax[0].set(xlabel='Parametr zagęszczenia',ylabel='Największa różnica częstotliwości [%]',title='12 modów pustego prostopadłościanu: wzorzec analityczny')
    for b,style in [(False,'--'),(True,'-')]:
        for freq,color in [(20.,'#cf7200'),(80.,'#6956a5')]:
            rr=[r for r in checks['formal0D_limit'] if r['braced']==b and r['f_hz']==freq]
            ax[1].loglog([r['spatial_scale'] for r in rr],[100*r['relative_admittance_matrix_error_to0D'] for r in rr],'o',ls=style,color=color,
                label=f"{'Ze ściągiem' if b else 'Bez ściągu'}, {freq:g} Hz")
    ax[1].set(xlabel='Formalna skala A, przy stałym C',ylabel='Różnica pełnej macierzy portów względem 0D [%]',title='Pomijalna bezwładność gazu, nie fizyczne ogrzewanie')
    ax[1].legend(fontsize=7)
    for a in ax:a.grid(True,which='both',alpha=.25)
    fig.suptitle('Odrębne wzorce i granice modelu; to nie pomiary gotowego urządzenia',fontsize=10)
    save(fig,'83_P21B_wzorce_i_granica0D')
    numerical_false=[r for r in fields if r['within_numerical_screen']!='True']
    primary=[r for r in comp if r['is_probe']=='True'];diagnostic=[r for r in comp if r['is_probe']!='True']
    result=dict(status='SPATIAL_MODULE_FINDINGS_NOT_FULL_MAIN_CABINET_OR_MATERIAL_IDENTIFICATION',
        field_rows=len(fields),comparison_rows=len(comp),numerical_flagged_rows=len(numerical_false),
        max_uniform_admittance_change_at_probes=max(float(r['uniform_admittance_relative_change_to0D']) for r in primary),
        max_uniform_admittance_change_at_diagnostics=max(float(r['uniform_admittance_relative_change_to0D']) for r in diagnostic),
        max_uniform_admittance_mesh_change_at_probes=max(r['uniform_admittance_relative_change'] for r in mesh),
        max_absolute_deviation_mesh_change_pa_per_outer_pa=max(r['deviation_absolute_change_pa_per_unit_outer_pa'] for r in mesh),
        minimum_gas_mode_reference_hz=min(float(r['first_rigid_gas_mode_hz']) for r in models),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [cp,Path(__file__),state,
            OUT/'p21b_podsumowanie.json',OUT/'p21b_modele_i_geometria.csv',OUT/'p21b_pola_i_energia.csv',OUT/'p21b_porownanie_z0D.csv',
            OUT/'p21b_macierze_admitancji.csv',OUT/'p21b_kontrole_niezalezne.json']},
        next='P21C: główna komora z regulacją i wypełnieniem,rzeczywiste mocowanie i niejednorodne pole;nie zastępować tego samym modułem.',
        limitations=['Matched-case mesh changes and finite frequency samples,not a continuum certificate.',
            'Large relative variation of small internal pressure is not large SPL,THD or a product ranking.',
            'Rigid-cavity modes and lossless diagnostic responses do not identify physical coupled resonance peaks.'])
    (OUT/'p21b_ocena_projektowa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P21B figures81–83;flags',len(numerical_false),'max primary correction',result['max_uniform_admittance_change_at_probes'],flush=True)


if __name__=='__main__':main()
