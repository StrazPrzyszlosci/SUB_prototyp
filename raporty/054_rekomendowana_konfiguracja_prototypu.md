# Raport 054 — rekomendowana konfiguracja pierwszego prototypu

Data: 2026-10-30. **Wybrano konfigurację do dalszego opracowania prototypu.**
To rekomendacja inżynierska na podstawie modeli, nie ukończona dokumentacja
wykonawcza ani potwierdzenie osiągów gotowego urządzenia. Publikacja wyników w PR została ponownie zlecona przez użytkownika.

## Jeden rekomendowany wariant

| Element | Rekomendacja | Status / uzasadnienie |
|---|---|---|
| Głośnik | **Dayton Audio RSS390HF-4, 15″, 4 Ω** | Dane producenta + porównanie wszystkich 27 konfiguracji; najlepsze minimum badanego konserwatywnego scenariusza |
| Topologia | Zamknięta; jeden stały front pod C02 | Wymaganie użytkownika |
| Punkt startowy | **Około 120 l netto powietrza** | 10 nominalnych wkładów daje 118,84 l przy rezerwie 8 l; dokładność zależy od rzeczywistej wyporności |
| Regulacja | Około **100 / 120 / 150 l** | 16 / 10 / 0 mocowanych, szczelnych wkładów; krok nominalnie 3,06 l |
| Gabaryt korpusu W×D×H | **880×480×500 mm** | Obliczona geometria; pionowo 500×480×880 mm |
| Limit głębokości | Nie przekroczyć 500 mm po dodaniu wystających elementów | Korpus zostawia 20 mm; maskownica, wychylenie i terminal muszą się w tym zmieścić albo trzeba zmniejszyć głębokość korpusu i przeliczyć litraż. Nie zatwierdzono jeszcze maskownicy |
| Materiał | MDF 22 mm, front 44 mm (dwie klejone warstwy) | Model izotropowy + porównanie frontów; rzeczywista jakość laminowania i spoin wymaga kontroli |
| Pozycja | Oś około 231 mm od lewej i 250 mm od dołu frontu | Blisko środka lewej połowy; niewielkie odsunięcie od skrajnej krawędzi. Można odbić lustrzanie |
| Usztywnienia | Dzielić duże panele na pola rzędu ≤280×300 mm, z zachowaniem torów wkładów | Docelowa funkcja konstrukcyjna z modelu płyt; rozmieszczenie i sztywność realnych wręg nie są jeszcze zatwierdzonym rysunkiem |
| Wypełnienie startowe | Zdejmowana tylna warstwa poliestrowa 50 mm | Pole około 0,381 m², objętość obwiedni 19,06 l. Przy założeniu 20 kg/m³: **około 0,38 kg**; nie odejmować 19 l jako litego materiału |
| Wkłady | Nominalnie 180×170×100 mm zewnętrznie, szczelne, ścianki MDF około 8 mm, podparte wewnętrznie | Wzorzec P20/P21; końcowy obrys wraz ze spoinami/okuciami wymaga kontroli. Mocowanie dodatnie we wszystkich orientacjach, nie luźny stos |
| Klejenie | PVAc D3 do prób, np. Kleiberit 303.0; stałe szerokie połączenia i listwy | Kandydat procesu. Brak Gc/S-N/J(t) MDF nie pozwala zatwierdzić trwałości samą klasą D3 |
| Napęd | Zewnętrzna klasa D; projektowy budżet **40 V RMS / 12 A RMS** dla osobnych sinusów | 40 V na czystych 4 Ω odpowiada 400 W, ale głośnik nie jest stałym rezystorem. To wymaganie portu, nie nastawa bezpiecznej mocy |
| DSP | **miniDSP Flex Eight w wersji z 8 wyjściami analogowymi**, bez Dirac w modelu 96 kHz | Dwa suby + dwa monitory trójdrożne; producent potwierdza macierz i wyjścia |
| Filtry początkowe | HP BW2 20 Hz, LP LR4 80 Hz, bez dodatniego EQ do pierwszych pomiarów | Odtwarzalne współczynniki software, nie gotowa ochrona X/T ani wyrównanie do 20 Hz |

Rekomendowana skrzynia ma być platformą prób. Nie należy zamawiać CNC
wyłącznie z tej tabeli: grubość frontu, otwór, wręgi, mocowania wkładów
oraz całkowity obrys muszą tworzyć jeden zweryfikowany rysunek wykonawczy.
Konstrukcja i regulacja zostały wybrane warunkowo; detale wykonawcze pozostają otwarte.
Raport 055 pokazuje, że skrócenie korpusu do 470 mm wymaga też zmiany
układu wkładów: obecny układ kolidowałby z tylną matą na 6 mm.

## Rzeczywisty bilans litrów

Puste wnętrze: 836×414×456 mm = **157,823 l brutto**.
W modelu startowym rezerwa na głośnik, usztywnienia i osprzęt wynosi 8 l;
nie jest to zmierzona wyporność RSS390HF-4. Zakres stresowy 4–11 l daje:

| Wkłady | Nominalne netto [l] | Zakres przy rezerwie 4–11 l [l] |
|---:|---:|---:|
| 0 | 149.44 | 146.44–153.44 |
| 10 | 118.84 | 115.84–122.84 |
| 16 | 100.48 | 97.48–104.48 |

Odjęto także 0,381 l ciała stałego maty przy założonej porowatości 0,98.
Efektywna podatność z matą nie jest tym samym co netto powietrza.
Zmienna masa/gęstość i rzeczywisty opór przepływu materiału mogą wymagać
zmiany grubości; 0,38 kg to punkt eksperymentu, nie udowodnione optimum włókniny.

