# K17 — podparte wkłady w prowadnicach, bez przecinania maty 50 mm

**4 listopada 2026 · Kontynuacja K16; drugi model geometryczny, NIE zweryfikowane zamki, sztywność, serwis ani rysunki do CNC.**

## Konstrukcyjna odpowiedź na K16

[K16](K16_podparcia_i_zabezpieczenia_20_wkladow.md) sprawdziło 80 hipotetycznych wsporników dochodzących od frontu lub tylnej ściany. Odczyt: 48 tylnych wsporników **przecina warstwę maty 50 mm**. K17 odpowiada na ten konflikt bez arbitralnego usuwania tłumienia: dwanaście **pełnowysokościowych prowadnic/żeber nośnych** rozpiętych nominalnie między dolnym i górnym MDF, po dwie w każdej z sześciu grup wkładów, połączonych z miejscami podparcia oraz przytrzymania od góry.

**[Model K17 OpenSCAD](../dokumentacja/K17_p30e_prowadnice_i_zabezpieczenia_NIE_CNC.scad)** powstaje z [generatora](../skrypty/k17_prowadnice_wkladow.js) i [pamięci geometrii K15](../wyniki/k15_p30e_przed_CNC_zestawienie.json). [Pełny wynik K17 JSON](../wyniki/k17_prowadnice_boczne_wkladow.json).

### Rzeczywiście przebadana geometria modelowa

Prowadnice ulokowano w trzech pasach głębokości: **Y=44–52 mm** (grupa przednich dużych wkładów), **Y=208–220 mm** (tylne duże) i **Y=224–236 mm** (małe). Pełny zasięg pionowy: **Z=22–478 mm** między płytami dolną i górną. Szerokość pojedynczej prowadnicy w kierunku X wynosi modelowo 16 mm, a grubość przednich i pozostałych części w osi Y odpowiednio 8 i 12 mm. Każdy modelowy język podparcia lub retencji ma 4 mm grubości Z, zakładkę 12 mm pod/na skrzynkę, w projektowanym profilu wspornika. Nie podano rzeczywistych wymiarów zamka, jego luzów ani materiału produkcyjnego.

| Kryterium geometryczne | Wynik K17 |
|---|---:|
| Prowadnice pełnowysokościowe dotykające spodniej i górnej płyty MDF | **12** |
| Integralne miejsca podparcia i antywysunięciowe, 4 na skrzynkę | **80** |
| Kolizje dodatniej objętości z 138 referencyjnymi elementami K15 | **0** |
| Kolizje między prowadnicami oraz innymi językami (poza celowym stykiem profilu) | **0** |
| Przecięcia warstwy maty tylnej Y=353–403 mm | **0** |
| Przecięcia konserwatywnej prostopadłościennej obwiedni kosza P30A | **0** |
| Nominalna dodatkowa objętość pełnego, stale zainstalowanego systemu profili | **1,020928 l** |

**12 prowadnic w tym modelu zawiera 80 miejsc kontaktowych na 20 wkładów; to nie 92 obowiązkowo oddzielne detale do cięcia.** Ich realne kształty i sposób wycinania można dopiero określić po sprawdzeniu materiału i połączenia. Ponieważ języki są zintegrowane z prowadnicami, **pozostają wewnątrz skrzyni również po wyjęciu wkładów**. Model SCAD pokazuje je we wszystkich trzech stanach regulacji; nie mogą „znikać” bez rozmontowania prowadnic.

**Zerowe przecięcia brył w nominalnym modelu nie dowodzą** możliwości montażu przez rzeczywisty otwór. Czteromilimetrowy język jest tylko cienką geometrią kinematyczną, nie wykazaną wytrzymałościowo półką. Potrzebny jest prawdziwy mechanizm wsunięcia skrzynki pod górną blokadę, odporny na drgania i odwrócenie. W tej chwili **nie określono blokady przesuwu wzdłuż prowadnicy** ani fizycznego zamocowania prowadnic do dolnej i górnej ściany.

## Co to robi z litrażem?

Jeżeli wszystkie 12 prowadnic z miejscami ustalenia mają pozostać w korpusie, to nominalne stany P30E zmalałyby geometrycznie — **przed** odjęciem innych nowo dodanych mocowań K01 i bez pomiaru rzeczywistej wyporności kosza:

| Stan | P30E [l] | P30E minus objętość modelowych prowadnic [l] |
|---|---:|---:|
| 100 | 100,1193 | **99,0984** |
| 120 | 119,9193 | **118,8984** |
| 150 | 150,1593 | **149,1384** |

To tylko orientacyjne odejmowanie objętości nowych, modelowo niepokrywających się brył. Nie jest to zatwierdzony fizyczny bilans netto. Materiał, kierunki naprężeń i kształt prowadnic nie są jeszcze dobrane, a odrębne klocki kosza, klej, uszczelki i inne okucia mogą ponownie zmienić wnętrze.

## Wnioski i kolejność badań przed rzeczywistym CNC

1. **Jako kierunek dalszych badań rekomenduję prowadnice wewnętrzne omijające tylną matę**, nie układ wsporników K16 przecinających włókninę. Należy zmniejszyć liczbę i masę elementów po weryfikacji strukturalnej, aby projekt był przystępny dla firmy CNC.
2. Opracować w detalach przekroje, wybór materiału i **wzmocnione mocowanie prowadnic do podłogi oraz sufitu**; nie można polegać na samym kontakcie „dotyka MDF”. Wykonać uproszczone obliczenia ugięcia, lokalnego zginania oraz później MES/próbki materiałowe.
3. Dopasować zamki, uszczelki antydrganiowe i blokady pozycji do obracania obudowy, transportu i wielokrotnej wymiany modułów. Każda skrzynka musi być mechanicznie unieruchomiona bez klejenia jej do stałej struktury.
4. Ponownie uruchomić **trasowanie wkładów i narzędzia K02/K07** z dwunastoma prowadnicami, wszystkimi nieusuniętymi językami kontaktowymi oraz rzeczywistym koszem. Konserwatywne AABB P30A kosza to tylko geometria przesiewowa.
5. Powtórzyć bilans 100/120/150 l, wpływ na propagację akustyczną i rezonanse, sprawdzić czy prowadnice są w ogóle technologicznie wykonalne w zadanych formatkach i tolerancjach MDF.
6. Dopiero po zatwierdzeniu konstrukcji oraz fizycznych prób wykonać pliki produkcyjne (DXF/STEP). **CNC HOLD.**

**Decyzja:** K17 dostarcza poprawioną koncepcję podparcia bez naruszenia maty. Nie wolno jednak przedstawiać jej jako gotowej do wycięcia ani pozwalać, by 20 wkładów wisiało w modelu bez widocznego toru siły.
