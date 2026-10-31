# Raport 086 — P34B: weryfikacja obciążeń i blokowania wkładów

**31.10.2026 · 324 scenariusze sił i masy 20 modułów, 3 litraże × 3 gęstości MDF × 3 grubości ścianek × 4 przyspieszenia × 3 różnice ciśnienia.**

![Jakie obciążenia powinien przenosić mechanizm blokujący wkłady?](../wyniki/p34b_sily_mocowania_wkladow.svg)

## Pytanie konstrukcyjne

Regulacja objętości 100/120/150 l oznacza wyjmowanie i wkładanie **sztywnych, szczelnych modułów** przez otwór głośnika. P30E sprawdził nominalnie 20/20 torów wkładania w uproszczonej geometrii przy obwiedni 6 mm. Nie oznacza to jeszcze, że zamocowane moduły **pozostaną nieruchome** podczas pracy subwoofera, przenoszenia i transportu. Dla ich rzeczywistych śrub, zatrzasków i uszczelek nie ma projektu ani pomiaru.

## Co policzono?

Pudełka o wymiarach [mm]: 8 tylnych dużych **210×120×100**, 8 przednich dużych **210×150×100**, cztery małe **180×100×100**. Dla gęstości MDF 650/730/800 kg/m³ i grubości ścian 6/8/10 mm policzono masę zamkniętej cienkościennej bryły jako `rho·(Vzew−Vwew)`. Nie uwzględniono złączy, uszczelki, kleju czy lakieru.

Przy przyspieszeniach umownych 1/3/5/10 g i hipotetycznej **różnicy ciśnienia między przeciwnymi ścianami** 250/1000/2500 Pa, oszacowano **konserwatywną sumę** siły bezwładności `m·a` i ciśnienia `Δp·Amax`. Rozdzielono ją umownie na **dwa punkty mocowania** i zastosowano diagnostyczny współczynnik 2. To **nie** jest rzeczywisty współczynnik bezpieczeństwa ani nośność łącznika.

## Wynik reprezentatywny: 100 l, MDF 730 kg/m³, 8 mm, 5 g, Δp=1000 Pa

| Moduł | Liczba | Masa sztuki | Obwiednia obciążenia pojedynczego punktu |
|---|---:|---:|---:|
| Duży tylny | 8 | 0,602 kg | **54,7 N** |
| Duży przedni | 8 | 0,705 kg | **66,1 N** |
| Mały | 4 | 0,469 kg | **41,0 N** |

Łączna masa samych modułów MDF: **12,34 kg** w ustawieniu 100 l, przy ustawieniu 120 l (8 tylnych i 4 przednie) **7,64 kg**, a przy 150 l (1 tylny) około **0,60 kg**. Nie są to masy całych subwooferów.

W pełnej siatce najbardziej obciążający pojedynczy modelowy łącznik wymaga około **170,9 N** przy 10 g, 2500 Pa i grubości 10 mm (pozostałe założenia). **Nie oznacza to, że istniejąca śruba wytrzyma taką siłę** ani że taki scenariusz odpowiada rzeczywistemu transportowi.

## Kiedy symulacja siły nie wystarcza?

- Ciśnienie po obu stronach zamkniętego wkładu w dużej mierze się znosi; potraktowanie całego `Δp` jako działającego na największą powierzchnię jest **celowo bardzo zachowawcze**. Dopiero gradienty ze sprzężonego P34A/P21G można przeliczyć na lokalną siłę netto.
- Obciążenia od uderzenia zależą od sposobu pakowania i przewożenia. Test 5 g i 10 g nie kwalifikuje urządzenia do transportu.
- Dwa punkty mocowania to wyłącznie założenie. Rzeczywista geometria powoduje momenty, wyboczenie, odrywanie, ścinanie i koncentracje naprężeń.
- Wielokrotne wkładanie/usuwanie może uszkadzać MDF, łby wkrętów, rowki i uszczelki. **Nie ma próby zmęczeniowej, tolerancji ani danych nośności MDF.**
- Potrzebny jest bezpieczny, niezależny od tarcia mechanizm blokady, możliwy do zamontowania przez otwór głośnika, bez kolizji z membraną, terminalem i koszem.

## Rekomendacja przed CAD/CNC

Zaprojektować możliwie prosty **mechaniczny rygiel/uchwyt z dodatnią blokadą**, z wyraźnym przechwytywaniem sił przez wręgi lub szyny; nie opierać zabezpieczenia wyłącznie na wciśnięciu modułów. Przygotować pliki STEP 20 modułów z zatrzaskami/śrubami, uszczelkami, gniazdami i narzędziem, następnie ponowić tor P30E z pełnymi bryłami i tolerancjami. Zmierzyć wytrzymałość połączenia w MDF, odrywanie i zachowanie przy wielokrotnym montażu. **Nie zatwierdza się konkretnego typu śrub, kleju ani pełnej konstrukcji.**

**Reprodukcja:** `node skrypty/p34b_sily_mocowania_wkladow.js` → pełny JSON `wyniki/p34b_moduly_wklady_324_20261031.json`.
