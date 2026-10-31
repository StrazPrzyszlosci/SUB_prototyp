# Raport 072 — P24G: przedziałowa obwiednia temperatury i zabezpieczenie przy niepewności

**31.10.2026 — ukończone badanie matematyczno-numeryczne, NIE kwalifikacja bezpieczeństwa urządzenia.**
Kontynuacja raportów P24B–P24F. Punkt wyjścia `main=fde7d244b449762af0869321487335148b8e221a`.

## Cel
Zastąpić nieuzasadnione marginesy P24F (15 K, 5 K/s) **jawnie warunkową górną obwiednią** dwu-węzłowego modelu Cauer. Pokazać, kiedy obwiednia jest matematycznie poprawna w modelu dyskretnym, ile wydajności odbiera, oraz jak zawodzi po złamaniu założeń pomiaru. Jest to model zamkniętej skrzyni 80 l z nominalnym C02 Dayton RSS390HF-4, nie pomiar realnego produktu.

## Równania i zakres warunków
Stan: `Tc` i `Tm` jako przyrosty temperatury, `Pcu=Re(Tc) I_rms²`. Równania jak P24B:

```text
Tc_next = Tc + dt * (Pcu - (Tc - Tm) / Rcm) / Cc
Tm_next = Tm + dt * ((Tc - Tm) / Rcm - Tm / Rma) / Cm
```

Przyjęto prostokąt parametrów:
- `Cc ∈ [20,90] J/K`, `Rcm ∈ [0.25,1.2] K/W`,
  `Cm ∈ [500,1500] J/K`, `Rma ∈ [0.8,2.5] K/W`.
- `Re0 ∈ [2.7,3.3] Ω`, `alpha ∈ [0.0037,0.0042]/K`,
  czujnik poprawnie skalibrowany `Iind/Itrue ∈ [0.95,1.05]`.
- W rzeczywistych symulowanych obiektach P24B: korzystna, środkowa i niekorzystna termika (wszystkie wewnątrz zakresów), `Re0=3Ω`, `alpha=0.00393/K`.
- `dt=0.05s`, `120s`, trzy osobne stałe sinusy: 20, 40, 80 Hz. Modelowy tor wzmacniacza NC500MP TRS4, limit 27 A peak, idealny modelowy `Xpeak≤11.2mm`, wyciszenie po idealnie zadanym 0.25s. **Żadna z tych wartości nie jest zmierzoną implementacją limitera ani realnym progiem Daytona.**

W modelu pasywnej impedancji z P24B realna część `Zterminal` jest co najmniej `Re`, zatem:
```text
Pcu = Re |I|² <= U_rms² / Re0_min            [brak pomiaru I]
Pcu <= (I_indicated / 0.95)² * Re0_max * (1 + alpha_max * Tc_upper)
                                              [tylko przy spełnionym błędzie ±5%]
Pcu_upper = min(bound_voltage, bound_current) [dla wiarygodnego prądu]
```
Niezgodne/fizycznie niedostępne dane prądowe **nie są podstawą** ograniczenia oszacowanej mocy: pozostaje wariant napięciowy i watchdog.

Obliczamy osobno górne wartości obu stanów z mapy Eulera, maksymalizując prawą stronę względem wszystkich końców przedziałów R/C. Dla `dt<min(Cc_min·Rcm_min, Cm_min/(1/Rcm_min+1/Rma_min))` mapa jest współrzędnie monotoniczna (układ kooperatywny). W tym liniowo-ułamkowym zapisie ekstrema parametrów dla ustalonych stanów występują na końcach przedziałów, co pozwala na indukcyjne zawieranie **dowolnych stałych parametrów wewnątrz podanego prostokąta w dyskretnym modelu Eulera**, o ile moc wejściowa rzeczywiście pozostaje pod obliczoną granicą. Dodatkowa obwiednia energii `Tc≤∫Pupper dt/Cc_min` korzysta z nieujemności strat ciepła do otoczenia i temperatur. Ostateczna obwiednia to minimum dwóch górnych granic.

