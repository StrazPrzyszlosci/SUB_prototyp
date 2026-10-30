# Raport 051 — P21C1: kołowa membrana i bezwładność powietrza

Data: 2026-10-30. **Obliczenia modelowe; brak pomiarów. Wyłącznie praca lokalna, bez publikacji i PR.**

## Pytanie i zakres

Czy wnioski P21C0 pozostają po zastąpieniu kwadratu kołem o powierzchni
katalogowego Sd? Zbadano 26 produktów z zamrożonej puli repozytorium.
C26P/C26S mają tę samą powierzchnię: policzono jeden port akustyczny,
bez tworzenia dwóch pozornie niezależnych geometrii. Nie aktualizowano kart producentów.
Koło o promieniu sqrt(Sd/pi) jest **założonym tłokiem równoważnym**, nie
odwzorowaniem stożka, zawieszenia, kosza lub otworu montażowego.

27 wnętrz: 60/100/150 l, głębokość zewnętrzna 350/425/500 mm,
W/H=1/1,5/2. Ściany geometryczne 22 mm, akustycznie sztywne;
c=343 m/s i rho=1,2 kg/m³ to założenia. Źródło na froncie,
z=H/2 i x=W/2 albo W/4; osobne częstotliwości 20/25/31,5/40/63/80 Hz.
Brak regulatora, wypełnienia, strat, ścian podatnych, kosza i napędu.
Objętości są brutto pustego wnętrza; nie finalnym Vb netto.

## Wyprowadzenie

Uśrednienie modu cosinusowego po dysku daje

\[
b_{nl}=\cos(n\pi x_c/W)\cos(l\pi z_c/H)
\frac{2J_1(a\kappa_{nl})}{a\kappa_{nl}},\qquad
\kappa_{nl}^2=(n\pi/W)^2+(l\pi/H)^2.
\]

W zerze iloraz ma granicę 1. Wzór wynika z całki Fouriera jednorodnego
koła; osobno sprawdzono go całkowaniem po cięciwach. Kwadraty b razy
wagi epsilon (1 dla zera, 2 dla dodatniego indeksu) wchodzą do tej samej
sumy głębokości D cot(qD)/q co w raporcie 050. R oznacza nacisk
zwrotny na tłok przy zadanym ruchu, podzielony przez nacisk gazu 0D.
Nie oznacza stosunku SPL na zewnątrz.

**Granica ogona:** Parseval daje sumę wszystkich wag b² = WH/(pi a²).
Po odjęciu policzonego prostokąta indeksów zostaje dodatnia reszta E_N.
Poza nim kappa >= pi(N+1)/max(W,H). Poniżej pierwszego modu
pominięte składniki są ujemne, a ich moduł maleje z kappa. Zatem

\[
R_N-B_N\le R\le R_N,\qquad
B_N=E_N k^2D\frac{\coth(D\alpha_{min})}{\alpha_{min}},
\quad \alpha_{min}=\sqrt{[\pi(N+1)/\max(W,H)]^2-k^2}.
\]

To analityczne ograniczenie ucięcia ocenione w float, nie certyfikat
przedziałowy obejmujący zaokrąglenia ani niepewność danych producenta.
Policzono rzędy 80/160/320. Dla kwadratu o identycznej powierzchni
użyto osobnej granicy ogona z P21C0; oba źródła mieszczą się na froncie.

W granicy małej częstotliwości K_g R = K_g - omega² M_air + O(omega⁴),
gdzie K_g=rho c² Sd²/V, a

\[
M_{air}=\frac{\rho S_d^2}{V}\left[\frac{D^2}{3}+
\sum_{(n,l)\ne(0,0)}\epsilon_n\epsilon_l b_{nl}^2
\frac{D\coth(\kappa_{nl}D)}{\kappa_{nl}}\right].
\]

To bezwładność wewnętrznego gazu w zadanej geometrii, nie Mms ani Mmd.
Różnica dwóch pozycji tego samego tłoka usuwa wspólną nieznaną bazową
masę przetwornika. Nie usuwa zmian promieniowania zewnętrznego przy
przesunięciu na skończonym froncie; ich tutaj nie policzono.

## Wyniki

