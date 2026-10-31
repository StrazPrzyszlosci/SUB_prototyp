# Raport 067 — P24B: nagrzewanie cewki w czasie, Re(T), DSP i dwa niezależne ograniczenia X/T

**31 października 2026. Status: wykonano 729 jawnie warunkowych symulacji. Nie jest to pomiar, prognoza rzeczywistego uszkodzenia, fabryczny model Daytona ani gotowy limiter miniDSP.**

## Pytanie badawcze

Poprzedni P22C obejmuje zespoloną impedancję Z(f), oddzielne limity wyjścia DSP, napięcia, prądu i poprawne **szczytowe** Xmax. Nie rozwiązuje jednak odpowiedzi termicznej na 5 sekund dźwięku, 25 sekund przerwy, ani na 180 sekund ciągłego sinusa. W P15A istniała ogólna dwuwęzłowa topologia Cauer; P24B sprzęga ją **w każdej chwili** z rzeczywistym stanem rezystancji elektrycznej cewki, wejściem P22C i mechaniczną obwiednią. W ten sposób bada, czy ochrona wychylenia może zastąpić ochronę termiczną.

## Model i domena ważności

C02 Dayton RSS390HF-4, uproszczony stan T/S z briefu: Fs=19,5 Hz, Re(25°C)=3Ω, Le=0,92mH, Mms=306g, BL=15Tm, Vas=212l, Sd=829,6cm², Xmax jednostronne szczytowe 14mm. **Współczynnik temperaturowy α=0,00393/K jest przyjętym scenariuszem dla miedzi**, nie pomiarem konkretnego uzwojenia; realny drut/klej/czujnik mogą mieć inną charakterystykę.

