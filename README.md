# SUB_prototyp — przewodnik po badaniach subwoofera

Projektujemy **prototyp subwoofera zamkniętego z regulowaną objętością**.
Aktualna decyzja [U-021](DECYZJE_I_PYTANIA.md): **front stały, niedemontowalny,
pod jeden docelowo wybrany przetwornik**.
Badania mają doprowadzić do wyboru **jednego przetwornika i jednej konstrukcji**:
objętości, płyt, usztywnień, połączeń, kleju oraz wymagań napędu i ochrony.
Ten README prowadzi od pytań projektowych przez najważniejsze wykresy do
raportów, danych i odtwarzalnych obliczeń.

**Stan: 2026-10-26.** Pula obejmuje **26 produktów od 11 producentów**,
w tym 4 STX i **3 SB Acoustics**. Liczymy **27 konfiguracji elektrycznych**,
ponieważ nowy dwucewkowy SB ma osobno połączenie szeregowe i równoległe.
Najnowsze uzupełnienia to [raport 038 — dodatkowe SB](raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md)
(5832 punkty modelu liniowego) oraz [raport 039 — obliczenia wypełnienia](raporty/039_wypelnienie_ilosc_polozenie_i_straty.md)
(masa, objętość gazu, położenie i 17 820 punktów napędu).
Najnowszy [raport 040 — listwa stałego frontu](raporty/040_listwa_stalego_frontu_i_droga_sily.md)
dodaje 20 wariantów 3D: poprawę sztywności oraz przeniesienie obciążeń
na nowe spoiny. Lokalna zbieżność naprężeń pozostaje otwarta.
Następnie [raport 041 — podmodel lokalny](raporty/041_lokalny_podmodel_i_granice_wiarygodnosci.md)
sprawdza 24 realizacje do 102 033 współrzędnych. W stałym oknie obserwacji
wpływ danych globalnych jest większy niż ostatnich osobnych zagęszczeń lokalnych.
Poprzednie etapy obejmują [pełną ramę 3D — raport 035](raporty/035_pelna_rama_3D_spoiny_i_podparcie.md),
[screening spoin/odspojenia — raport 036](raporty/036_spoiny_3D_i_wirtualne_odspojenie.md)
i [wymagania modułu spoin stałego frontu — raport 037](raporty/037_staly_front_wymagany_modul_spoin.md).
Trwa program badań przed budową; ostateczny wybór i końcowy PDF są przed nami.
Przedstawione wyniki są obliczeniami i symulacjami, bez pomiarów fizycznego prototypu.

**Zakresy nie są jednakowe:** duże kampanie niepewności, nieliniowości
i termiki wykonano dla pierwotnych 24 baz. Nowe SB mają dane producenta,
ocenę dostępnych opinii i porównanie liniowe; nie przypisujemy im automatycznie
wyników starszych kampanii. C04 jest referencją części modeli mechanicznych,
nie zatwierdzonym docelowym głośnikiem.

| Ustalenie | Obowiązujący kontekst |
|---|---|
| Wymagania | [Brief v0.6](brief_system_audio_DIY_v0.6.md) i [późniejsze decyzje użytkownika](DECYZJE_I_PYTANIA.md) |
| Referencje | ADAM Sub12 i Sub15; progi liczbowe pozostają otwarte |
| Pokój | Około **4,6 × 3,7 × 2,5 m**, 42,55 m³; docelowo **RTV po lewej, kanapa po prawej** oryginalnego rzutu |
| Docelowy system | Dwa subwoofery przy monitorach, jeden sweet spot 2,5–3 m; przyszła architektura co najmniej 8 wyjść DSP |
| Obecny zakres | Nauka, źródła, obliczenia i symulacje do budowy. Zakupy, CAD i dobór aparatury pozostają odłożone |

## Najważniejsze ustalenia przed lekturą

