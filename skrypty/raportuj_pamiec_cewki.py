"""P12C: raport z wykonanej fizyki, odczytów, dopasowań i24baz."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_cewki_z_pamiecia import FluxBranch,generalized_inductance

ROOT=Path(__file__).resolve().parents[1]


def read(name):return json.loads((ROOT/'wyniki'/name).read_text())


def rows(name):
    with (ROOT/'wyniki'/name).open() as handle:return list(csv.DictReader(handle))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(ROOT/'wyniki'/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    result=read('p12c_podsumowanie.json');checks=read('p12c_weryfikacja.json')
    packet=read('p12c_kontrola_pakietu.json');ident=read('p12c_ident_Le.json')
    proof=read('p12c_wykluczenie_1_bieguna_audyt.json');bench=read('p12c_replikacja_sily.json')
    linear=rows('p12c_liniowy_naped.csv');dynamic=rows('p12c_nieliniowa_pamiec_zweryfikowana.csv')
    force=rows('p12c_replikacja_sily.csv');step=rows('p12c_skok_pradu_i_sila.csv')
    with (ROOT/'dane/zrodla/digitalizacja/Purifi_NAB01_Lgen_fig4.csv').open() as h:
        data=sorted([r for r in csv.DictReader(h) if float(r['position_mm'])==0],key=lambda r:float(r['f_hz']))
    fdata=np.array([float(r['f_hz']) for r in data]);center=np.array([float(r['Lgen_magnitude_h']) for r in data])
    low=np.array([float(r['digitization_lower_h']) for r in data]);high=np.array([float(r['digitization_upper_h']) for r in data])
    fig,axes=plt.subplots(1,2,figsize=(12,5));f=np.geomspace(20,10000,500)
    axes[0].errorbar(fdata,center*1000,yerr=np.array([center-low,high-center])*1000,fmt='ko',label='Odczyt |Lgen| i zakres digitalizacji')
    for witness in ident['witnesses']:
        bs=[FluxBranch(**b) for b in witness['branch_parameters']]
        value=generalized_inductance(f,witness['instant_h'],bs)
        axes[0].loglog(f,abs(value)*1000,label=witness['network_id'])
        axes[1].semilogx(f,np.angle(value,deg=True),label=witness['network_id'])
    axes[0].set(xlabel='Hz',ylabel='|Lgen| [mH]',title='C18, x=0; dane producenta, nie surowy pomiar')
    axes[1].set(xlabel='Hz',ylabel='Modelowa faza Lgen [°]',title='Dwa dopuszczone dopasowania; fazy nie podano')
    for ax in axes:ax.axvspan(20,30,color='gray',alpha=.12);ax.grid(alpha=.25);ax.legend(fontsize=7)
    save(fig,'25_Lgen_modul_i_nieznana_faza')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    selected=sorted([r for r in force if float(r['q'])==0 and float(r['current_peak_a'])==1],key=lambda r:float(r['omega_tau']))
    x=np.array([float(r['omega_tau']) for r in selected]);y=np.array([float(r['H2_amplitude_ratio']) for r in selected])
    axes[0].loglog(x,y,'o',label='FFT siły');axes[0].loglog(x,np.sqrt(1+x*x),label='sqrt(1+(omega*tau)²)')
    axes[0].set(xlabel='omega*tau',ylabel='Amplituda H2: FLUX/NAIVE',title='Ten sam DC i Zblocked, różne H2 siły')
    for field,label in [('normalized_force_A2','FLUX: i*(G*i)/2'),('normalized_naive_force_A2','NAIVE: (G*i)²/2')]:
        axes[1].plot([float(r['time_over_tau']) for r in step],[float(r[field]) for r in step],label=label)
    axes[1].set(xlabel='t/tau',ylabel="F/(dL2/dx) [A²]",title='Skok prądu0,5→1A; replikacja wzoru18')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    save(fig,'26_pamiec_i_sila_wzor18')
    fig,axes=plt.subplots(1,2,figsize=(12,5));selected_case=[]
    colors={'SIMPLE':'C0','FLUX_ONE':'C1','NAIVE_ONE':'C2','FLUX_TWO':'C3'}
    for profile in ['SIMPLE','FLUX_ONE','NAIVE_ONE','FLUX_TWO']:
        part=[r for r in dynamic if r['candidate_id']=='C02' and float(r['volume_l'])==100
              and float(r['reference_envelope_fraction'])==.75 and r['profile']==profile]
        selected_case.extend(part)
        axes[0].plot([float(r['f_hz']) for r in part],[float(r['h2_pressure_pct']) for r in part],'o-',label=profile,color=colors[profile])
        if profile!='SIMPLE':
            base={float(r['f_hz']):r for r in selected_case if r['profile']=='SIMPLE'}
            axes[1].plot([float(r['f_hz']) for r in part],
                         [float(r['spl_fundamental_equivalent_4pi_1m_db'])-float(base[float(r['f_hz'])]['spl_fundamental_equivalent_4pi_1m_db']) for r in part],'o-',label=profile,color=colors[profile])
    axes[0].set(xlabel='Hz',ylabel='H2 ciśnienia ekwiwalentnego [%]',title='C02/100l; modele warunkowe, to samo V')
    axes[1].set(xlabel='Hz',ylabel='Zmiana H1 względem SIMPLE [dB]',title='Mms/Cms/BL/Rms zamrożone')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    save(fig,'27_pamiec_napedu_i_harmoniczne')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for scenario in ['REAL_LGEN_30_0.5','REAL_LGEN_100_0.5','REAL_LGEN_1000_0.5','ABS_LGEN_100_0.5']:
        part=[r for r in linear if r['candidate_id']=='C02' and float(r['volume_l'])==100 and r['scenario']==scenario]
        pole=scenario.split('_')[-2];kind='Re(Lgen)' if scenario.startswith('REAL') else '|Lgen|'
        label=f'{kind}, biegun{pole}Hz'
        axes[0].plot([float(r['f_hz']) for r in part],[float(r['delta_1v_vs_simple_db']) for r in part],'o-',label=label)
        axes[1].plot([float(r['f_hz']) for r in part],[float(r['capacity_X1_delta_vs_simple_db']) for r in part],'o-',label=label)
    axes[0].set(xlabel='Hz',ylabel='Zmiana SPL przy1Vrms [dB]',title='Umowne rodziny: strata przy1kHz=0,5Re')
    axes[1].set(xlabel='Hz',ylabel='Zmiana modelowego limitu V/I/X [dB]',title='C02/100l,40Vrms/12Arms/1Xref')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    save(fig,'28_niepewnosc_definicji_Le_i_napedu')
    exclusion=ident['one_pole_exact_exclusion'];fc_lower=np.sqrt(exclusion['required_fc2_lower_hz2']);fc_upper=np.sqrt(exclusion['required_fc2_upper_hz2'])
    min_delta=min(float(r['delta_1v_vs_simple_db']) for r in linear);max_delta=max(float(r['delta_1v_vs_simple_db']) for r in linear)
    stress=[x['extra_relative_widening'] for x in proof['stress_boxes'] if x['exclusion_proved_by_test']]
    example=[r for r in selected_case if float(r['f_hz'])==20]
    lines=[f'''# Raport 021 — pamięć cewki, definicja L_gen i siła

Stan: **2026-10-25**; źródła zebrano24października. Badania P12C przed
budową, kontynuacja raportu020. To wyniki obliczeń i warunkowych symulacji,
bez pomiaru własnego urządzenia i bez końcowej rekomendacji głośnika/skrzyni.
Obowiązują wcześniejsze bramki danych: C07 ma konflikt oznaczenia4/8Ω,
C11 niepotwierdzony aktualny status katalogowy, a C12/C18 są kontrolami10″.
Samo obliczenie przypadku nie potwierdza spełnienia briefu przez model.

## Wynik i zalecenie inżynierskie

**Do dalszych symulacji przyjąć dodatnią realizację pamięci FLUX**, z siłą
zgodną ze wzorem18 źródła w zablokowanej pozycji. KontrolaNAIVE ma taką
samą impedancję i również przechodzi bilans energii, ale interpretuje
pomocniczy prąd obwodu jako podstawę niewłaściwej siły mechanicznej.
Sam poprawny wykresZ i dodatnie straty nie walidują tego sprzężenia.

Z jednej liczby Le nie da się wyznaczyć pełnych strat/fazy i napędu w basie.
Nie wolno na tej podstawie rozstrzygnąć rzeczywistego THD24kandydatów.
Istnieją dopasowania modułu wykresu producenta, które przewidują różne fazy
20Hz. Nie są one zidentyfikowanym modelem produktu. C18 pozostaje kontrolą10″.

## Wykonany zakres i warunki

| Obszar | Wynik |
|---|---:|
| Kalibracje jednej liczby;24bazy×2definicje×5biegunów×3straty | {result['calibration_rows']} |
| Dodatnie kalibracje / odrzucone konstrukcje parametrów | {result['calibrations_valid']} / {result['calibrations_rejected']} |
| Liniowe wiersze:667sieci×4Vb×7częstotliwości | {result['linear_rows']} |
| PełneODE:24bazy×3Vb×3częstotliwości×2poziomy×4realizacje | {result['dynamic_rows']} |
| Przypadki rozstrzygnięte po dokładniejszej kontroli | {len(packet['refined_cases'])} |
| ParyFLUX_ONE/NAIVE_ONE z tą samą Zblocked | {packet['paired_force_cases']} |
| Replikacja wzoru18:tau/f/prąd/pozycja | {bench['rows']} |
| Odczyt wykresu producenta |30punktów,6częstotliwości,5pozycji |
| Dopasowania o1/2/3gałęziach | {ident['fits']} |

Liniowo Vb=30/60/100/150l, f=20/25/31,5/40/63/80/100Hz.
PełneODE Vb=30/100/150l i f=20/40/80Hz. Gaz szczelny, tau=5ms,
Re i termika cewki zamrożone. Mms/Cms/BL/Rms to efektywne, zamrożone
parametry katalogowego zestawuT/S. Dopasowanie skalaru nie zachowuje
automatycznie całej identyfikacjiT/S ani Qes.

Każdy sinus osobno, od stanu zerowego, faza0. Napęd to0,25/0,75 obwiedni
prostego modelu przy40Vrms/12Arms/Xref; napięcie jest wspólne dla porównania.
Obserwowane SPL/H2/H3 to ekwiwalentny monopol4π/1m/RMS, nie realna
kierunkowość membrany. Wyższe harmoniczne wykraczają poza sam bas.
Nie dodano ponownie frontowej masy/promieniowania ani pokoju.
Szczyty w tabeli są próbkowane; bez certyfikatu maksimum ciągłego rozruchu.

## Oryginalna definicja i digitalizacja

[Risbo et al., AES141/2016](https://purifi-audio.com/documents/content/WT1Pkt9-SxijAvNyifNN4Ao2a2)
podaje `Lgen=(Zblocked-Re)/s`. Jest to wielkość **zespolona**.
Jej część rzeczywista to Im(Zblocked)/omega, a część urojona zawiera stratę
Re(Zblocked)-Re. Na oryginalnej osi Fig4 karty NAB-01 widnieje **|Lgen|[mH]**.
Wcześniejszej niejednoznaczności nie zastąpiono domysłem; sprawdzono obraz.

Wykres producenta odczytano z oryginalnegoPDF o zachowanymSHA, render300dpi,
z jawną kalibracją osi liniowejx i logarytmicznejy. Czarną linię oddzielono
od cienkiej siatki. Nie użyto automatycznych tabel punktów Firecrawl.
Poniżej x=0; przedziały są **wyłącznie niepewnością digitalizacji**, nie
deklarowaną niepewnością producenta ani tolerancją populacji.

| Hz | Moduł L_gen [mH] | Przedział digitalizacji [mH] |
|---:|---:|---:|''']
    for r in data:lines.append(f"| {r['f_hz']} | {1000*float(r['Lgen_magnitude_h']):.4f} | {1000*float(r['digitization_lower_h']):.4f}–{1000*float(r['digitization_upper_h']):.4f} |")
    lines.append(f'''
Le0,62mH@1kHz z tabeli jest zgodne z odczytem modułu w granicach tej
digitalizacji. Nie ustalono jednak identycznej definicji i częstotliwości Le
dla wszystkich pozostałych katalogów. W porównaniu1kHz jest jawnym
wspólnym punktem kalibracji; REAL_LGEN i ABS_LGEN to różne hipotezy.
W tym raporcie x oznacza lokalne wychylenie cewki, nie współrzędną x pokoju.
Wobec tego wykresu C18 interpretacja REAL_LGEN jest kontrolą, nie odczytem osi.
„TypicalPerformance” nie rozstrzyga tu jednoznacznie pomiaru/symulacji.

## Dokładne wykluczenie jednej gałęzi i pozostała niejednoznaczność

Dla jednej gałęziR–L `|Lgen|²=A+B/(1+(f/fc)²)`. Iloraz różnic trzech
kwadratów modułu eliminuje A/B. Wyprowadzoną tożsamość sprawdzono
symbolicznie; przedziały nierówności policzono na liczbach wymiernych.
Jedne trójki wymagają fc≥**{fc_lower:.2f}Hz**, inne fc≤**{fc_upper:.2f}Hz**.
To sprzeczność dla **wszystkich dodatnich fc** tej jednogałęziowej rodziny
w zapisanych, zewnętrznie zaokrąglonych przedziałach, nie tylko dla siatki.

Wykluczenie utrzymuje się także dla dodatkowych umownych poszerzeń:
{', '.join(str(round(100*float(x),1))+'%' for x in stress)}. To stres odczytów,
nie przyjęcie tych wartości jako tolerancji producenta. Brak wykluczenia
innym testem nie dowodzi istnienia dopasowania. Nie oceniono nieznanej
pełnej niepewności źródła ani wszystkich innych klas obwodów.

Wykonano76wielostartowych dopasowań. N=1/N=2 nie dały rozwiązania
w przyjętym pudełku; dla N=3 znaleziono **{ident['within_digitization_box']}**.
Wykluczenie N=1 jest dokładne w opisanej dziedzinie; **nie udowodniono
niemożliwości N=2**. N=3 jest najmniejszym z uzyskanych dopasowań tej
kampanii, nie dowodem trzech fizycznych elementów w motorze.

Z danych tabeli C18 wynika nominalny konieczny warunek
Re(Zblocked156Hz)≤4,7Ω dla pasywnej mechaniki przy tych samych warunkach.
Nie jest tolerancją produkcji. Wszystkie znalezione modeleN3 go spełniają;
w porównaniu ogólnych rodzin **{result['nominal_C18_inconsistent']}**scenariuszy C18 go narusza.
Odrzuca się taką interpretację parametrów, a nie przetwornik.

Dwa znalezione świadki spełniają odczyty i warunek nominalny, lecz mają:

| Świadek | FazaLgen20Hz [°] | Re(Zblocked20Hz) [Ω] | Re(Zblocked156Hz) [Ω] |
|---|---:|---:|---:|''')
    for w in ident['witnesses']:lines.append(f"| {w['network_id']} | {w['Lgen_phase20_deg']:.3f} | {w['real_Z20_ohm']:.5f} | {w['real_Z156_ohm']:.5f} |")
    lines.append(f'''
Są to świadki niejednoznaczności, **nie globalne obwiednie** fazy/parametrów.
20Hz jest ekstrapolacją poniżej najniższych30Hz wykresu. Sama płaskość
modułu nie oznacza zerowej pochodnej zespolonej: gdy Lgen=M*exp(jphi),
`|dLgen/dx|²=(dM/dx)²+(M*dphi/dx)²`. Osobna dodatnia konstrukcjaR–L
ma stały moduł przy100Hz i niezerowy człon fazy; nie przypisano jej Purifi.

## Impedancja i energia nie wystarczają do identyfikacji siły

Wzór18 przy zablokowanej pozycji zawiera `i*(G*i)`, nie `(G*i)²`.
W naszym216przypadkowym doświadczeniu izolowano sam składnik jednej gałęzi
pamięci. Obie wersje mają wtedy ten sam DC, a iloraz amplitud H2 wynosi
dokładnie `sqrt(1+(omega*tau)²)`.
Przy omega*tau=1 to+3,0103dB oraz45°różnicy fazy. Odtworzono też
bezwymiarowy skok0,5→1A. Nie odtworzono pomiarów4″DUT i MagNet źródła.
Prądy sinusoidy mają amplitudy1/4/12A_peak. Skok jest idealizacją narzuconego
prądu, nie odtworzeniem osiągalnego impulsu napięciowego wzmacniacza.

Własne rozszerzenie z ruchem ma stany pamięci j:

```text
Lj=Lj0*a(x)²; jdot=(a*i-j)/tau
lambda_total=lambda0+sum(Lj0*a*j)
Frel=Frel0+sum(Lj0*a_x*i*j)
Efield=Efield0+sum(Lj0*j²/2)
Deddy=sum[Lj0/tau*(a*i-j)²]
```

Napięcie wynika z pochodnej całego lambda_total. Realizacja ma dodatnią
energię i dodatnie straty, a przy zablokowanej pozycji spełnia źródłowe
równanie18. Sprawdzono ją też niezależną macierzą sprzężonych induktorów.
Tau jest stałe po x; nie jest to uniwersalna identyfikacja dowolnej
zmiennej geometrii i nieliniowego materiału. W tej kampanii materiał
magnetyczny jest liniowy w prądzie; nie symulowano histerezy magnetycznej.

## Pełny ruch: ten sam napęd, różne mechanizmy

FLUX_ONE/NAIVE_ONE mają ten sam Zblocked dla zamrożonej pozycji.
FLUX_ONE/FLUX_TWO mają ten sam **pełny zespolony Zblocked@1kHz** w x=0,
co sprawdzono dla24baz z błędem względnym {packet['matched_complex_reference_max_relative_error']:.3g}.
Zmiana modelu wewnętrznego pozostaje widoczna w ruchu i harmonicznych.

Przykład C02/100l/20Hz/0,75obwiedni, wspólne napięcie
{float(example[0]['voltage_rms_v']):.3f}Vrms. To zadane hipotetyczne kształty, nie pomiar C02:

| Model | H2 ekwiwalentnego ciśnienia [%] | H3 [%] | Strata pamięci [W] | Strata efektywnego Rms [W] |
|---|---:|---:|---:|---:|''')
    for r in example:lines.append(f"| {r['profile']} | {float(r['h2_pressure_pct']):.5f} | {float(r['h3_pressure_pct']):.5f} | {float(r['mean_eddy_loss_w']):.5f} | {float(r['mean_structural_loss_w']):.5f} |")
    lines.append(f'''
W432parach FLUX/NAIVE największa różnica H2 wynosi
**{packet['max_H2_pair_difference_pp']:.4f}punktu procentowego**. Największa różnica H1
wynosi **{packet['max_absolute_fundamental_pair_difference_db']:.5f}dB**; są to osobno wybrane
maksima po zadanej siatce. Obie realizacje są pasywne. NAIVE pozostaje
kontrolą nieprawidłowego przypisania siły do pomocniczego prądu, nie finalistą.

W ogólnej siatce nieznanych strat/biegunów zmiana SPL przy1V wynosi
od{min_delta:+.3f}do{max_delta:+.3f}dB względem prostegoLe. To umowne rodziny, nie
tolerancja tych produktów. Ich tłumienie elektryczne wFs też się zmienia:
nie udajemy pełnego dopasowaniaT/S przez zachowanie jednego skalaru.

Deddy nie należy dodawać do I²Re jako ciepła samej cewki. Pomocnicze
gałęzie nie identyfikują miejsca emisji ciepła w silniku. P15/P16 nadal
wymagają danych lub jawnych scenariuszy podziału strat.
Pole mean_structural_loss_w oznacza Rms_effective*v², nie niezależny
pomiar strat strukturalnych. W liniowych sinusach przy jednocześnie
aktywnym X dla obu porównywanych sieci pamięć nie zwiększa pułapu
od Sd·X; zmienia potrzebne napięcie i prąd, nie geometryczne wyparcie.
W{packet['comparable_linear_motion_limited_rows']}takich liniowych porównaniach zmiana pułapu wyniosła najwyżej
{packet['max_linear_motion_limit_change_db']:.3g}dB. Nie przenosić tej tożsamości pojedynczego sinusa
na dowolne przebiegi nieliniowe i wielotonowe.

## Kontrole, granice i ograniczenia

Pierwszy przebieg:1711okresowych punktów i17flag domknięcia cyklu.
Wszystkie flagi oraz3wybrane świadki przeliczonoRadau3e-11/3e-13,
1024próbkami/cykl, do256cykli. Wystarczyło maksymalnie
{max(r['end_cycles'] for r in packet['refined_cases'])}cykli; końcowa tabela ma1728punktów spełniających zadane
kryterium. Nie jest to dowód jedynej orbity, stabilnościFloqueta ani
braku wszystkich innych gałęzi. Stany mają jawne odniesienia; pamięć j
ma jednostkę odniesienia1A, nie zmierzony prąd w metalu.

| Kontrola | Największy błąd / wynik |
|---|---:|
| Energia gradientem,8punktów i obie realizacje | {checks['max_energy_gradient_relative_error']:.3g} względnie |
|160porównań macierz stanu vs niezależny obwód częstotliwościowy | {checks['max_state_vs_frequency_relative_error']:.3g} względnie |
| Redukcja N=0 do wcześniejszego modelu | {checks['no_memory_reduction_relative_error']:.3g} względnie |
| Bilans pełnej serii po kontroli | {packet['max_relative_energy_residual']:.3g} względnie |
| Replikacja zespolonego H2 wzoru18 | {bench['max_relative_H2_complex_error']:.3g} względnie |
| Odrębne ODE filtra vs rozwiązanie okresowe | {bench['max_absolute_ODE_filter_error']:.3g} bezwzględnie |
| Bezstratna granica z niezerową zamrożoną pamięcią | {checks['nonzero_frozen_memory_lossless_energy_drift']:.3g} dryfu energii |

Sprawdzono N=0, Linstant=0 (redukcja algebraiczna), tau→0, tau→∞,
f=0 i formalnie f→∞. Przy skończonymtau limitf→0 dajeLinstant+sumLj;
przy tau→∞ wziętym najpierw i zerowej pamięci zostajeLinstant. Niezerowy
stan zamrożony zachowuje energię/siłę i nie może zostać automatycznie usunięty.
Nie modelowano ponownie przecieku, frontowej reakcji ani termiki cewki.
Końcowy wybór jednego głośnika/skrzyni i końcowyPDF wymagają reszty programu.

**Następny domyślny krok: P14 — IMD i sygnały wielotonowe**, następnie
operator promieniowania harmonicznych, dalsza analiza amplitud/gałęzi,
termika i mechanika/klej. UżywaćFLUX, zachowując niepewność pamięci i
nie utożsamiać wyników umownych rodzin z THD konkretnego produktu.

## Artefakty

![Odczyty i faza](../wyniki/25_Lgen_modul_i_nieznana_faza.png)
![Siła i pamięć](../wyniki/26_pamiec_i_sila_wzor18.png)
![Ruch i harmoniczne](../wyniki/27_pamiec_napedu_i_harmoniczne.png)
![Definicja Le i napęd](../wyniki/28_niepewnosc_definicji_Le_i_napedu.png)

Kod:[model](../skrypty/model_cewki_z_pamiecia.py),
[kontrole](../skrypty/sprawdz_pamiec_cewki.py),
[kampania](../skrypty/analiza_cewki_z_pamiecia.py),
[replikacja siły](../skrypty/replikacja_sily_L2R2.py),
[dokładne wykluczenie/dopasowania](../skrypty/analiza_ident_Le_i_dopasowania.py),
[audyt wykluczenia](../skrypty/audyt_wykluczenia_1_bieguna.py),
[rozstrzygnięcia Radau](../skrypty/sprawdz_pakiet_pamieci.py).
Wejścia:[konfiguracja](../dane/konfiguracje/p12c_pamiec_cewki.json),
[kalibracja digitalizacji](../dane/konfiguracje/p12c_digitalizacja_Lgen.json),
[pochodzenie źródeł](../dane/zrodla/P12C_definicja_Lgen_i_sila.json).
Wyniki:[kalibracje](../wyniki/p12c_kalibracje_i_odrzucenia.csv),
[linia napędu](../wyniki/p12c_liniowy_naped.csv),
[pełny ruch po kontroli](../wyniki/p12c_nieliniowa_pamiec_zweryfikowana.csv),
[dowód i świadkowie](../wyniki/p12c_ident_Le.json),
[dane odczytu](../dane/zrodla/digitalizacja/Purifi_NAB01_Lgen_fig4.csv).

Dziennik ma hash wejść/kodu i kopię startową. Wznowienie zgodnych
przypadków nie jest świeżą niezależną replikacją. Digitalizacja jest
oddzielnym etapem pozyskania źródła, wymagającym oryginalnegoPDF oSHA
i PyMuPDF1.28.0; zwykłe obliczenia używają zapisanych30odczytów.
Docelowy pokój nadal opisujeU-020/raport019: RTV po lewej, kanapa po prawej
oryginalnego rzutu; dokładnych pozycji nie zastąpiono pomiarem z pikseli.
''')
    target=ROOT/'raporty/021_pamiec_cewki_i_definicja_Lgen.md'
    target.write_text('\n'.join(lines));print('Zapisano',target.relative_to(ROOT))


if __name__=='__main__':main()
