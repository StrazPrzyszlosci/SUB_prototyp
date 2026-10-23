# 06. Metrologia i walidacja prototypu subwoofera

Dokument roboczy B+R, 2026-10-23. Podstawa: `brief_system_audio_DIY_v0.6.md`, z uwzględnieniem nadrzędnej aktualizacji użytkownika poniżej. Dokument opisuje plan pracy i ograniczenia metod; nie zawiera wyników pomiarów ani zatwierdzonych progów odbiorowych. Nie wykonywano tu researchu internetowego ani weryfikacji norm.

Powiązania planowane: [plan B+R](../PLAN_B_R.md), [raport inicjalizacji](../raporty/001_inicjalizacja.md), [szablon raportu pomiarowego](../szablony/raport_pomiarowy.md).

## 1. Obowiązująca aktualizacja i kolejność pracy

| ID | Data | Ustalenie nadrzędne wobec briefu | Skutek dla walidacji |
| --- | --- | --- | --- |
| U-001 | 2026-10-23 | Użytkownik ma multimetr, oscyloskop i lutownicę. | Posiadane przyrządy można wykorzystać w zakresie ich rzeczywiście potwierdzonych możliwości; nie zakładamy posiadania mikrofonu, interfejsu ani odpowiednich sond. |
| U-002 | 2026-10-23 | Dobór i zakupy toru pomiarowego po zakończeniu budowy prototypu. | Nie dobieramy teraz modeli, sond ani zestawu zakupowego. Przed budową nie wymagamy pomiarów T/S, mikrofonu ani interfejsu. |
| U-003 | 2026-10-23 | Pomiary są możliwe wyłącznie w pokoju odsłuchowym. | Wszystkie wykonywane pomiary akustyczne opisujemy jako in-room. Ground-plane pozostaje wiedzą o niedostępnej metodzie odniesienia; nie jest zadaniem, warunkiem rozpoczęcia budowy ani obowiązkową bramką. |
| U-004 | 2026-10-23 | Obecny zakres to praca badawcza do budowy prototypu. | Opis budowy i pomiarów poniżej jest planem dalszych etapów; obecnie prowadzimy research, obliczenia i dokumentację. |
| U-005 | 2026-10-23 | Uwzględniamy opinie użytkowników i osób znających aktualne przetworniki. | Relacje zapisujemy oddzielnie z modelem i warunkami; nie mieszamy ich z wynikami pomiarów. |

Obowiązuje następujący podział:

1. **Przed budową:** zebrać katalogowe T/S i warunki ich deklaracji; opisać tolerancje, braki oraz scenariusze modelu. Zaprojektować odwracalną regulację objętości i dostęp serwisowy. Nie uzależniać budowy od zakupu aparatury lub pomiaru free-air.
2. **Podczas budowy:** dokumentować geometrię, objętość netto, uszczelnienia, wzmocnienia, połączenia i zmiany. Pasywne kontrole posiadanym multimetrem są możliwe po odłączeniu zasilania i potwierdzeniu rozładowania układu; nie stanowią walidacji akustycznej.
3. **Po zakończeniu budowy:** wrócić do decyzji o sposobie realizacji pomiarów. Dopiero wtedy ustalić dostępny tor, jego kalibrację i zakres wiarygodnych wyników. Poniższe procedury akustyczne oraz identyfikacja T/S są planem na ten etap.
4. **Po pomiarach bazowych:** porównywać iteracje skrzyni, następnie stroić system w pokoju pod jeden sweet spot. Zmiany DSP muszą być odtwarzalne.

Można rozpocząć budowę przy otwartych niewiadomych metrologicznych, jeśli ryzyka konstrukcyjne są opisane. Brak pomiaru oznacza otwartą ocenę osiągów, a nie domyślne spełnienie lub niespełnienie wymagań. Jeżeli bezpieczne uruchomienie elektroniki wymaga kompetencji lub wyposażenia, których brak, odraczamy tę czynność; nie przenosimy tego ograniczenia na budowę pasywnej skrzyni.

## 2. Co dokładnie wolno wnioskować

Rozdzielamy trzy warstwy danych:

| Warstwa | Przykładowe dane | Uprawniony wniosek | Ograniczenie |
| --- | --- | --- | --- |
| Źródła i model przed budową | Katalogowe T/S, tolerancje, model objętości, wychylenia i napięcia | Prognoza zależna od założeń | Nie jest pomiarem zakupionego egzemplarza |
| Diagnostyka prototypu w pokoju | Impedancja, pomiar nearfield, porównanie skrzyń, temperatura | Zachowanie konkretnego egzemplarza w opisanej konfiguracji | Nearfield nie daje automatycznie absolutnego SPL w odległości odniesienia ani pełnej charakterystyki w wolnym polu |
| System w pokoju | SPL, szum, integracja i kompresja w sweet spocie | Wynik in-room dla podanej pozycji, ustawień i stanu cieplnego | Nie jest walidacją wolnego pola ani dowodem osiągów w innym pokoju |

Każda liczba otrzymuje rodzaj źródła: `dane producenta`, `pomiar własny`, `pomiar niezależny`, `symulacja`, `obliczenie przybliżone` lub `założenie`. Powtórzenie własnego pomiaru nie czyni go pomiarem niezależnym. Wniosek obliczony z pomiarów zachowuje odsyłacze do wszystkich wejść.

Oddzielamy **warunki wykonania**, **granice bezpieczeństwa** i **progi jakości**. Poziom początkowy, odstęp między próbami lub liczba powtórzeń opisują protokół. Nie są zatwierdzonymi progami jakości subwoofera. Limit przerwania testu może wynikać z potwierdzonych ograniczeń sprzętu, nawet gdy specyfikacja odbiorowa nie została jeszcze zatwierdzona.

## 3. Karta wymagania i status decyzji

Przed oceną danej cechy zapisać: identyfikator wymagania, wielkość, jednostkę, pasmo, pozycję, sygnał, czas, kryterium ograniczenia, źródło progu, status zatwierdzenia i regułę uwzględnienia niepewności. Wartość bez tych warunków nie wystarcza do odbioru.

| Cecha do określenia | Dane, które należy zebrać po budowie | Próg odbiorowy na obecnym etapie |
| --- | --- | --- |
| Użyteczne 20–40 Hz | Poziom podstawowej, harmoniczne, kompresja, napięcie jeżeli mierzalne, stan termiczny | Do zaproponowania i zatwierdzenia; bez liczby domyślnej |
| SPL szczytowy | Rzeczywisty peak, sygnał, pasmo, czas i pozycja in-room | Do zatwierdzenia |
| SPL długotrwały | RMS/poziom równoważny, dokładny czas, widmo i crest factor | Do zatwierdzenia |
| THD i kompresja | Krzywe względem częstotliwości i poziomu, granice pomiaru | Do zatwierdzenia |
| Szum | Tło, stany elektroniki, widmo, poziomy ważone i nieważone | Do zatwierdzenia |
| Integracja | Odpowiedzi sekcji, wspólna referencja czasowa, zmierzona suma | Do zatwierdzenia |
| Powtarzalność | Powtórzenia bez zmian i po ponownym ustawieniu mikrofonu | Do zatwierdzenia |

