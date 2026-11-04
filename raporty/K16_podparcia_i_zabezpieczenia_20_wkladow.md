# K16 — wymienne wkłady regulacji objętości MUSZĄ mieć nośne mocowania

**4 listopada 2026 · Po K15, P30E i K02/K07. 20 wkładów bez mocowań nie jest projektem konstrukcyjnym. Badanie referencyjnych podparć, NIE zatwierdzony detal ani instrukcja CNC.**

## Wykryta luka

Dotychczasowy parametryczny model **K15** rysuje 20 szczelnych, zamkniętych skrzynek o objętościach zewnętrznych i masach MDF8, ale nie pokazuje **żadnego mechanizmu, którym te skrzynki przekazują siły do korpusu**. Wkłady nie mogą pozostawać zawieszone w powietrzu. Modyfikując litraż 100/120/150 l, musimy zachować stabilne ustalenie, brak grzechotania i możliwość demontażu przez otwór głośnika. Sam test kolizji AABB **nie potwierdza** mocowania.

Wyniki audytu obciążenia i wsporników: [K16 JSON](../wyniki/k16_model_podparcia_20_wkladow.json) · [80 oznaczonych elementów mocowań CSV](../wyniki/k16_80_stykow_modulow_REFERENCYJNE_NIE_CNC.csv) · [odtwarzalny generator JS](../skrypty/k16_podparcie_modulow.js) · [model OpenSCAD K16, rozbudowujący K15](../dokumentacja/K16_p30e_z_mocowaniami_modulow_NIE_CNC.scad).

## 1. Droga sił i zabezpieczenie przy zmianie orientacji obudowy

Ustanowiono wymóg funkcjonalny dla **KAŻDEJ skrzynki**:
- minimum dwa niezależnie ułożone punkty **podparcia od dołu**, przenoszące ciężar na rzeczywistą ścianę lub zweryfikowaną wręgę;
- co najmniej dwa przeciwległe **punkty przytrzymujące od góry / zapobiegające wypadnięciu** przy odwróceniu lub transporcie;
- konstrukcyjne przeciwdziałanie przesuwowi w pozostałych kierunkach oraz rezonansom, obrotowi, stukaniu i zmęczeniu;
- rozłączalne i dostępne od frontu po wyjęciu kosza mocowania, z jednoznacznym stanem „zablokowane”; wkład nie może wymagać dostępu od zewnątrz przez zamknięty tył;
- obie połowy rzeczywistego połączenia (kotwa w MDF i element wkładu) muszą być wymiarowane, a nie wyłącznie ich bryły AABB.

**K16 nie wybiera jeszcze konkretnego zatrzasku, mocowania lub śruby.** Wariant z czterema modelowymi elementami przy każdej skrzynce służy do wyznaczenia kolizji i skali obciążeń, nie jest zatwierdzonym 80-elementowym systemem.

## 2. Weryfikacja wariantu „dwa dolne wsporniki + dwa górne rygle”

W jednym jawnie hipotetycznym wariancie K16 sprawdzono dla każdej z 20 skrzynek **cztery bryły o przekroju 16×8 mm**: dwa dolne elementy dotykają spodu skrzynki, dwa górne jej wierzchu. Każda bryła dochodzi do wewnętrznego frontu **Y=44 mm** albo wewnętrznego tyłu **Y=403 mm**, wychodząc pod wypełnienie od krawędzi na 12 mm. Poszczególne poziomy Z mają przesunięte naprzemiennie pozycje X, by nie nachodziły na elementy mocowania sąsiedniej skrzynki. Model **nie obejmuje rzeczywistych sworzni, śrub, blach, kołków, nakrętek, skręcania, połączenia z MDF ani sztywności wspornika**.

| Wielkość | K16 |
|---|---:|
| Wkłady (4 małe, 8 dużych tylnych, 8 dużych przednich) | **20** |
| Dwa dolne i dwa górne modelowe elementy na wkład | **80 brył referencyjnych** |
| Wkłady mocowane do wewnętrznego frontu | **8** |
| Wkłady mocowane do tylnej ściany | **12** |
| Długość elementu od ściany do zakładki (front/tył) | **20 / 68 mm** |
| Wysunięcie od ściany do powierzchni wkładu (front/tył) | **8 / 56 mm** |
| Modelowa suma objętości 80 elementów | **0,499712 l** |
| Dodatnie geometryczne kolizje tych 80 elementów z 138 bryłami K15 | **0** |
| Dodatnie kolizje dwóch elementów między sobą | **0** |
| Wycięcia/przejścia przez obwiednię 50-mm maty tylnej | **48** |

**Zerowa kolizja modelowanych, prostych brył nie oznacza, że wszystkie zatrzaski da się założyć**. Nie prowadzono ponownie pełnych tras K02/K07 z narzędziem, rzeczywistym koszem, przystawkami montażowymi i dłonią.

## 3. Najważniejszy wynik: konflikt z 50-mm tylną matą

