# Raport 077 — P30D: 50-mm mata, krótsze wkłady, montaż z marginesem oraz objętość i drgania

**Data 31.10.2026. Status: 7 wariantów bryłowych i 9 prób obwiedni montażowej, obliczenia wzorcowe 2D/3D i stres objętości.** Wyniki potwierdzają wyłącznie właściwości przyjętych modeli, nie nośność całej obudowy ani gotowość CNC.

## Dlaczego P30D

Poprzedni raport 076 (P30A–C) zaproponował 1040 × 430 × 500 mm z matą 40 mm: modelowa maksymalna głębokość 486 mm, nominalnie około 102/122/152 l. Tę decyzję warto skonfrontować z alternatywą **zachowującą pełną warstwę 50 mm**, ponieważ absorpcji akustycznej zmniejszonej warstwy nie wykazano. Oparto się na geometrii P20D (raport 057) i znanym ryzyku podatności wręg P18E (raport 059).

## Nowa rodzina rozwiązań: siedem wariantów

Zachowano front MDF 44 mm, inne ścianki 22 mm, boczne rozmieszczenie wręg oraz wysokość 500 mm. Użyto 50-mm maty przy tylnej ścianie dla wszystkich wariantów. Zmieniono tylko głębokość ośmiu tylnych wkładów z 150 na 130/120/110 mm oraz przesunięto cztery małe wkłady w stronę frontu o 10/15/20 mm. Wariant 1000 × 440 mm bez zmian jest kontrolą względem P20D. Bilans netto odejmuje modelową wyporność głośnika 5 l, osprzęt 0,175 l, objętość wręg i ciała stałego włókniny; wnętrze porowate pozostaje gazem.

| W × D korpusu [mm] | Mata | Maks. modelowa głębokość z osłoną | Pozostały margines | Najbliższa nominalna obj. 100 / 120 / 150 l |
|---|---:|---:|---:|---|
| 1000 × 440 | 50 mm | 496 mm | 4 mm | 100,11 / 120,36 / 149,61 l |
| 1010 × 430 | 50 mm | 486 mm | 14 mm | 100,79 / 119,78 / 149,63 l |
| **1020 × 425** | **50 mm** | **481 mm** | **19 mm** | **100,12 / 119,92 / 150,16 l** |
| 1030 × 425 | 50 mm | 481 mm | 19 mm | 101,75 / 119,75 / 149,99 l |
| 1040 × 430 | 50 mm | 486 mm | 14 mm | 103,96 / 120,16 / 150,01 l |
| 1050 × 425 | 50 mm | 481 mm | 19 mm | 105,02 / 119,87 / 150,02 l |
| 1055 × 420 | 50 mm | 476 mm | 24 mm | 105,23 / 120,08 / 150,20 l |

**Nowy faworyt do dalszego CAD/FEM:** 1020 × 425 × 500 mm. To pierwszy z badanej rodziny, który łączy pełną tylną matę 50 mm, wszystkie trzy litraże blisko celów bez dodatkowych elementów oraz prawie 20 mm modelowego zapasu głębokości. Jest szerszy od bazowego o 20 mm; nie wykazano miejsca w docelowym pokoju.

## Eksperyment montażowy: nie tylko nominalne 3 mm

Niezależnie od bilansu litrów użyto istniejącego modelu trójwymiarowych brył AABB i sprawdzanych ciągle odcinków ruchu translacyjnego. Przetestowano 20 modułów, uwzględniając już zamontowane. P30D poszerza obwiednię kolizji ponad domyślne 3 mm.

| Korpus | Obwiednia +3 mm | +4 mm | +5 mm | +6 mm | +8 mm |
|---|---|---|---|---|---|
| 1000 × 440 | 20/20 | 8/20 | — | — | — |
| 1010 × 430 | 20/20 | — | — | 20/20 | — |
| **1020 × 425** | **20/20** | **20/20** | **20/20** | **20/20** | **0/20: 12 statycznych kolizji** |

8-mm wariant nie mieści się już w modelu. Nie oznacza to, że realna śruba 6-mm lub narzędzie będą pasować; należy je narysować jako pełne bryły i powtórzyć analizę ze swobodą obrotu. Wariant bazowy przy +4 mm utracił drogę już na dziewiątym module w użytym grafie. To porażka tej reprezentacji ścieżek, a nie matematyczny dowód niemożliwości dowolnego montażu.

## Objętość, zmienność komponentów i masa

