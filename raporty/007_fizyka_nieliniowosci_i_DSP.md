# Raport 007 — sprężyna powietrzna, Re i cele korekcji

Aktualizacja po tym raporcie: N7 wykonano i udokumentowano w
[raporcie009](009_N7_straty_nieszczelnosci.md). Użytkownik zlecił następnie
[program30badań](../PROGRAM_30_BADAN.md) i rozszerzenie puli producentów;
poniższe wyniki pozostają historycznym eksperymentem czterech modeli.

Data 2026-10-23. Zakres naukowy zgodny zU-010. Wszystkie liczby poniżej
są **obliczeniami lub scenariuszami**, bez pomiarów fizycznego prototypu.

## 1. Nieliniowa sprężyna powietrzna

Dla jednolitego ciśnienia, szczelnej sztywnej skrzyni i przyjętej przemiany
adiabatycznej modelujemy `p_abs V^γ=const`, przyγ=1,4 iP0=101325 Pa jako
parametrach scenariusza. Dodatniex zmniejsza objętość:

```text
ε = Sd X/Vb
x(t) = X cos(ωt)
Δp(t) = P0[(1−ε cos(ωt))^(−γ)−1]
F_air(t) = Sd Δp(t)
```

Nie rozwiązujemy tutaj nieliniowego ruchu membrany. Wyznaczamy siłę, którą
wytwarza gaz przy **zadanym idealnie sinusoidalnym ruchu**. Jej harmoniczne
nie sąTHD ruchu ani promieniowanego dźwięku. Rzeczywista dynamika zawiera
również silnik, zawieszenie, masę i tłumienie.

W rozwinięciu dla małegoε:

```text
H2/H1 siły ≈ (γ+1) ε/4
H3/H1 siły ≈ (γ+1)(γ+2) ε²/24
```

Zatem w tym przybliżeniuH2 siły rośnie liniowo zSd·X/Vb, aH3 kwadratowo.
Nie można tego automatycznie traktować jako rankingu głośników: różne
przetworniki mogą mieć inne dominujące nieliniowości, a siły łączą się fazowo.

Wynik FFT dla 60 l i przyjętego ruchu katalogowego:

| Kandydat | ε | H2/H1 siły powietrza [%] | H3/H1 siły [%] |
|---|---:|---:|---:|
| RSS315HF-4 |0,012267|0,7360|0,00512|
| RSS390HF-4 |0,019357|1,1615|0,01274|
| RSS315HFA-8 |0,012076|0,7246|0,00496|
| SB34SWPL76-4 |0,011450|0,6870|0,00446|

Wartości przy największym ruchu są analizą warunkową, nie zaleceniem pracy
ciągłej przyXmax. P0 iγ dobrano jawnie; małosygnałowy modułγP0 jest bliski,
ale nie identyczny zρc² w bazowym modelu. Nie dopasowywano tych stałych do wyniku.
Rzeczywiste wypełnienie i wymiana ciepła mogą zmienić przemianę gazu.

Kontrole: zgodność z szeregiem dla małego ruchu, podwojenieH2 przy podwojeniuε
oraz zgodność FFT 16384/32768 próbek. Obliczono 72 przypadki:4 modele× 6 objętości×3 amplitudy.
[CSV](../wyniki/nieliniowosc_sprezyny_powietrznej.csv),
[wykres](../wyniki/05_sprezyna_powietrzna.png).

Wniosek: litraż wpływa także na nieliniowość samego gazu. Obecny rachunek
nie określa, czy ten składnik dominuje w całkowitych zniekształceniach.

## 2. Wzrost rezystancji bez zgadywania temperatury

RozpatrzonoRe×1/1,25/1,5 przy 10 Vrms,60 l i tej samej mechanice. ZachowanoBL,
Cms,Mms iRms;Qes zwiększono proporcjonalnie do Re. Samo zwiększenieRe przy
stałymQes w naszej parametryzacji niepoprawnie rekonstruowałoby równieżBL.

| Kandydat | ZmianaSPL przy 20 Hz, Re×1,5 [dB] | Przy 40 Hz [dB] |
|---|---:|---:|
| RSS315HF-4 |−1,933|−0,607|
| RSS390HF-4 |−2,716|−0,610|
| RSS315HFA-8 |−2,151|−0,840|
| SB34SWPL76-4 |−0,655|−0,755|

