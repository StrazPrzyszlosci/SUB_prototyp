"""Oddziela zbieżność lokalną od wpływu granicy i pola rodzica; bez certyfikatu."""
from pathlib import Path
import csv,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    paths=[OUT/'p19g_przypadki_i_bilans.csv',OUT/'p19g_dodatkowe_przypadki.csv',
           OUT/'p19g_lokalne_pola_spoin.csv',OUT/'p19g_dodatkowe_okna.csv']
    cases=[r for p in paths[:2] for r in csv.DictReader(p.open())]
    observations=[r for p in paths[2:] for r in csv.DictReader(p.open())]
    cfg=json.loads((ROOT/'dane/konfiguracje/p19g_podmodel_lokalny.json').read_text())
    def obs(cid,joint):return next(r for r in observations if r['case_id']==cid and r['joint']==joint and r['window']=='TRIM5MM')
    comparisons=[]
    for label,a,b in [('YZ_REFINEMENT','B30_middle_H0.0025_P14_X8','B30_middle_H0.00125_P14_X8'),
                      ('X_REFINEMENT','B30_middle_H0.0025_P14_X16','B30_middle_H0.0025_P14_X32'),
                      ('DOMAIN_MIDDLE_TO_FAR','B30_middle_H0.0025_P14_X8','B30_far_H0.0025_P14_X8'),
                      ('PARENT_N14_TO_N18','B30_middle_H0.0025_P14_X8','B30_middle_H0.0025_P18_X8')]:
        for joint in ['front_bottom','front_cleat','bottom_cleat']:
            r1,r2=obs(a,joint),obs(b,joint)
            for key in ['tension_rms_pa','compression_rms_pa','shear_rms_pa']:
                x,y=float(r1[key]),float(r2[key])
                comparisons.append(dict(comparison=label,joint=joint,quantity=key,first_pa=x,second_pa=y,
                    absolute_change_pa=y-x,relative_change=(y/x-1) if abs(x)>1 else None,
                    scope='Same x window, same 30mm geometry; trim5mm is numerical diagnostic, not material length.'))
    fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    ax[0].add_patch(Rectangle((71,98),40,40,fc='#999',alpha=.35,label='Rzut łaty stopy 40×40 mm'))
    colors=['#cf7200','#6956a5','#258299']
    for d,color in zip(cfg['domains'],colors):
        x0=(cfg['center_x_m']-d['half_width_x_m'])*1000;w=2*d['half_width_x_m']*1000
        ax[0].add_patch(Rectangle((x0,22),w,(d['rear_y_m']-.022)*1000,fill=False,ec=color,lw=2,label=d['id']))
    lo,hi=np.array(cfg['observation_window_x_m'])*1000
    ax[0].axvspan(lo,hi,color='#277f96',alpha=.12,label='Stałe okno x obserwacji')
    ax[0].set(xlim=(45,145),ylim=(18,170),xlabel='x [mm]',ylabel='y w głąb [mm]',title='Dno: granica może przecinać fizyczną podporę')
    ax[0].legend(fontsize=8);ax[0].set_aspect('equal')
    for rectangle in [Rectangle((0,0),22,125,fc='#d5dce1',ec='#555'),Rectangle((22,0),138,22,fc='#d5dce1',ec='#555'),Rectangle((22,22),30,30,fc='#e5ad67',ec='#70491e')]:ax[1].add_patch(rectangle)
    for d,color in zip(cfg['domains'],colors):
        ax[1].plot([0,22],[d['top_z_m']*1000]*2,color=color,lw=2)
        ax[1].plot([d['rear_y_m']*1000]*2,[0,22],color=color,lw=2,label=d['id'])
    ax[1].set(xlim=(-2,168),ylim=(-2,132),xlabel='y [mm]',ylabel='z [mm]',title='Przekrój: front, dno i listwa 30 mm')
    ax[1].set_aspect('equal');ax[1].legend(fontsize=8)
    for a in ax:a.grid(alpha=.2)
    fig.suptitle('Podmodel: zadane przemieszczenia na cięciach, znana trakcja stopy',fontsize=11)
    save(fig,'67_P19G_domena_i_przecieta_podpora')
    fig,ax=plt.subplots(2,2,figsize=(12,8))
    js=['front_bottom','front_cleat','bottom_cleat'];labels=['Front–dno','Front–listwa','Dno–listwa']
    hs=[.01,.005,.0025,.00125];ns=[4,8,16,32]
    for j,label,color in zip(js,labels,['#cf7200','#258299','#6956a5']):
        for row,key in enumerate(['tension_rms_pa','shear_rms_pa']):
            ax[row,0].plot(np.array(hs)*1000,[float(obs(f'B30_middle_H{h:g}_P14_X8',j)[key])/1000 for h in hs],marker='o',label=label,color=color)
            ax[row,1].plot(ns,[float(obs(f'B30_middle_H0.0025_P14_X{n}',j)[key])/1000 for n in ns],marker='o',label=label,color=color)
    for row,quantity in enumerate(['rozciągania','ścinania']):
        ax[row,0].set_xscale('log',base=2);ax[row,0].invert_xaxis();ax[row,0].set_xticks(np.array(hs)*1000,labels=['10','5','2,5','1,25'])
        ax[row,0].set(xlabel='Docelowy krok y/z [mm]; nx=8',ylabel=f'Przestrzenne RMS {quantity} [kPa]')
        ax[row,1].set_xscale('log',base=2);ax[row,1].set_xticks(ns,labels=[str(n) for n in ns])
        ax[row,1].set(xlabel='Liczba przedziałów x; krok y/z=2,5 mm',ylabel=f'Przestrzenne RMS {quantity} [kPa]')
    ax[0,0].set_title('Zagęszczenie przekroju');ax[0,1].set_title('Zagęszczenie wzdłuż listwy')
    for a in ax.ravel():a.grid(alpha=.25);a.legend(fontsize=8)
    fig.suptitle('Listwa 30 mm, middle, pole N14; ciężar + statyczne 1 kPa; okno z odcięciem 5 mm',fontsize=11)
    save(fig,'68_P19G_dwa_kierunki_zbieznosci')
    fig,ax=plt.subplots(1,2,figsize=(12,4.8));x=np.arange(3)
    for delta,d,color in zip([-.24,0,.24],cfg['domains'],colors):
        ax[0].bar(x+delta,[float(obs(f'B30_{d["id"]}_H0.0025_P14_X8',j)['tension_rms_pa'])/1000 for j in js],width=.24,label=d['id'],color=color)
    for delta,n,color in zip([-.16,.16],[14,18],['#6956a5','#258299']):
        ax[1].bar(x+delta,[float(obs(f'B30_middle_H0.0025_P{n}_X8',j)['tension_rms_pa'])/1000 for j in js],width=.32,label=f'Pole globalne N{n}',color=color)
    for a in ax:
        a.set(xticks=x,xticklabels=labels,ylabel='Przestrzenne RMS rozciągania w oknie [kPa]');a.grid(axis='y',alpha=.25);a.legend(fontsize=8)
    ax[0].set_title('Zmiana odległości granicy; pole N14')
    ax[1].set_title('Zmiana pola rodzica; domena middle')
    fig.suptitle('Ten sam obszar obserwacji; 30 mm, nx=8, krok 2,5 mm; ciężar + statyczne 1 kPa',fontsize=11)
    save(fig,'69_P19G_granica_i_pole_globalne')
    summary=dict(status='FINITE_LOCAL_RESOLUTION_AND_PARENT_SENSITIVITY_NOT_GLOBAL_STRENGTH_CERTIFICATE',
        cases=len(cases),observation_rows=len(observations),max_dof=max(int(r['dof']) for r in cases),comparisons=comparisons,
        max_free_linear_residual=max(float(r['free_linear_residual']) for r in cases),
        max_force_moment_balance_normalized=max(float(r['force_moment_balance_normalized']) for r in cases),
        max_energy_work_relative_error=max(float(r['energy_work_relative_error']) for r in cases),
        no_claims=['Zero dodatniej części w oknie nie jest dowodem bezpieczeństwa połączenia.',
                   'Dwa kierunki zagęszczenia osobno,nie certyfikat wspólnego continuum.',
                   'Okno lokalne nie jest całą spoiną z P19F.',
                   'N14/N18 to dwie realizacje pola,nie statystyczna tolerancja produktu.'],
        next='P20:sztywne moduły regulacjiVb,dostęp przy stałym froncie,bilansnetto i mocowania;gates materiałowe P19 zachować.',
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'dane/konfiguracje/p19g_podmodel_lokalny.json',*paths]})
    (OUT/'p19g_ocena_i_roznice.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    print('P19G post:',len(cases),'cases,',summary['max_dof'],'DOF; parent sensitivity retained.')


if __name__=='__main__':main()
