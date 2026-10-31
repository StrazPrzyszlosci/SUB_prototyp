# Raport 066 — P21G: przestrzenny model FV rzeczywistych przeszkód P20D i podatnych paneli

**31 października 2026. Status: wykonana nowa kampania obliczeniowa.** Model jest małosygnałowy, liniowy i warunkowy. **Nie stanowi pomiaru, pełnego MES konstrukcji, obliczenia THD, promieniowania ścian ani projektu wykonawczego.**

## Problem badawczy i hipoteza

P21D/raport 060 opisuje przestrzenne pole gazu z wręgami i wkładami P20D, ale uznaje wszystkie ściany za sztywne. P21E/064 i P21F/065 wprowadzają podatne panele, lecz bez prawdziwych przeszkód P20D. Pytanie P21G: **czy można do wielokomórkowego modelu FV z przeszkodami dołączyć sprężyste porty dwóch ścian bez utraty wzajemności i bilansu mocy?** Jaki jest wpływ na prędkość C02, C11, C06 w 20–80 Hz i jak zmienia się wynik po zagęszczeniu siatki?

Hipoteza: w zadanym, ograniczonym modelu podatność paneli ma niewielki, ale niezerowy wpływ na napęd; potwierdzenie wymaga złączenia portów przy wspólnym polu ciśnienia, nie sumowania osobnych korekt P21D i P21E w dB.

## Wspólna geometria i świadome różnice od P21D

