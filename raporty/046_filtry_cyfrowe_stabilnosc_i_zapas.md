# Raport 046 — P23A: cyfrowa korekcja, stabilność i zapas sygnału

Stan: 2026-10-27. **Obliczenia i symulacje software przed budową.**
P21B liczy się osobno; numer 045 zarezerwowano dla jego raportu.
Nie jest to pomiar miniDSP ani gotowy preset do urządzenia.

## Wniosek przydatny przy budowie

**Rekomendacja:** współczynniki trzeba projektować dla właściwego Fs,
zapisywać z wystarczającą precyzją i sprawdzać po ponownym odczycie.
Sama stabilność nie wystarcza do zachowania właściwej charakterystyki.
Nie należy traktować największego wzmocnienia sinusa jako pełnej ochrony
przed przesterowaniem przez dowolny sygnał ograniczony w amplitudzie.

**Symulacja:** w zbadanej siatce 20–80 Hz największa różnica między
realizacją float64 a analogowym wzorcem to 0,00035355 dB.
Zaokrąglenie samych współczynników do float32 dało do
0,57086 dB, a do sześciu miejsc
po kropce — 74,566 dB.
Ta ostatnia duża wartość obejmuje silnie zmienione zera charakterystyki.
Nie jest THD, różnicą SPL w pokoju lub wynikiem konkretnego procesora.

![Cyfrowy projekt i osobny błąd zapisu](../wyniki/84_P23A_transformacja_i_zapis_wspolczynnikow.png)

## Pula i wykonany zakres

27 konfiguracji elektrycznych /26 produktów, w tym STX i nowe SB Acoustics.
Wspólne założenia: 30/60/100/150 l netto powietrza, LT20/25/30 Hz z Q=1/√2,
HP drugiego rzędu 18 Hz i LP Linkwitz–Riley czwartego rzędu 80 Hz.
Fs 48/96/192 kHz są scenariuszami programu. Dokumentacja Flex Eight
potwierdza 96 kHz, nie przełączanie tego urządzenia na wszystkie trzy Fs.

Wykonano 972 projekty,4860 reprezentacji kaskad,19440 rekordów sekcji,
300 granicznych filtrów HP,9 przebiegów czasowych i 9 przypadków niezgodnego Fs.
Każda kaskada ma 4 sekcje: LT, HP2 i dwa LP2. Nie zrównujemy tych obliczeń
z identyfikacją przetwornika lub kwalifikacją czasu pracy.

Wejścia i ograniczenia są w [konfiguracji](../dane/konfiguracje/p23a_filtry_dyskretne.json),
pełne wyniki w [podsumowaniu](../wyniki/p23a_podsumowanie.json).
Rekordy zawierają nazwy modeli i połączeń, nie tylko identyfikator scenariusza.

## Model i interpretacja korekcji

Model drugiego rzędu ma Le=0, stałe T/S, sztywne ściany i gaz 0D:

    Hbox(s) = s²/(s²+s*wc/Qc+wc²)
    HLT(s) = (s²+s*wc/Qc+wc²)/(s²+s*wt/Qt+wt²)
    Hbox*HLT = s²/(s²+s*wt/Qt+wt²)
    s = 2*Fs*(1-z^-1)/(1+z^-1)

Ostatnią transformację zastosowano bez prewarpu we wspólnym porównaniu.
Analogowy głośnik pozostaje układem ciągłym; cyfrowa LT nie usuwa dokładnie
każdego rzeczywistego bieguna produktu. Indukcyjność, termika, pamięć,
przecieki, panele i wypełnienie zaburzają idealne skracanie.
Wpływ samego przekształcenia w tym paśmie jest mały, lecz to nie usuwa tych
braków modelu. Odrębny test HP z jawnym prewarpem zgadza się z pierwotnym
wzorem W3C i SciPy w 12 punktach.

