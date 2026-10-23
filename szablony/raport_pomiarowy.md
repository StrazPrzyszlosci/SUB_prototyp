# Raport pomiarowy / karta przygotowania pomiarów — [tytuł]

**Szablon, wersja 2026-10-23.** Wszystkie pola w nawiasach kwadratowych oraz puste komórki wymagają uzupełnienia. Nie są wynikami ani akceptacją wymagań. Nieużywane sekcje pozostawić z uzasadnieniem `NIE_DOTYCZY`, `NIEZMIERZONE` lub `POZA_ZAKRESEM_METODY`; nie zastępować braku danych zerem. Kopia szablonu przed wykonaniem testów jest planem, a nie raportem zakończonej walidacji.

Powiązania planowane: [plan B+R](../PLAN_B_R.md), [raport inicjalizacji](../raporty/001_inicjalizacja.md).

## 1. Identyfikacja i zakres

| Pole | Wartość |
| --- | --- |
| ID raportu / rewizja | [uzupełnij] |
| Session ID / lista run_id | [uzupełnij; brak, jeśli nie wykonywano pomiarów] |
| Autor / operator | [uzupełnij] |
| Data i godziny ze strefą | [uzupełnij; nie mylić z datą szablonu] |
| Etap | [przed budową / budowa / po budowie / integracja] |
| Charakter dokumentu | [plan / pomiar / analiza danych / porównanie iteracji] |
| Badany egzemplarz i config_id | [uzupełnij] |
| Cel i pytanie rozstrzygane | [jedno konkretne pytanie] |
| Zakres częstotliwości, poziomów i punktów | [uzupełnij] |
| Czego ten raport nie rozstrzyga | [jawne ograniczenia] |
| Ścieżka do danych i manifestu | [uzupełnij po pozyskaniu danych] |

**Rodzaje źródeł:** `dane producenta`, `pomiar własny`, `pomiar niezależny`, `symulacja`, `obliczenie przybliżone`, `założenie`. Każdy wniosek musi wskazywać źródło. Własne powtórzenia nie są pomiarem niezależnym.

## 2. Aktualizacje nadrzędne i zgodność zakresu

| ID | Data | Obowiązująca decyzja | Jak zastosowano w tym raporcie |
| --- | --- | --- | --- |
| U-001 | 2026-10-23 | Użytkownik ma multimetr, oscyloskop i lutownicę. Dobór i zakupy toru pomiarowego odkładamy do zakończenia budowy prototypu. Przed budową nie wymagamy pomiarów T/S ani free-air. | [uzupełnij] |
| U-002 | 2026-10-23 | Pomiary są możliwe wyłącznie w pokoju odsłuchowym. Ground-plane jest niedostępną metodą odniesienia, nie zadaniem ani blokadą rozpoczęcia budowy. Wyniki akustyczne są in-room. | [uzupełnij] |

Jeżeli raport powstaje przed budową, wypełnić źródła katalogowe, scenariusze i ryzyka; sekcje pomiarowe oznaczyć jako planowane po budowie. Nie tworzyć w tej karcie listy zakupowej ani rekomendacji modeli toru. Wykorzystanie posiadanych przyrządów wymaga potwierdzenia ich możliwości dla konkretnego pomiaru.

## 3. Pytanie, hipoteza i reguła zakończenia

- Pytanie badawcze: [uzupełnij].
- Hipoteza robocza i jej rodzaj źródła: [uzupełnij].
- Zmienna celowo zmieniana: [uzupełnij].
- Warunki utrzymywane stałe: [uzupełnij].
- Wynik, który podważy hipotezę: [uzupełnij].
- Plan powtórzeń i uzasadnienie: [uzupełnij].
- Warunki przerwania ze względu na bezpieczeństwo lub utratę wiarygodności: [uzupełnij na podstawie danych badanego układu].
- Warunek zakończenia po uzyskaniu wystarczającej odpowiedzi: [uzupełnij].

## 4. Wymagania — oddzielnie od danych

