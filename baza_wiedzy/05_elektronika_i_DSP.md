# 05. Elektronika zewnętrzna, modele DSP i granice ochrony

## Status i granice rozdziału

- **[Wymaganie — brief]** Podstawą jest [brief v0.6](../brief_system_audio_DIY_v0.6.md): gotowy miniDSP, gotowe moduły wzmacniaczy klasy D i elektronika poza skrzynią subwoofera.
- **[Ustalenie — użytkownik]** Aktualny etap obejmuje badania do budowy; nie montujemy elektroniki, nie wybieramy konkretnych modeli, nie kupujemy i nie podajemy niezweryfikowanych cen.
- **[Ustalenie — użytkownik]** Użytkownik ma multimetr, oscyloskop i lutownicę; dobór oraz zakupy toru pomiarowego są odłożone do zakończenia budowy, a późniejsze pomiary wyłącznie w pokoju.
- **[Model/metoda]** Oznaczenie obejmuje wiedzę inżynierską, równania i procedury badawcze; nie oznacza wykonanego pomiaru, symulacji ani zweryfikowanej funkcji dowolnego modelu miniDSP.
- **[Rekomendacja]** Rozdział rozwija przyszły [plan B+R](../PLAN_B_R.md); parametry modeli elektroakustycznych mają pochodzić z [planowanego rozdziału 02](02_modelowanie_elektroakustyczne.md).
- **[Ustalenie — zakres]** Nie prowadzono researchu internetowego; nie ustalono modeli referencyjnych, progów odbiorowych ani konkretnych wymagań prawnych dla przyszłego produktu.

## Architektura i osiem niezależnych wyjść

- **[Wymaganie — brief]** Docelowo dwa subwoofery oraz dwa aktywne monitory trójdrożne wymagają co najmniej ośmiu niezależnych wyjść DSP i odpowiadających im kanałów wzmacniacza.
- **[Model/metoda]** Niezależność oznacza osobny routing, poziom, filtry, opóźnienie i ochronę każdego toru; liczba wejść, gniazd albo kanałów deklarowanych ogólnie nie wystarcza.

| Wyjście robocze | Przeznaczenie docelowe | Status |
|---|---|---|
| 1 | Lewy monitor: sekcja niskotonowa | **[Założenie]** Numeracja do przyszłego mapowania |
| 2 | Lewy monitor: sekcja średniotonowa | **[Założenie]** Numeracja do przyszłego mapowania |
| 3 | Lewy monitor: sekcja wysokotonowa | **[Założenie]** Numeracja do przyszłego mapowania |
| 4 | Prawy monitor: sekcja niskotonowa | **[Założenie]** Numeracja do przyszłego mapowania |
| 5 | Prawy monitor: sekcja średniotonowa | **[Założenie]** Numeracja do przyszłego mapowania |
| 6 | Prawy monitor: sekcja wysokotonowa | **[Założenie]** Numeracja do przyszłego mapowania |
| 7 | Pierwszy subwoofer | **[Założenie]** Numeracja do przyszłego mapowania |
| 8 | Drugi subwoofer | **[Założenie]** Numeracja do przyszłego mapowania |

- **[Rekomendacja]** Dla prototypu opisać jeden czynny tor subwoofera i rozbudowę do powyższej mapy; nie przesądzać zakupu urządzenia przejściowego ani liczby obudów elektroniki.
- **[Model/metoda]** Przy sumowaniu kanałów lewego i prawego uwzględnić sygnały skorelowane: suma może przekroczyć zakres pojedynczego wejścia mimo braku clippingu na wejściach.
- **[Rekomendacja]** Sprawdzić później liczbę wejść, matrycę sumowania, niezależność wyjść, dostępne bloki, zasoby filtrów, maksymalne opóźnienia i sposób odtwarzania konfiguracji.
- **[Model/metoda]** Kilka urządzeń DSP wymaga dodatkowo analizy zegarów, opóźnień, wspólnej regulacji głośności i zachowania przy utracie jednego urządzenia.
- **[Wymaganie — brief]** Własny programowalny DSP jest kierunkiem późniejszym; nie stanowi warunku uruchomienia pierwszego prototypu ani przedmiotu obecnej implementacji.

