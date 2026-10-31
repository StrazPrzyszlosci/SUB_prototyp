# Raport 058 — P25C: sygnały czasowe, grzanie i ochrona portu

Data: 2026-10-30. **Nowe obliczenie w modelu zredukowanym, nie pomiar urządzenia.**
Badanie rozwija P22B/P24A i wielotony P29B. Nie zastępuje oczekującego
sprzężenia przestrzennego z rzeczywistą geometrią: 100/120/150 l to tutaj
jawne wartości netto modelu 0D, a nie stwierdzenie, że nowa skrzynia je osiąga.

## Pytanie i hipoteza

Czy HP20 i ograniczenie napięcia albo statyczne sprzężenie prądowe
utrzymają ruch w zadanym zakresie przy zmiennym Re(T), wielotonie i impulsach?
Hipoteza kontrolna: nie wystarczą. Druga hipoteza: sterowanie mocą portu
przez barierę energii daje wystarczający, konserwatywny warunek ograniczenia
X/I/T w zdefiniowanym modelu. Wynik może zmienić architekturę ochrony;
nie służy wybieraniu głośnika na podstawie sztucznie niskiego limitera.

## Dane, model i jednostki

C02 RSS390HF-4, C11 RSS390HE-22 seria, C06 STX W.32.800.8.FCX:
zamrożone T/S z `dane/przetworniki/pula_rozszerzona.json`, bez zmiany
pierwotnych danych. `analiza_rozszerzenia_SB.candidates` i `model_subwoofera`
wyprowadzają Mms, Cms, BL i Rms ze spójnego zestawu Fs/Q/Vas/Sd/Re.
Mms pozostaje efektywne; nie dodajemy frontowej masy promieniowania
ani ponownie tylnej masy powietrza. Nie jest to identyfikacja Mmd.

Wszystkie równania w SI, x [m], v [m/s], i [A], θ [K powyżej otoczenia]:

```
K = 1/Cms + rho*c²*Sd²/Vb
xdot = v
Mms*vdot = BL*i - Rms*v - K*x
Le*idot = u - Re0*(1+alpha*theta)*i - BL*v
Cth*theta_dot = Re0*(1+alpha*theta)*i² - theta/Rth
```

Zmienna `u` to idealne napięcie fizycznego portu, nie próbka miniDSP.
Le, BL i mechanika pozostają stałe. Gaz jest jednorodny, adiabatyczny,
ściany sztywne; brak nieliniowości zawieszenia, przepływu i magnesu,
przecieków, termiki skrzyni, LC wzmacniacza oraz opóźnienia sterownika.
Źródło może odebrać energię zwrotną. Tego nie przenosić bez kontroli na zasilacz.

Jawne, **niezidentyfikowane scenariusze cieplne**:
Rth/Cth/θ0 = 0,3 K/W / 200 J/K / 0 K albo 1,2 K/W / 50 J/K / 60 K.
Alpha=0,004/K. Granica θlim=80 K jest progiem modelu, nie dopuszczalną
temperaturą kleju lub cewki. Xref=0,6 katalogowego Xmax; nie oznacza niskiego THD.
Szyny ±56,5685 V; Ihardware=16,9706 A peak. Wspólny limit prądu:

`Icap=min(Ihardware, sqrt(theta_lim/[Rth*Re0*(1+alpha*theta_lim)]))`.

Nie utożsamiać Icap z samym sprzętowym limitem ani mocy Pe z grzaniem miedzi.

## Rzeczywiście wykonany eksperyment

216 przebiegów: 3 kandydatów × 3 Vb × 4 sygnały × 3 strategie × 2 scenariusze
termiczne. Każdy 6 s, 24 kHz, rozruch od zerowego ruchu/prądu,
20 ms narastania oraz ostatnie 0,5 s bez wejścia przed filtrem.
To krótkie próby dynamiczne, nie symulacja długotrwałego stanu cieplnego.
Sygnały deterministyczne, nie nagrania ani model statystyczny gatunków:

- osiem tonów 20/25/31/40/50/63/80/100 Hz z amplitudą ∝1/sqrt(f), fazy zgodne;
- ten sam zbiór tonów z fazami Schroedera;
- powtarzane co 0,5 s pakiety 35 Hz z zanikiem 65 ms i składnikiem 73 Hz;
- 7 Hz + 35 Hz i impuls Gaussa w 0,12 s, szerokość 4 ms.