Nie wpisywać arbitralnych liczb jako ustalonych wymagań. Próg proponowany nie jest progiem zatwierdzonym. Przy braku zatwierdzenia wynik można opisać, ale ocena odbiorowa pozostaje `NIEROZSTRZYGNIĘTE`.

| ID wymagania | Wielkość / jednostka | Pasmo, punkt i warunki | Proponowany próg / źródło | Status i ślad zatwierdzenia | Reguła decyzji z niepewnością |
| --- | --- | --- | --- | --- | --- |
| [ID] | SPL peak in-room | [sygnał, czas, pozycja] | [do zaproponowania] | [do zatwierdzenia] | [do uzgodnienia] |
| [ID] | SPL RMS / poziom równoważny in-room | [pasmo, czas, crest factor] | [do zaproponowania] | [do zatwierdzenia] | [do uzgodnienia] |
| [ID] | Wydajność 20–40 Hz in-room | [siatka częstotliwości i kryteria użyteczności] | [do zaproponowania] | [do zatwierdzenia] | [do uzgodnienia] |
| [ID] | THD / harmoniczne | [poziomy i zakres harmonicznych] | [do zaproponowania] | [do zatwierdzenia] | [do uzgodnienia] |
| [ID] | Kompresja | [odniesienie wejścia, czas, temperatura] | [do zaproponowania] | [do zatwierdzenia] | [do uzgodnienia] |
| [ID] | Szum | [pasmo, ważenie, stan wejść, punkt] | [do zaproponowania] | [do zatwierdzenia] | [do uzgodnienia] |
| [ID] | Integracja / powtarzalność | [referencja czasu, S0 i diagnostyka] | [do zaproponowania] | [do zatwierdzenia] | [do uzgodnienia] |

Referencja ADAM Audio, jeśli używana: [model i dokument wskazane w odrębnym researchu / nie wybrano]. Status zatwierdzenia modelu: [uzupełnij]. Brakujące warunki katalogowe: [uzupełnij]. Dopuszczalny zakres porównania: [uzupełnij; nie zestawiać in-room i wolnego pola jako równoważnych pomiarów].

## 5. Katalogowe wejścia i scenariusze przed budową

| Parametr | Wartość / jednostka | Źródło, rewizja, data | Tolerancja podana przez źródło | Status / brak danych |
| --- | --- | --- | --- | --- |
| Fs, Qes, Qms, Qts | [uzupełnij] | [uzupełnij] | [udokumentowana / nieznana] | [uzupełnij] |
| Vas, Re, Le | [uzupełnij; dla Le częstotliwość/model] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| Sd, Mms, Cms, BL | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| Xmax / Xmech | [oddzielne wartości i definicje] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| Ograniczenia termiczne / moc | [wartości i warunki deklaracji] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

- Spójność jednostek i zależności T/S: [uzupełnij].
- Nieznane tolerancje i ich znaczenie dla projektu: [uzupełnij].
- Zakresy scenariuszy inżynierskich, ich uzasadnienie i zachowane zależności parametrów: [uzupełnij; nie nazywać ich tolerancją produkcyjną bez źródła].
- Model nominalny i warianty objętości: [identyfikatory obliczeń / nie wykonano].
- Decyzje możliwe bez pomiaru egzemplarza: [uzupełnij].
- Niewiadome pozostawione na etap po budowie: [uzupełnij].

**Pomiar free-air nie jest warunkiem rozpoczęcia budowy.** Brak własnych T/S zapisać jako ograniczenie modelu.

## 6. Obiekt i konfiguracja

| Element | Identyfikacja / ustawienie / źródło |
| --- | --- |
| Przetwornik i numer egzemplarza | [uzupełnij] |
| Skrzynia / rewizja / config_id | [uzupełnij] |
| Wymiary i objętość wewnętrzna brutto | [uzupełnij wraz z jednostkami] |
| Wypory przetwornika, wzmocnień i wkładów | [osobne pozycje, metoda ustalenia] |
| Objętość geometryczna netto i niepewność | [uzupełnij; nie utożsamiać z efektem wypełnienia] |
| Wypełnienie | [rodzaj, masa, położenie] |
| Uszczelki, montaż, osłona, wkłady regulacyjne | [uzupełnij] |
| Zewnętrzna elektronika i routing | [stan faktyczny / plan, bez doboru zakupowego] |
| DSP: preset, plik, rewizja, hash | [uzupełnij] |
| Gain, podziały, HPF, EQ, opóźnienie, polaryzacja | [uzupełnij per tor] |
| Limiter i dostępna obserwacja jego działania | [uzupełnij / nieznane] |
| Stan początkowy i wcześniejsze obciążenie | [uzupełnij] |