## Model kompletnego toru sygnałowego

- **[Model/metoda]** Tor roboczy: źródło → wejście analogowe z ADC albo wejście cyfrowe → regulacja poziomu i routing → filtry kanału → ochrona → DAC → wzmacniacz → przetwornik.
- **[Model/metoda]** Typ wejścia decyduje o obecności ADC; wejście cyfrowe nie usuwa ograniczeń poziomu wewnątrz DSP ani potrzeby przetwarzania częstotliwości próbkowania, jeśli jest wymagane.
- **[Rekomendacja]** Sporządzić mapę wszystkich regulacji poziomu: źródło, wejście DSP, matryca, EQ, wyjście DSP, tłumik analogowy i wzmocnienie modułu.
- **[Model/metoda]** Dla każdego węzła rozdzielić poziom nominalny, maksymalny bez przesterowania, szum oraz sposób reprezentacji wartości szczytowej i RMS.
- **[Model/metoda]** dBFS jest odniesieniem cyfrowym, a wolty odnoszą się do konkretnego wejścia lub wyjścia; przeliczenie wymaga udokumentowanego poziomu analogowego i konwencji sygnału.
- **[Model/metoda]** Wzmacniacz opisać wzmocnieniem napięciowym `A_v(f,Z,T)`, ograniczeniem napięcia i prądu oraz stanem termicznym; jedna moc przy impedancji nominalnej nie opisuje całego toru.
- **[Rekomendacja]** Zachować konfigurację odniesienia z wyciszonymi nieużywanymi wyjściami, jednoznacznym mapowaniem przewodów i zablokowaną przypadkową zmianą przypisania kanałów.

## Modele filtrów: co mogą opisać

- **[Model/metoda]** Uproszczona odpowiedź napięcie–ciśnienie obudowy zamkniętej może mieć postać `H_b(s) = K s²/[s² + (ω_b/Q_b)s + ω_b²]`, gdzie `ω_b = 2πf_b`.
- **[Model/metoda]** `s` jest zespoloną częstotliwością w s⁻¹, `f_b` podaje się w Hz, a `Q_b` jest bezwymiarowe; `K` zawiera czułość i ustaloną geometrię promieniowania, bez odpowiedzi pokoju.
- **[Model/metoda]** To model małosygnałowy o parametrach skupionych, przy założeniach dotyczących promieniowania; pomija m.in. nieliniowości napędu, zmiany termiczne i szczegółowe mody obudowy.
- **[Model/metoda]** `f_b` i `Q_b` opisują bieguny tego modelu; częstotliwość spadku o 3 dB zależy od dobroci i nie jest ogólnie równa `f_b`.
- **[Model/metoda]** Przekształcenie typu Linkwitz ma szablon `F_LT(s) = [s² + (ω_b/Q_b)s + ω_b²]/[s² + (ω_t/Q_t)s + ω_t²]`; docelowe `ω_t,Q_t` pozostają zmiennymi badania.
- **[Model/metoda]** Iloczyn `H_b F_LT` odtwarza docelowe bieguny tylko w granicach poprawności modelu; filtr nie zwiększa dostępnego wychylenia, napięcia ani możliwości odprowadzania ciepła.
- **[Model/metoda]** Alternatywą badawczą są półki i PEQ; porównywać ich łączną odpowiedź amplitudową, fazową oraz koszt w headroomie, zamiast zakładać równoważność pojedynczego podbicia z transformacją.
- **[Rekomendacja]** Rozpatrzyć wariant bez rozszerzenia pasma, wariant z głębszym zejściem i wariant priorytetu headroomu; bez danych nie ustalać częstotliwości ani dobroci jako nastaw końcowych.
- **[Model/metoda]** Szablon analogowy wymaga przekształcenia do filtru cyfrowego przy znanej częstotliwości próbkowania; sprawdzić odwzorowanie częstotliwości, stabilność i kwantyzację współczynników.
- **[Model/metoda]** Sekcje biquad wymagają określenia konwencji współczynników i ich normalizacji; współczynniki z innego urządzenia nie muszą być przenośne bez przeliczenia.
- **[Model/metoda]** Nawet przemienne idealne filtry liniowe mogą powodować różne poziomy pośrednie po zmianie kolejności; limiter jest nieliniowy, więc kolejność względem niego zmienia działanie toru.

