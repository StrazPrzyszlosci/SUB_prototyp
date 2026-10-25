# IMD, fazy, modulacja i emisja — wiedza po P14B

Status: teoria oraz obliczenia warunkowych modeli, 2026-10-25.
Nie jest to identyfikacja nieliniowości naszych 24 produktów.
[Raport024](../raporty/024_P14B_emisja_i_swiadkowie.md) zawiera wybrane wyniki;
pełna kampania P14B pozostaje w toku.

## Nieliniowość tworzy częstotliwości nieobecne na wejściu

**Wyprowadzenie:** dla x=a cos(w1t)+b cos(w2t) składnik x² tworzy
sumę i różnicę częstotliwości; x³ tworzy także |2f1−f2| i |2f2−f1|.
Przy RMS A,B współczynnik RMS linii mieszanej drugiego rzędu wynosi
sqrt(2) A B, a trzeciego 1,5 A²B lub 1,5 AB². Faza jest m phi1+n phi2.
Gdy podpisana częstotliwość jest ujemna, dodatnia reprezentacja wymaga
sprzężenia zespolonego oraz odwrócenia znaków m,n. Kontrole obejmują ten przypadek.

Dla 45+95 Hz produkt |2×45−95| ma 5 Hz. **Rekomendacja:** przyszłą ochronę
badać na całym x(t), a nie tylko dwóch wejściowych sinusach. Filtr wejściowy
nie filtruje bezpośrednio produktów wytwarzanych wewnątrz przetwornika.
Zmienienie amplitud tonów może zmniejszyć ich generację; nie jest to
tożsame z usunięciem 5 Hz z gotowego ruchu.

## Dlaczego potrzebne są zespolone fazory

**Teoria:** produkty różnych mechanizmów sumują się wektorowo. Dwa
podobne moduły mogą się wzmacniać lub znosić. Różnica dwóch modeli pola
DeltaP=P_moving−P_fixed jest kontrolowanym porównaniem tych modeli,
nie nowym niezależnym źródłem o znanej fazie w fizycznym głośniku.
Procentów RMS nie wolno dodawać arytmetycznie jako ogólnej reguły.

Dla zespolonego nośnego C i pary bocznej U,L:

```text
u = U/C; l = L/C
AM_depth_first_pair = |u + conjugate(l)|
PM_index_first_pair = |u - conjugate(l)|
```

Są to małosygnałowe równoważniki pierwszej pary bocznej. Nie identyfikują
jednoznacznie mechanizmu fizycznego i nie zastępują miary całego sygnału.
Pięcioliniowy klaster nośnej rekonstruujemy osobno jako
E(theta)=1+sum_j c_j exp(i j theta), j=−2,−1,1,2.
Własne diagnostyki to std(|E|)/mean(|E|) oraz odchylenie częstotliwości
f_low Im(E'/E), tylko gdy obwiednia nie zbliża się do zera.

**Źródło SRC38:** oryginalne AN10 wymaga częstotliwości >8:1 i napięć
voice:bass=1:4. Nasze próby tych warunków nie spełniają. Dodatkowo na s.3
wydrukowano sqrt(2/K) w normalizacji d_AMD: dla tej samej obwiedni to
sqrt(2) razy nasza miara std/mean. Nie nazywamy ich identycznym wynikiem
ani badaniem zgodnym z IEC. Przykładowych wykresów nie przenosimy na kandydatów.

## Od ruchu do ciśnienia

**Model kontrolny stacjonarny:** p_RMS=−rho Sd w² X_RMS exp(−ikr)/(4pi r).
Ten sam ruch przy 5 Hz i 95 Hz nie promieniuje jednakowo: współczynnik
przy X zawiera f². Należy podawać osobno X, prąd i ciśnienie, z geometrią.
Odgroda nieskończona, promieniowanie pod kątem i czasza na sferze mają
inne transmitancje i częstotliwościową dyfrakcję. Zastosowanie ich do
tego samego X nie zmienia automatycznie obciążenia zwrotnego w ODE.
Nie jest to rozwiązanie finalnej prostokątnej skrzyni ani pola pokoju.

**Wyprowadzenie i SRC39:** zdefiniowany punktowy iniekcyjny monopol na
torze z(tau) ma potencjał, w naszej konwencji znaków:

```text
(c^-2 dtt - Laplacian) Psi = Q(t) delta(r-z(t))
Psi(r,t) = Q(tau) / (4pi R(tau) [1-Mr(tau)])
t = tau + R(tau)/c
p = rho * dPsi/dt
Q = Sd * dx/dtau
```

Czynnik 1−Mr wynika z całkowania delty funkcji Greena. Dla poddźwiękowego
toru czas opóźniony jest jednoznaczny. W kodzie użyto odtworzonego pasma
0–1000 Hz i okresowego splajnu. Dziedzinę jego prędkości kontrolujemy
przez ekstrema pochodnej każdej części splajnu, a odległość przez osłonę
ruchu. Są to rachunki zmiennoprzecinkowe, nie certyfikowana arytmetyka przedziałowa.

To **kontrolny model ruchomego źródła punktowego**, nie całe rozwiązanie
ruchomej membrany. Wysokie harmoniczne poza zapisanym pasmem, zmienna
granica rzeczywistego tłoka i sprzężenie zwrotne pola pozostają odrębnymi
zagadnieniami. Nawet dla liniowego ruchu jego nieliniowa geometria może
tworzyć produkty: nie nazywać ich błędem numerycznym modelu LTI.

**Niezależna granica małej amplitudy:** dla x=A cos(wt), obserwatora na
osi w odległości r i C=rho Sd/(4pi r), współczynnik szczytowy drugiej
harmonicznej do rzędu A² wynosi
C(−A²w²/r−2i A²w³/c) exp(−2iwr/c). Porównanie z pełnym czasem opóźnionym
sprawdza także fazę, nie tylko moduł. Zamrożenie toru przy zachowanym Q
odtwarza stacjonarny monopol; ruch jednostajny ma jawny wzorzec tau.

## Prąd stały i kontrola bilansu

**Twierdzenie warunkowe:** przy stałym Re, BL zależnym tylko od x,
zerowej średniej napięcia i okresowym całkowitym strumieniu:

```text
<V> = Re <I> + Delta(lambda_total)/T + Delta(integral BL(x) dx)/T
=> <I> = 0
```

Nie wymaga to <x>=0. Asymetryczny gaz/zawieszenie może przesunąć średnią
pozycję przy zerowym średnim prądzie. Nie wolno przenosić tego wniosku
bez zmian do Re(T), BL(x,T), przejściowego rozruchu lub nieokresowego stanu.
Niewielki niezerowy wynik FFT wymaga zestawienia z błędem powyższej
tożsamości i niedomknięciem cyklu, zamiast natychmiastowej interpretacji fizycznej.

## Co pozostaje otwarte

Pełne P14B obejmuje również klasy fazy, małe amplitudy i preload; zapis
części kampanii nie zamyka tych studiów. Potrzebne są rozstrzygnięcia flag,
zbieżność wybranych dużych odpowiedzi, a potem termika i dynamiczna ochrona.
Ogon RMS samego X powyżej 1 kHz nie ogranicza automatycznie ogona p,
ponieważ emisja waży go częstotliwościowo. Miary 5–1000 Hz nie są THD
całego nieskończonego pasma ani wynikiem fizycznego prototypu.