- Korpus 1000 × 440 × 500 mm, prostokąt wewnętrzny **956 × 374 × 456 mm**, z **11 bryłami wręg**, według \`dane/konfiguracje/p18e_geometria_zamrozona.json\` i reguły P20D.
- Stany \`150: 2 duże, 0 małych\`, \`120: 11 dużych, 1 mały\`, \`100: 16 dużych, 3 małe\` oraz identyczna geometryczna wyporność kosza zastępczego **A = 5 l**. Nazwy 100/120/150 są nazwami konfiguracji, nie dokładnymi litrażami.
- **Przestrzeń powietrza przed uwzględnieniem ciała włókien**: 150,087424 / 119,937424 / 100,587424 l. W modelu materiał nie usuwa dodatkowej ilości powietrza; wliczono tylko jego stratność efektywną.
- Na ścianie tylnej wyklejenie scenariuszowe 50 mm. **Uproszczenie względem P21D:** zamiast właściwości z modelu porów \`CircularPores\` zastosowano stałe \`rho=1,2 kg/m³\`, \`K=rho*c²*(1+j*0,035)\` w warstwie oraz niezmienione realne \`rho,c=343 m/s\` w gazie. Jest to **założenie fenomenologiczne**, nie odtworzenie P21D ani własność konkretnej maty. Nie wolno porównywać liczbowo zmian portu P21G–P21D jako samego efektu sprężystości.
- C02/C11/C06: parametry producentów zapisane w \`dane/przetworniki/pula_rozszerzona.json\`. Mms skuteczne odzyskano z Fs, Vas, Qes/Qms, Sd; bez drugiego dodawania masy promieniowania.
- Membrana jest sztywnym dyskiem o powierzchni Sd przy x=209 mm, z=228 mm na przedniej ścianie; udział każdej komórki granicznej pochodzi z całkowania pola koła, a nie aproksymacji do środka komórki.
- Dwie **jednorodne** podatne powierzchnie na z=0 i z=H, z pominięciem fragmentów zajętych przez sztywne przeszkody. Pole każdej **odkrytej** powierzchni wynosi **0,3377 m²**. To uśrednione porty objętościowe, **nie realne postacie drgań z MES**.
- Hipotetyczne podatności: \`C_panel=1,9034748e−8 m³/Pa\` na panel, \`s=0/0,5/1/2\`. Pierwszy mod panelu: 143,30533 Hz dla pierwszego i **założone** 152,44 Hz dla drugiego, tłumienie \`ζ=0,03\`. Dane C_panel pochodzą z konkretnego modelu P18E, **nie z pomiaru realnego zestawu ścian**.

## Równania i praca portów

Wykorzystano zgodny z P21D, objętościowy model Helmholtza w komórkach:

\`[L(rho) − omega² diag(Vcell/Kbulk)] p = j*omega*S*Q\`.

Dla dwóch sąsiadów przewodność przepływu objętościowego to \`Aface/[rho*(dleft+dright)]\`, a macierz \`L\` jest wzajemna i symetryczna. Macierz \`S\` ma pięć kolumn: trzy osobne źródła–dyski C02/C11/C06 na froncie oraz dwie odkryte powierzchnie paneli. Wszystkie kolumny sumują się do 1.

Port ciśnieniowo-objętościowy \`Z(jw)=jw Sᵀ[L−w² V/K]⁻¹ S\` ma jednostkę Pa·s/m³, zachowuje wzajemność, a dla przyjętego pasywnego K nie powinien produkować ujemnej mocy czynnej.

Dla konkretnego kandydata z \`Sd\`, amplitud prędkości \`v\`, \`q1=y1'\`, \`q2=y2'\`:

\`Q=(Sd*v, −q1, −q2)\`, \`p=Z*Q\`.

\`Zm*v + Sd*p0 = BL*i\`,
\`(Kw_j/(jw)+Rw_j+jw*Mw_j)*qj=pj\`,
\`(Re+jw*Le)*i+BL*v=U\`.

\`Kw=1/Cw\`, \`Mw=Kw/(2πfp)²\`, \`Rw=2ζ√(KwMw)\`. W obliczeniach \`U=1 V RMS\`. Dla \`s=0\` rozwiązujemy osobną **sztywną** granicę, bez dzielenia przez 0.

**Bilans mocy RMS (zgodny z fazorami):**

\`Re(U*conj(i)) = Re*|i|² + Rms*|v|² + ∑ Rw_j*|qj|² + Re(Qᴴ Z Q)\`.

Badana zmiana \`20log10(|v_podatne|/|v_sztywne|)\` jest stosunkiem prędkości przy tym samym napięciu. Nie jest wynikiem SPL w pokoju, THD czy maksymalnego poziomu głośnika. Korekta środka komórki do granicy czołowej z P21D **nie została tu zaimplementowana**; ten sam brak dotyczy wszystkich wariantów porównawczych.

## Wykonana kampania: 348 odpowiedzi, 29 rozwiązań FV

| Konfiguracja | Siatka (maks. rozmiar komórki) | Niewiadome powietrza | Częstotliwości |
|---|---:|---:|---|
| 120_coarse | 60 mm | 5 601 | 20–80 Hz, krok 5 Hz |
| 120_refined | 45 mm | 8 843 | 20–80 Hz, krok 5 Hz |
| 120_fine80 | 35 mm | 10 841 | 80 Hz |
| 100_coarse | 60 mm | 6 257 | 40 Hz |
| 150_coarse | 60 mm | 3 118 | 40 Hz |

Łącznie **29 faktoryzacji macierzy gazu**; dla każdej trzech kandydatów i czterech stanów paneli \`s=0,0,5,1,2\`: **348 odpowiedzi napędu**.

### Wariant 120_refined (119,937 l), nominalna podatność s=1

| Głośnik | Minimum Δv w 20–80 Hz | Maksimum Δv w 20–80 Hz | Δv przy 20/40/80 Hz |
|---|---:|---:|---|
| C02 RSS390HF-4 | **−0,06038 dB** | **+0,13322 dB** | +0,13322 / −0,04247 / −0,05169 dB |
| C11 RSS390HE-22 | −0,03510 dB | +0,08432 dB | +0,08432 / −0,00428 / −0,03510 dB |
| C06 STX W.32.800.8.FCX | −0,02915 dB | +0,06070 dB | +0,06070 / −0,01615 / −0,02912 dB |

![P21G: wpływ podatnych ścian na prędkość trzech przetworników](../wyniki/106_P21G_komora_i_podatne_panele.svg)

Przy dwukrotnie większej, nadal hipotetycznej podatności C02 dla 120_refined uzyskał od **−0,11533** do **+0,25350 dB** na badanej siatce. Nie ma podstaw do utożsamienia tych różnic z poprawą jakości brzmienia.

### Kontrole fizyczne i numeryczne

- Wszystkie stany odtworzyły **dokładną objętość geometryczną** 119,937424 / 100,587424 / 150,087424 l dla danej klasy prostopadłościennych przeszkód. Nie oznacza to dokładnej objętości rzeczywistego kosza ani wypełnienia.
- Maksymalna względna reszta rozwiązania układu FV (w normie \`||A p−b||/||b||\`) = **2,681·10⁻¹²**.
- Maksymalna względna niesymetria wzajemnego portu = **3,145·10⁻¹⁵**.
- W obliczeniach z podatnymi ścianami maksymalna reszta bilansu mocy RMS = **1,065·10⁻¹⁵**. Nie wystąpiła ujemna strata energii w testowanych przypadkach.
- Zmiana amplitudy C02 przy 80 Hz między siatkami **60→45 mm**: około **0,00774 dB**, a między **45→35 mm**: **0,00184 dB**. Różnica *samego wpływu podatności* \`Δv\` na tych dwóch gęstszych siatkach wynosi tylko **3,8·10⁻⁶ dB**. Wartości nie wyznaczają błędu rzeczywistego kontinuum ani nie certyfikują całego pasma; lokalna rozdzielczość przy koszu i wręgach wymaga osobnej kontroli.
- Dotychczasowa kontrola niezależności ma charakter **wzajemności i bilansu jednego operatora FV**, nie osobnego solwera z alternatywną siatką / elementami. Nie oznaczamy więc zadania P05 jako zakończonego w całości.

## Co nowego wiadomo, a czego nadal nie wiadomo

Model P21G po raz pierwszy pozwala w jednym równaniu rozwiązywać przestrzenne **sztywne bryły wręg i wkładów** oraz **porty podatnych ścian**. To usuwa istotną lukę konstrukcyjną między P21D i P21E/P21F. W badanych warunkach wpływ uproszczonego ruchu paneli na samą prędkość membrany jest mały, ale nie mówi nic o bezpośredniej emisji dźwięku z paneli. Możliwy jest rezonans panelu poza pasmem badanego napędu, a sztywne wręgi nie są jeszcze podatnymi elementami mechaniki.

**Nadal otwarte:** pełne ugięcia z lokalnego MES i naciski na wręgi, wielomodowe funkcje postaci, dynamiczna podatność zależna od wilgotności/kleju, prawdziwy kosz i materiał porowaty P21D, praca w obu orientacjach, zmienny stan wkładów, własna emisja paneli, zbieżność pola przy lokalnych prześwitach i walidacja po budowie. Parametry termiczne i ochrona P25E nie są jeszcze zintegrowane z nowym portem.

C02 pozostaje **faworytem warunkowym**, nie nowym zatwierdzonym zwycięzcą. Nie wolno wyprowadzać z P21G nowej przewagi nad STX lub C11 na podstawie samego zakresu Δv.

## Reprodukcja

\`OPENBLAS_NUM_THREADS=1 python skrypty/p21g_fv_podatne_panele.py\`

Konfiguracja: \`dane/konfiguracje/p21g_fv_panele.json\`. Bryły:
\`dane/konfiguracje/p18e_geometria_zamrozona.json\` oraz
\`dane/konfiguracje/p20d_geometria.json\`.
T/S: \`dane/przetworniki/pula_rozszerzona.json\`.

Po wykonaniu skrypt tworzy \`wyniki/p21g_porownania.csv\` (348 wierszy),
\`wyniki/p21g_kontrole.json\`, \`wyniki/p21g_podsumowanie.json\`
oraz \`wyniki/p21g_manifest.json\` (SHA-256 wejść i wyników).
W PR znajdują się skrypt, konfiguracja, podsumowanie z aktualnego przebiegu,
39 częstotliwościowych świadków, wykres i niniejszy raport. 