## Podział pasma, faza i integracja

- **[Model/metoda]** Celem zwrotnicy jest suma odpowiedzi akustycznych sekcji; elektryczny filtr o określonej nazwie nie gwarantuje tej samej charakterystyki akustycznej.
- **[Model/metoda]** Filtry dolno- i górnoprzepustowe dobierać łącznie z odpowiedzią przetworników, obudowami i opóźnieniami; szablon Linkwitz–Riley jest metodą do rozważenia, nie ustalonym wyborem.
- **[Model/metoda]** Suma w punkcie odsłuchu jest zespolona i zależy od fazy, amplitudy oraz drogi propagacji; nie wyznacza jej suma samych modułów charakterystyk.
- **[Model/metoda]** Opóźnienie `τ` wnosi fazę `φ(f) = −2πfτ`; odwrócenie polaryzacji zmienia znak sygnału i nie jest zamiennikiem dowolnego opóźnienia.
- **[Model/metoda]** Filtr all-pass zmienia fazę i opóźnienie grupowe bez idealnej zmiany modułu; nie usuwa ograniczeń przyczynowości ani przestrzennej zależności odpowiedzi pokoju.
- **[Model/metoda]** FIR może realizować inne kompromisy fazy i opóźnienia niż IIR; dostępność, długość, latencja i ewentualne dzwonienie przed impulsem wymagają analizy konkretnej implementacji.
- **[Rekomendacja]** Dla dwóch subwooferów zachować niezależne poziomy, opóźnienia, polaryzację, EQ i ochronę; ich ustawienia nie muszą być identyczne.
- **[Model/metoda]** Drugi subwoofer nie gwarantuje stałego przyrostu SPL w całym paśmie; sumowanie zależy od sygnałów, położenia, fazy i ograniczeń poszczególnych torów.

## Gain staging: poziomy, szum i clipping

- **[Model/metoda]** Clipping może wystąpić w źródle, ADC, matrycy, blokach DSP, DAC lub wzmacniaczu; zmniejszenie poziomu za przesterowanym węzłem nie odtwarza utraconego przebiegu.
- **[Model/metoda]** Zapas cyfrowy trzeba liczyć dla całej kaskady i sumowania; maksymalny boost nie jest zawsze równy największej dodatniej wartości wpisanej w jeden filtr PEQ.
- **[Rekomendacja]** Analizować odpowiedź łączną oraz szczyty sygnałów w węzłach pośrednich; sam wykres charakterystyki amplitudowej nie obejmuje wszystkich przejść i sum chwilowych.
- **[Model/metoda]** Dla szczytu `L_pk` dBFS i stałego wzmocnienia skalarnego `B` dB warunek bez zapasu to `L_pk + B ≤ 0`; nie jest to ogólna granica szczytów po filtrze o maksymalnym module `B` dB.
- **[Model/metoda]** Jeśli DAC daje `D_FS` V RMS dla sinusoidy przy 0 dBFS, to dla sinusoidy na poziomie `L` dBFS w liniowym zakresie `U_głośnika,RMS = |A_v| D_FS · 10^(L/20)`, z uwzględnieniem stałych tłumień.
- **[Model/metoda]** Dla tej samej konwencji próg `L_lim = 20 log10[U_lim,RMS/(|A_v| D_FS)]`; wzór nie opisuje automatycznie detektora szczytowego ani sygnałów o innym współczynniku szczytu.
- **[Model/metoda]** Dla sinusoidy `U_pk = √2 U_RMS`; dla muzyki związek między RMS a szczytem zależy od przebiegu i okna analizy, więc progów nie wolno przenosić bez określenia detektora.
- **[Rekomendacja]** Skalibrowanie poziomów będzie przyszłym zadaniem; obecnie brak wartości `D_FS`, `A_v`, progów clippingu oraz ograniczeń wyjściowych, więc nie podawać nastaw limitera w dBFS.
- **[Model/metoda]** Bardzo mały poziom cyfrowy przy dużym stałym wzmocnieniu końcówki może pogorszyć relację sygnału do szumu wyjścia analogowego; maksymalne poziomy wszędzie zwiększają z kolei ryzyko przesterowania.
- **[Rekomendacja]** Dobierać czułość końcówki i tłumienie jako kompromis szumu oraz zapasu; tłumik znajdujący się za limiterem wymaga uwzględnienia w jego kalibracji.
- **[Model/metoda]** Nie zakładać, że wewnętrzne obliczenia zmiennoprzecinkowe chronią ADC, DAC lub każdy blok programu; formaty, zakresy i wskaźniki przesterowania wymagają dokumentacji urządzenia.
- **[Model/metoda]** Szczyty odtworzonego przebiegu analogowego mogą różnić się od szczytów próbek; zapas i obsługa true-peak są odrębnymi zagadnieniami do sprawdzenia.

