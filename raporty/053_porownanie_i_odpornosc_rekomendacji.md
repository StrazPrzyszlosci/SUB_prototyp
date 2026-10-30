# Raport 053 — P29A/B: porównanie, niepewność i sygnały

Data: 2026-10-30. **Rekomendacja eksperymentu, nie ranking zmierzonej jakości.**

## Kryterium i zakres

Przeliczono wszystkie 27 konfiguracji elektrycznych / 26 produktów.
5 objętości 60/80/100/120/150 l, 2 budżety 40 V/12 A i 60 V/20 A RMS,
3 hipotetyczne pułapy strat miedzi 50/100/200 W. W każdej konfiguracji
121 częstotliwości w 20–80 Hz i 512 punktów Sobola plus nominalny.
810 wierszy syntezy, 50279130 ocen częstotliwościowych (część wspólnego
modelu ponownie oceniana przy różnych limitach; nie tyle niezależnych modeli).

Metryka: minimum obwiedni dla **oddzielnych sinusów**, monopól 2π/1 m,
ciśnienie RMS; katalogowy skok peak. Nie jest to muzyka, SPL w pokoju,
czas dopuszczalnej pracy albo wynik przy normowym THD.

Zakresy stresowe: Mms ±10%, Cms ±15%, BL ±10%, Rms ±30%, Re ±5%,
Le ±20%, Sd ±2%, V ±3%; moduł gazu 0,714–1 adiabatycznego,
dodatkowy Rms 0–1 bazowego, Xref 0,5–0,8 katalogowego, wzrost T 0–80 K.
Re(T) ma założone alpha=0,004/K. To niezależnie zaburzane parametry
fizyczne, nie rozkład produkcji ani pewność, że obejmują rzeczywiste egzemplarze.
Wspólne współrzędne Sobola porównują warianty, nie dowodzą dominacji
przy wszystkich niezależnych parach. Nominalny Xref=0,7 Xmax nie gwarantuje THD.

Pułap Pcu nie jest katalogowym Pe. Wybrano trzy scenariusze właśnie
po to, aby nie przypisać nieznanego chłodzenia na podstawie mocy nadrukowanej.
50 W stałego grzania wymaga Rth ≤0,8 K/W dla przyrostu ≤40 K w prostym
stanie ustalonym; dla 80 K: ≤1,6 K/W. Te progi nie są pomiarami produktu.
Nie uwzględniają innych źródeł ciepła i dopuszczalnych temperatur materiału.

## Wynik porównania przy 120 l i 40 V/12 A

| Konfiguracja | Nominalnie, Pcu≤50 W [dB] | Minimum próby stresowej, 50 W [dB] | Minimum próby stresowej, 200 W [dB] |
|---|---:|---:|---:|
| C02: Dayton RSS390HF-4 | 98.79 | 95.80 | 95.80 |
| C11: Dayton RSS390HE-22 seria | 96.31 | 93.40 | 98.47 |
| C20: Dayton UMII12-22 seria | 94.47 | 91.28 | 95.80 |
| C21: Dayton UMII15-22 seria | 93.64 | 90.79 | 96.81 |
| C04: SB Acoustics SB34SWPL76-4 | 94.23 | 91.24 | 91.24 |
| C06: STX W.32.800.8.FCX | 94.83 | 91.84 | 91.84 |
| C15: FaitalPRO 15XL1400 8ohm | 96.15 | 93.60 | 95.22 |
| C25: SB Acoustics SB34SWNRX-S75-6 | 92.63 | 89.64 | 89.64 |
| C26S: SB Acoustics SB34SWPL76-3-DV series | 94.23 | 91.24 | 91.24 |

**Przyjęta po analizie reguła wyboru prototypu:** preferuj wariant z
najwyższym zaobserwowanym minimum przy konserwatywnym scenariuszu 50 W
Próg do 0,2 dB od plateau spełnia już **100 l**, a nie dopiero 120 l.
Korekta P29C (raport 055) rozdziela wybór głośnika od wyboru punktu
eksperymentu: **C02 RSS390HF-4, start około 120 l**, z regulacją 100/120/150 l.
120 l jest decyzją inżynierską, nie najmniejszą objętością wynikającą z tego
progu ani globalnym optimum. Reguła nie była prerejestrowana przez użytkownika.
Badanie wszystkich pułapów pokazuje też argument przeciw wyborowi:
przy większym dozwolonym grzaniu wygrywa RSS390HE-22.

