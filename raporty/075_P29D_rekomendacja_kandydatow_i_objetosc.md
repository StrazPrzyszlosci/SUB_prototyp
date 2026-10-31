# Raport 075 — P29D: czy zmienia się faworyt? Pojemność netto 75–150 l przy nowych kandydaturach

**31 października 2026.** Badanie porównawcze na zamrożonych parametrach repozytorium P22C, po kampaniach P24B–P24I. **Wniosek: C02 Dayton RSS390HF-4 pozostaje warunkowym faworytem.** Nie ma nowego zwycięzcy po rozszerzeniu puli do 34 modeli / 35 konfiguracji. 33 konfiguracje przeszły liniowy przesiew, 2 są wstrzymane (SUPRAVOX / EMS). Uwaga: nie wykonywaliśmy nowych pomiarów fabrycznych ani kalibracji cieplnej dla konkurentów.

## Rzeczywisty brief i decyzja
Dwa niezależne subwoofery zamknięte, dwa monitory 3-drożne (łącznie 8 kanałów centralnego DSP); napęd klasy D w formie modułów PCB, cel niski bas 20–40Hz, limit **pełnej głębokości z elementami wystającymi 500 mm**; warianty netto 75/80/100/120/150l.

**Rekomendacja do badań inżynierskich:** projektuj obudowę z regulacją około **100/120/150 l, start ~120 l**. Dokładny korpus 880×480×500mm z raportu 054 jest koncepcją przed zatwierdzeniem maskownicy, terminala, połączeń, kierunku montażu i wyporności. 480 mm głębokości korpusu zostawia jedynie 20 mm zewnętrznego budżetu wystawania; potrzeba nowego rysunku CAD/kolizji. Mniejsza objętość 75/80 l to wariant wymuszony przestrzenią, nie nowy preferowany punkt eksperymentu.

## Nowy audyt 225 przypadków i F3
Zamrożono pięć kandydatur P22C: C02 RSS390HF-4, C11 RSS390HE-22 w szeregu, C06 STX W.32.800.8.FCX, N07 PHL 6301MNd i N05 PURIFI PTT10.0X04-NAB-01.

**Siatka:** 5 głośników × 5 objętości × 3 f (20/40/80Hz) × 3 hipotetyczne budżety mocy strat miedzi (50/100/200W) = **225 obliczeń sinusoidalnych**. Przyjęto jednakowe ograniczenie portu źródła 40Vrms/12Arms i Rs=0,0026Ω, granicę katalogowego Xmax szczytowego oraz zespoloną impedancję małosygnałową. To punkt porównania, **nie realna charakterystyka mocy modułu przy 8Ω**. Mms i BL brakujące w kartach C11/C06 odtworzono z tożsamości T/S; dla C02/N07/N05 przyjęto zamrożone wartości z P22C.

Dla układu idealnie zamkniętego: `Qtc = Qts sqrt(1+Vas/Vb)`, `fc=Fs sqrt(1+Vas/Vb)`, a F3 wyznaczono przez rozwiązanie charakterystyki filtrującej drugiego rzędu. Nie uwzględniono wypełnienia, strat skrzyni, EQ, pokoju ani zniekształceń.

### Wpływ objętości na C02

| Objętość netto | Qtc | Idealne F3 | Moc strat cewki przy Xmax i 20Hz | Idealny SPL 20Hz przy 50W Pcu | Idealny SPL 40Hz przy 50W Pcu |
|---|---:|---:|---:|---:|---:|
| 75 l | 0.839 | 33.06 Hz | 214.1 W | 95.54 dB | 113.19 dB |
| 80 l | 0.820 | 32.83 Hz | 188.1 W | 96.10 dB | 113.18 dB |
| 100 l | 0.758 | 32.30 Hz | 120.3 W | 98.04 dB | 113.07 dB |
| 120 l | 0.714 | 32.15 Hz | 83.7 W | 99.62 dB | 112.41 dB |
| 150 l | 0.666 | 32.26 Hz | 53.9 W | 101.53 dB | 110.80 dB |

**Interpretacja:** blisko 100–120l małosygnałowe F3 jest prawie płaskie; przy 20Hz większa skrzynia wymaga jednak znacznie mniejszej mocy strat cewki do osiągnięcia tej samej amplitudy ruchu. Zmiana 80→120l redukuje ją z 188,1 do 83,7W (w modelu ustalonej sinusoidy). Przy przyjętym limicie strat 50W nominalny idealny SPL przy 20Hz rośnie o **3.52 dB**, ale przy 40Hz może się nieco obniżyć — nie jest to przewaga bezwarunkowa. Wartości 50W nie wolno uznać za bezpieczną temperaturę!