Nominalne 70 V RMS dotyczy normalizacji przed obwiednią i filtrem.
Nie jest to jednakowa moc akustyczna lub głośność wszystkich sygnałów.
Filtr software: BW2 HP20 i LR4 LP80, zaprojektowany dla częstotliwości
obliczenia. Bez LT i dodatniego EQ. Scenariusz prowokuje clipping.
Crest factor przed i po filtrze zapisano w JSON; fazy mają znaczenie.

Strategie:

1. `rail`: HP/LP oraz nasycenie napięcia do szyn.
2. `current_feedback`: `u=clip(cmd-10 ohm*sign(i)*max(|i|-Icap,0))`.
   To skończone sprzężenie, nie idealne narzucenie prądu.
3. `energy_barrier`: nasycenie napięcia i ograniczenie dopływu energii,
   z idealną znajomością stanu oraz parametrów.

Stanów x/v/i nie przycinano. Zachowano energię indukcyjności i SEM.

## Nowy warunek bariery

Fizyczna energia elektryczno-mechaniczna:

`E=(K*x²+M*v²+Le*i²)/2`, `Edot=u*i-Rms*v²-Re(theta)*i²`.

Przyjmujemy `Ecap=min(K*Xref²,Le*Icap²)/2` i λ=500/s. Dopuszczamy
napięcie w szynach spełniające

`u*i <= Rms*v²+Re(theta)*i²+lambda*(Ecap-E)`.

Jeśli propozycja przekracza tę półpłaszczyznę, kontroler rzutuje ją na
brzeg, dzieląc dopuszczalną moc przez i. W domenie E≤Ecap prawa strona
jest nieujemna, więc u=0 jest zawsze wykonalne; i=0 nie powoduje problemu.
Na E=Ecap mamy Edot≤0. Z E≥Kx²/2 i E≥Le i²/2 wynikają |x|≤Xref,
|i|≤Icap. Na θ=80 K z doboru Icap wynika θdot≤0, a przy θ=0 mamy θdot≥0.
Dla E(0)≤Ecap i θ(0)∈[0,80 K] jest to niezmienniczy obszar **ciągłego,
idealnie obserwowanego modelu**. Dowód nie zależy od rodzaju wejścia,
ale zależy od stałości dodatnich M/K/Le i poprawnego Re/Rth.

To inny, prostszy certyfikat niż elipsoida P24A. Ponieważ wspólna energia
musi ograniczać także energię samej indukcyjności, kryterium jest bardzo
konserwatywne dla wychylenia. Nie jest dowodem optymalności ochrony ani
możliwości wykonania obserwatora w obecnym miniDSP. Próbkowanie, opóźnienie,
błąd identyfikacji, nieznany stan początkowy i odbiór energii są osobnymi bramkami.

## Wynik kampanii

| Strategia | Największe |x|/Xref | Największe |i|/Icap | Największy przyrost θ [K] |
|---|---:|---:|---:|
| HP/LP i szyny | 2,908 | 4,179 | 69,864 |
| Sprzężenie prądowe 10 Ω | 2,821 | 2,806 | 64,212 |
| Bariera energii | 0,365 | 0,996 | 60,000 |

Maksima dotyczą różnych przypadków. Wysoki start 60 K jest wliczony;
6 s nie doprowadziło scenariuszy bez bariery do 80 K, ale to nie dowód
bezpiecznej pracy ciągłej. Bariera ma mniejsze poziomy sygnału, więc porównanie
nie oznacza tej samej głośności lub neutralnej ingerencji.

Największy ruch: C02 / 150 l / fazy Schroedera / same szyny: **24,427 mm**,
przy Xref=8,4 mm. Po przekroczeniu katalogowej dziedziny wynik jest testem
niewystarczalności ochrony w modelu; nie prognozą fizycznego ruchu, THD lub
uszkodzenia produktu. Nie stwierdzamy, że C11 lub C06 fizycznie grają lepiej.

![Przebiegi C02](../wyniki/p25c_przebiegi.png)
![Ruch i straty miedzi](../wyniki/p25c_ograniczenia.png)

