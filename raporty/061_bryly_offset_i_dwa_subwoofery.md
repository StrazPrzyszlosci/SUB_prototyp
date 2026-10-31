# Raport 061 — P26D/P27D: nowe bryły, przesunięte źródła i dwa subwoofery

Data: 2026-10-31. **Obliczenia scenariuszowe, nie pomiar pokoju, nie preset DSP i nie ocena rzeczywistego SPL.** Zintegrowano gabaryt obudowy1000×440×500 mm z położeniem osi231/250 mm od lewej/dolnej krawędzi frontu. Nowością względem wcześniejszego P26 jest rzeczywiste powiązanie orientacji bryły z przesunięciem źródła oraz jawna kontrola wspólnego budżetu dwóch źródeł.

## Pytanie i hipoteza

Czy obrót poziom/pion i odbicie głośnika, wynikające z tej samej obudowy, zmieniają odpowiedź wystarczająco, by wpłynąć na wybór ustawienia i gain/delay? Hipoteza: przesunięcie źródła zmienia sprzężenie z modami; najkorzystniejszy wariant nominalny nie musi być odporny na nieznane straty. Nie zakładamy dostępności tylnej ściany ani znajomości transferów monitorów.

## Geometria i nieznane dane

Pokój3,7×4,6×2,5 m, x szerokość, y od frontu, z wysokość; źródło i siedem punktów diagnostycznych wywodzą się z istniejących konfiguracji. Sweet spot scenariuszowy [1,85;3,10;1,10] m. Sąsiedzi: ±0,15 m w x/y i ±0,10 m w z. Nie są to zmierzone pozycje użytkownika. W istniejącym scenariuszu monitory [0,65;0,65;1,10] i[3,05;0,65;1,10] dają odległość do centralnego punktu około2,73 m, ale **nie modelowano ich obudów, transferów ani zwrotnic**.

Środki brył w x wynoszą0,70 i3,00 m. Ustawienie A: oba drewniane fronty y=0,65 m. Ustawienie B: lewy front y=0,55 m, prawy y=0,80 m. Są to lokalizacje przy przedniej strefie/monitorach, bez źródeł przy tylnej ścianie.

Obwiednia dodatkowo przyjmuje: tylny występ8 mm, przedni48 mm, stopki20 mm. Cała głębokość w tej rodzinie to **496 mm**. Jest to scenariusz obrysu C02 z P20D, nie potwierdzony wymiar maskownicy. Równoważny port źródła umieszczono16 mm przed drewnianym frontem; wartość spoczynkowa jest założeniem. Większy skok C11 wymaga osobnego sprawdzenia obrysu. Obie skrzynie mieszczą się w pustym prostopadłościanie i nie przecinają się; minimalny odstęp od przedniej ściany w B wynosi102 mm. **Nie sprawdzono mebli, przejść, monitorów ani dostępu serwisowego**, bo brak ich ustalonych brył.

- H_in: poziomo, źródła bliżej osi pokoju: x0,969 i2,731 m, z0,270 m.
- H_out: poziomo, źródła skierowane ku bocznym ścianom: x0,431 i3,269 m, z0,270 m.
- V_low: pionowo, źródła x0,700 i3,000 m, z0,251 m.
- V_high: pionowo po przeciwnym obrocie/odbiciu: te same x, z0,789 m.

Dla każdej orientacji A/B zapisano pełne min/max brył i źródła w `dane/konfiguracje/p26d_bryly_scenariusze.json`. Obrót nie przekształca przypadkowo punktu źródła w środek nowego frontu.

## Model i równania

Wykorzystano istniejący `ModalRoom` z P26: liniowy, fenomenologiczny model prostopadłościanu z sztywnymi funkcjami modalnymi i diagonalnymi stratami. `exp(+j omega t)`, ciśnienia i prędkości objętościowe RMS. Dla niezerowych modów:

`H_rs(s) = rho c²/V Σ psi_n(r) psi_n(s) exp[−(sigma_s²+sigma_r²) k_n²/2] s/(s²+2 gamma s+c² k_n²)` [Pa s/m³],

`k_n² = Σ (n_i pi/L_i)²`, `gamma=3 ln(10)/T60` [1/s].

Mod zerowy ma osobną relaksację `rho c²/[V(s+1/tau0)]`. T60=0,2/0,4/0,8 s oraz tau0=0,02/0,2/2 s tworzą9 scenariuszy, a nie zmierzony RT60 i przeciek tego pokoju. Wygładzenie źródła0,12 m i odbiornika0,03 m jest heat-kernel Neumanna; **nie jest promieniem membrany**. Bazowe kmax=40 m⁻¹. Nie rozwiązano rzeczywistego impedancyjnego warunku ściany, okien/przejścia ani rozpraszania na dwóch bryłach. Bryły ograniczają pozycje, ale nie są przeszkodami w równaniu fali.

Pierwsze mody osiowe idealnego prostopadłościanu: szerokość46,35 Hz, długość37,28 Hz, wysokość68,60 Hz. To opis modelu, nie zmierzone częstotliwości pokoju.

Wszystkie strategie mają **jednakowy łączny budżet amplitudy prędkości objętościowej**:

`U_L=alpha U0`, `U_R=(1−alpha) exp(−j omega delay) U0`, `|U_L|+|U_R|=U0`.

Przyjęto U0=1 m³/s do normalizacji transferu, nie jako osiąg głośnika. Dla jednego źródła U=U0. To nie jest wspólna moc elektryczna, stałe wychylenie lub maksymalny SPL. Nie dodajemy automatycznie6 dB za drugie źródło. Nie sprzężono reakcji pokoju z napędem i nie przyznano obu źródłom jednocześnie pełnego pojedynczego budżetu.

Metryka centralna: różnica max–min `20log10|p/U0|` na siatce20–80 Hz co0,5 Hz. Sąsiedztwo: największa bezwzględna różnica dB względem centrum oraz rozstęp siedmiu punktów dla wspólnej częstotliwości. Diagnostyka fazy: RMS zawiniętej różnicy faz dwóch portów po delay, a osobno kasowanie `20log10(|suma|/suma_modułów)`. Ujemny względny delay oznacza opóźnienie przeciwnego kanału plus wspólne przesunięcie; nie wymaga fizycznej antycypacji.

## Wykonana próba i wyniki

8 geometrii×9 środowisk=72 modele transferu, każdy z7 odbiornikami i121 częstotliwościami. Cztery strategie tworzą288 wierszy porównań: oba po0,5, zamrożony wybór nominalny, tylko lewy, tylko prawy. Na geometrię sprawdzono27 par `alpha∈{0,25;0,5;0,75}` i delay−8…+8 ms co2 ms. Wybrano najniższą nierównomierność **tylko dla T60=0,4 s/tau0=0,2 s**, po czym te same parametry zastosowano do8 pozostałych środowisk. Remisy do1e−9 dB rozstrzygnięto zachowaniem równych gainów i zerowego delay. To skończona próba, nie globalna optymalizacja lub zalecenie nastaw.

| Układ | Nierównomierność nominalna, oba równo [dB] | Najgorsza różnica sąsiad–centrum nominalnie [dB] | Najgorsza nierównomierność w9 środowiskach, oba równo [dB] |
|---|---:|---:|---:|
| A_H_in | 34.56 | 12.69 | 37.00 |
| A_H_out | 53.73 | 30.13 | 53.73 |
| A_V_low | 42.04 | 19.14 | 42.24 |
| A_V_high | 32.28 | 13.75 | 78.92 |
| B_H_in | 33.51 | 11.58 | 36.39 |
| B_H_out | 58.10 | 34.13 | 66.52 |
| B_V_low | 39.79 | 16.95 | 40.06 |
| B_V_high | 32.72 | 10.90 | 66.17 |

