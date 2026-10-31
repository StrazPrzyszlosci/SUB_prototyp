# Raport 065 — P21F: przestrzenne mody gazu i podatne pola ścian

**Data: 31 października 2026.**
**Status: wykonany eksperyment z modelem zastępczym oraz kontrolami algebraicznymi.**
To **nie** jest pełny model MES/FV docelowego P20D, nie pomiar i nie certyfikat zniekształceń, SPL ani gotowości wykonania.

## Pytanie i hipoteza

P21D (raport 060) rozwiązuje przestrzenne pole gazu z *niepodatnymi* wręgami/wkładami, a P21E (raport 064) jest wzajemnie sprzężonym modelem *podatnych* ścian, ale z jednorodnym ciśnieniem. Jak zmienia się odpowiedź napędu, gdy w jednym **jawnym modelu zastępczym** dopuścimy wiele modów akustycznych, lokalizację membrany i trzy ruchome pola ścian?

Nie wolno dodawać wyników P21D i P21E jako dwóch niezależnych korekt w dB. Nowy port musi być wzajemny, energetycznie pasywny, z tym samym ruchem/polem ciśnienia w równaniach głośnika i ścian.

## Geometria, źródło i wyraźne uproszczenie

P20D podaje wnętrze prostokątnego korpusu **956 × 374 × 456 mm** i otwór membrany przesunięty w poziomie. Tutaj używamy **pustego prostopadłościanu** o tych wymiarach do zdefiniowania przestrzennych postaci Neumanna.

**To nie jest geometria wnętrza gotowej skrzyni.** W rzeczywistym P20D wręgi, hermetyczne wkłady i wypełnienie zajmują miejsce, zmieniają topologię i warunki brzegowe. W obliczeniach P21F przyjmujemy 100/120/150 l **wyłącznie do współczynnika ściśliwości modu zerowego** przy zachowaniu tej samej geometrii postaci przestrzennych. To hybrydowa, scenariuszowa parametryzacja; dla danych stanów wkładów nie jest ona dokładnym rozwiązaniem równania fali i **nie upoważnia do ilościowego przypisywania wykresów fizycznej skrzyni**. W szczególności model może pomijać lokalne rezonanse szczelin między modułami.

