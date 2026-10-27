"""P24A:ściśle warunkowy wynik modelu i jawna cena konserwatywnego zapasu."""
from pathlib import Path
from fractions import Fraction as F
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
    study=json.loads((OUT/'p24a_podsumowanie.json').read_text());exact=json.loads((OUT/'p24a_weryfikacja_dokladna_LDL.json').read_text())
    drive=json.loads((OUT/'p24a_naped_i_ODE_podsumowanie.json').read_text());symbols=json.loads((OUT/'p24a_tozsamosci_symboliczne.json').read_text())
    assert study['cases']==exact['accepted']==972 and drive['continuous_ODE_cases']==36 and len(symbols['identities'])==5
    records=[json.loads(p.read_text()) for p in sorted((ROOT/study['checkpoint_folder']).glob('*.json'))]
    table=read('p24a_obszary_i_poziomy.csv');performance=read('p24a_naped_i_cena_zapasu.csv');observations=read('p24a_ciagle_trajektorie_z_temperatura.csv')
    selected=[r for r in table if float(r['volume_l'])==100 and float(r['Rth_assumed_k_w'])==.6 and float(r['temperature_rise_limit_k'])==80 and float(r['X_catalog_reference_fraction'])==.6]
    key='C02_V100_Rth0.6_T80_X0.6';reference=next(r for r in records if r['case_id']==key);cert=reference['certificate'];p={k:float(F(v)) for k,v in cert['parameters'].items()}
    example=[r for r in performance if r['case_id']==key and float(r['frozen_temperature_rise_k'])==0]
    fig,axes=plt.subplots(1,2,figsize=(13,5.4),constrained_layout=True)
    axes[0].bar(np.arange(len(selected)),[float(r['source_peak_voltage_v']) for r in selected],color='#007c91')
    axes[0].set(xticks=np.arange(len(selected)),xticklabels=[r['configuration'] for r in selected],
        ylabel='Dopuszczony świadek napięcia źródła [V peak]',xlabel='Konfiguracja;większy wynik nie oznacza lepszego głośnika',title='100 l / Rth=0,6 K/W / ΔT=80 K / Xref=0,6 Xmax')
    axes[0].tick_params(axis='x',labelrotation=90,labelsize=8);axes[0].grid(axis='y',alpha=.25)
    f=[float(r['f_hz']) for r in example]
    axes[1].semilogx(f,[float(r['individual_sine_spl_rms_2pi_1m_db']) for r in example],'o-',color='#cb4b16',label='Osobny sinus:limity X/I/V')
    axes[1].semilogx(f,[float(r['universal_witness_spl_rms_2pi_1m_db']) for r in example],'o-',color='#007c91',label='Stały poziom:świadek LMI')
    axes[1].set(xlabel='Częstotliwość [Hz]',ylabel='SPL RMS [dB],2π / 1 m',title='C02 / 100 l;zamrożone θ=0;ten sam Icap i Xref')
    axes[1].set_xticks(f,labels=[f'{v:g}'.replace('.',',') for v in f])
    axes[1].xaxis.set_minor_formatter(NullFormatter())
    axes[1].grid(alpha=.25,which='both');axes[1].legend(fontsize=9)
    fig.suptitle('Stała granica napięcia dla dowolnego ograniczonego sygnału w zadanym modelu\nŚwiadkowie dopuszczalności,nie optimum i nie gwarancja fizycznego urządzenia',fontsize=12)
    save(fig,'92_P24A_napiecie_i_cena_konserwatyzmu')
    keywave='C26P_V100_Rth0.6_T80_X0.6_ambient_step'
    with np.load(OUT/'p24a_przebiegi_reference.npz') as data:wave=data[keywave]
    record=next(r for r in records if r['case_id']=='C26P_V100_Rth0.6_T80_X0.6');param={k:float(F(v)) for k,v in record['certificate']['parameters'].items()}
    fig,axes=plt.subplots(2,1,figsize=(11,6.7),constrained_layout=True,sharex=True)
    axes[0].plot(wave[:,0],wave[:,6],color='#007c91',label='W:funkcja Lapunowa,bez jednostki energii')
    axes[0].axhline(1,color='#cb4b16',ls='--',label='Granica obszaru W=1')
    axes[0].set(ylabel='W [-]',title='C26P / 100 l / skok napięcia do granicy świadka / zimny start')
    axes[0].legend(fontsize=9)
    axes[1].plot(wave[:,0],abs(wave[:,2])/param['Xref'],label='|x|/Xref',color='#6c4797')
    axes[1].plot(wave[:,0],abs(wave[:,4])/param['Icap'],label='|i|/Icap',color='#007c91')
    axes[1].axhline(1,color='#cb4b16',ls='--');axes[1].set(ylabel='Wykorzystanie granicy [-]',xlabel='Czas [s]')
    axes[1].legend(fontsize=9)
    for ax in axes:ax.grid(alpha=.25)
    fig.suptitle('Ciągłe ODE z Re(θ),ruchem i grzaniem;Cth=200 J/K jest założeniem\nPrzebieg ilustruje wybraną rodzinę;dowód opiera się na dokładnych nierównościach',fontsize=12)
    save(fig,'93_P24A_obszar_ruch_prad_i_czas')
    r=next(r for r in records if r['case_id']=='C04_V100_Rth0.6_T80_X0.6');p4={k:float(F(v)) for k,v in r['certificate']['parameters'].items()}
    a=p4['Re0']*p4['Icap']**2;b=1/p4['Rth']-p4['alpha']*a;equilibrium=a/b
    fig,axes=plt.subplots(1,2,figsize=(12.5,5.2),constrained_layout=True)
    t=np.linspace(0,600,500)
    for cth in [50,200]:axes[0].plot(t,equilibrium*(1-np.exp(-b*t/cth)),label=f'Górne porównanie,Cth={cth} J/K')
    axes[0].axhline(80,color='#cb4b16',ls='--',label='Umowna granica80 K')
    axes[0].set(xlabel='Czas [s]',ylabel='Przyrost temperatury [K]',title='Obwiednia przy |i|≤Icap,nie prognoza samogrzania')
    axes[0].legend(fontsize=8);axes[0].grid(alpha=.25)
    with np.load(OUT/'p24a_przebiegi_reference.npz') as data:
        for kind in ['sine20','two20_85','step']:
            w=data['C04_V100_Rth0.6_T80_X0.6_ambient_'+kind]
            axes[1].plot(w[:,0],w[:,5],label={'sine20':'Sinus20 Hz','two20_85':'20+85 Hz','step':'Skok'}[kind])
        short=w[:,0]
    axes[1].plot(short,equilibrium*(1-np.exp(-b*short/200)),'--',color='#cb4b16',label='Porównanie górne,Cth200')
    axes[1].set(xlabel='Czas [s]',ylabel='Przyrost temperatury [K]',title='C04 / 100 l / trzy wybrane zimne przebiegi')
    axes[1].legend(fontsize=8);axes[1].grid(alpha=.25)
    fig.suptitle('Ciepło miedzi i jednobiegunowy model cieplny;Rth,Cth,α i ΔT są założeniami\nObwiednia analityczna oceniona float;nie temperatura fizycznej cewki ani certyfikat produktu',fontsize=12)
    save(fig,'94_P24A_temperatura_i_obwiednia_porownawcza')
    failures=[dict(case_id=r['case_id'],trial=t) for r in records for t in r['trials'] if not t.get('candidate_accepted',False)]
    post=dict(status='COMPLETE_SCOPED_EXACT_MODEL_INVARIANCE_AND_COST_NOT_DEVICE_CERTIFICATION',
        accepted_certificates=972,temperature_endpoint_LMIs=1944,rejected_search_trials=len(failures),failed_trials=failures,
        continuous_ODE_cases=36,performance_rows=11664,thermal_comparison_rows=23328,
        max_sampled_W=max(float(r['max_sampled_W']) for r in observations),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),
            OUT/'p24a_podsumowanie.json',OUT/'p24a_weryfikacja_dokladna_LDL.json',OUT/'p24a_naped_i_ODE_podsumowanie.json',OUT/'p24a_tozsamosci_symboliczne.json']},
        limitations=['Exact feasibility for declared decimal model parameters does not establish physical fidelity or global optimality.',
            'Safe-source bound excludes LC,nonlinear BL/Cms/Le,unidentified extra heating and DAC reconstruction uncertainty.',
            'Frozen-temperature sine cost is a comparison,not inevitable protection penalty or measured usable SPL.'],
        next='P21C main chamber;P24B and P25 integrate realistic signals,filtering and wider uncertainty before final selection.')
    (OUT/'p24a_ocena_projektowa.json').write_text(json.dumps(post,ensure_ascii=False,indent=2,allow_nan=False))
    examples='\n'.join(f'|{float(v["f_hz"]):g} Hz|{num(v["universal_witness_spl_rms_2pi_1m_db"])} dB|{num(v["individual_sine_spl_rms_2pi_1m_db"])} dB|{num(v["conservative_level_difference_db"])} dB|' for v in example)
    certificate_link='../'+study['checkpoint_folder']+'/'+key+'.json'
    md=f'''# Raport 049 — P24A: wspólny obszar ruchu, prądu i temperatury

Stan: 2026-10-27. **Wynik matematyczny dla zadanej rodziny modeli**, uzupełniony
symulacjami. Nie jest to certyfikacja fizycznego głośnika lub zabezpieczenia.

## Wniosek dla prototypu

**Obliczenie i dowód warunkowy:** dla 972 rodzin znaleziono stałą granicę
napięcia źródła oraz obszar stanów, który w określonym modelu utrzymuje
ruch, prąd i przyrost temperatury w zadanych granicach. Wynik obejmuje
**dowolny sygnał o ograniczonej amplitudzie** i wszystkie temperatury
w przedziale, a nie tylko wybrane sinusy lub próbki siatki temperatur.

**Rekomendacja:** użyć tego wyniku jako konserwatywnego punktu odniesienia
przy badaniu ochrony. Nie przyjmować go automatycznie jako końcowej nastawy
wysokiej wydajności. Przykład C02/100 l daje około 4,99 V peak, podczas gdy
osobny sinus może korzystać z większej amplitudy. Ta różnica pokazuje cenę
wybranego wystarczającego warunku. Nie dowodzi, że każda skuteczna ochrona
musi tyle tracić ani że większe wejście jest niemożliwe.

![Stała granica napięcia i cena wybranego zapasu](../wyniki/92_P24A_napiecie_i_cena_konserwatyzmu.png)

C04 i C02 nadal są przykładami. Nie dokonano końcowego wyboru przetwornika.

## Założenia i wykonany zakres

27 konfiguracji × 3 objętości60/100/150 l × Rth0,3/0,6/1,2 K/W ×
przyrost40/80 K × Xref0,6/1 katalogowego Xmax = 972 rodziny.
Progi to osie scenariuszy, nie zatwierdzona specyfikacja briefu.
Xmax nie jest gwarancją niskiego THD, a przyjęty przyrost temperatury
nie jest dopuszczeniem izolacji, kleju lub materiału cewki.

Model ma stałe M,K,Le,BL,Rms,sztywne ścianki,gaz0D i brak zewnętrznego LC.
Katalogowe Le reprezentuje tu jedną dodatnią stałą cewkę. Nie identyfikuje
to fizycznego Ld, zespolonego Lgen lub pamięci motoru z P12C.
Re(θ)=Re0*(1+αθ), z umownym α=0,004/K. Ciepło obejmuje wyłącznie miedź:

    Cth*theta_dot = Re0*(1+alpha*theta)*i²-theta/Rth
    Cth > 0

Nie dodano nieznanego grzania od prądów wirowych, zmian BL/Le/K z temperaturą
lub ruchu paneli. Parametry termiczne nie zostały przypisane produktom.
Pula obejmuje STX i wszystkie trzy SB; dawne badania nieliniowe dla24baz
nie stają się przez to pomiarami nowych modeli.

[Konfiguracja modelu](../dane/konfiguracje/p24a_wspolny_obszar_niezmienniczy.json),
[warunki ODE i porównań](../dane/konfiguracje/p24a_weryfikacja_i_sygnaly.json),
[tabela972obszarów](../wyniki/p24a_obszary_i_poziomy.csv).

## Model i wspólna elipsoida

Stan fizyczny z=(x,v,i). Napięcie u jest napięciem portu Thevenina przed Rs.
To nie zawsze napięcie zacisków głośnika. P22A pokazuje osobne znaczenie LC.

    xdot=v
    M*vdot=BL*i-Rms*v-K*x
    Le*idot=u-(Re0*(1+alpha*theta)+Rs)*i-BL*v
    xi=(x/Xref, v/(1 m/s), i/Icap)
    xi_dot=A(theta)*xi+b*u
    W=xi.T*inv(X)*xi

Macierz X jest dodatnio określona. W jest bezwymiarową funkcją Lapunowa,
**nie energią fizyczną w J**. Wyszukano X,λ,γ spełniające

    A(theta)*X+X*A(theta).T+lambda*X+gamma*b*b.T <= 0
    X[0,0] <= 1, X[2,2] <= 1
    lambda>0, gamma>0
    U² <= lambda*gamma

Zapis „≤0” dla macierzy oznacza ujemną półokreśloność, nie porównanie
każdego elementu. A jest afiniczne w θ. Sprawdzenie obu końców przedziału
daje więc tę samą nierówność dla każdego θ pomiędzy nimi, także zmiennego
w czasie. Nie zakładamy stałej temperatury w tym dowodzie.

Po domknięciu kwadratu, z a=xi.T*inv(X)*b:

    Wdot <= -lambda*W-gamma*a²+2*a*u
         <= -lambda*W+u²/gamma
         <= lambda*(1-W), gdy |u|<=U

Jeśli W(0)≤1, obszar W≤1 pozostaje niezmienniczy. Nierówność Cauchy’ego
daje |x|≤Xref i |i|≤Icap. Dodatkowo wymagamy dokładnie

    Icap² <= Ihardware²
    Re0*(1+alpha*theta_limit)*Icap² <= theta_limit/Rth

Na granicy temperatury prawa strona równania cieplnego jest niedodatnia.
Na granicy θ=0 jest nieujemna. Wspólny obszar W≤1 i0≤θ≤θlimit jest zatem
niezmienniczy w zadanym modelu. Jest to warunek na stan początkowy,
nie ochrona każdego dowolnego stanu o nieznanej energii i temperaturze.

## Wyszukiwanie i niezależne dokładne sprawdzenie

Wykonano6804próby:7wybranych λ na rodzinę. CVXPY1.6.5/Clarabel0.11.1
wyszukiwały kandydatów w osobnym środowisku. Status `optimal` nie był
kryterium dowodu. Zaokrąglone macierze pomniejszono z marginesem i przyjęto
wyłącznie po dokładnym sprawdzeniu liczb wymiernych.

Pierwsza kontrola bada wszystkie minory główne3×3. Drugi weryfikator,
napisany osobno i bez importowania kodu wyszukującego, używa eliminacji
Schura/LDL oraz stdlib Fraction. Sprawdził972dodatnie X i1944macierze
końcowe. Zweryfikował też nierówności termiczne i napięcia.
Trzy próby λ odrzucono; każda rodzina ma innego zaakceptowanego świadka.
Odrzucenie próby nie dowodzi niemożliwości większego poziomu.

Przyjęte granice napięcia wynoszą1,952715–15,37004 V peak w całej puli
scenariuszy. To nie wyznaczone globalne maksimum. Pełny przykład:
[C02/100l/Rth0,6/80K/Xref0,6]({certificate_link}).
Parametry są zdefiniowanymi liczbami dziesiętnymi modelu; dokładna
arytmetyka nie dodaje dokładności do danych producenta.

[Niezależna kontrola972świadków](../wyniki/p24a_weryfikacja_dokladna_LDL.json),
[pięć tożsamości symbolicznych](../wyniki/p24a_tozsamosci_symboliczne.json).

## Koszt względem osobnych sinusów

11664punkty porównują wspólny świadek napięcia z osobnym sinusem przy
tych samych Xref i Icap oraz szynach56,57 V peak. Dla diagnostyki liczymy
zamrożone θ=0 iθlimit. Nie jest to temperatura samogrzania stanu ustalonego.
Geometria:idealny monopol2π/1m,ciśnienieRMS,osobne ustalone sinusy20–80Hz.
Nie przeliczamy tych liczb na pokój4,6×3,7×2,5m jako faktu.

| C02/100l/zimny model | Stała granica świadka | Osobny sinus X/I/V | Różnica kryteriów |
|---|---:|---:|---:|
{examples}

Przykład ma Rth0,6 K/W,ΔT80 K iXref0,6Xmax. Duża różnica jest ceną
konkretnego wystarczającego warunku dla dowolnego wejścia, w tym DC.
Nie jest dowodem nieuniknionego kosztu dowolnego innego limitera.
Znane pasmo wejścia, właściwa realizacja filtrów i sterowanie z pamięcią
wymagają osobnej analizy, zanim wykorzystamy większy poziom.

## Ciągłe trajektorie i temperatura

36ODE obejmuje C02,C04,C05,C11,C26P,C26S, po3sygnały i2temperatury startu.
Sygnały to sinus20Hz,ograniczona suma20+85Hz i skok. Vb100l,Rth0,6 K/W,
Cth200 J/K,czas0,8s,ruch i prąd początkowo zero. Cth jest założeniem.
Napięcie źródła nie przekracza wartości zaakceptowanego świadka.

Największe próbkowane W wynosi{num(post['max_sampled_W'])}; nie znaleziono
naruszeń granic w tych realizacjach. Uniwersalny wniosek wynika z dokładnych
nierówności oraz hipotez modelu, nie z próbkowania36przebiegów.

![Przykład funkcji Lapunowa,ruchu i prądu](../wyniki/93_P24A_obszar_ruch_prad_i_czas.png)

Osobna analityczna obwiednia cieplna używa a=Re0*Icap² oraz
b=1/Rth−αa>0:

    theta_upper(t)=a/b+(theta0-a/b)*exp(-b*t/Cth)

To górne porównanie dla chwilowego |i|≤Icap, nie przewidywana temperatura
głośnika podczas muzyki.23328wartości dla Cth50/200 J/K oceniono float;
nie są przedziałami z zaokrągleniem na zewnątrz. Dokładna niezmienniczość
granic została sprawdzona oddzielnymi nierównościami.

![Analityczna obwiednia temperatury i wybrane krótkie przebiegi](../wyniki/94_P24A_temperatura_i_obwiednia_porownawcza.png)

## Granice użycia przy budowie

- Dane T/S i Rth nie identyfikują fizycznego egzemplarza. Wynik nie obejmuje
  nieznanej tolerancji BL/Cms/Le, nieliniowej pamięci lub dodatkowego grzania.
- Granica dotyczy napięcia **ciągłego portu źródła**. Ograniczenie samych
  próbek cyfrowych nie gwarantuje jej po rekonstrukcji DAC, zmianie gainu,
  filtrze wyjściowym lub nieznanym overshoot wzmacniacza.
- Projekt nie zakłada dobudowania własnego kontrolera stanu do miniDSP.
  Wzorzec stałego poziomu jest punktem odniesienia; możliwość wdrożenia
  wymaga zbadania rzeczywistego toru i jego kalibracji.
- ADAM Sub12/Sub15 są odniesieniem briefu. Te umowne progi nie zastępują
  uzgodnionych progów odbiorowych lub pomiaru THD/SPL gotowego urządzenia.

## Odtwarzanie

Dokładne sprawdzenie zapisanych świadków nie wymaga CVXPY:

    python3 skrypty/sprawdz_swiadkow_P24A.py

Odtworzenie tabel,ODE,wykresów i raportu korzysta ze świadków:

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_obszary_P24A.py

Nowe wyszukiwanie wymaga opcjonalnego środowiska `requirements_p24.txt`.
Wznowienie zgodnych972zapisów nie jest świeżym niezależnym SDP.
Źródła narzędzi: [SRC62/SRC63](../dane/zrodla/P24A_narzedzia_SDP.json).
Użycie danych,ograniczenia i pliki dowodowe pozostają w osobnym manifeście.

**Najbliższa integracja:** główna komoraP21C,wypełnienie i regulacja,
następnie ochrona z filtrami/sygnałami i szerszą niepewnością. Końcowy
wybór głośnika i skrzyni,PDF oraz Release1 pozostają otwarte. Rozbudowane
podsumowania opinii powstaną po badaniach, zgodnie z decyzją użytkownika.
'''
    # Odstępy w nowej prozie;nie modyfikujemy adresów,kodu i danych świadków.
    import re
    lines=[]
    for line in md.splitlines():
        if not line.startswith(('    ','|')) and '](' not in line and '://' not in line:
            line=re.sub(r'(?<=[a-ząćęłńóśźż])(?=\d)|(?<=\d)(?=[a-ząćęłńóśźż])',' ',line)
            line=re.sub(r',(?!\d)(?=\S)',', ',line)
            line=re.sub(r'([;:])(?=[^\s*])',r'\1 ',line)
            line=re.sub(r'(\d)(k?Hz|dB|ms|Ω|V|A)\b',r'\1 \2',line)
            line=re.sub(r'(?<=\d) e([+-]\d)',r'e\1',line)
        lines.append(line)
    rendered=('\n'.join(lines)+'\n').replace('P24 A','P24A').replace('P22 A','P22A').replace('Re 0','Re0')
    (ROOT/'raporty/049_obszar_niezmienniczy_i_koszt_ochrony.md').write_text(rendered)
    print('P24A report049,figures92–94;exact model certificates,not device certification.')


if __name__=='__main__':main()
