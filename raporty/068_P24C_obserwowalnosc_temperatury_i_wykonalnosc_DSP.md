# Raport 068 — P24C: obserwowalność temperatury z U/I i wykonalność zabezpieczeń miniDSP

**Data:** 2026-10-31. **Punkt bazowy:** main \`52ebf1de02f2211cf7c9238c65ec8ecd41d9dd67\`. **Status:** wykonana wstępna analiza strukturalna i 50 000 prób numerycznych; audyt funkcji DSP na podstawie instrukcji producenta. **Nie** jest to kwalifikacja sprzętowa ani gotowe nastawy.

## Streszczenie decyzji

1. Temperatura cewki **może być strukturalnie rozpoznawalna** z zespolonej impedancji zaciskowej \`Z=U/I\`, jeżeli znane są zimne parametry, współczynnik temperaturowy i stan modelu elektromechanicznego. Nie jest gwarantowana obserwowalność praktyczna po uwzględnieniu dryftu rezystancji toru, BL(x,T), Le(f,I), błędów fazy oraz pracy w pobliżu rezonansu.
2. W 80 l C02 przy 40 Hz nawet hipotetyczne 3% obniżenie BL podczas grzania powoduje **-53,62 K** błędu estymacji przyrostu T. Przy 150 Hz wynosi **-0,19 K** w tym *uproszczonym modelu*. Nie oznacza to, że 150 Hz jest automatycznie właściwą częstotliwością pilota — trzeba uwzględnić ograniczenia pasma, akustykę i moc diagnostyczną.
3. Instrukcje miniDSP potwierdzają PEQ/HPF i kompresor outputowy w obu Flex Eight/HTx, ale nie dowodzą dostępności pomiarów U/I *zacisków głośnika*, wykonywania dowolnego kodu użytkownika w DSP ani temperatury jako zmiennej sterującej. Wyjściowy wskaźnik RMS w Device Console pokazuje poziom sygnału w torze DSP, **nie prąd cewki**.
4. **Wariant wyłącznie miniDSP:** konserwatywny filtr subsoniczny, EQ i kompresor poziomu sygnału można skonfigurować, lecz bez odrębnego sprzężenia **nie wolno** nazywać tego gwarantowaną ochroną X(t)/T(t).
5. **Wariant docelowy do badania:** miniDSP do zwrotnic i korekcji + osobny czujnik U/I i kontroler ochrony, który ma *zweryfikowaną możliwość* szybkiego, niezależnego dla dwóch kanałów zmniejszenia wysterowania lub wyciszenia końcówek. Sam monitoring przez USB nie jest zabezpieczeniem.

## Zakres, równania, obserwowalność

Dla przyjętego liniowego P24B (\`Fs=19,5 Hz\`, \`Re0=3 Ω\`, \`Le=0,92 mH\`, \`BL=15 Tm\`, \`Xmax=14 mm peak\`, \`Sd=829,6 cm²\`, \`Mms=306 g\`), w 80 l:

\`\`\`text
Zterminal(f,T) = Re0*(1+alpha*(T-T0)) + j*2*pi*f*Le + BL^2/Zm(f,Vb)
Z = U_phasor / I_phasor                         [pomiar zespolony na zaciskach]
delta_T_hat = (real(Zhot)-real(Zcold)) / (alpha*Re0)
alpha = 0.00393 / K, Re0=3 ohm, alpha*Re0=0.01179 ohm/K
\`\`\`

Wynik różnicowy działa tylko wtedy, gdy pozostałe składniki \`Re(Z)\` i rezystancja przewodów nie zmieniły się od zimnej kalibracji. To **warunek badawczy, nie cecha gwarantowana**. W szczególności przy pomiarze U po stronie wzmacniacza, a nie na zaciskach głośnika, dolicza się przewody i wyjście wzmacniacza.

Dla termiki P24B \`x=[Tcewka,Tmotor]\`, \`Ccewka=40 J/K\`, \`Rcewka-motor=0,6 K/W\`, \`Cmotor=1000 J/K\`, \`Rmotor-otoczenie=1,5 K/W\` macierz lokalnej dynamiki:

\`\`\`text
A = [[-1/(Cc*Rcm),                1/(Cc*Rcm)],
     [ 1/(Cm*Rcm), - (1/Rcm+1/Rma)/Cm]]
C = [1, 0]       (wyjście proporcjonalne do temperatury cewki)
O = [[1,0],[-1/(Cc*Rcm),1/(Cc*Rcm)]]
det(O) = 1/(Cc*Rcm) = 0.0416666667 != 0
\`\`\`

**Wniosek ograniczony:** dwuwęzłowy model jest formalnie obserwowalny dla znanych parametrów oraz idealnego ciągłego odczytu temperatury cewki. To **nie dowodzi**, że z rzeczywistych U/I da się odtworzyć osobno nieznane \`Rth/Cth\`, stan motoru i temperaturę przy zakłóceniach. Identyfikacja parametrów termicznych wymaga niezależnych pobudzeń, danych podczas chłodzenia i walidacji pomiarowej.

## Wykonana kampania numeryczna

**Skrypt:** \`skrypty/p24c_obserwowalnosc_ui.py\`, wymaga NumPy. **Wynik:** \`wyniki/p24c_obserwowalnosc_20261031.json\`. Deterministyczny generator \`default_rng(20261031)\`; pięć częstotliwości, po 10 000 losowań na częstotliwość. Przyjęty, **niezmierzony** błąd stosunku U/I: niezależny szum względny amplitudy o odchyleniu standardowym 0,5% i szum fazy o odchyleniu standardowym 0,2° dla zimnego i ciepłego pomiaru. Cel \`delta_T=+80 K\` służy porównaniu z konturem P24B — **nie jest limitem bezpieczeństwa**. Dodatkowo osobne testy deterministyczne: dryft wzmocnienia odczytu 1%, spadek BL o 1% i 3%, oraz dryft rezystancji zewnętrznej 0,1 Ω.

| f [Hz] | Re(Z) zimna [Ω] | RMSE ΔT przy podanym szumie [K] | |błąd| p95 [K] | błąd dryftu gain 1% [K] | błąd spadku BL o 3% [K] |
|---:|---:|---:|---:|---:|---:|
| 20 | 3,3064 | 2,54 | 4,95 | +3,60 | -1,54 |
| 40 | 13,6969 | 9,13 | 17,83 | +12,42 | **-53,62** |
| 80 | 3,1903 | 2,30 | 4,50 | +3,51 | -0,95 |
| 150 | 3,0381 | 2,11 | 4,12 | +3,38 | -0,19 |
| 300 | 3,0087 | 2,19 | 4,28 | +3,35 | -0,04 |

**Uwaga:** dryft \`0,1 Ω\` pomiędzy kalibracją a pomiarem daje błąd **8,48 K** niezależnie od f dla tej różnicowej metody. Wspomniane p95 jest empirycznym 95. percentylem bezwzględnego błędu z **przyjętego** rozkładu Monte Carlo, a nie 95% gwarancją urządzenia.

Różnicowy pomiar może usunąć **stały** błąd BL i toru, ale nie usuwa ich **zmian** w czasie. Przy dużym poziomie sygnału BL(x), nieliniowa indukcyjność i SEM ruchu mogą zmieniać estymator nawet bez grzania. Również problem niskiego prądu pomiarowego i kwantyzacji dla częstotliwości poza pasmem nie został tutaj zasymulowany. Brak sygnału diagnostycznego, przerwa w pomiarach albo nietypowa treść muzyczna może uczynić T chwilowo **nieobserwowalną praktycznie**.

### Warunki odtwarzania

\`\`\`bash
python3 -m pip install numpy
python3 skrypty/p24c_obserwowalnosc_ui.py > /tmp/p24c_obserwowalnosc.json
\`\`\`

Kontrolne asercje do następnego etapu: (1) przy idealnych parametrach \`delta_T_hat=80 K\`; (2) wszystkie wyniki skończone; (3) zero błędu mechanicznego gdy brak zmian BL/Le/Cms; (4) test zmiany \`Vb/Qms\` i błędów fazy poza rozkładem normalnym; (5) zbieżność oceny dla liczby próbek \`N\`.

## Audyt funkcjonalny miniDSP na podstawie materiałów producenta

Źródła pierwotne (sprawdzone 31.10.2026):
- [Flex Eight — tor sygnałowy](https://docs.minidsp.com/product-manuals/flex-eight/signal-flow/index.html) oraz [kompresor](https://docs.minidsp.com/product-manuals/flex-eight/dsp-reference/compressor.html).
- [Flex Eight — wyjścia i wskaźnik poziomu](https://docs.minidsp.com/product-manuals/flex-eight/signal-flow/output-channels.html).
- [Flex HTx — tor sygnałowy](https://docs.minidsp.com/product-manuals/flex-htx/signal-flow/) oraz [kompresor](https://docs.minidsp.com/product-manuals/flex-htx/dsp-reference/compressor.html).
- [Flex HTx — wyjścia i wskaźnik poziomu](https://docs.minidsp.com/product-manuals/flex-htx/signal-flow/output-channels.html).

| Funkcja | Flex Eight | Flex HTx | Stan dowodu i znaczenie |
|---|---|---|---|
| Zwrotnica HPF/LPF, PEQ | TAK | TAK | Dla filtracji i konserwatywnego ograniczenia pasma, a nie gwarancji Xmax |
| Kompresor per kanał z threshold/ratio/attack/release | TAK | TAK | Kontrola **poziomu sygnału DSP**, bez pomiaru mechaniki/termiki |
| Mute, gain, delay per kanał | TAK | TAK | Dostępne w interfejsie; niezbadana opóźniona automatyka i fail-safe |
| Wskaźnik poziomu RMS sygnału DSP | TAK | TAK | Nie mierzy fizycznego U, I na zaciskach ani temperatury |
| Pomiar napięcia i prądu na zaciskach subwoofera | NIE WYKAZANO | NIE WYKAZANO | Wymaga osobnego układu pomiarowego |
| Własny kod obserwatora Cauer / dynamiczne wstrzykiwanie danych U/I | NIE WYKAZANO | NIE WYKAZANO | Nie przyjmować możliwości instalacji własnego algorytmu w firmware |
| Gwarantowany limiter X_peak, T_coil z rzeczywistym sprzężeniem | NIE WYKAZANO | NIE WYKAZANO | Oracle P24B nie jest dostępną funkcją |
| Symetryczne wyjście 4 Vrms | NIE | TAK | Odrębna cecha elektryczna, nie ochrona |

**Kwestia otwarta:** oprogramowanie Device Console udostępnia sterowanie konfiguracją, ale bez dowodu udokumentowanego, deterministycznego API, czasu aktualizacji oraz bezpiecznej ścieżki wprowadzania \`gain/mute\` nie wolno projektować na nim krytycznej pętli ochronnej.

## Architektury do decyzji

**A — tylko miniDSP + płytkowy moduł końcówki:** zwrotnica, HPF, PEQ i konserwatywny kompresor. Wykonalne jako *wstępna ochrona sygnału* po kalibracji poziomów i pomiarach wyjściowych. **Brak potwierdzonej zamkniętej pętli X/T**. Nie traktować fabrycznych zabezpieczeń wzmacniacza przed przetężeniem lub przegrzaniem jako ochrony membrany/cewki.

**B — miniDSP + zewnętrzny kontroler ochrony:** dwa niezależne pomiary U/I wykonane po stronie obciążenia i dwa niezależne sterowane tory ograniczania/mute, powiązane ze sprawdzoną dynamiką końcówek. Kontroler mierzy opóźnienie end-to-end, ma watchdoga, utratę czujnika wykrywa jako uszkodzenie, a nie jako temperaturę 0 K. W razie awarii ogranicza/wstrzymuje wysterowanie w niezależnej ścieżce sprzętowej. To propozycja architektury, **nie zakończony projekt elektryczny**.

**C — otwarte programowalne DSP + analog front end U/I:** potencjalnie najlepsza droga do prawdziwej implementacji P24B, ale trzeba potwierdzić liczbę kanałów, ADC, dostęp do sygnału powrotnego, opóźnienie, pamięć, stabilność i koszt całego toru ośmiokanałowego. Nie wybrano modułu ani chipu.

### Bramka P24C — wymagane dowody przed nastawami

1. **Pomiar zimnego Re i Z(f)** rzeczywistego egzemplarza w projektowanej skrzyni oraz czteroprzewodowe oszacowanie dodatkowej rezystancji.
2. Kalibracja **obu torów U/I** oraz fazy na wzorcowym obciążeniu, z oszacowaniem dryftu i minimalnego SNR; pomiar na odpowiednich zaciskach (ostrożnie z mostkowymi/floating wyjściami klasy D).
3. Próba **grzanie–chłodzenie** z odniesieniem do zmierzonej rezystancji cewki; odrębna identyfikacja Rth/Cth, BL/Le i zależności od wymuszenia. Nie zakładać, że termometr na koszu mierzy natychmiast temperaturę drutu.
4. Zaprojektowanie **estymatora z przedziałem niepewności**, kontrolą innowacji i degradacją do trybu bezpiecznego przy utracie sygnału, błędach modelu lub braku pobudzenia.
5. Test czarnej skrzynki miniDSP i wzmacniacza: próg i obwiednia kompresora, clipping, peak vs RMS, opóźnienie ataku i release, zachowanie po restartach, utracie źródła i zmianie głośności/presetu.
6. Dla dwóch subwooferów oddzielne ścieżki błędu i awaryjne wyciszenie. Dopiero po pomiarowym określeniu granic uszkodzenia i tolerancji modelu można zatwierdzić wartości limiterów.

**Stan:** P24C nie zamyka sprawy bezpieczeństwa. Wniosek projektowy jest **warunkowy**: miniDSP stanowi potwierdzony procesor filtrów i kompresji sygnału, a dla ochrony zależnej od temperatury/wychylenia potrzebny będzie potwierdzony tor sprzężenia i regulator lub ograniczenie osiągów na podstawie zmierzonych, konserwatywnych obwiedni.