Nieznane warunki referencji ADAM Audio wpisujemy jako braki. Bez zgodności warunków nie ogłaszamy parytetu. Pomiary prototypu w pokoju pozostaną in-room także wtedy, gdy katalog referencji zawiera dane wolnego pola. Nie przeliczamy ich mechanicznie na pozornie wspólną bazę.

Statusy stosowane w raporcie: `ZMIERZONE`, `OBLICZONE`, `NIEZMIERZONE`, `POZA_ZAKRESEM_METODY`, `NIEWAŻNE`. Ocenę wymagania zapisujemy osobno: `SPEŁNIONE`, `NIESPEŁNIONE`, `NIEROZSTRZYGNIĘTE` lub `NIE_DOTYCZY`. Bez zatwierdzonego progu ocena brzmi `NIEROZSTRZYGNIĘTE`, nawet gdy dane wyglądają korzystnie.

## 4. Przed budową: katalogowe T/S i niepewność modelu

Dla każdego kandydata zachować dokument źródłowy, wersję, datę pozyskania i tabelę parametrów z jednostkami. Zanotować, czy wartości są typowe, gwarantowane, dotyczą pojedynczego egzemplarza, jakiej temperatury i jakiej procedury. Nie łączyć T/S z różnych rewizji przetwornika w jeden rzekomo spójny zestaw.

Minimalny zestaw do modelu zamkniętego obejmuje `Fs`, `Qes`, `Qms`, `Qts`, `Vas`, `Re`, `Sd`; zależnie od modelu także `Le`, `Mms`, `Cms`, `BL`, definicję `Xmax`, ograniczenia mechaniczne i termiczne. Brak parametru pozostaje brakiem. `Re` nie jest impedancją nominalną, `Xmax` nie jest `Xmech`, a moc katalogowa nie wyznacza samodzielnie bezpiecznego napięcia przy każdej częstotliwości.

Procedura przed budową:

1. Sprawdzić zgodność jednostek i podstawową zależność `1/Qts = 1/Qes + 1/Qms`; rozbieżność wyjaśnić zamiast ręcznie dopasowywać wartości bez śladu.
2. Wprowadzić udokumentowane tolerancje. Gdy ich nie podano, zapisać `tolerancja nieznana`. Zgodność kart katalogowych nie dowodzi małego rozrzutu produkcyjnego.
3. Obok modelu nominalnego wykonać analizę wrażliwości na T/S i objętość. Zakresy bez danych producenta oznaczyć jako **scenariusze inżynierskie**, podać ich uzasadnienie i nie nazywać tolerancją egzemplarzy ani przedziałem ufności.
4. Zachować zależności między parametrami. Nie zmieniać niezależnie wszystkich T/S tak, by powstał fizycznie niespójny zestaw. Monte Carlo wymaga uzasadnionych rozkładów i korelacji; brak tych danych przemawia za jawnymi scenariuszami, nie za fikcyjną statystyką.
5. Porównać odpowiedź, potrzebny EQ, napięcie i przewidywane wychylenie dla kilku odwracalnych objętości. Wszystkie krzywe opisać jako modelowe.
6. Wypisać, które decyzje są odporne na niepewność, a które sprawdzi późniejszy pomiar. Nie wymagać teraz pomiaru free-air ani zakupu miernika impedancji.

Objętość geometryczna netto to wewnętrzna objętość po odjęciu rzeczywistych wyporów przetwornika, wzmocnień, wkładów i innych elementów. Wypełnienie opisujemy oddzielnie: rodzaj, masa, ułożenie. Nie przeliczamy jego objętości na arbitralny stały procent „dodatkowych litrów akustycznych”.

## 5. Po budowie: sesja, geometria i kontrola toru

Po ukończeniu prototypu ustalić, które pomiary można wykonać wiarygodnie. Nie jest to obecnie dobór toru ani lista zakupów. Funkcjonalne wymagania konkretnego testu obejmują odpowiedni zakres częstotliwości, brak przesterowania, znaną kalibrację oraz zgodną z badaną wielkością synchronizację. Niespełnione wymaganie ogranicza ten test.

Przed każdą późniejszą sesją:

1. Nadać identyfikator sesji i konfiguracji. Zapisać przetwornik, skrzynię, jej objętość netto, wkłady, uszczelnienie, wypełnienie, wzmacniacz, routing i preset DSP. Zdjęcia muszą pokazywać pozycje i orientację.
2. Zdefiniować początek układu współrzędnych pokoju i jednostki. Zapisać pozycję środka membrany, kapsuły mikrofonu, sweet spotu, kierunki osi oraz położenie drzwi i istotnych mebli. Odległość mierzyć od jawnie określonego punktu źródła, nie przypadkowej krawędzi skrzyni.
3. Zanotować temperaturę, a jeśli dostępne także wilgotność, stan wentylacji i źródła hałasu. Zapisać czas od ostatniej głośnej próby. Dla porównań przyjąć jawne kryterium powrotu do stanu odniesienia.
4. Zapisać częstotliwość próbkowania, długość sygnału, okna analizy, ważenie, wygładzanie, zakres i poziomy. Wyłączyć automatyczną regulację wzmocnienia i niezamierzone ulepszacze dźwięku; zanotować, czego nie można wyłączyć.
5. Jeżeli wybrany później mikrofon ma plik kalibracji, zachować plik przypisany do egzemplarza i orientacji. Kalibracja odpowiedzi częstotliwościowej i kalibracja czułości absolutnej to różne informacje. Bez wiarygodnego przeliczenia na paskale nie raportować skalibrowanego SPL.
6. Sprawdzić cały łańcuch poziomów: generator, system operacyjny, wejście DSP, filtry/EQ, wyjście DSP, wzmacniacz i rejestrację. Zapis `dBFS` nie zastępuje napięcia na głośniku ani SPL.
7. Wykonać pomiar tła i powtórzenia małosygnałowe. Praktyczna propozycja protokołu to trzy powtórzenia bez zmiany konfiguracji; liczba ta służy ocenie rozrzutu, nie jest normą odbiorową.

Plik kalibracji, aplikacja i jej ustawienia nie nadają automatycznie całemu stanowisku potwierdzonej niepewności. Oddzielić rozrzut powtórzeń od błędu czułości, geometrii, tła, zegarów i obróbki.

## 6. T/S i impedancja — późniejsza procedura opcjonalna