## Cel 20 Hz i koszt w headroomie

- **[Wymaganie — brief]** Użyteczne okolice 20 Hz są celem do porównania z wysokim SPL i headroomem w basie; nie ma wymogu płaskiego 20 Hz przy dowolnej głośności.
- **[Model/metoda]** Podbicie `B` dB zwiększa wymaganą amplitudę napięcia w danej częstotliwości w stosunku `10^(B/20)`; przy niezmienionej impedancji moc czynna skaluje się jak `10^(B/10)`.
- **[Model/metoda]** W modelu liniowym wychylenie przy tej samej częstotliwości rośnie proporcjonalnie do napięcia; ograniczenie przez wychylenie może pojawić się przed clippingiem wzmacniacza.
- **[Model/metoda]** Dla akustycznie małego promiennika i stałej geometrii wymagana amplituda wychylenia przy zadanym ciśnieniu skaluje się jak `1/(S_d f²)`; to model promieniowania, nie prognoza SPL w pokoju.
- **[Model/metoda]** Rozszerzanie pasma filtrami zużywa osobno zapas cyfrowy, zapas napięcia i prądu końcówki oraz zapas mechaniczny i termiczny przetwornika.
- **[Model/metoda]** HPF ogranicza zawartość poniżej potrzebnego pasma, lecz jego nachylenie, faza i częstotliwość zmieniają odpowiedź użytkową; samo istnienie HPF nie gwarantuje ochrony.
- **[Rekomendacja]** Porównać konfiguracje pod kątem napięcia, prądu, wychylenia i przewidywanego ograniczenia w funkcji częstotliwości; nie oceniać ich wyłącznie przez F3 lub ilość boostu.
- **[Model/metoda]** Wzmocnienie pomieszczenia zależy od miejsca i częstotliwości; nie wpisywać stałego room gain jako gwarantowanego odzyskania headroomu.
- **[Rekomendacja]** Dla każdego wariantu litrażu ponownie policzyć wymagania filtru i ochrony; zmiana skrzyni lub przetwornika unieważnia automatyczne przeniesienie wcześniejszych nastaw.

## Ochrona urządzenia niezależna od room EQ

