"""Raport P11 z obliczeń; bez wyników urządzenia i bez końcowego PDF."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(name):
    return json.loads((ROOT / 'wyniki' / name).read_text())


def read_rows(name):
    with (ROOT / 'wyniki' / name).open() as handle:
        return list(csv.DictReader(handle))


def count(value):
    return f'{value:,}'.replace(',', ' ')


def main():
    geometry = read_json('p11_geometrie_podsumowanie.json')
    coupling = read_json('p11_sprzezenia_podsumowanie.json')
    dense = read_json('p11_pokoj_gesty_skan.json')
    spatial = read_json('p11_pokoj_zbieznosc_przestrzenna.json')
    checks = read_json('p11_weryfikacja.json')
    packet = read_json('p11_kontrola_pakietu.json')
    benchmark = read_json('p11_replikacja_Bellows2024.json')
    symbolic = read_json('p11_bilans_symboliczny.json')
    rows = read_rows('p11_geometrie_i_naped.csv')
    summaries = read_rows('p11_pokoj_geste_podsumowania.csv')
    raw = json.loads((ROOT / 'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers = {r['candidate_id']: r['model']['name'] for r in raw}
    pilot = geometry['mass_pilot']
    keys = ['candidate_id', 'volume_l', 'profile', 'geometry', 'f_hz']
    reference = {tuple(r[k] for k in keys): r for r in rows if float(r['reference_faces']) == 2}
    double_count = [float(r['spl_1m_from_front_1v_rms_db']) -
                    float(reference[tuple(r[k] for k in keys)]['spl_1m_from_front_1v_rms_db'])
                    for r in rows if float(r['reference_faces']) == 0]
    example = [r for r in rows if r['candidate_id'] == 'C02' and float(r['volume_l']) == 100
               and r['profile'] == 'ADIABATIC' and float(r['reference_faces']) == 2
               and float(r['f_hz']) == 20]
    pressure_refinement = next(r for r in dense['refinements'] if r['metric'] == 'max_abs_pressure_feedback_db')
    lines = [f'''# Raport 017 — promieniowanie, masa powietrza i sprzężenie pokoju

Stan: 2026-10-24. **Wyniki obliczeń i symulacji P11**, dla 24 modeli
przetworników, w tym dwóch kontrolnych 10″. Raport cząstkowy przed budową.
Nie są to wyniki fizycznego urządzenia. Końcowy PDF i wybór jednego głośnika
oraz jednej konstrukcji pozostają zależne od pozostałych pakietów programu.

## Wynik wpływający na projekt

Obciążenie promieniowaniem trzeba rozwiązać razem z napędem oraz jawnie
uzgodnić z powietrzem zawartym w katalogowym Mms. Dodanie nowej masy i oporu
do niezmienionego Mms/Rms nie jest uniwersalnie zachowawcze: w kontrolowanej
siatce różnica względem dopasowania dwóch referencyjnych powierzchni wynosi
od **{min(double_count):+.3f} do {max(double_count):+.3f} dB** przy tym samym napięciu.
To różnica modeli i konwencji, nie zmierzony błąd katalogu.

W gęstym skanie sprzężenie pokoju zmienia ciśnienie w punkcie S0 do około
**{pressure_refinement['refined_value']:.3f} dB** względem przyłożenia tego samego
pola do źródła bez reakcji pokoju. Maksimum dotyczy warunkowego C07 i
hipotetycznego ustawienia B. Nie jest korektą do zastosowania w pokoju użytkownika.
Dla C02/C06/C11 znalezione zmiany są mniejsze; podano je poniżej.

**Rekomendacja:** zachować oddzielne modele geometrii i konwencji referencyjnej.
Przy aktywnym ograniczeniu ruchu zmiana podatności albo masy nie tworzy
dodatkowego Sd·X. Może zmienić potrzebne napięcie i prąd. Same te obliczenia
nie rozstrzygają THD, termiki, kleju ani końcowej przewagi kandydata.

## Wykonany eksperyment i jednostki

| Zakres | Liczba przypadków / wierszy |
|---|---:|
| Dopasowania referencyjnej masy/oporu w Fs; n=0/1/2 | {count(geometry['calibration_rows'])} |
| Trzy geometrie × 4 Vb × 2 profile gazu × 3 konwencje × 6 częstotliwości × 24 modele | {count(geometry['motor_rows'])} |
| Odrębne normalizacje odniesienia 2π/4π | {count(geometry['reference_rows'])} |
| Odrębny katalogowy zestaw C15 z podanym Mmd | {count(geometry['pilot_rows'])} |
| Odgroda, podłoga/ściana i jedno/dwa źródła | {count(coupling['wall_rows'])} |
| Sprzężony pokój, sześć częstotliwości porównawczych | {count(coupling['room_rows'])} |
| Wrażliwość na aperturę Gaussa | {count(coupling['sigma_sensitivity_rows'])} |
| Gęsty skan: konfiguracje × punkty częstotliwości | {count(dense['cases'])} × {count(dense['frequency_points'])} |
| Realizacje częstotliwościowe gęstego skanu | {count(dense['total_frequency_realizations'])} |
| Odrębna kontrola przestrzenna wybranych świadków | {spatial['points']} |
| Sprawdzone kombinacje granic V/I/X w tabelach | {count(packet['sinusoidal_combinations_checked'])} |

Vb=30/60/100/150 l **netto powietrza**. Gaz: koniec adiabatyczny albo
pasywna relaksacja 5 ms, bez przypisania jej materiałowi. Porównawcze
częstotliwości: 20/25/31,5/40/63/80 Hz. Skan gęsty: 20–80 Hz co 0,1 Hz;
trzy znalezione przypadki ekstremalne przeliczono co 0,05 Hz.

Wszędzie fazory RMS i exp(+jωt); SPL odnosi się do 20 µPa. Sygnał to osobny
sinus w stanie ustalonym, bez określonej bezpiecznej długości pracy.
Temperatura odniesienia 293,15 K, p0=101325 Pa, gamma=1,4,
rho≈1,204118 kg/m³, c≈343,232 m/s. Re i mechanika nie są grzane w tym etapie.
Budżety napędu: 40 Vrms/12 Arms lub 60 Vrms/20 Arms **na wzmacniacz**.
Granica ruchu: 0,7/1,0 katalogowego jednostronnego X; nie jest wspólnym
progiem THD. Pe nie użyto jako wspólnego limitu cieplnego.

Impedancja mechaniczna ma jednostkę N·s/m. Dla Q=Sd·v:
Zacoustic=Zmechanical/Sd², a moc RMS wynosi Re(F·conj(v)), bez czynnika 1/2.
W polu bliskim całkujemy Re(p·conj(vr)), nie samą wielkość |p|²/(rho·c).
To rozróżnienie sprawdzono niezależną całką strumienia energii.

## Mmd/Mms: dane producenta i eksperyment kalibracyjny

**Dane producenta:** karta FaitalPRO 15XL1400, wersja 8 Ω, podaje
Mms={pilot['source_mms_g']:.1f} g i Mmd={pilot['source_mmd_g']:.1f} g.
Ich różnica wynosi {pilot['source_difference_g']:.1f} g. W naszym ośrodku
dwie statyczne masy powietrza tłoka w nieskończonej odgrodzie dają
{pilot['two_face_static_piston_air_g']:.3f} g. Zgodność rzędu wielkości nie
identyfikuje protokołu producenta. Gęstość {pilot['implied_density_if_two_face_static_formula']:.6f}
kg/m³ wynikałaby z narzucenia tej formuły; nie jest odczytaną temperaturą
ani gęstością podczas pomiaru fabrycznego.

**Obliczenie:** pierwotny spójny zestaw Fs/Vas/Sd użyty w puli daje
Mms={pilot['internally_consistent_primitive_mms_g']:.3f} g. Różnicę do
drukowanych 190 g zachowano. Osobna tabela pilota używa opublikowanych
Mmd/Cms/BL/Rms. Przy odjęciu oporu referencyjnego nadal zakłada n=2;
sam drukowany Mmd nie identyfikuje rozdziału wszystkich strat Rms.
Nie podmieniono jednego Mmd w innym zestawie T/S bez śladu.

**Założenie kalibracyjne**, dla Zref tłoka w odgrodzie:

```text
M_effective = Mms - n*Im[Zref(Fs)]/(2*pi*Fs)
R_effective = Rms - n*Re[Zref(Fs)]
```

n=0 jest celową kontrolą podwójnego dodania powietrza; n=1/2 to hipotezy
konwencji. Dopasowanie zachowuje reaktancję i opór w Fs, lecz nie odtwarza
całej krzywej, jej nachylenia ani pełnego Q. Wynik nie jest pomiarem Mmd.
Nie wykazano, że n=1/2 wyczerpuje wszystkie protokoły katalogowe.
Niedodatnią masę lub stratę pozostałą model odrzuca.

## Nieskończona odgroda i skończona bryła kontrolna

**Model analityczny:** okrągły tłok o a=sqrt(Sd/pi), q=ka:

```text
Zrad = rho*c*Sd*[1-J1(2q)/q + j*H1(2q)/q]
Mair_front(0) = 8*rho*a³/3
```

Niezależna całka Rayleigha i całka kierunkowej mocy zgadzają się z tym
rozwiązaniem. Przy małym ka stosujemy szeregi zamiast odejmowania bliskich
liczb. Formalny duży ka sprawdza model sztywnego tłoka; nie potwierdza
sztywności rzeczywistej membrany przy wysokiej częstotliwości.

**Model kontrolny bryły skończonej:** radialnie drgająca czasza na sztywnej
sferze, na zewnątrz suma wychodzących funkcji Hankela. Wewnątrz osobno
sprężanie jednorodne K(s)/s i reszta rozłożonego pola opisana funkcjami
Bessela sferycznymi. Objętość sfery wewnętrznej to Vb; offset promienia
zewnętrznego 22 mm jest parametrem geometrii kontrolnej, nie wybraną grubością MDF.
To nie jest płaski kosz w skrzyni prostopadłościennej ani propozycja CAD.

Przykład **C02 / RSS390HF-4, 100 l, 20 Hz, gaz adiabatyczny, n=2**.
Punkt na osi leży 1 m od frontu danej geometrii. Kolumna ograniczonego
napędu uwzględnia 40 Vrms/12 Arms/1X. Wszystkie trzy przypadki ogranicza X.

| Geometria wzorcowa | SPL przy 1 Vrms [dB] | Limit modelowy V/I/X [dB] |
|---|---:|---:|''']
    labels = {'INFINITE_BAFFLE_LUMPED': 'Nieskończona odgroda, gaz skupiony',
              'FINITE_SPHERE_LUMPED': 'Czasza na sferze, gaz skupiony',
              'FINITE_SPHERE_CAVITY': 'Czasza na sferze, gaz rozłożony'}
    for r in example:
        lines.append(f"| {labels[r['geometry']]} | {float(r['spl_1m_from_front_1v_rms_db']):.3f} | {float(r['V40_X1_spl_1m_rms_db']):.3f} |")
    lines.append(f'''
Te różnice są wynikiem **różnych geometrii kontrolnych**. Nie wolno podawać
101,83 dB z nieskończonej odgrody jako osiągu wolnostojącego prototypu.
Dokładne 6,0206 dB dotyczy oddzielnego przeliczenia normalizacji monopola
2π/4π przy tym samym przepływie i odległości. Skończona bryła, położenie
punktu oraz reakcja napędu wymagają osobnego rozwiązania.

**Replikacja opublikowanej teorii:** z sumy Legendre'a otrzymano minimum
poprawki Bellows2024 **{benchmark['computed_minimum']:.9f}** przy
**{benchmark['computed_half_angle_degrees']:.6f}°**, zgodne z drukowanymi
0,6167 i 50,5°. Normalizacja dotyczy promienia rzutu czaszy b·sin(theta)
oraz 0<theta≤90°, nie promienia koła o powierzchni Sd. Pełną pulsującą sferę
sprawdzono osobnym rozwiązaniem. Wartość 0,6133·a dla otwartego końca rury
nie jest ogólną poprawką dowolnego nieodgrodzonego głośnika.

## Ściany, dwa źródła i rzeczywiste wymiary pokoju

Odgroda z obrazami podłogi/lewej ściany ma macierz wzajemnych impedancji
uzyskaną z całki Rayleigha. Ściany są idealnie sztywne i prostopadłe do
nieskończonej odgrody. Sprawdzono wzajemność i dodatniość całkowitej mocy.
Ten eksperyment **jest oddzielny od pełnego modelu pokoju**; nie dodajemy
jego zysku do pola modalnego. Dwa wzmacniacze o tym samym napięciu każdy
nie oznaczają stałej łącznej mocy względem pojedynczego wzmacniacza.

W pokoju przyjęto x=3,7 m, y=4,6 m, z=2,5 m, V=42,55 m³,
przednią ścianę szerokości 3,7 m i miejsca przy monitorach. Cztery ustawienia
A–D, modalne T60=0,2/0,4/0,8 s i tau0=0,02/0,2/2 s dają 36 rodzin.
Ich współrzędne, S0 i straty są założeniami U-017. Nie ma danych rzeczywistej
pozycji głowy ani monitorów. Nie przyjęto swobodnego układu przód/tył.

Źródło i odbiór siły mają tę samą aperturę Gaussa sigma=0,12 m; obserwator
sigma=0,03 m. Dzięki zgodności portów otrzymujemy pasywną macierz, nie
tylko pole przy narzuconym przepływie. Sigma nie jest promieniem membrany.
Odrębnie zbadano 0,08/0,12/0,16 m w wybranym scenariuszu. Kalibracja
wolnego portu Gaussa usuwa referencyjne przednie powietrze; pozostała masa
jest efektywna, nie niezależnie zmierzonym Mmd. Model pomija rozpraszanie
na przyszłej skrzyni. Nierozpoznanej geometrii nie utożsamiamy z tolerancją
produkcyjną ani ze zmierzonym pokojem.

Napęd rozwiązywany jest łącznie z reakcją pola. Dla D=Dfree+DeltaZ:

```text
epsilon = ||Dfree^(-1)*DeltaZ||_2
epsilon<1 => ||v-vfree||_2/||vfree||_2 <= epsilon/(1-epsilon)
```

To warunkowe ograniczenie zmiany **wektora prędkości** w danej
częstotliwości. Nie jest względnym ograniczeniem ciśnienia w dołku pola.
W całej sprawdzonej siatce epsilon<1; największe epsilon wynosi
{dense['maxima']['max_perturbation_norm']:.6f}, a znaleziona względna zmiana
wektora prędkości {100*dense['maxima']['max_relative_velocity_change']:.3f}%.
Nie jest to dowód maksimum po ciągłym paśmie ani po dowolnym ustawieniu.

Poniżej maksima bezwzględnych zmian znalezione osobno dla każdej miary
na siatce 0,1 Hz, po wszystkich zadanych Vb/ustawieniach/stratach/liczbach
źródeł. Kolumny nie muszą dotyczyć tego samego punktu.

| Kandydat | Zmiana wektora v [%] | Zmiana SPL przy 1 Vrms/amp [dB] | Zmiana limitu 40V/12A/1X [dB] |
|---|---:|---:|---:|''')
    for cid in ['C02', 'C06', 'C07', 'C11', 'C15']:
        selected = [r for r in summaries if r['candidate_id'] == cid]
        vmax = max(float(r['max_relative_velocity_change']) for r in selected)
        pmax = max(float(r['max_abs_pressure_feedback_db']) for r in selected)
        cmax = max(float(r['max_abs_available40v12a1X_change_db']) for r in selected)
        lines.append(f'| {cid}: {drivers[cid]} | {100*vmax:.3f} | {pmax:.3f} | {cmax:.3f} |')
    lines.append(f'''
C07 ma nierozwiązany konflikt oznaczenia 8/4 Ω w źródle. Największa zmiana
SPL występuje w ustawieniu B, Vb=60 l, dwa źródła, T60=0,8 s, tau0=0,02 s.
Ustawienie B (front y=0,35 m) nie przeszło wcześniejszej kontroli gabarytu
dla przykładowej rodziny sześciennych skrzyń. Nie dowodzi to niemożliwości
każdej szerokiej/płytkiej geometrii, lecz wyklucza traktowanie tego przypadku
jako gotowego, potwierdzonego ustawienia. C11 zachowuje wcześniejszą bramkę
tożsamości/statusu źródła katalogowego. Żaden z tych wierszy nie jest
ostatecznym rankingiem zgodności z briefem.

## Kontrole niezależne, zbieżność i granice

| Kontrola | Największa zaobserwowana różnica |
|---|---:|
| Rayleigh vs Bessel/Struve, względnie | {checks['rayleigh_vs_struve_max_relative_error']:.3g} |
| Moc kierunkowa vs Re(Zrad), względnie | {checks['angular_power_max_relative_error']:.3g} |
| Ciśnienie osiowe vs całka powierzchniowa, względnie | {checks['axis_pressure_integral_max_relative_error']:.3g} |
| Pełna sfera vs rozwiązanie zamknięte, względnie | {checks['full_sphere_max_relative_error']:.3g} |
| Strumień energii czaszy vs praca na porcie, względnie | {checks['cap_flux_max_relative_error']:.3g} |
| Czasza: 512 vs 1024 składniki, względnie | {checks['cap_convergence']['relative_512_1024']:.3g} |
| Wolny port Gaussa vs odrębna całka, względnie | {checks['gaussian_integral_max_relative_error']:.3g} |
| Bilans mocy w gęstym skanie, względnie | {dense['max_relative_energy_residual']:.3g} |
| Zagęszczenie f do 0,05 Hz: największa zmiana znalezionego maksimum SPL | {pressure_refinement['absolute_difference']:.6f} dB |
| kmax=40 vs 60 m⁻¹, port siły, względnie | {spatial['max_relative_port_difference']:.3g} |
| kmax=40 vs 60 m⁻¹, operator obserwatora, względnie | {spatial['max_relative_observer_difference']:.3g} |
| kmax=40 vs 60 m⁻¹, bezwzględny SPL rozwiązania sprzężonego | {spatial['max_abs_coupled_SPL_difference_db']:.3g} dB |
| kmax=40 vs 60 m⁻¹, różnica poprawki sprzężenia | {spatial['max_abs_feedback_difference_db']:.3g} dB |

Mała różnica **ilorazu** ciśnień nie zastępuje kontroli obu operatorów:
część ich błędu może się skracać. Dlatego zapisano też zmianę absolutnego
SPL i operatora obserwatora. Kontrola przestrzenna obejmuje wyłącznie
{spatial['points']} wybrane punkty ekstremalne i sąsiednie, nie całą dziedzinę.

Bilans motorów i modów potwierdzono symbolicznie:
`{symbolic['status']}`. Przeciwne moce sił/przepływów znoszą się,
a każdy człon modalny i mod relaksacyjny ma nieujemną część rzeczywistą.
W granicy bez strat mogą istnieć nierozpraszane mody; nie przypisujemy
jej bezwarunkowej asymptotycznej stabilności.

| Granica / dziedzina | Oczekiwany i sprawdzony wynik |
|---|---|
| ka→0 w modelu sztywnego tłoka | Re(Z) rzędu ka², Im(Z)/omega→8rho·a³/3 |
| Formalnie duży ka sztywnego tłoka | Re(Z)→rho·c·Sd; nie jest modelem breakupu membrany |
| f=0 promieniowania na zewnątrz | Zerowa impedancja statyczna, skończona granica dodanej masy |
| Pełna czasza/sfera | Zgodność z rozwiązaniem pulsującej sfery |
| Mały kąt czaszy przy stałym Sd | Dojście do płaskiej odgrody; zbadana zbieżność, bez deklaracji błędu dla dowolnego kąta |
| Komora, f→0 | Wyodrębniony biegun K(s)·Sd²/(sV); nie skończona wartość w f=0 |
| Bezstratna komora przy własnych modach | Możliwe bieguny; nie obiecuje się ograniczonej odpowiedzi na rezonansie |
| Niedodatnia masa/opór po kalibracji | Odrzucenie niepasywnego zestawu |
| Dwa porty, dowolne fazy w geometrii wzorcowej | Wzajemność i nieujemna całkowita moc promieniowania |
| Aktywny X przy tej samej geometrii zewnętrznej | Ten sam pułap ciśnienia od ruchu, inne wymagane V/I |

Dla {count(packet['motion_limited_groups'])} grup ograniczonych ruchem rozrzut
po zmianie masy/profilu gazu/budżetu napędu wynosi maksymalnie
{packet['max_motion_limited_group_spread_db']:.3g} dB. Niezależny osiowy wzór
pułapu ruchu zgadza się względnie do
{packet['max_relative_closed_axis_motion_ceiling_error']:.3g}.
Największy szczytowy Mach w skalibrowanych przypadkach skalarnych wynosi
{packet['max_peak_mach_in_calibrated_scalar_cases']:.5f}. Nie dowodzi to małego
THD motoru ani bezpieczeństwa cewki.

## Otwarte wyniki i następny eksperyment

P11 wykonano dla jawnych rodzin kontrolnych i sprzężenia modalnego.
Nie rozwiązano rozpraszania na docelowym prostopadłościanie, rzeczywistego
profilu membrany, kosza i wypełnienia, ani nie zidentyfikowano masy suchej
i strat każdego fizycznego egzemplarza. Te zależności pozostają jawne
przy integracji P18/P21/P29. Skończona siatka, lokalne zagęszczenie i
sprawdzenie pasywności nie certyfikują wszystkich możliwych zjawisk.

**Najbliższy krok: P12/P13**, energetycznie zgodny model BL(x), Cms(x),
Le(x,i) i Rms(v), połączony z nieliniowym gazem. Najpierw źródła, dziedzina
i identyfikowalność krzywych; następnie obliczenia dla jawnych rodzin
warunkowych oraz kontrola liniowej granicy, współenergii i zbieżności.
Brak krzywych produktu nie upoważnia do przypisania mu fikcyjnego THD.
Dalsze P14–P29 obejmą termikę, panele, klej, regulację Vb i ochronę DSP.
Nie wybrano jeszcze zwycięzcy ani finalnego litrażu.

## Wykresy i odtwarzanie

![Opór i masa promieniowania](../wyniki/17_promieniowanie_i_masa_powietrza.png)
![Skończona bryła kontrolna](../wyniki/18_skonczona_bryla_i_odgroda.png)
![Reakcja pokoju na napęd](../wyniki/19_reakcja_pokoju_na_naped.png)
![Ściany i apertura](../wyniki/20_sciany_i_apertura.png)
![Gęsta siatka przy modach](../wyniki/21_gesty_skan_reakcji_pokoju.png)

Kod: [promieniowanie](../skrypty/model_promieniowania.py),
[napęd wieloportowy](../skrypty/naped_z_promieniowaniem.py),
[obrazy](../skrypty/odgroda_i_obrazy.py),
[kampania geometrii](../skrypty/analiza_promieniowania.py),
[pokój](../skrypty/analiza_scian_i_sprzezen.py),
[gęsty skan](../skrypty/gesty_skan_sprzezenia_pokoju.py),
[replikacja teorii](../skrypty/replikacja_poprawki_czaszy.py),
[weryfikacja](../skrypty/sprawdz_promieniowanie.py),
[energia](../skrypty/audyt_energii_promieniowania.py),
[zbieżność przestrzenna](../skrypty/sprawdz_zbieznosc_pokoju_P11.py),
[granice tabel](../skrypty/sprawdz_pakiet_promieniowania.py).
Wejścia: [konfiguracja](../dane/konfiguracje/p11_promieniowanie.json),
[pochodzenie źródeł](../dane/zrodla/P11_promieniowanie_i_konwencje_mas.json),
[wyprowadzenie w bazie wiedzy](../baza_wiedzy/13_promieniowanie_masy_i_reakcja_pokoju.md).
Tabele: [geometrie](../wyniki/p11_geometrie_i_naped.csv),
[kalibracje](../wyniki/p11_kalibracje_masy.csv),
[obrazy](../wyniki/p11_sciany_i_wzajemne.csv),
[sprzężenie pokoju](../wyniki/p11_pokoj_sprzezenie_zwrotne.csv),
[gęste podsumowania](../wyniki/p11_pokoj_geste_podsumowania.csv),
[kontrola przestrzenna](../wyniki/p11_pokoj_zbieznosc_przestrzenna.json),
[kontrola V/I/X](../wyniki/p11_kontrola_pakietu.json).
Pełne odtworzenie: `python3 skrypty/odtworz_wszystko.py`, manifest na końcu.

Źródła pierwotne SRC28–30:
[COMSOL6.3](https://www.comsol.com/model/download/1340691/models.aco.baffled_piston_radiation.pdf),
[FaitalPRO, 8 Ω](https://faitalpro.com/en/products/LF_Loudspeakers/product_details/datasheet.php?id=201060150),
[Bellows2024](https://sambellows.github.io/assets/pdf/2024_spherical_cap.pdf).
Oryginalne równania i rysunki obejrzano; automatycznych tablic punktów
wykresów nie użyto. Wykresy źródłowe nie są naszymi pomiarami.
Link Southampton przekierował na stronę główną i został odrzucony jako
nieprzeczytana praca. Prywatne kopie robocze PDF mają hashe w rejestrze;
repozytorium zawiera fakty i pochodzenie, bez publikacji tych kopii.
''')
    target = ROOT / 'raporty/017_promieniowanie_i_sprzezenie_pokoju.md'
    target.write_text('\n'.join(lines), encoding='utf-8')
    print('Zapisano', target.relative_to(ROOT))


if __name__ == '__main__':
    main()