Ta sekcja opisuje metodę do rozważenia **po budowie**. Przed budową wystarczają dane katalogowe i analiza wrażliwości. Pomiar T/S ani demontaż przetwornika do free-air nie są obowiązkowym krokiem projektu.

### 6.1. Co daje multimetr, a czego nie daje

Na odłączonym i rozładowanym układzie można zmierzyć rezystancję DC przetwornika, sprawdzić ciągłość przewodów oraz niepożądane zwarcia. Zanotować rezystancję przewodów i styków; przy małych oporach może istotnie zmieniać wynik. Stosować funkcję kompensacji lub udokumentowaną poprawkę, jeśli przyrząd i metoda na to pozwalają.

Multimetr nie wyznacza samodzielnie zespolonej impedancji, `Fs`, `Qts` ani `Vas`. Jego pomiar napięcia AC wymaga znajomości pasma, zakresu i zachowania dla danego przebiegu. Sam napis „true RMS” nie dowodzi poprawności pomiaru wyjścia klasy D.

### 6.2. Zespolona impedancja

Jeżeli później dostępna metoda ma odpowiednią kalibrację, mierzyć przy małym sygnale w zakresie obejmującym rezonans i obie jego strony. Rejestrować napięcie i prąd albo równoważne dwa napięcia **jednocześnie, ze wspólnym zegarem próbkowania**. W prostym niskonapięciowym układzie z rezystorem szeregowym:

`Z(f) = R_ref × V_DUT(f) / [V_source(f) − V_DUT(f)]`

To iloraz wielkości zespolonych. Wzór zakłada właściwą topologię z uzgodnionym punktem odniesienia, znany rezystor oraz skalibrowaną różnicę amplitudy i fazy kanałów. Nie jest instrukcją podłączenia mas interfejsu lub oscyloskopu do mostkowego wzmacniacza. UMIK nie jest wejściem do pomiaru napięć elektrycznych.

Procedura:

1. Udokumentować schemat, rezystor odniesienia, przewody i zakresy. Kalibrację otwarcia, zwarcia i obciążenia wykonywać tylko według procedury danego bezpiecznego układu pomiarowego; nigdy nie zwierać wyjścia wzmacniacza mocy w celu „kalibracji”.
2. Sprawdzić tor na znanym obciążeniu kontrolnym, w wymaganym paśmie, z zachowaniem ograniczeń mocy i temperatury.
3. Wykonać kilka przebiegów przy małym poziomie i porównać wynik po niewielkiej zmianie pobudzenia. Jeżeli rezonans lub dobroć zależą od poziomu, nie podawać jednej wartości bez wskazania amplitudy i historii termicznej.
4. Zachować surowe kanały, moduł i fazę impedancji, temperaturę, orientację przetwornika oraz dopasowanie modelu z resztami. Sam zrzut ekranu z tabelą T/S jest niewystarczający.
5. Dla głośnika zamontowanego w skrzyni dopasować parametry układu w obudowie. Zmienione rezonans i dobroć nie są automatycznie free-air `Fs` i `Qts` przetwornika.

### 6.3. Opcjonalna identyfikacja parametrów przetwornika

Jeżeli po budowie będzie uzasadnione bezpieczne wyjęcie głośnika, pomiar bez obudowy można rozważyć w tym samym pokoju. Określenie free-air dotyczy tu swobodnego przetwornika, **nie wolnego pola akustycznego pokoju**. Stabilne mocowanie, orientacja, odstęp od przeszkód i powtarzalność są częścią metody. Wynik obciążony wpływem otoczenia wymaga zastrzeżenia. Nie wykonywać dużych wychyleń bez obudowy jako testu wydajności.

Z dopasowania małosygnałowej impedancji można oszacować `Fs`, `Qes`, `Qms`, `Qts` i `Re`, jeśli model oraz jakość danych to uzasadniają. Sam przebieg impedancji bez dodatkowej informacji nie wyznacza jednoznacznie wszystkich parametrów mechanicznych i `Vas`. `Le` trzeba opisać częstotliwością i modelem; pojedyncza liczba nie opisuje pełnej zależności od częstotliwości.

Możliwe rozszerzenia, wyłącznie przy uzasadnieniu po budowie:

- **Masa dodana:** zważyć rzeczywistą masę dodatkową wraz z mocowaniem; rozmieścić ją symetrycznie i bez uszkadzania membrany. Rezonans musi przesunąć się na tyle, by różnica była rozstrzygalna, a model nadal miał sens. Dla modelu skupionego `Mms = Δm / [(Fs/Fm)^2 − 1]`, gdzie `Fm` jest rezonansem z masą. Następnie `Cms = 1 / [(2πFs)^2 Mms]` i `Vas = ρ c² Sd² Cms`. Jednostki SI; `Sd` to powierzchnia efektywna, nie powierzchnia zewnętrznego obrysu kosza. Niepewność `Sd`, mocowania, masy i rezonansu przenosi się do wyniku.
- **Znana szczelna objętość:** w idealnym modelu `Vas = Vb × [(Fc/Fs)^2 − 1]`. Wymaga znanego niezależnie `Fs`, prawidłowej objętości netto, szczelności oraz rozpoznanych strat. Użycie katalogowego `Fs` daje wynik warunkowy, nie pełny pomiar T/S danego egzemplarza. Wypełnienie i podatność ścian mogą zaburzać prosty model.

Jeśli warunki nie pozwalają na wiarygodną identyfikację, pozostawić T/S jako katalogowe. Nadal można mierzyć porównawczo impedancję układu, zmiany rezonansu i skutki iteracji skrzyni. Nie wyprowadzać `Xmax`, maksymalnego SPL ani THD z samego małosygnałowego dopasowania T/S.

## 7. Nearfield w pokoju i granice ground-plane

### 7.1. Nearfield — możliwa diagnostyka po budowie

Pomiar blisko membrany zwiększa udział promieniowania bezpośredniego względem tła pokoju. Może pomóc porównywać niski zakres pasma, nieszczelności i iteracje skrzyni. Nie usuwa automatycznie wpływu pomieszczenia, geometrii membrany i nieliniowości toru.

Procedura:

1. Unieruchomić mikrofon względem przetwornika. Zapisać pozycję kapsuły i jej odległość od wskazanej części membrany w spoczynku, orientację oraz fotografię. Zostawić zapas względem możliwego wychylenia; próby blisko membrany zaczynać od małego sygnału.
2. Zmierzyć tło i serię małosygnałową przy identycznym pobudzeniu. Sprawdzić powtarzalność po niewielkiej kontrolowanej zmianie odległości; jej wpływ stanowi część niepewności porównania.
3. Zestawić kilka punktów na membranie, jeżeli w analizowanym paśmie wynik zależy od miejsca. Nie zakładać z góry zakresu poprawności na podstawie jednej odległości.
4. Zachować dane bez wygładzania. Wykres prezentacyjny może być wygładzony, ale wartości charakterystyczne liczyć według zapisanej metody.
5. Używać przede wszystkim do względnych porównań przy niezmienionej geometrii. Przeliczenie na odległe pole wymaga modelu geometrii i promieniowania; nie stosować prostego prawa `1/r` między kilkoma milimetrami od membrany a sweet spotem.

