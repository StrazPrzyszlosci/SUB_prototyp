"""P20B: porównanie regulatorów z jawnymi bramkami i własnymi wykresami."""
from pathlib import Path
import csv,hashlib,json,os
from collections import Counter
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
import numpy as np
from model_przegrody_P20B import Partition,two_chamber
from geometria_przegrody_P20B import matched_geometry
from analiza_przegrod_P20B import conductance
from naped_z_przegroda_P20B import ModuleReference
from model_gazu import Medium

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as stream:return list(csv.DictReader(stream))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    cp=ROOT/'dane/konfiguracje/p20b_przegroda_vs_moduly.json';cfg=json.loads(cp.read_text())
    bp=ROOT/cfg['reference_insert_config'];base=json.loads(bp.read_text());medium=Medium();gamp=medium.gamma*medium.p0_pa
    freq=np.linspace(20,80,1201);s=2j*np.pi*freq
    geometries=[matched_geometry(base,cfg,n,.018,'LINER_GEOMETRY') for n in cfg['primary_module_counts']]
    fig,ax=plt.subplots(1,2,figsize=(12,4.9))
    ax[0].add_patch(Rectangle((0,0),640,460,fill=False,lw=2,color='#333'))
    ax[0].axvline(352,color='#777',ls=':',label='Położenie stałego ściągu')
    for q,color in zip(geometries,['#258299','#6956a5','#cf7200','#a95353']):
        y=q['matched_position_from_inner_front_m']*1000
        ax[0].add_patch(Rectangle((y,1),18,458,color=color,alpha=.3))
        text_height=475+32*((q['module_count']//4)%2)
        ax[0].text(y,text_height,f"N={q['module_count']}\n{y:.0f} mm",ha='center',va='center',fontsize=8,color=color)
    ax[0].set(xlim=(-10,655),ylim=(-10,535),xlabel='Odległość od wewnętrznego frontu [mm]',ylabel='Wysokość wewnętrzna [mm]',title='Taki sam gaz z przodu; płyta 18 mm, tył zamknięty')
    ax[0].legend(loc='lower left',fontsize=8);ax[0].set_aspect('equal')
    ax[1].add_patch(Rectangle((-229,-229),458,458,fill=False,lw=2,color='#258299',label='Przegroda 458×458 mm'))
    ax[1].add_patch(Circle((0,0),229,fill=False,ls='--',color='#258299',label='Środkowy wpisany dysk Ø458 mm'))
    ax[1].add_patch(Circle((0,0),355.8/2,fill=False,lw=2,color='#a95353',label='Największy badany otwór Ø355,8 mm'))
    ax[1].set(xlim=(-265,265),ylim=(-265,265),xlabel='x [mm]',ylabel='z [mm]',title='Sztywna przegroda: ograniczenie dostępu od frontu')
    ax[1].set_aspect('equal');ax[1].legend(loc='upper center',fontsize=8)
    fig.suptitle('Geometria kontrolna, stały front U-021; luz 1 mm i osprzęt niekwalifikowane',fontsize=11)
    save(fig,'74_P20B_pozycje_i_dostep')
    q=geometries[-1];Ca=q['matched_active_air_l']*.001/gamp;Cb=q['rear_geometric_air_l']*.001/gamp
    specs=[('18 mm, obwód nieruchomy','PERIM',np.inf,.018,'#222'),
        ('18 mm, rama 4×10⁴ N/m','PERIM',1e4,.018,'#a95353'),
        ('18 mm, rama 4×10⁶ N/m','PERIM',1e6,.018,'#cf7200'),
        ('18 mm, 4 łaty ×10⁶ N/m','PATCH4',1e6,.018,'#6956a5'),
        ('25 mm, 4 łaty ×10⁷ N/m','PATCH4',1e7,.025,'#258299')]
    fig,ax=plt.subplots(1,2,figsize=(13,5.2));dense=[];models={}
    for label,kind,k,t,color in specs:
        m=Partition(base,cfg,t,kind,'CCCC' if kind=='PERIM' else 'FREE',k);models[(kind,k,t)]=m
        geo=matched_geometry(base,cfg,16,t,'LINER_GEOMETRY');cb=geo['rear_geometric_air_l']*.001/gamp
        r=two_chamber(freq,Ca,cb,m.compliance(freq));extra=gamp*(1/r['input_impedance']-s*Ca)/s*1000
        ax[0].plot(freq,extra.real,label=label,color=color);ax[1].semilogy(freq,np.maximum(-extra.imag,1e-10),color=color,label=label)
        for j,f in enumerate(freq):dense.append(dict(model=label,f_hz=float(f),extra_storage_l=float(extra[j].real),extra_loss_l=float(-extra[j].imag)))
    module=ModuleReference(base,cfg,freq);extra=16*module.admittance/s*gamp*1000
    ax[0].plot(freq,extra.real,color='#777',ls='--',label='16 modułów MDF8 + ściąg')
    ax[1].semilogy(freq,np.maximum(-extra.imag,1e-10),color='#777',ls='--',label='16 modułów MDF8 + ściąg')
    ax[0].set_yscale('symlog',linthresh=1)
    ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='Re(dodatkowej podatności) × γp₀ [l]',title='Ujemna część reaktywna nie jest ujemnym gazem')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='−Im(dodatkowej podatności) × γp₀ [l]',title='Straty w pasywnym modelu mogą wzrosnąć przy rezonansie')
    ax[0].legend(fontsize=8,loc='lower left')
    for a in ax:a.grid(True,which='both',alpha=.25)
    fig.suptitle('Z przodu 80,835 l gazu; zamknięty tył, szczelny obwód, wspólne βK; symulacja 0D/MITC',fontsize=11)
    save(fig,'75_P20B_podatnosc_i_mocowanie')
    from analiza_wkladow_P20A import table
    table('p20b_swiadkowie_gestej_czestotliwosci.csv',dense)
    fig,ax=plt.subplots(1,2,figsize=(12,5.0));m=models[('PERIM',np.inf,.018)];chi=m.compliance(freq)
    # Rozkład źródeł z zadanym Qmem; nie obwiednia wzmacniacza ani SPL w pokoju.
    for gs,gv,label,color in [(0.,0.,'Szczelne obie komory','#222'),(10.,0.,'Przeciek obwodu 10 Hz ref, tył zamknięty','#6956a5'),
        (10.,10.,'Obwód i odpowietrzenie: po 10 Hz ref','#cf7200'),(np.inf,np.inf,'Obie drogi otwarte: formalna granica','#a95353')]:
        r=two_chamber(freq,Ca,Cb,chi,conductance(gs,medium),conductance(gv,medium));T=r['vent_flow_per_input']
        ext=1-T*np.exp(-s*(.64+2*.022)/medium.c)/(1+.64+2*.022)
        ax[0].plot(freq,np.abs(T),label=label,color=color)
        # Zero dokładne jest zerem, a nie sztucznym minimum dB.
        ax[1].plot(freq,np.abs(1-T),ls='--',color=color)
        ax[1].plot(freq,np.abs(ext),color=color,label=label)
    ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='|Q wentylacji / Q membrany|',title='Dopływ tylny i membrana mają przeciwne znaki')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='|suma ciśnień| / |sam monopol membrany|',title='Linia: przód 1 m; kreski: źródła współlokowane')
    ax[0].legend(fontsize=8);ax[1].legend(fontsize=7)
    for a in ax:a.grid(alpha=.25)
    fig.suptitle('Dwa diagnostyczne monopole 4π, bez reakcji promieniowania i pokoju; ref zdefiniowany dla 100 l',fontsize=10)
    save(fig,'76_P20B_wentylacja_i_dwa_zrodla')
    material=read('p20b_materialy_masa_i_pas.csv');selected=[r for r in material if int(round(float(r['t_mm']))) in [12,18]]
    fig,ax=plt.subplots(1,2,figsize=(12,5.0));xs=np.arange(len(selected))
    labels=[('Form' if 'Form/' in r['product'] else 'Spruce')+' '+f"{float(r['t_mm']):g} mm" for r in selected]
    ax[0].bar(xs,[float(r['mass_ratio_to_MDF18_assumption']) for r in selected],color=['#258299' if 'Form/' in r['product'] else '#cf7200' for r in selected])
    ax[1].bar(xs-.17,[float(r['Ba_ratio_to_MDF18_assumption']) for r in selected],width=.34,label='Kierunek a',color='#258299')
    ax[1].bar(xs+.17,[float(r['Bb_ratio_to_MDF18_assumption']) for r in selected],width=.34,label='Kierunek b',color='#cf7200')
    for a in ax:
        a.axhline(1,color='#222',ls='--',label='MDF18: założenie E=2,1 GPa, ρ=730 kg/m³')
        a.set_xticks(xs,labels);a.grid(axis='y',alpha=.25)
    ax[0].set(ylabel='Masa / masa MDF18',title='Kwadrat 458×458 mm, bez osprzętu')
    ax[1].set(ylabel='Em · t³ / (E_MDF · t_MDF³)',title='Nominalna sztywność pasa zginanego, nie całej płyty')
    ax[0].legend(fontsize=7);ax[1].legend(fontsize=7)
    fig.suptitle('Dane pierwotne Metsä: Form/FormPLUS MC12%, Spruce MC10%; brak dopasowania wilgotności MDF',fontsize=10)
    save(fig,'77_P20B_sklejka_masa_i_kierunki')
    drive=read('p20b_naped_i_porownanie_regulatorow.csv');amps=read('p20b_dziedzina_amplitudy.csv')
    amplitude=[]
    for p in cfg['amplitude_screen_main_pressure_rms_pa_cases']:
        rr=[r for r in amps if float(r['front_pressure_rms_pa'])==p]
        amplitude.append(dict(front_pressure_rms_pa=p,rows=len(rr),outside_bending=sum(float(r['bending_peak_over_thickness'])>.2 for r in rr),
            outside_gas=sum(float(r['maximum_gas_pressure_peak_fraction'])>.01 for r in rr),
            outside_travel=sum(float(r['maximum_absolute_motion_peak_m'])>=float(r['minimum_axial_travel_clearance_m']) for r in rr)))
    by_model=Counter(r['regulator_model'] for r in drive if r['within_assumed_linear_domain']=='False')
    witnesses=[r for r in drive if r['configuration_id']=='C04' and r['lining']=='LINER_GEOMETRY' and float(r['driver_displacement_l_stress_axis'])==4 and float(r['amp_v_rms'])==40 and int(r['module_count_equivalent'])==16 and float(r['f_hz']) in [20.,40.,80.] and r['seal_100l_reference_corner_hz']=='0.0' and r['vent_100l_reference_corner_hz']=='0.0']
    inputs=[cp,bp,Path(__file__),ROOT/'skrypty/model_przegrody_P20B.py',ROOT/'skrypty/geometria_przegrody_P20B.py',ROOT/'skrypty/analiza_przegrod_P20B.py',
        ROOT/'skrypty/naped_z_przegroda_P20B.py',ROOT/'skrypty/analiza_wkladow_P20A.py',ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/model_gazu.py',
        OUT/'p20b_naped_i_porownanie_regulatorow.csv',OUT/'p20b_dziedzina_amplitudy.csv',OUT/'p20b_materialy_masa_i_pas.csv']
    result=dict(status='CONDITIONAL_REGULATOR_COMPARISON_NOT_FINAL_CABINET_SELECTION',dense_frequency_rows=len(dense),amplitude_screen_breakdown=amplitude,
        drive_flagged_by_model=dict(by_model),C04_selected_witnesses=witnesses,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        next='P20C: pełna mechanika3D modułu100mm z rozdzielnymi portami wnętrze/zewnętrze i promieniowaniem; równoległy kontrolny port sztywno blokowanej przegrody do zachowania porównania metod. Potem P21 i ochrona.',
        limitations=['Dense grid samples do not certify continuous-frequency maxima.',
            'Module and partition dry component masses omit unresolved fastening hardware; carrier mass0.25kg is a mechanical assumption.',
            'Fixed front remains fixed. Rigid partition needs preinstallation; nominal tool clearance is not a complete access proof.',
            'Material comparison is directional beam-strip proxy only; full plywood plate and adhesion remain open.'])
    (OUT/'p20b_ocena_projektowa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20B figures74–77;',len(dense),'dense witnesses;',len(witnesses),'C04 rows; domain flags retained.')


if __name__=='__main__':main()