- **[Rekomendacja]** Rozdzielić konfigurację urządzenia: przetwornik, objętość, wzmocnienie, HPF i limity, od konfiguracji pokoju: położenie, opóźnienia i korekcja po przyszłych pomiarach.
- **[Model/metoda]** Niezależność oznacza utrzymanie ochrony po wyłączeniu, wymianie lub resecie room EQ; nie oznacza, że korekcja pokoju nie zmienia zapotrzebowania na napięcie i wychylenie.
- **[Rekomendacja]** Logicznie umieścić końcowy limiter ochronny za wszystkimi blokami mogącymi podnieść poziom danego wyjścia; dalsze wzmocnienia muszą być stałe, znane i uwzględnione w kalibracji.
- **[Model/metoda]** Jeśli architektura sprzętu wymusza inny układ bloków, potrzebny jest dowód granicy poziomu dla całego toru; nie zakładać dowolnej kolejności bloków w nieustalonym miniDSP.
- **[Model/metoda]** Limiter szczytowy ogranicza krótkotrwałe napięcie według określonego detektora, czasu ataku i ewentualnego look-ahead; nie jest automatycznie ogranicznikiem wychylenia przy każdej częstotliwości.
- **[Model/metoda]** Limiter RMS uwzględnia poziom i czas przez okno detekcji oraz stałe czasowe; nie mierzy temperatury cewki. Model termiczny wymaga dodatkowo danych cieplnych, których nie zastępuje moc katalogowa.
- **[Model/metoda]** Moc czynna wymaga średniej iloczynu napięcia i prądu; `U_RMS²/R` jest modelem rezystora, a impedancja przetwornika zależy od częstotliwości i stanu pracy.
- **[Model/metoda]** Ochrona wychyleniowa wymaga zależności `X(f)/U(f)` i analizy sygnałów; pojedynczy limit napięcia można przyjąć konserwatywnie dla określonego pasma, ale nie utożsamiać go z dokładnym estymatorem wychylenia.
- **[Model/metoda]** Granicę napięcia rozpatrywać jako minimum ograniczeń końcówki, prądu, wychylenia i termiki, przy zgodnych definicjach amplitudy; ograniczenia dynamiczne wymagają dodatkowego modelu czasowego.
- **[Rekomendacja]** Próg mechaniczny opierać na udokumentowanej definicji wychylenia i marginesie; katalogowe Xmax nie gwarantuje niskiego THD, a Xmech nie jest celem pracy.
- **[Model/metoda]** Atak, powrót i look-ahead zmieniają przepuszczane szczyty, opóźnienie, modulację i słyszalność działania; żaden zestaw czasów nie jest tu zatwierdzony.
- **[Rekomendacja]** W przyszłej analizie czasowej uwzględnić start sygnału, krótkie impulsy, wieloton, sygnały o różnych współczynnikach szczytu oraz przełączenie i odtworzenie presetu.
- **[Model/metoda]** Limiter nie naprawia wcześniejszego clippingu ani uszkodzenia końcówki; zabezpieczenia DC, nadprądowe i termiczne są odrębnymi funkcjami sprzętu do zweryfikowania.
- **[Rekomendacja]** Jeżeli wybrany DSP nie zapewni wymaganej ochrony, pozostawić bramkę doboru otwartą lub zmienić architekturę; nie zastępować brakującej funkcji samą korekcją pasma.

## Room EQ i ograniczenia późniejszych pomiarów w pokoju

- **[Ustalenie — użytkownik]** Pomiary nastąpią po budowie i tylko w pokoju; obecnie nie dobieramy mikrofonu, interfejsu ani akcesoriów i nie deklarujemy uzyskanych wyników.
- **[Model/metoda]** Odpowiedź w sweet spocie zawiera urządzenie, propagację i odbicia; bez dodatkowych założeń nie rozdziela ich jednoznacznie ani nie stanowi pomiaru wolnego pola.
- **[Rekomendacja]** Korygować pokój po ustaleniu działania urządzenia i integracji; główny punkt odsłuchu pozostaje priorytetem, a sąsiednie punkty służą ocenie wrażliwości wyniku.
- **[Model/metoda]** Głęboki dołek interferencyjny może być mało podatny na boost, który zwiększy obciążenie przetwornika; rozważyć położenie, opóźnienie i ograniczenie zakresu korekcji.
- **[Model/metoda]** Odwrócenie modułu odpowiedzi nie odwraca dowolnej odpowiedzi czasowej pokoju; filtry przyczynowe i stabilne mają ograniczenia, a wynik zależy od położenia odbiornika.
- **[Rekomendacja]** Po każdej zmianie room EQ ponownie sprawdzić budżet poziomów oraz aktywność limiterów; preset pokojowy nie może wyłączać zabezpieczeń urządzenia.
- **[Model/metoda]** Każdy przyszły wynik SPL opisać pasmem, sygnałem, czasem, odległością, geometrią, miarą RMS/szczyt i kryterium limitu; nie przenosić go automatycznie do innego pokoju.