**Duże liczby wynikają z głębokich zer modelu. Nie prognozują rzeczywistej dziury78 dB w pokoju i nie uzasadniają jej wypełniania EQ.** Minimalne zmiany warunków, źródeł i przyjętego tłumienia mogą zmienić głębokość zera. Użyteczny wniosek to niestabilność wyboru na podstawie jednego scenariusza, nie dokładny poziom dołka.

| Układ | alpha lewy | delay prawy [ms] | nominalna nierównomierność po wyborze [dB] | zmiana średniego transferu vs oba równo [dB] | najgorsza nierównomierność po wyborze,9 środowisk [dB] |
|---|---:|---:|---:|---:|---:|
| A_H_in | 0.50 | 0.0 | 34.56 | +0.00 | 37.00 |
| A_H_out | 0.50 | 0.0 | 53.73 | +0.00 | 53.73 |
| A_V_low | 0.50 | 0.0 | 42.04 | +0.00 | 42.24 |
| A_V_high | 0.50 | 0.0 | 32.28 | +0.00 | 78.92 |
| B_H_in | 0.25 | -4.0 | 31.49 | -1.77 | 43.71 |
| B_H_out | 0.75 | -8.0 | 39.49 | -2.73 | 63.08 |
| B_V_low | 0.25 | -6.0 | 35.54 | -3.43 | 51.04 |
| B_V_high | 0.75 | 0.0 | 31.95 | +0.43 | 66.62 |

Średni transfer jest średnią dB po częstotliwości; nie jest sprawnością ani poziomem muzyki. B_H_in poprawia nominalną nierównomierność33,51→31,49 dB, lecz pogarsza najgorszy scenariusz36,39→43,71 dB i obniża średni transfer o1,77 dB. B_V_low ma analogiczny problem:39,79→35,54 dB nominalnie, ale40,06→51,04 dB w najgorszym środowisku i−3,43 dB średniego transferu. Dalsze zwiększenie sygnału w celu odrobienia takiej straty wymagałoby większego U i kontroli X/V/I/T; obecny budżet go nie zapewnia.

Dla symetrycznych A i punktu na osi **H_L=H_R**. Przy zerowym delay każdy podział alpha przy sumie1 daje ten sam transfer centralny, także jedno źródło z całym budżetem. Taki pomiar sam nie identyfikuje najlepszego podziału gainów. Nie oznacza braku korzyści dwóch subwooferów: różnice pojawiają się poza osią i przy rzeczywistych indywidualnych limitach przetworników. Właśnie dlatego zapisano7 punktów i nie przypisano obu głośnikom osobno U0.

RMS różnicy faz po nominalnym wyborze wynosi w B_H_in około79,67°, B_H_out123,11°, B_V_low117,41°, B_V_high10,49°. Odpowiadające najgorsze kasowanie sumy to około−5,12/−6,39/−9,20/−0,28 dB. Mała faza względna nie eliminuje wspólnego dołka transferu pokoju. Nie jest to zgodność fazowa z monitorami — ich odpowiedzi są nieznane.

## Kontrole i zbieżność

Sprawdzono zamknięte obwiednie wszystkich16 brył w pustym pokoju i brak wzajemnego przecięcia w8 układach. Kontrola lustrzana A porównała odbiorniki x±0,15 m dla równych źródeł w każdym z9 środowisk:36 warunków z resztą względną poniżej1e−11. To kontrola symetrii modelu i transformacji geometrii, nie niezależna walidacja rzeczywistego pola.

Dwa świadki zbieżności kmax40→60 m⁻¹: A_H_in oraz B_V_high w nominalnym środowisku. Sprawdzono20/40/60/80 Hz i częstotliwość minimum znalezioną na siatce. Największa względna zmiana pojedynczego zespolonego portu wyniosła8,75e−7, zmiana modułu7,08e−6 dB. Obowiązuje stałe wygładzenie0,12/0,03 m; wynik nie jest certyfikatem granicy źródła punktowego ani wszystkich parametrów strat.

