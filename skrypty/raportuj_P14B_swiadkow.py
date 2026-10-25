"""Wykresy i mierzalne wnioski z15zamrożonych świadków, bez zamykaniaP14B."""
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from projekcja_P14B import ROOT,OUT
from model_subwoofera import Driver
from model_nieliniowy import Plant
from model_emisji_P14B import fixed_operators,moving_monopole,pressure_metrics


def save(fig,name):
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/(name+'.'+ext),dpi=170)
    plt.close(fig)


def main():
    witness=OUT/'p14b_swiadkowie_emisji.npz';meta=json.loads((OUT/'p14b_swiadkowie_emisji.json').read_text())
    assert hashlib.sha256(witness.read_bytes()).hexdigest()==meta['archive_sha256']
    cfg=json.loads((ROOT/'dane/konfiguracje/p14b_IMD.json').read_text());g=json.loads((ROOT/'dane/konfiguracje/p14b_emisja.json').read_text())
    raw=np.load(witness,allow_pickle=False)
    rows={str(case):json.loads(text) for case,text in zip(raw['case_id'],raw['row_json'])}
    spectra={str(case):arr for case,arr in zip(raw['case_id'],raw['spectrum'])}
    for case,arr in spectra.items():assert hashlib.sha256(np.ascontiguousarray(arr,dtype='<c16').tobytes()).hexdigest()==meta['spectrum_sha256'][case]
    pool=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers'];entry=next(r for r in pool if r['candidate_id']=='C02')
    plant=Plant.from_driver(Driver(**entry['model']));f=np.arange(801)*1.25;omega=2*np.pi*f
    hv=fixed_operators(plant,100,f,g);projected={};summary=[]
    for case,row in rows.items():
        p=Plant.from_driver(Driver(**next(r for r in pool if r['candidate_id']==row['candidate_id'])['model']))
        stationary=p.sd/plant.sd*hv['MONOPOLE_4PI']*(1j*omega)*spectra[case][0]
        moving,diagnostic=moving_monopole(spectra[case][0],f,p.sd,g)
        projected[case]=(stationary,moving)
        for name,pressure in [('MONOPOLE_4PI',stationary),('MOVING_MONOPOLE_AXIS',moving)]:
            metrics,lines=pressure_metrics(pressure,f,row,cfg)
            summary.append(dict(case_id=case,candidate_id=row['candidate_id'],pair_hz=row['frequencies_hz'],profile=row['profile'],geometry=name,
                                voltage_each_rms_v=row['voltage_scale'],**metrics))
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    selected=[('000220','LTI'),('000222','NL prosty'),('000223','NL FLUX1')]
    major=(f>=5)&(f<=300)&(np.arange(len(f))%4==0)
    for case,label in selected:
        x=abs(spectra[case][0]);pressure=abs(projected[case][0])
        mx=major&(x*1000>1e-7);mp=major&(pressure>1e-7)
        axes[0].semilogy(f[mx],x[mx]*1000,'o',label=label,markersize=4,alpha=.7)
        axes[1].semilogy(f[mp],pressure[mp],'o',label=label,markersize=4,alpha=.7)
    axes[0].set(xlabel='Częstotliwość [Hz]',ylabel='X RMS [mm]',title='Ruch: także produkt przy 5 Hz')
    axes[1].set(xlabel='Częstotliwość [Hz]',ylabel='p RMS [Pa]',title='Monopol 4π / 1 m: p proporcjonalne do f²X')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8);ax.axvline(5,color='k',alpha=.2)
    fig.suptitle('C02 / 100 l; 45 + 95 Hz po 20 Vrms; umowne krzywe, nie wynik pomiaru')
    save(fig,'31_P14B_ruch_i_emisja_5Hz')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8));labels=['LTI','Gaz NL','NL prosty','FLUX1','FLUX2'];ids=[f'{k:06d}' for k in range(220,225)]
    for ax,key,title in zip(axes,['IM2_pct','IM3_difference_pct'],['IM2: suma i różnica','IM3: dwie różnice']):
        for offset,geometry in [(-.18,'MONOPOLE_4PI'),(.18,'MOVING_MONOPOLE_AXIS')]:
            values=[next(r[key] for r in summary if r['case_id']==case and r['geometry']==geometry) for case in ids]
            ax.bar(np.arange(5)+offset,np.maximum(values,1e-10),width=.32,label='Stałe źródło' if offset<0 else 'Kontrolny ruchomy monopol')
        ax.set(yscale='log',xticks=np.arange(5),xticklabels=labels,ylabel='Własna miara IM / RSS podstawowych [%]',title=title);ax.grid(axis='y',alpha=.25);ax.legend(fontsize=8,loc='lower right')
    fig.suptitle('Ten sam zapisany ruch; odrębne projekcje pola, bez zmiany reakcji na membranę')
    save(fig,'32_P14B_kinematyka_i_intermodulacja')
    case='000223';line=int((45+95)/1.25);stationary,moving=projected[case]
    a=stationary[line];b=moving[line];delta=b-a
    den=np.linalg.norm(stationary[[36,76]])
    a,b,delta=[100*v/den for v in (a,b,delta)]
    fig,ax=plt.subplots(figsize=(7,6))
    for start,end,label,color in [(0,a,'P stałe','C0'),(a,b,'ΔP dla zmiany modelu emisji','C1'),(0,b,'P ruchome','C2')]:
        ax.annotate('',xy=(end.real,end.imag),xytext=(complex(start).real,complex(start).imag),arrowprops=dict(arrowstyle='->',color=color,lw=2))
        ax.plot([complex(start).real,end.real],[complex(start).imag,end.imag],color=color,label=label,alpha=.4)
    points=np.array([0,a,b]);margin=max(np.ptp(points.real),np.ptp(points.imag),.2)*.18
    ax.set(xlim=(min(points.real)-margin,max(points.real)+margin),ylim=(min(points.imag)-margin,max(points.imag)+margin),
           xlabel='Re(P)/RSS podstawowych stałego źródła [%]',ylabel='Im(P)/RSS podstawowych stałego źródła [%]',
           title='Produkt 140 Hz; C02 / 100 l / FLUX1 / 45 + 95 Hz')
    ax.axhline(0,color='k',lw=.5);ax.axvline(0,color='k',lw=.5);ax.grid(alpha=.25);ax.legend(fontsize=8);ax.set_aspect('equal',adjustable='box')
    save(fig,'33_P14B_fazory_i_kompensacja')
    r=rows['000223'];x5=abs(spectra['000223'][0,4]);funds=[36,76]
    result=dict(status='15_SELECTED_WITNESSES_NOT_FULL_P14B',witness_file_sha256=meta['archive_sha256'],
                source_dynamic_run_sha256=meta['dynamic_run_sha256'],
                C02_FLUX1_45_95_100l=dict(X5_rms_mm=float(x5*1000),X5_to_motion_fundamentals_pct=float(100*x5/np.linalg.norm(spectra['000223'][0,funds])),
                    steady_peak_mm=r['x_peak_sampled_m']*1000,current_rms_a=r['current_rms_a'],voltage_each_rms_v=r['voltage_scale']),
                metrics=summary,
                scope='Własne miary, założone krzywe. MOVING nie jest rzeczywistym ruchomym tłokiem. Nie dodawać skalarnie procentów ani traktować tych punktów jako rankingu producentów.')
    (OUT/'p14b_swiadkowie_wyniki.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print(json.dumps({k:v for k,v in result.items() if k!='metrics'},indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
