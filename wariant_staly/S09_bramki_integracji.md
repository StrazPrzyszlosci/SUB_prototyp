# S09. Zintegrowane bramki do budowy pary ze stałym litrażem

Stan 12.11.2026. Ten rejestr dotyczy WYŁĄCZNIE gałęzi badania/stala-obudowa-2-2 i korpusu A 102 l. Nie dopisywać do README i nie uznawać paczek wariantu regulowanego za produkcyjne rysunki obudowy stałej.

## Zamknięte na poziomie modelowym
- S01: decyzja robocza RSS390HF-4 + 102 l NETTO, wariant A; trzy proporcje porównane, A wybrane do obu orientacji.
- S01: dwie jednostki, niezależne kanały DSP subów i po 3 kanały dla każdego monitora; porównane scenariusze pola pokoju.
- S02/S03: uproszczony MES korpusu i niezależna metoda płyty; wrażliwość na sztywność spoin i pierścienia.
- S04/S05: głębokość z osłoną i koncepcja bocznego wyjścia przyłącza; brak przymiarki hardware.
- S06: 16 nominalnych formatek na parę, bilans 101,9861 l.
- S07: osiowy odstęp kosza od wręgi i metoda sprawdzania przejścia przez złożony front.
- S08: niezależne obwiednie tolerancji litrażu oraz identyfikacja ryzyka wcisku wręgi.

## Otwarte bramki, w kolejności technicznej

| Bramka | Brakujący dowód | Kryterium przejścia | Stan |
|---|---|---|---|
| M1 material/spoiny | Rzeczywista partia MDF, próby klejenia, wartości E, wilgotność, trwałość | Dokumentacja rzeczywistych materiałów i bezpieczne połączenia | HOLD |
| M2 montaż i tolerancje | Suchy montaż 16 formatek i wręgi, wymiary po obróbce | Dodatni kontrolowany luz, kwalifikowany klej, zamknięcie objętości S08 | HOLD |
| M3 front i przetwornik | 8 osi FR1/FR2/pierścień, próba S03, pomiar przejścia S07 | Demontaż od przodu, pełny docisk i szczelność bez utraty nośności | HOLD |
| M4 gniazdo i kaseta | Rzeczywisty wtyk, przepust, przewód, siatka i tkanina | Brak kolizji z Xpeak, prześwit i serwis w 450 mm, brak przecieków | HOLD |
| M5 praca mechaniczna | MES po aktualizacji materiałów, masa i środek masy, stopki pod pion/poziom | Stateczność, brak rezonansów zabudowy, udokumentowane siły i ugięcia | HOLD |
| E1 tor mocy | Faktyczny wzmacniacz i zasilacz dwóch kanałów | Z(f), napięcie, prąd szczytowy, temperatura, clipping i ochrona elektryczna | HOLD |
| E2 DSP | Model urządzenia, rzeczywisty timing i limitery | Headroom 9 dB EQ, HP, X(T), ograniczenie U/I i fail-safe pod obciążeniem | HOLD |
| A1 akustyka jednej sztuki | Prototyp w 102 l, impedancja i pomiary | SPL 20-40 Hz, THD/IMD, kompresja, brzęczenie maskownicy | HOLD |
| A2 system 2.2 | Dwie sztuki i rzeczywiste monitory 3-drożne | Rzeczywiste transmitancje, opóźnienia, faza i odsłuch w sweet spot | HOLD |
| CNC | M1-M5, przegląd wykonawcy i CAM | Jednoznaczne rysunki z tolerancjami oraz protokół odbioru | HOLD |

## Najbliższe czynności możliwe bez sprzętu
1. Przenieść docelowe pozycje wręgi, kołnierza, gniazda i osprzętu do JEDNEGO parametrycznego modelu korpusu A, bez rozwiązań regulowanych; sprawdzić kolizje i sumę objętości.
2. Wykonać alternatywną, niezależną kontrolę siatki MES ze zginaniem przez grubość i podatnymi spoinami; model nie może przypisywać nominalnego idealnego pierścienia realnemu złączu.
3. Przygotować osobne rysunki do prób FR1/FR2/pierścienia, wręgi i przepustu, wyraźnie oznaczone NIE CNC, z kartami pomiarowymi S03/S07/S08.
4. Zestawić dopasowanie fizycznej końcówki mocy i miniDSP, gain structure oraz zagrożenia przy rozruchu. Brak sprzętu oznacza analizę katalogową, nie kwalifikację limiterów.
5. Przygotować warunki pomiarów jednej skrzyni i późniejszej pary, z rozróżnieniem pól swobodnych i efektów pokoju.

Decyzja: utrzymać 102 l jako jeden ustalony cel projektowy, nie wracać do układu 100/120/150 l. Wyjść poza 102 l tylko w wyniku nowej, uzasadnionej zmiany wymagań i jawnej rewizji decyzji, a nie jako kolejny regulowany wariant. Na tym etapie żadna część nie jest dopuszczona do seryjnego CNC.
