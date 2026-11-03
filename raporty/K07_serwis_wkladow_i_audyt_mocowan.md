# K07. Czy można zmieniać litraż bez opróżniania skrzyni?

**3 listopada 2026 · Audyt K01–K06, nowa symulacja kolejności obsługi.** Najbliższa decyzja dotyczy tylnego osprzętu głośnika. Przy samych klockach 20 mm model pozwala przejść przez trzy nastawy, pozostawiając wspólne wkłady na miejscu. Osprzęt zamontowany na stałe wymaga osobnej próby.

## Co faktycznie sprawdzały poprzednie etapy

- K01–K03. Osiem klocków musi jednocześnie zmieścić się obok kosza i przenieść siłę z kołnierza przez front na skrzynię. Odległość osi od wycięcia wynosi nominalnie 6,1 mm. Dla otworu w MDF o średnicy d pozostaje 6,1 − d/2 mm materiału po stronie wycięcia przed tolerancjami. Otwór w koszu, otwór przelotowy w MDF i gniazdo wkładki należy wymiarować oddzielnie. Sama szerokość pasa nie rozstrzyga o wytrzymałości.
- K04. Odtworzono 22 próby kolejności oraz 42 przypadki obrysu nakrętek. Planer zatrzymuje się przy pierwszej niedostępnej trasie. W pełnej obwiedni 28,8 mm wkłada moduły 0–15 i zatrzymuje się przy ID 16. Modułów 17–19 w tej sekwencji już nie próbuje. Osobna kontrola 20 końcowych pozycji dotyczy wyłącznie kolizji z zastępczą bryłą osprzętu.
- K05. Odtworzony wynik zgadza się z wersjonowanym JSON. Wartość 12,1 mm dotyczy przesunięcia środka płaskiej podkładki Ø12 po przejściu osiowym. Nie określa potrzebnego miejsca na rękę.
- K06. Odtworzono 24 trasy. Skorygowano kontrolę ścian tak, aby dla każdej sondy obejmowała oba końce ruchu promieniowego. Współrzędne zmieniają się monotonicznie, więc ich skrajne wartości są na końcach. Dodano dolne ograniczenie poprawności numerycznej przez porównanie z próbkowaniem. Wyniki zbiorcze pozostały zgodne. Dla Ø48 odległość do lewej ściany to 1 mm na osi 180°. Osobno na końcu dojścia powierzchnia każdej sondy zatrzymuje się 0,5 mm przed tylną powierzchnią klocka. Żaden z tych wymiarów nie jest tolerancją wykonawczą.
- Poprawiono regresję K06. Sprawdza odsyłacz do raportu w przewodniku zamiast nieistniejącej frazy. Zmiany geometrii źródłowej P30A/P30E również uruchamiają kontrolę.

## Jedna kolejność dla trzech objętości

Planer K02 sprawdza wejście od zewnątrz i dalsze odcinki z już ułożonymi wkładami. K07 zmienia kolejność na **4–15, następnie 0–3, następnie 16–19** (ID od zera). Pierwszy wkład daje stan 150 l, pierwszych 12 daje 120 l, a komplet 20 daje 100 l. Są to nazwy stanów modelu P30E. Nie wymagają wyjmowania wspólnych modułów między nastawami.

| Przeszkoda przy każdej śrubie | Luz wokół wkładu | Kolejno ułożone | Ostatnia osiągnięta nastawa |
|---|---:|---:|---|
| Klocek 20 mm | 3 i 6 mm, dwie próby | 20/20 w obu | 100 l |
| Pełny pryzmat K04 o głębokości 28,8 mm | 3 i 6 mm, dwie próby | 16/20 w obu | 120 l |

W drugim przypadku pierwsza trasa wkładu ID 16 przecina obrys mocowania nr 0 (0°). Planer nie znalazł objazdu. **To miejsce do sprawdzenia na makiecie.** Kąt 180° ma inne ograniczenie: jest najbliższy ścianie przy operowaniu za śrubą. Użycie pełnego pryzmatu zamiast kształtu konkretnego osprzętu oraz ograniczenie ruchu wkładów do translacji mogą wykluczać realne trasy.