## Wpływ temperatury przy tym samym napięciu

Dodatkowe 12 par przy 120 l: tor `rail`, start +60 K i samogrzanie versus
zimny liniowy układ Re0, **identyczne przycięte napięcie portu**.
Odnotowano zmianę RMS przyspieszenia przez pełne 6 s, nie zmierzony SPL:
C02 od −1,132 do −0,315 dB, C11 od −1,058 do −0,233 dB,
C06 od −0,984 do −0,259 dB. To łączny wpływ gorącego startu i przebiegu
Re(T), nie izolowana kompresja powstała wyłącznie podczas sześciu sekund.
Dane: `p25c_termiczne_porownanie.json`. Nie wyprowadzać z nich THD.

## Kontrole i niepewność

Dla wszystkich przebiegów całkowano osobno pracę portu, straty mechaniczne,
straty miedzi oraz odpływ ciepła i porównano z końcowymi energiami.
Zagęszczenie 24→48 kHz obejmuje wybranych świadków największego ruchu,
prądu/temperatury oraz trzech strategii. Obejmuje także zmianę dyskretyzacji
filtru i wejścia, nie wyłącznie błąd integratora.
Niezależnie napisane skalarne równania rozwiązano adaptacyjnym DOP853
przy tej samej interpolacji wejścia; nie jest to pomiar lub pełna niezależna
recenzja. Dokładne błędy i progi akceptacji w `p25c_podsumowanie.json`.
Dodatkowa kontrola przejściowa (2026-10-31): dwa świadki, w tym największy ruch i gorący start bariery, porównano z odrębnie zapisanym DOP853 na250 punktach do1,25 s. Maksymalna różnica skali Xref/Icap/80K/prędkości1m/s wynosi0,000816; nie ograniczano porównania do niemal zerowego końca wybrzmienia. Wynik `p25c_weryfikacja_przejsciowa.json`. Cały zbiór nie jest objęty dowodem błędu numerycznego między próbkami.

Niepewność tutaj to osie Vb i dwóch rodzin Rth/Cth/startu. Nie obejmuje
wszystkich niezależnych zaburzeń T/S, Mmd, paneli lub dynamiki materiału.
Sześć sekund nie identyfikuje wolnych biegunów termiki. Gwarancja
matematyczna bariery dotyczy idealnego modelu i ciągłego sterownika;
wyniki RK4 stanowią jej wybrane realizacje, nie dowód certyfikacji sprzętu.

## Decyzja i minimalna kalibracja

HP20 sam nie spełnia pełnej funkcji ochrony. Sprzężenie prądowe o skończonym
wzmocnieniu również nie zamyka ruchu. Zachować barierę jako konserwatywny
punkt odniesienia i rozwinąć obserwator/ochronę o większej wydajności.
RSS390HF-4 pozostaje rekomendacją warunkową; to badanie nie rozstrzyga
przewagi produktu nad C11/C06. Zamknięto zadany eksperyment P25C,
nie pakiety P22–P25 jako całość ani całą naukę możliwą bez urządzenia.

Przed nastawą sprzętową: zidentyfikować wzmocnienie DAC→port, szyny,
limity/reakcję prądową i zachowanie zwrotnej energii; Re(T), Rth/Cth
z nagrzewania i stygnięcia; impedancję w rzeczywistych Vb; model ruchu,
BL/Le i użyteczny skok. Zmierzyć opóźnienie/rekonstrukcję, sprawdzić
rozruch gorący i stan po awarii, a następnie testować przy małym napięciu
ze stopniowaniem oraz zapisem napięcia, prądu, temperatury i ruchu.
Bez tych danych bariera nie jest gotowym presetem miniDSP.

## Odtwarzanie

```
OPENBLAS_NUM_THREADS=1 python skrypty/p25c_czas_ochrona.py
OPENBLAS_NUM_THREADS=1 python skrypty/p25c_porownanie_termiczne.py
```

Wejście: `dane/konfiguracje/p25c_sygnaly_ochrona.json`.
Surowe agregaty 216 przebiegów: `wyniki/p25c_kampania.csv`.
Wersje i SHA: `wyniki/p25c_manifest.json`.
