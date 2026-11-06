# K36 — prowadnice i mocowania na wspólnych bazach korpusu

5 listopada 2026. **Projekt roboczy, CNC HOLD.** Kontynuacja K35.
Wkłady pozostają w dotychczasowych położeniach. Zmieniono zależne od płyt
końce prowadnic, wysokości płatów kanałów, ograniczniki i pozycję płytek.
Dodano trzy robocze DXF korygujące krawędź metalowej blokady K33.

## Rozwiązane zależności

Przednia powierzchnia wręgi pozostaje X448; jej rzeczywisty tył to
`448+t_PORTAL`. Płytka4 mm opiera się teraz na tym tyle, a nie na stałym X470.
Płat kanału zaczyna się na `max(474,448+t_PORTAL+4+g)`, co usuwa zachodzenie
płytki na płat przy grubszej wrędze. **Nie przesuwa się skrzynek.**

| Element | Nowa reguła, mm |
|---|---|
| Początek szyny A | 448+t_PORTAL+g |
| Koniec szyny/płatu A | 750−g |
| Początek szyny/płatu B | 750+t_MID_PORTAL+g |
| Koniec odcinka B | 1080−t_SIDE_R−g |
| Dół/góra płatu kanału | t_BOTTOM+g /500−t_TOP−g |
| Górna powierzchnia dolnej szyny | stałe Z40 |
| Dół górnego ogranicznika | stałe Z466 |
| Przednia powierzchnia tylnego ogranicznika | stałe X1018 |
| Tył tylnego ogranicznika | 1080−t_SIDE_R−g |

`g=0,2` jest wciąż założoną szczeliną, nie zatwierdzoną specyfikacją kleju.
Przebadano512 skrajnych zestawów dziewięciu grubości korpusu/wręg K35.
W żadnym nie stwierdzono kolizji płytek z innymi stałymi elementami poza
zamierzonym stykiem z własną wręgą. Test sprawdza też konkretne szczeliny
styku i niezmienione poziomy podparcia, nie tylko dodatnie wymiary.

## Operacje, których nie wolno pomylić ze zwykłym wycięciem obrysu

Aby zachować poziom Z40, dolne szyny mają **17,3–18,3 mm** grubości.
Przyjęto wykonanie przez obróbkę płaszczyzny z grubszego materiału nominalnie22,
po pomiarze rzeczywistej grubości. Nie można zapewnić18,3 mm z płyty18.
Górne ograniczniki mają11,3–12,3 mm; propozycją jest obróbka z nominalnego18.

Tylny ogranicznik ma39,3–40,3 mm zamiast sumy nominalnych22+18. W modelu
zastąpiono te dwie części jedną obwiednią wykończonego laminatu25+18,
z założoną spoiną0,2, obrabianego do wymiaru. Stary `BACKSTOP_PACK` nie jest
montowany dodatkowo. Przyjęte grubości pozwalają na naddatek, ale płaskość,
spoiny, rzeczywiste wymiary i możliwość wykonania wymagają kwalifikacji.

Model nadal przyjmuje nominalne8 mm płatów,18 mm szyn pośrednich,
4 mm metalu i25 mm małego dystansu. **512 kombinacji dotyczy dziewięciu płyt
korpusu/wręg, nie wszystkich niezależnych grubości całej skrzyni.** Brak
kolizji nie oznacza potwierdzonej trwałości ani ciągłego podparcia klejem.

## Dodatkowa poprawka: przednia krawędź blokady

Kontrola frontu o największej badanej grubości `22,5+0,1+22,5=45,1`
ujawniła kolizję: stara metalowa poprzeczka zaczynała się na Y45,
a poza otworem głośnika zachodziła na front o0,1 mm.

**Przesunięto tylko jej krawędź na Y47, pozostawiając tył na Y357.**
Szerokość poprzeczki maleje312→310 mm; osie śrub nadal Y55/347,
a lokalnie8/300 zamiast10/302. Nosek i promienieR4 zachowują globalne
położenie. Dla długiego wariantu kołnierz i gwinty również pozostają
w tych samych miejscach globalnych. Trzy DXF należy stosować jako zestaw,
zastępujący odpowiadające widoki K33. Kołnierz K33 pozostaje bez zmiany.

