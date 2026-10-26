# Raport 039 — P09C: ilość, położenie i straty wypełnienia

Stan: 2026-10-26. **Obliczenia geometryczne i symulacja**, uzupełnienie
[raportu 016](016_gaz_wypelnienie_i_granice.md) na polecenie użytkownika,
aby uwzględnić obliczenia wypełnienia skrzyni. Nie dobrano jeszcze produktu
i ilości wykonawczej. Zbadano 18 wariantów wyklejenia, 55 modeli warstwowych
oraz 17 820 punktów napędu dla 27 konfiguracji, w tym nowych SB.

## Wnioski do projektu

**Wynik modelu:** masę materiału należy podać razem z obszarem, grubością,
porowatością, mikrostrukturą i mocowaniem. Warstwy o tej samej masie mogą
mieć różne straty zależnie od położenia. Objętość zajęta przez porowaty
materiał nie jest objętością wypartego gazu: gaz pozostaje w otwartych porach.

**Rekomendacja badawcza:** końcowy projekt ma określać rodzaj materiału,
masę, geometrię, sposób utrzymania i wymagane prześwity przy koszu/wentylacji.
Nie zastępować tego jednym procentowym „bonusem litrów”. Wkłady sztywne
do regulacji Vb są osobnym elementem P20; włóknina nie zastępuje ich bilansu.
Wybór wypełnienia należy sprawdzić także po zmianie objętości regulowanej skrzyni.

## Dwa oddzielne eksperymenty

1. **Geometria wyklejenia pięciu lub sześciu ścian.** Rzeczywiste objętości
   rdzenia, obszaru porowatego, gazu i ciała stałego oraz masa. Naroża są
   policzone jednokrotnie. Wariant pięciu ścian pozostawia front bez wyklejenia.
2. **Propagacja 1D przez warstwę zajmującą cały przekrój.** Ten sam materiał
   i jego masa przy froncie, w środku albo z tyłu. To osobna geometria
   do badania położenia; nie jest symulacją całego wyklejenia pięciu ścian.

W obu użyto kontrolnych wymiarów wewnętrznych **460 × 640 × 460 mm**,
czyli 135,424 l przed odjęciem kosza, usztywnień i regulatora. Wymiary
powiązano z konfiguracją ramy P18C. Nie jest to finalny Vb netto prototypu.

## Jawne założenia materiału

Porowatość geometryczna phi=0,98. Gęstości suchego materiału
10/20/40 kg/m³; ciepło właściwe szkieletu Cp=1400 J/(kg K).
Są to **założenia rodzin**, nie karty konkretnych produktów lub tolerancje.
Zmiana gęstości przy stałej phi nie jest prawem zagęszczania jednej włókniny.