Obliczono błąd amplitudy, argumentu ilorazu i analitycznie wyznaczonego
opóźnienia grupowego. To opóźnienie samej kaskady; nie obejmuje ADC, DAC,
buforów, całkowitej latencji DSP lub wyrównania monitorów.

| Zapis | Max błąd amplitudy | Max błąd fazy | Max błąd opóźnienia grupowego |
|---|---:|---:|---:|
|float64|9,6433e-16 dB|5,0399e-15°|0 ms|
|float32|0,57086 dB|9,331°|1,2094 ms|
|decimal6|74,566 dB|180°|10,51 ms|
|decimal9|0,022291 dB|0,13137°|0,020954 ms|
|decimal17|2,4998e-11 dB|3,737e-14°|0 ms|

To maksima znalezione w określonej skończonej siatce, nie dowód globalnego
ekstremum ciągłego pasma. decimal6/9/17 oznacza liczbę miejsc po kropce.
17 miejsc po kropce nie jest tą samą regułą co 17 cyfr znaczących lub
gwarancja dokładnego odtworzenia każdego float64.

## Stabilność i przypadki graniczne

Własna konwencja zgadza się z SciPy:

    H(z)=(b0+b1*z^-1+b2*z^-2)/(1+a1*z^-1+a2*z^-2)
    |a2|<1, 1+a1+a2>0, 1-a1+a2>0

Warunki obliczono jako **dokładne ułamki zapisanych współczynników**.
Nie oparto decyzji wyłącznie na zaokrąglonych pierwiastkach wielomianu.
Wyprowadzenie Cayleya i dodatnie współczynniki Hurwitza zapisano w
[kontrolach](../wyniki/p23a_kontrole_niezalezne.json).
Wszystkie 4860 głównych kaskad są ściśle stabilne w tej definicji, mimo że
część ma bardzo duży błąd charakterystyki.

W 300 odrębnych filtrach kontrolnych cutoff 0,5/2/5/18/80 Hz i Q=0,5/0,707/2/10:
float32 daje 12 przypadków na granicy i 6 poza obszarem, sześć miejsc 17 na
granicy i 4 poza, dziewięć miejsc 1 poza. float64 i decimal17 nie dały takich
przypadków w tej siatce. **To granice hipotetycznej reprezentacji**,
nie zarzut wobec arytmetyki miniDSP, której tu nie zidentyfikowano.

![Dokładna stabilność dla zapisanych współczynników](../wyniki/85_P23A_dokladna_stabilnosc_i_granice.png)

Przy cutoff→0 lub Q→∞ margines dąży do 0. Przy Fs→∞, gdy zachowujemy
fizyczną częstotliwość filtru, bieguny dążą do z=1; stały krok kwantyzacji
staje się wtedy problemem. Zwiększenie Fs nie oznacza automatycznie
lepszej dokładności niskiego filtru o tej samej precyzji współczynników.

Przykład bieguna z=1 skasowanego zerem pokazuje różnicę między stabilną
minimalną transmitancją a marginalnym stanem niewidocznym na wyjściu.
Nie deklarujemy stabilności każdej implementacji przez samo skasowanie.

## Sygnał w czasie i zapas poziomu

9 przebiegów po 4 s: cztery tony 20/31,5/63/80 Hz o zadanych fazach, skok 0,1
od stanu zerowego i impuls jednostkowy. Referencja C04/100 l/LT25/HP18/LR4 80
jest kontrolą, nie wyborem docelowego głośnika. Odróżniono:

- współczynniki float32 przy arytmetyce float64,
- SciPy SOS float32 i float64 z **tymi samymi** współczynnikami i wejściem.

Porównanie pokazuje osobny wpływ stanów i obliczeń. Różnic nie nazywamy
szumem lub zniekształceniami konkretnego hardware. Skończony przebieg nie
dowodzi braku cykli granicznych, przepełnienia lub problemów przy zmianie
nastaw w locie.

