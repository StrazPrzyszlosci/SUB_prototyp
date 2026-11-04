# Macierz wymagań i dowodów

Wydanie 0.1, 2026-10-23. U = wymaganie użytkownika, P = propozycja,
O = otwarte. Akceptacja briefu nie oznacza akceptacji dowolnych liczb modelu.

| ID | Wymaganie | Status | Dowód lub sposób weryfikacji | Etap |
|---|---|---|---|---|
| W01 | Pierwszy prototyp sealed, regulowany litraż | U | Bilans objętości i projekt modułów | R3/R5 |
| W02 | Szerokie porównanie 12″ i 15″, w tym STX | U | 24 modele / 11 producentów, 12 576 scenariuszy; raport 010, nie finalny ranking | R1/R2 |
| W03 | Dane producentów i krytyczny przegląd opinii każdego kandydata | Częściowo | 24 zestawy modelowe, 24 audyty opinii; braki pomiarów i tożsamości wariantów jawne | R1 |
| W04 | Sensowny kompromis 20 Hz/headroom 20–40 Hz | U, liczby O | Pasma SPL, Xpeak, napięcie, THD i kompresja po budowie | R2/P2 |
| W05 | Neutralność i niski szum, również cicho | U, progi O | Gain staging i dokumentacja elektroniki; późniejsze pomiary | R4/P2 |
| W06 | Referencje ADAM Audio średniej/wyższej półki | U-009: Sub12/Sub15 zatwierdzone | Progi liczbowe otwarte; referencje monitorów odłożone | R0 |
| W07 | Główna ocena sweet spot 2,5–3 m | U | Plan ustawienia, późniejsze pomiary z pozycją mikrofonu | R0/P2 |
| W08 | Sąsiednie punkty tylko diagnostyczne | U | Badanie wrażliwości, bez optymalizacji całej kanapy | P2 |
| W09 | Brak narzuconego budżetu;głębokość zewnętrzna maksymalnie500mm | U-026 | Limit zastępuje wcześniejszy brak ograniczeń gabarytów;W/H otwarte,nowa geometria do obliczenia | R3/P18–P21/P29 |
| W10 | Zewnętrzny wzmacniacz, DSP, zasilacz | U | Schemat i dokumentacja mechaniczna | R4/R5 |
| W11 | Gotowy miniDSP, minimum 8 niezależnych wyjść docelowo | U | Routing i instrukcja konkretnej wersji | R4 |
| W12 | Moduły klasy D, dopasowanie napięcia/prądu i ochrony | U | Z(f), limity, dokumentacja zasilacza, chłodzenie | R4 |
| W13 | Front stały, niedemontowalny, pod jeden wybrany przetwornik; regulowana objętość | U-021 | Stałe połączenie front–korpus, klej/nośność i bilans Vb. Wcześniejszy wymienny front zastąpiony decyzją użytkownika | P19/P20/R3 |
| W14 | Przygotowanie elementów MDF do obróbki CNC | U | [Kwestie technologiczne do uzgodnienia](WYKONAWCA_CNC.md) | R3/R5 |
| W15 | Osłona membrany, stabilność, serwis | U | Rysunek mechaniczny i późniejszy odbiór montażu | R5/P1 |
| W16 | Docelowo 2 subwoofery i monitory aktywne 3-drożne | U | Schemat 8 torów i pozostawiony zakres podziału | R4/P3/P4 |
| W17 | Powtarzalność i kalibracja w różnych pokojach | U, przyszłe | Dokumentacja wersji i pilotaż w kilku lokalizacjach | P5 |
| W18 | Teraz wyłącznie badania do budowy | U-004 | Plan R0–R5; brak zleceń wykonawczych | Bieżący |
| W19 | Tor pomiarowy wybrać po budowie | U-002 | Brak bieżącej listy zakupowej aparatury | P2 |
| W20 | Pomiary wyłącznie w pokoju | U-003 | Wyniki oznaczone in-room; ograniczenia oddzielenia urządzenia | P2 |
| W21 | Opinie właścicieli i konstruktorów | U-005 | [Rejestr doświadczeń](baza_wiedzy/08_opinie_i_ocena_dowodow.md) | R1 |
| W22 | Pokój około 4,6 × 3,7 × 2,5 m; front 3,7 m | U-016 | [Konfiguracja i osie](dane/konfiguracje/pokoj_odsluchowy.json); geometria przybliżona | P26/P27 |
| W23 | Dwa subwoofery w realnych miejscach przy monitorach | U | Sprawdzenie dwóch gabarytów, prześwitów i odległości 2,5–3 m; brak swobody przód/tył | P18–P21/P27 |
| W24 | Jeden głośnik i jedna obudowa z obliczonym połączeniem klejowym | U | Wynik integracji całego programu, obecnie otwarte | P19/P29 |
| W25 | Końcowy PDF po badaniach możliwych bez sprzętu | U | [Macierz 30 pakietów](PROGRAM_30_BADAN.md); nie zastępować braków wynikami fikcyjnymi | P30 |
| W26 | Ustawienie pionowo lub poziomo w zabudowie | U-026 | Sprawdzić dostęp,mocowanie,podparcie i prześwity w obu orientacjach | P18–P21/P27 |
| W27 | Głośnik może być przesunięty;preferowany środek jednej z połów frontu | U-026,preferencja | Położenie uzgodnić z koszem,wzmocnieniami i regulacją;nie zakładać centralnego otworu | P18/P21/P29 |
| W28 | Rozszerzenie badań: pojedynczy duży głośnik vs 2 × 10″ lub 2 × 12″ w jednej zamkniętej obudowie, także para izobaryczna | U-2026-11-02, badanie alternatyw | Raport 109, 3168 scenariuszy i audyt 60 l izobarycznie / 120 l pojedynczo; nie zastępuje jeszcze W13/W24 w finalnej konstrukcji | P43/P29/P18–P21 |
| W29 | Analiza ceny dwóch koszy w odniesieniu do Daytona oraz pełnego kosztu dwóch docelowych subwooferów | U-2026-11-02, kryterium dodatkowe | Ceny jednostkowe z datą i URL; oddzielnie BOM wzmacniacza, DSP, frontów, sprzęgającej komory izobarycznej i montażu; bez automatycznego uznania najtańszego kosza | P43/P29 |