Przy dużym poziomie mikrofon nearfield może przesterować się wcześniej niż w sweet spocie. Odsunięcie mikrofonu zmienia jednocześnie skalę i udział pokoju. Dlatego pomiar nearfield THD i pomiar THD w sweet spocie są odrębnymi seriami, a nie automatycznie wymiennymi danymi.

### 7.2. Ground-plane — wiedza o metodzie niedostępnej

Ground-plane wykorzystuje pomiar przy dużej powierzchni odbijającej w warunkach ograniczających inne odbicia. Wymaga odpowiedniej geometrii, powierzchni, otoczenia i opisu odległości. Sama kapsuła położona na podłodze pokoju nie usuwa ścian, sufitu ani modów.

Zgodnie z U-003 **nie planujemy wykonania ground-plane, pomiarów na zewnątrz ani zastępowania nimi pomiarów w pokoju**. Brak tej metody oznacza ograniczenie zakresu porównania z urządzeniami mierzonymi w innych warunkach. Nie blokuje rozpoczęcia budowy ani dalszych badań in-room. Wyniku przy podłodze w pokoju nie podpisujemy jako pomiaru referencyjnej półprzestrzeni.

Krótkie bramkowanie odpowiedzi impulsowej nie odtwarza wiarygodnie dowolnie niskich częstotliwości. Zależność skali rozdzielczości od długości okna jest rzędu `Δf ≈ 1/T`; nie jest gwarancją usunięcia wszystkich odbić. Nie sklejać nearfield z pomiarem w pokoju jako „wolnego pola”, jeżeli brak niezależnie uzasadnionego obszaru zgodności i modelu przejścia.

## 8. SPL: definicje i komplet warunków

Dla skalibrowanego ciśnienia akustycznego, przy `p0 = 20 µPa`:

- `L_RMS = 20 log10(p_RMS/p0)` — RMS w podanym przedziale czasu i paśmie;
- `L_peak = 20 log10(max(|p(t)|)/p0)` — rzeczywisty szczyt w podanym przedziale, po jawnie określonym filtrowaniu;
- `crest factor = 20 log10(p_peak/p_RMS)` — dla tego samego przebiegu, okna i pasma.

Dla nieobciętej sinusoidy w stanie ustalonym peak jest około 3,01 dB powyżej RMS. Nie stosować tej różnicy automatycznie do burstów, szumu, muzyki ani katalogowego „max SPL”. Nie utożsamiać detektora Fast/Slow, wartości RMS FFT, poziomu równoważnego i rzeczywistego peak.

Każdemu wynikowi SPL muszą towarzyszyć:

| Grupa | Wymagane informacje |
| --- | --- |
| Źródło i geometria | Jeden/dwa subwoofery, pozycje, odległość, wysokość, orientacja, pokój i stan wyposażenia |
| Sygnał | Plik lub definicja generatora, częstotliwości/pasmo, obwiednia, czas, liczba powtórzeń, odstępy i crest factor |
| Definicja wyniku | Peak/RMS/poziom równoważny, pasmo, ważenie, długość integracji, uwzględnienie harmonicznych |
| Tor i konfiguracja | Kalibracja, zakres rejestracji, gain staging, filtry ochronne, EQ, limiter i ewentualna redukcja wzmocnienia |
| Stan | Temperatura, historia pobudzenia, tło, ważność i niepewność |
| Ograniczenie | THD/harmoniczne, kompresja, limiter, clipping, termika, wychylenie, hałas lub zakres pomiaru |

**Podstawową etykietą wyniku jest `in-room` z identyfikatorem punktu.** Maksimum podstawowej sinusoidy oraz całkowity poziom obejmujący harmoniczne mogą mieć różne wartości. Do charakterystyki wydajności subwoofera nie podnosić wyniku przez doliczanie zniekształceń bez wyjaśnienia.

Zależność `L(r2) = L(r1) − 20 log10(r2/r1)` jest modelem odpowiedniego pola swobodnego i tego samego źródła w zakresie jego stosowalności. Nie służy do przenoszenia pomiaru między punktami tego pokoju, między nearfield i sweet spotem ani między pokojem i kartą katalogową. Nie stosować automatycznej poprawki stałej liczby dB między wolnym polem, podłogą pokoju i jego narożnikiem.

## 9. Po budowie: THD, kompresja i wydajność in-room

### 9.1. Seria poziomów

Najpierw ustalić bezpieczny obszar pracy z modelu, danych przetwornika i elektroniki. Potem przygotować serię od małego poziomu, z obserwacją toru, temperatury oraz zachowania mechanicznego. Praktyczna propozycja to kroki rzędu 1–2 dB blisko ograniczenia; to rozdzielczość eksperymentu, nie norma ani wymagany zapas.

W pokoju zaplanować ochronę słuchu, odsunięcie osób postronnych i łatwo dostępne wyciszenie. Nie prowadzić odsłuchu w sweet spocie podczas prób granicznych; obecność słuchacza nie jest potrzebna do rejestracji SPL.

1. Zmierzyć serię odniesienia przy małym sygnale w sweet spocie. Zdefiniować jawnie częstotliwości; przykładowa siatka planu obejmuje 20, 25, 31,5 i 40 Hz oraz punkty w dalszym paśmie pracy. Nie oznacza to, że prototyp musi osiągnąć określony poziom w każdym z tych punktów.
2. Dla każdej częstotliwości lub przebiegu zachować pełny opis czasu i obwiedni. Krótkie pobudzenie i długie grzanie są odrębnymi testami; jeden nie zastępuje drugiego.
3. Podnosić poziom tylko przy ważnych danych i braku przesłanek przerwania. Zapisywać poziom zadany, rzeczywiste napięcie jeśli wiarygodnie mierzone, poziom podstawowej, harmoniczne, temperaturę i stan ograniczników.
4. Wracać do małosygnałowego punktu kontrolnego między seriami. Jego dryft może wskazywać nagrzanie, zmianę ustawienia lub problem z torem.
5. Po wystudzeniu powtórzyć wybrane punkty. Zatrzymać się po zebraniu danych rozstrzygających pytanie; nie dążyć do awarii jako sposobu znalezienia maksimum.

Przerwać przy niepokojących odgłosach mechanicznych, podejrzeniu nadmiernego wychylenia, przegrzewaniu, zapachu, zadziałaniu zabezpieczeń, clippingu toru lub utracie wiarygodności rejestracji. Takie zdarzenie dokumentuje się bez wymuszania kolejnej próby. Bez pomiaru wychylenia nie raportować „Xmax nieprzekroczone” jako faktu; model i obserwacja odsłuchowa mają inny status dowodowy.