**Obliczenie:** dla stabilnego liniowego filtru i |x[n]|≤1 zachodzi
|y[n]|≤Σ|h[k]|. To inna norma niż największa amplituda sinusa.
Dla referencji 96 kHz największy znaleziony sinus ma wzmocnienie
3,7159 dB, zaś skonstruowany ograniczony sygnał daje 7,4354 dB.
Suma bezwzględnych wartości impulsu do 1 s wynosi 2,35381013.
Oszacowanie reszty z obciętych splotów daje ogon≤
9,5336e-09; liczby oceniono
zmiennoprzecinkowo, bez certyfikowanego zaokrąglania na zewnątrz.

Przy tych założeniach potrzebny zapas dla dowolnego ograniczonego wejścia
wynosi około 7,4354 dB. Skonstruowany sygnał nie jest reprezentatywną
muzyką. To świadek obalający utożsamienie sinusowego maksimum z pełnym
zapasem. Osobny, luźniejszy iloczyn norm sekcji pozostawiono w danych.
Wartość 7,44 dB dotyczy wyjścia całego liniowego filtru.

Zbadano też 12 różnych kolejności tych samych sekcji,48 wyjść pośrednich.
Przy założeniu identycznego limitu każdego wyjścia, najmniejsze znalezione
ograniczenie maksymalnej normy pośredniej to
2,3538
dla LT-LP-LP-HP; największe to
2,9276
dla HP-LT-LP-LP.
Pełna transmitancja pozostaje ta sama, lecz porty pośrednie mogą potrzebować
innego zapasu. Nie obejmuje to wewnętrznych stanów DF2T lub nieznanego
skalowania rzeczywistego procesora. Nie jest zaleceniem zmiany jego topologii.
Szczegóły: [kolejność i poziomy](../wyniki/p23a_kolejnosc_i_poziomy_posrednie.csv).

![Błędy arytmetyki i inny zapas dla sygnału czasowego](../wyniki/86_P23A_arytmetyka_i_zapas_sygnalu.png)

## Źródła, znaki i granice wdrożenia

[SRC58–61](../dane/zrodla/P23A_filtry_i_formaty.json):oryginalny HPF W3C
obejrzano w browser-harness, nagrywanie wyłączone. Oficjalna dokumentacja
miniDSP potwierdza 96 kHz oraz przykładowy plik biquad. Dodatnie sprzężenie
w tym przykładzie wymaga zmiany znaków względem naszej konwencji.
To interpretacja sprawdzona algebraicznie: bez zmiany znaków przykład
traci ścisłą stabilność. Nie zastępuje sprawdzenia importu w urządzeniu.
Własny serializer odtwarza współczynniki dokładnie, lecz nie wgrano nic do DSP.

Dokumentacja FIR wymaga pliku IEEE754 single, co **nie określa** formatu
stanów IIR, akumulatora, FMA, skalowania lub wewnętrznego zapasu poziomu.
SciPy online opisuje 1.18.0, użyty pakiet to 1.17.1; wzór sprawdzono osobno.
Niepewnych cech sprzętu nie uzupełniono domysłem.

## Odtwarzanie i dalszy krok

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_filtry_P23A.py

Odrębne kontrole: 9 tożsamości/granic,45 porównań transmitancji z 80 cyframi,
45 pochodnych fazy,12 kontroli współczynników,3 przebiegi DF1 vs DF2T,
4 dokładne przypadki znaków/granic i 3 dodatkowe sprawdzenia największych
błędów kwantyzacji z 80 cyframi.

**Następny krok DSP:** P23B/P24 — skorygowany fizyczny układ
elektroakustyczny, stany przejściowe i dynamiczna ochrona V/I/X/T, z uwzględnieniem
sygnałów P25. Filtr HP na wejściu nie usuwa produktów IMD powstających
później w głośniku. Równolegle pozostaje P21C: główna komora, regulacja,
położenie wypełnienia, mocowanie i dobór proporcji. Pojedynczy wybór,
końcowy PDF i Release 1 czekają na syntezę całego programu.
