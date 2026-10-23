# Macierz wymagań i dowodów

Wydanie 0.1, 2026-10-23. U = wymaganie użytkownika, P = propozycja,
O = otwarte. Akceptacja briefu nie oznacza akceptacji dowolnych liczb modelu.

| ID | Wymaganie | Status | Dowód lub sposób weryfikacji | Etap |
|---|---|---|---|---|
| W01 | Pierwszy prototyp sealed, regulowany litraż | U | Bilans objętości i projekt modułów | R3/R5 |
| W02 | Porównanie co najmniej 3 przetworników, 12″ i 15″ | U | Dane źródłowe + wspólny model; policzono 3 Dayton iSB | R1/R2 |
| W03 | Rozszerzenie o konkurencyjnego producenta | Zrealizowane wstępnie | SB34SWPL76-4: obejrzanyPDF i model; opinie i rynek otwarte | R1 |
| W04 | Sensowny kompromis 20 Hz/headroom 20–40 Hz | U, liczby O | Pasma SPL, Xpeak, napięcie, THD i kompresja po budowie | R2/P2 |
| W05 | Neutralność i niski szum, również cicho | U, progi O | Gain staging i dokumentacja elektroniki; późniejsze pomiary | R4/P2 |
| W06 | Referencje ADAM Audio średniej/wyższej półki | U-009: Sub12/Sub15 zatwierdzone | Progi liczbowe otwarte; referencje monitorów odłożone | R0 |
| W07 | Główna ocena sweet spot 2,5–3 m | U | Plan ustawienia, późniejsze pomiary z pozycją mikrofonu | R0/P2 |
| W08 | Sąsiednie punkty tylko diagnostyczne | U | Badanie wrażliwości, bez optymalizacji całej kanapy | P2 |
| W09 | Brak narzuconego budżetu i gabarytów | U | Koszt minimalny przy spełnionych wymaganiach; jawne kompromisy | R1–R5 |
| W10 | Zewnętrzny wzmacniacz, DSP, zasilacz | U | Schemat i dokumentacja mechaniczna | R4/R5 |
| W11 | Gotowy miniDSP, minimum 8 niezależnych wyjść docelowo | U | Routing i instrukcja konkretnej wersji | R4 |
| W12 | Moduły klasy D, dopasowanie napięcia/prądu i ochrony | U | Z(f), limity, dokumentacja zasilacza, chłodzenie | R4 |
| W13 | Możliwa wymiana głośnika i objętości | U | Wymienny front, prześwity, mechanizm uszczelnienia | R3 |
| W14 | CNC od wskazanego wykonawcy MDF | U | [Wymagania wykonawcy](WYKONAWCA_CNC.md) | R3/R5 |
| W15 | Osłona membrany, stabilność, serwis | U | Rysunek mechaniczny i późniejszy odbiór montażu | R5/P1 |
| W16 | Docelowo 2 subwoofery i monitory aktywne 3-drożne | U | Schemat 8 torów i pozostawiony zakres podziału | R4/P3/P4 |
| W17 | Powtarzalność i kalibracja w różnych pokojach | U, przyszłe | Dokumentacja wersji i pilotaż w kilku lokalizacjach | P5 |
| W18 | Teraz wyłącznie badania do budowy | U-004 | Plan R0–R5; brak zleceń wykonawczych | Bieżący |
| W19 | Tor pomiarowy wybrać po budowie | U-002 | Brak bieżącej listy zakupowej aparatury | P2 |
| W20 | Pomiary wyłącznie w pokoju | U-003 | Wyniki oznaczone in-room; ograniczenia oddzielenia urządzenia | P2 |
| W21 | Opinie właścicieli i konstruktorów | U-005 | [Rejestr doświadczeń](baza_wiedzy/08_opinie_i_ocena_dowodow.md) | R1 |

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
