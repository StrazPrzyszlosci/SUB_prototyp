"""Raport cząstkowy P09/P10 z wykonanych badań, bez końcowego PDF."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load_rows(name):
    return list(csv.DictReader((ROOT/'wyniki'/name).open()))


def main():
    result=json.loads((ROOT/'wyniki/p09_p10_podsumowanie.json').read_text())
    checks=json.loads((ROOT/'wyniki/p09_p10_weryfikacja.json').read_text())
    fits=json.loads((ROOT/'wyniki/p09_dopasowania_widm.json').read_text())
    thermal=load_rows('p09_relaksacja_i_naped.csv')
    alignment=load_rows('p09_projekcja_F3.csv')
    slow=load_rows('p10_wyrownanie_DC.csv')
    nonlinear=load_rows('p10_gaz_bezwymiarowy.csv')
    def count(n):return f'{n:,}'.replace(',',' ')
    lines=[f'''# Raport 016 — gaz, wypełnienie i granice szczelności

Stan: 2026-10-24. Badania P09/P10 przed budową, **24 modele przetworników**.
To raport cząstkowy; pojedynczy wybór głośnika i konstrukcji oraz końcowy
PDF wymagają pozostałych pakietów programu. Dwa modele 10-calowe są kontrolami.

## Wynik wpływający na projekt

Wypełnienie nie ma jednego stałego „bonusu objętości”. Zmienia zespoloną
podatność, straty i niekiedy masę akustyczną. Zmiana sztywności gazu może
pomóc przy tym samym napięciu, a zarazem pogorszyć modelowe F3 przez tłumienie.
Nie zwiększa samego limitu Sd·X, gdy napęd już osiąga przyjęty limit ruchu.

Dla RSS390HF-4, 100 l, szczelnej komory i 20 Hz:

- koniec izotermiczny daje około **+1,06 dB przy tym samym V**;
- relaksacja 5 ms daje około **+0,13 dB**, mimo części rzeczywistej podatności
  odpowiadającej około 122,6 l;
- projekcja F3 bez Le wynosi około **32,30 Hz adiabatycznie**, **32,19 Hz
  izotermicznie**, lecz **34,57 Hz dla 5 ms**;
- przy budżecie 40 Vrms/12 Arms i pełnym katalogowym X wszystkie trzy
  warianty dochodzą do tego samego modelowego limitu ruchu około 101,89 dB
  w normalizacji 2π/1 m/RMS. Mniejsza sztywność nie tworzy dodatkowego Sd·X.

To porównanie modeli, bez deklaracji rzeczywistego THD i room gain.
Nie przypisano podanych czasów relaksacji konkretnej włókninie.

## Wykonany zakres

| Obszar | Wykonane przypadki / wiersze |
|---|---:|
| Termika, napęd, Vb=30/60/100/150 l; 7 profili, 3 przecieki i 6 częstotliwości | {count(result['thermal_band_rows'])} |
| Projekcja F3 dla Le=0 względem asymptoty modelu | {count(result['projected_f3_cases'])} |
| Warstwy ZK, szkielet nieruchomy/wiotki, dwa Cp i umowna sorpcja | {count(result['material_rows'])} |
| Bezwymiarowe przebiegi nieliniowego gazu i granice cieplne | {count(result['nonlinear_dimensionless_cases'])} |
| Odwzorowanie gazu na 24 modele, amplitudy i temperatury | {count(result['nonlinear_driver_rows'])} |
| Hermetyczne offsety cieplne i barometryczne | {count(result['static_offset_rows'])} |
| Wyrównanie DC z kontrolą biegunu pełnego stanu | {count(result['dc_relaxation_rows'])} |
| Nieliniowe bilanse cyklu pracy/ciepła/dostępności | {count(result['energy_cycle_cases'])} |

Częstotliwości porównawcze: 20/25/31,5/40/63/80 Hz. Dodatkowe gęste siatki
służą badaniu relaksacji i zbieżności. Limity dotyczą osobnych sinusów.
0,7/1,0 katalogowego X nie jest wspólnym progiem THD różnych producentów.

## Równania i zgodność fizyczna

Ośrodek wynika z p0=101325 Pa, T0=293,15 K, gamma=1,4 i R=287,05 J/(kg K):
rho={result['medium']['rho_kg_m3']:.6f} kg/m³, c={result['medium']['c_m_s']:.3f} m/s.
Mms/Cms/BL/Rms przetworników zachowano z pierwotnej identyfikacji T/S.
Nie przeliczano mechaniki po zmianie temperatury gazu. Regresję do dawnego
ośrodka rho=1,2041/c=343 wykonano osobno; drobne różnice ostatnich cyfr
nie są poprawą osiągów.

Z bilansów gazu otrzymano dodatni model relaksacyjny:

```text
K(s)=p0*(1+gamma*s*tau)/(1+s*tau)
Fbox=K0*y+sum[Dk_j*(y-q_j)]
y_dot=v-G*Fbox/Sd²
q_j_dot=(y-q_j)/tau_j
```

Energia elektryki, mechaniki i komory spełnia:

```text
dE/dt=V*i-Re*i²-Rms*v²-G*Fbox²/Sd²
      -sum[Dk_j*(y-q_j)²/tau_j]
```

Przeciek i wymiana ciepła mają oddzielne dodatnie straty. Zachowano stały Ra
przy zmianie Vb, definiując go przez częstotliwość odniesioną do 100 l.
Redukcje tau=0/∞, Ra=0/∞ i Le=0 usuwają zbędne stany. Nie dodano drugi raz
diagnostycznej mocy promieniowania do Rms. Dla przecieku metryka SPL zakłada
wspólną fazę drogi zewnętrznych źródeł; geometria rzeczywistego przecieku jest otwarta.

**F3 w tabeli jest projekcją Le=0**, z pierwszym przejściem w górę przez −3 dB
względem asymptoty matematycznego modelu. Wiele biegunów relaksacji nie daje
jednego bezwarunkowego Fc/Qtc. Nie zastosowano do nich wzoru obudowy 2. rzędu.
Model warstwowy ma własne rezonanse i nie otrzymał fikcyjnego katalogowego F3.

## Podatność, strata i headroom

Przykład 100 l bez przecieku. Kolumny SPL są różnicą względem adiabatycznego
wariantu tego samego głośnika. Maksimum uwzględnia modelowe V/I/X, bez termiki cewki.

| Model / profil | Zmiana przy tym samym V, 20 Hz [dB] | Zmiana limitu40V/12A/1X [dB] |
|---|---:|---:|''']
    for cid in ['C02','C06','C11']:
        selected=[r for r in thermal if r['candidate_id']==cid and r['volume_l']=='100.0' and r['leak_ref_hz']=='0.0' and r['f_hz']=='20.0']
        base=next(r for r in selected if r['profile']=='ADIABATIC')
        for pid in ['ISOTHERMAL','T005']:
            row=next(r for r in selected if r['profile']==pid)
            lines.append(f"| {cid} / {pid} | {float(row['delta_to_adiabatic_same_Ra_db']):+.3f} | {float(row['V40_X1_spl_db'])-float(base['V40_X1_spl_db']):+.3f} |")
    lines.append('''
T005 oznacza 5 ms. C02 to RSS390HF-4, C06 — STX W.32.800.8.FCX,
C11 — RSS390HE-22. Przy tym samym napięciu różnica nie jest taka sama
jak przy tym samym ograniczeniu wychylenia. Dla C11 napięcie pozostaje
ograniczeniem w tym przykładzie, dlatego podatność może zwiększyć limit modelu.

## Materiał: geometria porów, mocowanie i pojemność cieplna

Model Zwikkera–Kostena obejmuje straty lepkościowe i cieplne w okrągłych
porach. Oryginalne obrazy równań 12/14/19/20/24/25/01 z
[dokumentacji COMSOL](https://doc.comsol.com/6.3/doc/com.comsol.help.aco/aco_ug_pressure.05.182.html)
obejrzano w przeglądarce. Promień poru nie jest średnicą włókna.
Porównano promienie 50/200/1000 µm, phi=0,98, szkielet nieruchomy i wiotki,
tylną warstwę 5/10/50 cm w komorze1D o głębokości50 cm.
Gęstość suchego szkieletu20 kg/m³ jest założeniem, nie kartą produktu.

Porowatość jest już w zespolonej gęstości i module. Tabela zachowuje także
ubytek prawdziwej objętości gazu przez materiał. Pełne wypełnienie phi=0,98
daje geometrycznie98 l gazu zamiast100 l; nie odejmowano tego drugi raz.
Porównanie prowadzi do pustej komory1D o tej samej geometrii. Model portu
uśrednionego nie potwierdza dopasowania kosza, przejściówki ani gabarytu w pokoju.

Dwa bilanse cieplne pokazują znaczenie skończonej pojemności materiału:

```text
Klow=p0*[1+(gamma-1)*Cg/(Cg+Cs)]
tau_eff=Cg*Cs/[Hgs*(Cg+Cs)]
```

Przy izolowanym od otoczenia materiale Cs=Cg dolny moduł wynosi1,2*p0,
a nie p0. Rezerwuar o nieskończonej pojemności cieplnej jest osobnym końcem
modelu. Nie wyprowadzamy Cs ani Hgs z samej masy upakowanej włókniny.

Odtworzenie cieplnej części ZK dodatnim widmem relaksacji daje dla poru200 µm:

| Liczba członów | Maks. względna różnica modułu względem ZK |
|---:|---:|''')
    for fit in fits:
        if fit['pore_radius_m']==.0002:
            lines.append(f"| {fit['terms_requested']} | {100*fit['max_relative_bulk_modulus_error']:.3f}% |")
    lines.append(f'''
Wagi są nieujemne, a granice izotermiczna i adiabatyczna są zachowane.
Jedna relaksacja nie odtwarza dokładnie rozproszonej dyfuzji. Siatki kilku
czasów nie są zagnieżdżone, więc błąd nie musi monotonicznie maleć przy
każdej zmianie liczby członów. To dopasowanie do modelu porów, nie do pomiaru włókniny.

Karta [ISOVER Aku-Płyta,2022](https://www.isover.pl/documents/karta-produktu-pds/kt-aku-plyta-aku-plat-202206.pdf)
podaje **AFr≥5 kPa*s/m²**. Ten parametr jest dolną granicą oporności właściwej,
nie oporem konkretnej warstwy ani pełną identyfikacją. W odczytanej dokumentacji
Delany–Bazley ma warunek0,01≤rho*f/sigma≤1. Przy podanej dolnej granicy sigma
górne ograniczenie tej liczby w20–40Hz wypada poniżej0,01. Nie użyto więc
niezweryfikowanej ekstrapolacji DB/Miki do tego zakresu.
Przewodność cieplna materiału lambda_D=0,037 W/(m K) nie została użyta
jako przewodność gazu. Do wyboru konkretnego wypełnienia nadal brakuje
porowatości, stanu szkieletu, mikrostruktury, Cp i przewodnictwa wymiany ciepła.

## Wyjątek: sorpcja nie jest samą izotermicznością

Oryginał [Venegas et al., Forum Acusticum2023](https://dael.euracoustics.org/confs/fa2023/data/articles/000280.pdf)
pobrano i obejrzano na stronach2–5, wraz ze wszystkimi rysunkami.
Równanie11 zawiera porowatość pozorną Phi, która może przekraczać1.
Przykład Phi=2,2563 i udziału0,25 służy tutaj tylko jako statyczny parametr
umownej rodziny. Widmo0,001/0,01/0,1s jest naszym założeniem.
Zespolona dodatkowa podatność została skonstruowana pasywnie i zbadana
w naszym modelu zamkniętym. Jej parametrów nie zidentyfikowano dla produktu.

Wykresy źródłowe dotyczą **modelu bass-reflex**, r=1m, e_g=sqrt(8)V,
Rg=0 i zadanych parametrów. Nie przyjęto niepodanej konwencji RMS/peak ani
nie przeniesiono ich SPL do naszego sealed. Transkrypcję tekstu Wright/KEF
także przeczytano, lecz PDF na pierwszym hoście zwracał403. Automatycznych
tablic punktów jego wykresów nie zaakceptowano. Nie jest to rekomendacja
użycia dowolnego węgla aktywnego ani gwarancja stałego bonusu objętości.

## Nieliniowy gaz: amplituda, temperatura i niezamienne granice

Rozwiązano gaz z zadanym `V/V0=1+epsilon*sin(omega*t)` i wymianą Newtona.
Nowe wyniki obejmują przebiegi pośrednie, odmienną temperaturę początkową
i stałe H, a nie tylko dotychczasowe adiabatyczne72przypadki.
H2/H1 i H3/H1 są harmonicznymi **ciśnienia wewnątrz i siły gazu przy
narzuconym ruchu**, nie rzeczywistym THD akustycznym głośnika.

Transformacja `Z=(T/T0)*(V/V0)^(gamma-1)` daje liniowy filtr dla wymuszenia
`(V/V0)^(gamma-1)`. Rozwiązanie okresoweFFT porównano z niezależnym strzelaniem
ODE/Radau. Sprawdzono też dodatnią dostępność gazu oraz bilans pracy i ciepła.

Istotny przypadek graniczny: H=0 z początkową entropią i granica H→0 po
osiągnięciu stanu okresowego dają inne DC i amplitudę siły. Dla epsilon=0,2:

| Koniec adiabatyczny | Średnie p−p0 [Pa] | Amplituda składowej podstawowej [Pa] | H2/H1 [%] |
|---|---:|---:|---:|''')
    for row in nonlinear:
        if row['epsilon']=='0.2' and row['omega_tau']=='inf':
            lines.append(f"| {row['adiabatic_mode']} | {float(row['pressure_dc_relative_pa']):.2f} | {float(row['fundamental_peak_pa']):.2f} | {float(row['h2_to_h1_pct']):.4f} |")
    lines.append(f'''
Ten duży epsilon jest testem modelowej granicy; nie jest zadeklarowanym
ruchem prototypu. Same zgodne procenty harmonicznych nie potwierdzają
zgodnego ciśnienia DC ani siły podstawowej.

## Hermetyczna masa a powolne wyrównywanie ciśnienia

Dla idealnie uwięzionej masy100l, C02 i powolnego ogrzania o5K przy
stałym ciśnieniu na zewnątrz model liniowego zawieszenia daje offset około
**12,34mm**. To **formalna granica hermetyczności**, nie prognoza dla
rzeczywistej skrzyni mającej mikroprzecieki. Dla części scenariuszy wynik
wykracza poza katalogowy ruch; oznaczono tam granicę modelu Cms, nie położenie
po uderzeniu w ogranicznik. Sprawdzono także zmianę zewnętrznego ciśnienia±1000Pa.

Czas wyrównania DC zależy od powietrza i od podatności membrany:

```text
tau_DC = Ra*(V/p0+Sd²*Cms)
```

Dla C02/100l i cieplnego profilu5ms:

| fleak przy100l [Hz] | Czas najwolniejszego bieguna [s] | Największa zmiana20–80Hz na sprawdzonej siatce [dB] |
|---:|---:|---:|''')
    for row in slow:
        if row['candidate_id']=='C02' and row['volume_l']=='100.0':
            lines.append(f"| {float(row['leak_ref_hz']):g} | {float(row['slowest_state_pole_tau_s']):.3f} | {float(row['max_abs_audio_delta_20_80_db']):.6f} |")
    lines.append(f'''
To wskazuje możliwość rozdzielenia bardzo wolnego wyrównywania barometrii
od pracy w basie. Liczby nie dobierają geometrii otworu. Nieznane pozostają
bezwładność, przepływ nieliniowy, rzeczywisteRa i jego powtarzalność po montażu.
Są to dane do eksperymentu prototypowego, nie polecenie wywiercenia otworu.

## Weryfikacja niezależna i ograniczenia

- **{checks['stable_state_models']} stabilnych realizacji stanu**; sprawdzono macierz energii i końce.
- Największy względny bilans mocy: **{checks['max_relative_power_residual']:.3g}**.
- Niezależny układ5równań termodynamiki: błąd ruchu **{checks['max_relative_primitive_thermodynamics_error']:.3g}**.
- Regresja do adiabatycznegoN7: **{checks['max_relative_legacy_N7_error']:.3g}**.
- Radialna dyfuzja pędu/ciepła metodąFV,36przypadków i siatki64–512:
  maksymalna różnica przy512komórkach **{checks['max_fv_error_at512']:.3g}** względem Bessela.
- ODE vsFFT nieliniowego gazu: maksymalna różnica p/p0 **{checks['nonlinear_ode_max_pressure_error_over_p0']:.3g}**.
- Sprawdzono6tożsamości symbolicznych, w tym dostępność i pasywność sorpcji.

Zgodność matematyki nie identyfikuje materiału ani nie waliduje urządzenia.
Port1D ma uśrednione ciśnienie; masa powietrza wymaga uzgodnienia zMmd/Mms
wP11. Pełny nieliniowy napęd, zawieszenie, termika cewki i limitery pozostają
odrębnymi pakietami. Dokładne pozycje w pokoju4,6×3,7×2,5m są nadal nieznane
(U-017). Nie przypisano stałego room gain i nie wybrano toru pomiarowego.

## Rekomendacja dla dalszego projektu

Zachować regulację znanej objętości geometrycznej oraz możliwość demontażu
i odtwarzalnego mocowania wypełnienia. Zapisywać masę, objętość wypartego
powietrza i stan materiału. Weryfikować osobno zmianę podatności, straty
i bardzo wolne wyrównanie ciśnienia. Nie wybierać końcowego litrażu przez
dopisanie stałego procentu doVb.

Najbliższy krok: **P11 — skończony tłok, obciążenie promieniowaniem i
konwencjaMmd/Mms**, następnieP12/P13 nieliniowy napęd. Końcowy wybór
jednego głośnika i jednej konstrukcji z obliczonym klejem pozostaje P19/P29.

![Relaksacja gazu](../wyniki/13_relaksacja_cieplna_gazu.png)
![Pory i mocowanie](../wyniki/14_pory_i_mocowanie_wypelnienia.png)
![Nieliniowy gaz](../wyniki/15_nieliniowy_gaz_i_granice.png)
![Hermetyczność i DC](../wyniki/16_hermetycznosc_i_wyrownanie_DC.png)

Kod: [gaz](../skrypty/model_gazu.py), [wypełnienie](../skrypty/model_wypelnienia.py),
[nieliniowa termodynamika](../skrypty/termodynamika_nieliniowa.py),
[kontrole](../skrypty/sprawdz_gaz_i_wypelnienie.py),
[tożsamości](../skrypty/audyt_termodynamiki.py),
[kampania](../skrypty/analiza_gazu_i_wypelnienia.py).
Wejścia:[konfiguracja](../dane/konfiguracje/p09_p10_gaz_i_wypelnienie.json),
[źródła](../dane/zrodla/P09_P10_materialy_i_sorpcja.json).
Wyniki:[termika/napęd](../wyniki/p09_relaksacja_i_naped.csv),
[projekcjeF3](../wyniki/p09_projekcja_F3.csv),
[wypełnienie](../wyniki/p09_modele_wypelnienia.csv),
[gaz dla24modeli](../wyniki/p10_gaz_dla_przetwornikow.csv),
[offsety](../wyniki/p10_offset_cieplny_i_barometryczny.csv),
[DC](../wyniki/p10_wyrownanie_DC.csv),
[weryfikacja](../wyniki/p09_p10_weryfikacja.json),
[podsumowanie](../wyniki/p09_p10_podsumowanie.json).
''')
    (ROOT/'raporty/016_gaz_wypelnienie_i_granice.md').write_text('\n'.join(lines))


if __name__=='__main__':main()