| W30 | **Bramka pierwotnego briefu:** neutralność, niski szum, czysty headroom i niskie THD/IMD 20–40 Hz w pokoju 4,6×3,7×2,5 m, jeden sweet spot w odległości 2,5–3 m. Cena jest kryterium WTÓRNYM; odniesienie do ADAM Sub12/Sub15. | U, progi O | B12-06: audyt zgodności; do wykonania pomiary THD/kompresji oraz model i kalibracja 2 subów z monitorami | P26–P30/B12-06 |
| W31 | **W13/W24 pozostają bazową architekturą: jeden głośnik i jedna obudowa; finalnie dwa osobne subwoofery i 6 kanałów monitorów.** Para 2×STX w jednej skrzyni to wyjątek porównawczy; przy docelowych dwóch skrzyniach oznacza 4 kosze, nie 2. | U, wariant C05 w badaniu | B12-06: porównanie Vd, footprint, fizycznych kanałów, założeń pokojowych; brak kwalifikacji akustycznej | B12-06/P29 |
| W32 | Wymóg 500 mm głębokości dotyczy pełnego urządzenia z maskownicą i terminalem; geometria 2×STX z B12-05 ma tylko hipotetyczne 0,5–2,5 mm zapasu. | U, mechanika O | B12-05 i B12-06; przed CNC rzeczywisty kosz, złącza, przegląd FEM spoin, grawitacja w obu orientacjach | B12-06/P18–P21 |

| W33 | B12-07: **dwie fizyczne skrzynie** ze sterowaniem niezależnym przy monitorach w docelowym 4,6×3,7×2,5 m, a nie dwa kosze we wspólnej obudowie; odrzucać nominalnie kolidujące pozycje źródeł. | U, pozycje O | 27 modelowych wariantów A/B/D; hipotetyczne C przecina ściany. Przed wyborem wymagane wymiary mebli/monitorów oraz pomiar i model w sweet spocie | P26/B12-07 |
| W34 | Porównanie z ADAM Sub12/Sub15 musi dotyczyć tych samych pasm, dystansu, THD, czasu trwania i maksymalnego poziomu; katalogowy globalny SPL nie dowodzi 20-Hz parytetu. | U, progi O | Zweryfikowano deklaracje producenta 22/20 Hz, ≥115/≥120 dB; brak równoważnych danych 20–40Hz. Sub15 głębokość 525 mm, jako wzorzec klasy. | B12-07/P29 |

| W35 | Podstawa konstrukcji pierwszego prototypu C02 to korpus P30E 1020×425×500 mm z matą 50 mm i regulacją 100/120/150 l; korpus nie jest pełnym gabarytem urządzenia. | U, obwód O | B12-08: 160 scenariuszy wystawania; bez pomiaru maskownicy i terminala brak dopuszczenia CNC. | B12-08 |
| W36 | Prawdziwy tor siły 8 śrub Daytona → nośnik/ramę → MDF i wręgi musi być projektowalny, serwisowalny i kwalifikowalny materiałowo; sam cienki pierścień nie jest dowodem nośności. | U, złącze O | B12-08: 2232 przesiewy, brak przecięcia przy hipotetycznym luzie 1 mm i mostku 2 mm dla Ø6,5; konieczny CAD kosza + próby złączy. | B12-08/09 |
| W37 | Dobór kandydata nadal jest uzależniony od rzeczywistych THD/IMD, chłodzenia i czystego SPL 20–40 Hz w pokoju; C11 ma alternatywną przewagę w odmiennym scenariuszu Pcu. | U, pomiary O | Audyt P29A–D/B12-08: C02 wstępnym faworytem platformy, nie ostatecznym zwycięzcą. | B12-08/P29 |

