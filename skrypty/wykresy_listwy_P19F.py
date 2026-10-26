"""P19F: geometria, kompromis masy/sztywności i jawnie niezbieżne naprężenia."""
from pathlib import Path
import csv
import hashlib
import json
import os
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
    cases=list(csv.DictReader((OUT/'p19f_geometrie_i_podatnosc.csv').open()))
    joints=list(csv.DictReader((OUT/'p19f_spoiny_i_przeniesienie_obciazen.csv').open()))
    loads=list(csv.DictReader((OUT/'p19f_obciazenia_i_podpory.csv').open()))
    def tr(cid,joint):
        return next(float(r['tensile_spatial_rms_pa']) for r in joints
                    if r['case_id']==cid and r['load']=='GRAVITY_PLUS_STATIC_1KPA' and r['joint']==joint)/1000
    def case(cid):return next(r for r in cases if r['case_id']==cid)
    fig,axes=plt.subplots(1,4,figsize=(12,3.8))
    for ax,size in zip(axes,[0,20,30,40]):
        ax.add_patch(Rectangle((0,0),22,100,fc='#d5dce1',ec='#555'))
        ax.add_patch(Rectangle((22,0),78,22,fc='#d5dce1',ec='#555'))
        ax.plot([22,22],[0,22],color='#922947',lw=3)
        if size:
            ax.add_patch(Rectangle((22,22),size,size,fc='#e5ad67',ec='#70491e'))
            ax.plot([22,22],[22,22+size],color='#277f96',lw=3)
            ax.plot([22,22+size],[22,22],color='#6a52a0',lw=3)
        r=case(f'N14_B{size}_REF')
        ax.set(title=('Bez listwy' if not size else f'{size} × {size} mm')+f'\n+{float(r["added_mass_kg"]):.3f} kg; {float(r["occupied_volume_l"]):.3f} l',
               xlim=(-2,100),ylim=(-2,100),xlabel='y: w głąb [mm]')
        ax.set_aspect('equal');ax.grid(alpha=.15)
    axes[0].set_ylabel('z: w górę [mm]')
    fig.suptitle('Przekrój kontrolny: front i dno 22 mm, osobna bryła MDF i dwie spoiny',fontsize=11)
    save(fig,'64_P19F_geometria_listwy_i_spoin')
    fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    for n,color in zip([10,14,18],['#cf7200','#6956a5','#258299']):
        chosen=[case(f'N{n}_B{s}_REF') for s in [0,20,30,40]]
        ax[0].plot([float(r['section_m'])*1000 for r in chosen],
                   [100*(1-float(r['C_frozen_to_same_mesh_no_cleat_ratio'])) for r in chosen],marker='o',label=f'N={n}',color=color)
    ax[0].set(xlabel='Bok kwadratowej listwy [mm]',ylabel='Spadek podatności przy tym samym H [%]',title='Pełna rama i te same podpory; zamrożone H kontrolne')
    ax[0].legend()
    x=np.arange(3)
    for dx,j,label,color in zip([-.24,0,.24],['front_bottom','front_cleat','bottom_cleat'],
                               ['Pierwotna front–dno','Nowa front–listwa','Nowa dno–listwa'],['#555','#258299','#6956a5']):
        ax[1].bar(x+dx,[tr(f'N18_B{s}_REF',j) for s in [20,30,40]],width=.24,label=label,color=color)
    ax[1].axhline(tr('N18_B0_REF','front_bottom'),color='#b74c34',ls='--',label='Bez listwy: pierwotna spoina')
    ax[1].set(xticks=x,xticklabels=['20 mm','30 mm','40 mm'],ylabel='Przestrzenne RMS rozciągania [kPa]',title='N=18, ciężar + statyczne 1 kPa; bez kryterium nośności')
    ax[1].legend(fontsize=8)
    for a in ax:a.grid(axis='y',alpha=.25)
    save(fig,'65_P19F_sztywnosc_i_przeniesienie_naprezen')
    fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    ns=[10,14,18]
    ax[0].plot(ns,[tr(f'N{n}_B0_REF','front_bottom') for n in ns],marker='o',ls='--',color='#555',label='Bez listwy: front–dno')
    for j,label,color in zip(['front_bottom','front_cleat','bottom_cleat'],['30 mm: front–dno','30 mm: front–listwa','30 mm: dno–listwa'],['#cf7200','#258299','#6956a5']):
        ax[0].plot(ns,[tr(f'N{n}_B30_REF',j) for n in ns],marker='o',color=color,label=label)
    ax[0].set(xlabel='Parametr siatki całej ramy N',ylabel='Przestrzenne RMS rozciągania [kPa]',title='Lokalne naprężenia nadal zależą od siatki')
    ax[0].legend(fontsize=8)
    es=[1e7,1e8,1718e6]
    ids=['N14_B30_E1e+07','N14_B30_E1e+08','N14_B30_REF']
    for j,label,color in zip(['front_bottom','front_cleat','bottom_cleat'],['Pierwotna spoina','Nowa front–listwa','Nowa dno–listwa'],['#cf7200','#258299','#6956a5']):
        ax[1].semilogx(np.array(es)/1e6,[tr(cid,j) for cid in ids],marker='o',color=color,label=label)
    ax[1].set(xlabel='Założone efektywne E nowych spoin [MPa]',ylabel='Przestrzenne RMS rozciągania [kPa]',title='N=14, listwa 30 mm, warstwa 0,2 mm; reszta bez zmiany')
    ax[1].legend(fontsize=8)
    for a in ax:a.grid(True,alpha=.25)
    fig.suptitle('Ciężar własny + statyczne 1 kPa; kontrolna rama i sztywny kosz C04',fontsize=11)
    save(fig,'66_P19F_siatka_i_modul_nowych_spoin')
    # Wyliczone zmiany zamiast ręcznego przepisywania procentów.
    c14,c18=case('N14_B30_REF'),case('N18_B30_REF')
    comparisons=[]
    for j in ['front_bottom','front_cleat','bottom_cleat']:
        comparisons.append(dict(joint=j,N14_rms_kpa=tr('N14_B30_REF',j),N18_rms_kpa=tr('N18_B30_REF',j),
                                relative_change_N14_N18=tr('N18_B30_REF',j)/tr('N14_B30_REF',j)-1))
    result=dict(status='POSTPROCESSING_WITH_OPEN_LOCAL_STRESS_CONVERGENCE',
        cases=len(cases),load_rows=len(loads),joint_rows=len(joints),
        compliance_ratio_change_N14_to_N18=float(c18['C_frozen_to_same_mesh_no_cleat_ratio'])/float(c14['C_frozen_to_same_mesh_no_cleat_ratio'])-1,
        local_stress_mesh_comparisons=comparisons,
        min_floor_normal_reaction_n=min(float(r['minimum_floor_normal_reaction_n']) for r in loads),
        max_linear_residual=max(float(r['normalized_linear_residual']) for r in cases),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            Path(__file__),OUT/'p19f_geometrie_i_podatnosc.csv',OUT/'p19f_spoiny_i_przeniesienie_obciazen.csv',OUT/'p19f_obciazenia_i_podpory.csv']})
    (OUT/'p19f_ocena_zbieznosci.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},ensure_ascii=False))


if __name__=='__main__':main()