## 7. Aparatura i dopuszczalność pomiarów elektrycznych

Nie dopisywać modeli ani parametrów na podstawie samej informacji, że użytkownik ma dany rodzaj przyrządu. Brak wyposażenia dla konkretnego testu oznacza odroczenie testu, a nie obowiązek zakupu przed budową.

| Przyrząd użyty w sesji | Model / egzemplarz | Funkcja | Zakres i ograniczenia potwierdzone w dokumentacji | Kalibracja / plik / data | Status przydatności |
| --- | --- | --- | --- | --- | --- |
| Multimetr, jeśli użyty | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij / brak danych] | [potwierdzona / niepotwierdzona] |
| Oscyloskop i sonda, jeśli użyte | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij / brak danych] | [uzupełnij] |
| Inny tor, dopiero po budowie | [tylko stan faktyczny] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

Lutownica jest posiadanym narzędziem montażowym, nie źródłem danych metrologicznych.

**Jeśli planowany jest pomiar wyjścia BTL/mostkowego, wypełnić przed podłączeniem:**

- Topologia wyjścia i dokument potwierdzający: [uzupełnij / nieznane — pomiar odroczony].
- Punkty pomiaru, schemat połączeń i obciążenie: [uzupełnij].
- Odpowiednia sonda różnicowa lub rzeczywiście izolowany system: [stan faktyczny i dokumentacja / brak — pomiar odroczony].
- Dopuszczalne napięcia różnicowe i wspólne, izolacja, pasmo, tłumienie, odporność na przełączanie: [uzupełnij].
- Uziemienia i połączenia USB/innych przyrządów sprawdzone: [jak sprawdzono].
- Zasady bezpiecznego wyłączenia i rozładowania przy zmianie połączeń: [uzupełnij].

Nie przyłączać masy zwykłej uziemionej sondy do aktywnego zacisku mostka, nie odłączać przewodu ochronnego oscyloskopu i nie traktować odejmowania dwóch kanałów jako izolacji. Nie podłączać wyjścia mocy do wejścia liniowego. Multimetr między zaciskami wymaga potwierdzenia izolacji i wiarygodności dla badanego przebiegu klasy D; sam true RMS nie wystarcza. Bez potwierdzenia właściwej aparatury wpisać `napięcie wyjściowe NIEZMIERZONE`.

## 8. Pokój, pozycje i środowisko

Wszystkie wykonane tu pomiary akustyczne są **in-room**. Ground-plane i pomiar wolnego pola: `POZA_ZAKRESEM_METODY — U-002`; nie są obowiązkowym zadaniem tej sesji.

| Pole | Wartość |
| --- | --- |
| Pokój / potwierdzone wymiary | [uzupełnij] |
| Początek i kierunki układu współrzędnych | [uzupełnij; jednostki] |
| Pozycja subwoofera i punkt odniesienia odległości | [uzupełnij] |
| S0 — główny sweet spot | [x, y, z, orientacja kapsuły] |
| Odległość odsłuchu | [zmierzona; założenie briefu 2,5–3 m nie zastępuje pomiaru] |
| Punkty sąsiednie | [ID, przesunięcia względem S0; diagnostyka, nie cała kanapa] |
| Ustawienie nearfield, jeśli stosowane | [kapsuła względem membrany, odległość i zapas wychylenia] |
| Drzwi, okna, meble, adaptacja, wentylacja | [uzupełnij] |
| Temperatura / wilgotność, jeśli dostępne | [wartości, metoda, czas / nie mierzono] |
| Tło i zakłócenia okresowe | [uzupełnij] |
| Zdjęcia i szkic | [ścieżki do rzeczywistych plików] |

