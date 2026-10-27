"""Wyniki pasywnego portu:zmiana Q,limity i niezależny bilans mocy."""
from pathlib import Path
import csv,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from analiza_rozszerzenia_SB import candidates
from model_portu_wzmacniacza_P22 import port_response

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(n):
    with (OUT/n).open() as f:return list(csv.DictReader(f))


def num(v,d=6):return f'{float(v):.{d}g}'.replace('.',',')


def save(fig,n):
    fig.savefig(OUT/(n+'.png'),dpi=170);fig.savefig(OUT/(n+'.svg'));plt.close(fig)


def main():
    summary=json.loads((OUT/'p22a_podsumowanie.json').read_text());checks=json.loads((OUT/'p22a_kontrole_niezalezne.json').read_text())
    assert summary['networks']==3240 and checks['independent_KCL_KVL_points']==19440
    rows=read('p22a_naped_z_portem.csv');qs=read('p22a_Q_z_rezystancja.csv');pool=candidates();ids=[c for c,p,d,x in pool]
    lookup={c:d for c,p,d,x in pool}
    fig,axes=plt.subplots(2,1,figsize=(13,7.5),constrained_layout=True,sharex=True)
    x=np.arange(len(ids))
    for shift,rs,color in [(-.2,.1,'#007c91'),(.2,.5,'#cb4b16')]:
        y=[100*float(next(r for r in qs if r['configuration']==cid and float(r['volume_l'])==100 and float(r['rs_ohm'])==rs)['relative_q_increase']) for cid in ids]
        axes[0].bar(x+shift,y,width=.38,label=f'R źródła {rs:g} Ω',color=color)
        y=[-float(next(r for r in rows if r['configuration']==cid and float(r['volume_l'])==100 and float(r['rs_ohm'])==rs and r['network']=='RL0_C0' and float(r['f_hz'])==80)['difference_from_ideal_source_db']) for cid in ids]
        axes[1].bar(x+shift,y,width=.38,label=f'R źródła {rs:g} Ω',color=color)
    axes[0].set(ylabel='Wzrost Qtc względem R=0 [%]',title='Rzut Le=0/L=0/C=0; ta sama mechaniczna częstotliwość własna')
    axes[0].legend();axes[1].set(ylabel='Zmniejszenie pułapu SPL przy 80 Hz [dB]',xlabel='Konfiguracja elektryczna; pełne modele w tabelach raportu',
        title='Pełne katalogowe Le; osobny sinus 80 Hz, 40 V RMS / 12 A RMS / katalogowe Xmax',xticks=x,xticklabels=ids)
    axes[1].tick_params(axis='x',labelrotation=45,labelsize=9)
    for ax in axes:ax.grid(axis='y',alpha=.25)
    fig.suptitle('Rezystancja wyjścia i przewodów zmienia tłumienie oraz budżet napięcia\n27 konfiguracji / 100 l / monopol 2π, 1 m; scenariusze, nie pomiar wzmacniacza',fontsize=12)
    save(fig,'87_P22A_rezystancja_zrodla_i_obwiednia')
    fig,axes=plt.subplots(1,2,figsize=(12.5,5.2),constrained_layout=True)
    f=np.geomspace(20,200,400)
    for cid in ['C02','C04','C26P','C26S']:
        d=lookup[cid];r=port_response(d,100,f,.1,300e-6,10e-6)
        axes[0].semilogx(f,100*(abs(r['source_current']/r['driver_current'])-1),label=cid+' '+d.name.replace('SB Acoustics ','').replace('Dayton ',''))
    axes[0].set(xlabel='Częstotliwość [Hz]',ylabel='|I źródła| / |I głośnika| − 1 [%]',title='Prądy dwóch różnych portów; R=0,1 Ω')
    axes[0].legend(fontsize=8);axes[0].grid(alpha=.25,which='both')
    select=[next(r for r in rows if r['configuration']=='C26P' and float(r['volume_l'])==100 and float(r['rs_ohm'])==.5 and r['network']=='L300u_C10u' and float(r['f_hz'])==hz) for hz in [20,40,80]]
    x=np.arange(3);bottom=np.zeros(3)
    for key,label,color in [('source_resistance_loss_w','Straty R źródła','#cb4b16'),('coil_copper_loss_w','Miedź cewki','#007c91'),('mechanical_loss_w','Straty mechaniczne','#6c4797')]:
        values=np.array([float(r[key]) for r in select]);axes[1].bar(x,values,bottom=bottom,label=label,color=color);bottom+=values
    axes[1].set(xticks=x,xticklabels=['20','40','80'],xlabel='Oddzielny sinus [Hz]',ylabel='Moc czynna [W]',title='C26P / 100 l / R=0,5 Ω; obwiednia V/I/X')
    axes[1].legend(fontsize=8);axes[1].grid(axis='y',alpha=.25)
    fig.suptitle('Założony szeregowy L=300 µH i równoległy C=10 µF\nPrąd pojemności nie jest prądem cewki; to model liniowy bez czasu pracy i pokoju',fontsize=12)
    save(fig,'88_P22A_dwa_prady_i_bilans_mocy')
    examples=[]
    for cid in ['C02','C04','C26P','C26S']:
        a=next(r for r in qs if r['configuration']==cid and float(r['volume_l'])==100 and float(r['rs_ohm'])==.1)
        b=next(r for r in rows if r['configuration']==cid and float(r['volume_l'])==100 and float(r['rs_ohm'])==.1 and r['network']=='RL0_C0' and float(r['f_hz'])==80)
        examples.append(f'|{cid}: {lookup[cid].name}|{num(a["qtc_Le0_ideal"])}|{num(a["qtc_Le0_with_source_R"])}|{num(b["difference_from_ideal_source_db"])} dB|')
    example_table='\n'.join(examples)
    md=f'''# Raport 047 — P22A: rzeczywisty port źródła w modelu liniowym

Stan: 2026-10-27. **Obliczenia i symulacje**, bez badania fizycznego
wzmacniacza. Parametry obwodu są jawnie przyjętymi scenariuszami.

## Wniosek dla prototypu

**Rekomendacja:** końcowy model powinien obejmować łączną impedancję
wyjściową źródła i przewodów. Ograniczenie prądu należy przypisać do
właściwego miejsca obwodu. Przy filtrze wyjściowym prąd wzmacniacza może
różnić się od prądu cewki; napięcie źródła też nie musi być napięciem
na zaciskach głośnika. Nie są to dwa określenia tej samej wielkości.

**Obliczenie:** mała rezystancja ma większe znaczenie względne dla
niskoimpedancyjnego połączenia. C26P przy100l i Rźródła=0,1Ω ma
Qtc około0,6106 zamiast0,5692 w rzucie Le=0. C26P pozostaje przykładem,
nie wybranym głośnikiem. Nie określono dopuszczalnego R z briefu;
trzeba powiązać ten parametr z końcowym DSP i budżetem napięcia.

![Rezystancja źródła a tłumienie i obwiednia napędu](../wyniki/87_P22A_rezystancja_zrodla_i_obwiednia.png)

## Wykonany zakres i jednostki

27konfiguracji elektrycznych,4objętości30/60/100/150l,6rezystancji
0/0,02/0,1/0,5/1/2Ω i5rodzin L/C. Razem3240modeli portu i19440punktów
napędu przy20/25/31,5/40/63/80Hz. Osobno648projekcji Q i siatka10–200Hz
licząca{summary['frequency_points_per_sweep']}częstotliwości na model.
R=2Ω i L=300µH są próbami stresowymi, nie zaleceniem konstrukcyjnym.

Fazory napięć,prądów i ciśnienia są RMS. Ruch membrany oceniono jako
szczyt sqrt(2)*|X|. Ciśnienie pochodzi z idealnego monopola2π/1m;
nie jest prognozą w pokoju42,55m³. Każdy punkt oznacza oddzielny ustalony
sinus,bez kwalifikacji czasu pracy,muzyki lub kompresji cieplnej.
Wspólne40V RMS/12A RMS i katalogowe Xmax służą porównaniu.
Nie użyto nieznanej mocy katalogowej C26P jako limitu cieplnego.

[Konfiguracja](../dane/konfiguracje/p22a_port_wzmacniacza.json),
[punkty napędu](../wyniki/p22a_naped_z_portem.csv),
[zmiana transferu](../wyniki/p22a_zmiana_transferu.csv).

## Równania i bilans energii

Pasywny port Thevenina ma szeregowe Rs+sLs i pojemność Cp na zaciskach:

    Zm = Rms+s*Mms+K/s
    K = 1/Cms+rho*c²*Sd²/Vb
    Vt = (Re+s*Le)*Id+BL*v
    Zm*v = BL*Id
    Is = Id+s*Cp*Vt
    Vs = Vt+(Rs+s*Ls)*Is

Te cztery ostatnie równania rozwiązano także niezależną macierzą4×4
dla wszystkich19440opublikowanych punktów. Maksymalna różnica względna
wynosi{num(checks['max_relative_direct_system_error'])}.
Model5stanów x,v,Id,Is,Vt dla dodatnich Le,Ls,Cp daje osobną kontrolę162punktów:
różnica do{num(checks['max_relative_state_space_error'])}.

    E = (K*x²+M*v²+Le*Id²+Ls*Is²+Cp*Vt²)/2
    dE/dt = Vs*Is-Rs*Is²-Re*Id²-Rms*v²

Indukcyjności i pojemność magazynują energię. W ustalonym sinusie:

    Re(Vs*conj(Is)) = Rs*|Is|²+Re*|Id|²+Rms*|v|²

Maksymalny względny residual bilansu w3240siatkach wynosi
{num(summary['max_energy_relative_residual'])}. To kontrola numeryczna,
nie dokładność przewidywania fizycznego egzemplarza.
Nie dodano kolejny raz masy promieniowania do katalogowego Mms.

![Oddzielne prądy i udział strat czynnych](../wyniki/88_P22A_dwa_prady_i_bilans_mocy.png)

## Co można wyprowadzić po całej dodatniej rezystancji

Dla Le=Ls=Cp=0 i Rtotal=Re+Rs:

    Q(Rs) = sqrt(M*K)/(Rms+BL²/(Re+Rs))
    dQ/dRs > 0
    f_mechanical = sqrt(K/M)/(2*pi)

Zmienia się tłumienie, nie mechaniczna częstotliwość własna tej projekcji.
Nie przypisujemy jednego Q ogólnemu układowi RLC z dodatkowymi biegunami.

| Przykład 100 l / R źródła 0,1 Ω | Qtc przy R=0, Le=0 | Qtc z Rs, Le=0 | Zmiana pułapu przy 80 Hz, pełne Le |
|---|---:|---:|---:|
{example_table}

**Dowód dla samego Rs:** przy stałej częstotliwości>0 pasywny głośnik
ma Re(Zdriver)>0. Wówczas

    d|Zdriver+Rs|²/dRs = 2*(Re(Zdriver)+Rs) > 0

Przy wspólnych limitach Vs,Is i X obwiednia dopuszczalnego prądu głośnika
nie rośnie po dodaniu Rs. Jej trzy ograniczenia to
Vmax/|Zdriver+Rs|,Imax i Xmax/(sqrt(2)*|X/Id|).
To wniosek dla wszystkich Rs≥0 i każdego dodatniego f w tym modelu,
nie tylko tabeli.648grup porównano również numerycznie.
Gdy aktywny jest sam katalogowy limit ruchu, ten sam ruch daje ten sam
pułap monopola. Rezystor nie zwiększa Sd ani Xmax.

Nie przenosimy tego dowodu na dowolny obwód LC,aktywną pętlę,
model temperatury lub realny wzmacniacz. L/C mogą zmieniać rozkład napięć
i prądów przy zachowaniu pasywności całego obwodu.

## Granice oraz brakujące zjawiska

- Rs=Ls=Cp=0 odtwarza wcześniejszy model głośnika.
- Ls→0 i Cp→0 redukują odpowiednie elementy równań bez dodawania strat.
- Rs→∞ przy ustalonym Vs i f oznacza zanik prądu oraz ruchu. Świadkowie
  przy10⁴/10⁸Ω zachowują zbieżność Rs*|Is|→1 dla Vs=1V.
- Le=0 to osobna projekcja drugiego rzędu;nie pomiar nieliniowej cewki.
- Katalogowe Le i liniowe T/S nie obejmują PWM,sprzężenia wzmacniacza,
  zasilacza,clippingu,dynamicznego ograniczenia prądu lub regeneracji energii.

Zerowy Rs jest prawidłową granicą źródła idealnego,nie stwierdzeniem o
rezystancji przewodów. Dane R/L/C nie zostały przypisane żadnemu producentowi.
Nie wykonywano doboru handlowego ani zakupu elektroniki.

## Odtwarzanie i kolejny krok

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_port_P22A.py

[Kontrole i tożsamości](../wyniki/p22a_kontrole_niezalezne.json),
[manifest](../wyniki/manifest_portu_P22A.json).
Kolejny etap P22B/P24 ma objąć saturację,SEM od ruchu,wykonalność
jednoczesnego ograniczenia V/I oraz dynamiczną ochronę X/T po korekcji DSP.
Badanie P21B nadal ma osobny aktywny przebieg;następnie P21C wiąże główną
komorę,wypełnienie i regulację. Wybór jednego głośnika i konstrukcji,
końcowy PDF i Release1 pozostają otwarte.
'''
    # Odstępy tylko w nowej prozie,bez modyfikacji wzorów,linków i surowych tabel.
    import re
    lines=[]
    for line in md.splitlines():
        if not line.startswith(('    ','|')) and '](' not in line and '://' not in line:
            line=re.sub(r'(?<=[a-ząćęłńóśźż])(?=\d)|(?<=\d)(?=[a-ząćęłńóśźż])',' ',line)
            line=re.sub(r',(?!\d)(?=\S)',', ',line)
            line=re.sub(r'([;:])(?=[^\s*])',r'\1 ',line)
            line=re.sub(r'(\d)(k?Hz|dB|ms|Ω|µH|V|A)\b',r'\1 \2',line)
            line=re.sub(r'(?<=\d) e([+-]\d)',r'e\1',line)
        lines.append(line)
    (ROOT/'raporty/047_port_zrodla_tlumienie_i_bilans.md').write_text(('\n'.join(lines)+'\n').replace('P22 A','P22A'))
    print('P22A report047,figures87–88;passive assumed port,not measured amp.')


if __name__=='__main__':main()
