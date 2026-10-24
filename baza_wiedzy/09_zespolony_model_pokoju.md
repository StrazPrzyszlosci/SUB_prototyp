# 09. Zespolony model pokoju i jego granice

Stan: 2026-10-24. Własne wyprowadzenie dla pokoju około 3,7 m w osi x,
4,6 m w osi y i 2,5 m w osi z. Geometria wynika z briefu; pozycje, straty
i rozkład źródeł w tym badaniu są założeniami. Wyniki w
[raporcie 013](../raporty/013_pokoj_i_realne_gabaryty.md).

## Podstawa metody i dziedzina

Rozwinięcie modalne rozwiązuje falowy charakter niskoczęstotliwościowego pola.
W pracy [Meissnera i Wiśniewskiego, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7481690/)
absorpcja pojawia się także w członach sprzęgających mody. W naszym pierwszym
modelu pozostawiamy sztywną bazę prostopadłościanu i diagonalne dodatnie
straty. To rodzina modeli do analizy wrażliwości, a nie odtworzenie rzeczywistych
impedancji ścian. Beton, regały i perforowany sufit nie wyznaczają ich liczbowo.
Dokumentacja [COMSOL, Eigenmodes of a Room](https://www.comsol.com/model/download/1166101/models.mph.eigenmodes_of_room.pdf)
podaje rozwiązanie analityczne pustego prostopadłościanu i rozdziela je od
przewidywania tłumienia. Nie uruchamialiśmy COMSOL ani narzędzi CAD.

Nie stosujemy prawa odwrotności odległości jako transmitancji wnętrza.
Funkcja Greena zawiera mody, ich znaki w miejscu źródła i odbioru oraz fazę.
W każdej analizie trzeba zachować ten sam układ osi. Dawny CSV modów miał
kolejność długość/szerokość/wysokość; obecny model jawnie używa xyz.

## Równania, jednostki i normalizacja

Dla fazorów RMS z konwencją `exp(+jωt)` przyjmujemy `s=jω`. Prędkość
objętościowa źródła `U` ma jednostkę m³/s, a ciśnienie p — Pa.
Sztywna baza cosinusowa jest znormalizowana do średniej objętościowej:

```text
psi_n(r) = product_i [a_ni cos(n_i*pi*r_i/L_i)]
a_ni = 1 dla n_i=0, sqrt(2) dla n_i>0
(1/V) integral_V psi_n psi_m dV = delta_nm
k_n² = sum_i (n_i*pi/L_i)²
omega_n = c*k_n
```

Projektujemy człony modalne:

```text
H_n(r,rs,s) = rho*c²/V * s*psi_n(r)*psi_n(rs)
             / (s² + 2*sigma_n*s + omega_n²),  n != 0
sigma_n = 3*ln(10)/T60_n
p(r,s) = sum_sources H(r,rs,s)*U_source(s)
```

`T60_n` oznacza spadek **obwiedni jednego niedotłumionego oscylatora** o 60 dB,
ponieważ `exp(-sigma_n*T60_n)=10^-3`. Nie jest wynikiem równania Sabine'a
ani pomiarem pogłosu całego pokoju. W badaniu przyjęto trzy dodatnie wartości
wspólne dla modów: 0,2/0,4/0,8 s. Są scenariuszami, nie estymacją z adaptacji.

Każdy człon ma dodatnie straty. Dla źródła i odbioru z takim samym rozkładem
przestrzennym hermitowska część macierzy impedancji portów jest nieujemna.
Wynika to z `Re[s/(s²+a*s+omega_n²)] = a*omega² /
[(omega_n²-omega²)²+a²*omega²] >= 0` dla `s=j*omega`, `a>=0`, oraz
nieujemnych wag i macierzy zewnętrznych `b_n*b_n^T`.
Wzajemność wymaga zamiany zarówno punktów, jak i odpowiadających im apertur.
Nie wystarczy sprawdzić samego modułu odpowiedzi.

## Człon jednorodnego sprężania

Indeks zerowy nie jest rezonansem o niezerowej częstotliwości. To przestrzennie
jednorodne ciśnienie wynikające z bilansu masy/podatności pokoju:

```text
Cab_room = V/(rho*c²)
H_0(s) = 1/[Cab_room*(s + 1/tau0)]
```

`tau0` jest osobnym fenomenologicznym czasem relaksacji ciśnienia. W granicy
`tau0→inf` dostajemy szczelną kompresję `1/(Cab_room*s)`. Dla skończonego tau0
H0 dąży do stałej przy `s→0`; przy `tau0→0` człon zanika. W obliczeniach
nie wyprowadzamy tau0 z samej objętości pokoju. Przy stałym niezerowym U
szczelna komora nie ma ustalonego rozwiązania DC — ciśnienie narasta.
Rzeczywiste źródło membranowe ma `U=Sd*s*x`, co zmienia interpretację tej granicy.

Jednorodna sztywność obciążająca membranę wynosi `Sd²*rho*c²/Vroom`.
Jej stosunek do sztywności gazu w skrzyni 100 l wynosi około 0,00235.
To dotyczy wyłącznie tych dwóch jednorodnych składników. Nie dowodzi, że
reakcję pokoju można pominąć przy rezonansach lub w całej identyfikacji głośnika.
W obecnej kampanii U jest zadane; brak sprzężenia zwrotnego pokoju z ruchem.

## Regularizacja i zbieżność

Punktowa funkcja Greena ma osobliwość przy źródle, a ucięta suma punktowa
może zbiegać wolno. Wprowadzamy rozłożone źródło i uśredniony odbiór poprzez
operator wygładzający Neumanna o współczynnikach:

```text
w_n = exp[-0.5*(a_source²+a_receiver²)*k_n²]
H = H_0 + sum_(n!=0) w_n*H_n
```

To zdefiniowana matematycznie rodzina źródeł, z normalizacją całkowitego U
i odbiciami rozkładu przy ścianach. Parametr a nie jest promieniem membrany
ani gotowym modelem tłoka w odgrodzie. Wybór a i ucięcia kmax trzeba badać
oddzielnie. Zbieżność sumy dla danego a nie waliduje fizycznego modelu apertury.
W skrypcie sprawdzamy `kmax=25/40/55 m^-1` i osobno `a_source=0,10/0,12/0,18 m`.
Nie nazywamy tej ostatniej siatki tolerancją produkcji przetwornika.

Niezależna kontrola jednowymiarowa wykorzystuje zamkniętą funkcję Greena
między sztywnymi końcami i porównuje ją z 40 001 członami szeregu. Ponadto
całkujemy bazę kwadraturą Gaussa, sprawdzamy wzajemność, pasywność portów,
granicę DC, dodatniość parametrów i analityczną symetrię dwóch źródeł.

## Co daje symetria dwóch źródeł

Dla lustrzanych pozycji x i `Lx-x` przy tym samym y,z:

```text
cos(n*pi*x/Lx) + cos[n*pi*(Lx-x)/Lx]
  = [1+(-1)^n]*cos(n*pi*x/Lx)
```

Zgodnie pobudzona para nie pobudza modów o nieparzystym indeksie szerokości.
Nie usuwa to pierwszego modu długości przy około 37,3 Hz: oba źródła na tej
samej głębokości mają ten sam znak sprzężenia z tym modem. Przy centralnym
odbiorze `x=Lx/2` nieparzyste mody szerokości są również niewidoczne dla samego
odbiornika. Dlatego dodatkowa symetryczna sztuka daje w tym idealnym punkcie
6,02 dB przy zachowaniu U każdej sztuki, lecz nie zmienia kształtu krzywej.

Przy stałej **sumie U** oba źródła dostają po połowie; ten sam przykład daje
0 dB względem pojedynczego źródła. Żadna z tych normalizacji nie jest deklaracją
porównania przy jednakowej mocy elektrycznej. Zasilanie i wzajemne obciążenie
promieniowaniem muszą zostać zbadane oddzielnie. Opóźnienie drugiego źródła
wnosi czynnik `exp(-s*delay)`; odwrócenie polaryzacji mnoży go przez -1.

Wnioski dotyczą jednego sweet spotu i jawnego sąsiedztwa diagnostycznego.
Nie wolno rozciągać ich na całe pomieszczenie, inną geometrię, brak symetrii
lub model impedancyjnych ścian bez kolejnej kontroli.