## 9. Protokół i kontrola jakości

| Parametr | Zapis sesji |
| --- | --- |
| Oprogramowanie / wersja / system | [uzupełnij] |
| Sygnał i plik/hash lub definicja generatora | [uzupełnij] |
| Pasmo / częstotliwości / poziomy zadane | [uzupełnij] |
| Czas, obwiednia, crest factor, przerwy | [uzupełnij] |
| Częstotliwość próbkowania i format | [uzupełnij] |
| Tor gain, wyłączone AGC i dodatkowa obróbka | [uzupełnij; nieznane jawnie] |
| Kalibracja odpowiedzi i czułości absolutnej | [oddzielnie; jeśli brak czułości, nie deklarować skalibrowanego SPL] |
| Okna analizy, ważenie, pasmo i wygładzanie | [uzupełnij] |
| Zakres harmonicznych i metoda ekstrakcji | [uzupełnij] |
| Referencja czasu / kompensacja zegarów | [uzupełnij / brak potwierdzenia] |
| Powtórzenia i punkt kontrolny | [uzupełnij] |
| Warunki termiczne i kryterium stabilizacji | [uzupełnij / niepotwierdzone] |

Kontrole wykonane, z dowodem lub przyczyną braku:

- Tło i zakres rejestracji: [uzupełnij].
- Clipping i możliwa nieliniowość całego toru, także analogowego: [uzupełnij].
- Stabilność geometrii i pobudzenia: [uzupełnij].
- Powtarzalność bez zmian: [uzupełnij].
- Dryft po serii i powrót do stanu odniesienia: [uzupełnij].
- Odstępstwa od planu oraz ich wpływ: [uzupełnij].

## 10. Dziennik prób i pliki surowe

| run_id | Czas | config_id / point_id | Bodziec i poziom | Stan cieplny | Plik surowy | Ważność / powód wykluczenia |
| --- | --- | --- | --- | --- | --- | --- |
| [uzupełnij po próbie] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [rzeczywista ścieżka] | [uzupełnij] |

Zachować natywną sesję programu, dostępne surowe WAV/przebiegi, bodźce, pliki kalibracji, zdjęcia, konfigurację DSP oraz eksporty CSV/TXT z jednostkami. Surowych plików nie nadpisywać; zachować próby przerwane. Zrzut ekranu jest ilustracją, nie zamiennikiem danych.

- Manifest: [ścieżka; pola co najmniej plik, rola, rozmiar, SHA-256, run_id].
- Metadane i opis schematu kolumn: [ścieżki].
- Ograniczenia eksportu aplikacji: [uzupełnij].
- Braki danych i ich przyczyny: [uzupełnij].

## 11. Impedancja i T/S — sekcja opcjonalna po budowie

Status: [plan po budowie / wykonano / nie mierzono; nie jest to warunek rozpoczęcia budowy].

- Metoda: [rezystancja DC / impedancja w skrzyni / opcjonalna identyfikacja przetwornika].
- Schemat i bezpieczne odniesienie elektryczne: [uzupełnij].
- Wspólny zegar równoczesnych kanałów napięcia/prądu: [jak potwierdzono / nie dotyczy].
- Kalibracja i obciążenie kontrolne: [uzupełnij].
- Poziom, pasmo, temperatura, orientacja, rezystancja przewodów: [uzupełnij].
- Model dopasowania i reszty: [uzupełnij].
- Parametry skrzyni oddzielone od free-air T/S: [uzupełnij].
- Dodatkowa informacja potrzebna do Vas/Mms: [rzeczywista masa / znana objętość i niezależne Fs / brak].
- Jeżeli użyto katalogowego Fs lub Sd: [zapis warunkowego charakteru wyniku].

| Parametr | Wynik / jednostka | Źródło: pomiar, dopasowanie lub katalog | Niepewność / ograniczenie | run_id / plik |
| --- | --- | --- | --- | --- |
| [uzupełnij] | [brak do czasu pozyskania danych] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

