# SUB_prototyp — przewodnik po badaniach subwoofera

Projektujemy **prototyp subwoofera zamkniętego z regulowaną objętością**.
Badania mają doprowadzić do wyboru **jednego przetwornika i jednej konstrukcji**:
objętości, płyt, usztywnień, połączeń, kleju oraz wymagań napędu i ochrony.
Ten README prowadzi od pytań projektowych przez najważniejsze wykresy do
raportów, danych i odtwarzalnych obliczeń.

**Stan: 2026-10-25.** Porównujemy 24 modele od 11 producentów, w tym 4 STX.
Najnowszy ukończony zakres to [czasowa analiza styku frontu — raport 034](raporty/034_czasowy_styk_i_pelny_MES.md).
Trwa program badań przed budową; ostateczny wybór i końcowy PDF są przed nami.
Przedstawione wyniki są obliczeniami i symulacjami, bez pomiarów fizycznego prototypu.

| Ustalenie | Obowiązujący kontekst |
|---|---|
| Wymagania | [Brief v0.6](brief_system_audio_DIY_v0.6.md) i [późniejsze decyzje użytkownika](DECYZJE_I_PYTANIA.md) |
| Referencje | ADAM Sub12 i Sub15; progi liczbowe pozostają otwarte |
| Pokój | Około **4,6 × 3,7 × 2,5 m**, 42,55 m³; docelowo **RTV po lewej, kanapa po prawej** oryginalnego rzutu |
| Docelowy system | Dwa subwoofery przy monitorach, jeden sweet spot 2,5–3 m; przyszła architektura co najmniej 8 wyjść DSP |
| Obecny zakres | Nauka, źródła, obliczenia i symulacje do budowy. Zakupy, CAD i dobór aparatury pozostają odłożone |

## Od czego zacząć

