# Front subwoofera: otwór, masa, mocowania i kontakt

Wykonane eksperymenty: [raport 033](../raporty/033_front_otwor_kosz_i_styk_jednostronny.md).

**Fizyka modelu:** otwór usuwa materiał i masę, kosz dodaje masę i ścieżki
sił. Sama częstotliwość pierwszej postaci pełnej płyty nie określa
zachowania frontu z głośnikiem. Mod o najniższym f może być przechyłem
kosza prawie niewzbudzanym przez jednorodne ciśnienie; udziały wymuszenia
muszą być zapisane osobno od uporządkowanych częstotliwości.

## MITC na ogólnej siatce

Stosujemy naturalne współrzędne xi,eta, x=N*xnodes, J=dN/dxi*xnodes.
Naturalne ścinanie to pochodna w pomniejszona o rzut obrotów na kierunek
styczny mapowania. Interpolowane są kowariantne składowe z punktów wiązania
na krawędziach, a dopiero potem wracamy przez J^-1 do składowych kartezjańskich.
Przeniesienie prostokątnego wzoru z samymi dx/dy na dowolny czworokąt
bez tej transformacji nie jest właściwym rozszerzeniem elementu.

Okrąg aproksymowany wielokątem wymaga kontroli liczby segmentów i pola.
Schodkowe usunięcie komórek wprowadza sztuczne naroża; naprężenia w takich
narożach nie mogą zostać uznane za fizyczny szczyt przy gładkim otworze.

## Siły i masa

Ruch względny stożka należy odróżnić od ruchu kosza. Jeżeli M zawiera już
masę całego głośnika, Mmoving*ddot(xrelative) jest sprzężeniem kinetycznym,
a nie następną masą dodawaną do tego samego DOF. Mms obejmuje powietrze;
referencyjne odjęcie w Fs nie identyfikuje niezależnie rzeczywistego Mmd.

Ciśnienie na zamkniętej powierzchni nie tworzy dowolnej siły netto.
Przy zamknięciu otworu zastępczą powierzchnią sprawdzamy sumę pól i nie
doliczamy ponownie Sd*p. Do modelu komory stosujemy ten sam wektor H
do obciążenia ciśnieniem i zmiany objętości H^T*q. Zapewnia to wzajemność
portu i umożliwia niezależny bilans mocy.

## Docisk jest stanem mechanicznym

Śruba rozciągana i uszczelka ściskana wymagają różnych warunków aktywności.
Przykładowa energia dyskretna ma dodatnie składniki max(gap,0)² dla
uszczelki i max(delta0-gap_bolt,0)² dla śrub. Parametr kbolt*delta0 nie
jest zachowaną siłą po odkształceniu frontu. Zamiana momentu dokręcania
na siłę wymaga dodatkowych danych o tarciu i gwincie.

Po rozwiązaniu docisku dynamikę można liniować tylko w obszarze, w którym
aktywny zestaw kontaktów pozostaje ten sam. Dla pojedynczej sinusoidy
test statyczny stan ± sqrt(2)*moduł RMS obejmuje cały cykl w danym punkcie.
Przekroczenie oznacza potrzebę rozwiązania zmiennego styku, nie obliczony
czas otwarcia ani pewny hałas lub przeciek. Otwarcie jednego punktu
mechanicznego nie identyfikuje automatycznie połączonego kanału powietrza.

Nośność otworów, ścinanie od ciężaru, pełzanie, nieszczelność i zmęczenie
wymagają osobnych danych i modeli. Zbilansowana energia liniowego modelu
nie kwalifikuje nieznanej uszczelki, gwintu lub MDF3D.