Nie wyprowadzać Xmax, THD ani maksymalnego SPL z samej małosygnałowej impedancji. Multimetr nie zastępuje pomiaru zespolonej impedancji. Pomiar przetwornika bez skrzyni w pokoju nie oznacza pomiaru akustycznego wolnego pola.

## 12. Odpowiedź nearfield i in-room

| run_id | Metoda / point_id | Pobudzenie i konfiguracja | Wynik / plik krzywej | Zakres ważności | Ograniczenia |
| --- | --- | --- | --- | --- | --- |
| [uzupełnij] | [nearfield in-room / S0 / punkt diagnostyczny] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

- Wpływ zmiany położenia kapsuły nearfield: [uzupełnij / nie sprawdzono].
- Różnice S0 i punktów sąsiednich: [uzupełnij; S0 pokazać osobno].
- Użyte okno i jego ograniczenie w niskim paśmie: [uzupełnij].
- Jeśli przeliczano lub łączono krzywe: [model, wejścia i uzasadnienie; bez nich nie wykonywać przeliczenia na wolne pole].
- Różnica model–pomiar i możliwe przyczyny: [uzupełnij].

## 13. SPL, THD i kompresja — wyniki in-room

Przed wypełnieniem potwierdzić definicję SPL i skalę absolutną. Peak to rzeczywisty szczyt w zadanym paśmie/oknie; RMS i poziom równoważny wymagają czasu integracji. Nie przeliczać peak/RMS stałą poprawką dla dowolnego sygnału. Nie stosować prawa odległości pola swobodnego między punktami pokoju.

**Warunki wspólne tabeli:** [point_id, konfiguracja, sygnał, czas/obwiednia, pasmo, ważenie, kalibracja, początkowy stan termiczny]. Jeżeli się zmieniają, podzielić tabelę.

| run_id | f / pasmo [Hz] | Poziom zadany [dBFS] | Napięcie audio RMS [V] lub „nie mierzono” | SPL podstawowej [dB] | SPL RMS / czas [dB, s] | SPL peak [dB] | THD [%], zakres harmonicznych | Kompresja [dB], odniesienie | Ważność / ograniczenie |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

- Osobne poziomy harmonicznych i tło przy tych częstotliwościach: [plik tabeli / brak danych].
- THD czy THD+N, metoda i pasmo: [uzupełnij].
- Składowe poniżej rozstrzygalności lub poza pasmem: [uzupełnij; nie wpisywać zera].
- Wpływ dołków/podbicia pokoju na podstawową i harmoniczne: [uzupełnij].
- Kompresja względem napięcia czy poziomu cyfrowego: [uzupełnij; bez napięcia dotyczy całego toru względem nastawy].
- Zadziałanie limitera, clipping, zmiany temperatury: [obserwacje z dowodami / brak możliwości rozdzielenia].
- Podejrzenie ograniczenia przez mikrofon lub rejestrację: [uzupełnij].
- Najwyższy zbadany ważny poziom i przyczyna zakończenia serii: [uzupełnij, zawsze in-room].
- Czy osiągnięto granicę urządzenia, granicę metody czy tylko koniec planu: [uzupełnij].
- Czy wolno nazwać wynik maksymalnym użytecznym SPL: [tylko przy komplecie zatwierdzonych kryteriów i ważnych pomiarach; w przeciwnym razie „nierozstrzygnięte”].

Nie ekstrapolować maksimum w całym paśmie z kilku częstotliwości. Bez pomiaru wychylenia nie deklarować jako faktu, że Xmax nie zostało przekroczone. Jeśli ograniczenia nie osiągnięto, nie przedstawiać najwyższej próby jako zmierzonego maksimum.

## 14. Szum i obserwacje przy cichym odsłuchu

**Wspólne warunki:** [punkt, pasmo, ważenie, czas, gain, kalibracja, stan pokoju i wejść].

