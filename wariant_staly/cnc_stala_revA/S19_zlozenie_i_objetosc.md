# S19. Złożenie 3D i poprawka bilansu objętości - CNC FIRST

Stan: 13.11.2026. Wszystkie części nadal podlegają ukończeniu projektu cyfrowego, bez jakichkolwiek prób materiałowych i bez prototypowych pomiarów przetwornika. To analiza projektowa z dokumentacji producentów.

## Nowy wspólny model przestrzenny

[S19_zlozenie_revA0.scad](S19_zlozenie_revA0.scad) odwzorowuje całą geometrię od S17 i S18 w jednym globalnym układzie. Zawiera:
- korpus W816,8/H473,3/D394,0, dwie warstwy frontu, ścianę tylną, boki i jedną wręgę;
- ring Ø400/358x6 na osi głośnika, osiem pilotów pod gwint M5 oraz kieszeń FR2;
- głośnik jako UPROSZCZONĄ obwiednię katalogową, nie model STEP kosza;
- 4 blind piloty Ø10x18 w FR1 pod inserty RAMPA M6 (do kasety);
- ramkę MDF12 na 4 metalowych dystansach Ø16/Ø6,6x24;
- prawy bok z otworem Ø30 i 4 pilotami Ø10x18 od zewnątrz do kasety;
- sześciopłytową aluminiową kasetę Neutrik/LAPP o obwiedni 70x80x72, podstawa AL3;
- przyłącze wzdłuż osi głębokości, zewnętrzne względem komory.

Nominalna głębokość ze strefą kasety frontowej 38mm: 394+38=432mm. Z rezerwą montażową 5mm za skrzynią: 437mm, a więc 13mm od budżetu450mm. Nie jest to jeszcze dowód wykonalności całej zabudowy w obu pozycjach, bo faktyczny przewód, meble i podpory są niezaprojektowane do końca.

## Weryfikacja położenia pierścienia i przetwornika

Oś symetrii: X408,4/Z236,65. Otwór frontowy Ø355,8, PCD Ø368, kołnierz Ø388,4. Pierścień i oś bazowa przechodzą przez obie warstwy. Kołnierz leży POZA frontem i nie wchodzi w komorę. Uproszczony walec kosza nie zastępuje struktury odlewu, zacisków ani fabrycznego modelu 3D. Projekt powinien w kolejnym etapie przejąć STEP producenta, gdzie dostępny, i zautomatyzować testy kolizji.

## Zaktualizowany bilans

S01 i S06 odejmowały 0,175l jako umowną wyporność terminala. S18 przenosi złącze na ZEWNĄTRZ, więc jego korpus nie wypiera powietrza z komory. W generatorze S17:
- umowna wyporność Daytona pozostaje 5,000l (założenie konstrukcyjne, nie pomiar ani dana producenta),
- wyporność terminala wewnętrznego wynosi 0,000l (brak osprzętu terminala wewnątrz komory),
- przewody i klej pozostają umowną wypornością 0,150l,
- otwór Ø30 w MDF22 pod szczelną kasetą zwiększa wolną przestrzeń o około 0,01555l przed potrąceniem wkładki kablowej i uszczelnienia.

Wynik kalkulacyjny nominalnej nowej geometrii: około 102,18l netto. Jest to nadal JEDNA docelowa pojemność 102l z tolerancją badań S01 ±3l, bez regulacji.

To nie jest rzeczywista objętość egzemplarza. W ostatecznym projekcie CAD skorygować wpływ geometrii dławnicy, łączników, przewodu, spoin i wytłumienia, bez wzywania do pomiarów fizycznych przed końcem projektu.

## Dalsze zadania tylko CAD/CAM

1. Uzupełnić 3D zacisków Daytona, uszczelki kosza i pełnych modeli Neutrik/LAPP, sprawdzić kolizje cyfrowo.
2. Dokończyć osłonę terminala: bloki serwisowe M3, spoiny i izolację styków, przekrój rzeczywistej uszczelki oraz głębokości połączeń.
3. Wybrać konkretny materiał perforowanej siatki, sposób obszycia tkaniny, połączenia z ramką i prześwit przy Xpeak.
4. Dokończyć podparcie dla obu orientacji korpusu, zabezpieczenie przewrócenia i montaż w zabudowie.
5. Po pełnym modelu 3D uruchomić symulacje naprężeń, drgań i bilans sztywności na danych dostawców. Potem dopracować obróbkę CNC, pasowania, dogbones, nesting i CAM.

Weryfikacja automatyczna: python wariant_staly/cnc_stala_revA/sprawdz_s19.py. Główny README niezmieniany.