Model warstwowy wykorzystuje istniejący Zwikker–Kosten z prostymi
okrągłymi porami o promieniach 50/200/1000 µm, szkielet nieruchomy lub
wiotki oraz gęstość suchą 20 kg/m³. Promień poru nie jest średnicą włókna.
Źródło równań: wcześniej odczytana dokumentacja pierwotna
[COMSOL — Poroacoustics Models](https://doc.comsol.com/6.3/doc/com.comsol.help.aco/aco_ug_pressure.05.182.html),
SRC24; zakres weryfikacji oryginałów zapisuje
[rejestr P09/P10](../dane/zrodla/P09_P10_materialy_i_sorpcja.json).
Nie przeprowadzano nowej identyfikacji mikrostruktury.

## Masa i objętości: rachunek bez podwójnego odejmowania

Przy W/H/D i grubości t dla pięciu ścian:

    Vgeometry = W*H*D
    Vcore = (W-2t)*(H-2t)*(D-t)
    Vporous = Vgeometry - Vcore
    Vsolid = (1-phi)*Vporous
    Vgas = Vcore + phi*Vporous
    mdry = rho_dry_bulk*Vporous

Dla sześciu ścian ostatni czynnik Vcore wynosi D−2t. Masy nie wyprowadzano
z samej grubości ani z gęstości litego polimeru.

| Pięć ścian; rho_dry=20 kg/m³ | 25 mm | 50 mm | 75 mm |
|---|---:|---:|---:|
| Obszar materiału porowatego [l] | 32,043 | 58,960 | 81,128 |
| Masa sucha [kg] | 0,641 | 1,179 | 1,623 |
| Objętość ciała stałego [l] | 0,641 | 1,179 | 1,623 |
| Rzeczywista objętość gazu [l] | 134,783 | 134,245 | 133,801 |
| Veq: izotermiczne pory + adiabatyczny rdzeń [l] | 147,344 | 157,357 | 165,603 |
| Veq: skończone Cs, izolowany materiał + adiabatyczny rdzeń [l] | 146,834 | 156,418 | 164,312 |

Zbieżność liczb masy [kg] i wypartej objętości [l] w tej tabeli wynika
przypadkowo z wybranych rho_dry=20 kg/m³ i 1−phi=0,02; nie jest przelicznikiem
ogólnym. **58,96 l obszaru włókniny nie wypiera 58,96 l gazu.**
Porowatość oznacza tu dostępne, otwarte pory; zamknięte komórki wymagają
innego modelu i nie otrzymują automatycznie tego samego wyniku.

![Masa materiału, objętość gazu i oddzielne granice podatności](../wyniki/62_P09C_masa_materialu_i_objetosc_gazu.png)

## Co oznaczają podane Veq

W quasistatycznym modelu wspólnego ciśnienia, z **założonym adiabatycznym
rdzeniem**, równoległe podatności objętości sumują się:

    C = Vcore/(gamma*p0) + Vporous/Kporous
    Veq = gamma*p0*C
    Kporous_low,ideal = p0/phi
    Kporous_high = gamma*p0/phi

Stąd Veq_low,ideal=Vcore+gamma*phi*Vporous, a Veq_high=Vgas.
To granice wskazanego modelu, nie uniwersalna asymptota rzeczywistej
skrzyni przy dowolnych ścianach i wymianie ciepła. W rzeczywistym limicie
f→0 również gaz rdzenia może wymieniać ciepło ze ściankami.

Dla lokalnej pojemności gazu w porach i materiału:

    Cg = p0*phi*Vporous / [(gamma-1)*T0]
    Cs = mdry*Cp_solid
    Klow_pore_gas = p0*[1+(gamma-1)/(1+Cs/Cg)]

Przy wskazanych założeniach lokalne Cs/Cg≈33,06. Zmiana grubości przy
stałych phi/rho/Cp skaluje obie pojemności i nie zmienia ich stosunku.
Hgs i Hs0 pozostają nieznane: z samej pojemności nie znamy częstotliwości
przejścia ani wartości przy 20–80 Hz. Idealnie izotermiczne ścianki porów
w ZK i osobne skończone Cs to dwa eksperymenty; nie dodano ich efektów drugi raz.

## Położenie tej samej warstwy

Warstwa 50 mm przez cały przekrój 460 × 460 mm ma objętość obrysową
10,58 l i masę **0,2116 kg** przy rho_dry=20 kg/m³. Liczby te różnią się
od wariantu wyklejenia pięciu ścian. Dla a=200 µm, phi=0,98 i szkieletu
nieruchomego obliczono wejściowy opór akustyczny:

| Położenie tej samej warstwy | Re(Zin), 20 Hz [Pa·s/m³] | Re(Zin), 80 Hz [Pa·s/m³] |
|---|---:|---:|
| Przy froncie | 793,52 | 815,29 |
| W środku | 229,22 | 283,11 |
| Przy tylnej ścianie | 10,47 | 13,84 |

Wynik zależy od rozkładu prędkości i ciśnienia w komorze. Sam większy
opór wejściowy nie oznacza lepszego subwoofera; może wymagać większego
napędu i inaczej tłumić rezonans. Model 1D pomija rzeczywisty kosz,
niejednorodne wymuszenie i mody poprzeczne. Pierwszy poprzeczny próg
idealnego pustego przekroju wynosi około 373 Hz, lecz lokalne pola
zanikające przy koszu mogą mieć znaczenie również poniżej tej wartości.

![Ta sama warstwa w różnych miejscach — straty i ograniczenia napędu](../wyniki/63_P09C_polozenie_warstwy_i_naped.png)

Duży pik w lewym panelu dotyczy rezonansu osiowego około 268 Hz geometrii
kontrolnej, a nie nowego użytecznego pasma subwoofera. Mniejszy/większy pik
przy różnych położeniach nie jest samodzielnym rankingiem tłumienia skrzyni.

## Napęd: osobno przy tym samym napięciu i przy wspólnych limitach

Wykonano 55 modeli, w tym pustą komorę: 3 promienie × 2 szkielety ×
3 grubości 25/50/100 mm × 3 położenia + EMPTY. Każdy połączono z
27 konfiguracjami głośników, 6 częstotliwościami i dwoma budżetami
40 V RMS/12 A RMS oraz 60 V RMS/20 A RMS. Razem **17 820 punktów**.
Nie jest to powtórzenie kampanii 016: dodano położenie warstwy,
geometrię 640 mm i nowe SB.

SPL: **osobny sinus ustalony, RMS, idealne 2π/1 m**, limit katalogowego
Xpeak lub V/I. Brak limitu cieplnego, określonego dopuszczalnego czasu,
THD, pokoju, EQ, pracy dwóch subwooferów i ochrony dynamicznej.
Medium wynika z p0/T0/gamma/R jak w P09/P10, a mechanika T/S jest zamrożona.
Drobne różnice względem starszej rho/c nie są korzyścią wypełnienia.

Przykład C04, warstwa 50 mm/a200 µm/rigid, 40 V RMS/12 A RMS:

- Przy 20 Hz wiąże X: wszystkie trzy położenia dają tę samą granicę
  ruchu, mimo różnych strat i zapotrzebowania na napięcie. Wariant frontowy
  wymaga około 26,67 V RMS, tylny około 26,27 V RMS.
- Przy 80 Hz wiąże V: zmiana granicy względem pustej komory 1D wynosi
  około −0,106/−0,040/−0,013 dB dla front/środek/tył. Nie przenosić
  tego wyniku na inne promienie, głośniki lub wyklejenie boków.
- W tym ostatnim eksperymencie model daje około **425–434 W strat I²Re**.
  Nie potwierdza pracy ciągłej; Pe z innego protokołu nie jest automatycznie
  tym samym limitem strat. To uzasadnia połączenie z termiką i ochroną.

Załamania krzywych wynikają ze zmiany aktywnego limitu X/V/I.
Sprawdzono dodatkowo wąski obszar przejścia X→V około 32–33 Hz C04;
nie stwierdzono skoku równania, tylko szybkie przejście obwiedni.

## Niezależna propagacja i przypadki graniczne

Dokładną rekurencję warstw ZK sprawdzono **odrębną siecią objętości
skończonych p/Q**. Masa zespolona leży między węzłami, a po połowie
podatności komórki przypada na węzły końcowe. Zasilanie: Qin=1 m³/s jako
normalizacja liniowego portu, Qrear=0; nie jest realnym przepływem prototypu.

    Zedge = s*rho_eq*dx/A
    Ynode += s*A*dx/(2*K_eq)
    Qedge = (p_left-p_right)/Zedge
    Re(p_in*conj(Qin)) = sum Re(Zedge)*|Qedge|² + sum Re(Ynode)*|pnode|²

Wykonano **80 rozwiązań**, EMPTY i trzy położenia, częstotliwości
20/80/125/300 Hz, siatki 32/64/128/256/512. Największa względna różnica
zespolonego Zin na ostatniej siatce wynosi **1,45e−5** (około 0,00145%).
Nie jest to błąd fizycznego produktu ani certyfikat całego pasma.
Znormalizowana reszta mocy sieci jest poniżej 6,2e−12. Normalizacja używa
większej z modułu zespolonej mocy portu i mocy strat, z dolną skalą 1 W.
Przy zadanym Qin=1 liczbowo daje to użytą w kodzie skalę |p_in|;
nie dzielono przez małą różnicę dwóch mocy.

Ponadto sprawdzono:

- Brak materiału oraz pełne wypełnienie: położenie przestaje mieć znaczenie,
  różnice do 2,3e−16. Poprawiono wyznaczanie zerowych odcinków, aby
  odejmowanie zmiennoprzecinkowe nie tworzyło ujemnej długości ~1e−17 m.
- Niskoczęstotliwościową granicę sumy podatności przy 1e−6 Hz dla 54 rodzin:
  największa różnica względna około 1,44e−7. To sprawdzenie granicy modelu,
  nie propozycja pomiaru w tym paśmie.
- Re(Zin)≥0 na badanej siatce. Bilans wejścia napędu, Re·I², efektywnego
  Rms i portu komory ma względną resztę poniżej 8,9e−16. Nie identyfikuje
  to oddzielnych źródeł grzania przetwornika.

Sieć FV sprawdza propagację przy tych samych właściwościach ZK; nie jest
niezależnym pomiarem lub identyfikacją porów. Radialną dyfuzję materiału
kontrolowano wcześniej w 016. Nie deklarujemy sprawdzenia wszystkich
geometrii, wszystkich możliwych włóknin lub pełnej poroelastyczności Biota.

## Braki danych i następny krok

Do wyboru konkretnego materiału nadal potrzebne są: rzeczywista porowatość,
oporność przepływu i jej zależność od upakowania, mikrostruktura lub
parametry równoważnego ośrodka, Cp, stan szkieletu, sposób mocowania,
objętości kosza/ściągów/wkładów oraz prześwit wentylacyjny wybranego głośnika.
Nie wyprowadzono ich z samej deklaracji AFr≥5 kPa·s/m² lub lambda_D.

**Najbliższy krok tej gałęzi:** po zamrożeniu geometrii i zakresu regulacji
powiązać rodzinę materiału z przestrzennym polem P21 i napędem/ochroną.
Główny krok konstrukcyjny pozostaje lokalne połączenie stałego frontu.
Wypełnienie musi wejść do końcowego porównania, bilansu netto i rekomendacji.

Artefakty:
[wejścia](../dane/konfiguracje/p09c_ilosc_i_rozmieszczenie_wypelnienia.json),
[geometria i masa](../wyniki/p09c_geometria_masa_i_podatnosc.csv),
[warstwy](../wyniki/p09c_warstwy_i_straty.csv),
[napęd](../wyniki/p09c_naped_i_wypelnienie.csv),
[zbieżność niezależnej sieci](../wyniki/p09c_niezalezna_siec_i_zbieznosc.csv),
[podsumowanie i hashe](../wyniki/p09c_podsumowanie.json).

Odtworzenie bez dawnych kampanii:

    OPENBLAS_NUM_THREADS=1 python3 skrypty/analiza_ilosci_i_rozmieszczenia_wypelnienia.py
