# K10 — paszport materiałowy WSZYSTKICH elementów projektowanej obudowy

**3 listopada 2026 · Audyt istniejących badań P18–P19/P30E/P34C/P36–P37 i pierwszy ilościowy przesiew materiałów.** Zasada: **każda część konstrukcyjna, uszczelniająca i montażowa ma własny materiał-kandydata, warunki pracy, ślad dowodowy i listę kontroli kwalifikacyjnych**. To nie jest nakaz wykonania wszystkiego z MDF. **35/35 pozycji ma przypisanego kandydata; 0/35 posiada komplet rzeczywistych badań dopuszczających do produkcji.** Nie zatwierdzono CNC.

## 1. Co policzono już przed K10?

- [P30E](078_P30E_mata50_montaz_robustnosc.md): geometria korpusu 1020 × 425 × 500 mm, front MDF44, ściany i wręgi MDF22, **20 skrzynek MDF8**, tylna mata50, masy i modelowe objętości netto 100/120/150 l. Nie było odrębnego doboru materiału dla poszczególnych części.
- [P36A](091_P36A_grubosc_MDF_podatnosc_i_wregi.md): **324 scenariusze** grubości 18/22/25/28 mm, E i gęstości, 0/1/2 idealnych podpór. To obliczenia podatności płyt *z idealnymi warunkami podparcia*, nie nośności pełnej obudowy.
- [P37B](095_P37B_czulosc_MDF_spoiny.md): wpływ E, gęstości i podatności spoin na globalny model oraz zalecenia do pomiarów; **brak prawdziwych próbek MDF**.
- [P19A](030_P19A_obliczenia_spoin_i_material_kleju.md): 656 uproszczonych modeli połączeń, analiza katalogowego epoksydu LOCTITE EA 9466 i PVAc KLEIBERIT 303.0. Żadnego z nich nie zakwalifikowano do obciążenia od ośmiu śrub w realnym MDF.
- [P34C](088_P34C_obciazenia_i_blokowanie_wkladow.md): **324 scenariusze** masy, różnicy ciśnień i przyspieszeń wyjmowanych modułów. Bez zwymiarowanych rzeczywistych zatrzasków i ich nośności.
- K01–K09: klocki20, kołnierz i mocowania, drogę wkładania, inspirację Francisa z wkładką gwintowaną w doklejonym klocku. Nie dowodzą siły wyrywania wkładki ani odporności spoiny na pełzanie.

**Wniosek z audytu:** dotychczasowy wybór MDF22, MDF8, MDF44, kleju i akustycznej maty był **hipotezą projektu**, a nie końcową optymalizacją materiałową. K10 dodaje kompletny paszport ról oraz porównania, nie kasując poprzednich badań.

## 2. Karty materiałowe i jawne źródła danych

