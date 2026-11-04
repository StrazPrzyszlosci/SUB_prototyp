# K15 — parametryczne złożenie korpusu i lista elementów przed CNC

**4 listopada 2026 — badanie konstrukcyjne po P30E/K14. Geometria referencyjna, NIE projekt do frezowania. CNC HOLD.**

## Czego brakowało?

P30E zweryfikowało referencyjny korpus, lecz dotychczas nie mieliśmy **jednego źródła wymiarów, modelu 3D i powiązanego z nim pełnego zestawienia formatek**. K15 tworzy taką bazę, żeby wykrywać błędy i uzgodnić technologię z przyszłym wykonawcą CNC. Wyniki są obliczeniami geometrycznymi, nie badaniami wytrzymałości, złączy ani rzeczywistego prototypu.

**Artefakty:** [generator, źródło wymiarów](../skrypty/k15_pre_cnc_model.js) · [model 3D OpenSCAD](../dokumentacja/K15_p30e_zlozenie_parametryczne_NIE_CNC.scad) · [lista 138 formatek CSV](../wyniki/k15_p30e_przed_CNC_138_elementow.csv) · [zestawienie parametrów i kontroli JSON](../wyniki/k15_p30e_przed_CNC_zestawienie.json).

## 1. Spójne współrzędne 3D

Korpus W×D×H **1020×425×500 mm**. X od lewej do prawej, Y od zewnętrznego frontu do tyłu, Z od spodu do góry. Front składa się z **dwóch płatów MDF22** na Y=0–22 oraz 22–44, razem 44 mm po dopiero przewidzianym klejeniu. Tył: Y=403–425. Boki: X=0–22 i 998–1020, Y=44–403. Spód i góra leżą między bokami. **Wnętrze 976×359×456 mm**.

Model zawiera **11 uproszczonych brył wręg P30A/P30E** i **20 modułów** w wariantach 100/120/150 l. Każdy moduł jest rozłożony na sześć niepokrywających się płatów MDF8. Wygenerowany model OpenSCAD ma przełącznik stanu objętości, wyświetla osobno konstrukcję, moduły, wręgi i osiem niezatwierdzonych czerwonych kopert pod mocowanie K01. Elementy te są **modelem do weryfikacji**, nie zweryfikowaną geometrią technologii.

### Korpus i wręgi — nominalne formatki, NIE cięcie

| Rodzina | Liczba | Wymiary formatek | Materiał kandydat |
|---|---:|---|---|
| Laminowany front | 2 | 1020×500×22 mm, z nominalnym otworem centralnym z rysunku producenta | MDF22 |
| Tył | 1 | 1020×500×22 mm; otwór pod terminal nierozstrzygnięty | MDF22 |
| Dwa boki | 2 | 359×500×22 mm | MDF22 |
| Spód i góra | 2 | 976×359×22 mm | MDF22 |
| Dwie wręgi U: szyny | 4 | 359×22×22 mm | MDF22 |
| Dwie wręgi U: przednie poprzeczki | 2 | 412×10×22 mm, **krytyczna wąska formatka** | MDF22 |
| Dwie wręgi U: tylne poprzeczki | 2 | 412×22×22 mm | MDF22 |
| Trzecia krótka rama: szyny i poprzeczka | 3 | 2× 139×22×22 mm + 1× 412×22×22 mm | MDF22 |
| Skrzynki regulacji: 4 małe + 16 dużych | 120 | Każda skrzynka — sześć płatów MDF8; indywidualne formatki i położenie w CSV | MDF8 |

W sumie **7 płyt zewnętrznych + 11 elementów wręg + 120 formatek 20 skrzynek = 138 referencyjnych elementów**. Warianty skrzynek mają nominalne gabaryty **4×(180×100×100)**, **8×(210×120×100)** i **8×(210×150×100) mm**. Rozpisanie każdej skrzynki na osobne płaty MDF8 zakłada wyłącznie prosty geometryczny układ stykowy, **bez kwalifikacji klejenia, szczelności, złączy i zamków**. 

Nominalna suma **pełnych prostokątnych** formatek wynosi **2,662908 m² MDF22** oraz **2,112960 m² MDF8**, bez ścieżek frezu, odpadów, rezerw na uchwyty, odchyłek i formatu arkusza. **10-mm szerokość przedniej poprzeczki wręgi nie jest zatwierdzoną geometrią technologicznie wykonalnej części.**

## 2. Różne średnice otworów — nie mieszamy ich przy CNC