Dopuszczono 1103 źródeł, odrzucono geometrycznie 301; wykonano **6618 punktów** i 451 par położeń. Odrzucenie dotyczy tylko wystawania równoważnego dysku poza front, nie kwalifikacji całego głośnika.

Przykłady: 150 l brutto, D zewnętrzne 500 mm, W/H=1,5, 80 Hz. Ostatnia kolumna to granica niskoczęstotliwościowa, nie masa dopasowana przy 80 Hz.

| Model | Sd [cm²] | R centralnie | R przesunięty | Delta M_air [g] |
|---|---:|---:|---:|---:|
| C02: Dayton RSS390HF-4 | 829.6 | 0.628975 | 0.522147 | 2.436 |
| C04: SB Acoustics SB34SWPL76-4 | 458.0 | 0.451357 | 0.349142 | 0.703 |
| C25: SB Acoustics SB34SWNRX-S75-6 | 508.0 | 0.486797 | 0.384061 | 0.870 |

Największa znaleziona różnica koło–kwadrat przy równym Sd wynosi -0.010055 jednostki R: C12_V150_D0.5_A1_X0.25, 80 Hz. Jej przedział ucięcia wynosi [-0.010072; -0.009971]. To różnica kształtu kontrolnego źródła, nie poprawa jakości produktu.

Największa zmiana M_air po przesunięciu: 4.215 g dla C14, 100 l, D=350 mm, W/H=2; przedział ucięcia [4.215; 4.215] g. To maksimum znalezione w skończonej siatce.

![Membrana i położenie](../wyniki/96_P21C1_membrana_i_przesuniecie.png)

## Kontrole i ograniczenia

Największa zmiana 160→320: 4.5080398e-05 R; największa granica ogona: 3.9421743e-05 R. Sześć odrębnych całek po dysku sprawdza sprzężenie źródła. Trzy świadki sprawdzają obrót, granicę masową przy 0,1 Hz i dalsze zagęszczenie do 640. Każdy przebieg kampanii sprawdza znak zmiany i zgodność z granicą poprzedniego rzędu. To kontrola matematyczna własnego modelu, nie niezależna recenzja lub nowa walidacja FV wszystkich punktów.

## Znaczenie dla decyzji

| Kryterium | Wynik modelowy | Co pozostaje nieznane | Warunek dalszego użycia / następny krok |
|---|---|---|---|
| Powierzchnia źródła | Koło z Sd i porównanie równej powierzchni | Kształt stożka i ruch zawieszenia | Zachować port skończony; nie zastępować go monopolem |
| Pozycja | R i zmiana wewnętrznej bezwładności dla dwóch pozycji | Front zewnętrzny, kosz i wzmocnienia | Porównać pełny bilans mas bez podwójnego Mms |
| Głębokość | Wszystkie warianty ≤500 mm | Wyporność kosza, prześwity i osprzęt | Sprawdzić rysunek montażowy i bilans netto |
| Regulacja i wypełnienie | Tutaj nie są modelowane | Przestrzenne straty i objętość zajęta | Następne obliczenie: port kołowy z warstwą porowatą i przegrodą |
| Ostateczny wybór | Brak rankingu produktów | Sprzężony napęd, ciepło, DSP, pokój | Zintegrować przed wyborem; prototyp zweryfikować pomiarowo |

Przesunięcie nadal zmienia nacisk po zastąpieniu kwadratu kołem.
Nie wynika stąd automatycznie, że centralne położenie daje lepszy bas.
Zamknięto wyłącznie krok P21C1; pełne P21C i wybór prototypu pozostają otwarte.

## Odtworzenie

```bash
OPENBLAS_NUM_THREADS=1 python3 skrypty/membrana_kolowa_P21C1.py
OPENBLAS_NUM_THREADS=1 python3 skrypty/raportuj_P21C1.py
```

Wejścia i wersje bibliotek zapisano w `wyniki/p21c1_podsumowanie.json`.
Pliki wynikowe: `p21c1_membrana.csv`, `p21c1_odrzucenia.csv`,
`p21c1_przesuniecie.csv`. Manifest zawiera kod, wejścia, brief i wyniki.
Nie pozyskano nowych danych producentów i nie wykonano pomiarów.