**Ograniczenia dowodu:** krok Eulera, kooperatywność, pasywność obciążenia, poprawny pomiar napięcia zaciskowego i prądu, zerowe warunki początkowe, wymienione zakresy R/C/elektryczne. Nie ma dowodu zawierania rzeczywistego ciągłego procesu ani nieliniowych zmian BL/Cms/Le. Zakresy nie pochodzą z pomiarów; nie są fizycznymi granicami rzeczywistego przetwornika.

## Kampania, testy i wyniki
`3 termiki × 3 częstotliwości × 5 trybów czujnika × 3 strategie = 135 przebiegów`.
Spośród nich **108** mieści się w założeniach pomiaru, a **27** wymusza błąd prądu −30% (poza zakresem), dla negatywnej kontroli. Tryby wewnątrz zakresu: nominalny, −5% prądu, brak danych od 20 do 45 s, całkowity brak danych (w obu ostatnich watchdog wycisza po 1 s). Strategie:
- Punkt odniesienia: fikcyjny odczyt `Tc−20K`, reakcja na `+55K`.
- Przedział z prądem, warunkowy próg górnej obwiedni `35K`.
- Przedział tylko z napięciem, ten sam próg `35K`.

| Strategia | Przekroczenia arbitralnego konturu +80 K / 36 | Maksymalny rzeczywisty modelowy przyrost | Średni czas wysterowania w 120 s |
|---|---:|---:|---:|
| Niepewna temperatura +55K | 3/36 | 80.175 K | 36.29 s |
| Przedział, wiarygodny I, +35K | 0/36 | 37.869 K | 23.54 s |
| Przedział, tylko U, +35K | 0/36 | 29.227 K | 1.64 s |

**Kontrola własności numerycznych:** przy spełnionych założeniach **0/108 naruszeń obwiedni temperatury** i **0/108 naruszeń nierówności ograniczającej Pcu**. Przy błędnym odczycie prądu −30%, czyli poza zakresem kalibracji, w **3/27 przebiegach** obwiednia przestała zawierać prawdziwy modelowy stan. To kontrolowana demonstracja konieczności gwarancji czujnika, nie ocena awaryjności sprzętu.

**Krytyczny kompromis:** wariant tylko z napięciem ogranicza średni czas wysterowania do 1.64s na 120s, a nawet wariant z pomiarem prądu do 23.54s. Dodatkowo próg wyciszenia jest arbitralny i nie sprawdzono długotrwałej pracy, chłodzenia po wyciszeniu ani powrotu do grania. W obecnej postaci nie jest to użytkowy limiter, tylko rygorystyczny, lecz zachowawczy test modelu.

## Co naprawdę zostało udowodnione?
- **Warunkowo w modelu dyskretnym**: przy poprawnym założeniu przedziałów i wiarygodnych wejściach Pcu, metoda generuje górny oszacowany stan termiczny. Przejście na rzeczywisty głośnik wymaga osobnego dowodu i pomiarów.
- **W skończonej próbie**: brak przekroczeń konturu +80 K dla 72 symulacji przedziałowych (36+36), ale **to nie jest matematyczny dowód utrzymania konkretnego konturu dla wszystkich sygnałów i parametrów**.
- **Nie udowodniono**: wydajnej ochrony przy długiej muzyce, poprawnego czujnika I/U na stopniu klasy D, zgodności API miniDSP, rzeczywistego czasu sprzętowego wyciszenia, termicznego bezpieczeństwa cewki ani ochrony podczas awarii zasilania.

## Decyzja R&D
Nie zastępować w elektronice P24F automatycznie modelem P24G. Przed zakupem i wdrożeniem: kalibracja rzeczywistej Re(T), Rth/Cth i odchyłki czujników, weryfikacja napięcia/prądu na *zaciskach* (wyjścia pływające klasy D!), test watchdog + niezależne MUTE/EN, dostępność API i nieblokujące opóźnienia, osobny pomiar wychylenia. Następny etap P24H: *recovery*, dopuszczalna moc średnia z uwzględnieniem chłodzenia oraz odporność na strumień muzyczny i przerwy telemetrii.

## Odtwarzanie
`node skrypty/p24g_przedzialowa_ochrona.js`

Pliki: `skrypty/p24g_przedzialowa_ochrona.js`, `wyniki/p24g_przedzialowa_ochrona_20261031.json`, niniejszy raport. Brak wymaganych bibliotek zewnętrznych. Wyniki są syntetyczne i deterministyczne.
