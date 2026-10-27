"""Wyniki nasycenia:jawne przekroczenia zamiast deklaracji gotowej ochrony."""
from pathlib import Path
import csv,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(n):
    with (OUT/n).open() as f:return list(csv.DictReader(f))


def num(v,d=6):return f'{float(v):.{d}g}'.replace('.',',')


def save(fig,n):
    fig.savefig(OUT/(n+'.png'),dpi=170);fig.savefig(OUT/(n+'.svg'));plt.close(fig)


def main():
    study=json.loads((OUT/'p22b_podsumowanie.json').read_text());checks=json.loads((OUT/'p22b_kontrole_niezalezne.json').read_text())
    assert study['cases']==648 and checks['selected_continuous_cases']==7 and not checks['time_step_flags']
    cfg=json.loads((ROOT/'dane/konfiguracje/p22b_nasycenie_i_prad.json').read_text());rows=read('p22b_trajektorie.csv')
    mesh=read('p22b_zbieznosc_i_ciagle_ODE.csv');gates=read('p22b_wykonalnosc_stanu_granicznego.csv')
    ids=list(dict.fromkeys(r['configuration'] for r in rows));x=np.arange(len(ids))
    fig,axes=plt.subplots(2,1,figsize=(13,7.5),sharex=True,constrained_layout=True)
    for gain,shift,color in [(0.,-.2,'#cb4b16'),(10.,.2,'#007c91')]:
        for ax,key,label in [(axes[0],'current_to_assumed_peak_threshold','I peak / umowny próg'),
                             (axes[1],'x_to_catalog_reference','X peak / katalogowe Xmax')]:
            values=[max(float(r[key]) for r in rows if r['configuration']==cid and float(r['feedback_gain_ohm'])==gain) for cid in ids]
            ax.bar(x+shift,values,width=.38,label=f'Feedback I: G={gain:g} Ω',color=color)
            ax.set_ylabel(label);ax.axhline(1,color='black',ls='--',lw=1);ax.grid(axis='y',alpha=.25)
    axes[0].legend();axes[0].set_title('Największy znaleziony wynik w 12 przypadkach na konfigurację i G')
    axes[1].set(xticks=x,xticklabels=ids,xlabel='Konfiguracja; sinus20 / sinus80 / dwa tony20+85 Hz,60/100 l,2poziomy')
    axes[1].tick_params(axis='x',labelrotation=45,labelsize=9)
    fig.suptitle('648 trajektorii / 0,6 s / źródło ±56,57 V / próg16,97 A peak\nBrak EQ/ochrony X/T; liniowe T/S poza Xmax są matematycznym stresem,nie prognozą produktu',fontsize=12)
    save(fig,'89_P22B_prad_i_brak_ochrony_wychylenia')
    key='C26P_V100_sine80_A1.5_G10'
    with np.load(OUT/'p22b_przebiegi_reference.npz') as data:wave=data[key]
    selected=wave[(wave[:,0]>=.40)&(wave[:,0]<=.48)]
    row=next(r for r in rows if r['case_id']==key)
    fig,axes=plt.subplots(3,1,figsize=(11,7.2),sharex=True,constrained_layout=True)
    t=selected[:,0]
    axes[0].plot(t,selected[:,1],label='Zadane napięcie',color='#9e9e9e')
    axes[0].plot(t,selected[:,2],label='Napięcie źródła po ograniczeniach',color='#007c91')
    for sign in [-1,1]:axes[0].axhline(sign*cfg['source_rail_peak_v_assumed'],color='#cb4b16',ls='--',lw=1)
    axes[0].set_ylabel('Napięcie chwilowe [V]');axes[0].legend(fontsize=8,loc='upper right')
    axes[1].plot(t,selected[:,5],color='#007c91',label='Prąd zachowanego stanu Le')
    for sign in [-1,1]:axes[1].axhline(sign*cfg['current_threshold_peak_a_assumed'],color='#cb4b16',ls='--',lw=1)
    axes[1].set_ylabel('Prąd chwilowy [A]');axes[1].legend(fontsize=8,loc='upper right')
    axes[2].plot(t,selected[:,3]*1000,color='#6c4797')
    for sign in [-1,1]:axes[2].axhline(sign*float(row['catalog_xmax_reference_mm']),color='#cb4b16',ls='--',lw=1)
    axes[2].set(ylabel='Wychylenie [mm]',xlabel='Czas [s];środki kroków obliczenia')
    for ax in axes:ax.grid(alpha=.25)
    fig.suptitle('C26P / 100 l / 80 Hz / hipotetyczne G=10 Ω; liniowy model głośnika\nPrzerywane: szyny napięcia, próg pętli prądowej i katalogowe odniesienie ruchu',fontsize=12)
    save(fig,'90_P22B_napiecie_prad_i_ruch_w_czasie')
    rates=cfg['verification_rates_hz'];errors=[max(float(r['max_error_scaled_by_catalog_X_velocity80_and_Ithreshold']) for r in mesh if int(r['integration_rate_hz'])==rate) for rate in rates]
    fig,axes=plt.subplots(1,2,figsize=(12.5,5.2),constrained_layout=True)
    axes[0].loglog(rates,100*np.array(errors),'o-',color='#007c91')
    axes[0].set(xticks=rates,xticklabels=['12k','24k','48k','96k'],xlabel='Częstotliwość integracji [1/s]',
        ylabel='Max błąd stanu ze skalowaniem odniesienia [%]',title='7świadków vs ciągłe LSODA;nie badanie sprzętu')
    axes[0].grid(alpha=.25,which='both')
    axes[0].xaxis.set_minor_formatter(NullFormatter())
    margin=np.array([float(r['required_boundary_voltage_margin_v']) for r in gates])
    axes[1].bar(np.arange(len(gates)),margin,color=np.where(margin>=0,'#007c91','#cb4b16'))
    axes[1].axhline(0,color='black',lw=1);axes[1].set(xticks=np.arange(len(gates)),xticklabels=[r['configuration'] for r in gates],
        ylabel='Margines napięcia na granicy prądu [V]',xlabel='Umowny stan x=0,|v|=2π*80Hz*Xmax,I przeciwne do v',
        title='Lokalna wykonalność;bez dowodu osiągalności stanu')
    axes[1].tick_params(axis='x',labelrotation=90,labelsize=8);axes[1].grid(axis='y',alpha=.25)
    fig.suptitle('Dokładność obliczeń i osobne ograniczenie fizyczne sterowania\nMargines=Vrail+(Re+Rs)*Ipróg−|BL*v|;ujemny:żadne napięcie w szynach nie zatrzyma przyrostu |I|',fontsize=11)
    save(fig,'91_P22B_zbieznosc_i_wykonalnosc_SEM')
    maxima={}
    for gain in [0.,10.]:
        selected=[r for r in rows if float(r['feedback_gain_ohm'])==gain]
        maxima[str(gain)]={key:max(float(r[key]) for r in selected) for key in ['current_to_assumed_peak_threshold','x_to_catalog_reference']}
    maxerr=next(errors[i] for i,rate in enumerate(rates) if rate==cfg['integration_rate_hz'])
    assessment=dict(status='COMPLETE_SCOPED_SOURCE_SATURATION_AND_CURRENT_FEEDBACK_NOT_PROTECTION',
        cases=648,independent_continuous_cases=7,step_comparisons=28,remaining_numerical_flags=0,
        max_scaled_state_error_at_primary_rate=maxerr,maxima_by_feedback=maxima,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),
            OUT/'p22b_podsumowanie.json',OUT/'p22b_kontrole_niezalezne.json',OUT/'p22b_trajektorie.csv']},
        limitations=['Current feedback G10 is a finite-gain law,not guaranteed current or excursion protection.',
            '208 mathematical trajectories exceed catalog X reference and cannot be read as quantitative physical product predictions.',
            '27 local kinematic boundary witnesses do not prove reachability;11 show a local control-voltage infeasibility under the assumptions.',
            'Selected seven ODE comparisons and four time steps do not certify every trajectory or every Le->0 limit.'],
        next='P24:model-based excursion/current/thermal protection after P23;P21C main chamber and integrated selection remain open.')
    (OUT/'p22b_ocena_projektowa.json').write_text(json.dumps(assessment,ensure_ascii=False,indent=2,allow_nan=False))
    md=f'''# Raport 048 — P22B: nasycenie, SEM i zachowany stan prądu

Stan:2026-10-27. **Symulacje warunkowych rodzin**,bez fizycznego wzmacniacza.
Pętla prądowa i szyny napięcia są założeniami. Nie jest to gotowa ochrona.

## Co wynika dla prototypu

**Wynik negatywny:** hipotetyczny feedback prądu o skończonym wzmocnieniu
zmniejsza przekroczenie prądu,ale nie zapewnia twardego limitu i nie chroni
samodzielnie wychylenia. W 648trajektoriach zachowano82przypadki powyżej
umownego progu prądu:41dla G=0 i41dla G=10Ω. Maksimum Ipeak/Ipróg spada
z{num(maxima['0.0']['current_to_assumed_peak_threshold'])} do
{num(maxima['10.0']['current_to_assumed_peak_threshold'])}.
208trajektorii przekracza katalogowe odniesienie Xmax:104w każdej grupie G.
Nie oznacza to208potwierdzonych przeciążeń fizycznego urządzenia.

Największy ruch matematycznej rodziny ma STX W.32.500.8.MC_v2 przy100l,
sinusie20Hz i silnym zadaniu. Prąd nie uruchamia tu pętli;sam feedback I
pozostawia ruch około3,353Xmax odniesienia. To kontrprzykład dla tezy,
że kontrola samego prądu zawsze wystarcza do kontroli ruchu. Ilościowy ruch
poza domeną liniowych T/S nie jest prognozą rzeczywistego STX ani jego THD.

![Prąd i brak samodzielnej ochrony ruchu](../wyniki/89_P22B_prad_i_brak_ochrony_wychylenia.png)

**Rekomendacja:** P24 ma kontrolować model ruchu i historię cieplną
oprócz napięcia/prądu. Należy zachować energię indukcyjności i SEM od ruchu,
zamiast wstawiać arbitralne clip(I) do równania siły. Potrzebny będzie
również opis,co rzeczywisty wzmacniacz robi z energią zwracaną.

## Wykonany eksperyment

27konfiguracji ×60/100l ×2poziomy ×3sygnały ×G=0/10Ω =648trajektorii.
Sygnały:sinus20,sinus80 i suma20+85Hz. Skala0,5/1,5 mnoży odniesienie
40V RMS;w sumie tonów to RMS całej sumy bez rampy. Rozruch ma gładką
rampę40ms. Szyny±56,5685V i próg16,9706A peak są założeniami;próg pętli
nie jest gwarantowanym ogranicznikiem. Rs=0,1Ω,brak zewnętrznego LC.

Czas0,6s,ostatnie okno0,2s,stany początkowe zero. Krok1/48000s
oznacza rozdzielczość integracji,nie PWM lub Fs wybranego miniDSP.
Nie użyto tu LT ani realnej muzyki:zadanie oznacza hipotetyczne napięcie
po DAC. Wyniki nie potwierdzają stanu okresowego,czasu bezpiecznej pracy,
kompresji,THD lub charakterystyki w pokoju42,55m³.

[Konfiguracja](../dane/konfiguracje/p22b_nasycenie_i_prad.json),
[648trajektorii i flagi domeny](../wyniki/p22b_trajektorie.csv),
[trzy pełne przebiegi](../wyniki/p22b_przebiegi_reference.npz).
Zapis zawiera środki kroków;kolumna energii jest jawnie energią końca kroku.
Licznik przekroczenia jest odsetkiem kroków z przekroczeniem w odczycie,
nie dokładnym czasem fizycznego przeciążenia.

## Równania i źródło nieliniowości

W tym etapie głośnik ma liniowe,stałe T/S i Le>0. Nieliniowy jest port źródła:

    dx/dt = v
    M*dv/dt = BL*i-Rms*v-K*x
    Le*di/dt = u-(Re+Rs)*i-BL*v
    u = clip(cmd-G*sign(i)*max(|i|-Ipróg,0),-Vrail,+Vrail)

To pętla statyczna o skończonym wzmocnieniu G w Ω,bez pamięci. Nie określa
pasma ani topologii rzeczywistej elektroniki. Dodatni/ujemny port napięcia
może przyjmować energię zwrotną;to ważne założenie tego modelu.
Nie przypisano mu układu zasilania,modułu klasyD lub określonego produktu.

![Zadanie,napięcie po ograniczeniach,prąd i ruch](../wyniki/90_P22B_napiecie_prad_i_ruch_w_czasie.png)

## Energia i metoda numeryczna

    E=(K*x²+M*v²+Le*i²)/2
    dE/dt=u*i-(Re+Rs)*i²-Rms*v²

Zastosowano implicit midpoint. Nie opóźnia się prawa sprzężenia o pełny
krok:wewnątrz kroku rozwiązano monotoniczne równanie skalarne dla u.
Stan indukcyjności i ruch nie są obcinane.

    zmid = inv(I-h*A/2)*zold + h/2*inv(I-h*A/2)*B*u_mid
    znew = 2*zmid-zold
    Enew-Eold = h*(u_mid*i_mid-(Re+Rs)*i_mid²-Rms*v_mid²)

Współczynnik i_mid przy u jest dodatni. Prawo sprzężenia jest ciągłe i
nierosnące w i;wynikowe równanie ma jedno rozwiązanie.100osobnych brentq
potwierdza zamknięty wzór do{num(checks['max_controller_root_error_v'])}V.
Największy względny residual energii wszystkich648trajektorii to
{num(study['integration']['max_energy_relative_residual'])}.
To kontrola równań i integratora,nie fizyczna dokładność modelu.

## Niezależna kontrola i granice

Siedem świadków obejmuje duże ruchy,prądy,dwa tony i obie wartości G.
Oddzielny solver LSODA rozwiązał ciągłe równania z własnymi bilansami energii.
28porównań ma kroki1/12000,1/24000,1/48000 i1/96000s. Przy podstawowym
kroku największy błąd stanu,skalowany katalogowym X,odpowiadającą mu
prędkością80Hz i progiem I,wynosi{num(100*maxerr)}% w tych7przebiegach.
Nie certyfikuje to automatycznie wszystkich648przypadków lub każdej fazy.

Implicit midpoint zachowuje tu dyskretną energię,ale **nie jest L-stabilny**.
Dla silnie tłumionego skalarnego modu jego współczynnik kroku dąży do−1,
nie do0. Dlatego nie deklarujemy jednostajnie poprawnej granicy Le→0
przy stałym kroku. To jawna granica metody,nie ukryta walidacja DAE.

## Wykonalność jednoczesnego ograniczenia napięcia i prądu

Na dodatniej granicy i=Ipróg trzeba zapewnić di/dt≤0. Przy źródle±Vrail
istnieje odpowiednie napięcie tylko jeśli

    -Vrail <= (Re+Rs)*Ipróg+BL*v

Na ujemnej granicy analogicznie BL*v≤Vrail+(Re+Rs)*Ipróg.
Duża SEM może uniemożliwić dotrzymanie obu ograniczeń w danym stanie.
27osobnych świadków przyjmuje x=0,|v|=2π*80Hz*Xmax i prąd przeciwny
do prędkości.11ma ujemny margines napięcia.
**Nie dowiedziono osiągalności tych stanów** przez użyty sterownik.
To lokalny test fizycznej wykonalności;dane zawierają także energię stanu
i krytyczną częstotliwość kinematyczną. Nie jest to diagnoza wzmacniacza.

![Zbieżność oraz osobny margines SEM](../wyniki/91_P22B_zbieznosc_i_wykonalnosc_SEM.png)

## Następny krok

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_nasycenie_P22B.py

[Kontrole](../wyniki/p22b_kontrole_niezalezne.json),
[ocena projektowa](../wyniki/p22b_ocena_projektowa.json).
Następne P24/P25 powinny połączyć rzeczywistą korekcję P23,model ruchu,
ograniczenia źródła,pamięć cieplną i sygnały z odpowiednim zapasem.
Wyniki P22B nie są gotową ochroną. P21B nadal ma osobny przebieg;
główna komora P21C i końcowa synteza pozostają wymagane.
Nie wybrano jeszcze finalnego głośnika/skrzyni,nie utworzono końcowego PDF
ani Release1. Podsumowania opinii czekają zgodnie z kolejnością użytkownika.
'''
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
    (ROOT/'raporty/048_nasycenie_SEM_i_stan_pradu.md').write_text(('\n'.join(lines)+'\n').replace('P22 B','P22B').replace('_v 2','_v2'))
    print('P22B report048,figures89–91;not qualified current/X/T protection.')


if __name__=='__main__':main()