| Temat | Co wynika z badań | Co pozostaje do rozstrzygnięcia |
|---|---|---|
| Głośnik | **Obliczenie:** przewaga zależy od pasma i aktywnego limitu X/V/I; większe Sd lub mniejsze Le nie rozstrzyga wyboru | Jedna końcowa rekomendacja po integracji niepewności, termiki, konstrukcji i DSP |
| Litraż | **Obliczenie:** trzeba wspólnie spełnić ograniczenia napędu i ruchu; po dojściu do Sd·Xmax dalszy litraż nie podnosi pułapu samego ruchu | Zakres regulacji, netto po odjęciu elementów i mechanizm regulacji |
| Wypełnienie | **Obliczenie/symulacja:** liczymy masę, objętość włókien i gazu oraz wpływ położenia na straty; porowata mata i sztywny wkład mają różne bilanse | Konkretny materiał, rozmieszczenie, mocowanie i powiązanie z komorą 3D oraz regulacją Vb |
| Konstrukcja | **Symulacja:** w referencyjnej ramie jeden ściąg zmniejsza podatność o około 18% przy dodatkowych 0,464 kg | Geometria dla wybranego głośnika, lokalne połączenia i pełne sprzężenie z powietrzem |
| Klej | **Symulacja:** wyznaczono wymagania sztywności; energia wirtualnego odspojenia zmienia się o 27–41% między dwiema siatkami | Nośność, adhezja do MDF, pełzanie, zmęczenie i zbieżna analiza lokalna; D3/D4 nie wystarcza |
| Pokój i ochrona | **Założenia/scenariusze:** znamy wymiary i orientację mebli; pozycje i straty nie są zmierzone. Dwa tony mogą generować ruch poniżej pasma wejścia | Dwie wykonalne lokalizacje, integracja fazowa, dyskretne DSP i ochrona w czasie |

## Od czego zacząć

