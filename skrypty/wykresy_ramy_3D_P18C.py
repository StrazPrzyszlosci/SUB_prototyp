"""Rama3D i decyzje konstrukcyjne;standardowe figury2D bezCAD."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from model_ramy_3D_P18C import Cabinet3D

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))


def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=160);fig.savefig(OUT/(name+'.svg'));plt.close(fig)


def main():
    rows=read('p18c_rama.csv');lookup={r['case_id']:r for r in rows}
    adaptive=json.loads((OUT/'p18c_adaptacja_i_granice.json').read_text())
    thick=json.loads((OUT/'p18c_zbieznosc_grubosci.json').read_text())
    check=json.loads((OUT/'p18c_kontrole.json').read_text())
    b=Cabinet3D(n=4);fig,ax=plt.subplots(figsize=(10,7),layout='constrained')
    colours=['#d95f02','#7570b3','#1b9e77','#66a61e','#e6ab02','#a6761d']
    offsets=[np.array(x)*.04 for x in [(0,-1,0),(0,1,0),(-1,0,0),(1,0,0),(0,0,-1),(0,0,1)]]
    names=['front z otworem','tył','lewy bok','prawy bok','dno','góra']
    for panel,col,offset,label in zip(b.panels,colours,offsets,names):
        xyz=panel.xyz+offset;uv=np.column_stack([xyz[:,0]+.55*xyz[:,1],xyz[:,2]+.35*xyz[:,1]])*1000
        segments=[uv[np.r_[face,face[0]]] for face in panel.boundary]
        ax.add_collection(LineCollection(segments,colors=col,linewidths=.6,alpha=.65))
        ax.plot([],[],color=col,label=label)
    ax.autoscale();ax.set_aspect('equal');ax.set(xlabel='Rzut x + 0,55y [mm]',ylabel='Rzut z + 0,35y [mm]')
    ax.legend(fontsize=9,ncol=3,loc='upper left')
    fig.suptitle('P18C: sześć osobnych brył i dwanaście podatnych połączeń\nRozsunięcie 40 mm służy prezentacji; rzeczywisty model ma wspólne powierzchnie spoin, nie jest plikiem CNC',fontsize=11)
    save(fig,'55_P18C_pelna_rama_i_polaczenia')

    fig,axs=plt.subplots(1,3,figsize=(14,4.7),layout='constrained')
    mesh=sorted([r for r in rows if r['case_id'].startswith('MESH_')],key=lambda r:int(r['mesh_n']))
    N=[int(r['mesh_n']) for r in mesh]+[r['n'] for r in adaptive['adaptive']]
    C=[float(r['wall_volume_compliance_m3_pa']) for r in mesh]+[r['compliance_m3_pa'] for r in adaptive['adaptive']]
    axs[0].plot(N,np.array(C)*1e8,'-o');axs[0].set(xlabel='Przedziały wzdłuż wnętrza N',ylabel='Podatność ×10⁸ [m³/Pa]',title='Cała rama, 2 warstwy przez MDF')
    for enhanced,style,label in [(False,'-s','Zwykły H8'),(True,'-o','EAS9')]:
        values=[r for r in check['pure_bending'] if r['enhanced']==enhanced]
        axs[1].plot([r['n_length'] for r in values],[r['compliance_ratio'] for r in values],style,label=label)
    axs[1].axhline(1,color='gray',ls=':');axs[1].set(xlabel='Elementy wzdłuż belki',ylabel='Podatność / rozwiązanie dokładne',title='Odrębna próba czystego zginania');axs[1].legend(fontsize=8)
    T=[2,3]+[r['layers'] for r in thick['rows']]
    C=[float(lookup['MESH_10']['wall_volume_compliance_m3_pa']),adaptive['thickness3']['compliance_m3_pa']]+[r['compliance_m3_pa'] for r in thick['rows']]
    axs[2].plot(T,np.array(C)*1e8,'-o');axs[2].set(xlabel='Warstwy przez grubość 22 mm',ylabel='Podatność ×10⁸ [m³/Pa]',title='Osobny kierunek zbieżności, N=10')
    for ax in axs:ax.grid(alpha=.25)
    fig.suptitle('Kontrole modelu; ostatnia zmiana siatki nie jest ścisłym certyfikatem błędu continuum',fontsize=11)
    save(fig,'56_P18C_zbieznosc_i_element_brylowy')

    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    keys=['BOND_1','TIES_1','TIES_2'];mass=[float(lookup[k]['total_mass_kg']) for k in keys];comp=[float(lookup[k]['wall_volume_compliance_m3_pa'])*1e8 for k in keys]
    axs[0].plot(mass,comp,'-o')
    for label,x,y in zip(['bez ściągu','1 ściąg','2 ściągi'],mass,comp):axs[0].annotate(label,(x,y),xytext=(6,5),textcoords='offset points')
    axs[0].set(xlabel='Masa modelu z głośnikiem [kg]',ylabel='Podatność ×10⁸ [m³/Pa]',title='Jeden: y=0,55D; dwa: y=0,4D i 0,7D')
    dynamic=read('p18c_harmoniczne.csv')
    for support in [0.,1e4,1e5,1e6]:
        data=sorted([r for r in dynamic if r['case_id']=='BOND_1' and r['signal']=='BASKET_Y_1N_RMS' and float(r['normal_each_n_m'])==support],key=lambda r:float(r['f_hz']))
        axs[1].loglog([float(r['f_hz']) for r in data],[float(r['basket_y_rms_m'])*1e6 for r in data],'-o',label='swobodna' if support==0 else f'kz={support:g} N/m/stopę')
    axs[1].set(xlabel='Częstotliwość [Hz]',ylabel='Ruch kosza [µm RMS] przy 1 N RMS',title='Osobna siła na sztywny model głośnika');axs[1].legend(fontsize=7)
    for ax in axs:ax.grid(alpha=.25)
    fig.suptitle('Pełna rama 3D: usztywnienia i podparcie — C04, 22 mm, wspólna siatka N=10\nGłośnik jako sztywna masa 6 DOF; siła kontrolna nie jest rzeczywistym napędem elektroakustycznym',fontsize=10)
    save(fig,'57_P18C_sciagi_masa_i_podparcie')

    fig,axs=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    keys=['BOND_1','BOND_0.01','BOND_0.0001','ORTHO_STRESS','SOFT_ISO_STRESS']
    labels=['referencja','0,01k spoin','0,0001k spoin','En/Gnt stres','E×0,65; ρ800']
    axs[0].bar(np.arange(5),[float(lookup[k]['wall_volume_compliance_m3_pa'])/float(lookup['BOND_1']['wall_volume_compliance_m3_pa']) for k in keys],color=['#4c78a8','#f58518','#e45756','#54a24b','#b279a2'])
    axs[0].set(xticks=np.arange(5),xticklabels=labels,ylabel='Podatność / referencja',title='Hipotezy stresowe; nie tolerancje producentów');axs[0].tick_params(axis='x',rotation=30,labelsize=8)
    joint=[r for r in read('p18c_spoiny.csv') if r['case_id']=='BOND_1' and r['load']=='GRAVITY_FLOOR_100000']
    idx=np.arange(len(joint))
    axs[1].barh(idx-.17,[float(r['rms_spatial_normal_traction_pa'])/1000 for r in joint],.32,label='normalna')
    axs[1].barh(idx+.17,[float(r['rms_spatial_tangent_traction_pa'])/1000 for r in joint],.32,label='styczna')
    axs[1].set(yticks=idx,yticklabels=[r['joint'] for r in joint],xlabel='Przestrzenne RMS trakcji [kPa]',title='Ciężar własny + głośnik; kz=10⁵ N/m/stopę')
    axs[1].tick_params(axis='y',labelsize=8);axs[1].legend(fontsize=8)
    fig.suptitle('Połączenia całej skrzyni: sztywność i obciążenie — RMS powierzchni nie jest szczytem ani nośnością spoiny',fontsize=11)
    save(fig,'58_P19D_spoiny_ciezar_i_parametry')
    path=OUT/'p19d_wirtualne_rozwarstwienie.csv'
    if path.exists():
        data=read(path.name);fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
        for label,col in [('GRAVITY','#2166ac'),('GRAVITY_PLUS_STATIC_1KPA','#b2182b')]:
            points=[r for r in data if r['load']==label];x=[float(r['crack_length_m'])*1000 for r in points]
            axs[0].plot(x,[float(r['total_potential_release_j'])/float(r['removed_area_m2']) for r in points],'-o',color=col,label=('ciężar' if label=='GRAVITY' else 'ciężar + 1 kPa statyczne')+'; N=10')
            axs[1].plot(x,[float(r['active_compressive_contact_area_fraction'])*100 for r in points],'-o',color=col)
        verification=json.loads((OUT/'p19d_weryfikacja.json').read_text())
        for r in verification['mesh_comparisons']:
            col='#2166ac' if r['load']=='GRAVITY' else '#b2182b'
            axs[0].plot(10,r['average_0_to_10mm_release_j_m2'],'x',color=col,ms=10,mew=2,label='N=14; '+('ciężar' if r['load']=='GRAVITY' else 'ciężar + 1 kPa'))
        axs[0].set(xlabel='Szerokość odspojenia od wnętrza [mm]',ylabel='Średnie GΔ(0→a) [J/m²]',title='Skończony ubytek; widoczna zależność od siatki');axs[0].legend(fontsize=7)
        axs[1].set(xlabel='Szerokość odspojenia [mm]',ylabel='Ściskana część usuniętej spoiny [%]',title='Po odspojeniu zachowano kontakt normalny')
        for ax in axs:ax.grid(alpha=.25)
        fig.suptitle('P19D: wirtualne odspojenie front–dno; N=10, sprężystość, bez tarcia\nGΔ nie jest Gc materiału, progiem inicjacji ani trwałością zmęczeniową kleju',fontsize=11)
        save(fig,'59_P19D_wirtualne_odspojenie_i_kontakt')
    path=OUT/'p19e_wymagane_moduly_stalego_frontu.csv'
    if path.exists():
        data=read(path.name);fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
        for scope,col,label in [('FRONT_ONLY','#2166ac','tylko front–korpus'),('ALL_JOINTS','#b2182b','wszystkie spoiny')]:
            for n,style in [(10,'-o'),(14,'--s')]:
                points=sorted([r for r in data if r['scope']==scope and int(r['mesh_n'])==n],key=lambda r:float(r['relative_C_allowance']))
                axs[0].semilogy([float(r['relative_C_allowance'])*100 for r in points],[float(r['effective_E_at_200um_pa'])/1e6 for r in points],style,color=col,label=label+f', N={n}')
            row=next(r for r in data if r['scope']==scope and int(r['mesh_n'])==14 and float(r['relative_C_allowance'])==.1)
            axs[1].plot([.05,.2,.5],[float(row[k])/1e6 for k in ['effective_E_at_50um_pa','effective_E_at_200um_pa','effective_E_at_500um_pa']],'-o',color=col,label=label)
        axs[0].set(xlabel='Scenariusz dopuszczonego wzrostu podatności [%]',ylabel='Próg efektywnego E spoiny [MPa]',title='Stały front, t=0,2 mm; sztywność, nie nośność');axs[0].legend(fontsize=7)
        axs[1].set(xlabel='Grubość modelowej warstwy [mm]',ylabel='Próg E [MPa] dla scenariusza +10% C',title='Ten sam kn/ks, N=14; nie prawo konkretnego kleju');axs[1].legend(fontsize=8)
        for ax in axs:ax.grid(alpha=.25)
        fig.suptitle('U-021 / P19E: obliczeniowe wymagania sztywności stałego połączenia\n5/10/20% są osiami badania, nie progami briefu; bez wniosku o adhezji, Gc, pełzaniu lub zmęczeniu',fontsize=11)
        save(fig,'60_P19E_staly_front_i_wymagany_modul')
    print('Wykresy55–60 zapisane w dostepnym zakresie')


if __name__=='__main__':main()