- **Ø355,8 mm** to nominalna średnica *wycięcia pod kosz* z dokumentacji Daytona. Przed wykonaniem należy dobrać pasowanie i zweryfikować rzeczywisty egzemplarz.
- **8×Ø6,5 mm na PCD Ø368 mm** to **fabryczne otwory w metalowym kołnierzu głośnika**. W K15 są jedynie widocznymi znacznikami referencyjnymi; **nigdzie nie wycinamy w MDF otworów Ø6,5 mm pod śruby**.
- Przykładowy przelot **Ø5,5 mm pod hipotetyczną śrubę M5 w MDF** nie jest jeszcze przewidziany do wiercenia: K14 wykazał nierozwiązany problem nośności i docisku płytki stalowej w drewnie. Potrzebny jest nowy, fizycznie wiarygodny projekt przenoszenia sił.

Nie wolno utożsamiać otworu kosza, otworu pod śrubę, otworu pod wkładkę i otworu w odrębnej ramie stalowej.

## 3. Niezależne kontrole rachunkowe i zachowany litraż

Generator sprawdza, że **żadne dwie nominalne bryły MDF spośród 138 elementów nie mają wspólnej dodatniej objętości**, a wszystkie mieszczą się wewnątrz zewnętrznego obrysu. Jego bilans odtwarza **52,600134 l** materiału skrzyni z otworem i **1,609080 l** wręg (P30E/K10), po uwzględnieniu testowego wyporu kosza **5 l**, osprzętu **0,175 l** oraz maty porowatej 50 mm:

| Stan | Wkłady | P30E odtworzone [l] | Warunkowo minus osiem nowych klocków K01 [l] |
|---|---|---:|---:|
| 100 l | 16 dużych + 4 małe | **100,1193** | 99,9690 |
| 120 l | 12 dużych | **119,9193** | 119,7690 |
| 150 l | 1 duży | **150,1593** | 150,0090 |

Ostatnia kolumna zakłada, że **0,150336 l ośmiu kopert K01** nie było jeszcze nigdzie uwzględnione i że zainstalowano je w całości. Nie są to pomiary rzeczywistej objętości, gwarancja osiągnięcia tych litrów ani zatwierdzone wymiary CNC. Gdy konstrukcja mocowania zostanie zmieniona, tę kolumnę trzeba ponownie przeliczyć.

Kontrola braku kolizji **AABB** dotyczy tylko wspólnej objętości modelowych prostych brył; **nie potwierdza** wejścia i wyjścia wkładów, dostępności dłoni i narzędzi, styków rzeczywistego kosza, wentylacji, mocowania złącza, klejonych spoin ani pozytywnej nośności konstrukcji.

## 4. Konkretne bramki do wydania właściwego modelu CNC

1. **G15-1 — materiał i połączenia:** grubości dostępnego MDF, laminacja frontu, klej i technologia łączenia ścian, wpusty, fazowania, odsadzenia, minimalne szerokości wycinanych części; w szczególności przednie 10-mm pasy wręg.
2. **G15-2 — rzeczywiste mocowanie Daytona:** po K14 nowa droga sił bez niekwalifikowanego 0,5-mm drewnianego pasa; osobny dobór trzpienia, otworu w MDF, kształtu klocka, gwintu, uszczelki, momentu i serwisu. Potrzebne wymiary rzeczywistego kosza.
3. **G15-3 — szczelne i serwisowalne moduły:** zatrzaski, uchwyty, łączenia MDF8, uszczelnienie i blokada 20 modułów; powtórzenie tras K02/K07 z realnymi narzędziami i wszystkimi przeszkodami w 3D.
4. **G15-4 — całe urządzenie:** realny grill, stopy, terminal, przewody i mocowanie elektroniki, obrys zewnętrzny **maksymalnie 500 mm** z rzeczywistym dodatnim zapasem.
5. **G15-5 — testy konstrukcji:** materiał z kart i prób, nośność połączeń, szczelność, zmęczenie, kontrolowany kontakt 3D i odtworzenie akustyki 100/120/150 l; geometria zgodna z pomiarami i tolerancjami.
6. **G15-6 — dopiero zamrożone pliki dla wykonawcy:** indywidualne warstwy i rysunki DXF/STEP, wymiarowanie i tolerancje, zamówienie próbki, kontrola pierwszej sztuki i niezależny przegląd.

**Wniosek:** mamy jedno źródło prawdy dla nominalnej geometrii, numerację 138 elementów, trzy ustawienia modułów oraz odtwarzalny model 3D i listę formatek. To znaczny krok w kierunku CNC, **ale ani jedna z 138 formatek nie jest jeszcze zwolniona do frezowania. CNC HOLD.**

**Odtwarzanie:** uruchomić polecenie `node skrypty/k15_pre_cnc_model.js`. Odtwarza ono identyczne pliki SCAD, JSON i CSV.