Dla 1020 × 425 mm stany nominalne wymagają odpowiednio: 16 dużych + 4 małe (100,12 l), 12 dużych + 0 małych (119,92 l), 1 duży + 0 małych (150,16 l). Przekroczenie nominalnej liczby modułów może być skorygowane po fizycznej identyfikacji wyporności. Scenariuszowy niezależny stres ±2 mm wnętrza, ±5% wręg, 2–8 l rzeczywistej efektywnej wyporności głośnika, 0,05–0,30 l okuć, gęstości maty i wymiarów modułów ±0,5 mm daje:

| Nominał | Modelowy przedział przy zakładanych skrajnościach |
|---|---|
| 100,12 l | 94,22–106,00 l |
| 119,92 l | 114,25–125,57 l |
| 150,16 l | 144,83–155,48 l |

To **nie** tolerancja wykonawcza ani przedział ufności rzeczywistej skrzyni. Trzeba zmierzyć przetwornik/wkłady i skalibrować objętości.

Masa szacunkowa przy MDF 730 kg/m³, po odjęciu cylindrycznego otworu frontu i uwzględnieniu zamkniętych pustych modułów o ściance 8 mm, wynosi około: **51,9 kg** dla konfiguracji 100 l, **47,2 kg** dla 120 l i **40,2 kg** dla 150 l. **Bez głośnika, maskownicy, wzmacniacza, okuć i wykończenia.** Dla MDF 650–800 kg/m³ masa jeszcze się zmienia. To argument za sprawdzeniem przenoszenia, połączeń, orientacji i mocowania 20 ciężkich modułów.

## Płyta i akustyka — tylko niezależne wskaźniki

Dla nieperforowanego pola górnego 426 × 359 mm, idealnie swobodnie podpartego na obwodzie (SSSS), model Kirchhoffa z E=2,1 GPa, ν=0,3, ρ=730 kg/m³, MDF 22 mm przewiduje **f11≈235,4 Hz** i środkowe ugięcie **45,0 μm przy stałym nacisku 1000 Pa**. W kontrolnym wcześniejszym 426 × 374 mm jest to f11≈224,5 Hz oraz 49,5 μm. Szereg Naviera (17→33 składniki nieparzyste) zmienia ugięcie o mniej niż 0,0001 μm.

**Te liczby nie są pierwszą częstotliwością własną gotowej skrzyni.** Zintegrowana, choć zredukowana analiza P18E uzyskała około 143 Hz na starej geometrii, co dowodzi, że realne podpory są podatne; przy zmianie geometrii P18E musi zostać uruchomiony ponownie. Próg wytrzymałości spoiny, rezonanse elementów mocujących, promieniowanie paneli, grawitacja i zmęczenie są otwarte.

Idealna pierwsza częstość pustej sztywnej komory zmienia się z około **179,4 Hz (1000×440)** do **175,7 Hz (1020×425)**. Nie jest to rezonans rzeczywistej komory z 11 wręgami, matą, wkładami i źródłem kołowym; żadnej zweryfikowanej charakterystyki 20–80 Hz ani THD nie można z tego wywieść.

## Bramki przed jakimkolwiek CNC

1. Pełna geometria CAD: front i kosz, odporny grill, śruby, gasket, stopy, terminal, przewody, rzeczywiste złącza i narzędzia; zweryfikować obrys całego urządzenia ≤500 mm z marginesem.
2. Sprawdzić możliwość serwisu 20 modułów z **rzeczywistymi uchwytami i zatrzaskami**, a następnie projekt spoin i trwałego blokowania wkładów (pion/poziom).
3. Pełna dynamiczna analiza całej ramy (FEM), geometrii wręg, frontu z otworem i styków, z materiałem MDF zmierzonym, nie samym E fabrycznym.
4. Ponowny przestrzenny port gazu P21G na zmienionej geometrii 100/120/150 l; sama zachowana grubość maty nie oznacza zachowanej akustyki.
5. Weryfikacja objętości i szczelności na fizycznym prototypie oraz próby akustyczne/prądowe/termiczne z bezpiecznym wysterowaniem.

**Nie zamrażać dokumentacji CNC ani nie zatwierdzać ochrony głośnika z samych tych symulacji.**

## Odtwarzanie

Uruchomić z katalogu repozytorium: **python skrypty/p30d_mat50_geometria_montaz.py**. Wymaga numpy i istniejącego skryptu **skrypty/p30a_robust_geometry.py**. Program zapisuje wyniki jako **wyniki/p30d_50mm_multimodel_20261031.json**.