Dodatkowo zagęszczono częstotliwości w dwóch najgorszych scenariuszach:

| Układ / środowisko | krok [Hz] | nierównomierność [dB] | częstotliwość minimum [Hz] |
|---|---:|---:|---:|
| A_V_high, T60=0.8, tau0=0.02 | 0.250 | 78.9667 | 59.500 |
| A_V_high, T60=0.8, tau0=0.02 | 0.125 | 78.9801 | 59.500 |
| B_H_out, T60=0.4, tau0=2 | 0.250 | 66.5465 | 62.000 |
| B_H_out, T60=0.4, tau0=2 | 0.125 | 66.5465 | 62.000 |

Zmiana0,25→0,125 Hz to0,0134 dB dla A_V_high i0 dB dla B_H_out na tych siatkach; nie dowodzi globalnego ekstremum po ciągłej częstotliwości. Niepewność geometrii i warunków brzegowych pozostaje znacznie ważniejszą niewiadomą niż te reszty. Suma narzuconych |U| jest algebraicznie1 dla każdej strategii; nie nazywamy jej bilansem mocy akustycznej, bo nie obliczono pracy źródeł ani ich wzajemnego obciążenia.

![Bryły, transfer i wrażliwość](../wyniki/p26d_bryly_i_odpowiedz.png)

## Decyzja, granice i dalsza integracja

1. Zachować możliwość pion/poziom i odbicia osi na etapie prób. Nominalnie V_high wygląda korzystniej niż V_low, ale przy innych stratach jego najgorszy przypadek jest znacznie gorszy. Nie wybrano rzeczywistego ustawienia.
2. Nie dostrajać gain/delay do jednej niezmierzonej funkcji pokoju. Przykłady B są konkretnymi kontrprzykładami odporności nominalnej poprawy. Potrzebna identyfikacja osobnych transferów i ocena sąsiedztwa, nie tylko osi.
3. Pozostawić dwa niezależne wyjścia DSP dla subwooferów. Podział gainów, opóźnienia, polaryzacja i EQ mają przejść późniejszy pomiarowy bilans dynamiki; **nie utworzono gwarantowanego EQ** ani progów limitera.
4. Nie przenosić wniosków z narzuconego U na porównanie osiągów C02/C11/C06 bez sprzężonego modelu napędu. Geometria C02 została powiązana z pozycją; rzeczywista membrana, promieniowanie i rozpraszanie na bryle pozostają poza tym krokiem.
5. P26/P27: wykonano nowy zakres geometrii i strat. P28: nadal brak rzeczywistych monitorów i ich fazy/latencji. Pełny program oraz fizyczna walidacja pozostają otwarte.

Po budowie: zmierzyć osobno każdy sub przy niezmienionym napięciu i pozycji mikrofonu, zachować pełne zespolone transfery i7 punktów, a następnie ocenić ich sumę przy stałym budżecie i rzeczywistych ograniczeniach. Po pomiarze monitorów dobrać podział akustyczny i delay. Nie ponawiać pytania o dokładne pozycje teraz: zapisane współrzędne pozostają scenariuszami.

Odtwarzanie:

```bash
OPENBLAS_NUM_THREADS=1 python skrypty/pokoj_bryly_P26D.py
python skrypty/raportuj_bryly_P26D.py
```

Źródła wejściowe: `pokoj_odsluchowy.json`, `pokoj_rzut_scenariusze_v2.json`, `p26_scenariusze.json`, aktualna bryła i offset z P20D. Ich role są rozdzielone: przybliżone wymiary pokoju i limit obrysu pochodzą z wymagań, współrzędne/tłumienie/maskownica są założeniami. Wykorzystano istniejący kod modelu pokoju z zakresów raportów013/017/019, nie wykonywano nowych pomiarów ani nie szukano cen. Hashe kodu, wejść, briefu i wyników: `wyniki/p26d_manifest.json`.
