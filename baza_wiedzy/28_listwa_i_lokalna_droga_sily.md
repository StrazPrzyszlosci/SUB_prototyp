# 28 — Listwa i lokalna droga siły

**Wyprowadzenie i symulacja:** [raport 040](../raporty/040_listwa_stalego_frontu_i_droga_sily.md).

Listwa klejona do dwóch płyt dodaje bryłę, masę i dwie powierzchnie
przenoszenia sił. Nie jest idealnym unieruchomieniem krawędzi. Może
zmniejszyć naprężenie jednej spoiny i zwiększyć je w sąsiedniej.
Wspólny moduł, geometria i podatność MDF współokreślają wynik.

## Dwie miary potrzebują odrębnej kontroli

Globalna podatność C=HᵀK⁻¹H waży całe pole przemieszczeń. Naprężenie
lokalne zależy od gradientów i skoku przemieszczenia po obu stronach spoiny.
Mała zmiana C nie ogranicza automatycznie błędu lokalnego RMS lub maksimum.
W P19F względna korzyść C listwy 30 mm jest stabilniejsza od pól spoin.
Nie wolno przenieść progu zbieżności jednej wielkości na wszystkie inne.

## Ciśnienie działa na zmienioną geometrię

Po dodaniu listwy zakryte obszary przestają być granicą gazu, a odsłonięte
ściany listwy stają się jego granicą. Samo dodanie masy i K bez korekty
portu H daje inny eksperyment. Kontrolą są bilans sił/momentów oraz
zmiana tensorów pracy afinicznej o −Vlistwy·I.

Zamrożone H może służyć porównaniu samej sztywności. Trzeba je oznaczyć
jako kontrolę, bo nie jest rzeczywistym obciążeniem zmienionej komory.
W bilansie Vb listwa jest ciałem stałym; materiał porowaty z P09C wymaga
odrębnego rozdzielenia włókien i dostępnych porów.

## Podmodel i granice nośności

Następny podmodel powinien zagęszczać również sąsiednie płyty, przenosić
pole brzegowe z pełnej ramy i sprawdzać odległość sztucznej granicy.
Bardzo sztywne połączenie niezgodnych siatek wymaga kontroli interpolacji
oraz rozdzielenia wpływu dyskretyzacji i fizycznej koncentracji.

Naprężenia referencyjnego modelu nie identyfikują adhezji, Gc, pełzania
lub S–N. Dobór kleju potrzebuje tych danych albo jawnych warunkowych
wymagań; klasa D3/D4 i moduł wolnej folii nie zamykają tej decyzji.
