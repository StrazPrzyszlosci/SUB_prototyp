# Raport 114 — P45: czy dwa tanie przetworniki 12″ zastąpią jednego Daytona?

**Stan:** 2 listopada 2026. **Typ:** rzeczywiste obliczenia modelu liniowego 0D na producentowych danych T/S; brak pomiarów prototypu, nie wyznaczono THD, temperatury ani bezpieczeństwa konstrukcji.

## Pytanie i kryterium

Czy ekonomiczny wariant dwóch identycznych 12-calowych przetworników może zapewnić odpowiedni zapas 20–80 Hz względem Dayton RSS390HF-4 w tym samym zamkniętym litrażu i przy uczciwym wspólnym budżecie strat miedzi? Nie należy porównywać samej ceny, katalogowych mocy RMS ani 2 głośników z jednym przy różnych ograniczeniach.

## Źródła i dane

- Dane T/S: istniejąca `dane/przetworniki/pula_rozszerzona.json` (C02, C05, C06, C04, C23, C01, C03). Nie dopisywano nowych modeli do liczby 39.
- C05 STX W.32.500.8.MC_v2 — producent [215 zł i geometria](https://stx.pl/w-32-500-8-mc.html), Fs 24 Hz, Qes 0,30, Qms 2,48, Vas 199 l, Sd 491 cm², Xmax 7,5 mm jednostronnie z katalogowych 15 mm p-p, nominalnie 8 Ω; głębokość kosza 133 mm.
- [STX W.32.800.8.FCX](https://stx.pl/category/glosniki-niskotonowe) — 990 zł/szt. w katalogu; dwa egzemplarze nie należą do najtańszej gałęzi.
- [Dayton RSS390HF-4 — oferta odniesienia 1613,33 zł](https://loudspeakershop.eu/glosnik-dayton-audio-rss390hf-4-15-reference-sub-p-7660.html). Ceny zmienne, dostępność/transport nie gwarantowane.
- Model T/S ze źródeł projektowych, test równowagi mocy dla każdego punktu. Wszystkie przedziały są **hipotetyczne**, nie fabryczne tolerancje ani zmierzone temperatury.

## Metoda i 12 870 wyników

13 układów × 5 obudów netto (75/80/100/120/150 l) × 11 osobnych sinusów (20–100 Hz) × 3 założone **łącz­ne** budżety strat miedzi (50/100/200 W) × 2 udziały katalogowego Xmax (70%/100%) × 3 mnożniki Re (1/1,2/1,4), razem **12 870**. Napięcie maksymalne 40 V RMS, prąd maksymalny 12 A RMS, a w dwukanałowym układzie osobno 12 A RMS na kanał. Limity Pcu nie są podawanymi przez producenta limitami pracy ciągłej; tu służą tylko równej konkurencji.

Model wykorzystuje spójne Fs/Qes/Qms/Vas/Sd/Re/Le i mechaniczne równania wejściowego modelu projektu. Dla normalnej, zgodnej fazowo pary identycznych głośników: Mms'=2Mms, Cms'=Cms/2, Rms'=2Rms, Sd'=2Sd. Dla idealnej pary izobarycznej Sd'=Sd. Dla cewek połączonych w szeregu Re'=2Re, Le'=2Le, BL'=2BL; dla równoległych Re'=Re/2, Le'=Le/2, BL'=BL. Gorące Re mnoży się **po** doborze nominalnego BL, co jest tylko analizą wrażliwości. Oba głośniki traktowane są jako idealnie zgodne i synchroniczne.

Dla każdego punktu liczono impedancję zespoloną, RMS prądu i prędkości, maksymalne **szczytowe** wychylenie, rzeczywistą moc w Re, moc tracona w mechanicznych Rms i SPL idealnego monopola w półprzestrzeni 2π/1 m. Niezależny bilans P_we=Pcu+Rms·|v|². Maksymalna względna reszta bilansu: **8.546e-16**; każdy punkt spełnia przyjęte ograniczenia.

## Wyniki porównania (120 l, 20/40 Hz, 50 W łącznego Pcu, Re×1, pełny katalogowy Xmax)

| Konfiguracja | Nominalna impedancja | 20 Hz, dB | 40 Hz, dB | Ograniczenie 20 Hz |
|---|---:|---:|---:|---|
| D15_C02 | 4 Ω | 99.62 | 112.46 | Cu_assumed |
| STX500_SINGLE_C05 | 8 Ω | 91.91 | 103.95 | Xcatalog |
| STX500_2_PAR | 4 Ω | 97.30 | 109.97 | Cu_assumed |
| STX500_2_SER | 16 Ω | 97.30 | 108.87 | Cu_assumed |
| STX500_2_DUALAMP | 8 Ω | 97.30 | 109.97 | Cu_assumed |
| STX500_2_ISOBARIC_PAR | 4 Ω | 91.91 | 103.95 | Xcatalog |
| STX800_2_PAR | 4 Ω | 97.92 | 113.92 | Cu_assumed |
| STX800_2_SER | 16 Ω | 97.92 | 107.90 | Cu_assumed |
| SB34SWPL76_2_PAR_LOW2OHM | 2 Ω | 103.35 | 110.57 | Xcatalog |
| LAB12_2_PAR_LOW3OHM | 3 Ω | 98.66 | 115.02 | Cu_assumed |
| LAB12_2_SER | 12 Ω | 98.66 | 109.90 | Cu_assumed |
| DAYTON12HF_2_PAR_LOW2OHM | 2 Ω | 98.15 | 115.61 | Cu_assumed |
| DAYTON12HFA_2_PAR | 4 Ω | 97.88 | 112.96 | Cu_assumed |

**Przykłady wrażliwości przy 20 Hz:** STX500 2× równolegle 97.30 dB w wariancie podstawowym, 94.83 dB dla x≤0,7Xmax i Re×1,4. Dayton odpowiednio 99.62 i 98.15 dB. Różnice te nie są zmierzonymi zniekształceniami i nie pozwalają wyznaczyć bezpiecznej temperatury cewki.

**Izobaryczny:** STX500_2_ISOBARIC_PAR: 91.91 dB przy 120 l i 20 Hz; jedna promieniująca membrana. Izobaryczny nie zapewnia +6 dB z samego podwojenia koszy. Zastosowanie izobaryczne ma sens przede wszystkim wtedy, gdy naprawdę trzeba zmniejszyć skrzynię — podlega osobnemu modelowi mechaniczno-termicznemu komory sprzęgającej.

## Ekonomia i geometria

W cenach ofertowych samych głośników 2× C05 = **430 zł**, C02 = **1613,33 zł**, różnica **1183,33 zł**. Dwa C06 kosztują **1980 zł**, więc nie są ekonomicznym zamiennikiem według przyjętych ofert. Dodatkowy koszt wycięcia drugiego otworu, pierścieni, przewodów, większego frontu, chłodzenia i ewentualnie drugiej końcówki nie został policzony. Warunek ekonomiczny: dodatkowe koszty pary mniejsze niż 1183,33 zł, ale również spełnione progi jakościowe, nie tylko niższa cena.

Kontrola **wyłącznie 2D**: front 1020×500 mm, dwa kołnierze C05 o Ø332 mm, osie X=245 i 775 mm, Z=250 mm. Od krawędzi po 79 mm poziomo i 84 mm pionowo, między kołnierzami 198 mm. Otwory koszy Ø284 mm, BCD Ø316 mm. **To nie jest dowód, że dwie masy i wręgi P30E nie kolidują, nie ma modelu trójwymiarowego ani pozwolenia na CNC.** Należy przeliczyć bilans *rzeczywistego* litrażu netto po dwóch koszach.

## Interpretacja praktyczna i następna bramka

1. Najtańsza para STX 12″ jest poważnym **kandydatem kosztowym**, lecz ma sumaryczne katalogowe Vd ≈0,7365 l wobec Daytona 1,1614 l. Samo Vd stanowi wskaźnik granicy wychylenia, nie zmierzone THD.
2. 2×8 Ω w równoległym połączeniu daje nominalnie 4 Ω i może pracować na jednym kanale kompatybilnej końcówki; 16 Ω szeregowo szybciej wykorzystuje budżet napięcia; dwa kanały mocy są osobnym kosztowo wariantem. Nie wolno utożsamiać zgodności impedancji nominalnej z bezpieczeństwem rzeczywistego modułu D.
3. **Przy 20 Hz model nie dowodzi równoważności z Daytonem**, szczególnie po zredukowaniu budżetu wychylenia do 70%; ale znacząca różnica ceny uzasadnia dalsze prace.
4. Przed rekomendacją konieczne: pełna charakterystyka BL(x), Cms(x), Le(x,f), Re(T), THD/IMD pod tym samym SPL, wzmacniacz i zabezpieczenia X/T, mechanika frontu z dwoma otworami, koszt całego subwoofera i dla docelowych dwóch subwooferów osobna optymalizacja ustawienia w pokoju. Nie traktować katalogowej mocy 500 W C05 jako dopuszczalnego Pcu.

Dane: [konfiguracja i źródła](../dane/konfiguracje/p45_dual12_20261102.json), [pełne agregaty](../wyniki/p45_dual12_odpornosc_20261102.json), [715 przypadków przekrojowych](../wyniki/p45_dual12_bazowe_715.csv), [skrypt z możliwością wygenerowania wszystkich 12 870 przypadków](../skrypty/p45_dwa_tanie_12_robustnosc.js). Archiwa P43 (akustyka) i P43-K/P44-K (konstrukcja) pozostają nietknięte.
