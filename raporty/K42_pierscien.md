# K42. Próbne mocowanie kosza na pierścieniu uwięzionym między płytami

Do próby wybrano stalowy pierścień Ø400/358 × 6 mm z ośmioma gwintami M5×0,8 na Ø368. Jest osadzony w kieszeni na przedniej stronie FR2 i zakryty przez FR1. Śruba dociska kołnierz do FR1, a stal opiera się o tył FR1. Dwa ustalacze przeciw obrotowi umieszczono na osi pionowej na Ø388. Otwory ustalaczy oraz sposób ich trwałego zamocowania w metalu wymagają doboru pasowania. Do próby przyjąć występ kołków Ø4 o 4 mm za metal. Podczas klejenia ustawić współosiowo osiem gwintów i ochronić je przed klejem. Gwint po sklejeniu jest trudno wymienialny. Uszczelnienie i zabezpieczenie przed drganiami należy sprawdzić.

[Trzy DXF do próby](../dokumentacja/cnc/K42_PROBA_HOLD) · [generator i kontrola 128 kombinacji wymiarów](../skrypty/k42_pierscien.py) · [rysunek Daytona](https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf)

FR1 i FR2 pokazano od przodu obudowy, w tej samej orientacji X/Z. FR2 obrabiać od powierzchni stykającej się z FR1. Kieszeń Ø400,4 na głębokość 6,20 od powierzchni. Osiem otworów ulgi Ø6,5 pogłębić o kolejne 4 mm od dna kieszeni, dwa gniazda kołków Ø4,2 o kolejne 5 mm. Następnie wyciąć Ø355,8. W stali oznaczenie Ø5 na warstwie GWINT wskazuje nominalny gwint, operator dobiera narzędzie do gwintowania. Rysunki przyjmują płaski montaż kosza na uszczelce. Używać jako osobny wariant próbny, bez łączenia operacji z DXF K41.

| Sprawdzana wielkość | Wynik nominalny |
|---|---:|
| MDF między otworem FR1 Ø5,6 a wycięciem | 3,30 mm |
| Stal od obwiedni gwintu Ø5 do wewnętrznej krawędzi | 2,50 mm |
| Wewnętrzna krawędź stali względem wycięcia MDF | 1,10 mm na promieniu |
| MDF za najgłębszym gniazdem w FR2 grubości 22 mm | 10,80 mm |
| Masa pierścienia brutto przy przyjętej gęstości 7850 kg/m³ | 1,18 kg |

Przesiew długości śruby M5×40 uwzględnia niezależne krańce siedmiu przedziałów. Długość 39,8 do 40,2 mm, podkładka 0,9 do 1,1, kołnierz 10,3 do 10,7, ściśnięta uszczelka 0,7 do 1,3, FR1 21,5 do 22,5, odsunięcie początku stali od tyłu FR1 od 0 do 0,65, stal 5,9 do 6,1. Są to założone granice przesiewu. Najmniejsze wejście trzpienia w stal wynosi 3,55 mm przed odjęciem faz i wybiegu gwintu. Największy występ za stal wynosi 0,90 mm, przy nominalnym pogłębieniu 4 mm. Wynik nie kwalifikuje M5×40 pod względem nośności. Sprawdzić również długość rzeczywistej części gwintowanej.

Luz promieniowy śruby Ø5 w FR1 wynosi 0,30 mm. Niezależne błędy położenia osi ±0,2 mm w X i Z dają do 0,283 mm przesunięcia jednej osi względem idealnej. Jeżeli obie części są wykonane z takim błędem względem wspólnego układu, różnica może osiągnąć 0,566 mm. Taki proces odpada. Wymagana jest wspólna baza i sprawdzian złożenia ośmiu osi. Nominalny luz pierścienia w kieszeni 0,20 mm na promieniu również wchodzi do budżetu rejestracji.

Następna próba obejmuje pomiar pełnych zwojów, rejestracji otworów po sklejeniu, obciążenia utrzymującego docisk uszczelki, odcisku i odkształcenia MDF oraz utraty siły po czasie i cyklach wykręcania. Trzeba dobrać siłę dopuszczalną na podstawie badań materiału i węzła, sprawdzić orientację narzędzia przy koszu i szczelność. Pierścień mieści się w grubości laminatu. Sprawdzenie przekroju nominalnego nie zastępuje kwalifikacji złącza. CNC HOLD.