| run_id | Stan systemu | Poziom / jednostka / pasmo | Widmo i tony | Tło / szum rejestracji | Wniosek i granica rozstrzygalności |
| --- | --- | --- | --- | --- | --- |
| [uzupełnij] | [tło przy wyłączonym badanym systemie] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| [uzupełnij] | [włączony, wejścia jak w użytkowaniu, bez odtwarzania] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| [uzupełnij] | [udokumentowany mute / inny bezpieczny stan diagnostyczny] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

- Oddzielenie szumu głośnika, mechaniki/elektroniki i tła: [uzupełnij / nierozstrzygnięte].
- Odejmowanie energii tła: [nie stosowano / metoda, założenia i niepewność; nie odejmować liczb dB].
- Ocena odsłuchowa w S0: [osoba, ustawienie poziomu, warunki, sposób przełączania, obserwacja / nie wykonano].
- Zakres dopuszczalnego wniosku o „czarnym tle”: [uzupełnij; nie utożsamiać braku rozróżnienia z zerowym szumem].

## 15. Faza, czas i sumowanie sekcji

Status: [wykonano / nierozstrzygnięte / plan po budowie]. Jeżeli później użyto UMIK lub innego mikrofonu USB, traktować jego zegar i zegar odtwarzania jako niezależne do czasu potwierdzenia sposobu ich obsługi.

- Referencja czasowa, źródło sygnału referencyjnego i stała geometria: [uzupełnij].
- Potwierdzona obsługa różnicy zegarów / kompensacja: [wersja, ustawienie i sposób sprawdzenia / brak potwierdzenia].
- Powtórzenie tej samej sekcji przed i po serii: [run_id, rozrzut czasu i fazy].
- Oryginalne impulsy i zapis wszystkich przesunięć/resamplingu: [pliki i operacje].
- Czy zachowano wspólny czas, bez osobnego zerowania każdej sekcji: [jak potwierdzono].

| Konfiguracja | run_id / wspólna referencja | Opóźnienia, polaryzacja, filtry | Wynik w zakresie podziału | Ograniczenia |
| --- | --- | --- | --- | --- |
| [sekcja osobno] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| [druga sekcja osobno] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| [rzeczywista suma] | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

Przewidywana suma zespolona i zgodność z rzeczywistą sumą: [uzupełnij / nie liczono z powodu braku wspólnego czasu]. Bez potwierdzonej synchronizacji nie wyciągać precyzyjnych opóźnień z oddzielnych przebiegów. Odwrócenie polaryzacji nie zastępuje dowolnego opóźnienia. Faza i opóźnienie grupowe w pokoju obejmują wpływ odbić.

## 16. Temperatura i długotrwałe obciążenie

| run_id / czas | Pobudzenie, pasmo, crest factor | Stan początkowy | Temperatura i miejsce/metoda odczytu | Zmiana odpowiedzi / kompresja | Zabezpieczenia / zakończenie |
| --- | --- | --- | --- | --- | --- |
| [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij / nie mierzono] | [uzupełnij] | [uzupełnij] |

- Kryterium i potwierdzenie powrotu do stanu odniesienia: [uzupełnij / niepotwierdzone].
- Rezystancja zimna/gorąca, jeśli bezpiecznie zmierzona: [wartości, temperatura odniesienia, czas opóźnienia od wyłączenia i korekta przewodów].
- Estymacja temperatury uzwojenia: [model i źródło współczynnika materiałowego / nie wykonywano].
- Ograniczenia: [czujnik na radiatorze nie mierzy cewki; estymacja rezystancyjna nie mierzy gorącego punktu].

Nie przyjmować uniwersalnego limitu temperatury ani czasu chłodzenia bez danych konkretnego układu. Nie mierzyć rezystancji na zasilanym wyjściu wzmacniacza.

## 17. Porównanie iteracji skrzyni A–B–A

Status: [wykonano / plan po budowie / nie dotyczy].

| Wariant / config_id | Zmieniony element i objętość netto | Stałe warunki / odstępstwa | Dane nearfield, in-room, impedancja jeśli dostępna | Stan cieplny | Wynik porównania |
| --- | --- | --- | --- | --- | --- |
| [A przed] | [uzupełnij] | [uzupełnij] | [run_id] | [uzupełnij] | [uzupełnij] |
| [B] | [uzupełnij] | [uzupełnij] | [run_id] | [uzupełnij] | [uzupełnij] |
| [A po] | [uzupełnij] | [uzupełnij] | [run_id] | [uzupełnij] | [uzupełnij] |