**MDF.** [EGGER, karta surowego MDF zgodnego z EN 622-5](https://www.egger.com/get_download/8a07fd0a-3b33-4452-b872-43f2c2ae41c4/Technical_datasheet_E1E05_TSCA_ST_CE_TD-504_Polish.pdf?country=PL): dla zakresu grubości **powyżej 19 do 30 mm** średni moduł sprężystości na zginanie z EN 310 to **2100 N/mm²**; dla **powyżej 6 do 9 mm** to **2700 N/mm²**. Karta podaje różne parametry dla grubości, a **gęstość zależną od zakładu**, dlatego stosowane przez P30E/P34C **730 kg/m³ jest założeniem**, nie zmierzoną gęstością kupionej płyty. Nie ma jeszcze ustalonej fabryki, partii ani rzeczywistego profilu przez grubość.

**Sklejka.** [WISA-Birch, karta produktu 21 mm](https://www.specifiedby.com/upm/wisa-birch/UPM_UPM_WISA-Birch_Technical_Fact-Sheet.pdf) podaje kierunkowo **E∥=9858 N/mm²** i masę powierzchniową **14,3 kg/m²** przy 21 mm. [WISA Form Birch, karta porównawcza obu kierunków](https://www.wisaplywood.com/siteassets/documents/brochures/wisa_concrete-forming-plywood-en.pdf) podaje dla porównywalnej grubości 21 mm **E⊥=7642 N/mm²**. **Uwaga: słabsza sztywność pochodzi z produktu WISA-Form, masa z niepowlekanej WISA-Birch. To hybrydowy scenariusz orientacyjny, nie dokładna karta jednego SKU.** Moduł Poissona `ν=0,30` użyty w przesiewie jest osobnym hipotetycznym parametrem. Dla całej płyty sklejki wymagany jest **model ortotropowy (E_x,E_y,G_xy,ν_xy)**, a nie podstawienie jednego E do modelu izotropowego.

**Klej.** [KLEIBERIT 303.0, karta producenta](https://www.kleiberit.com/fileadmin/Content_new/Produktinformationen/303.0/dbe3030_KSE.pdf): PVAc D3 jako 1K; D4 po przewidzianym dodatku utwardzacza 303.5. **Klasa D3/D4 nie jest wytrzymałością konkretnej spoiny MDF w MPa**. Zachowujemy istniejący audyt EA9466 z P19A. Materiał dobiera się na podstawie konstrukcji rzeczywistej spoiny, jej ścinania/odrywania, wilgotności, pełzania i liczby cykli.

Dla **EPDM, zaczepów, stopek, wykończenia, uszczelek, siatki i przewodów** zapisano rodziny materiałowe, ale **brakuje wybranego artykułu katalogowego i jego zweryfikowanych parametrów**. Żadnych wartości nośności, odporności ogniowej, współczynnika tarcia ani pochłaniania dźwięku nie wpisano jako faktów bez źródła.

## 3. Liczbowy przesiew płyt — niepełny, lecz odtwarzalny

Przy tym samym modelowym prostokątnym polu P30E **426×359 mm**, nominalnym nacisku **1000 Pa** i idealnym podparciu SSSS zastosowano wskaźniki `D=E h³/[12(1−ν²)]`, `μ=ρh`, `w/w₀=D₀/D`, `f/f₀=√[(D/μ)/(D₀/μ₀)]`. Punkt odniesienia MDF22 to **45 μm** i **235,4 Hz** w uproszczonym modelu P30E. Tabela **nie jest obliczeniem 3D gotowej obudowy**. Dla sklejki jest to **heurystyczny wskaźnik jednego kierunku zginania**, NIE wiarygodna predykcja ugięcia ani częstości płyty ortotropowej.

| Hipoteza materiału | grubość [mm] | E na zginanie [GPa] | μ [kg/m²] | D / D_MDF22 | wskaźnik ugięcia [µm] | wskaźnik f11 [Hz] |
|---|---:|---:|---:|---:|---:|---:|
| MDF22_reference | 22 | 2.100 | 16.06 | 1.000 | 45.00 | 235.4 |
| MDF25_reference | 25 | 2.100 | 18.25 | 1.467 | 30.67 | 267.5 |
| WISA_birch21_weak_proxy | 21 | 7.642 | 14.30 | 3.165 | 14.22 | 443.8 |
| WISA_birch21_strong_proxy | 21 | 9.858 | 14.30 | 4.083 | 11.02 | 504.1 |
| MDF8_reference | 8 | 2.700 | 5.84 | 0.062 | 727.89 | 97.1 |

**Praktyczny wynik:** przejście z MDF22 na **MDF25** podnosi nominalny wskaźnik D około **1,47×**, ale też masę powierzchniową o **2,19 kg/m²**. Sklejka brzozowa ma duży potencjał sztywności przy zbliżonej masie, ale **nie wolno przypisać jej tej samej geometrii P30E bez zmiany grubości i ponownego bilansu**, a ortotropia może ograniczać wynik całej obudowy. Zmiana materiału ścian, wręg i frontu wymaga odrębnego sprawdzenia, także ze względu na inne drogi sił.

## 4. Front 44 mm — materiał warstwowy wymaga sprawdzenia spoiny

Dla **dwóch warstw MDF22** idealizacje wyznaczają różne granice: bez przenoszenia sił między warstwami ich suma wskaźników zginania to `2×D(22)`; przy idealnym pełnym zespoleniu ekwiwalentna płyta grubości44 ma `D(44)=8×D(22)`. **Stosunek wynosi 4**, ale **nie są to wartości dopuszczalne rzeczywistego frontu**. Otwór Ø355,8, osiem śrub na PCD Ø368, cienki pas MDF przy nich, lokalne klocki i warstwa kleju uniemożliwiają bezpośrednie przeniesienie tego rachunku na nośność oraz odkształcenia realnego frontu. Należy zbadać osobno laminowanie dwóch MDF22, odrywanie i creep oraz kontakt kołnierza.

## 5. Masa z rzeczywistych brył P30E — bez podwójnego liczenia

Odtworzono geometryczny bilans P30E: objętość powłoki **52,600134 l materiału**, 11 modelowych wręg łącznie **1,60908 l**, obwiednia ośmiu klocków K01 o głębokości20 **0,150336 l** (klocków **nie było** w pierwotnej masie P30E). Przy umownej gęstości MDF730 powłoka + wręgi ważą około **39,57 kg**, a same klocki przy odrębnym, **hipotetycznym** 700 kg/m³ — około **0,105 kg**. Gęstość klocków nie jest wartością katalogową konkretnego wybranego drewna.

Wkłady P34C: 8 tylnych **210×120×100**, 8 przednich **210×150×100** i 4 małe **180×100×100 mm** (modele pustych wewnątrz prostopadłościanów). Porównano MDF8 przy 730 kg/m³ z hipotetyczną sklejką9 przy 14,3 kg/m² /21 mm jako gęstością orientacyjną. Przy **tych samych wymiarach zewnętrznych**, ale innych rozmiarach wnętrza szczelnego wkładu:

| Stan nominalny [l] | same moduły MDF8 [kg] | same moduły sklejka9 [kg] | różnica mas [kg] | P30E MDF: powłoka + wręgi + moduły [kg] |
|---:|---:|---:|---:|---:|
| 100 | 12.34 | 12.75 | 0.41 | 51.91 |
| 120 | 7.64 | 7.90 | 0.26 | 47.21 |
| 150 | 0.60 | 0.62 | 0.02 | 40.18 |

Wartości masy bazowej odpowiadają wcześniejszemu P30E (~51,9/47,2/40,2 kg). *Nie zawierają* głośnika, maskownicy, uszczelnień, śrub, przewodów, klejów, metalowych zaczepów ani wykończenia. **Pełnej masy i rzeczywistej regulacji litrażu nie znamy**. Nie wolno z tej tabeli wnioskować, że po zamianie MDF8 na sklejkę9 ukończony moduł ma już poprawny zamek i da się włożyć przez otwór.

## 6. Materiał dla każdej funkcji — rejestr 35 pozycji

**Status każdej pozycji: kandydat do badań, NIE zatwierdzony materiał wykonawczy.** Kolumna „bramka” przedstawia brakującą kwalifikację, a nie przeprowadzony test. Szczegółowe założenia i odniesienia do wcześniejszych raportów są we [w pełni wersjonowanym rejestrze danych](../dane/k10_rejestr_materialow_czesci_obudowy.json).

| ID | Część / funkcja | Materiał wstępny | Bramka do rzeczywistego wyboru |
|---|---|---|---|
| E01 | Front nośny z wycięciem Ø355,8 | dwie warstwy MDF po 22 mm klejone do 44 mm | próby łączenia warstw i odrywania 8 punktów; rysunek kosza i warstwy kleju; pomiar dynamiki pełnego frontu |
| E02 | Ściana lewa korpusu | MDF 22 mm (EGGER jako karta referencyjna, ρ=730 model P30E) | karta konkretnej partii (E,ρ, wilgoć, emisje); MES P33C/P37; próby złącza, szczelność |
| E03 | Ściana prawa korpusu | MDF 22 mm (EGGER jako karta referencyjna, ρ=730 model P30E) | karta konkretnej partii (E,ρ, wilgoć, emisje); MES P33C/P37; próby złącza, szczelność |
| E04 | Ściana górna | MDF 22 mm (EGGER jako karta referencyjna, ρ=730 model P30E) | karta konkretnej partii (E,ρ, wilgoć, emisje); MES P33C/P37; próby złącza, szczelność |
| E05 | Ściana dolna | MDF 22 mm (EGGER jako karta referencyjna, ρ=730 model P30E) | karta konkretnej partii (E,ρ, wilgoć, emisje); MES P33C/P37; próby złącza, szczelność |
| E06 | Ściana tylna | MDF 22 mm (EGGER jako karta referencyjna, ρ=730 model P30E) | karta konkretnej partii (E,ρ, wilgoć, emisje); MES P33C/P37; próby złącza, szczelność |
| E07 | Wręgi pionowe i obwody przy X=426/701 | MDF 22 mm (hipoteza P30E) | wytrzymałość osiowo/na wyboczenie; złącza, klej, frezy; kierunkowość sklejki i pełen MAC |
| E08 | Rygle górne i dolne wręg | MDF 22 mm (hipoteza P30E) | wytrzymałość osiowo/na wyboczenie; złącza, klej, frezy; kierunkowość sklejki i pełen MAC |
| E09 | Dodatkowe żebra poprzeczne i tylne | MDF 22 mm (hipoteza P30E) | wytrzymałość osiowo/na wyboczenie; złącza, klej, frezy; kierunkowość sklejki i pełen MAC |
| E10 | Osiem klocków pod wkładki gwintowane | klejonka bukowa 20 mm lub drewno klejone warstwowo o udokumentowanym gatunku | wybrać kartę drewna i rzeczywistą wkładkę; min 3 próbki na wariant; połączenie klejowe i tolerancje |
| E11 | Osiem tylnych dużych wkładów regulacji 210×120×100 | płyta MDF 8 mm (zamknięta skrzynka) | próby drgań, szczelność i rozwarstwienie w narożach; porównanie orientacji sklejki |
| E12 | Osiem przednich dużych wkładów regulacji 210×150×100 | płyta MDF 8 mm (zamknięta skrzynka) | szczelność 8 szt., obciążenia z rzeczywistymi zatrzaskami |
| E13 | Cztery małe wkłady regulacji 180×100×100 | płyta MDF 8 mm (zamknięta skrzynka) | test chwytania i zamknięcia, szczelności, powtarzanego transportu |
| E14 | Klejenie narożne zamkniętych wkładów | klej PVAc D3 KLEIBERIT 303.0 – kandydat technologiczny | próba z wodą/ciśnieniem, peel, zginanie, pełzanie i cykle serwisowe |
| E15 | Dodatnie rygle / zatrzaski wkładów | stal sprężynowa ocynkowana z elementem tłumiącym EPDM | katalogowy rygiel, obliczenie przekroju i zmęczenia, 20 kompletów, test blokady w 2 orientacjach |
| E16 | Uszczelnienie obwodu wkładów | zamkniętokomórkowa pianka EPDM | karta materiałowa, siła domknięcia, przepuszczalność, próba 100→120→150 |
| E17 | Uchwyty / pętle do wyjmowania wkładów | taśma poliestrowa z metalowymi kotwami | wytrzymałość mocowania, kolizje, osie 0/180°, odporność na rozdarcie |
| E18 | Klej ściana–ściana i front–korpus | PVAc KLEIBERIT 303.0 D3 (lub D4 po utwardzaczu) jako kandydat | próbki konkretnych krawędzi MDF44/22, rozwarstwienie i pełzanie 2 orientacje |
| E19 | Klej osiem klocków–front MDF44 | epoksyd dwuskładnikowy LOCTITE EA9466 jako referencja modelowa | rzeczywista szczelina, nośność w peel+shear, zmęczenie i creep |
| E20 | Uszczelka pod kołnierzem głośnika | komórkowa pianka EPDM z kartą compression set | karta σ–ε, siła docisku, sprężyste osiadanie, próba szczelności po serwisie |
| E21 | Osiem śrub montażowych przetwornika | stalowa śruba M5 ISO 4762, klasa 8.8 (HIPOTEZA bez doboru gwintu) | wybrany gwint, przekrój, min długość zakotwienia, korozja, moment z pomiaru |
| E22 | Osiem osadzonych wkładek gwintowanych | stal ocynkowana wkładka gwintowana w drewnie — typ i wymiar do wyboru | potwierdzić zewnętrzne Ø i L, gniazdo, nośność po cyklach |
| E23 | Rama osłony membrany / grill | stal malowana proszkowo – hipotetyczny profil | geometria, nośność na nacisk, bezpieczny prześwit, przewiew, mocowania |
| E24 | Siatka ochronna membrany | blacha stalowa perforowana z wykończeniem antykorozyjnym | wyznaczyć procent otwarcia, promień perforacji, test uderzenia i wibracji |
| E25 | Dystanse i łączniki grilla | stal nierdzewna / poliamid z metalowym gwintem | wybór średnicy, ściąg, moment dokręcenia, pomiar rattle |
| E26 | Cztery stopy lub listwy podparcia | elastomer EPDM z płytką stalową | karta Shore/tłumienia, siła–ugięcie, tarcie, odporność na przewrócenie |
| E27 | Płytka terminala z tyłu | aluminium 2 mm jako kandydat do uszczelnianej płytki | sztywność uszczelnianego wycięcia, prześwit i objętość netto |
| E28 | Uszczelka płytki terminala | EPDM zamkniętokomórkowy | dobór z karty, test nieszczelności w 20–80Hz |
| E29 | Mata tłumiąca przy tylnej ścianie | włóknina poliestrowa 50mm, nominalnie 20kg/m³ jako HIPOTEZA | opór przepływu vs f, masa, grubość, odporność ogniowa i mocowanie |
| E30 | Mocowanie i osłona maty tłumiącej | taśma/siatka poliestrowa i punktowe mocowania PA | test wibracji, odpadania, bezpieczeństwo temperaturowe |
| E31 | Prowadnice i opaski okablowania | poliamid PA66 z odpowiednią odpornością termiczną | karta temperatury, mocowania, promienie gięcia, brak tarcia |
| E32 | Przewody wewnętrzne i izolacja | przewód miedziany wielodrutowy z izolacją odporną termicznie | obliczenie I²R, temperatura, terminal, normy instalacyjne, odporność na wibracje |
| E33 | Wewnętrzne uszczelnienie szczelin korpusu | elastyczny uszczelniacz neutralny silikonowy kompatybilny z MDF | test adhezji do podkładu i szczelności, brak lotnych emisji szkodliwych |
| E34 | Wykończenie ochronne płyt / krawędzi | wodna powłoka uszczelniająca do MDF + lakier | karta absorpcji wilgoci, masa, kompatybilność kleju |
| E35 | Elementy opcjonalnej metalowej ramy | stal konstrukcyjna o udokumentowanej granicy plastyczności | CAD, masa/akustyka, analiza połączeń, dopuszczenie wyłącznie po porównaniu |

**Znaczenie pełnego pokrycia:** 35/35 oznacza *przypisanie materiału i wymogu*, a nie 35/35 policzonych nośności. Wiele pozycji to elementy katalogowe: ich certyfikowane parametry i gabaryty trzeba wprowadzić do obliczeń lub zweryfikować na próbkach. Jeżeli zakres konstrukcji zwiększy się o nowy element (np. prowadnicę, łącznik, pasek wytłumiający), trzeba dopisać nową pozycję do tego samego rejestru **zanim uzna się projekt za zamknięty**.

## 7. Kolejność kwalifikacji — bez mnożenia niepotrzebnych badań w przewodniku

**I. Duże części i nośne połączenia.** Ustalić realne MDF22 i MDF44 (lub zwymiarowaną sklejkę 21), E i gęstość obu kierunków, odporność na zginanie oraz odrywanie warstw. Dla wręg ocenić kierunek, łączność, podpory; dla 8 klocków pod wkładki porównać 20-mm klejonkę z realnie dostępną sklejką o rzeczywistej grubości. Obciążenia śruby przenieść na **układ front+klocek+klej**, a nie tylko na pojedynczy materiał. Dla sklejki stosować ortotropowy MES i zweryfikowaną spoinę.

**II. Wkłady ruchome.** Przeliczyć rzeczywistą masę 20 skrzynek przy MDF8 i alternatywnej sklejce9, szczelność, nośność narożników, uchwyty, zamki i uszczelki. Powtórzyć drogę wkładania K07 i bilans P30E przy zmianie grubości, ponieważ zbyt masywne albo inaczej zwymiarowane wkłady mogą zmienić litraż i serwis. W próbie obciążenia przyjąć jednoznaczną bazę P34C, nie dopisywać wytrzymałości zaczepu bez karty.

**III. Elementy dopełniające konstrukcję.** Dobrać ze znanych kart: EPDM uszczelek i stopek, materiał usztywnienia osłony, matę o zmierzonym oporze przepływu, lakier zabezpieczający krawędzie, przewody i terminal. Przeliczyć ich **masę, objętość, lokalne prześwity i dostęp serwisowy**. Szczególnie grill + terminal + stopki muszą mieścić się w limicie **500 mm całego urządzenia**, a nie tylko korpusu.

**IV. Zamknięcie bramki:** próbki materiałów z tolerancjami, próby spoin i mocowań, pomiary nieszczelności, powtórny MES ze stabilizacją P33C i kontrolą MAC oraz 100/120/150 l, potem prototyp. Bez wyników tych prób status dla wszystkich pozycji jest **CNC HOLD**.

[Skrypt odtwarzający K10](../skrypty/k10_audyt_materialow_obudowy.py) · [Wyniki liczbowe JSON](../wyniki/k10_wyniki_przesiewu_materialow.json) · [Rejestr 35 części](../dane/k10_rejestr_materialow_czesci_obudowy.json) · [test CI](../.github/workflows/k10-material-register.yml).
