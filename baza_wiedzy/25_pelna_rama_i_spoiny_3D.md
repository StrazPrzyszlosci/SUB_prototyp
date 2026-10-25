# Pełna rama i połączenia 3D

Wykonane badania: [P18C](../raporty/035_pelna_rama_3D_spoiny_i_podparcie.md)
i [P19D](../raporty/036_spoiny_3D_i_wirtualne_odspojenie.md).

## Od pojedynczej płyty do całej skrzyni

Normalne przemieszczenia ściany nie opisują jej rozciągania i ścinania.
Połączenie ścian w przestrzeni wymaga zgodnego przekazywania wszystkich
składowych siły i momentu. Nieruchoma krawędź pojedynczej płyty jest
szczególnym podparciem, a nie automatycznym modelem sąsiedniej ściany.

W siatce bryłowej źle dobrany element może zawyżać sztywność przy zginaniu.
Dodatkowe pola odkształcenia wymagają zerowej średniej, niezależności
i kontroli stabilności. Spełnienie patch testu jest konieczne, ale nie
dowodzi dokładności wszystkich geometrii. Własnej implementacji nie
utożsamiamy z elementem komercyjnego programu o podobnej nazwie.

## Połączenia niezgodnych siatek

Całkujemy różnicę interpolowanych przemieszczeń na wspólnej powierzchni.
Pola przecięcia są dzielone tak, aby nie obciążać spoiny na obszarze bez
materiału. Dodatnia energia skoku zapewnia wzajemność i przeciwne siły;
zgodna interpolacja położenia zachowuje globalny ruch sztywny.

Zapisujemy osobno średnią, przestrzenne RMS, część rozciągającą i
próbkowane maksimum. RMS bez znaku łączy ściskanie i rozciąganie.
Żadna z tych liczb nie staje się lokalnym dopuszczalnym naprężeniem
MDF lub spoiny na podstawie samego modułu lub klasy wodnej kleju.

## Globalne ruchy i podparcie

Swobodna zdrowa rama ma sześć ruchów sztywnych. Nie należy usuwać ich
poprzez przypadkowe zamocowanie przy obliczaniu naturalnej odpowiedzi.
W statyce odciążenie inercyjne rozdziela niezrównoważone obciążenie
od odkształcenia wewnętrznego; nie jest fizycznym punktem mocowania.

Podpory wprowadzają własne przemieszczenia, obroty, tarcie i możliwość
utraty docisku. Ich sztywność i straty trzeba podać jawnie. Jednostkowej
siły na kosz nie nazywamy siłą silnika: siły elektromagnetyczne działają
wewnętrznie między ruchomą częścią i statorem.

## Ciśnienie i objętość

Ciśnienie na zamkniętej powierzchni ma zrównoważone siły i momenty.
Otwór należy zamknąć odpowiednim portem mechanicznym; nie dodawać
ponownie Sd*p po wcześniejszym zastosowaniu całej powierzchni zamknięcia.
Ten sam H przenosi ciśnienie i zmianę objętości Hᵀq. Dylatacja daje
odrębną kontrolę geometrycznego V, a nie finalnego V netto z głośnikiem.

## Wirtualne odspojenie

Zmiana minimalnego potencjału po skończonym usunięciu spoiny daje
średnią energię na pole tego ubytku. Aby mówić o G, Gc lub trwałości,
potrzebne są zbieżność, geometria czoła pęknięcia, tryb obciążenia i
dane odpowiedniego materiału. Po odspojeniu należy zachować możliwość
ściskania powierzchni; całkowite usunięcie kontaktu zmienia problem.

Niepełna zbieżność ilościowa ma pozostać wynikiem negatywnym.
U-021 utrzymuje front stały pod jeden przetwornik; dalszy rachunek
dotyczy geometrii i sztywności tego połączenia, a jego nośność i trwałość
pozostają odrębnymi bramkami.

## Próg sztywności

Przy K=Kfixed+beta*Kvariable i stałym porcie obciążenia podatność
ma pochodną dC/dbeta=−qᵀKvariable q. Dodatnia energia połączeń daje
monotoniczny problem wyznaczenia progowego modułu. Eeff/t musi być
interpretowane razem z przyjętym prawem ścinania i grubością warstwy.
Wynik [P19E](../raporty/037_staly_front_wymagany_modul_spoin.md) określa
sztywność modelu dla zadanej zmiany C, nie wytrzymałość, Gc lub życie.