- **Chcę zrozumieć wnioski:** przejdź przez [wykresy i ich objaśnienia](#wykresy).
- **Chcę sprawdzić konkretny temat:** wybierz go w [mapie raportów](#mapa).
- **Chcę wiedzieć, co zostało:** zobacz [stan i następne decyzje](#dalsze-prace).
- **Chcę zweryfikować rachunek:** przejdź do [danych i odtwarzania](#odtwarzanie).
- **Szukam starszego dokumentu:** otwórz [pełny indeks raportów](raporty/README.md).

Jeśli czytasz tylko kilka dokumentów: zacznij od **038/039** (SB i wypełnienie),
**028** (wspólne wymagania napędu i objętości), **035–037** (rama i klej),
a potem sprawdź otwarte bramki w **programie 30 pakietów**.
Starszy raport opisuje stan swojego etapu; bieżące decyzje i zakres prowadzi
ten przewodnik. „Wykonano rodzinę modeli” nie oznacza zamknięcia całego pakietu.

<a id="mapa"></a>
## Mapa badań — pytanie → raport → dane

| Pytanie | Gdzie czytać | Gdzie sprawdzać wejścia lub wyniki |
|---|---|---|
| Jakie głośniki badamy i co wiadomo z opinii? | [010 — pierwotna szeroka pula](raporty/010_szeroka_pula_i_kwalifikacja.md), [012 — identyfikowalność](raporty/012_identyfikowalnosc_i_dane_publikowane.md), [038 — dodatkowe SB](raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md) | [24 bazy](dane/przetworniki/pula_rozszerzona.json) + [2 produkty SB](dane/przetworniki/rozszerzenie_SB_20261025.json); [opinie puli](dane/zrodla/opinie_puli_ocena.json) i [nowych SB](dane/zrodla/SB_rozszerzenie_pochodzenie.json) |
| Jak dobrać litraż, wychylenie i napęd łącznie? | [011 — granice objętości](raporty/011_granice_globalne_litrazu.md), [028 — wspólne ograniczenia](raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md) | [Wyniki P17](wyniki/p17_podsumowanie.json) |
| Jak niepewność danych zmienia kolejność kandydatów? | [015 — czułość i odporność](raporty/015_niepewnosc_globalna_i_odpornosc.md) | [Baza wiedzy o niepewności](baza_wiedzy/10_niepewnosc_globalna.md) |
| Co robią gaz, wypełnienie i nieszczelności? | [009 — przecieki](raporty/009_N7_straty_nieszczelnosci.md), [016 — gaz i materiały](raporty/016_gaz_wypelnienie_i_granice.md), [039 — ilość i położenie materiału](raporty/039_wypelnienie_ilosc_polozenie_i_straty.md) | [Geometria, masa i podatność](wyniki/p09c_geometria_masa_i_podatnosc.csv), [17 820 punktów napędu](wyniki/p09c_naped_i_wypelnienie.csv), [konfiguracje](dane/konfiguracje/) |
| Skąd biorą się nieliniowości i IMD? | [020 — nieliniowy napęd](raporty/020_nieliniowy_naped_i_sprzezony_gaz.md), [021 — pamięć cewki](raporty/021_pamiec_cewki_i_definicja_Lgen.md), [026 — dwa tony](raporty/026_P14B_pelna_kampania_dwutonowa.md) | [Podsumowanie P14B](wyniki/p14b_podsumowanie.json) |
| Jak prąd, temperatura i chłodzenie wpływają na pracę? | [025 — topologia termiki](raporty/025_P15A_topologia_i_granice_termiki.md), [027 — grzanie i napęd](raporty/027_P15B_sprzezenie_grzania_i_napedu.md) | [Podsumowanie P15B](wyniki/p15b_podsumowanie.json) |
| Jak policzyć panele, usztywnienia i klej? | [029 — płyty](raporty/029_P18A_plyty_sciagi_i_dynamika.md), [030 — spoiny](raporty/030_P19A_obliczenia_spoin_i_material_kleju.md), [035 — pełna rama](raporty/035_pelna_rama_3D_spoiny_i_podparcie.md), [036 — defekt spoiny](raporty/036_spoiny_3D_i_wirtualne_odspojenie.md) | [Materiał MDF i kleje](dane/materialy/), [wyniki 3D](wyniki/manifest_ramy_i_spoin_3D.json) |
| Jak otwór, kosz i uszczelka zmieniają front? | [033 — front i docisk](raporty/033_front_otwor_kosz_i_styk_jednostronny.md), [034 — styk w czasie](raporty/034_czasowy_styk_i_pelny_MES.md) | [Geometria producentów](dane/zrodla/P18B_geometria_i_ograniczenia.json), [przebiegi P19C](wyniki/p19c_podsumowanie.json) |
| Co oznacza stały front i jak dobrać jego połączenie? | [037 — wymagania modułu](raporty/037_staly_front_wymagany_modul_spoin.md), [040 — listwa i droga siły](raporty/040_listwa_stalego_frontu_i_droga_sily.md), [041 — podmodel i dane brzegowe](raporty/041_lokalny_podmodel_i_granice_wiarygodnosci.md), [U-021](DECYZJE_I_PYTANIA.md) | [12 progów](wyniki/p19e_wymagane_moduly_stalego_frontu.csv), [20 wariantów listwy](wyniki/p19f_geometrie_i_podatnosc.csv), [24 lokalne realizacje](wyniki/p19g_ocena_i_roznice.json) |
| Jak uwzględniamy pokój i dwie sztuki? | [013 — dwa źródła i gabaryty](raporty/013_pokoj_i_realne_gabaryty.md), [017 — sprzężenie pola](raporty/017_promieniowanie_i_sprzezenie_pokoju.md), [019 — aktualna orientacja](raporty/019_zamiana_kanapy_i_RTV.md) | [Konwencja pokoju](dane/konfiguracje/pokoj_odsluchowy.json), scenariusze opisane w raportach |

Pełny zakres i otwarte bramki są w [programie 30 pakietów](PROGRAM_30_BADAN.md).
Podstawy fizyczne wyjaśnia [baza wiedzy](baza_wiedzy/README.md), a ślad pracy
zapisujemy w [AGENTS.md](AGENTS.md).

<a id="wykresy"></a>
## Najważniejsze wykresy i wnioski projektowe

Czytaj warunki każdego wykresu: częstotliwość, sygnał, RMS/szczyt, odległość,
geometrię oraz aktywny limit. Wykresy używają różnych eksperymentów — m.in.
2π i 4π — więc ich liczb SPL nie porównuje się bezpośrednio.
Zakresy stresowe opisują przyjęte hipotezy; nie są tolerancjami producentów.

### 1. Głośniki: pierwotna pula i dodatkowe SB Acoustics

Porównanie przy wspólnych 100 l, 40 V RMS i 12 A RMS pokazuje, gdzie
ogranicza ruch, a gdzie napęd. Prawy panel ilustruje sam iloczyn Sd·Xmax.
**Wyższy słupek nie oznacza lepszego THD lub gotowego zwycięzcy** — definicje
Xmax różnią się, a ten etap nie zawiera pełnej termiki.

![24 kandydatów — porównanie liniowych ograniczeń i katalogowego Sd razy Xmax](wyniki/09_szeroka_pula.png)

[Raport 010: modele, źródła, konflikty i opinie](raporty/010_szeroka_pula_i_kwalifikacja.md).

Powyższy wykres zachowuje **pierwotne 24 bazy**. Nowe rozszerzenie dodaje
SB34SWNRX-S75-6 oraz SB34SWPL76-3-DV, bez nadpisywania dawnych danych.

| Identyfikator | Model SB Acoustics | Konfiguracja |
|---|---|---|
| C04 | SB34SWPL76-4 | Jedna cewka, istniejący model odniesienia |
| C25 | SB34SWNRX-S75-6 | Jedna cewka; PDF podaje 22,5 mm p-p, WWW 22 mm p-p |
| C26P / C26S | SB34SWPL76-3-DV | Ten sam produkt: obie cewki równolegle / szeregowo |

![SB Acoustics — porównanie napędu i litrażu z odniesieniami C01/C02 Dayton](wyniki/61_SB_porownanie_i_objetosc.png)

**Wynik liniowy:** przy wspólnych 100 l, 40 V RMS/12 A RMS i 80 Hz
C26P ogranicza prąd, a C26S napięcie. Przy 20 Hz obie konfiguracje
dochodzą do tego samego Sd·Xmax. C25 ma większe Sd niż C04, lecz mniejszy
iloczyn Sd·Xmax. Nie oznacza to rozstrzygnięcia THD lub jakości odsłuchu.
Każda częstotliwość to osobny sinus ustalony, bez kwalifikacji czasu pracy.

[Raport 038: wyniki, oryginalne źródła, opinie i braki](raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md)
· [27 konfiguracji w tabeli](wyniki/sb_rozszerzenie_podsumowanie.csv).

### 2. Odporność wyboru: czy kolejność przetrwa niepewność?

Obwiednie pokazują wpływ zadanych zakresów parametrów. Nakładanie się
obwiedni i zmiana przyjętego użytecznego skoku mogą odwrócić kolejność.
Nie utożsamiamy udziału wygranych w losowaniu z prawdopodobieństwem,
że dany fizyczny głośnik będzie lepszy.

![Niepewność parametrów i warunkowa zmiana kolejności kandydatów](wyniki/11_niepewnosc_i_kolejnosc.png)

[Raport 015: dziedziny, obwiednie i kontrprzykłady](raporty/015_niepewnosc_globalna_i_odpornosc.md).

### 3. Litraż: napięcie, prąd, ruch i chłodzenie muszą zgadzać się jednocześnie

Przedziały objętości wynikają ze wspólnych warunków dla sześciu **osobnych**
sinusów 20–80 Hz. Ilustracja używa 90 dB RMS, 4π/1 m, 40 V/12 A i testowych
parametrów cieplnych. Są to warunki obliczenia, nie zatwierdzone wymagania
klienta, muzyka ani wynik SPL w pokoju.

![Wspólne przedziały objętości przy ograniczeniach napędu i założonym chłodzeniu](wyniki/42_P17_wspolna_objetosc_i_chlodzenie.png)

[Raport 028: jak powstają granice i co je ogranicza](raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md).

### 4. Powietrze i wypełnienie: podatność zależy od częstotliwości

Gaz przechodzi między odpowiedzią bliższą izotermicznej i adiabatycznej,
a wymiana ciepła wprowadza straty. Wypełnienia nie zastępujemy jednym
stałym „bonusem litrów”. Pokazane czasy relaksacji są rodzinami modeli,
bez identyfikacji konkretnej włókniny.

![Relaksacja cieplna gazu — sztywność, straty i wpływ na odpowiedź](wyniki/13_relaksacja_cieplna_gazu.png)

[Raport 016: gaz, pory, materiały, nieliniowości i granice](raporty/016_gaz_wypelnienie_i_granice.md).

**Ilość wypełnienia również jest liczona.** Dla kontrolnej geometrii
460 × 640 × 460 mm, przed odjęciem kosza i ściągów, wyklejenie pięciu
ścian warstwą 50 mm ma około **1,18 kg** przy założonej gęstości 20 kg/m³.
Przy phi=0,98 rzeczywista objętość gazu wynosi około 134,24 l z początkowych
135,42 l. Obrys materiału zajmuje więcej miejsca niż same włókna.
To scenariusz obliczenia, nie ilość do zakupu lub końcowy litraż.

![Wypełnienie — masa, rzeczywista objętość gazu i oddzielne granice podatności](wyniki/62_P09C_masa_materialu_i_objetosc_gazu.png)

**Rozmieszczenie też ma znaczenie.** Poniżej ten sam materiał ma tę samą
masę, a zmieniamy jego położenie w modelu 1D. Warstwa przez cały przekrój
jest osobnym eksperymentem od wyklejenia pięciu ścian. Veq i oporu wejściowego
nie traktujemy jako stałego przyrostu fizycznych litrów lub rankingu jakości.

![Ta sama warstwa w trzech położeniach — zmiana strat i granicy napędu](wyniki/63_P09C_polozenie_warstwy_i_naped.png)

[Raport 039: geometria, 55 modeli warstwowych, 27 konfiguracji i niezależna sieć FV](raporty/039_wypelnienie_ilosc_polozenie_i_straty.md).
Wybór materiału, masy i rozmieszczenia wejdzie do końcowej rekomendacji;
**sztywne wkłady do regulacji Vb** będą liczone osobno.

### 5. Dwa tony: ruch może pojawić się również poniżej pasma wejścia

W warunkowym przykładzie 45 + 95 Hz powstaje produkt przy 5 Hz.
Znaczenie mechaniczne i emisja akustyczna są różne: w tym odniesieniu
ciśnienie zależy od przyspieszenia. Filtr wejściowy nie usuwa produktu
wytworzonego później przez model nieliniowy.

![Przykład IMD — ruch przy 5 Hz i odrębna projekcja ciśnienia](wyniki/31_P14B_ruch_i_emisja_5Hz.png)

[Opis przykładu i projekcji](raporty/024_P14B_emisja_i_swiadkowie.md)
· [zakończony zadany zbiór 3312 przypadków](raporty/026_P14B_pelna_kampania_dwutonowa.md).
Krzywe są hipotetyczne; nie przedstawiają zmierzonego IMD modelu handlowego.

### 6. Termika: mniejszy prąd nie zawsze oznacza mniejsze grzanie

Przy stałym napięciu wzrost Re zmniejsza prąd, lecz moc I²Re może
początkowo rosnąć — decyduje również zespolona impedancja.
Ochrona cieplna musi uwzględniać historię strat i warunki chłodzenia.
Alpha = 0,004/K na wykresie jest założeniem tego eksperymentu.

![Wpływ temperatury na prąd i moc grzania przy stałym napięciu](wyniki/37_P15B_prad_i_grzanie.png)

[Raport 027: sprzężenie cieplne, obwiednie i ograniczenia danych](raporty/027_P15B_sprzezenie_grzania_i_napedu.md).

### 7. Pokój: częstotliwość modu nie określa jeszcze jego amplitudy

Idealny prostopadłościan o wymiarach z briefu ma pierwsze mody osiowe
około 37,3 / 46,4 / 68,6 Hz. Ich poziomy i zaniki zależą od strat,
otwarć oraz położenia źródeł i słuchacza. Dokładne pozycje pozostają
nieznane; jawne scenariusze nie stają się pomiarem pokoju.

![Mody osiowe idealnego pokoju — częstotliwości bez założonych amplitud](wyniki/02_mody_osiowe.png)

[Raport 013: modele pokoju i dwie sztuki](raporty/013_pokoj_i_realne_gabaryty.md)
· [raport 019: RTV po lewej, kanapa po prawej](raporty/019_zamiana_kanapy_i_RTV.md).

### 8. Ścianki: usztywnienie może dać więcej niż sama grubość

W referencyjnej parze ścian 460 × 640 × 22 mm przy 1 kPa statycznym
jeden ściąg zmniejsza ugięcie z około 154,7 do 29,7 µm, a dwa do 12,7 µm
w wariancie SSSS. Trzeba równocześnie sprawdzić masę, nakładki,
połączenia i postacie, których ściąg nie usztywnia.

![Grubość MDF i ściągi — częstotliwości własne oraz statyczne ugięcie](wyniki/43_P18A_grubosc_sciagi_i_ugiecie.png)

[Raport 029: model MES, kontrole i granice wniosku](raporty/029_P18A_plyty_sciagi_i_dynamika.md).

### 9. Klej i nakładki: średnie F/A nie wystarcza

Rozmiar nakładki, jej grubość i podatność MDF zmieniają koncentrację
naprężeń. Większe pole nie zapewnia proporcjonalnego spadku szczytu.
Obliczone pole modelu spoiny nie jest rzeczywistym maksimum 3D;
klasa D3/D4 nie zastępuje nośności, pełzania ani zmęczenia połączenia.

![Rozprowadzanie siły przez nakładkę — koncentracja naprężeń w modelu](wyniki/47_P19A_nakladka_i_koncentracja_naprezen.png)

[Raport 030: obliczenia spoin, referencja kleju i brakujące dane trwałości](raporty/030_P19A_obliczenia_spoin_i_material_kleju.md).

### 10. Front: otwór i kosz zmieniają konstrukcję

Siatka odwzorowuje otwór główny i skończone obszary przekazywania sił.
Pokazane średnice pochodzą z rysunków producentów; nie jest to dokumentacja
CNC. Luz, frez i lokalne otwory śrubowe wymagają osobnego dopracowania.

![Siatki frontów z nominalnymi otworami C04 i C02 oraz modelowymi łatami mocowania](wyniki/49_P18B_siatka_frontu_z_otworem.png)

Porównanie niżej izoluje wpływ geometrii przy **wspólnym umownym ładunku
10 kg**. Nie przypisuje tej masy wszystkim głośnikom. Miękkie mocowanie
może ograniczać korzyść z pogrubienia frontu, a pierwszy mod może być przechyłem kosza.

![Wpływ grubości frontu i zamocowania na częstotliwość oraz ruch kosza](wyniki/50_P18B_grubosc_i_ruch_kosza.png)

[Raport 033: front, masa, mocowania i niezależne odniesienia](raporty/033_front_otwor_kosz_i_styk_jednostronny.md).

### 11. Docisk: uszczelka i śruby mają różne warunki pracy

Uszczelka przenosi ściskanie, a śruby w modelowanej drodze siły —
rozciąganie. Parametr T₀ oznacza zadane skrócenie sprężyny pomnożone
przez jej sztywność; nie jest momentem dokręcania ani zachowaną siłą.
W P19B 20 z 72 scenariuszy wskazało możliwą zmianę styku.

![Docisk, zachowane siły śrub i flagi nieadekwatności zamrożonego styku](wyniki/52_P19B_docisk_i_bramki_styku.png)

[Raport 033: jednostronny docisk i jawne flagi](raporty/033_front_otwor_kosz_i_styk_jednostronny.md).

### 12. Styk w czasie: rozstrzygnięcie konkretnego przypadku przy 80 Hz

Dla wskazanego C04 z hipotetyczną uszczelką obliczono okresowe otwieranie
styku przy zadanym względnym ruchu stożka 1 mm RMS. Sprawdzono redukcję,
energię, inny integrator i pełne 2959 współrzędnych MES. Jest to jeden
warunkowy przypadek; nie potwierdzenie hałasu, przecieku lub THD produktu.

![Czasowy przebieg ruchu, otwierania styku, bilansu energii i harmonicznych kontaktu](wyniki/53_P19C_przebieg_styku_i_energia.png)

[Raport 034: wynik, zbieżność i ograniczenia](raporty/034_czasowy_styk_i_pelny_MES.md)
· [dodatkowy wykres zbieżności](wyniki/54_P19C_zbieznosc_i_pelny_MES.png).

### 13. Cała rama: połączenia ścian, masa i podparcie

![Geometria kontrolna sześciu ścian, połączeń i kosza — widok poglądowy](wyniki/55_P18C_pelna_rama_i_polaczenia.png)

To geometria kontrolna, **nie gotowa skrzynia do zamówienia**:
460 × 640 × 460 mm wewnątrz, ścianki 22 mm. Rozsunięcie ścian na rysunku
służy czytelności; nie jest szczeliną konstrukcyjną. Geometria brutto
nie jest finalnym Vb netto po odjęciu głośnika, usztywnień i regulacji.

Model obejmuje sześć brył i dwanaście podatnych spoin. Wariant z jednym
ściągiem zmniejsza obliczoną podatność o około 18% przy dodatkowych 0,464 kg.
Ruch przy osobnej sile 1 N RMS zależy także od podparcia. Głośnik jest tu
sztywną masą odniesienia. Zgodnie z U-021 rozwijamy stałe połączenie
frontu z korpusem; wykres nie jest odpowiedzią całego napędu elektroakustycznego.

![Pełna rama — porównanie ściągów, masy i scenariuszy podparcia](wyniki/57_P18C_sciagi_masa_i_podparcie.png)

[Raport 035: siatki do 36 771 współrzędnych, równowaga i ograniczenia](raporty/035_pelna_rama_3D_spoiny_i_podparcie.md)
· [raport 036: energia wirtualnego odspojenia nie jest jeszcze zbieżna](raporty/036_spoiny_3D_i_wirtualne_odspojenie.md).

![Wirtualne odspojenie — energia i zachowany styk ściskający; porównanie siatek](wyniki/59_P19D_wirtualne_odspojenie_i_kontakt.png)

**Otwarta bramka:** wynik energii dla defektu 10 mm różni się o około
27% dla ciężaru i 41% dla ciężaru z ciśnieniem statycznym 1 kPa między
N=10 i N=14. Gδ z tego eksperymentu nie jest odpornością materiałową Gc,
trwałością spoiny lub potwierdzeniem doboru kleju. Stały front pozostaje
decyzją projektu; dopracowania wymaga lokalna droga przenoszenia sił.

**Listwa przy stałym froncie:** dodatkowa bryła łączy front z dnem przez
dwie nowe spoiny. Wariant 30 × 30 mm/440 mm dodaje około 0,289 kg
i zajmuje 0,396 l. Kontrolna podatność przy tym samym H spada około
2,6%; rzeczywisty port ciśnienia zmienia się po zasłonięciu powierzchni.

![Listwa — poprawa sztywności oraz przejęcie naprężeń przez nowe spoiny](wyniki/65_P19F_sztywnosc_i_przeniesienie_naprezen.png)

**Wynik wymagający dalszej analizy:** dla 30 mm lokalne RMS naprężeń
zmienia się o 17–27% między N=14 i 18. Nowa spoina może przejąć większą
koncentrację, mimo poprawy globalnej sztywności. Nie zatwierdzamy z tego
kleju lub trwałości. Obciążenie: ciężar i statyczne 1 kPa, model C04.

![Lokalne naprężenia — odrębna zależność od siatki i modułu nowych spoin](wyniki/66_P19F_siatka_i_modul_nowych_spoin.png)

[Raport 040: geometria, tensor masy/ciśnienia, kontrola Schura i pole do podmodelu](raporty/040_listwa_stalego_frontu_i_droga_sily.md).

**Podmodel P19G:** w stałym fragmencie pierwotnej spoiny dalsze zagęszczenie
przekroju zmienia RMS rozciągania o około 0,45%, a ścinania o 0,10%.
Osobne zagęszczenie wzdłuż listwy daje około 0,043/0,081%.
To skończone kontrole dwóch kierunków. Ocena całych spoin z 040 pozostaje
otwarta; okno z odcięciem 5 mm nie jest materiałową strefą kohezji.

![Lokalny podmodel — osobne zagęszczenia przekroju oraz długości listwy](wyniki/68_P19G_dwa_kierunki_zbieznosci.png)

**Dane brzegowe też ograniczają wynik:** zmiana źródłowego pola N14→N18
daje około +19,4% rozciągania i +14,6% ścinania w tym samym oknie.
Nie uznajemy zera dodatniej części w pojedynczej siatce za dowód nośności.
Zachowano wpływ odległości granicy i częściowo wyciętej podpory.

![Podmodel — wpływ odległości granicy i źródłowego pola globalnego](wyniki/69_P19G_granica_i_pole_globalne.png)

[Raport 041: 24 podmodele, 144 oceny okien, transfer stóp i kontrole obciążeń](raporty/041_lokalny_podmodel_i_granice_wiarygodnosci.md).

### 14. Stały front: wymagany moduł spoiny

Wyznaczono progi efektywnego E dla zadanego przyrostu podatności, osobno
dla samego frontu i wszystkich spoin. Przykładowo dla +10% C i warstwy
0,2 mm na N=14 wynoszą około 9,09 i 72,14 MPa. Są to wyniki modelu
sztywności; nie gwarancja nośności, adhezji, pełzania lub zmęczenia.
Scenariusze 5/10/20% nie są zatwierdzonymi progami briefu.

![Stały front — wymagania efektywnego modułu spoiny i wpływ grubości warstwy](wyniki/60_P19E_staly_front_i_wymagany_modul.png)

[Raport 037: metoda monotoniczna, dane i ograniczenia siatki](raporty/037_staly_front_wymagany_modul_spoin.md).

<a id="dalsze-prace"></a>
## Co wynika dla dalszego projektu

Dotychczasowe badania uzasadniają wspólne dobieranie przetwornika,
objętości i napędu, konstrukcję z kontrolowanymi usztywnieniami oraz
osobne sprawdzenie frontu, docisku i ochrony dynamicznej.
**Ostateczny głośnik i skrzynia nie zostały jeszcze wybrane.**

| Pozostały blok | Decyzja, do której ma doprowadzić |
|---|---|
| Nowe SB i porównanie finalistów | Uzupełnienie odporności i wspólnych wymagań napędu; wynik liniowy nie zastępuje brakujących danych fizycznych |
| Stały front i jego połączenie z korpusem, regulacja Vb, pole przestrzenne | Geometria prototypu, realne objętości netto, ścieżki sił, szczelność i wykonanie |
| Wypełnienie w docelowej geometrii | Materiał, masa, rozmieszczenie, mocowanie, prześwity i wpływ na straty/podatność przy różnych Vb |
| Napęd, cyfrowe DSP, clipping, ochrona i szersze sygnały | Wymagania napięcia/prądu, filtry i kontrola ruchu/temperatury w czasie |
| Dwie sztuki w docelowym pokoju | Wykonalne miejsca, gabaryty, faza, opóźnienia i integracja |
| Odporne porównanie finalistów i domknięcie programu | Jeden przetwornik, jedna regulowana obudowa i końcowy PDF z uzasadnieniem |

Najbliższy krok po P19G: **P20 — sztywne wkłady regulacji Vb**, dostęp
przy stałym froncie, bilans netto, masa, podatność ich ścian i obciążenia
mocowania. Następnie pole przestrzenne P21. Wyniki połączeń pozostają
warunkowe względem materiału i źródłowego pola; kolejne same lokalne
zagęszczenia nie zastąpią tych danych.
Gałąź doboru po raporcie 038 wymaga rozszerzenia analizy odporności
i wspólnych ograniczeń na nowe SB. Obecne porównanie nie zatwierdza jeszcze
głośnika, kleju lub litrażu wykonawczego.
Stan każdego pakietu sprawdzaj w [programie badań](PROGRAM_30_BADAN.md).
[Raport 032](raporty/032_postep_po_mechanice_i_zakres_do_konca.md) opisuje
orientacyjną ocenę postępu po wcześniejszym etapie; liczba symulacji
nie jest procentem gotowości urządzenia.

<a id="odtwarzanie"></a>
## Dane, kod i odtwarzanie

| Katalog lub dokument | Zastosowanie |
|---|---|
| [dane/przetworniki](dane/przetworniki/) | Parametry katalogowe, modele, konflikty i luki |
| [dane/konfiguracje](dane/konfiguracje/) | Jawne wejścia, jednostki i scenariusze |
| [dane/zrodla](dane/zrodla/) i [rejestr źródeł](baza_wiedzy/ZRODLA.md) | Pochodzenie danych, oryginały/odczyty, daty i hashe |
| [skrypty](skrypty/) | Modele Python, niezależne kontrole i generowanie wykresów |
| [wyniki](wyniki/) | CSV, JSON, wykresy PNG/SVG i manifesty przebiegów |
| [raporty](raporty/README.md) | Interpretacja, rekomendacje i ograniczenia wyników |
| [baza_wiedzy](baza_wiedzy/README.md) | Wyjaśnienia fizyki i metod obliczeniowych |
| [dane/pomiary](dane/pomiary/README.md) | Miejsce przyszłych pomiarów; obecnie bez wyników urządzenia |

Obliczenia używają Pythona 3.12, NumPy, SciPy, SymPy i Matplotlib.
[Wymagania środowiska](requirements.txt); dokładne wersje i hashe są
zapisywane w manifestach. Skrypty ustalają katalog projektu z własnej ścieżki.

Pełne odtworzenie archiwizuje poprzedni stan wyników:

```bash
python3 skrypty/odtworz_wszystko.py
```

Można również uruchomić tylko interesujący etap:

```bash
# Panele, spoiny i reakcja powietrza P18A/P19A/P21A
python3 skrypty/odtworz_mechanike_P18_P19_P21.py

# Front i docisk P18B/P19B
OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_front_i_styk_P18B_P19B.py

# Czasowa odpowiedź styku P19C
OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_styk_czasowy_P19C.py

# Dodatkowe SB i porównanie liniowe całej rozszerzonej puli
OPENBLAS_NUM_THREADS=1 python3 skrypty/analiza_rozszerzenia_SB.py
python3 skrypty/manifest_rozszerzenia_SB.py

# Ilość i rozmieszczenie wypełnienia P09C
OPENBLAS_NUM_THREADS=1 python3 skrypty/analiza_ilosci_i_rozmieszczenia_wypelnienia.py
python3 skrypty/manifest_wypelnienia_P09C.py

# Listwa stałego frontu P19F, niezależne kontrole i zachowanie pola
OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_listwe_P19F.py

# Lokalny podmodel P19G i osobne kontrole kierunków siatki
OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_podmodel_P19G.py
```

Podczas aktywnej kampanii nie uruchamiaj pełnego przebiegu archiwizującego
jej wyniki. Zgodne dzienniki i archiwa przywracają wcześniej policzone
przypadki; ich odczyt nie jest nową niezależną replikacją. P19C jawnie
korzysta z zachowanego zimnego pilota i przygotowanych stanów porównawczych.

Etap ramy i spoin 3D można odtworzyć osobno:

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_rame_i_spoiny_3D.py

Manifesty wykonanych etapów: [P14B/P15B](wyniki/manifest_P14B_P15B.json),
[P17](wyniki/manifest_P17.json), [panele i spoiny](wyniki/manifest_mechaniki_P18_P19_P21.json),
[front i docisk](wyniki/manifest_frontu_P18B_P19B.json),
[styk w czasie](wyniki/manifest_styku_czasowego_P19C.json),
[rama i spoiny 3D](wyniki/manifest_ramy_i_spoin_3D.json),
[rozszerzenie SB](wyniki/manifest_rozszerzenia_SB.json),
[wypełnienie P09C](wyniki/manifest_wypelnienia_P09C.json),
[listwa P19F](wyniki/manifest_listwy_P19F.json),
[podmodel P19G](wyniki/manifest_podmodelu_P19G.json).
[Nowe SB: wejścia, wersje i kontrole](wyniki/sb_rozszerzenie_weryfikacja.json)
opisują osobny etap 5832 punktów. Surowe oryginały nowych PDF i wyciągi
tekstów zachowujemy prywatnie; publiczny [rejestr](dane/zrodla/SB_rozszerzenie_pochodzenie.json)
zawiera URL, rewizje, hashe i zakres odczytu.
Kontrole sprawdzają opisane modele i ich dziedziny; walidacja urządzenia
nastąpi po budowie, zgodnie z [briefem](brief_system_audio_DIY_v0.6.md).
