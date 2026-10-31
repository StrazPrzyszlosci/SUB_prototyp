# Raport 097 — P38B: audyt układu współrzędnych źródła w P34B/P35A

**1 listopada 2026.** Wykonano **15 zestawień par**, czyli 30 rozwiązań 3D FV komory (trzy konfiguracje 100/120/150l × 20/40/60/80Hz i dodatkowe siatki 36mm przy 80Hz). Porównano historyczne osadzenie kosza i źródła 231/250mm we wnętrzu z pozycją przeliczoną z wymiarów ZEWNĘTRZNYCH P31C.

## Wykryty problem

P31C położenie głośnika **x=231, z=250mm** podaje względem **zewnętrznego** frontu 1020×500mm. Wnętrze zaczyna się na x=z=22mm od zewnętrznych krawędzi. To oznacza, że oś kosza w lokalnej siatce 976×456mm ma współrzędne **x=209, z=228mm**.

W P34B zapisano natomiast `source_xz_mm=[231,250]` w siatce już wewnętrznej, a jego zastępczy kosz 5l był osadzony również w x231/z250. To przesuwa oba obiekty o 22mm w prawo i 22mm w górę względem projektu. P35A powtarzał tę geometrię, więc jego rozkład sił na ścianach **pozostaje historyczny i wymaga ponownego policzenia w prawidłowym układzie**.

![Porównanie dwóch układów odniesienia](../wyniki/p38b_audyt_pozycji_zrodla.svg)

## Przeliczono oba ustawienia dla tej samej uproszczonej geometrii

W tabeli pokazano **RMS przestrzennego odchylenia względnego ciśnienia od średniego pola w komorze**. To nie jest SPL, charakterystyka brzmienia ani zniekształcenia.

| Wariant | Siatka | Historyczny kosz/źródło x231/z250 | Spójny kosz/źródło x209/z228 |
|---|---:|---:|---:|
| 100l / 80Hz | 55mm | 30,07% | **31,57%** |
| 120l / 80Hz | 55mm | 19,09% | **21,03%** |
| 150l / 80Hz | 55mm | 26,42% | **28,72%** |
| 100l / 80Hz | 36mm | 31,54% | **32,67%** |
| 120l / 80Hz | 36mm | 20,42% | **21,72%** |
| 150l / 80Hz | 36mm | 27,12% | **28,57%** |

**Wniosek:** błąd odniesienia nie jest numerycznie obojętny, szczególnie bliżej 80Hz. Wyliczone różnice w granicach około 1–2,3 punktu procentowego potwierdzają potrzebę jawnych układów współrzędnych w przyszłym CAD/FV/MES. Nie dowodzi to, że 120l fizycznie brzmi inaczej.

## Jak zachowano historię badania?

- Dotychczasowe raporty P34B/P35A, wyniki JSON i wykresy pozostawiono **bez nadpisywania** dla pełnej odtwarzalności.
- W skrypcie P34B przestawiono dwie stałe pozycji źródła/kosza na argument `cfg.source_xz_mm`. **Domyślna wartość pozostała historyczna [231,250]** — jej ponowne wywołanie nadal powinno dawać ten sam wynik.
- [Nowy skrypt P38B](../skrypty/p38b_audyt_ukladu_wspolrzednych.js) uruchamia oba warianty, zapisuje komplet 15 par.
- [Dane 15 par](../wyniki/p38b_koordynaty_FV_15_20261101.json), z uwzględnieniem objętości siatki oraz wartości ciśnienia w strefie źródła.

## Kolejne zadania, których ten audyt jeszcze nie zastępuje

1. Przebudować wszystkie bryły źródła, wręg i modułów we wspólnym zewnętrznym systemie CAD i automatycznie przekształcać je do lokalnej siatki FV.
2. Zaktualizować mapy P35A ciśnień na ścianach **ze spójnymi współrzędnymi** i z rzeczywistym konturem kosza.
3. Dodać do solvera straty maty 50mm, rozkład nacisków na wkładach i stan podatnych ścian.
4. Nie przenosić wyników historycznych bez korekty do MES i nie zatwierdzać frezowania CNC.

**Granice ważności:** małosygnałowy model powietrza bez pochłaniania, sztywne ściany, hipotetyczna bryła kosza 5l; wyniki nie są kalibracją materiałów ani walidacją akustyczną prototypu.