To czułość odpowiedzi na Re, a nie zmierzona kompresja termiczna.
Nie obliczono temperatury odpowiadającejRe×1,5, stałych czasowych ani czasu
bezpiecznej pracy. Nie znamyRth/Cth, chłodzenia, zmian magnesu i zawieszenia.
KatalogowePe nie dostarcza tych parametrów.

[CSV72wierszy pasmowych](../wyniki/scenariusze_wzrostu_Re.csv),
[wykres](../wyniki/04_wzrost_rezystancji.png).

## 3. Cele 20/25/30 Hz a wspólny budżet ruchu i napięcia

Wykonano 216 wariantów:4 modele× 6 objętości×3 celeLT×3 częstotliwościHP.
Qt=1/√2, HP Butterwortha 2. rzędu przy 12/18/22 Hz, LP LR4 przy 80 Hz.
Ograniczenia napędu jak w raporcie 002:40 Vrms/12 Arms i katalogowy wskaźnik
sqrt(Pe·Znom). Wszystkie częstotliwości 10–200 Hz mają spełniać limity modelu.

Definicja eksperymentu: osobne sinusy o takim samym poziomie **przed**
filtrami. Maksimum tego wspólnego poziomu to:

```text
Vin,max = min_f [Vlimit(f)/|DSP(f)|], f w paśmie kontroli
```

To mocniejszy warunek niż osobna swobodna maksymalizacja każdego punktu
obwiedni z raportu 002. Nadal nie opisuje sumy wielotonowej, muzyki, limiterów
czasowych ani częstotliwości poza pasmem kontroli.

PrzykładHP 18 Hz, idealna półprzestrzeń 2π/1 m, SPLRMS:

| Kandydat / netto | Cel LT [Hz] | SPL 20 Hz [dB] | SPL 40 Hz [dB] |
|---|---:|---:|---:|
| RSS315HF-4 /60 l |20|97,87|102,32|
| RSS315HF-4 /60 l |25|97,88|104,34|
| RSS315HF-4 /60 l |30|97,66|106,00|
| RSS390HF-4 /100 l |20|101,83|106,36|
| RSS390HF-4 /100 l |25|101,85|108,39|
| RSS390HF-4 /100 l |30|101,62|110,04|

W tych konfiguracjach podniesienie celuLT uwalnia około 3,68 dB poziomu 40 Hz
w porównywanym przebiegu przy zbliżonym ograniczeniu 20 Hz. To skutek
kształtowania pasma i możliwości podniesienia wspólnego wejścia. Nie oznacza
zwiększeniaSd·Xmax ani dodatkowego bezwarunkowego headroomu muzyki.

Wymagane tłumienie cyfrowe w CSV uwzględnia maksimum samej krzywej filtrów.
Należy później dodać routing, sumowanie, rzeczywiste poziomyDAC/wzmacniacza
i weryfikację implementacji cyfrowej. Analogowy wzorzec nie jest gotowym presetem.

[Tabela216wariantów](../wyniki/cele_dsp.csv), [wykres](../wyniki/06_cele_dsp.png).
Każdy wariant sprawdzono numerycznie pod kątemXmax, napięcia i prądu na siatce.
Nie sprawdzono ciągłego maksimum przedziałowego ani dynamiki limitera.

## 4. Co wolno przyjąć do dalszego projektu

Uzasadnione: porównywaćVb razem z kosztami korekcji, zachowywać spójność
T/S podczas perturbacjiRe i rozdzielać siłę gazu odTHD. Nierozstrzygnięte:
liniowość rzeczywistych egzemplarzy, kompresja cieplna w czasie, straty
i nieszczelności, bezwzględny wynik w pokoju, finalna ochrona i użytecznySPL.

Następne działanie naukowe: model strat/nieszczelnościN7 z
[planu naukowego](../PLAN_BADAN_NAUKOWYCH.md), z kontrolą granicy szczelnej
i dodatniej mocy strat. Kontrola planu wskazała konieczność uwzględnienia
zespolonego promieniowania przecieku razem z membraną; samo obciążenie
mechaniczne nie wystarcza do prognozy całkowitegoSPL. Bez nowych zakupów
i prac nad narzędziamiCAD.