### 9.2. THD i harmoniczne

Dla amplitud RMS składowych z tego samego pomiaru:

`THD = sqrt(p2² + p3² + ... + pN²) / p1`

W procentach mnożymy przez 100. Zapisać `N`, pasmo rejestracji, metodę ekstrakcji, okno i sposób oddzielenia harmonicznych od szumu. THD+N jest inną wielkością. Jeśli wyższe harmoniczne wypadają poza wiarygodnym pasmem, wynik opisuje tylko uwzględnione składowe.

Oprócz THD przechowywać co najmniej poziom podstawowej i dostępnych harmonicznych osobno, zarówno względnie, jak i absolutnie, jeżeli kalibracja pozwala. W pokoju różne częstotliwości są wzmacniane lub tłumione inaczej. Dół odpowiedzi przy podstawowej może zawyżać iloraz THD; lokalne minimum przy harmonicznej może go zaniżać. Wynik z sweet spotu opisuje tor wraz z propagacją w pokoju, nie izolowaną nieliniowość głośnika.

### 9.3. Kompresja

Dla niezmienionej konfiguracji i wzrostu rzeczywistego pobudzenia o `ΔL_in`:

`C(f) = ΔL_in − [L_high(f) − L_ref(f)]`

Dodatnie `C` oznacza mniejszy przyrost wyjścia niż oczekiwany. Jeżeli `ΔL_in` obliczono z napięcia na zaciskach, użyć `20 log10(V_high/V_ref)` z porównywalnych okien i pasma. Jeżeli dostępny jest tylko krok cyfrowy, nazwać wynik **kompresją całego toru względem poziomu zadanego**. Nie przypisywać jej wyłącznie cewce.

Raportować krzywe nieznormalizowane i znormalizowane do tej samej wartości pobudzenia. Negatywna niewielka „kompresja” może być skutkiem rozrzutu; nie interpretować jej automatycznie jako korzystnej ekspansji. Zadziałanie limitera, ograniczenie zasilania i nagrzanie przetwornika rozpatrywać osobno, o ile są dostępne dane rozróżniające.

### 9.4. Granice pomiaru i zapis maksimum

- Brak clippingu cyfrowego nie dowodzi braku przesterowania analogowej części mikrofonu, wzmacniacza ani wejścia rejestrującego.
- Zniekształcenia mikrofonu lub elektroniki mogą ograniczyć wynik. Niezależna zmiana poziomu i geometrii może pomóc w diagnostyce, ale sama nie identyfikuje źródła zniekształceń.
- Harmoniczna na poziomie szumu nie ma wiarygodnej dokładnej wartości procentowej. Zapisać `nierozstrzygalna przy tym tle`; górną granicę podawać tylko z uzasadnioną metodą jej obliczenia.
- Porównanie głośnego pomiaru z cichym wymaga wystarczającego SNR obu przebiegów. Nie odejmować w dB tła od sygnału.
- Maksimum z kilku punktów częstotliwości nie dowodzi minimum osiągów w całym ciągłym paśmie. Zachować siatkę i nie interpolować przez niewiadome ograniczenia.

Jeżeli seria kończy się bez osiągnięcia ograniczenia, raport brzmi „najwyższy zbadany poziom in-room”, z powodem zakończenia. Dolną granicę maksymalnego **użytecznego** SPL można podać tylko wtedy, gdy ten punkt spełnia wszystkie wcześniej zatwierdzone warunki użyteczności. Gdy progów brak, nie nadawać mu tej kwalifikacji.

## 10. Szum własny i tło pokoju

Po budowie planować osobną serię przy niezmienionej pozycji i ustawieniach mikrofonu. Zachować surowe nagrania z jednakowym czasem, pasmem i gainem. Rozpatrzyć następujące stany, o ile ich przełączanie jest bezpieczne:

1. Tło pokoju przy wyłączonym badanym systemie; zapisać inne urządzenia i instalacje.
2. System w docelowej konfiguracji, bez odtwarzania, z wejściami podłączonymi tak jak podczas użytkowania.
3. Udokumentowane wyciszenie sygnału w DSP. Cyfrowa cisza nie musi wyłączać przetwornika D/A ani wzmacniacza.
4. Osobne sekcje lub alternatywne, przewidziane przez producenta stany wejść, jeżeli pomagają zlokalizować problem. Nie zwierać nieznanych wyjść ani nie pozostawiać nieopisanych wejść jako rzekomego odpowiednika stanu użytkowego.

Raportować widmo, składowe tonalne i całkowity poziom w zadanym paśmie. Dla subwoofera wynik nieważony/pasmowy jest istotny obok ewentualnego dBA; ważenie A może silnie ograniczyć udział niskiego basu. Zapisać ważenie i nie traktować pojedynczej liczby dBA jako pełnej oceny ciszy.

Jeżeli sygnał z włączonym systemem i tło są zbyt podobne względem niepewności oraz zmienności, wkład systemu jest nierozstrzygnięty. Dla nieskorelowanych, stacjonarnych składników można rozważyć odejmowanie energii `p_system² = p_on² − p_background²`, z propagacją niepewności. Wynik ujemny lub niestabilny nie oznacza „ujemnego szumu” ani braku szumu. Wspólne tony i zmienne tło mogą unieważnić takie odejmowanie.

Oddzielić szum akustyczny głośnika, brum/pisk elektroniki, wentylator i szum własny rejestracji. Pomiary elektryczne szumu na wyjściu wzmacniacza podlegają ograniczeniom z sekcji 12; mikrofon nie mierzy bezpośrednio szumu napięciowego.

Test odsłuchowy „czarnego tła” przeprowadzać z docelowej pozycji i przy zapisanym ustawieniu głośności. Zanotować warunki, osobę i obserwację. Jeżeli możliwe, porównać losowo oznaczone, bezpiecznie przełączane stany bez widocznej wskazówki dla słuchacza. Brak zgłoszonej słyszalności w tym teście nie ustanawia uniwersalnego progu słyszenia.

## 11. Faza i timing przy mikrofonie USB z osobnym zegarem

Ta procedura dotyczy sytuacji, gdy **po budowie** zostanie wybrany np. UMIK. Nie jest rekomendacją zakupu. Mikrofon USB i urządzenie odtwarzające mają zwykle niezależne zegary; nominalnie jednakowa częstotliwość próbkowania nie zapewnia ich synchronizacji. Zmienna latencja i dryft mogą zaburzać porównanie fazy, opóźnienia i sumowania z oddzielnych przebiegów.

Plan pomiaru:

1. Ustalić wspólną referencję czasową dla wszystkich porównywanych sekcji. Dla dostępnego oprogramowania sprawdzić możliwość akustycznego sygnału referencyjnego od stałego źródła, jego wymagania i obsługę różnicy zegarów. Nie zakładać działania kompensacji bez weryfikacji w użytej wersji i konfiguracji.
2. Źródło referencyjne, mikrofon, routing i odległości muszą pozostać stałe. Subwoofer o ograniczonym paśmie może nie nadawać się do odtworzenia sygnału referencyjnego; brak odpowiedniej referencji oznacza otwarte pomiary czasu, nie powód zakupu sprzętu przed budową.
3. Powtórzyć tę samą sekcję przed i po serii. Sprawdzić stabilność położenia impulsu i fazy. Porównać również przebiegi o różnym czasie trwania, jeżeli podejrzewany jest dryft.
4. Zachować oryginalne impulsy, offset referencji i wszystkie operacje przesuwania/resamplingu. Nie wyrównywać każdego pomiaru osobno do własnego szczytu: usunęłoby to opóźnienia, które miały być zmierzone.
5. Sekcje mierzyć osobno z zachowaniem tej samej referencji, potem rzeczywiście razem. Suma przewidywana z zespolonych odpowiedzi ma sens dopiero po potwierdzeniu wspólnego czasu i skalowania. Zweryfikować ją pomiarem łącznym w tej samej pozycji.
6. Jeśli nie można potwierdzić czasu, raportować krzywe amplitudy i bezpośredni wynik wspólnego odtwarzania; opóźnienie i fazę między niezależnymi przebiegami oznaczyć jako nierozstrzygnięte.

Zmiana polaryzacji to odwrócenie znaku. Opóźnienie wprowadza zależne od częstotliwości przesunięcie fazy; nie zastępować go uniwersalnym przełącznikiem „180°”. Wybierać ustawienie na podstawie zakresu podziału, pomiaru sumy i wrażliwości wokół sweet spotu. Głęboki null przy przeciwnej polaryzacji może być diagnostyczny, ale nie dowodzi poprawnej integracji w całym paśmie.

W pokoju faza, opóźnienie grupowe i zanik zawierają wpływ odbić. Rozwijanie fazy oraz obliczanie pochodnych w dołkach o małym SNR może dawać pozorne duże opóźnienia. Nie usuwać tych punktów bez zapisania maski ważności i nie utożsamiać czasu maksimum niskotonowego impulsu z jednoznacznym czasem przelotu.

## 12. Napięcie wzmacniacza mostkowego i posiadane przyrządy

Użytkownik ma multimetr i oscyloskop; ich model, sposób uziemienia, zakresy oraz wyposażenie sondowe nie są tu potwierdzone. Nie dobieramy ani nie kupujemy toru. Pomiar wolno wykonać istniejącą aparaturą **tylko po wykazaniu jej przydatności do konkretnego podłączenia**.

Wyjście BTL/mostkowe ma dwa aktywne zaciski. Żaden z nich nie musi być masą. Zaciski klasy D mogą dodatkowo przenosić sygnał przełączający i znaczne napięcie wspólne.

- **Nie podłączać masy zwykłej, uziemionej sondy oscyloskopowej do żadnego zacisku głośnikowego mostka.** Może to zewrzeć aktywne wyjście przez przewód ochronny. Dwa takie kanały i odejmowanie matematyczne nie zapewniają izolacji.
- Nie odłączać przewodu ochronnego oscyloskopu i nie „unosić” jego obudowy. Samo zasilanie bateryjne lub wejście opisane jako zbalansowane nie dowodzi wymaganej izolacji.
- Pomiar między zaciskami wymaga potwierdzonej odpowiedniej sondy różnicowej albo rzeczywiście izolowanego systemu pomiarowego. Należy sprawdzić napięcie różnicowe i wspólne, pasmo, dopuszczalne przebiegi przełączające, tłumienie, izolację oraz sposób odniesienia zgodnie z dokumentacją aparatury i wzmacniacza. Nie wystarcza sam napis „differential”.
- Multimetr może być użyty między zaciskami tylko po potwierdzeniu jego dopuszczalnych napięć, izolacji, pasma, crest factor i odporności na składowe przełączające. True RMS nie gwarantuje poprawnego wyniku audio na surowym wyjściu klasy D. Nie łączyć nieznanego wyjścia z masą przez USB, komputer lub inne urządzenie.
- Nie podłączać wyjścia mocy bezpośrednio do wejścia liniowego interfejsu. Tłumienie, filtracja i izolacja wymagają zweryfikowanej konstrukcji; ten dokument nie projektuje takiego adaptera.

Jeżeli odpowiedniej aparatury nie ma lub jej parametrów nie potwierdzono, wpisać `napięcie wyjściowe niezmierzone` i odroczyć test. To nie blokuje budowy skrzyni. Kontrole rezystancji i ciągłości wykonywać bez zasilania; podłączenia pomiarowe przy wyjściu mocy przygotowywać po bezpiecznym wyłączeniu i rozładowaniu, zgodnie z dokumentacją układu.

Podczas dozwolonego pomiaru zapisać punkty przyłączenia, model przyrządu i sondy, zakresy, filtrowanie, czas analizy oraz obciążenie. Oddzielać napięcie audio od tętnień/przełączania. `P = V_RMS²/R` opisuje moc w znanym rezystancyjnym obciążeniu w danych warunkach. Dla głośnika o zespolonej impedancji rzeczywista moc wymaga poprawnego pomiaru napięcia i prądu, ich fazy lub średniej `v(t)i(t)`. Nie podstawiać automatycznie impedancji nominalnej do wzoru na moc.

## 13. Iteracje zamkniętej skrzyni

Każda iteracja otrzymuje osobny identyfikator konfiguracji. Dokumentować wymiary wewnętrzne, wypory i objętość netto, wkłady, wzmocnienia, uszczelki, sposób dokręcenia i osłonę. Nie zmieniać jednocześnie objętości, masy wypełnienia, pozycji w pokoju i EQ, jeśli pytanie dotyczy samej objętości.

Po budowie stosować sekwencję:

1. Zarejestrować stan A: mały sygnał, temperatura, nearfield i sweet spot, a także impedancja, jeśli jej pomiar jest dostępny. Korekcję pokoju pozostawić wyłączoną; konieczne filtry ochronne pozostają jawnie zapisane.
2. Wprowadzić jedną odwracalną zmianę. Wkłady redukujące objętość muszą być sztywne, stabilnie zamocowane i nie blokować wentylacji głośnika. Objętości pustych lub nieszczelnych elementów nie traktować bez uzasadnienia jak pełnego wyporu.
3. Po ustabilizowaniu temperatury wykonać te same pomiary przy tym samym pobudzeniu. Zmiana położenia membrany lub mikrofonu wymaga zapisania nowej geometrii.
4. Wrócić do A. Układ A–B–A pomaga ujawnić dryft temperatury, montażu i toru. Jeśli drugi A odbiega od pierwszego, nie przypisywać całej różnicy wariantowi B.
5. Porównać modele z danymi, w tym reszty dopasowania. Zmiana rezonansu może wynikać z objętości, nieszczelności, strat, temperatury lub podatności ścian. Sam pojedynczy pik impedancji nie rozstrzyga wszystkich tych przyczyn.