- **Chcę zrozumieć wnioski:** przejdź przez [wykresy i ich objaśnienia](#wykresy).
- **Chcę sprawdzić konkretny temat:** wybierz go w [mapie raportów](#mapa).
- **Chcę wiedzieć, co zostało:** zobacz [stan i następne decyzje](#dalsze-prace).
- **Chcę zweryfikować rachunek:** przejdź do [danych i odtwarzania](#odtwarzanie).
- **Szukam starszego dokumentu:** otwórz [pełny indeks raportów](raporty/README.md).

<a id="mapa"></a>
## Mapa badań — pytanie → raport → dane

| Pytanie | Gdzie czytać | Gdzie sprawdzać wejścia lub wyniki |
|---|---|---|
| Jakie głośniki badamy i co wiadomo z opinii? | [010 — szeroka pula](raporty/010_szeroka_pula_i_kwalifikacja.md), [012 — identyfikowalność](raporty/012_identyfikowalnosc_i_dane_publikowane.md) | [24 kandydatów](dane/przetworniki/pula_rozszerzona.json), [krytyczna ocena opinii](dane/zrodla/opinie_puli_ocena.json) |
| Jak dobrać litraż, wychylenie i napęd łącznie? | [011 — granice objętości](raporty/011_granice_globalne_litrazu.md), [028 — wspólne ograniczenia](raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md) | [Wyniki P17](wyniki/p17_podsumowanie.json) |
| Jak niepewność danych zmienia kolejność kandydatów? | [015 — czułość i odporność](raporty/015_niepewnosc_globalna_i_odpornosc.md) | [Baza wiedzy o niepewności](baza_wiedzy/10_niepewnosc_globalna.md) |
| Co robią gaz, wypełnienie i nieszczelności? | [009 — przecieki](raporty/009_N7_straty_nieszczelnosci.md), [016 — gaz i materiały](raporty/016_gaz_wypelnienie_i_granice.md) | [Konfiguracje modeli](dane/konfiguracje/), [źródła](baza_wiedzy/ZRODLA.md) |
| Skąd biorą się nieliniowości i IMD? | [020 — nieliniowy napęd](raporty/020_nieliniowy_naped_i_sprzezony_gaz.md), [021 — pamięć cewki](raporty/021_pamiec_cewki_i_definicja_Lgen.md), [026 — dwa tony](raporty/026_P14B_pelna_kampania_dwutonowa.md) | [Podsumowanie P14B](wyniki/p14b_podsumowanie.json) |
| Jak prąd, temperatura i chłodzenie wpływają na pracę? | [025 — topologia termiki](raporty/025_P15A_topologia_i_granice_termiki.md), [027 — grzanie i napęd](raporty/027_P15B_sprzezenie_grzania_i_napedu.md) | [Podsumowanie P15B](wyniki/p15b_podsumowanie.json) |
| Jak policzyć panele, usztywnienia i klej? | [029 — płyty](raporty/029_P18A_plyty_sciagi_i_dynamika.md), [030 — spoiny](raporty/030_P19A_obliczenia_spoin_i_material_kleju.md), [031 — reakcja powietrza](raporty/031_P21A_reakcja_powietrza_i_bilans.md) | [Materiał MDF i kleje](dane/materialy/), [wyniki mechaniki](wyniki/manifest_mechaniki_P18_P19_P21.json) |
| Jak otwór, kosz i uszczelka zmieniają front? | [033 — front i docisk](raporty/033_front_otwor_kosz_i_styk_jednostronny.md), [034 — styk w czasie](raporty/034_czasowy_styk_i_pelny_MES.md) | [Geometria producentów](dane/zrodla/P18B_geometria_i_ograniczenia.json), [przebiegi P19C](wyniki/p19c_podsumowanie.json) |
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

### 1. Punkt wyjścia: możliwości 24 kandydatów

Porównanie przy wspólnych 100 l, 40 V RMS i 12 A RMS pokazuje, gdzie
ogranicza ruch, a gdzie napęd. Prawy panel ilustruje sam iloczyn Sd·Xmax.
**Wyższy słupek nie oznacza lepszego THD lub gotowego zwycięzcy** — definicje
Xmax różnią się, a ten etap nie zawiera pełnej termiki.

![24 kandydatów — porównanie liniowych ograniczeń i katalogowego Sd razy Xmax](wyniki/09_szeroka_pula.png)

[Raport 010: modele, źródła, konflikty i opinie](raporty/010_szeroka_pula_i_kwalifikacja.md).

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

<a id="dalsze-prace"></a>
## Co wynika dla dalszego projektu

Dotychczasowe badania uzasadniają wspólne dobieranie przetwornika,
objętości i napędu, konstrukcję z kontrolowanymi usztywnieniami oraz
osobne sprawdzenie frontu, docisku i ochrony dynamicznej.
**Ostateczny głośnik i skrzynia nie zostały jeszcze wybrane.**

| Pozostały blok | Decyzja, do której ma doprowadzić |
|---|---|
| Pełna rama i połączenia, regulacja Vb, pole przestrzenne | Geometria prototypu, realne objętości netto, ścieżki sił, szczelność i wykonanie |
| Napęd, cyfrowe DSP, clipping, ochrona i szersze sygnały | Wymagania napięcia/prądu, filtry i kontrola ruchu/temperatury w czasie |
| Dwie sztuki w docelowym pokoju | Wykonalne miejsca, gabaryty, faza, opóźnienia i integracja |
| Odporne porównanie finalistów i domknięcie programu | Jeden przetwornik, jedna regulowana obudowa i końcowy PDF z uzasadnieniem |

Najbliższy krok po P19C: **pełna rama i połączenia obudowy**.
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
```

Podczas aktywnej kampanii nie uruchamiaj pełnego przebiegu archiwizującego
jej wyniki. Zgodne dzienniki i archiwa przywracają wcześniej policzone
przypadki; ich odczyt nie jest nową niezależną replikacją. P19C jawnie
korzysta z zachowanego zimnego pilota i przygotowanych stanów porównawczych.

Manifesty wykonanych etapów: [P14B/P15B](wyniki/manifest_P14B_P15B.json),
[P17](wyniki/manifest_P17.json), [panele i spoiny](wyniki/manifest_mechaniki_P18_P19_P21.json),
[front i docisk](wyniki/manifest_frontu_P18B_P19B.json),
[styk w czasie](wyniki/manifest_styku_czasowego_P19C.json).
Kontrole sprawdzają opisane modele i ich dziedziny; walidacja urządzenia
nastąpi po budowie, zgodnie z [briefem](brief_system_audio_DIY_v0.6.md).
