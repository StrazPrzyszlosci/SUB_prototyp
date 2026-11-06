# S06. Płyty wariantu A i pasowanie wręgi

Dla dwóch korpusów potrzeba 16 formatek MDF. Przyjęto połączenia na styk zgodne z podziałem brył S02. Dwa pełne fronty i pełny tył nakrywają krawędzie boków, dna i góry. Boki biegną przez całą wysokość, dno i góra mieszczą się między nimi. Referencyjny gabaryt korpusu po zaokrągleniu do 0,1 mm wynosi 816,8 × 473,3 × 394,0 mm (szerokość, wysokość, głębokość). Grubość nominalna wszystkich płyt wynosi 22 mm.

| Część | Obrys formatki, mm | Na skrzynię | Na parę | Funkcja lub obróbka do weryfikacji |
|---|---|---:|---:|---|
| FR1 | 816,8 × 473,3 | 1 | 2 | Przednia warstwa frontu, otwór i osie kosza |
| FR2 | 816,8 × 473,3 | 1 | 2 | Tylna warstwa frontu, kieszeń pierścienia od strony FR1 |
| Tył | 816,8 × 473,3 | 1 | 2 | Pełna płyta zamykająca |
| Bok | 328,0 × 473,3 | 2 | 4 | Jeden prawy bok na skrzynię dostaje przepust S05 |
| Dno i góra | 772,8 × 328,0 | 2 | 4 | Pomiędzy bokami |
| Wręga | 772,6 × 429,1 | 1 | 2 | Okno 712,6 × 369,1 mm, założony promień wewnętrzny R3 |

Suma powierzchni prostokątnych formatek dla pary wynosi 4,6175 m² przed wycięciem otworów. Rozkrój arkuszy wymaga osobnego doliczenia odstępów narzędzia, obrzeży i odpadów. Kasety maskownic, podpory, pierścienie i osłony terminala stanowią osobne pozycje. To zestawienie służy do oceny konstrukcji i wyceny materiałowej.

## Bazy i objętość

Przyjąć początek na zewnętrznym dolnym lewym narożniku przedniej płyty, patrząc na głośnik. X w prawo, Z w górę, Y w głąb. Warstwy FR1 i FR2 zajmują odpowiednio Y od 0 do 22 oraz od 22 do 44 mm. Komora sięga do Y = 372 mm. Wręga zajmuje Y od 197 do 219 mm. Po obu jej stronach pozostają odcinki po 153 mm. Środek głośnika na nowym froncie to X = 408,4 i Z = 236,65 mm. Zachować wspólną bazę FR1/FR2 przy kontroli ośmiu osi, według [próby frontu S03](S03_karta_proby_frontu.md).

Światło korpusu wynosi 772,8 × 429,3 × 328,0 mm. Bilans dla jednej skrzyni:

| Składnik | Objętość |
|---|---:|
| Komora geometryczna | 108,8183 l |
| Wręga z oknem R3 | 1,5072 l |
| Przetwornik, założenie S01 | 5,000 l |
| Terminal, założenie do rewizji po wyborze przepustu S05 | 0,175 l |
| Przewody i klej, założenie S01 | 0,150 l |
| Netto obliczeniowe | 101,9861 l |

Różnica względem celu 102 l to 14 ml na skrzynię. Zmiana naroży okna wręgi z R3 na R4 dodaje około 0,13 ml MDF. Dokładność netto ograniczają przede wszystkim wyporność głośnika, przepustu i rzeczywiste światło komory. Grubość obrzeża wręgi wynosi 30 mm. Po wprowadzeniu nominalnego luzu montażowego trzeba osobno potwierdzić ciągłość spoiny i jej sztywność, od których zależą wyniki S02.

## Co przeliczyć po pomiarze płyty

Przy jednakowych formatkach z tabeli i MDF o grubości 22,3 mm pakiet dna z bokami ma 817,4 mm szerokości, czyli wystaje łącznie o 0,6 mm względem frontu. Głębokość rośnie do 394,9 mm, a wręga jest o 0,4 mm za wysoka. Przy grubości 21,7 mm luz pionowy wręgi rośnie do 0,8 mm. To scenariusze wrażliwości, a nie deklaracja tolerancji dostawcy.

W odrębnym przeliczeniu utrzymano zewnętrzne wymiary docelowe i na nowo wymiarowano części dla każdego scenariusza. Przy odchyłce każdego wymiaru obudowy ±0,2 mm, jednorodnej grubości płyty 21,7 lub 22,3 mm oraz R3 lub R4 zakres obliczeniowy wyniósł od 101,29 do 102,69 l przy stałych pozostałych wypornościach. Skrypt kontroluje bilans objętości także przez niezależne zsumowanie pełnych płyt przed obróbką frontu.

Dla różniących się płyt od szerokości zewnętrznej odjąć grubości rzeczywistego lewego i prawego boku, od wysokości grubości dna i góry, a od głębokości grubości FR1, FR2 i tyłu. Uwzględnić zmierzoną grubość ściśniętych spoin w odpowiednich łańcuchach wymiarowych. Model nominalny zakłada pomijalne grubości spoin na stykach. Wymiary po oklejeniu uwzględnić osobno w budżecie głębokości S04.

## Pasowanie i kolejność montażu

Luz 0,2 mm jest łączny na wymiar, czyli nominalnie po 0,1 mm na stronę. Jeśli światło i zewnętrzny wymiar wręgi mają niezależne odchyłki po ±0,2 mm, wynikowe pasowanie wynosi od wcisku 0,2 mm do luzu 0,6 mm. Nie przenosić nominalnych 0,2 mm do zamówienia bez pomiaru. Zbyt luźna wręga utrudnia uzyskanie nośnego połączenia ze ścianami.

1. Zmierzyć materiał przeznaczony na każdą płytę w kilku miejscach. Przeliczyć formatki względem wspólnych baz i wykonać próbę złącza na tej samej partii MDF.
2. Złożyć na sucho boki, dno i górę w przyrządzie. Na obu płaszczyznach wręgi zmierzyć światło w kilku przekrojach i obie przekątne. Sprawdzić prostopadłość i naroża. Dobrać obrys wręgi do najmniejszego prześwitu oraz sprawdzonej spoiny.
3. Ustawić wręgę z dostępem od otwartej strony przed zamknięciem ostatniej płyty. Sprawdzić docisk wszystkich czterech krawędzi, usunąć nadmiar kleju i utrzymać położenie w czasie utwardzania. Przed zamknięciem sprawdzić trasę przewodu, przepust i prześwit kosza.
4. Złożyć próbnie FR1, pierścień, FR2 i kosz. Zachować dostęp do kontroli pierścienia przed sklejeniem frontu. Po związaniu sprawdzić gabaryt, szczelność i wyjęcie głośnika.

Dane brakujące do wydania obrysów produkcyjnych obejmują rzeczywisty materiał, pasowanie wręgi, kwalifikację połączenia FR1/FR2, przepust S05 i zatwierdzenie architektury. [Model obliczeniowy](s06.py) · [wyniki dla pary](s06_wyniki.json) · [model złożonej skrzyni S02](S02_korpus.md).