Rozdzielić dwa pytania: (a) jak skrzynia zachowuje się przy stałym napięciu/pobudzeniu bez korekcji pokoju, (b) ile kosztuje uzyskanie tej samej odpowiedzi docelowej po korekcji. Dla (b) porównać zapotrzebowanie na napięcie, ograniczniki, kompresję i przewidywane wychylenie. Nie wyrównywać wykresów dowolnym EQ bez ujawnienia kosztu headroomu.

Nieszczelności, drgania paneli i odgłosy osłony dokumentować osobno: pozycja, częstotliwość, poziom i metoda obserwacji. Subiektywnie słyszalny problem jest sygnałem diagnostycznym, nie pomiarem jego amplitudy. Nie nazywać skrzyni „idealnie szczelną” na podstawie samego braku słyszalnego syku.

## 14. Temperatura i długotrwałe obciążenie

Test krótkiego headroomu zaczynać z opisanego stanu odniesienia. Test termiczny jest osobną serią z określonym widmem, czasem, crest factor, przerwami oraz warunkami wentylacji. Muzyka, sinus i szum pasmowy grzeją układ inaczej; wyników nie utożsamiać.

Zapis planowanej serii po budowie powinien obejmować temperaturę otoczenia, dostępne temperatury obudowy/elektroniki, czas pracy, poziom zadany, ewentualnie napięcie audio, zmiany odpowiedzi i wskazania zabezpieczeń. Temperatura radiatora, magnesu lub panelu nie jest bezpośrednim pomiarem temperatury cewki.

Jeżeli można bezpiecznie zmierzyć rezystancję uzwojenia w stanie zimnym i po próbie, można oszacować średnią zmianę temperatury:

`T_hot − T_cold ≈ (R_hot/R_cold − 1)/α`

Wymaga to znanego materiału i odpowiedniego współczynnika `α`, porównywalnych styków oraz uwzględnienia rezystancji przewodów i chłodzenia przed odczytem. Nie przyjmować materiału cewki bez źródła. Wynik jest estymacją średniej temperatury uzwojenia w granicach modelu, a nie pomiarem gorącego punktu. Nie przełączać miernika rezystancji na zasilanym wyjściu wzmacniacza.

Nie narzucamy niezweryfikowanej uniwersalnej temperatury granicznej ani czasu chłodzenia. Granice wynikają z danych konkretnej konstrukcji, a powrót do stanu odniesienia weryfikujemy dostępną temperaturą, rezystancją i powtórzeniem małosygnałowym. Jeśli stabilizacja jest niepotwierdzona, porównanie termiczne pozostaje warunkowe.

## 15. Sweet spot i późniejsza integracja systemu

Główny punkt oceny to jedna pozycja głowy w odległości orientacyjnie 2,5–3 m, do potwierdzenia geometrią. Nie uśredniamy całej kanapy jako celu optymalizacji.

Po pomiarach bazowych prototypu:

1. Ustalić punkt S0 na wysokości uszu. Zapisać współrzędne oraz stan fotela/kanapy. Mikrofon nie może być przypadkowo zasłonięty oparciem.
2. Zmierzyć kilka realnych ustawień subwoofera przy monitorach i innych dopuszczalnych lokalizacjach. Nie zakładać swobody ustawienia przód–tył ani wymuszonej symetrii.
3. Najpierw zebrać odpowiedzi bez korekcji modów. Potem wybrać ustawienie i integrować poziom, polaryzację, filtry oraz opóźnienie, z ograniczeniami timingowymi z sekcji 11.
4. Jeżeli później dostępne są dwa subwoofery, mierzyć każdy osobno i oba razem. Nie zakładać zysku stałej liczby dB ani jednakowych presetów. Uwzględnić wspólne ograniczenia wzmacniaczy, DSP i zasilania.
5. Dopiero następnie wprowadzać korekcję pokoju. Nie podbijać głębokiego lokalnego dołka bez analizy jego przyczyny i kosztu w napięciu/wychyleniu. Zachować preset bazowy i wszystkie wersje pośrednie.
6. Powtórzyć pomiar S0 i wykonać punkty diagnostyczne wokół niego. Przykładowy plan to przesunięcia o 10 cm w lewo/prawo, przód/tył oraz górę/dół; jest to propozycja siatki, nie próg odbiorowy ani wymóg dla całej kanapy. Rzeczywiste przesunięcia zapisać.
7. Pokazać S0 oddzielnie od sąsiednich krzywych. Ocenić wrażliwość na drobny ruch głowy i powtarzalność ustawienia. Przypadkowa wąska poprawa w jednym punkcie wymaga jawnego komentarza.

Po zmianie EQ wrócić do pomiaru kompresji i ograniczeń przy wymaganych poziomach: płaska odpowiedź małosygnałowa nie dowodzi headroomu. Wynik w tym pokoju nie potwierdza działania produktu we wszystkich pokojach 17–20 m²; przenośnym rezultatem B+R jest również udokumentowana procedura ponownej kalibracji.

## 16. Plan plików surowych i metadanych

Poniższa struktura jest **planem przyszłego zapisu**, nie informacją o istniejących wynikach. Nie trzeba jej tworzyć przed budową. Każda sesja ma jednoznaczne ID, np. schemat `RRRRMMDD_sesjaNN`, a każda próba osobne `run_id`. Powtórzenia nie nadpisują poprzednich plików.

```text
dane_pomiarowe/
  RRRRMMDD_sesjaNN/
    README.md                  opis, status i ograniczenia sesji
    manifest.csv               ścieżka, rola, rozmiar, SHA-256, run_id
    metadata.json              aparatura, geometria, środowisko, protokół
    konfiguracje/              identyfikatory skrzyń, DSP, routing, zdjęcia
    kalibracja/                oryginalne pliki i opis ich zastosowania
    bodzce/                    pliki sygnałów lub pełna definicja generatora
    raw/                       oryginalne sesje programu, WAV, przebiegi elektryczne
    eksporty/                  CSV/TXT z jednostkami, impedancja, IR, widma
    analiza/                   kod/notatnik, wersje środowiska, parametry obróbki
    wyniki/                    tabele pochodne, wykresy, maski ważności
```