### Porównanie pięciu kandydatur w 120 l, model 50W Pcu
| Kandydat | Katalogowy Vd jednostronny [cm³] | Idealne Qtc | Idealne F3 [Hz] | Modelowy 20Hz/2π/1m [dB] |
|---|---:|---:|---:|---:|
| C02 Dayton RSS390HF-4 | 1161 | 0.714 | 32.1 | 99.62 |
| C11 Dayton RSS390HE-22 series | 2171 | 0.650 | 40.1 | 96.30 |
| C06 STX W.32.800.8.FCX | 737 | 0.532 | 45.8 | 97.90 |
| N07 PHL 6301MNd | 915 | 0.381 | 119.6 | 97.08 |
| N05 PURIFI PTT10.0X04-NAB-01 | 531 | 0.427 | 60.3 | 95.06 |

**F3 dla PHL przy niskim Qtc jest bardzo wysokie bez EQ**: ten zawodowy 15-calowy przetwornik nadal może być korygowany w DSP, ale potrzeba osobnego badania zapasu elektrycznego, ruchu i zniekształceń. Duża moc AES PHL nie oznacza większego poziomu przy 20Hz niż C02.

**Przypadek zmiany rankingu w wąskim kryterium:** przy 80 l / 20Hz / umownym Pcu 50W STX C06 uzyskuje 96,89 dB, a C02 96,10 dB w prostym modelu. Nie jest to powód do ogłoszenia STX nowym zwycięzcą: przy 40Hz i w rozległej kampanii odporności P29C C02 pozostaje mocny, a ceny i THD/IMD nie były porównane. Różnice dla 75/80l wymagają osobnej pełnej kampanii odporności, jeśli wymiar skrzyni stanie się priorytetem.

## Co już wiemy z wcześniejszych badań i nie wolno stracić
1. **Raporty 053–055 (P29A–C):** modelowa najgorsza wartość 120l przy Pcu 50W sprzyja C02; pułapy 27–86W wskazują C02, a 87–200W wskazują C11. Przejście 86,813W nie jest fizyczną granicą bezpieczeństwa cewki.
2. **Raport 055:** pierwszy litr spełniający margines 0,2dB wobec plateau P29C to 99l; plateau od ~102l dla tego metrycznego testu. 120l jest wyborem do regulowanego prototypu, nie optimum matematycznym.
3. **Raporty 067–074:** C02 posiada pogłębione, lecz nieskalibrowane analizy obserwacji temperatury i dynamicznej ochrony; nie zweryfikowano ograniczników miniDSP ani nie porównano rzeczywistych Rth/Cth 34 głośników.
4. **Nowa pula:** N01 GPA416-8B, N02 VOLT RV3863, N03 SUPRAVOX (HOLD), N04 EMS (HOLD), N05 PURIFI (już obecny wcześniej), N06 Kartesian, N07 PHL6301MNd, N08 ETON, N09 Davis. Nowych *unikalnych* produktów przybyło osiem, nie dziewięć.

## Następne decyzje badawcze
**A.** Jeśli dwie duże skrzynie mieszczą się przy monitorach: zachować 120l start, wkłady 100/120/150l; zintegrować wręgi, matę, front i faktyczny obrys ≤500mm.

**B.** Jeśli brak miejsca na ~120l netto: sprawdzić 100l jako kompromis (przed 80l). Jeśli tylko 75–80l, ponownie porównać STX i C02 z rzeczywistą termiką/THD, a nie przyjąć dawny ranking 120l.

**C.** Klucz do zmiany faworyta: realnie dopuszczalne straty cewki przy sygnale wielotonowym, BL(x), Cms(x), Le(f,I), THD i kompresja, długotrwałe U/I, gabaryt i **kompletny koszt pary**. Nie ma jeszcze końcowego głośnika, wzmacniacza ani bezpiecznej nastawy. Testy P24 nie są certyfikacją.

## Reprodukcja
`node skrypty/p29d_5_finalistow_75_150l.js`

Dane: `wyniki/p29d_5_finalistow_75_150l_20261031.json`. Obliczenia numeryczne i pierwsze dwa świadki C02 20Hz/80l i /120l porównano z zamrożonym raportem P22C z tolerancją 0,5W; odtwarzanie jest sprawdzalne, nie fizycznie zwalidowane.