Przyrosty temperatury względem otoczenia (T_c, T_m):
\`Re(T_c)=Re0*(1+α*T_c)\`,
\`C_c dT_c/dt=P_cu(T_c,U,f,Vb)−(T_c−T_m)/R_cm\`,
\`C_m dT_m/dt=(T_c−T_m)/R_cm−T_m/R_ma\`,
\`P_cu=Re(T_c)*|I_RMS(T_c,U,f,Vb)|²\`.

\`I_RMS\` wyliczono z \`Z_terminal=Re(T_c)+jwLe+BL²/Zm(Vb,f)\` oraz oporu wyjściowego końcówki. \`Zm\` ma liniową sprężystość gazu w skrzyni zamkniętej. **Nie** uwzględniono zmian BL, Cms, Le przy T i x, zjawisk wirnikowych, chłodzenia ruchem powietrza, wypełnienia, sprzężenia paneli P21G, promieniowania w pokoju, muzyki wielotonowej, termicznego foldbacku końcówki ani sieci 230V.

### Zamrożone, całkowicie hipotetyczne zestawy Cauer

| Scenariusz | C cewki [J/K] | R cewka–motor [K/W] | C motor [J/K] | R motor–otoczenie [K/W] |
|---|---:|---:|---:|---:|
| korzystny | 90 | 0,25 | 1500 | 0,8 |
| środkowy | 40 | 0,6 | 1000 | 1,5 |
| niekorzystny | 20 | 1,2 | 500 | 2,5 |

**Nie są to producentowe parametry RSS390HF-4.** Nie wolno wprowadzać wyliczonego wzrostu temperatury do karty katalogowej jako pomiaru.

## Siatka wykonanych obliczeń

3 objętości **75/80/120 l** × 3 częstotliwości **20/40/80 Hz** × 3 tory wzmacniacza i DSP (**ICEpower 300AS1 RCA 2V**, **NC500MP RCA 2V**, **NC500MP symetryczne TRS 4V**) × 3 hipotetyczne zestawy Cauer × 3 sygnały (180s ciągły, 5s sygnału/25s przerwy, 1s/9s) × 3 strategie ochrony = **729 trajektorii**.

Wykonano **628826 kroków** w siatce \`dt=0,2 s\`; mniej niż 729×900, ponieważ **40 niekontrolowanych lub wyłącznie mechanicznie kontrolowanych** trajektorii zatrzymano przy **umownym +200 K**. To limit dziedziny modelu, **nie przewidywany próg awarii ani fabryczna temperatura uszkodzenia**.

Trzy strategie:
1. **Bez ochrony głośnika:** tylko napięcie, prąd i gain opisany w przyjętym modelu wzmacniacza; może naruszać szczytowe Xmax.
2. **Tylko X:** idealny modelowy limit \`X_peak≤0,8*Xmax\` dla sinusa, bez kontroli temperatury. Wartość 0,8 to arbitralny margines do analizy, nie zalecenie do ustawienia.
3. **X+T oracle:** powyższy limit plus **idealny odczyt przyrostu temperatury cewki w każdym kroku** i matematyczny predyktor jednego kroku \`T_c,next≤80 K\`. **+80 K jest tylko konturem diagnostycznym**, nie potwierdzonym bezpiecznym wzrostem T. Nie ma dowodu możliwości realizacji obserwatora w Flex Eight/HTx ani uwzględnienia jego opóźnienia, błędów parametrów i przetwarzania w DSP.

Dane pełnej kampanii [CSV 729 trajektorii](../wyniki/p24b_kampania_729.csv), [konfiguracja](../dane/konfiguracje/p24b_czasowa_termika_20261031.json), [skrypt odtworzenia](../skrypty/p24b_czasowa_termika_cewki.py) oraz [podsumowanie](../wyniki/p24b_podsumowanie.json).

## Najważniejsze rzeczywiście policzone wyniki

### 80 l, 80 Hz, środkowy scenariusz Cauer, sygnał ciągły

| Wzmacniacz/ochrona | Maks. przyrost T cewki | Obciążenie mechaniczne | Interpretacja |
|---|---:|---:|---|
| ICEpower 300AS1, bez ochrony termicznej | +156,45 K po 180 s | Xpk ok. 3,46 mm | Xmax nie jest aktywną barierą; liczy się grzanie |
| NC500MP RCA 2V, bez ochrony termicznej | +178,13 K po 180 s | Xpk ok. 3,77 mm | Większy napęd nie zwiększa w tym miejscu X do 14 mm, ale podnosi straty cewki |
| NC500MP TRS 4V, bez ochrony termicznej | **+200 K po 64 s — stop numeryczny** | Xpk ok. 4,48 mm | Sama ochrona X nie pomaga, bo Xpk daleko od Xmax |
| NC500MP TRS 4V, idealna kontrola X+T 80K | **+80 K** po ograniczeniu sygnału | Xpk≤4,48 mm | Wymaga średnio \`−5,04 dB\` skutecznego poziomu *napięcia na źródle* w aktywnych okresach; to nie jest dokładnie redukcja SPL |

![P24B — przebieg grzania przy 80Hz](../wyniki/108_P24B_czasowe_nagrzewanie_80Hz.svg)

[Przebiegi po 1 s dla tego przypadku](../wyniki/p24b_profil_80Hz.csv). W przypadku niechronionym przerwanie wykresu przy +200K jest świadomą barierą zakresu modelu.

### Ten sam model, 80 l, 20 Hz, NC500MP TRS 4V

Bez ochrony liniowy model daje **maksymalnie 19,20 mm szczytowego wychylenia**, przekraczając referencyjne 14mm. Z samą idealną ochroną X≤11,2 mm uzyskano wzrost cewki aż **+125,73K** po 180s. Przy dodatkowej, umownej granicy termicznej +80K oba hipotetyczne ograniczenia były spełnione, ze średnim ograniczeniem napięcia źródła \`−4,31dB\`. **Poza zakresem Xmax ani powyżej znacznego wzrostu T model nie przewiduje poprawnie THD i realnego uszkodzenia**.

### Jak zmienia się efekt przy impulsach

Dla 80l/80Hz/300AS1, środkowego Cauer: **180s ciągłego sinusa → +156,45K**, ale ciąg **5s sygnału / 25s przerwy → +48,62K** po okresie badania. Porównanie obrazuje, dlaczego ochrona cieplna musi uwzględniać czas/duty cycle, a nie tylko stałą moc lub napięcie RMS.

### Audyt fizyczny i numeryczny

- W każdym kroku sprawdzono bilans energii Cauer: zmiana magazynowanej energii = \`dt*(P_cu−T_motor/Rma)\`. Maksymalna względna reszta **4,43×10⁻¹⁶** (to test spójności równań, nie niezależna walidacja parametrów).
- **108/243** przypadków bez ochrony głośnika naruszało referencyjny szczyt Xmax przynajmniej przez jeden krok. Ograniczona dziedzina liniowa oznacza, że ekstrapolacji tego zachowania nie można uznać za prognozę rzeczywistego ruchu poza Xmax.
- **40/729** trajektorii osiągnęło umowny stop modelu przy +200 K: 22 bez ochrony, 18 z samą ochroną X, **0** w idealnym scenariuszu X+T.
- Pole \`time_at_or_above_hypothetical_80K_s\` w CSV oznacza **czas na lub nad konturem +80K**; dla idealnego regulatora stan może pozostawać dokładnie na konturze, więc dodatnia wartość nie oznacza jego naruszenia.
- Zmiana kroku z **0,2s na 0,1s**: przy 80l/40Hz/NC500MP RCA 2V, środkowym Cauer, max przyrost T w trzech strategiach różnił się o około 0,0013% w obu obliczeniach. Dodatkowe niezależne przeliczenie 80l/80Hz/NC500MP TRS4: stop numeryczny nastąpił przy 64,0s dla obu siatek; max zanotowany wzrost 200,082K / 200,033K, a ograniczenie idealne utrzymywało +80K w obu siatkach. **To kontrola kroku, nie parametryczna walidacja rzeczywistej cewki.**

## Decyzje projektowe i otwarte bramki

1. **Potrzebne są niezależne bariery mechaniczna i termiczna.** Jedna skutecznie nie zastępuje drugiej; warunki graniczne zależą od częstotliwości, Vb, DSP, rzeczywistego Z(f) i widma programu.
2. Dostępne parametry T/S i moc 500 W RMS nie pozwalają obliczyć prawdziwej temperatury z powyższą dokładnością. **Nie ustalać na podstawie P24B limitera +80K, 11,2mm czy 500W dla sprzętu.**
3. Zmierzyć \`Re(T)\` w kontrolowanym nagrzewaniu i chłodzeniu, rezystancję na zimno, zmienne chłodzenie przy ruchu membrany, efektywny impuls cieplny/pomiary \`Rth,Cth\`; użyć pulsu diagnostycznego i zarejestrować krzywą wygaszania. Ważna jest termiczna identyfikowalność i niepewność.
4. Dla Flex Eight/HTx sprawdzić dostępność telemetrii i możliwości wprowadzenia sprzężenia \`U(t)/I(t)/T(t)\` do toru ograniczającego; jeśli brak, oddzielny kontroler przed wzmacniaczem/sprzężenie z zewnętrznym monitorowaniem oraz niezależna sprzętowa ochrona.
5. Wymagać testów prawdziwego clippingu i ograniczeń czasowych ICEpower/Hypex oraz zasilania 230V w zatwierdzonej obudowie, zgodnie z dokumentacją producentów, przed doborem modułu.
6. Dopiero po integracji mechaniki P21G/P21H, nieliniowego BL/Cms, pomiarów rzeczywistego przetwornika i dwukanałowego DSP przeprowadzić końcowy ranking opłacalności. **Dayton RSS390HF-4 nadal jest wstępnym faworytem, a nie zatwierdzonym wyborem.**