Surowe dane pozostają niezmienione. Jeśli aplikacja nie pozwala wyeksportować surowego WAV, zachować jej natywną sesję i jasno nazwać ograniczenie; nie przedstawiać CSV wygładzonej krzywej jako surowego przebiegu. Zachować również próby przerwane i nieważne, z przyczyną wykluczenia. Sumy SHA-256 pomagają wykryć zmianę pliku, ale nie dowodzą poprawności metody.

Minimalne metadane sesji:

| Obszar | Pola |
| --- | --- |
| Tożsamość | session_id, run_id, operator, czas ze strefą, ID protokołu i konfiguracji, cel |
| Źródło danych | rodzaj źródła, ścieżka do oryginału, rewizja dokumentu lub urządzenia, uwagi o brakach |
| Obiekt | egzemplarz, objętość netto i sposób jej obliczenia, wypełnienie, wariant skrzyni, historia zmian |
| Tor | przyrządy i numery egzemplarzy, sondy jeśli używane, kalibracje, zakresy, DSP, gain, Fs próbkowania |
| Pozycja | układ współrzędnych, source_id, point_id, x/y/z, orientacja, odległość i punkt jej odniesienia |
| Pobudzenie | typ, plik/hash, pasmo, poziom zadany, czas, obwiednia, crest factor, przerwy |
| Stan | temperatura i sposób odczytu, stan tła, wentylacja, czas od obciążenia |
| Analiza | okno, pasmo, ważenie, wygładzanie, liczba harmonicznych, referencja czasu, korekty |
| Ważność | clipping, SNR/tło, zakres metody, przyczyna przerwania, status brakujących pól |

Przykładowy **nagłówek** tabeli wyników pasmowych, bez przykładowych wyników:

```csv
session_id,run_id,config_id,point_id,method,f_hz,drive_dbfs,v_audio_rms,lp1_db,lp_peak_db,lp_rms_db,thd_percent,thd_harmonic_max,compression_db,temp_ambient_c,temp_method,validity,limit_reason,raw_path
```

Puste pole oznacza brak danych, nie zero. W metadanych musi istnieć powód braku, np. `nie mierzono`, `poniżej rozstrzygalności`, `poza zakresem`, `nieważne`. Jednostki i definicje kolumn są częścią schematu; `lp1_db` to poziom podstawowej, nie całkowity peak. Dla harmonicznych, przebiegów czasowych, impedancji i szumu stosować osobne tabele o właściwej strukturze, połączone `run_id`.

## 17. Opracowanie w Pythonie — plan po pozyskaniu danych

Nie tworzymy wyników z pustych pól ani syntetycznych przebiegów udających pomiar. Przed budową Python może obsłużyć wyłącznie jawnie oznaczony model i scenariusze katalogowe; po budowie może przetwarzać rzeczywiście zebrane dane.

Plan analizy:

1. **Kontrola wejścia:** sprawdzenie manifestu i hashy, jednostek, wymaganych pól, unikalności ID, częstotliwości próbkowania oraz zgodności konfiguracji. Niezgodne pliki trafiają do listy wyjątków; nie są automatycznie poprawiane bez śladu.
2. **Rozdzielenie danych:** surowe, skalibrowane i pochodne. Każda tabela pochodna wskazuje wejścia, parametry analizy i wersję kodu. Przeliczenie dBFS na Pa/V jest dopuszczalne tylko z przypisaną kalibracją.
3. **Obliczenia:** RMS/peak z właściwego pasma i okna; harmoniczne według jednej opisanej metody; kompresja przy porównywalnym pobudzeniu; impedancja z wielkości zespolonych i wspólnego czasu. Rozbieżności z eksportem aplikacji wyjaśnić.
4. **Kontrola jakości:** maski clippingu, niskiego SNR, niepewnego czasu, brakujących harmonicznych i zmiany geometrii. Wynik odrzucony pozostaje w danych z kodem przyczyny.
5. **Powtarzalność:** osobno rozrzut bez ruszania mikrofonu, po ponownym ustawieniu i między sesjami. Nie uśredniać faz z niezsynchronizowanych przebiegów; nie liczyć średniej energii przez dowolne uśrednianie liczb w dB.
6. **Porównanie:** krzywe przy tej samej geometrii i temperaturze, z poprawnym odniesieniem do pobudzenia. Jeżeli nie da się spełnić warunków, raportować różnice opisowo lub jako wynik warunkowy.
7. **Raport:** eksport tabel bez ukrytej interpolacji, wykresów z jednostkami, warunkami i zakresem ważności oraz listy otwartych pytań. Zapisać wersję Pythona, użyte biblioteki i sposób uruchomienia analizy.

Wartości w tabeli wymagań nie mogą być zaszyte w kodzie bez źródła i rewizji. Kod powinien otrzymywać osobno dane oraz zatwierdzoną specyfikację. Wynik porównania z progiem nie zmienia statusu niepewnego pomiaru.

## 18. Niepewność, zamknięcie raportu i następny eksperyment

Ocena niepewności obejmuje przynajmniej kalibrację amplitudy, powtarzalność, pozycjonowanie, tło, temperaturę, liniowość toru, obróbkę i timing, zależnie od wielkości. Nie dopisywać pozornie dokładnego `±… dB` bez podstaw. Mały rozrzut kolejnych przebiegów nie wyklucza wspólnego błędu systematycznego.

Przed odbiorem uzgodnić regułę decyzji przy granicy. Przykładowo można wymagać, aby cały uzasadniony przedział wyniku mieścił się po stronie spełniającej próg; jest to propozycja reguły do zatwierdzenia, nie przywołanie normy. Bez oszacowania niepewności wynik blisko granicy pozostaje nierozstrzygnięty.

Każdy raport kończy się odpowiedzią na pięć pytań:

1. Co rzeczywiście zmierzono, w jakim pokoju, punkcie, stanie i zakresie wiarygodności?
2. Co wynika tylko z katalogu, obliczenia lub założenia? Które niewiadome mogłyby zmienić wybór?
3. Które wymagania mają zatwierdzone progi i jakie są wyniki oceny? Czego nie można ocenić?
4. Jaki jest najsilniejszy argument przeciw obecnemu wariantowi i najtańsza wiarygodna alternatywa eksperymentalna?
5. Jaki jeden następny eksperyment rozstrzygnie najważniejszą niewiadomą, na jakich wejściach i z jaką regułą zakończenia?

Na obecnym etapie następnym działaniem metrologicznym jest **przygotowanie katalogowych wejść i scenariuszy niepewności do projektu regulowanej skrzyni**. Dobór toru i właściwa walidacja akustyczna pozostają odłożone do zakończenia budowy zgodnie z U-002. Dopuszczalne są wcześniejsze bezpieczne kontrole posiadanymi przyrządami, jeśli ich przydatność została potwierdzona; nie są warunkiem pozyskania T/S przed budową. Nie deklarujemy zgodności z normami, certyfikacji ani osiągów wolnego pola na podstawie opisanych badań w pokoju.