## Moduły klasy D, szum i obudowa elektroniki

- **[Rekomendacja]** Dla późniejszego doboru zebrać dokumentację modułu i zasilacza: zakres obciążenia, napięcie i prąd, warunki mocy, gain, szum, chłodzenie, stany błędów oraz mute/standby.
- **[Model/metoda]** Wspólny zasilacz kilku kanałów wymaga analizy jednoczesnego poboru i limitów; suma reklamowanych mocy kanałów nie potwierdza mocy ciągłej całego zestawu.
- **[Model/metoda]** Szum porównywać po odniesieniu do tego samego węzła, wzmocnienia, pasma i ważenia; sumowanie kwadratowe napięć szumów wymaga założenia ich nieskorelowania.
- **[Model/metoda]** Połączenie zbalansowane pomaga tylko przy zgodnej topologii wejścia, wyjścia i ekranowania; samo złącze nie ustala odporności na zakłócenia.
- **[Rekomendacja]** Zaplanować obudowę elektroniki z ochroną przed dostępem dziecka, mocowaniem modułów, wentylacją, odciążeniem przewodów i rozdzieleniem torów mocy od sygnałowych.
- **[Model/metoda]** Masa sygnałowa, ekran, obudowa i przewód ochronny pełnią różne role; ich połączenia wynikają z topologii oraz dokumentacji, a usuwanie ochrony nie jest metodą eliminacji brumu.
- **[Model/metoda]** Wyjścia modułu mogą być mostkowe lub pływające; zacisku głośnikowego nie traktować jako masy oscyloskopu. Przyszła metoda pomiaru zależy od topologii i dopuszczalnych napięć.
- **[Ustalenie — zakres]** Posiadanie oscyloskopu nie potwierdza gotowości do pomiarów końcówki klasy D ani pracy przy zasilaniu sieciowym; obecny rozdział nie jest instrukcją takich czynności.
- **[Rekomendacja]** Opisać oczekiwane zachowanie przy starcie, zaniku sygnału, awarii DSP i wyłączeniu; funkcje ograniczające trzaski i uszkodzenia muszą wynikać z dokumentacji dobranych urządzeń.
- **[Ustalenie — zakres]** Bez źródeł nie wskazujemy numerów norm, obowiązków prawnych ani zgodności produktu; temat przyszłej komercjalizacji wymaga osobnego opracowania.

## Następny etap badań i warunki zamknięcia doboru

- **[Rekomendacja]** Najbliższy krok: opisać w tabeli brakujące dane toru oraz wymagane funkcje miniDSP i modułów, równolegle do zebrania wejść przetworników i wariantów objętości.
- **[Rekomendacja]** Obliczenia później wykonać skryptami Pythona: odpowiedzi kaskad, poziomy pośrednie, napięcie, prąd i wychylenie; zapisać jednostki SI, wersje bibliotek, hashe wejść i ograniczenia.
- **[Ustalenie — zakres]** [Planowany raport obliczeń](../raporty/002_obliczenia_wstepne.md) nie jest tutaj źródłem istniejących wyników; nie wygenerowano współczynników filtrów ani presetów.
- **[Rekomendacja]** Przed zamknięciem doboru powiązać każdy limiter z przetwornikiem, objętością, pasmem, poziomem DAC i gainem końcówki; opisać zachowanie po resecie oraz granice ochrony.
- **[Wymaganie — brief]** Modele referencyjne i mierzalne progi wymagają zatwierdzenia użytkownika; liniowy model nie potwierdza niskiego THD, kompresji cieplnej ani klasy masteringowej.
- **[Ustalenie — otwarte]** Modele urządzeń, zasilanie, routing sprzętowy, częstotliwości filtrów i progi ochronne pozostają niewybrane; gotowość do budowy nie została w tym rozdziale zadeklarowana.
