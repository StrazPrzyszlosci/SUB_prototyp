# S05. Mniej miejsca na przewód przy boku skrzyni A

Do przymiarki obu identycznych modułów wybrać ten sam prosty wtyk NL4FXX-W-S i gniazdo NL4MPRXX z S04, lecz obrócić całe gniazdo o 90° na zewnętrznym wsporniku. Oś wtykania biegnie wzdłuż boku. Wtyk i przewód odchodzą ku frontowi. W ten sposób łuk przewodu może leżeć w płaszczyźnie równoległej do ściany skrzyni. Rozwiązanie wymaga wykonania wspornika i niezależnego szczelnego przepustu do komory akustycznej.

| Rozwiązanie | Budżet występu bocznego | Szerokość poziomego modułu z występem | Wysokość pionowego modułu ze stopami 20 mm i występem na górze |
|---|---:|---:|---:|
| Prosty wtyk prostopadły do boku, łuk S04 | 186,4 mm | 1003,2 mm | 1023,2 mm |
| Kątowy NL4FRX w gnieździe na boku | 72 mm | 888,8 mm | 908,8 mm |
| Prosty wtyk równoległy do boku na wsporniku | 70 mm | 886,8 mm | 906,8 mm |

Wszystkie liczby opisują obwiednię roboczą przy ułożonym przewodzie. Należy osobno doliczyć prześwit od mebla i miejsce dla ręki albo zapewnić możliwość wysunięcia całego modułu. Dla NL4FRX odczytano z rysunku 62 mm wzdłuż osi wtykania i maksymalnie 79 mm wzdłuż odgiętki. Do 62 mm doliczono z S04 10 mm na występ gniazda. Pominięcie zagłębienia po spięciu zawyża potrzebne miejsce. Kierunek wyjścia po zatrzaśnięciu i tor obrotu z przewodem wymagają przymiarki. Producent oznacza NL4FRX jako wycofany, więc nadaje się przede wszystkim do sprawdzenia, gdy egzemplarz jest już dostępny. [Rysunek wtyku](https://www.neutrik.co.uk/media/8484/download/nl4frx-1.pdf?v=1) · [status producenta](https://www.neutrik.com/en/product/nl4frx.pdf), sprawdzone 6 listopada 2026.

## Geometria próbna wspornika

Przyjąć zamkniętą zdejmowaną osłonę styków o zewnętrznych wymiarach 70 mm od ściany × 72 mm wysokości × 80 mm wzdłuż głębokości. Przednia płytka z gniazdem leży 270 mm od płaszczyzny frontu konstrukcyjnego, tył osłony na 350 mm. Oś gniazda znajduje się 35 mm od boku, w połowie wysokości płytki. Kołnierz Ø50,8 mm ma 9,6 mm minimalnego odstępu od jej zewnętrznej krawędzi. Użyć wymiarów konkretnego gniazda i wtyku z [S04](S04_glebokosc.md). Wszystkie wymiary wspornika są założeniami do przymiarki.

Na osi głębokości skrajny roboczy koniec wtyku z odcinkiem prostym wypada na 167,5 mm od frontu. Przy dodatkowym ruchu wypinania 35 mm trzeba utrzymać wolny korytarz co najmniej do 132,5 mm. Zapas 35 mm jest proponowany do próby. Ustawić blokadę tak, aby dało się ją zwolnić bez ciągnięcia za przewód. Łuk przewodu SP225 prowadzić dalej wzdłuż boku, w płaszczyźnie równoległej do płyty. Na przykład przy zastosowaniu promienia osi 80 mm z S04 ćwierćokrąg ku górze od punktu 167,5 mm kończy się 87,5 mm od frontu i 80 mm powyżej punktu rozpoczęcia. Promień sprawdzić na przewodzie. Po obrocie całego korpusu ten sam tor leży równolegle do górnej ściany modułu. Pętlę serwisową przenieść do dostępnej komory mebla.

Przy tych założeniach boczny występ maleje o 116,4 mm. W pozycji pionowej przy pochyleniu przód-tył 0,5° i szczelinie tylnej 5 mm model obwiedni S04 daje 446,9 mm zamiast 447,9 mm. Poprawa dotyczy głównie szerokości niskiej zabudowy i wysokości bocznego modułu. Skręcenie względem wnęki i wymagany dostęp podczas serwisu trzeba sprawdzić na miejscu.

## Wpływ na korpus i próba przed zatwierdzeniem

Osłona i kołnierz pozostają po stronie zewnętrznej. Przewód do komory przeprowadzić przez osobny uszczelniony przepust z odciążeniem. Mocowania osłony mają być ślepe albo osobno uszczelnione. Dobrać grubość płytki, połączenie z MDF, promień przewodów wewnątrz osłony i dostęp do zacisków. Zważyć osłonę z osprzętem do modelu podparcia. Obliczyć rzeczywiste wyparcie wewnętrznej części przepustu i skorygować szacunek 0,175 l z S01. Przy braku tych danych do porównań akustycznych obowiązuje dotychczasowy nominalny bilans 102 l.

Wykonać najpierw pełnowymiarową przymiarkę na wycinku płyty 22 mm. Zanotować maksymalny występ z przewodem i śrubami, drogę wypięcia, wolne miejsce na dłoń i rzeczywisty kształt łuku. Powtórzyć po obrocie o 90° w makiecie wnęki. Na docelowym zestawie sprawdzić szczelność przepustu, zachowanie odciążenia i drgania osłony. Wyniki rozstrzygną, czy zasadne jest przyjęcie 70 mm w zabudowie.

[Skrypt i kontrole](s05.py) · [wyniki](s05_wyniki.json). Odtworzenie: `python wariant_staly/s05.py`.

[Przymiarka w skali 1:1, A3 poziomo](S05_przymiarka.svg). Wydrukować w skali 100 procent i zmierzyć odcinek kontrolny 100 mm.
