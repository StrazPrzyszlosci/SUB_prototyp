# P35 — plan walidacji konstrukcji przed frezowaniem

**Stan: 31.10.2026. Dokumentacja kontrolna, nie zwolnienie wyrobu do produkcji.**
Celem jest zapewnienie, aby liczby z modeli P33–P35 przekładały się na wiarygodne decyzje konstrukcyjne, a nie tylko na kolejne wykresy.

## Etap A — fizyczne parametry MDF oraz spoin

| Próbka / test | Co trzeba zaobserwować | Wpływ na model | Warunek przejścia |
|---|---|---|---|
| Próbka MDF 22 i 44 mm, z różnych kierunków płyty | masa i wymiary, gęstość, ugięcie pod znanym obciążeniem | E, rho, ortotropia | obliczenie E z geometrii belki i oszacowanie przedziału niepewności, co najmniej 3 niezależne próbki/konfigurację |
| Spoina MDF–MDF, geometria docelowa | poślizg, odrywanie, odkształcenia i nośność przed zniszczeniem | k_trans/k_rot, nośność, lokalna energia pękania | 3 powtórzenia na rodzaj połączenia; znana powierzchnia klejenia, czasy utwardzania, wilgotność |
| Spoina MDF–sklejka, jeśli zostanie zaproponowana | jw., przy tej samej grubości i powierzchni | porównanie materiałów | nie przenosić danych z MDF–MDF bez testów |
| Połączenie wręga–panel | ugięcie oraz moment/siła przy działaniu na ramę | podatność wręgi | odtworzenie w modelu na **tych samych warunkach brzegowych** |
| Powtarzalne mocowanie wkładów | siła wyjęcia, luz po cyklach, pełzanie i uszkodzenia MDF | rygle, uszczelki, wkręty | brak samoczynnego wyjścia i udokumentowana siła w odniesieniu do P34C; liczba cykli do ustalenia przed testem |
| Materiał maty 50 mm | grubość, gęstość, opór przepływowy dla próbek i ułożenia | straty akustyczne komory | wyznaczony opór i jawna niepewność zamiast przypisania przypadkowego współczynnika |

Nie stanowi to certyfikacji bezpieczeństwa ani deklaracji zgodności z określoną normą. Próby niszczące i elektryczne muszą być zaplanowane z odpowiednimi zabezpieczeniami.

## Etap B — poprawna geometria CAD i MES

1. Zamodelować **wszystkie sześć paneli**, otwór i pogłębienie głośnika według rzeczywistego rysunku konkretnej jednostki, mocowanie śrubowe, front 44 mm i połączenia paneli.
2. Wprowadzić rzeczywiste **wręgi, ramę U, 20 wkładów**, mechanizmy ich blokowania i uszczelnienia oraz narzędzia potrzebne do montażu.
3. Sprawdzić wszystkie **trzy stany 100/120/150 l** na realnych bryłach 3D, nie tylko AABB. Powtórzyć tory wejścia/wyjścia 20 modułów, kolizje przy montażu z narzędziem, tolerancje wymiarowe i kompletne 500 mm głębokości ze stopami/maskownicą.
4. Zamienić kwadratowe komórki frontu na **siatkę dopasowaną do otworu**. Oddzielić obwodowe śruby i uszczelki od pól MDF.
5. Testować elementy Q4: **sztywne ruchy bryły, patch test, hourglass, shear locking**, obrót i proporcje elementów oraz siatki coraz gęstsze.
6. Porównywać **te same postacie drgań (MAC)** między siatkami. Nie identyfikować panelowego rezonansu wyłącznie przez pierwszy eigenvalue całej bryły na stopkach.

## Etap C — model sprzężony akustyka–mechanika

1. P35A dostarcza względne mapy ciśnienia **na zewnętrznych ścianach komory**. Uzupełnić siły na ściankach wkładów i wręg, a następnie zweryfikować bilans sił.
2. Skalibrować poziom średniego ciśnienia na podstawie znanego ruchu membrany, jej rzeczywistego Sd i geometrii kosza. Nie wprowadzać fikcyjnego `1000 Pa` jako stanu rzeczywistej pracy.
3. Włączyć dynamiczną podatność ścian i absorpcję maty do rozwiązania równania Helmholtza; sprawdzić bilans energii i stabilność schematu sprzężenia.
4. Przeprowadzić minimum trzy zagęszczenia siatki dla 20–120 Hz i 100/120/150 l. Osobno policzyć tolerancje objętości i wpływ nieregularnego rozkładu wkładów.
5. Jako kolejny kamień milowy przyjąć zgodność model–pomiar pierwszej, zmontowanej sztuki (impedancja, ciśnienie w komorze, przyspieszenia ścian, near-field, szczelność, THD/IMD przy tym samym SPL).

## Kryterium „można przygotować pliki CNC”

**Wszystkie warunki jednocześnie:** kompletny model CAD; potwierdzone gabaryty ≤500 mm *całego* urządzenia; liczony bilans objętości netto z rzeczywistą wypornością kosza; przetestowane rozkładanie i blokowanie modułów; siatka MES z potwierdzoną stabilnością i kontrolą zbieżności; udokumentowana wytrzymałość połączeń i obudowy pod właściwym obciążeniem; plan pomiarów po wykonaniu. Projekt z elektrycznym zasilaniem 230 V i wzmacniaczem PCB wymaga **niezależnej analizy bezpieczeństwa** i nie jest zatwierdzany samym modelem mechanicznym.

**Ostatnia decyzja:** utrzymać bazę 1020×425×500mm / 120l, ale **nie rozpoczynać frezowania w celu ostatecznej konstrukcji** bez zamknięcia powyższych bramek.