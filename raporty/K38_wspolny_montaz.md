# K38. Montaż wkładów i dobór podkładek

6 listopada 2026. CNC HOLD. Wspólna karta obejmuje 9 płyt korpusu, 25 części prowadnic i mocowań oraz 48 ścianek ośmiu wkładów. W fazie montażu wpisuje się także gabaryty gotowych wkładów, ich lewe współrzędne X w przyrządzie, 16 grubości po obróbce i 20 wysokości podparcia.

W syntetycznej sekwencji 150 → 120 → 100 l sprawdzono 42 czynności przy faktycznej kolejności zakładania elementów. Model obejmuje drogę przez front, okna R4, szyny, inne wkłady, przekładki, metalowe blokady i obwiednię narzędzia. Opuszczenie na podporę i dosunięcie blokady do wręgi kończy się na styku. Odwrócenie kolejności daje tę samą drogę geometryczną. Dostęp dłoni, przechylanie, sprężyste podkładki i drgania wymagają próby fizycznej.

| Wynik przykładu | K37 | Wariant próbny K38 |
|---|---:|---:|
| Przekładka dla zmierzonego odstępu 8,0 mm | 7,8 mm | 6,9 mm |
| Dolna granica luzu przy bliższym wkładzie | −0,35 mm | 0,10 mm |
| Szczelina końca szyny po złożeniu błędów | −0,05 do 0,45 mm | 0,10 do 0,60 mm |
| Czynności z dodatnim prześwitem poza zamierzonym kontaktem | 34/42 | 42/42 |

Założono błąd pozycji wkładu 0,15 mm, wymiaru 0,10 mm i grubości przekładki 0,10 mm. K38 odejmuje 1,10 mm od odstępu mierzonego dla konkretnej pary i zaokrągla wynik w dół do 0,1 mm. Dla połączeń korpusu i prowadnic przyjęto próbnie 0,35 mm na stronę. Klej wymaga kwalifikacji dla całego zakresu szczelin. Obwiednie 1024 zestawów grubości korpusu i prowadnic również przepuszczają 42 czynności dla referencyjnych gabarytów wkładów. Wynik opisuje kontrolowane przesunięcia osiowe.

## Ile miejsca pozostaje na docisk

Po dosunięciu metalowej blokady trzeba wypełnić sumę luzów na obu końcach stosu. W przykładzie K38 rzędy z dwoma dużymi wkładami dają 6,9 mm, a rząd z dwoma małymi 10,1 mm. Po zsumowaniu błędów dwóch powierzchni oporowych, obu wkładów i przekładki zakresy wynoszą odpowiednio 6,1 do 7,7 mm i 9,3 do 10,9 mm. W stanie 120 l długi ogranicznik przy jednym dużym wkładzie pozostawia nominalnie 3,8 mm. Wartości dotyczą sumy przestrzeni dla podkładek i ewentualnych sztywnych dystansów.

Dobór wymaga pomiaru siły w funkcji ugięcia podkładki. Jeżeli dopuszczalne siły odpowiadają łącznej wysokości roboczej podkładek od Hmin do Hmax, a zmierzony luz leży między Gmin i Gmax, nominalny sztywny dystans ma dolną granicę max(0, Gmax − Hmax + e) i górną Gmin − Hmin − e. Symbol e oznacza tolerancję dystansu. Gdy przedział jest pusty, trzeba dokładniej zmierzyć konkretny rząd albo zmienić podkładkę. Przykładowo rozrzut luzu 1,6 mm i dystans ±0,1 mm wymagają co najmniej 1,8 mm zakresu roboczego podkładek. Kolejna próba powinna ustalić siłę i trwałe odkształcenie po czasie dla wybranego materiału oraz sprawdzić pełne podparcie i możliwość ponownego wyjęcia wkładów.

[Karta pomiarowa](../dane/k38_karta_pomiarow.json) · [wyniki](../wyniki/k38_zlozenie.json) · [dobór dystansu](../skrypty/k38_docisk.py)

Uruchomienie z katalogu repozytorium:

```
python skrypty/k38_zlozenie.py --mode preview --family --output /tmp/k38.json
python skrypty/k38_zlozenie.py --mode stock --input karta.json --output /tmp/stock.json
python skrypty/k38_zlozenie.py --mode fit --input karta.json --output /tmp/fit.json
```

Skopiuj kartę i wpisz identyfikatory protokołów. Tryb stock wylicza wymiary przed montażem. Tryb fit zestawia stan z karty z propozycją ponownej obróbki. Wpis reference_design określa geometrię wykonaną. Wzorzec zawiera puste pola. Wydanie CNC wymaga jeszcze pomiarów, potwierdzenia docisku, połączeń materiałowych i osprzętu głośnika.