Nie odrzucono STX z powodu marki. C06 ma wartościowy model 12″,
ale mniejsze Sd·X ogranicza dół pasma w przyjętym kryterium. SB również
pozostaje sensowną alternatywą dla mniejszego zapotrzebowania na 20 Hz.
Nie wykazano, że C02 ma niższe rzeczywiste THD niż STX, SB lub Ultimax.

![Kryterium wyboru i front](../wyniki/97_P29_wybor_i_front.png)

## Kontrole i integracja

324 świadki sprawdzono odrębnym układem równań I/v/x i bilansem energii;
reszty około 2,2e−15. To kontrola algebraiczna, nie walidacja fizyczna.
Raport 052 dodaje przestrzenną warstwę, dwie konwencje tylnej masy gazu,
Re po ogrzaniu i diagnostyczną podatność ścian dla dziewięciu finalistów.
W tej rodzinie przy 120 l i pułapie 50 W minimum C02 to około 98,38 dB,
C11 około 95,09 dB, C06 około 94,83 dB. Nie łączyć tych minimów z minimami
Sobola jako jednego wspólnego certyfikatu: kampanie mają różne osie.

9 wielotonów: C02, 100/120/140 l, 10 jednoczesnych tonów 20–80 Hz,
3 układy faz. Wyrównanie poziomów tonów jest skończoną inversją
częstotliwościową przed filtrami HP BW2 20 Hz / LP BW4 80 Hz.
To nie realizowalny preset miniDSP, nagranie muzyki ani rzeczywisty limiter.
Pułapy: 56,57 Vpeak, 16,97 Apeak, 9,8 mmpeak i 50 W średniego Pcu.
W każdym przypadku wiąże ruch. Dla 120 l średnie Pcu wynosi około
7,50–13,33 W, a crest factor ruchu około 2,52–3,36, zależnie od faz.

Próbki 12 kHz uzupełniono granicą międzypróbkową: max_próbki +
(suma omega_k |amplituda_k|)/(2 Fs). Poziom przeskalowano tą granicą,
nie samym maksimum dyskretnym. Dotyczy tylko tych skończonych sinusów,
bez rozruchu, sygnału arbitralnego i zmian temperatury w czasie.
Nie przenosić starego certyfikatu P24A na nową komorę bez ponownej identyfikacji.

## Architektura dwóch subwooferów i monitorów

Sprawdzono macierz 2→8: kanały 1–3 lewy monitor, 4–6 prawy,
7–8 niezależne subwoofery, każdy z sumą 0,5 L + 0,5 R.
Norma każdego wiersza wynosi 1: sama macierz nie podwaja amplitudy
przy wspólnofazowym sygnale stereo. To nie ogranicza wzmocnienia EQ.

Idealne akustyczne LP LR4 + HP LR4 przy 80 Hz sumują się do modułu 1;
sprawdzono 1000 częstotliwości. Realne monitory są nieznane: filtry,
opóźnienia i fazę trzeba dobrać do pomiarów, nie do samej algebraicznej tożsamości.
Wariant startowy software ma HP BW2 20 Hz + LP LR4 80 Hz, bez dodatniego
EQ, zapis SOS dla 96 kHz. Wszystkie bieguny wewnątrz koła jednostkowego.
To inny LP niż w opisanym eksperymencie wielotonowym; nie utożsamiono ich.

## Wrażliwość rekomendacji

Wybór może zmienić się przy: (1) większym dopuszczalnym grzaniu lub
lepszym zmierzonym chłodzeniu konkurenta, (2) mniejszym rzeczywistym
użytecznym skoku C02, (3) braku miejsca na dwie szerokie skrzynie.
Nie zidentyfikowano danych, które pozwoliłyby ogłosić przewagę jakościową
nad ADAM Sub12/Sub15 lub końcowy poziom w sweet spocie.

Odtwarzanie: `synteza_P29A.py`, `integracja_P29B.py`,
`weryfikacja_i_geometria_P29.py`. Wejścia stresu i wszystkie wyniki
są zapisane; brak kosztorysu jest zgodny z odłożeniem części handlowej.
