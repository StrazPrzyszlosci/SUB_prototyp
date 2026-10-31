# P37 — protokół pierwszych pomiarów MDF i spoin (do uzupełnienia)

**Status:** to jest **plan przyszłych pomiarów**, a nie ich wyniki. W tabeli `P37_szablon_pomiarow_MDF_i_spoin.csv` pozostawiono pola puste — nie należy ich zastępować fikcyjnymi liczbami.

## Co mierzymy najpierw i dlaczego?

W raporcie 095 policzono czułość MES na cztery parametry. Sama częstotliwość f1 nie identyfikuje osobno E, rho i podatności spoin: różne zmiany mogą dać podobny efekt. Wybrano więc **cztery niezależne obserwacje**: masę/objętość próbki, krzywą siła–ugięcie MDF, poślizg spoiny pod ścinaniem oraz obrót spoiny pod momentem.

| Zadanie | Minimalny zestaw | Wynik |
|---|---|---|
| Gęstość i wilgotność MDF | minimum 3 próbki dla 22/44 mm i orientacji, masa oraz wszystkie wymiary | rozkład gęstości z niepewnością pomiarową |
| E statyczny MDF | minimum 3 próbki na orientację, kilka małych obciążeń w zakresie sprężystym | nachylenie krzywej N/mm, dopasowany E |
| Spoina MDF–MDF | ≥3 powtarzalne próbki rzeczywistego przekroju, rejestracja siły i poślizgu | sztywność translacyjna *dla dokładnie tej geometrii* |
| Naroże i wręga | ≥3 próbki, zadany moment i mierzony obrót | sztywność obrotowa i ograniczenia zniszczenia |
| Długi czas i starzenie | wybrane połączenia w czasie, wilgotności i temperaturze | pełzanie, wrażliwość środowiskowa |

**Bezpieczeństwo:** nie wykonywać prób łamania obciążonych elementów bez osłon i bezpiecznych narzędzi. Pomiary silnie zależą od geometrii próbki i prędkości obciążenia; współczynników N/mm nie wolno bez jednostek przenosić na k_trans w N/m² użyty w MES.

## Reguły opracowania

1. Wypełnić CSV surowymi danymi. Zachować datę, jednostki, temperaturę i wilgotność.
2. Nie wyznaczać E z jednego punktu; dopasować liniową część krzywej i sprawdzić histerezę.
3. Oddzielić rozrzut próbek od niepewności aparatury. Podawać przedziały lub granice.
4. Zbudować cyfrową próbkę w MES **z taką samą geometrią i warunkami brzegowymi**, aby oszacować E/parametry spoin.
5. Dopiero potem powtórzyć globalny MAC, a po uzyskaniu dobrych wyników — obciążenia z P35A i model strat maty.

Brak pomiarów nadal blokuje wiarygodne **zwolnienie do frezowania CNC**.