W idealnym modelu sztywne bryły można wyjąć, odwracając znalezione ruchy w odwrotnej kolejności. W praktyce trzeba także dosięgnąć zamka, chwycić wkład, utrzymać go i zabezpieczyć ponownie. Podczas zmiany litrażu po zamontowaniu głośnika trzeba dodatkowo zdjąć kosz i rozstrzygnąć, czy tylny osprzęt może pozostać na miejscu.

## Rekomendowane zadania i kryteria decyzji

| Kolejność | Wykonanie i zapis | Decyzja po próbie |
|---|---|---|
| 1. Pomiary geometrii | Zapisać rewizję kosza RSS390HF-4 i wspólną bazę pomiarową. Na wszystkich 8 osiach zmierzyć otwór kołnierza, położenie żeber i zacisków, odsadzenie kosza, wymiary nośnika i rzeczywistego narzędzia. Zapisać orientację, niepewność oraz zdjęcia ze skalą. | Wyznaczyć najmniejszy prześwit po odjęciu niepewności i tolerancji montażu. Brak dodatniego zapasu wymaga zmiany obrysu lub dodatkowego pomiaru. |
| 2. Makieta serwisowa 1:1 | Front 44 mm, klocki 20 mm, pozycje ścian i wręg, 20 wkładów z uchwytami i zamkami. Sprawdzić ID 16 przy 0°, potem operowanie przy 180°. Po ułożeniu wkładów zamontować osiem tylnych nośników, unieruchomić nakrętki i założyć kosz. | Zdjąć głośnik i wykonać pełen cykl 100 → 120 → 150 → 120 → 100 l od frontu. Zanotować każdą część wymagającą wyjęcia, dostęp narzędzia i obrót lub wypadnięcie nakrętki. Powtórzyć w obu przewidzianych orientacjach obudowy. |
| 3. Próbki połączenia | Z tego samego MDF, drewna i kleju wykonać co najmniej trzy porównywalne próbki pilotażowe na wariant i warunek. Odwzorować odległość do wycięcia, układ włókien klocka i grubości. Porównać śrubę przelotową z osadzoną nakrętką oraz wkręt obsługiwany od frontu. Zmierzyć zależność siła–przemieszczenie, rodzaj uszkodzenia i utratę docisku po cyklach serwisowych. | Przed kwalifikacją ustalić obciążenie projektowe, wymagany docisk uszczelki i zapas. Rozrzut i tryb zniszczenia wyznaczają dalsze próby. Sama średnia z pilotażu nie wystarcza do ustalenia momentu dokręcania. |
| 4. Zamknięcie geometrii | Dla rozwiązania, które przejdzie próby, zaktualizować trzy bilanse objętości o rzeczywiste wyporności. Zmierzyć pełną głębokość z osłoną, terminalem i przewodem w przewidzianej zabudowie. Na prototypie sprawdzić szczelność po ponownym montażu i grzechotanie wkładów. | Przed wydaniem wymiarów do wykonania potwierdzić serwis, nośność i całkowity gabaryt ≤500 mm. Wyniki szczelności i odsłuchu uzupełnić po budowie. |

Jeśli nośnik da się zamontować tylko raz, a potem utrudnia regulację, sprawdzić jego demontowalną wersję lub połączenie obsługiwane w całości od frontu. Zmianę konstrukcji uzależnić od wyniku próby serwisowej i próbek złącza. **CNC HOLD.**

### Odtworzenie

Python 3.12.14, NumPy 2.3.5. Z katalogu repozytorium uruchomić `python skrypty/k07_zmiana_objetosci.py` i porównać JSON z wersjonowanym wynikiem. Dane wejściowe są wersjonowane w K01, K02 i P30A/P30E. Głośnik jest wyjęty na czas ruchu wkładów. Model nie zawiera dłoni, zamków ani odkształceń.

[Skrypt](../skrypty/k07_zmiana_objetosci.py) · [Wynik czterech prób](../wyniki/k07_zmiana_objetosci.json) · [K04](K04_pelne_gabaryty_nakretki_podkladki_i_montaz_20_modulow.md) · [K06](K06_dostep_do_8_mocowan_po_20_wkladach.md).