Membrana to *dysk o powierzchni katalogowego Sd*, na przednim boku \`y=0\`, o środku \`x=0,209 m\` albo \`0,478 m\`, \`z=0,228 m\`. Projekcję na kosinusowe mody wyliczono przez całkę po całym dysku, z analitycznym czynnikiem \`2 J1(k⊥a)/(k⊥a)\` (dla \`k⊥=0\`: 1); dysk musi w całości mieścić się w powierzchni frontu. Ruch ścian reprezentują przestrzennie uśrednione *tłoki na fragmentach powierzchni*, **a nie rzeczywiste mody z MES**: \`x=0\`, \`x=Lx\` oraz \`z=Lz\`, każdy na centralnych 80% rozpiętości dwóch współrzędnych stycznych.

Model P21E przyjmuje sumaryczną podatność statyczną dwóch paneli \`Cw=3,8069496·10^-8 m³/Pa\` z założenia P18E. W P21F porównano: idealną sztywność; jeden równoważny stopień swobody na dwóch symetrycznych polach; trzy pola o udziałach podatności 0,375/0,375/0,25; te same pola przy podwojonej podatności. Częstotliwości modelowych pól: 143,30533/152,44/123 Hz, tłumienie \`ζ=0,03\`. Tłumienie akustyczne \`ζa=0,025\` jest przyjętym scenariuszem, **nie** zidentyfikowaną własnością konkretnej maty.

## Model: wzajemność i bilans energii

Mody komory znormalizowano w przestrzeni:

\`phi_n(x,y,z)=prod_j sqrt(2-[n_j=0]) cos(n_j*pi*r_j/L_j)\`,
\`omega_n=c*pi*sqrt((nx/Lx)^2+(ny/Ly)^2+(nz/Lz)^2)\`.

Wektor \`b_n\` zawiera *średnie* wartości \`phi_n\` na membranie i trzech polach. Dla prędkości objętościowych \`Q=[Sd*x',-y1',-y2',-y3']\` (ściany poruszają się na zewnątrz) oraz \`s=jω\`:

\`p=(A(s)/s)Q\`, gdzie

\`A(s)=K0 [1 1^T + sum_{n!=0} b_n b_n^T * s²/(s²+2ζa ω_n s+ω_n²)]\`,
\`K0=rho*c²/Vb\` [Pa/m³].

**Uwaga:** mody reprezentują równoważny prostokątny port *bez* wręg P21D, a nie rozwiązanie ich przestrzennego modelu.

\`Zmx(s) x + Sd*p_driver = BL*i\`, \`Zmj(s) yj = p_j\`,
\`(Re+s Le)i + BL*s*x = U\`, z
\`Zmx=1/Cms + Rm*s+M*s²\` i \`Zmj=Kj+Rj*s+Mj*s²\`.

Z T/S pochodzą \`Cms\`, skuteczne \`M\` i \`Rm\` oraz \`BL\`. W modelu **nie dodano** drugi raz masy powietrza do Mms. Wzajemność portów wynika z symetrycznych iloczynów \`b_n b_n^T\` i pary BL w SEM oraz sile.

**Bilans mocy RMS** dla 1 V RMS:

\`Re(U conj(i))=Re|i|²+Rm|x'|²+sum_j Rj|yj'|²+Re(Q^H p)\`.

Rozdzielona strata akustyczna modalna:

\`Re(Q^H p)=K0 sum_{n!=0} Re[s/(s²+2ζaω_n s+ω_n²)] |b_n^T Q|² >= 0\`.

Mod zerowy nie wnosi strat, a jego iloczyn pracy jest w tym modelu czysto bierny.

Warto zauważyć, że samo potwierdzenie energii **nie potwierdza** prawidłowej geometrii, kształtów rzeczywistych paneli ani danych materiałowych.

## Wykonany eksperyment

**52 272 obliczenia:** 3 kandydaci (C02 Dayton RSS390HF-4, C11 Dayton RSS390HE-22 szeregowo, C06 STX W.32.800.8.FCX) × 3 objętości (100/120/150 l) × 2 przesunięcia membrany × 4 modele ścian × 6 obcięć przestrzennych \`nmax=0..5\` × 121 częstotliwości 20–80 Hz co 0,5 Hz.

Przy \`nmax=0\` uwzględniono wyłącznie jednolite ciśnienie. Przy \`nmax=5\` uwzględniono **215 przestrzennych modów** (oprócz zerowego); każdy indeks kartezjański od 0 do 5. Wyniki 1 V RMS są amplitudami małosygnałowymi. Poniższe zakresy odnoszą się do skończonej siatki, a **nie do maksymalnego poziomu SPL** ani do głośności porównywanych przetworników.

### Wybrany wariant: C02, 120 l, źródło x=209 mm

| Założenie ścian | Zakres zmian amplitudy prędkości względem sztywnej komory 0D, 20–80 Hz |
|---|---:|
| Sztywne; tylko przestrzenne mody gazu | −0,4460…+0,0999 dB |
| Jeden modelowy tryb podatnych ścian | −0,4937…+0,2297 dB |
| Trzy podatne pola (nominalne) | **−0,4995…+0,2298 dB** |
| Trzy pola, 2× większa podatność | −0,5476…+0,3482 dB |

![Wpływ modelowej przestrzennej komory i trzech podatnych pól na amplitudę ruchu trzech kandydatów](../wyniki/105_P21F_mody_i_panele.svg)

Wykres zawiera 39 jawnie zapisanych świadków z siatki 0,5 Hz (co 5 Hz dla trzech kandydatów), a nie wszystkie 52 272 punkty.

### Cały skończony zbiór (wszyscy kandydaci, objętości, położenia)

| Wariant | Minimum Δv | Maksimum Δv | Największa bezwzględna przestrzenna korekta względem odpowiedniego nmax=0 |
|---|---:|---:|---:|
| Sztywny | −0,5386 dB | +0,1304 dB | 0,5386 dB |
| Jeden tryb ściany | −0,6067 dB | +0,3187 dB | 0,5364 dB |
| Trzy pola | −0,6152 dB | +0,3189 dB | 0,5427 dB |
| Trzy pola 2× | −0,6825 dB | +0,4938 dB | 0,5482 dB |

To porównanie *z jedną sztywną komorą 0D przy tym samym katalogowym T/S*, a nie rozkład błędu rzeczywistego P21D.

## Weryfikacja i kontrola zbieżności

- **2178 porównań** granicy \`nmax=0\` i pojedynczego trybu z analitycznym równaniem P21E: maksymalny względny błąd \`7,18·10^-16\`.
- Równania wymuszają zachowanie elektrycznego i mechanicznego bilansu energii: największa względna reszta \`7,36·10^-15\`.
- Niezależna modalna suma strat i \`Re(Q^H p)\`: największa względna reszta w skali mocy wejścia \`3,35·10^-16\`.
- **0/52 272** ujemnych strat mocy akustycznej przekraczających tolerancję \`10^-12 W\`.
- Na pełnej siatce \`nmax=4 → 5\` najwyższa zmiana amplitudy prędkości: **0,02398 dB**. **Nie można jeszcze ogłaszać ścisłej zbieżności.**
- Dodatkowo **288 świadków** dla 20/40/60/80 Hz i wszystkich kombinacji 3 kandydatów × 3 litraży × 2 miejsc × 4 scenariuszy: największe zmiany \`5→6: 0,01529 dB\`, \`6→7: 0,00510 dB\`, \`7→8: 0,00615 dB\`. Zbieżność nie jest monotoniczna, więc nie ma wiarygodnej ekstrapolowanej granicy błędu całego pasma.

Sprawdzono wzajemność i bilans *algebraicznego modelu*. Nie wykonano niezależnego rozwiązywania 3D FV P21D ze sprężystymi warunkami brzegowymi, prób siatek MES ani walidacji eksperymentalnej.

## Znaczenie dla decyzji projektowej

W tej jawnie założonej rodzinie przestrzenne składowe pola dają wpływ na napęd porównywalny lub większy niż dodanie dwóch/trzech podatnych pól. **Nie wolno zatem traktować „bonusowych litrów” ścian P21E jako pełnego opisu nowej skrzyni.**

Jednocześnie nie ma podstaw do odrzucenia C02 ani wskazania innego końcowego zwycięzcy. Różnice są modelowe, połączenie wybranych danych źródłowych z arbitralnymi kształtami ruchu paneli nie rozstrzyga konstrukcji i **nie uwzględnia kosztów**.

**Kolejna istotna bramka badawcza:** zastąpić pustą komorę prostokątną przestrzennym P21D **z rzeczywistymi obiektami P20D**, zaimplementować wzajemne porty ciśnienia na kilku powierzchniach, a potem połączyć z wielomodową mechaniką ramy i paneli, uwzględniając warunki podparcia P18E. Sprawdzić bilans, niezależną dyskretyzację, zagęszczenia oraz granice 0D; osobno dopiero dodać DSP P25E i termikę.

## Pliki i odtwarzanie

- [Kod kampanii](../skrypty/p21f_mody_gaz_panele.py), [jawna konfiguracja](../dane/konfiguracje/p21f_mody_gaz_panele.json).
- [Podsumowanie wyników](../wyniki/p21f_podsumowanie.json), [39 jawnych świadków](../wyniki/p21f_swiadkowie.csv), [wykres SVG](../wyniki/105_P21F_mody_i_panele.svg).
- [Kontrola wyższych modów](../skrypty/p21f_wysokie_mody.py).

W repozytorium znajdują się kod i agregaty. Główna kampania po uruchomieniu generuje **pełne CSV 52 272 punktów** (\`wyniki/p21f_kampania.csv\`), zestaw porównawczy 8712 punktów (\`wyniki/p21f_porownanie.csv\`), pełny JSON agregatów i manifest SHA-256. Skrypt kontroli generuje \`wyniki/p21f_wysokie_mody.json\`. Dużych tabel nie dołączono do PR; reprodukcja wymaga lokalnego uruchomienia i danych T/S dostępnych w repo. P21F nie zamyka fizycznej walidacji obudowy.