| W38 | **Każdy element konstrukcji i osprzętu subwoofera ma własny paszport materiałowy:** zastosowanie, materiał bazowy i warianty, dane z kart lub hipotezy, obciążenia, masa/sztywność/nośność, powiązanie z bilansem netto i statusem kwalifikacji. Nie zastępować nieznanych parametrów fikcyjnymi wynikami. | U-2026-11-03; spełniono ewidencję 35/35, NIE kwalifikację wytrzymałościową | [K10 rejestr 35 części](dane/k10_rejestr_materialow_czesci_obudowy.json), [raport materiałowy](raporty/K10_paszport_materialowy_wszystkich_czesci.md), [obliczenia K10](wyniki/k10_wyniki_przesiewu_materialow.json); 0/35 zatwierdzonych do wykonania. Zmiana materiału/grubości wymaga ponownego P30E/K07 i MES, doboru kleju, spoin, ognioodporności i akustyki. | K10/P19/P30E/P34/P36/P37 |


| **W39** | **Przygotowanie dokumentacji dla przyszłego CNC wymaga wspólnego parametrycznego modelu 3D oraz listy każdej formatki z materiałem, numerem, położeniem i statusem kwalifikacji.** Fabryczne Ø6,5 mm w koszu Daytona nie określa średnicy otworów w MDF. Ostateczne rysunki CNC/DXF wolno wydać dopiero po zatwierdzeniu złączy, montażu, zamków, tolerancji, grilla, osprzętu i nośności. | U-2026-11-04; referencyjna ewidencja 138/138 spełniona, **produkcja 0/138**, brak zwolnienia do CNC | [K15: generator złożenia](skrypty/k15_pre_cnc_model.js) · [model 3D](dokumentacja/K15_p30e_zlozenie_parametryczne_NIE_CNC.scad) · [138 formatek CSV](wyniki/k15_p30e_przed_CNC_138_elementow.csv) · [raport i bramki](raporty/K15_parametryczne_zlozenie_i_zestawienie_przed_CNC.md). 7+11+120 elementów, trzy stany objętości; brak łączników i ścieżek narzędzi. | K15/P30E/K02/K14 |

| **W40** | Wszystkie **20 wymiennych wkładów litrażowych** muszą mieć dodatni, kwalifikowany tor siły z wkładu do szkieletu, podparcie w kierunku grawitacji, blokadę przy odwróceniu i transporcie, odporność na drgania i demontaż przez otwór kosza. **Żaden wkład nie może pozostawać jako niezamocowana bryła w przestrzeni.** Mocowania nie mogą bez weryfikacji przecinać tylnej warstwy maty50, a ich objętość trzeba odjąć w każdym stanie 100/120/150 l. | U-2026-11-04: K16 80 referencyjnych mocowań, **48 przecięć maty** — wariant odrzucony; **K17: 12 referencyjnych prowadnic i 80 zintegrowanych języków bez przecięcia maty, jednak nadal 0/20 mocowań kwalifikowanych**, brak weryfikacji serwisu i nośności | [K16 badanie](raporty/K16_podparcia_i_zabezpieczenia_20_wkladow.md) · [OpenSCAD z referencyjnymi podporami](dokumentacja/K16_p30e_z_mocowaniami_modulow_NIE_CNC.scad) · [model JSON](wyniki/k16_model_podparcia_20_wkladow.json). Następne G16: szkielet/rozbieralne prowadnice, pełne kolizje, weryfikacja nośności i montażu. | K16/K15/K02/K07/P30E |

## Specyfikacja odbiorowa do uzupełnienia

| Wielkość | Zdefiniowane warunki | Próg |
|---|---|---|
| Odpowiedź małosygnałowa | Napięcie, odległość, wygładzanie, zakres, pozycja | Do propozycji po pełnym audycie referencji |
| Użyteczny SPL 20/25/31,5/40/63/80 Hz | Osobno burst i sygnał dłuższy; RMS/peak; THD i kompresja | Do zatwierdzenia, nie wynika z jednej liczby katalogowej |
| THD i H2/H3 | Te same pasma, poziomy i geometria; poziom tła | Do zatwierdzenia po znalezieniu porównywalnych danych |
| Kompresja | Przyrost wejścia i wynikowy przyrost wyjścia, stan termiczny | Do zatwierdzenia |
| Szum | Elektroniczny w paśmie i akustyczny, weighting i tło | Do zatwierdzenia; nie utożsamiać niesłyszalności z odczytem mikrofonu poniżej tła |
| Faza/czas | Jednoznaczny timing reference, pasmo podziału | Do zatwierdzenia przy integracji |
| Powtarzalność | Ta sama konfiguracja, temperatura, pozycja i ponowny montaż | Do zatwierdzenia po określeniu niepewności |

Brak zatwierdzonych progów nie upoważnia do ogłoszenia zwycięzcy kosztowego.
Można porównywać granice modelu i wskazywać obszary, w których dany wariant
jawnie potrzebuje większego Sd·Xmax, napięcia lub objętości.
