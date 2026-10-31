# 13. Promieniowanie, konwencje masy i reakcja pokoju

Stan: 2026-10-24. Równania i obliczenia P11 dla geometrii wzorcowych.
Wyniki są w [raporcie 017](../raporty/017_promieniowanie_i_sprzezenie_pokoju.md).
Nie utożsamiamy ich z pomiarem prototypu ani z rozwiązaniem jego przyszłej
prostopadłościennej obudowy. Geometria, kalibracja i normalizacja to osobne wejścia.

## Jednostki, fazory i moc

Przyjmujemy `exp(+j*omega*t)` i fazory RMS. Znak części urojonej zależy od
tej konwencji; dodatnia masa daje `+j*omega*M`, a podatność `K/(j*omega)`.

```text
Z_mechanical = F/v              [N s/m]
Z_specific   = p/v = Z_mechanical/Sd      [Pa s/m]
Z_acoustic   = p/Q = Z_mechanical/Sd²    [Pa s/m³]
Q=Sd*v
P=Re(F*conj(v))=Re(Z_mechanical)*|v|²
```

Dla RMS w ostatnim równaniu nie ma 1/2. Czynnik 1/2 występuje dla fazorów
amplitudy szczytowej. Przykład [COMSOL, Baffled Piston Radiation](https://www.comsol.com/model/download/1340691/models.aco.baffled_piston_radiation.pdf)
używa amplitudy prędkości; jego wykresy mocy nie mogą być porównane z naszym
1 m/s RMS bez uzgodnienia konwencji. Obejrzano oryginalne równania i rysunki.
Wzór siły dzielimy przez v; dzielenie jeszcze przez pole daje inną impedancję.

## Jednorodny okrągły tłok w nieskończonej odgrodzie

Dla `a=sqrt(Sd/pi)` oraz `q=k*a`:

```text
Zrad = rho*c*Sd*[1-J1(2q)/q + j*H1(2q)/q]
Re(Zrad)/(rho*c*Sd) = q²/2-q⁴/12+q⁶/144-...
Im(Zrad)/(rho*c*Sd) = 8q/(3pi)-32q³/(45pi)+...
Mair_front(f->0)=8*rho*a³/3
```

H1 jest funkcją Struve'a. Przy małym q obliczenie `1-J1(2q)/q` traci cyfry;
stosujemy szereg. Przy dużym q część rzeczywista dąży do rho*c*Sd, a masa
`Im(Zrad)/omega` nie pozostaje stała. Formalne duże ka weryfikuje równania
sztywnego tłoka, nie rzeczywistą membranę z jej modami i breakupem.

Odrębna całka Rayleigha wykorzystuje pole wspólne dwóch dysków:

```text
Aoverlap(r)=2a²*acos(r/(2a))-(r/2)*sqrt(4a²-r²)
Zrad=rho*s*integral_0^(2a) Aoverlap(r)*exp(-s*r/c) dr
```

To druga droga obliczenia bez Struve'a. Część rzeczywistą sprawdzamy też
całką mocy po kierunkach. Ciśnienia elementów mają wspólną fazę wymuszenia;
nie sumuje się ich samych mocy ani poziomów dB.

Na osi, w odległości z od płaszczyzny, dokładnie:

```text
p/v=rho*c*exp(-s*z/c)*[1-exp(-s*Delta/c)]
Delta=a²/[sqrt(z²+a²)+z]
```

Postać z Delta i `expm1` zachowuje małe różnice. Pole dalekie ma czynnik
`D(theta)=2*J1(ka*sin(theta))/(ka*sin(theta))`; dla małego argumentu D→1.
Sama mała kierunkowość nie oznacza, że skończona skrzynia jest nieskończoną odgrodą.

## Mmd, Mms i dopasowanie referencyjnego powietrza

Karta [FaitalPRO 15XL1400](https://faitalpro.com/en/products/LF_Loudspeakers/product_details/datasheet.php?id=201060150)
podaje Mms=190,0 g i Mmd=162,4 g. Numeryczny protokół odniesienia powietrza
nie jest tam określony. Nie wolno zamienić Mms w Mmd przez samą zmianę nazwy.
Nie znamy niezależnej masy Mmd większości kandydatów.

W eksperymencie kalibracyjnym przyjmujemy liczbę referencyjnych powierzchni n:

```text
M_effective=Mms-n*Im(Zreference(Fs))/(2*pi*Fs)
R_effective=Rms-n*Re(Zreference(Fs))
```

Odejmowane są składniki przy Fs, a nie dowolna stała masa. Pozostałe BL,
Cms i elektryka są zamrożone. Takie dopasowanie odtwarza zerową reaktancję
i opór w Fs wybranego modelu odniesienia. Nie odtwarza automatycznie całej
krzywej ani jej nachylenia; nie jest pomiarem rzeczywistego Mmd.
Nie twierdzimy, że hipotezy n=1/2 obejmują wszystkie protokoły producentów.
Niedodatnia pozostała masa lub strata odrzuca daną kalibrację.

Kontrola n=0 dodaje nowe powietrze do niezmienionego Mms/Rms. Jest celową
kontrolą podwójnego liczenia, a nie modelem finalisty. Jej błąd może mieć
oba znaki w różnych częstotliwościach, więc nie jest uniwersalnie zachowawczy.
Różnice między zaokrąglonym Mms z karty i Mms wyprowadzonym ze spójnego
zestawu Fs/Vas/Sd zachowujemy jawnie. Odrębny katalogowy zestaw Mmd/Cms/BL/Rms
jest osobnym eksperymentem, nie podmianą pojedynczej liczby w innym zestawie.

## Skończona bryła kontrolna i rozłożony gaz wewnątrz

Używamy sztywnej sfery z radialnie drgającą czaszą o powierzchni Sd.
Nie jest to płaski kosz ani rekomendacja budowy sfery. Dla promienia b,
`mu0=1-Sd/(2*pi*b²)` i wielomianów Legendre'a:

```text
c0=(1-mu0)/2
cn=[P_(n-1)(mu0)-P_(n+1)(mu0)]/2
Zoutside=-j*4*pi*rho*c*b²*sum[cn²/(2n+1)*hn(kb)/hn'(kb)]
Moutside(0)=4*pi*rho*b³*sum[cn²/((2n+1)*(n+1))]
```

hn jest wychodzącą funkcją Hankela drugiego rodzaju. Stabilna rekurencja
ilorazów unika przepełnienia funkcji sferycznych wysokiego rzędu. Pełna
czasza odtwarza pulsującą sferę; malejący kąt czaszy daje lokalnie płaską
odgrodę, lecz dojście do tej granicy jest powolne.

[Bellows 2024](https://sambellows.github.io/assets/pdf/2024_spherical_cap.pdf)
podaje poprawkę końcową zgodną z tą sumą. Odtworzono minimum około 0,6167
przy 50,5°. Normalizacja używa promienia rzutu `b*sin(theta)`, który różni
się od promienia koła o powierzchni Sd. Granice porównania z rurą dotyczą
0<theta<=90°. Wartość około 0,6133*a dotyczy otwartego końca półnieskończonej
rury; nie jest ogólnym wzorem dla nieodgrodzonej membrany.

Wewnętrzną komorę kontrolną opisuje regularna funkcja jn i przeciwna siła
ciśnienia. Oddzielono biegun jednorodnego sprężania:

```text
Zinside = Sd²*K(s)/(s*V) + Zdistributed_remainder
```

Reszta zawiera rozłożoną bezwładność i wyższe mody. Przy małym kb
wyrażenie `j0/j0'+3/(kb)` wymaga szeregu, aby nie utracić małego składnika
bezwładnościowego. Sama komora bez strat ma bieguny rezonansowe; model nie
obiecuje skończonej odpowiedzi przy dokładnie takim wymuszeniu.
Do strat części jednorodnej można włączyć dodatni model gazu z P09.

W polu bliskim strumień energii sprawdzamy przez `Re(p*conj(v_radial))`.
Użycie `|p|²/(rho*c)` w dowolnym miejscu pola bliskiego jest nieuzasadnione.
Całka przez zewnętrzne sfery zgadza się z pracą siły promieniowania na porcie.

## Dwa źródła, podłoga i ściana

Współczynniki wzajemne dwóch rozłącznych dysków pochodzą z podwójnej całki
Rayleigha. Macierz jest wzajemna. Jej część hermitowska odpowiada całce
kwadratu pola dalekiego, czyli jest nieujemna dla dowolnych faz prędkości.

Obrazy Neumanna podłogi i bocznej ściany są dokładne dla ścian prostopadłych
do nieskończonej odgrody. To nie jest ten sam problem co wszystkie sześć
ścian rzeczywistego pokoju. Model odgrody z obrazami i pełny model modalny
są osobnymi eksperymentami. Nie dodaje się ich wyników jako dwóch room gain.
Porównanie dwóch źródeł przy tym samym napięciu każdego wzmacniacza nie
jest porównaniem przy stałej łącznej mocy elektrycznej.

## Reakcja pełnego modelu pokoju na napęd

Dla pola modalnego P26 siła odbiera tę samą aperturę Gaussa co źródło.
Macierz impedancji mechanicznych ma wtedy postać `Sd_i*H_ij*Sd_j`.
Nie utożsamiamy szerokości sigma z promieniem membrany. Kalibracja do
referencyjnego portu Gaussa daje pozostałą masę efektywną, nie Mmd.

Jednorodny operator w wolnej przestrzeni ma dla q=k*sigma:

```text
Re(Hfree)=rho*omega²/(4*pi*c)*exp(-q²)
Im(Hfree)=rho*omega/(4*pi^(3/2)*sigma)*[1-2*q*Dawson(q)]
```

Sprawdzono go osobną całką radialną par rozkładów Gaussa. Model pokoju
jest pasywną rodziną modalną, ale pomija rozpraszanie na wybranej bryle
skrzyni. Nie jest dzięki samej pasywności zidentyfikowanym pokojem użytkownika.

Napęd rozwiązujemy łącznie dla prędkości i prądów wszystkich portów.
Praca oddana do pokoju jest składnikiem bilansu, a nie tylko wykresem
ciśnienia przy narzuconym ruchu. Dla `D=Dfree+DeltaZ`:

```text
epsilon=norm(Dfree^(-1)*DeltaZ,2)
epsilon<1  => norm(v-vfree)/norm(vfree)<=epsilon/(1-epsilon)
```

To ograniczenie zmiany wektora prędkości dla zadanego operatora. Nie jest
automatycznie względnym ograniczeniem ciśnienia w punkcie, szczególnie przy
dołku interferencyjnym. Obie wielkości zapisano osobno. Bilans energii
motorów i modów zweryfikowano symbolicznie. Dodatnie straty dają rozpraszanie;
granica całkowicie bezstratna może zachować nierozpraszane mody.

Pokój ma około 3,7 m w x, 4,6 m w y i 2,5 m w z. Współrzędne źródeł,
głowy, straty modalne i czas wyrównania ciśnienia są scenariuszami U-017.
Gęsty skan częstotliwości ma własną kontrolę zagęszczenia, a suma modalna
odrębną kontrolę kmax. Skończona siatka nie jest certyfikatem maksimum
po całym ciągłym paśmie ani gwarancją wykonania ustawienia w tym pokoju.