Zmiana obrysu wymaga uaktualnienia obliczenia masy i lokalnego przekroju
przy śrubie; wcześniejsze liczby K33 nie są automatycznym zatwierdzeniem
nowej części. Odległość osi przedniej śruby od krawędzi spada10→8 mm.
Nie wyznaczono dopuszczalnej siły przy tej krawędzi ani momentu dokręcania.

## Kontrola całej drogi względem zmienionej konstrukcji

Dla każdego stałego elementu utworzono prostopadłościenną obwiednię
obejmującą jego geometrię we wszystkich512 przypadkach. Kontrola ciągłych
osiowych przesunięć względem takiej obwiedni jest konserwatywna względem
tej rodziny geometrii: nie ogranicza się do sprawdzenia punktów końcowych.
Globalne otworyR4 nie zmieniają kształtu; wcześniejsza kontrola ich naroży
pozostaje zależnością modelu. Nie jest to test dowolnych ruchów6DOF.

Osobno sprawdzono przejście przez maksymalnie gruby front45,1 i referencyjny
otwórØ355,8, używając skrajnych naroży obwiedni X/Z w przekroju wejścia.
Wkłady, przekładki i blokady zachowują dotychczasową orientację.

| Test | Wynik |
|---|---|
| 8 dróg wkładów względem zmienionych stałych części i płytek | przechodzą |
| 4 drogi przekładek | przechodzą |
| 5 dróg blokad z nową krawędzią, kołnierzem i obwiednią spoiny | przechodzą |
| 8 podejść modelowego narzędzia o przekroju18×18 i długości60 | przechodzą |
| 8 podejść starej obwiedni20×20 | 4 przednie odrzucone, 4 tylne przechodzą |

Obwiednia20 mm przy osiY55 sięga doY45 i przecina najgrubszy front.
Obwiednia18 mm sięga doY46, pozostawiając nominalnie0,9 mm do frontu45,1.
To propozycja maksymalnej obwiedni narzędzia w tym teście, **nie wybrany
klucz ani dowód możliwości ruchu dłoni**. Uwzględnienie tolerancji osi,
ugięcia, nasadki i rękojeści może zmniejszyć zapas.

To kontrola przyrostowa nowej stałej konstrukcji. Wzajemna kolejność
wkładów oraz kolizje z innymi wyjmowanymi elementami bazują na K30/K33;
nie wykonano od nowa całego planowania serwisu z niezależnym solverem.
Front i położenia płytek zostały sprawdzone ponownie, a nie pominięte
przez zastosowanie prostego modelu ścian bez frontu.

## Pliki, odtwarzanie i dalszy krok

[Instrukcja trzech DXF](../dokumentacja/cnc/K36_KRAWEDZ_BLOKADY_HOLD/README.md)
· [generator](../skrypty/k36_bank_z_pomiarow.py)
· [test](../skrypty/sprawdz_k36.py)
· [geometria, zakresy i wyniki](../wyniki/k36_bank_z_pomiarow.json)
· [manifest](../wyniki/k36_manifest.json).

Uruchomienie: `python skrypty/k36_bank_z_pomiarow.py` i
`python skrypty/sprawdz_k36.py`. Test wymaga wykrycia czterech kolizji starego
narzędzia20 mm; ich obecność nie jest ukrywana pod ogólnym komunikatem PASS.
Niezależny odczyt DXF sprawdza jednostki, kontury, otwory, niezmienione osie
oraz promienieR4. K35 i kontrola README pozostają w regresji.

**Następny krok: włączyć rzeczywiste grubości płatów, szyn, metalu i dystansów
oraz tolerancje obróbki do tego samego modelu**, uaktualnić przekrój i nośność
przy przedniej śrubie blokady oraz przygotować jednoznaczną listę operacji
płaszczyznowania/laminowania. Potrzebna jest też identyfikacja rzeczywistego
narzędzia mieszczącego się w prześwicie. Nie kwalifikowano kleju, gwintów,
spoiny, kosza ani terminala. **Nowe DXF są robocze, CNC HOLD.**
