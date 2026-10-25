"""P17: rozróżnij granicęSdX, brak wspólnejVb i wymagania chłodzenia."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter
import numpy as np
from model_nieliniowy import Plant
from model_subwoofera import Driver
from model_gazu import Medium
from analiza_cewki_z_pamiecia import dynamic_network
from synteza_granic_P17 import requirements,at_volume

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as handle:return list(csv.DictReader(handle))


def main():
    pool=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers'];m=Medium()
    points=read('p17_punkty_i_wymagania.csv');bands=read('p17_wspolny_przedzial_Vb.csv');displacement=[]
    cfg=json.loads((ROOT/'dane/konfiguracje/p17_synteza_V_I_X_cieplo.json').read_text())
    memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text());by_id={r['candidate_id']:r for r in pool}
    for entry in pool:
        p=Plant.from_driver(Driver(**entry['model']));vd=p.sd*p.xref
        maximum=m.rho*(2*np.pi*20)**2*vd/(4*np.pi*np.sqrt(2))
        displacement.append(dict(candidate_id=entry['candidate_id'],driver=entry['model']['name'],size_class_in=entry['nominal_size_class_in'],
            nominal_Vd_l=float(vd*1000),nominal_X_reference_SPL20_4pi1m_rms_db=float(20*np.log10(maximum/20e-6)),
            final_selection_gate=entry['final_selection_gate'],scope='ODNIESIENIE_Sd_X_NIE_ZMIERZONY_UZYTECZNY_SPL'))
    with (OUT/'p17_nominalna_granica_SdX.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(displacement[0]));writer.writeheader();writer.writerows(displacement)
    keys=['candidate_id','profile','target_sine_SPL_rms_db','rise_scenario_k','thermal_Rth_test_k_w','amp_vrms','amp_arms']
    point_groups={}
    for row in points:point_groups.setdefault(tuple(row[k] for k in keys),[]).append(row)
    conflicts=[];single_impossible=0
    for row in bands:
        if row['status']!='NO_COMMON_VOLUME':continue
        parts=point_groups[tuple(row[k] for k in keys)]
        if all(r['status']=='CONDITIONAL_INTERVAL' for r in parts):
            conflicts.append(dict(band=row,frequency_intervals=[{k:r[k] for k in ['f_hz','Vb_min_l','Vb_max_l']} for r in parts]))
        else:single_impossible+=1
    active_examples=[]
    for cid in ('C02','C11'):
        for voltage in (40,60):
            row=next(r for r in bands if r['candidate_id']==cid and r['profile']=='FLUX_ONE' and r['target_sine_SPL_rms_db']=='95'
                and r['rise_scenario_k']=='80' and r['thermal_Rth_test_k_w']=='0.6' and float(r['amp_vrms'])==voltage)
            p=Plant.from_driver(Driver(**by_id[cid]['model']));instant,branches,_=dynamic_network(p,'FLUX_ONE',memory)
            level=20e-6*10**(95/20);volume=float(row['Vb_min_l']);constraints=[]
            for f in cfg['frequencies_hz']:
                req=requirements(p,f,level,instant,branches,80.,cfg['alpha_per_k'],cfg['distance_m'],cfg['gas_tau_s'])
                actual=at_volume(req,volume,p,80.,cfg['alpha_per_k'])
                constraints.extend([(actual['voltage_rms_v']/float(row['amp_vrms']),'V',f),
                    (actual['current_rms_a']/float(row['amp_arms']),'I',f),(.6/actual['Rth_max_all_heat_to_coil_k_w'],'Rth',f)])
            value,name,f=max(constraints)
            active_examples.append(dict(candidate_id=cid,amp_vrms=voltage,amp_arms=float(row['amp_arms']),
                target_4pi1m_rms_db=95,rise_scenario_k=80,Rth_test_k_w=.6,Vb_min_l=volume,
                active_constraint=name,active_frequency_hz=f,active_ratio=value,final_selection_gate=by_id[cid]['final_selection_gate']))
    with (OUT/'p17_przyklady_aktywnych_ograniczen.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(active_examples[0]));writer.writeheader();writer.writerows(active_examples)
    fig,ax=plt.subplots(figsize=(11,10));levels=[r['nominal_X_reference_SPL20_4pi1m_rms_db'] for r in displacement]
    colors=[{10:'C2',12:'C0',15:'C1'}.get(r['size_class_in'],'C3') for r in displacement]
    labels=[r['candidate_id']+' '+r['driver'] for r in displacement]
    ax.barh(np.arange(24),levels,color=colors,alpha=.8);ax.set_yticks(np.arange(24),labels=labels,fontsize=8);ax.invert_yaxis()
    for level in (85,90,95,100):ax.axvline(level,color='gray',ls=':',lw=1)
    ax.set(xlim=(75,105),xlabel='Nominalna granica odniesienia X przy 20 Hz [dB RMS, 4π / 1 m]',
           title='Nominalna granica z Sd × katalogowego X przy 20 Hz\nKolory: klasy średnicy; granica bez identyfikacji THD i pokoju')
    classes=sorted({r['size_class_in'] for r in displacement})
    ax.legend(handles=[Patch(color={10:'C2',12:'C0',15:'C1'}.get(size,'C3'),label=f'{size}″'+(' (kontrole)' if size==10 else '')) for size in classes],fontsize=8,loc='lower right')
    ax.grid(axis='x',alpha=.25);fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'41_P17_nominalne_SdX.{ext}',dpi=170)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,6));selected=[]
    for cid in ['C01','C02','C06','C11']:
        for rth in [.3,.6,1.2]:
            row=next(r for r in bands if r['candidate_id']==cid and r['profile']=='FLUX_ONE' and r['target_sine_SPL_rms_db']=='90'
                and r['rise_scenario_k']=='80' and r['amp_vrms']=='40' and float(r['thermal_Rth_test_k_w'])==rth)
            selected.append(row)
    ax.axvspan(30,150,color='gray',alpha=.09,label='Okno ilustracji 30–150 l, nie limit briefu')
    for k,row in enumerate(selected):
        color={'C01':'C0','C02':'C1','C06':'C2','C11':'C3'}[row['candidate_id']]
        if row['status']!='COMMON_CONDITIONAL_VOLUME_INTERVAL':ax.text(20,k,'brak');continue
        lo=float(row['Vb_min_l']);hi=float(row['Vb_max_l']) if row['Vb_max_l'] else 700.
        ax.plot([lo,hi],[k,k],color=color,lw=3);ax.plot(lo,k,'o',color=color)
        if not row['Vb_max_l']:ax.annotate('',xy=(700,k),xytext=(600,k),arrowprops=dict(arrowstyle='->',color=color))
    ax.set_yticks(np.arange(len(selected)),labels=[f"{r['candidate_id']}  Rth_test={r['thermal_Rth_test_k_w']} K/W" for r in selected],fontsize=8)
    ax.invert_yaxis();ax.set_xscale('log');ax.set_xticks([20,30,45,60,80,100,150,200,300,500,700]);ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set(xlim=(20,750),xlabel='Vb netto powietrza [l]; strzałka oznacza brak skończonej górnej granicy w modelu',
        title='90 dB RMS, 4π / 1 m; 6 osobnych sinusów 20–80 Hz\n40 Vrms / 12 Arms; przyrost 80 K tylko scenariuszem; C11 ma otwartą bramkę rewizji')
    ax.legend(fontsize=8,loc='lower right');ax.grid(axis='x',alpha=.25);fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'42_P17_wspolna_objetosc_i_chlodzenie.{ext}',dpi=170)
    plt.close(fig)
    result=dict(status='P17_DIAGNOSTIC_SYNTHESIS_NOT_DRIVER_SELECTION',
        conflict_bands_with_each_frequency_individually_feasible=len(conflicts),bands_with_at_least_one_V_I_thermal_impossible_frequency=single_impossible,
        conflicts=conflicts,selected_90db_volume_intervals=selected,
        nominal_displacement_bounds=displacement,
        active_constraint_examples=active_examples,
        scope='Analityczne przedziały dodatniejV dla wskazanych6sinusów i scenariuszy; nie całe pasmo,sygnałmuzyczny ani pokój. Nie kwalifikuje modeli z bramkami danych do końcowej rekomendacji.')
    (OUT/'p17_interpretacja.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print('P17:konflikty wspólnejVb',len(conflicts),'punktowo niemożliwe',single_impossible);return result


if __name__=='__main__':main()