Dla tylnej ściany modelowe elementy przebiegają przez warstwę Y=353–403 mm. **Każdy z 48 tylnych elementów przecina 50 mm obwiedni maty**, razem **0,3072 l geometrycznej obwiedni**, którą należałoby uwzględnić w technologii montażu i przy przeliczeniu przepływu/tłumienia.

Ten wynik **nie jest** masą ani objętością ciała stałego porowatej maty, dlatego nie odejmujemy 0,3072 l od akustycznej objętości netto wprost. Nie można też bez pomiaru wyciąć 48 otworów i stwierdzić, że zachowaliśmy ten sam opór przepływu i rozkład absorpcji. Ten wariant jako preferowaną konstrukcję **odrzucamy na obecnym etapie**, ponieważ koliduje z fundamentem P30E — pełnym wypełnieniem tylnym 50 mm.

**Wniosek do następnego modelu:** zaprojektować prawdziwe prowadnice/mostki i zakotwienia po bokach skrzynek do paneli bocznych lub specjalnie przeliczonego układu wręg, **omijając tylną matę**. Nawet wtedy trzeba opracować sposób włożenia i zdjęcia skrzynek, a nie tylko pokazać zieloną podporę w 3D.

## 4. Masa i zgrubna skala obciążeń, nie nośność

Przy **hipotetycznej** gęstości MDF8 730 kg/m³ i prostych zamkniętych ściankach o grubości 8 mm otrzymujemy masy modelowe:

- mały wkład 180×100×100 mm: **0,469 kg**;
- duży tylny 210×120×100 mm: **0,602 kg**;
- duży przedni 210×150×100 mm: **0,705 kg**.

W stanie 100 l komplet 20 skrzynek waży modelowo **12,34 kg**, bez zamków, śrub i uszczelek. Dla ilustracyjnego **testu 5 g** (scenariusz umowny, **NIE wymaganie normowe**), po przyjęciu, że tylko dwa dolne albo dwa górne elementy przenoszą całą siłę, belka wspornikowa o wymiarach **16×8 mm** i niepodpartym wysięgu **56 mm** daje modelowo do około **4,85 MPa** idealnego naprężenia zginającego. Dla przedniej ściany (wysięg 8 mm) analogicznie do **0,81 MPa**.

To są **wstępne wskaźniki mechaniki belki**, a nie naprężenia przy prawdziwym połączeniu. Nie uwzględniają koncentracji naprężeń, odrywania śruby z MDF, naprężeń przy gnieździe, siły w zatrzasku, pełzania, różnicy wytwarzanych płyt, nośności kleju, drgań i oporów demontażu. Nie wolno wybrać na tej podstawie 8-mm MDF jako dopuszczalnego materiału wspornika.

## 5. Bilans 100/120/150 l wymaga nowej korekty po wyborze systemu

Gdyby wszystkie 80 elementów pozostawało w obudowie w każdym stanie, nominalnie zajmowałyby **0,499712 l**. Jeżeli elementy byłyby **w całości demontowane razem z wkładami**, w scenariuszach zajętości model daje orientacyjnie **0,499712 / 0,319488 / 0,034816 l** przy 100/120/150 l. Rzeczywisty podział na stałe wsporniki i wyjmowane złącza jest nieznany. Nie wolno automatycznie nałożyć tych liczb na P30E, szczególnie tam, gdzie element przechodzi przez matę i gdzie geometrie mogą się nakładać.

## 6. Następny krok konstrukcyjny K17 (priorytet przed CNC)

**Wybrać system modułowych prowadnic wsparty na fizycznym szkielecie obudowy**, bez przecinania maty tłumiącej: schemat nośny wręga–boczna listwa/metalowy profil–półka–moduł, zabezpieczenie przód/tył i góra/dół, wygodnie uruchamiany i zwalniany po wyjęciu głośnika. Następnie zweryfikować w tej kolejności:

1. **Mechaniczny tor siły od KAŻDEGO modułu** i przeniesienie sił do MDF/wręg, udokumentowane połączenia, orientację pionową/poziomą/odwróconą.
2. **Wszystkie przejścia z K02/K07** przez rzeczywisty otwór i pomiędzy 11 wręgami, z klipsami, narzędziami, przewodami i istniejącymi wkładami.
3. **Pozostawiony materiał tłumiący 50 mm**, przestrzenie na dłonie, rzeczywiste tolerancje frezowania i blokadę przeciwdrganiową.
4. **Objętości 100/120/150 l z wybranymi stałymi i ruchomymi mocowaniami**, ich masę, obciążenia i odrębną analizę akustyczną.
5. **Badania materiałowe próbnych złączy** przed przekazaniem jakichkolwiek plików do firmy CNC.

**Decyzja:** K16 koryguje brak K15 — moduły nie mogą być tylko bryłami w przestrzeni. Dotychczasowy wariant podparć do tylnej ściany koliduje z matą i jest materiałowo niekwalifikowany. **Żaden wkład ani wspornik nie jest zwolniony do wykonania. CNC HOLD.**