- Czy powrót do A odtworzył wynik i jak to oceniono: [uzupełnij].
- Możliwe przyczyny różnic poza badaną zmianą: [temperatura, montaż, uszczelnienie, geometria, tło, inne].
- Porównanie przy stałym pobudzeniu, bez korekcji pokoju: [uzupełnij].
- Osobne porównanie po wyrównaniu do wspólnego celu: [presety, koszt EQ, napięcie/headroom/kompresja lub brak możliwości oceny].
- Odgłosy mechaniczne, przecieki, osłona i panele: [obserwacje i ich status dowodowy].

## 18. Sweet spot i diagnostyka otoczenia punktu

S0 jest priorytetem. Sąsiednie punkty opisują wrażliwość na ruch głowy; nie stanowią wymogu wyrównania całej kanapy.

| point_id | Pozycja / przesunięcie względem S0 | config_id / preset | Wynik / plik | Wrażliwość i uwagi |
| --- | --- | --- | --- | --- |
| S0 | [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij] |
| [punkt diagnostyczny] | [rzeczywiste przesunięcie] | [uzupełnij] | [uzupełnij] | [uzupełnij] |

- Ustawienia subwoofera porównane przed korekcją modów: [uzupełnij].
- Dane bazowe, korekcja i pomiar po korekcji: [run_id i presety].
- Jeżeli są dwa subwoofery: każdy osobno i oba razem: [run_id / nie dotyczy].
- Stabilność wyniku S0 po ponownym ustawieniu mikrofonu: [uzupełnij / nie sprawdzono].
- Wpływ EQ na osiągi przy większym poziomie: [zmierzono / prognoza / nie sprawdzono].
- Granice przenoszenia wniosków na inne pokoje: [uzupełnij; ten raport nie potwierdza osiągów we wszystkich pokojach 17–20 m²].

## 19. Opracowanie danych i niepewność

- Kod/notatnik analizy, wersja, sposób uruchomienia: [rzeczywiste ścieżki / brak analizy w Pythonie].
- Wersja Pythona i użytych bibliotek: [uzupełnij, jeśli stosowano].
- Kontrola hashy, jednostek i powiązania run_id z konfiguracjami: [wynik kontroli / nie wykonano].
- Kalibracje i przeliczenia na Pa/V: [wejścia i równania / nie stosowano].
- Okna, filtry, wygładzanie, interpolacja, normalizacja, przesunięcia czasu: [pełna lista operacji].
- Maski nieważnych punktów i powody: [pliki / nie było / nie oceniono].
- Zgodność z eksportem programu pomiarowego: [sprawdzono jak / nie sprawdzono].

| Składnik niepewności | Podstawa oszacowania | Wielkości objęte wpływem | Uwzględnienie w ocenie |
| --- | --- | --- | --- |
| Kalibracja i liniowość toru | [dane / brak] | [uzupełnij] | [uzupełnij] |
| Powtarzalność bez zmian | [powtórzenia / brak] | [uzupełnij] | [uzupełnij] |
| Pozycjonowanie i pokój | [kontrolowane przesunięcia / brak] | [uzupełnij] | [uzupełnij] |
| Tło i granica rozstrzygalności | [pomiary / brak] | [uzupełnij] | [uzupełnij] |
| Temperatura i dryft | [pomiary / brak] | [uzupełnij] | [uzupełnij] |
| Zegary, timing i obróbka | [weryfikacja / brak] | [uzupełnij] | [uzupełnij] |

Niepewność łączna i metoda jej wyznaczenia: [uzupełnij / nie wyznaczono]. Brak oszacowania nie jest zerową niepewnością. Nie podawać wielu cyfr, jeśli nie mają pokrycia w rozdzielczości i metodzie.

## 20. Ocena wymagań i zakres ważności

