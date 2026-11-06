# K40. Obudowa subwoofera 1080 × 432 × 500 mm

Wydanie do kontroli geometrii i wyceny. Produkcja całej obudowy wstrzymana. Wymiary w mm. W pliku zrodlo.json podano, czy użyto przykładu nominalnego, czy karty pomiarowej.

## Co zawiera pakiet

90 rysunków MDF, po jednej części w pliku. Obejmuje 9 części korpusu i wręg, 4 ścianki prowadnic, 16 szyn, 4 górne listwy, 4 przekładki, 5 elementów tylnych oporów oraz 48 ścianek ośmiu wkładów. Wykaz podaje obrys i grubość po obróbce. Pięć osobnych rysunków metalowych obejmuje także różne rzuty tej samej części. Do ich interpretacji służą opisy K32, K33 i K36 w repozytorium.

MDF ma wspólną bazę lokalną w lewym dolnym rogu obrysu, skala 1:1. OBRYS oznacza kontur zewnętrzny, OKNO otwór wewnętrzny przelotowy, OTWOR_PRZELOT granicę otworu, REFERENCJA otwór kosza wymagający potwierdzenia. Obrysy przedstawiają wymiary detalu po obróbce. Korekcję promienia narzędzia wykonuje CAM. W oknach wręg zaprojektowano narożniki R4. Dystanse i części laminowane wymagają doprowadzenia do grubości podanej w wykazie.

## Warunki wydania do produkcji

- Przód FR1/FR2, korekta K41. [Karta Dayton RSS390HF-4](https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf) podaje Ø388,4 kołnierza, Ø355,8 wycięcia, grubość kołnierza 10,5 i wysokość całkowitą 178 mm. Osiem otworów w kołnierzu ma Ø6,5 na okręgu Ø368 mm. W obu rzutach DXF wspólny środek to X231/Z250. Przyjęto ustawienie pierwszej osi w stronę +X i kolejnych co 45 stopni. Warstwy KOSZ_REF, PCD_REF i REFERENCJA wyłączyć z automatycznego CAM. Osadzenie, uszczelka i końcowe wiercenie w MDF zależą od wybranego mocowania. Przykład M5 z otworem Ø5,5 zostawia nominalnie 3,35 mm MDF do krawędzi wycięcia.
- BACK wymaga wyboru terminala lub przepustu, jego położenia i rysunku otworu. Sprawdzić głębokość całego zestawu z osprzętem i przewodami względem limitu 500 mm.
- Na podstawie grubości partii MDF oraz prób klejenia uzupełnić kartę K38. Wykonać próbę rzędu K39 i dobrać dystanse. Przekładki 6,9 mm dotyczą przykładowego odstępu 8 mm.
- Potwierdzić gwinty, spoiny, materiał i nośność blokad oraz połączeń z MDF. Zweryfikować bilans netto dla zainstalowanego osprzętu. Po zmianach przeliczyć tory i ponownie wygenerować komplet.
- Wykonawca dobiera narzędzia, mocowanie, kolejność operacji, naddatki i parametry maszyny. Przed rozkrojem sprawdzić w CAM obróbkę każdej strony, głębokości, orientację płyt, jednostki i kompensację. Archiwum zawiera geometrię CAD do tego etapu.

## Docisk do próby K39

Dla sztywnego stosu między dwiema liniowymi podporami osiowymi o sztywnościach k1 i k2 przemieszczenie pod siłą F ma wartość F/(k1+k2). Większa zmiana reakcji wynosi F razy max(k1,k2)/(k1+k2). Przy obu kierunkach obciążenia docisk wstępny musi przekraczać tę wartość, aby zachować kontakt. W scenariuszu K32, F = 165,943 N, granica wynosi 82,97 N dla równych sztywności lub 124,46 N dla stosunku 3:1. Szczytowa reakcja po przeciwnej stronie rośnie o odpowiednią zmianę. To przesiew quasi-statyczny przy założeniu sztywnego korpusu, bez tarcia, rezonansu i pełzania. Do wpisania limitów K39 potrzebne są rzeczywiste sztywności, założenie obciążenia użytkowego i dopuszczalna reakcja całego mocowania.

Odtwarzanie z katalogu repozytorium poleceniem `python skrypty/k40_pakiet_dxf.py pakiet.zip`. Opcja `--karta-fit karta.json` stosuje pomiary przy wyznaczaniu proponowanych wymiarów. Ten tryb również wymaga oceny technologicznej.
