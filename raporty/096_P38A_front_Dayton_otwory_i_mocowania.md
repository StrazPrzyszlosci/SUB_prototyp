# Raport 096 — P38A: front z rzeczywistym rozstawem mocowania Dayton RSS390HF-4

**1 listopada 2026.** Opracowano **parametryczny szkic frontu 2D**, zweryfikowano osiem pozycji otworów producenta, przeanalizowano sześć średnic hipotetycznych tulei/otworów oraz zapas głębokości. To **rysunek referencyjny, nie gotowy projekt CAD do frezowania**.

![Wymiary kosza i rozstaw otworów](../wyniki/p38a_front_NIE_CNC.svg)

## Dokumentacja źródłowa — bez zgadywania szablonu

Oficjalny rysunek Dayton Audio (RSS390HF-4, model C02):
https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf

Wymiar zewnętrzny: **Ø388,4 mm**; średnica wycięcia w froncie: **Ø355,8 mm**; rozstaw śrub na okręgu **Ø368 mm**, **8 otworów Ø6,5 mm**; całkowita głębokość **178 mm**; grubość czoła kosza **10,5 mm**. Przyjęto równomierną fazę osiem otworów co 45°, ale bez potwierdzonego *clockingu* rzeczywistego egzemplarza (położenia pierwszego otworu i zacisków). **Otwór Ø6,5 mm w aluminiowym kołnierzu NIE oznacza zalecanego otworu pilotującego Ø6,5 mm w MDF.**

## Jednoznaczne współrzędne

| Element | X od lewej krawędzi ZEWNĘTRZNEJ | X w lokalnym wnętrzu |
|---|---:|---:|
| Oś głośnika | **231 mm** | **209 mm** |
| Pierwsza wręga | 448 mm | 426 mm |
| Druga wręga | 723 mm | 701 mm |

Pionowo oś głośnika wynosi Z=250 mm od zewnętrznego dołu i Z=228 mm w układzie wewnętrznym (MDF22 mm). Sama głębokość wewnętrzna to 359 mm: 425 −44 mm front −22 mm tył.

## Główne odkrycie: bardzo mało miejsca na mocowanie

Promień otworu MDF: 177,9mm. Promień osi wkrętów: 184mm. Odległość środka otworu od krawędzi wycięcia to **6,1mm**. Dla przezotworu Ø6,5mm promień 3,25mm, więc pomiędzy krawędzią tego otworu a wycięciem MDF pozostaje promieniowo tylko **2,85mm**. Od zewnętrznej krawędzi tego samego otworu do zewnętrznej krawędzi kołnierza pozostaje **6,95mm**.

| Modelowa średnica tulei/otworu | Wolny materiał promieniowy między tuleją a wycięciem |
|---|---:|
| Ø6,5mm | 2,85mm |
| Ø8mm | 2,10mm |
| Ø10mm | 1,10mm |
| Ø12mm | 0,10mm |
| Ø14mm | **−0,90mm — kolizja geometryczna** |
| Ø16mm | **−1,90mm — kolizja geometryczna** |

To **geometria planarna**, nie zweryfikowana nośność MDF. Użycie gwintowanej tulei o znacznej średnicy nominalnej w tej osi może wejść w otwór głośnika. Trzeba zaprojektować **rzeczywistą ścieżkę sił (np. oddzielny pierścień/wiązanie/element stalowy)**, uwzględniając ścinanie, wyrywanie, odrywanie laminatu i możliwość demontażu. Nie aprobujemy konkretnej śruby, kołka, kleju ani rozwiązania zbrojenia.

W położeniu kosza x=231mm zewnętrzna obręcz dochodzi do x=36,8mm, czyli **14,8mm za wewnętrzną krawędź lewego panelu x=22mm**. Projekcja pierwszej wręgi zaczyna się x=448mm, zatem do prawej krawędzi obręczy pozostaje 22,8mm; uwaga: wręga jest **za frontem** i do rzeczywistej kolizji liczy się pełna objętość kosza oraz element mocujący, a nie przecięcie dwóch okręgów 2D.

## Głębokość, przewody i uszczelka

Nominalny korpus ma **425mm głębokości**, a kołnierz wystaje około 10,5mm przy montażu od zewnątrz; sam kosz daje obrys referencyjny **435,5mm**. Z limitu 500mm pozostaje **64,5mm na maskownicę, stopy, terminal, przewody, tolerancje i inne projekcje**. Przy przyjęciu motoru 178−10,5=167,5mm od płaszczyzny frontu, do początkowej płaszczyzny tylnej maty 50mm modelowo pozostaje **185,5mm**, ale kosz nie jest walcem: rzeczywiste wyprowadzenia i wentylacja magnesu wymagają kontroli.

## Pliki referencyjne i ograniczenia

- [Parametryczny kod](../skrypty/p38a_front_Dayton_wymiary.js) oblicza 8 współrzędnych, marginesy, poziomy odniesienia i zapisuje SVG, JSON i **wstępny DXF**.
- [Rysunek SVG — NIE CNC](../wyniki/p38a_front_NIE_CNC.svg)
- [DXF — NIE CNC](../wyniki/p38a_front_NIE_CNC.dxf) — warstwy REFERENCE, nie zweryfikowana dokumentacja frezowania.
- [JSON wymiarowy](../wyniki/p38a_front_geom_20261101.json)

## Bramki przed wykonaniem

**G38-1:** porównać kosz z fizycznym szablonem producenta, otworami, zaciskami i realnym położeniem osi.

**G38-2:** rozwiązać połączenie 8 śrub z MDF (wyrywanie, szczelinowanie, grubość 44mm, wkładka, pozycja wręgi) i zaprojektować prawdziwe bryły 3D pierścienia/mocowań.

**G38-3:** sprawdzić 500mm łącznie z maskownicą, terminalem, okablowaniem, wentylacją i wybranym sposobem osadzenia głośnika.

**G38-4:** dopiero na pełnym CAD uruchomić zwalidowany MES z konformalnym otworem i łącznikami. **Ten raport nie wydaje zgody na CNC.**