Status danych: `ZMIERZONE`, `OBLICZONE`, `NIEZMIERZONE`, `POZA_ZAKRESEM_METODY`, `NIEWAŻNE`. Status odbioru: `SPEŁNIONE`, `NIESPEŁNIONE`, `NIEROZSTRZYGNIĘTE`, `NIE_DOTYCZY`. Nie scalać tych dwóch ocen w pojedyncze „PASS”.

| ID wymagania | Dane / run_id / rodzaj źródła | Status danych | Zatwierdzony próg i warunki | Niepewność / ograniczenie | Ocena i uzasadnienie |
| --- | --- | --- | --- | --- | --- |
| [uzupełnij] | [uzupełnij] | [uzupełnij] | [uzupełnij / brak zatwierdzenia] | [uzupełnij] | [uzupełnij; przy braku progu nierozstrzygnięte] |

Nieprzeprowadzone badania oraz skutek dla wniosków: [uzupełnij]. Ground-plane i wolne pole pozostają poza zakresem U-002; ich brak nie jest negatywnym wynikiem prototypu. Pomiary in-room nie ustanawiają zgodności z niezweryfikowaną normą ani katalogowych osiągów urządzenia w innych warunkach.

## 21. Wnioski, decyzja i jeden następny eksperyment

- Odpowiedź na pytanie z sekcji 3, z odsyłaczami do danych: [uzupełnij / brak podstaw do odpowiedzi].
- Co jest potwierdzone pomiarem, co warunkowe, a co nadal nieznane: [uzupełnij].
- Trzy założenia, których błędność najbardziej zmieni wybór: [uzupełnij].
- Najsilniejszy argument przeciw obecnemu wariantowi: [uzupełnij].
- Najtańsza wiarygodna alternatywa konstrukcyjna lub eksperymentalna: [uzupełnij; bez doboru toru przed budową].
- Decyzja o iteracji: [kontynuować wariant / zmienić jeden element / odroczyć ocenę osiągów — uzasadnienie].
- Decyzja o przejściu do dwóch subwooferów/monitorów: [nie dotyczy / otwarta / uzasadnienie danymi].

**Następny eksperyment:** [jedno działanie; przed budową oprzeć projekt na analizie katalogowej/modelowej, a walidację akustyczną pozostawić na etap po budowie. Dopuszczalne są bezpieczne kontrole posiadanymi przyrządami o potwierdzonej przydatności; nie wymagają obecnego doboru ani zakupów toru].

| Element planu | Wpis |
| --- | --- |
| Niewiadoma do rozstrzygnięcia | [uzupełnij] |
| Dokładne wejścia i zależności | [uzupełnij] |
| Zmiana względem poprzedniej próby | [uzupełnij] |
| Dostępna metoda i granice w pokoju | [uzupełnij] |
| Warunek rozstrzygnięcia pytania | [uzupełnij; oddzielić od niezatwierdzonego progu jakości] |
| Warunek przerwania / zakończenia | [uzupełnij] |
| Wynik oczekiwany jako artefakt | [dane, tabela, wykres, raport; bez prognoz udających wyniki] |
| Odpowiedzialny / termin / otwarte decyzje | [uzupełnij] |

## 22. Załączniki i kontrola kompletności

- Oryginalne dane, metadane i manifest: [ścieżki / nie powstały].
- Konfiguracje, kalibracje, bodźce, schematy i zdjęcia: [ścieżki / nie dotyczy].
- Eksporty liczbowe, wykresy z jednostkami i zakresami ważności: [ścieżki / nie powstały].
- Kod analizy i ślad przeliczeń: [ścieżki / nie dotyczy].
- Źródła katalogowe i ich rewizje: [wykaz rzeczywistych źródeł].
- Lista wykluczonych prób i braków: [wykaz / brak prób].
- Progi i zgody: [ślad zatwierdzenia / brak zatwierdzenia].

Autor sprawdził rozdzielenie danych od założeń i progów: [imię/data lub nie sprawdzono]. Zakres zakończonej pracy: [uzupełnij]. Otwarte kwestie: [uzupełnij].
