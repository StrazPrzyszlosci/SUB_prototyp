"""Raport i wykresy P12/P13 z rzeczywiście wykonanych rodzin warunkowych."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def read_json(name):return json.loads((ROOT/'wyniki'/name).read_text())


def read_rows(name):
    with (ROOT/'wyniki'/name).open() as handle:return list(csv.DictReader(handle))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(ROOT/'wyniki'/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    result=read_json('p12_p13_podsumowanie.json');checks=read_json('p12_p13_weryfikacja.json')
    table_checks=read_json('p12_p13_kontrola_pakietu.json');comp=read_json('p13_kompensacja_gazu.json')
    comp_checks=read_json('p13_kompensacja_weryfikacja.json')
    rows=read_rows('p12_p13_naped_i_gaz.csv');comp_rows=read_rows('p13_kompensacja_gazu.csv')
    cfg=json.loads((ROOT/'dane/konfiguracje/p12_p13_naped_i_gaz.json').read_text())
    sample=[next(r for r in rows if r['candidate_id']=='C02' and float(r['volume_l'])==100
                 and float(r['f_hz'])==20 and float(r['reference_envelope_fraction'])==.75
                 and r['profile']==p['id']) for p in cfg['profiles']]
    labels=['Liniowy','Gaz','BL(x)','Kms(x)','Indukcyjność','R(v) stres','Pełny sym.','Pełny +','Pełny −']
    fig,ax=plt.subplots(1,2,figsize=(12,6));y=np.arange(len(sample))
    ax[0].barh(y-.16,[float(r['h2_pressure_pct']) for r in sample],height=.3,label='H2')
    ax[0].barh(y+.16,[float(r['h3_pressure_pct']) for r in sample],height=.3,label='H3')
    ax[0].set(yticks=y,yticklabels=labels,xlabel='Harmoniczna ciśnienia ekwiwalentnego [%]',title='C02, 100 l, 20 Hz; hipotetyczne kształty')
    ax[0].legend()
    ax[1].barh(y,[float(r['fundamental_compression_relative_to_linear_db']) for r in sample])
    ax[1].set(yticks=y,yticklabels=labels,xlabel='Zmiana H1 przy tym samym V [dB]',title='Ten sam napęd, różne mechanizmy')
    for a in ax:a.invert_yaxis();a.grid(axis='x',alpha=.25)
    save(fig,'22_nieliniowy_naped_i_gaz')
    fig,ax=plt.subplots(1,2,figsize=(12,5))
    for mult,label in [(-1,'Asymetria przeciwna'),(0,'Bez asymetrii'),(1,'Skasowany człon x²')]:
        selected=[r for r in comp_rows if r['candidate_id']=='C02' and float(r['volume_l'])==30
                  and float(r['f_hz'])==20 and float(r['cancellation_multiplier'])==mult]
        for a,field in zip(ax,['h2_pressure_pct','h3_pressure_pct']):
            a.semilogy([float(r['target_linear_x_fraction']) for r in selected],
                       [float(r[field]) for r in selected],'o-',label=label)
    ax[0].set(xlabel='Żądana frakcja Xref przed limitem V/I',ylabel='H2 ciśnienia ekwiwalentnego [%]',title='C02/30 l/20 Hz; napęd ≤40V/12A')
    ax[1].set(xlabel='Żądana frakcja Xref przed limitem V/I',ylabel='H3 ciśnienia ekwiwalentnego [%]',title='Kompensacja H2 nie usuwa H3')
    for a in ax:a.grid(alpha=.25);a.legend(fontsize=8)
    save(fig,'23_kompensacja_nieliniowosci_gazu')
    fig,ax=plt.subplots(1,2,figsize=(12,5))
    for cid in ['C02','C06','C11']:
        selected=[r for r in rows if r['candidate_id']==cid and float(r['volume_l'])==100
                  and float(r['reference_envelope_fraction'])==.75 and r['profile']=='GAS_ONLY']
        ax[0].plot([float(r['f_hz']) for r in selected],[float(r['h2_pressure_pct']) for r in selected],'o-',label=cid)
    for volume in [30,100,150]:
        for profile,style in [('FULL_ASYM_PLUS','-'),('FULL_ASYM_MINUS','--')]:
            selected=[r for r in rows if r['candidate_id']=='C02' and float(r['volume_l'])==volume
                      and float(r['reference_envelope_fraction'])==.75 and r['profile']==profile]
            sign='+' if profile.endswith('PLUS') else '−'
            ax[1].plot([float(r['f_hz']) for r in selected],[1000*float(r['x_dc_m']) for r in selected],style,label=f'{volume} l, {sign}')
    ax[0].set(xlabel='Hz',ylabel='H2 ciśnienia ekwiwalentnego [%]',title='Sprzężony ruch i gaz5ms, 100 l')
    ax[1].set(xlabel='Hz',ylabel='Offset x_DC [mm]',title='C02; kształty hipotetyczne, nie pomiar')
    for a in ax:a.grid(alpha=.25);a.legend(fontsize=7)
    save(fig,'24_harmoniczne_gazu_i_bias_napedu')
    resolution=table_checks['unsettled_resolutions'][0]
    numerical=next(r for r in table_checks['refinements'] if 'linear_numerical_harmonic_floor' in r['metrics'])
    example_comp=[r for r in comp_rows if r['candidate_id']=='C02' and float(r['volume_l'])==30
                  and float(r['f_hz'])==20 and float(r['target_linear_x_fraction'])==.6]
    lines=[f'''# Raport 020 — nieliniowy napęd i sprzężony gaz

Stan: 2026-10-24. **Obliczenia i symulacje P12/P13 przed budową.**
Wykonano {result['rows']:,} przypadków (spacje/komórki poniżej podają dokładny zakres).
Katalogowe bazy24modeli połączono z9jawnymi rodzinami mechanizmów.
Kształty BL/Kms/Le/R(v) są założeniami, **nie pomiarami tych24produktów**.
Nie jest to ranking rzeczywistego THD, raport końcowy ani finalny wybór.
Bramki jakości źródeł puli pozostają aktualne, w tym konflikt4/8Ω C07
i niepotwierdzony aktualny status katalogowy C11.

## Wynik wpływający na projekt

1. Nieliniowości wymagają wspólnego rozwiązania ruchu, prądu i gazu.
   Nie wystarczy dodać procentów harmonicznych niezależnych mechanizmów.
   Wykazano warunkową kompensację H2, z zachowaniem H3 i zależności od Vb.
2. Sygnał sinusoidalny dobrany z liniowej obwiedni V/I/X nie chroni rozruchu:
   **4scenariusze opuściły dziedzinę |x|≤1,25Xref przed pierwszym cyklem**.
   Odrębny solver potwierdził te przekroczenia. Nie są prognozą uszkodzenia
   rzeczywistego C05/C17; dotyczą hipotetycznych krzywych i startu od zera.
3. Katalogowe X nie jest wspólną granicą małego THD. Nieznane kształty
   istotnie zmieniają harmoniczne i DC przy tym samym napędzie.
4. Dane Le@1kHz nie identyfikują cewki w basie. Nowa karta Purifi pokazuje
   wyraźnie różne krzywe indukcyjności L_gen(x,f), nie utożsamione tu z Ld;
   potrzebny jest kolejny model z pamięcią
   prądów wirowych, zanim użyjemy źródłowych krzywych jako realizacji produktu.

## Dziedzina doświadczenia

| Wejście | Zakres / warunek |
|---|---|
| Bazy T/S |24modele,11producentów; C12 i C18 to kontrole10″ |
| Vb netto |30/60/100/150 l |
| Sinusy |20/25/31,5/40/63/80/100 Hz; każdy osobno |
| Napięcie |0,25/0,75 liniowej obwiedni min(40Vrms,12Arms/I1,Xref/X1) |
| Rodziny |Liniowa, gaz, BL, Kms, indukcyjność, stres R(v), pełna symetryczna i dwie asymetryczne |
| Gaz |Szczelny, idealny, tau=5ms; Re/T cewki zamrożone |
| Początek |Wszystkie stany zerowe, sinus od fazy0; brak łagodnego rozruchu |
| Czas |16cykli startowo, wydłużanie do64; osobne badanie nierozstrzygniętego punktu do128 |
| Próbowanie widma |4pełne ostatnie cykle,256próbek/cykl; kontrole do1024 |
| Solver serii |LSODA, rtol2e-8, atol2e-10; czas znormalizowany przez fazę |
| Sprzężenie frontu |Mms/Rms efektywne, bez nowego operatora promieniowania |
| Pole diagnostyczne |Monopol4π/1m/RMS; H2–H10 z przyspieszenia, bez twierdzenia o realnej kierunkowości |

9×24×4×7×2=**12 096**. Zatrzymanie dziedziny i brak wygaszenia nie są
usuwane z liczby przypadków. Wyższe harmoniczne sięgają1kHz; nie zakładamy
automatycznie kompaktowości fizycznej membrany w całym tym zakresie.
Szczyty ruchu/prądu w tabeli są szczytami z siatki. Nie są certyfikatem
ciągłego maksimum ani wynikiem mechanicznego zderzenia z ogranicznikiem.

Stała tau w różnych Vb oznacza różne H=m*cv/tau. Podawane temperatury
dotyczą gazu, nie cewki. Nie przyjęto wspólnej termicznej mocy katalogowej.

## Równania i kontrola energii

Źródło definiuje Kms(x) jako **sztywność sieczną Fs/x**. Jej styczna
wynosi dFs/dx, a energia to całka Fs dx. Wprowadzenie tej samej krzywej
jako pochodnej Fs dałoby inny model. Współczynniki w kodzie są w SI.

```text
Fs = x/Cms*(1+k1*q+k2*q²+k4*q⁴), q=x/Xref
BL = BL0*exp(b1*q-b2*q²-b4*q⁴)
lambda = Lsigma*i+Lp(x)*Is*tanh(i/Is)
Wco = integral_0^i lambda(x,j)dj
Frel = partial(Wco)/partial(x)
Ld = partial(lambda)/partial(i)>0
V = Re*i+Ld*di/dt+[BL+partial(lambda)/partial(x)]*v
M*dv/dt = BL*i+Frel-Fs-R(v)*v+Sd*(p-p0)
```

Dodatnie Lsigma i odpowiednie ograniczenia wielomianu zapewniają
dodatnią indukcyjność różniczkową oraz dodatnią styczną zawieszenia
w zadanej rodzinie. Nie są katalogowymi tolerancjami żadnego modelu.
Granica Is→∞ daje liniowy strumień w prądzie. Le=0 ma dokładną redukcję
algebraiczną prądu. Nie pomylono Le siecznego z różniczkowym Ld.

```text
Vgas=V0+Sd*x
p=p0*(T/T0)/(Vgas/V0)
Tdot=-(gamma-1)*T*Sd*v/Vgas-(T-T0)/tau
E=0.5*M*v²+Us+i*lambda-Wco+Agas
Edot=V*i-Re*i²-R(v)*v²-Dheat
```

Agas jest dostępnością gazu względem p0/T0, a Dheat≥0. Cztery tożsamości
sprawdzono symbolicznie; niezależny gradient energii w12punktach daje
maksymalny względny defekt {checks['max_relative_energy_gradient_error']:.3g}.
W bezstratnym teście dryf energii wynosi {checks['lossless_max_relative_energy_drift']:.3g}.
Celowe pominięcie Frel zwiększa go do {checks['omitted_reluctance_max_relative_energy_drift']:.3g}.
To wykrycie błędnej implementacji mechanizmu, nie pomiar strat materiału.

## Przykład wspólnego napędu

C02/RSS390HF-4,100l,20Hz,0,75liniowej obwiedni. Każdy wiersz ma to samo
napięcie **{float(sample[0]['voltage_rms_v']):.3f}Vrms**. H2/H3 są procentami
ekwiwalentnego ciśnienia monopola, a nie pomiarem głośnika. Kształty z
konfiguracji pozostają umowne; nie przypisujemy tym wartościom popularności
ani prawdopodobieństwa dla C02.

| Rodzina | H2 [%] | H3 [%] | Zmiana H1 [dB] | x_DC [mm] |
|---|---:|---:|---:|---:|''']
    for label,row in zip(labels,sample):
        lines.append(f"| {label} | {float(row['h2_pressure_pct']):.5g} | {float(row['h3_pressure_pct']):.5g} | {float(row['fundamental_compression_relative_to_linear_db']):+.4f} | {1000*float(row['x_dc_m']):+.5f} |")
    lines.append(f'''
Współczynniki R(v) w osobnym stresie nie dowodzą, że straty prędkościowe
dominują w silnym wooferze. Instrukcja producenta podkreśla ich odmienną
rolę w mikrogłośnikach. Nie przeniesiono tamtej krzywej na naszych kandydatów.

## Kompensacja gazu i zawieszenia —72odrębne pełne ODE

Dla adiabatycznej siły gazu współczynnik x² jest dodatni. Asymetria
zawieszenia o wartości

```text
k1_cancel=gamma*(gamma+1)/2*p0*Sd³*Cms*Xref/V0²
```

kasuje **człon kwadratowy rozwinięcia przy x=0**. Sprawdzono C02/C06,
30/100l,20/40Hz,3poziomy i znaki −/0/+ tego k1. BL/Le liniowe, gaz
adiabatyczny z ustaloną entropią początkową. Każda trójka ma stałe napięcie
i ten sam dodatni k2. To rodziny hipotetyczne, nie pomiary asymetrii tych modeli.

Przykład C02/30l/20Hz, żądane0,6Xref przed limitemV/I, faktyczne napięcie
**{float(example_comp[0]['voltage_rms_v']):.3f}Vrms**:

| Mnożnik k1_cancel | k1 | H2 ciśnienia [%] | H3 ciśnienia [%] |
|---:|---:|---:|---:|''')
    for row in example_comp:
        lines.append(f"| {float(row['cancellation_multiplier']):+.0f} | {float(row['k_asym']):+.6f} | {float(row['h2_pressure_pct']):.7g} | {float(row['h3_pressure_pct']):.7g} |")
    lines.append(f'''
H2 może się silnie zmniejszyć, podczas gdy H3 pozostaje. Nie oznacza to
zerowego THD ani rekomendacji wyboru asymetrycznego zawieszenia.
W pokazanym wykresie żądane poziomy0,6/0,9są ograniczone tym samym V/I;
płaski odcinek nie jest dowodem nasycenia akustycznego.
Warunek skaluje się z1/Vb² i zależy od założenia gazu; przy skończonej
wymianie ciepła pojawia się pamięć i faza. Celem prototypu jest zbadanie
takich interakcji, nie strojenie do jednej hipotetycznej kompensacji.
Odrębny DOP853 potwierdził H2 przykładu do różnicy
{comp_checks['checks'][1]['absolute_h2_percentage_point_difference']:.3g}punktu procentowego.
Sprawdzono też najsłabszy znaleziony ślad H2; różnica dwóch solverów nie
jest certyfikowanym przedziałem błędu ani walidacją fizyczną.

## Przypadki graniczne i rzeczywista precyzja serii

- Pierwszy przebieg: **12 091**przypadków spełniało zadane próbkowane
  kryterium cyklu; **4**zatrzymały się na granicy i **1**pozostał nierozstrzygnięty.
- Cztery przekroczenia dotyczą C05/C17,150l,63/40Hz,rodzinBL_ONLY i
  FULL_ASYM_MINUS. Granica została osiągnięta około0,50–0,52cyklu rozruchu.
  DOP853 potwierdził czasy względemLSODA do maksymalnie
  {max(r['absolute_stop_cycle_difference'] for r in table_checks['domain_crossings']):.3g}cyklu.
- Nierozstrzygnięty C17/150l/80Hz/BL_ONLY po64cyklach miał błąd
  {resolution['original_closure_error']:.3g}. Radau po **{resolution['end_cycles']}cyklach**
  uzyskał {resolution['closure_error']:.3g}, spełniając ostrzejszy próg1e-8.
  Nie ma z tego dowodu trwałej niestabilności, ani dowodu braku innych gałęzi.
- Największy względny bilans energii pierwszej serii:
  {result['max_valid_relative_energy_residual']:.3g}; wybrane świadki sprawdzono
  odrębnym solverem, mniejszymi tolerancjami i1024próbkami/cykl.
- W liniowym modelu serii pozorne THD sięgało
  **{numerical['coarse_thd_pct']:.6f}%**. Ten sam znaleziony świadek po dokładniejszym
  obliczeniu daje **{numerical['refined_thd_pct']:.6g}%**. To liczbowy poziom
  resztkowy, nie fizyczne THD. Nie interpretować harmonicznych poniżej
  rozdzielczości danego przebiegu jako efektu konstrukcji.
- NiezależneLSODA/Radau/DOP853 w kontrolnym przypadku zgadzają się
  w amplitudzie podstawowej do około1e-10względnie. Nie jest to globalny
  certyfikat błędu wszystkich12096punktów.
- Przypadki okresowe nie przekroczyły odniesionego X/prądu na siatce
  ostatnich4cykli. Nie zapisano pełnych szczytów rozruchu pozostałych
  przypadków: brak zatrzymania na1,25Xref nie dowodzi, że nie przekroczono
  1,0Xref. Cztery wyjścia z dziedziny są odrębnym wynikiem. Nie jest to
  dowód bezpieczeństwa dla dowolnego sygnału; limitery pozostająP24.

Zbadano dokładne redukcje Le=0,Vb→∞,tau=0/∞,dodatniość parametrów oraz
brak strat. Nie symulowano zderzeń, tarcia cewki, wilgotności, starzenia,
rozwarstwienia kleju, prądów wirowych/histerezy magnetycznej ani wszystkich
możliwych nieliniowości. Te wyniki nie zamykają programu30pakietów.

## Dane rzeczywiste i otwarte bramki identyfikacji

SRC31: oryginalne równania i rysunki KLIPPEL potwierdzają strukturę modelu,
ale nie określają naszych współczynników. SRC32 zawiera przykładowe krzywe
instrukcji; nie są to krzywe C01–C24. Automatycznych tabel wykresów nie użyto.

**Nowy test C18/Purifi NAB-01**, dokładna wersja, PatrickTurnmire/Redrock:
drukowane XBl82%=11,9mm i XC75%=10,2mm używają kryterium10%źródła;
przy kryterium20% oba wynoszą co najmniej13,4mm. Nie są wspólnym progiem
z katalogowym Xlin14,75mm ani z wcześniejszym Scan32/70%BL/50%Cms.
Nie wyprowadzono z tego20HzTHD gotowego sealed. C18 pozostaje kontrolą10″.

Oryginalny wykres Kms testu ma w x≈0 orientacyjnie1,4–1,7N/mm, podczas
gdy odwrotność katalogowego Cms0,44mm/N wynosi2,273N/mm. To ostrzeżenie
o identyfikacji/warunkach/historii, nie rozpoznanie błędu producenta.
Nie połączono bez uzgodnienia absolutnej krzywej z inną baząT/S.
Karta producenta0.95/June2024 ma moceTBD; nowsza strona ma osobne
deklaracje mocy. Historyczny test nie unieważnia automatycznie nowszej strony.

**Kolejny domyślny eksperyment: P12C — pasywna pamięć indukcyjności**
oraz niezależne odczyty źródłowych krzywych z niepewnością i warunkami.
Rozdzielić pozorne Le(x,f) od lambda(x,i), Kms od stycznej i zgodność
zestawów pomiarowych. PotemP14:IMD, większa analiza amplitudy/gałęzi
i rzeczywisty operator promieniowania harmonicznych; dalej termika,
mechanika/klej i ochrona. Ostateczna rekomendacja jednego głośnika i jednej
konstrukcji oraz końcowyPDF pozostają otwarte.

## Wykresy, wejścia i odtwarzanie

![Mechanizmy napędu](../wyniki/22_nieliniowy_naped_i_gaz.png)
![Kompensacja gazu](../wyniki/23_kompensacja_nieliniowosci_gazu.png)
![Gaz i bias](../wyniki/24_harmoniczne_gazu_i_bias_napedu.png)

Wejścia:[konfiguracja](../dane/konfiguracje/p12_p13_naped_i_gaz.json),
[stan źródeł24modeli](../dane/przetworniki/dostepnosc_nieliniowych_P12.json),
[SRC31–34](../dane/zrodla/P12_P13_nieliniowosci_i_luki.json).
Kod:[model](../skrypty/model_nieliniowy.py),
[kontrole](../skrypty/sprawdz_naped_nieliniowy.py),
[kampania](../skrypty/analiza_napedu_nieliniowego.py),
[kompensacja](../skrypty/analiza_kompensacji_gazu.py),
[kontrola tabel i wyjątków](../skrypty/sprawdz_pakiet_nieliniowy.py),
[baza wiedzy14](../baza_wiedzy/14_nieliniowy_naped_i_gaz.md).
Wyniki:[główna tabela](../wyniki/p12_p13_naped_i_gaz.csv),
[podsumowanie](../wyniki/p12_p13_podsumowanie.json),
[kontrola](../wyniki/p12_p13_kontrola_pakietu.json),
[72przypadki kompensacji](../wyniki/p13_kompensacja_gazu.csv),
[odrębna kontrola kompensacji](../wyniki/p13_kompensacja_weryfikacja.json).

Dziennik ma hash wejść, kopia kodu/wejść jest w archiwum startu.
Domyślny przebieg wznawia zgodne przypadki z dziennika; ponowne użycie
dziennika nie jest niezależną replikacją ODE. Aby wymusić nowy rachunek,
najpierw zachować dotychczasowy dziennik w osobnym archiwum, następnie
uruchomić kampanię bez niego. Nowy rachunek nie był potrzebny dla całej
siatki po kontroli; niezależne przeliczenia wykonano dla jawnych świadków.

Aktualny docelowy pokój: [U-020/raport019](019_zamiana_kanapy_i_RTV.md),
RTV po lewej i kanapa po prawej oryginalnego rzutu. Obecne równania napędu
nie zależą od orientacji pokoju; nie użyto dawnych S0 jako nowych pomiarów.
''')
    target=ROOT/'raporty/020_nieliniowy_naped_i_sprzezony_gaz.md'
    target.write_text('\n'.join(lines).replace('12,096','12 096'))
    print('Zapisano',target.relative_to(ROOT))


if __name__=='__main__':main()
