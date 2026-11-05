# K37 — grubości banku i operacje wykonawcze

5 listopada 2026. **CNC HOLD.** K37 rozszerza model K36 o indywidualne
grubości czterech płatów kanałów, dwunastu szyn pośrednich, ośmiu płytek
metalowych i jednego małego dystansu: razem25 wejść pomiarowych.
To nadal nie wszystkie pomiary gotowej obudowy — oddzielnie pozostają
korpus K35, wkłady K31 i pomiary wykończonych części obrabianych.

## Zmiany geometryczne

Wewnętrzne powierzchnie płatów pozostają Y68 i332. Zmiana grubości płatu
rozchodzi się na zewnątrz kanału. Górne powierzchnie szyn pozostają na
Z156/272/388, a rzeczywista grubość zmienia ich dolne powierzchnie.
Osiem płytek ma niezależne grubości; początek przednich płatów uwzględnia
najgrubszą płytkę oraz przyjętą szczelinę0,2 mm. Mały dystans zachowuje
tylną powierzchnię X1018, a jego przód zależy od zmierzonej grubości.

Dodano jawne szczeliny0,2 między szynami/ogranicznikami a płatami:
przednia szyna zaczyna się naY68,2, tylna kończy naY331,8. Szerokość50
pozostaje zachowana. Położenia skrzynek nie zostały przesunięte.
Zmiana ogranicza powierzchnię podparcia przy krawędzi; wymaga oceny
połączenia i ponownej kontroli wszystkich tras po połączeniu tolerancji.
Nie przenosimy automatycznie pełnego wyniku ruchowego K36 na K37.

## Lista operacji poza wycinaniem konturów

| Części | Liczba | Proponowany półfabrykat | Wymiar po obróbce |
|---|---:|---|---|
| Dolne szyny A/B, przód/tył | 4 | MDF nominalnie22 | 17,3–18,3 mm według korpusu |
| Górne ograniczniki A/B, przód/tył | 4 | MDF nominalnie18 | 11,3–12,3 mm według korpusu |
| Tylne ograniczniki rzędów | 4 | laminat25+18 ze spoiną roboczo0,2 | 39,3–40,3 mm |
| Przekładki między wkładami | 4 | MDF nominalnie10 | proponowane7,8 mm |

Każdy z16 rekordów zawiera w JSON identyfikator części, operację, zakres
wymiaru i minimalny naddatek przy zadanym rozrzucie półfabrykatu. Wszystkie
naddatki są dodatnie w tym modelu. Nie jest to potwierdzenie płaskości,
przydatności materiału po zdjęciu warstwy ani możliwości wykonawcy.

Zmiana przekładki rozwiązuje problem nominalnego8 mm w szczelinie8 mm:
płyta8,5 nie może się tam zmieścić bez obróbki. Propozycja7,8±0,1 daje
**łącznie0,1–0,3 mm luzu tylko wtedy, gdy przestrzeń między wkładami wynosi
dokładnie8 mm**. Wymiary i ustawienie rzeczywistych wkładów muszą wejść do
końcowego stosu tolerancji. Przekładkę wycentrowano w nominalnej szczelinie;
luz wpływa na docisk i możliwe stukanie, więc wymaga sprawdzenia podkładek
kontaktowych i całego łańcucha blokowania. Nie uznano go za bezwarunkowo
właściwy dla gotowego urządzenia.

## Najważniejszy wynik tolerancji

Samo odjęcie nominalnej szczeliny nie zapewnia pasowania. Dla styku końca
szyny przyjęto niezależne pozostałe błędy po obliczeniu geometrii:
cięcie±0,1, ustawienie±0,1 i pomiar powierzchni odniesienia±0,05 mm.
Szczelina0,2 ma wtedy zakres **−0,05…+0,45 mm**. W skrajnym przypadku
powstaje wcisk zamiast spoiny. Są to jawne założenia budżetu błędów,
nie pomiary wykonawcy; nie doliczamy ponownie całego rozrzutu grubości,
który już uwzględnia model wymiarowania.

Alternatywny budżet±0,05 dla każdej z trzech składowych dawałby0,05–0,35 mm,
ale **nie potwierdzono takiej dokładności procesu** i nie wolno zamienić
jej w wymóg „spełniony” przez wpisanie do pliku. Potrzebny jest przyrząd,
kontrola po obróbce i kwalifikacja kleju dla faktycznego zakresu szczelin.
Dostawca nie potwierdził w tym etapie nowej tolerancji.

Pozostałe wskaźniki wrażliwości:

- Pas metalu przy przedniej śrubie K36: nominalnie5 mm od krawędzi otworu,
  minimum4,75 przy założonych błędach krawędzi±0,1, osi±0,1 i promienia±0,05.
  To geometria, **nie obliczona nośność**.
- Rezerwa narzędzia przy froncie:0,9 mm nominalnie,0,55 po założonym budżecie
  dodatkowych błędów frontu0,15, osi0,1 i promienia narzędzia0,1.
  Nadal brak rzeczywistej nasadki, rękojeści i kontroli dłoni.

## Pomiary, kontrole i ograniczenia

[Szablon25 pomiarów](../dane/k37_pomiary_banku.json) zawiera wartości `null`.
Tryb `--require-measured` odmawia przy ich braku, przed zapisem wyników.
Nawet uzupełniony szablon dotyczy wyłącznie banku: uruchomienie K37 nadal
używa syntetycznego korpusu22 mm. Nie jest to zbiorczy eksport do CNC.

Wykonano50 zmian pojedynczego parametru (dolna/górna wartość dla25 części),
kontrolę dodatnich wymiarów i niezmienionych powierzchni podparcia,
cztery kombinacje grubości wręgi i metalu pod kątem kolizji z płatami,
kontrolę16 naddatków, niezależne obliczenie skrajnej szczeliny i test odmowy
bez zmiany plików. **50 prób nie jest pełnym iloczynem kombinacji25 parametrów**
ani ponowną kwalifikacją25 torów ruchu K36. Pełne połączenie niepewności
wymaga następnego sprawdzenia obwiedni; brakujące wyniki nie zostały
zastąpione licznikiem prób jednostkowych.

[Kod](../skrypty/k37_material_i_operacje.py) · [test](../skrypty/sprawdz_k37.py)
· [model,16 operacji i wyniki](../wyniki/k37_material_i_operacje.json)
· [manifest](../wyniki/k37_manifest.json).
Odtworzenie: `python skrypty/k37_material_i_operacje.py`, następnie
`python skrypty/sprawdz_k37.py`. Przełącznik `--require-measured` ma odmówić
przy dołączonym szablonie. Nie zmieniono starszych DXF.

**Następny krok: połączyć korpus, bank i wkłady w jednym wejściu pomiarowym,
a następnie sprawdzić tory i styki przy skumulowanych tolerancjach.**
Wynik ma oddzielać wymagany poziom wykonania od potwierdzonej zdolności
wykonawcy. Kwalifikacja kleju, nośności metalu/gwintów/spoin, kosza i terminala
pozostaje otwarta. Nie wydano plików gotowych do frezowania.