Sprawdzono 48 odcinków translacyjnych montażu 16 wkładów w pustym
korpusie, przez otwór po wyjętym głośniku. Należy zachować te korytarze
po dodaniu wręg i zamków. Test nie obejmuje narzędzia, dłoni, przewodów,
łączników ani tarcia. Moduły nie są konstrukcyjnym podparciem ścian.

## Dlaczego ten wariant, a nie sam największy skok

RSS390HF-4 daje w przyjętym badaniu dobry dół pasma bez uzależniania
wyboru od pułapu 200 W ciągłych strat miedzi. Około 120 l osiąga plateau
wybranego konserwatywnego kryterium; większy litraż pozostawiono jako
wartościową możliwość eksperymentu, zamiast na stałe budować mniejsze wnętrze.
Front 44 mm ogranicza podatność w przeprowadzonym porównaniu przesuniętego otworu.
Regulacja wkładami zachowuje stały front i nie wymaga uszczelnienia całej
ruchomej przegrody. Jej koszt to masa oraz zmiana przestrzennego portu.

**Najsilniejszy argument przeciw rekomendacji:** duża i ciężka skrzynia
z głośnikiem o mniejszym skoku od RSS390HE-22. Sam model masy korpusu
MDF daje około 36 kg, bez głośnika, wkładów i pełnego osprzętu.
Przy lepszym chłodzeniu i mocniejszym wykorzystaniu napędu HE może być
lepszym wyborem dla maksymalnego SPL. Nie wykazano wyższej jakości THD C02.

Alternatywa 12″: STX W.32.800.8.FCX (C06), jeśli priorytet przesunie się
na mniejszy gabaryt, lub SB34SWPL76-4 (C04) jako inny dobrze opisany kandydat.
Nie nazywamy żadnego najtańszym: zgodnie z zakresem nie badano bieżących cen.
Wariant o większym potencjale przy większym grzaniu: RSS390HE-22 (C11).

## Co może zmienić wybór i jak to rozstrzygnąć

1. Rzeczywiste użyteczne wychylenie/THD C02 okaże się znacznie gorsze niż
   przyjęty margines 0,5–0,8 Xmax. Rozstrzyga stopniowany test ruchu,
   zniekształceń i kompresji, z kontrolą napięcia i temperatury po budowie.
2. Chłodzenie lub BL(T) sprawi, że konserwatywna przewaga C02 zniknie.
   Potrzebne Re po ogrzaniu, kompresja i powtarzalne sygnały z określonym czasem.
3. Dwie skrzynie nie zmieszczą się w realnych miejscach. Suma szerokości
   poziomych to 1,76 m, pionowych 1,00 m; nie dowodzi to miejsca przy monitorach,
   meblach i przejściu. Pozycje użytkownika nadal nie są ustalone.

**Najkrótszy eksperyment rozróżniający litraż i wypełnienie:** w tym samym
prototypie porównać małosygnałową impedancję oraz bliskie pole przy 0/10/16
wkładach, najpierw bez maty, potem z tą samą zważoną matą. Zachować pozycję,
napięcie, temperaturę i pliki surowe. To identyfikuje obciążenie oraz
wykrywa przeciek; sam pomiar impedancji nie rozdziela wszystkich strat.
Pomiary w pokoju nie stają się pomiarem wolnego pola przez przeliczenie odległości.

## Ochrona i gotowość

Compressor miniDSP nie jest zidentyfikowanym obserwatorem wychylenia
ani temperatury. 40 V/12 A to możliwości modelowego napędu, a nie zgoda
na pełny sygnał. Nowego presetu ochronnego nie zatwierdzono: współczynniki
HP/LP nie zastępują limitu ruchu, pamięci cieplnej i kalibracji toru DAC–wzmacniacz.
Wyniki P24A są punktem odniesienia, nie certyfikatem nowej geometrii.

Wyłoniono **jedną rekomendację prototypu**, ale nie ogłoszono zamknięcia
wszystkich 30 pakietów, dokumentacji wykonawczej ani końcowego PDF.
Otwarte są pełne sprzężenie ścian/spoin/wkładów, rzeczywista identyfikacja
materiału i napędu, parametry ochrony, dokładny obrys maskownicy oraz pomiary.

## Źródła i odtworzenie

Podstawą są raporty 028, 038–051 oraz nowe 052–053. Dane katalogowe
pozostały niezmienione. Ponowny odczyt źródeł z 2026-10-30 zapisano w
`dane/zrodla/P29_weryfikacja_zrodel_20261030.json`.

- [RSS390HF-4 — producent](https://daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm)
- [Karta producenta RSS390HE-22](https://www.parts-express.com/pedocs/specs/295-292--dayton-audio-rss390he-22-spec-sheet.pdf)
- [Karta producenta UMII15-22](https://www.parts-express.com/pedocs/specs/295-714--dayton-audio-UMII15-22-spec-sheet.pdf)
- [Flex Eight — producent](https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight)
- [Routing i przetwarzanie](https://docs.minidsp.com/product-manuals/flex-eight/signal-flow/index.html)
- [Kleiberit 303.0 — TDS](https://www.kleiberit.com/fileadmin/Content_new/Produktinformationen/303.0/dbe3030_KSE.pdf)

Nowe pliki i hashe: `wyniki/manifest_rekomendacji_P29.json`.
