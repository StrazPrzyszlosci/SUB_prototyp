# 14. Nieliniowy napęd, współenergia i sprzężony gaz

Stan: 2026-10-24. P12/P13: równania i wykonane rodziny warunkowe przed
budową. Dane bazowe T/S pochodzą z katalogów; kształty nieliniowości
z konfiguracji kampanii są założeniami. Nie są zmierzonymi charakterystykami
24 produktów. Wynik zależy również od temperatury, historii i identyfikacji.

## Siła zawieszenia: sieczna i styczna

[KLIPPEL, sekcja3, oryginalna strona7](https://www.klippel.de/fileadmin/_migrated/content_uploads/Loudspeaker_Nonlinearities%E2%80%93Causes_Parameters_Symptoms_01.pdf)
definiuje Kms(x) jako sztywność **sieczną**, Fs(x)/x. Wzór Fs=Kms(x)*x
różni się od Fs=integral Kms(x)dx. Do kontroli lokalnej sztywności używamy
pochodnej dFs/dx; do energii całki Fs dx. Zmiana definicji zmienia mechanikę.

Dla q=x/Xref w naszej rodzinie:

```text
Ksec(x)=K0*(1+k1*q+k2*q²+k4*q⁴)
Fs(x)=Ksec(x)*x
Ktangent(x)=K0*(1+2*k1*q+3*k2*q²+5*k4*q⁴)
Us(x)=K0*Xref²*(q²/2+k1*q³/3+k2*q⁴/4+k4*q⁶/6)
```

K0=1/Cms, w N/m; wykres źródłowy N/mm wymaga mnożnika1000.
Wystarczający warunek globalnie dodatniej stycznej dla k2>0 i k4≥0 to
k1²<3*k2. Dopuszczamy też k1=k2=0. Warunek jest celowo wystarczający,
nie klasyfikuje wszystkich możliwych dodatnich wielomianów. Dodatnia
sztywność nie jest modelem zderzenia z ogranicznikiem, pełzania ani histerezy.

## BL(x): wzajemne sprzężenie elektromechaniczne

```text
BL(x)=BL0*exp(b1*q-b2*q²-b4*q⁴)
F_PM=BL(x)*i
e_PM=BL(x)*v
```

Ten sam BL występuje w sile i przeciwnej SEM. Pominięcie jednej zależności
narusza wzajemną wymianę mocy. Dodatni kształt wykładniczy jest naszą
rodziną analityczną, nie dopasowaniem do każdego kosza. BL0 oznacza wartość
w x=0; przy b1≠0 nie musi być maksimum charakterystyki.

## Strumień, indukcyjność różniczkowa i współenergia

Wybieramy funkcję strumienia skojarzonego lambda(x,i), a nie samą dowolną
tabelę „Le”. Jednostki: lambda w Wb·zwój, L w H, współenergia w J.

```text
lambda = Lsigma*i + Lp(x)*Is*tanh(i/Is)
Lp(x)=Lp0*exp(l1*q+l2*q²)
Ld=partial(lambda)/partial(i)=Lsigma+Lp*sech²(i/Is)>0
Wco(x,i)=integral_0^i lambda(x,j) dj
       = Lsigma*i²/2+Lp*Is²*log(cosh(i/Is))
Frel=partial(Wco)/partial(x)
Emag=i*lambda-Wco
```

Dodatnia Lsigma zapewnia dodatnie Ld także przy formalnie dużym prądzie.
Is→∞ daje liniowy w prądzie strumień, lecz nadal zależny od położenia.
Le katalogowe przy1kHz jest tylko wejściem odniesienia: nie identyfikuje
Lsigma/Lp/Is. Nie utożsamiamy indukcyjności siecznej lambda/i z różniczkową Ld.

```text
Vdrive=Re*i+Ld*di/dt+[BL(x)+partial(lambda)/partial(x)]*v
M*dv/dt=BL(x)*i+Frel-Fs-R(v)*v+Sd*(p_inside-p0)
dEmag/dt=i*Ld*di/dt+[i*partial(lambda)/partial(x)-Frel]*v
```

Znak siły porównujemy z kierunkiem x i umiejscowieniem źródła w schemacie,
nie z samym znakiem symbolu w cudzej gałęzi obwodu. Dla L niezależnego od i
w naszej konwencji Frel=0,5*i²*dL/dx. Pominięcie Frel daje defekt energii
−Frel*v. Dla nieliniowego prądu trzeba użyć całki współenergii; wzór
0,5*i²*dL/dx nie jest ogólny.

## Szczelny gaz z poruszającą się membraną

Przyjmujemy x>0 na zewnątrz i Vg=V0+Sd*x>0. Masa gazu jest stała,
m=p0*V0/(R*T0), a temperatura kąpieli T0 stała. Bez przecieku i pary wodnej:

```text
p_inside=p0*(T/T0)/(Vg/V0)
dT/dt=-(gamma-1)*T*Sd*v/Vg-(T-T0)/tau
Fgas=Sd*(p_inside-p0)
```

Rozwiązujemy ruch, prąd i temperaturę jednocześnie; ruch nie jest zadany.
Tau=0 redukuje temperaturę do T0. Tau=∞ daje koniec adiabatyczny z ustaloną
entropią początkową. Dla tau>0 skończonego temperatura jest stanem.
Nie dodajemy sztucznej małej tau w miejscu dokładnej redukcji.

Energia użyteczna względem otoczenia (dostępność) wynosi:

```text
Agas = p0*V0*[r-1-log(r)]
       +p0*V0/(gamma-1)*[theta-1-log(theta)]
r=Vg/V0; theta=T/T0
dAgas/dt=-Fgas*v-Dheat
Dheat=p0*V0/[(gamma-1)*tau]*(theta-1)²/theta >= 0
```

Funkcja u−log(1+u) jest nieujemna dla u>−1. Jej szereg zapobiega
utracie cyfr przy małym ruchu. Znormalizowany stan temperatury usuwa
również odejmowanie niemal równych dużych wartości T i T0.

Suma energii mechanicznej, zawieszenia, pola magnetycznego i gazu spełnia:

```text
dE/dt=Vdrive*i-Re*i²-R(v)*v²-Dheat
```

W granicy bez strat energia jest stała. Dodatnie straty dają nierosnącą
energię bez wymuszenia; samo to nie dowodzi jedynej stabilnej orbity
okresowej przy dowolnym wymuszeniu. Osiągnięcie powtarzalności cykli na
siatce nie zastępuje analizy Floqueta ani badania wszystkich gałęzi.

Stała tau przy zmianie Vb oznacza zmianę H=m*cv/tau. Nie opisuje bez zmiany
tej samej ilości materiału w różnych skrzyniach. Podawane temperatury są
temperaturami **gazu**, nie cewki. Re i mechanika pozostają zamrożone.

## Co liczymy i czego jeszcze nie zidentyfikowano

W tym etapie Mms/Rms zachowują sens parametrów efektywnych T/S. Nie
dodano ponownie masy ani strat promieniowania z P11. Brakuje pełnego
czasowego operatora reakcji frontu; pozostaje on jawny przy integracji.
Pole z ruchu jest diagnostyczną normalizacją monopola4π, 1m, RMS:

```text
p_n = -rho*Sd*(n*omega)²*x_n*exp(-j*n*omega*r/c)/(4*pi*r)
```

Stosunek harmonicznych ciśnienia nie jest stosunkiem harmonicznych x:
każda n-ta harmoniczna dostaje n². Przy wysokich harmonicznych rzeczywista
membrana nie musi być źródłem kompaktowym. Wymagana będzie osobna analiza
operatora promieniowania/kierunkowości; te liczby nie są THD gotowego subwoofera.

[LSI3](https://docs.klippel.de/db-lab/latest/transducer-parameter-identification/lsi3/lsi3.html)
stosuje także elementy L2/R2 dla prądów wirowych i identyfikację z sygnału.
Bez absolutnego odniesienia nie otrzymuje się wszystkich mechanicznych
parametrów w SI. Nie implementowaliśmy całego identyfikatora KLIPPEL.

**Nowe źródło:** karta Purifi NAB-01 pokazuje indukcyjność oznaczoną na osi
L_gen(x) dla30/100/300/1000/3000/10000Hz. Nie utożsamiamy tego oznaczenia
automatycznie z Ld=partial(lambda)/partial(i). To dowód zależności
częstotliwościowej wielkości źródłowej, nie
uzasadnienie stałego Le=0,62mH w całym basie. Dodatkowe pasywne gałęzie
i rozdzielenie parametrów pozornych od strumienia są kolejnym eksperymentem.
Krzywych przykładowego głośnika z instrukcji nie przenosimy na naszych kandydatów.

## Kompensacja i zakres wnioskowania

Rozwinięcie adiabatycznej siły gazu ma dodatni człon x²:

```text
Fgas=-gamma*p0*Sd²/V0*x
     +gamma*(gamma+1)/2*p0*Sd³/V0²*x²+...
k1_cancel=gamma*(gamma+1)/2*p0*Sd³*Cms*Xref/V0²
```

Przy dodatnim k1 człon kwadratowy zawieszenia może go skompensować.
To tożsamość rozwinięcia przy x=0, nie likwidacja wszystkich rzędów.
Zbadano pełne ODE dla k1 o znaku przeciwnym, zerowym i wyliczonym.
Zmiana Vb przesuwa warunek, a skończona wymiana ciepła dodaje pamięć:
nie istnieje z tego automatycznie jeden optymalny kształt dla całego pasma.

Bibliografia/fakty i ograniczenia odczytu:
[SRC31–34](../dane/zrodla/P12_P13_nieliniowosci_i_luki.json).
[Stan źródeł24modeli](../dane/przetworniki/dostepnosc_nieliniowych_P12.json).
Kod: [model](../skrypty/model_nieliniowy.py),
[niezależne kontrole](../skrypty/sprawdz_naped_nieliniowy.py),
[kampania](../skrypty/analiza_napedu_nieliniowego.py),
[kompensacja](../skrypty/analiza_kompensacji_gazu.py).
