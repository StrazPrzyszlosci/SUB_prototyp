# 12. Nieliniowa termodynamika gazu i wyrównanie ciśnienia DC

Stan: 2026-10-24. P10 dla idealnego gazu, stałego gamma i Newtonowskiej
wymiany ciepła. Wynik ciśnienia wewnętrznego przy zadanym ruchu nie jest
THD konkretnego subwoofera. Pełna dynamika nieliniowego napędu i zawieszenia
pozostaje P12/P13; wynik zbiorczy jest w [raporcie 016](../raporty/016_gaz_wypelnienie_i_granice.md).

## Równanie dla stałej masy

Membrana poruszająca się na zewnątrz zwiększa objętość:

```text
V(t)=V0+Sd*x(t)>0
p=m*R*T/V
m*Cv*T_dot = -p*V_dot-H*(T-T0)
```

Dla H=0 zachodzi `p*V^gamma=const` i
`T/T0=(V0/V)^(gamma-1)` przy początkowej entropii równowagi.
Dla idealnie szybkiej wymiany ciepła T=T0 i `p*V=const`.
Skończone H daje pamięć termiczną i straty. Przy zadanym sinusie x nie
otrzymujemy przez to sinusoidalnego ciśnienia ani zerowej wartości średniej.

## Bilans energii i dostępności

Sama energia wewnętrzna gazu ma człon pierwszego rzędu. Do dodatniego
bilansu małych i dużych odchyleń względem otoczenia użyteczna jest dostępność:

```text
A = m*Cv*[T-T0-T0*ln(T/T0)]
    +p0*V0*[V/V0-1-ln(V/V0)]
dA/dt = (p0-p)*V_dot-H*(T-T0)^2/T
```

A jest nieujemna dla dodatnich V,T i znika w równowadze. Po połączeniu
z mechaniczną i elektryczną energią człon pracy ciśnienia się skraca,
a `H*(T-T0)^2/T` pozostaje dodatnim rozpraszaniem. To tożsamość modelu
idealnego, sprawdzona symbolicznie; nie jest pomiarem H konkretnej włókniny.
W stanie okresowym średnia praca przekazana gazowi jest równa średniemu
ciepłu oddanemu otoczeniu i średniemu ubytkowi dostępności.

## Rozwiązanie okresowe i kontrola niezależna

Dla `V/V0=1+epsilon*sin(u)`, `u=omega*t`, `a=omega*tau`,
`tau=m*Cv/H` oraz `theta=T/T0` równanie ma postać:

```text
theta' = -(gamma-1)*theta*epsilon*cos(u)/(1+epsilon*sin(u))
         -(theta-1)/a
```

Nieliniowy problem upraszcza transformacja
`Z=theta*(1+epsilon*sin(u))^(gamma-1)`. Wtedy:

```text
Z'+Z/a=g(u)/a
g(u)=(1+epsilon*sin(u))^(gamma-1)
Z_n=g_n/(1+j*n*a)
```

To dokładne rozwiązanie wymuszonego stanu okresowego przez szereg Fouriera.
Temperaturę otrzymujemy przez dzielenie Z/g, a ciśnienie przez theta/(V/V0).
Nie jest to liniowy model ciśnienia: nieliniowość wraca w przekształceniu.
Niezależny solver Radau wyznacza warunek okresowy metodą strzelania i
odtwarza temperaturę oraz ciśnienie. Sprawdzamy osobno liczbę próbek FFT,
małą amplitudę, granice adiabatyczną/izotermiczną i bilans cyklu.

## Granica wymiany ciepła nie jest obojętna na czas obserwacji

Dokładnie H=0 zachowuje początkową entropię, więc Z=1 przy wybranym
początkowym stanie V=V0,T=T0. Jeżeli najpierw osiągniemy stan okresowy
przy dowolnym H>0, a potem zmniejszymy H do zera, pozostaje
`Z=mean(g)`, a nie 1. Dla gamma=1,4 i niezerowego epsilon zachodzi
mean(g)<1 z wklęsłości funkcji potęgowej.

Oba limity mają inne średnie temperatury i ciśnienia. Znormalizowane H2/H1
i H3/H1 mogą się w tym końcu zgadzać, bo cała zmienna część ciśnienia jest
przemnożona przez stałą. Zgodność samych procentów harmonicznych nie dowodzi
tożsamości sił i offsetu DC. Duże tau oznacza też długi czas dojścia do stanu
okresowego; nie należy nazywać tej granicy odpowiedzią na krótki burst.

## Temperatura otoczenia a ogrzanie uwięzionej masy

Przy początkowym p0 i różnych T0 masa gazu wynosi `m=p0*V0/(R*T0)`.
Dla ustalonego H zmienia się `tau=m*Cv/H`. Porównanie samych T0 przy
ustalonym omega*tau dawałoby te same bezwymiarowe krzywe ciśnienia i nie
badałoby zmiany szybkości wymiany ciepła. W kampanii użyto zarówno modeli
bezwymiarowych, jak i jawnego scenariusza wspólnego H.

Jeżeli masa pozostaje hermetycznie uwięziona po zamknięciu skrzyni,
powolne ogrzanie zmienia punkt równowagi. Z liniową sprężyną Cms:

```text
Ks*x=Sd*[p0*(Tnew/T0)*V0/(V0+Sd*x)-p_external]
```

W dodatniej dziedzinie objętości lewa strona minus prawa jest ściśle
rosnąca, więc fizyczny pierwiastek jest jedyny. W kodzie stosujemy stabilną
postać dodatniego pierwiastka równania kwadratowego. Wyniki poza katalogowym
ruchem są sygnałem granicy modelu liniowego zawieszenia; nie przewidują
położenia po dotknięciu ogranicznika ani uszkodzenia konkretnego głośnika.

## Akustyczne zamknięcie a powolne wyrównanie ciśnienia

Dla bardzo powolnego procesu gaz z wymianą ciepła jest izotermiczny.
Podatność mechaniczna membrany także magazynuje objętość:

```text
Cab_iso=V/p0
Cmem_acoustic=Sd²*Cms
tau_DC=Ra*(Cab_iso+Sd²*Cms)
```

Nie wolno utożsamiać tego czasu ze stosowanym w N7 `Ra*Cab_adiab`.
W kampanii porównano przybliżenie quasi-statyczne z najwolniejszym biegunem
pełnej realizacji gaz/napęd. Przy szybszym wyrównaniu pojawia się różnica,
bo membrana i prąd nie są już idealnie quasi-statyczne.

Bardzo mały przepływ DC może więc wyrównywać temperaturę/barometrię,
pozostawiając niemal niezmienione zachowanie w 20–80 Hz. To możliwość
projektowa do identyfikacji, a nie dobór otworu na podstawie jednej liczby
fleak. Geometria, bezwładność, nieliniowość przepływu i montaż mogą zmienić
rezystancję. Szczelność regulowanego frontu wymaga odtwarzalnej procedury.

## Zakres wniosków

Harmoniczne ciśnienia gazu przy zadanym ruchu są wkładem do siły na
membranie. Dopiero rozwiązanie sprzężonej dynamiki pozwoli określić, jakie
harmoniczne pojawią się w jej ruchu i promieniowaniu. Nie utożsamiamy
tych wyników z rzeczywistym THD, temperaturą cewki ani dopuszczalną mocą.
Pokój, jego straty i dokładne pozycje pozostają odrębną identyfikacją.
