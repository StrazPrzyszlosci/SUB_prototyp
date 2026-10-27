# Raport 049 — P24A: wspólny obszar ruchu, prądu i temperatury

Stan: 2026-10-27. **Wynik matematyczny dla zadanej rodziny modeli**, uzupełniony
symulacjami. Nie jest to certyfikacja fizycznego głośnika lub zabezpieczenia.

## Wniosek dla prototypu

**Obliczenie i dowód warunkowy:** dla 972 rodzin znaleziono stałą granicę
napięcia źródła oraz obszar stanów, który w określonym modelu utrzymuje
ruch, prąd i przyrost temperatury w zadanych granicach. Wynik obejmuje
**dowolny sygnał o ograniczonej amplitudzie** i wszystkie temperatury
w przedziale, a nie tylko wybrane sinusy lub próbki siatki temperatur.

**Rekomendacja:** użyć tego wyniku jako konserwatywnego punktu odniesienia
przy badaniu ochrony. Nie przyjmować go automatycznie jako końcowej nastawy
wysokiej wydajności. Przykład C02/100 l daje około 4,99 V peak, podczas gdy
osobny sinus może korzystać z większej amplitudy. Ta różnica pokazuje cenę
wybranego wystarczającego warunku. Nie dowodzi, że każda skuteczna ochrona
musi tyle tracić ani że większe wejście jest niemożliwe.

![Stała granica napięcia i cena wybranego zapasu](../wyniki/92_P24A_napiecie_i_cena_konserwatyzmu.png)

C04 i C02 nadal są przykładami. Nie dokonano końcowego wyboru przetwornika.

## Założenia i wykonany zakres

27 konfiguracji × 3 objętości 60/100/150 l × Rth 0,3/0,6/1,2 K/W ×
przyrost 40/80 K × Xref 0,6/1 katalogowego Xmax = 972 rodziny.
Progi to osie scenariuszy, nie zatwierdzona specyfikacja briefu.
Xmax nie jest gwarancją niskiego THD, a przyjęty przyrost temperatury
nie jest dopuszczeniem izolacji, kleju lub materiału cewki.

Model ma stałe M, K, Le, BL, Rms, sztywne ścianki, gaz 0D i brak zewnętrznego LC.
Katalogowe Le reprezentuje tu jedną dodatnią stałą cewkę. Nie identyfikuje
to fizycznego Ld, zespolonego Lgen lub pamięci motoru z P12C.
Re(θ)=Re0*(1+αθ), z umownym α=0,004/K. Ciepło obejmuje wyłącznie miedź:

    Cth*theta_dot = Re0*(1+alpha*theta)*i²-theta/Rth
    Cth > 0

Nie dodano nieznanego grzania od prądów wirowych, zmian BL/Le/K z temperaturą
lub ruchu paneli. Parametry termiczne nie zostały przypisane produktom.
Pula obejmuje STX i wszystkie trzy SB; dawne badania nieliniowe dla 24 baz
nie stają się przez to pomiarami nowych modeli.

[Konfiguracja modelu](../dane/konfiguracje/p24a_wspolny_obszar_niezmienniczy.json),
[warunki ODE i porównań](../dane/konfiguracje/p24a_weryfikacja_i_sygnaly.json),
[tabela972obszarów](../wyniki/p24a_obszary_i_poziomy.csv).

## Model i wspólna elipsoida

Stan fizyczny z=(x, v, i). Napięcie u jest napięciem portu Thevenina przed Rs.
To nie zawsze napięcie zacisków głośnika. P22A pokazuje osobne znaczenie LC.

    xdot=v
    M*vdot=BL*i-Rms*v-K*x
    Le*idot=u-(Re0*(1+alpha*theta)+Rs)*i-BL*v
    xi=(x/Xref, v/(1 m/s), i/Icap)
    xi_dot=A(theta)*xi+b*u
    W=xi.T*inv(X)*xi

Macierz X jest dodatnio określona. W jest bezwymiarową funkcją Lapunowa,
**nie energią fizyczną w J**. Wyszukano X, λ, γ spełniające

    A(theta)*X+X*A(theta).T+lambda*X+gamma*b*b.T <= 0
    X[0,0] <= 1, X[2,2] <= 1
    lambda>0, gamma>0
    U² <= lambda*gamma

Zapis „≤0” dla macierzy oznacza ujemną półokreśloność, nie porównanie
każdego elementu. A jest afiniczne w θ. Sprawdzenie obu końców przedziału
daje więc tę samą nierówność dla każdego θ pomiędzy nimi, także zmiennego
w czasie. Nie zakładamy stałej temperatury w tym dowodzie.

Po domknięciu kwadratu, z a=xi.T*inv(X)*b:

    Wdot <= -lambda*W-gamma*a²+2*a*u
         <= -lambda*W+u²/gamma
         <= lambda*(1-W), gdy |u|<=U

Jeśli W(0)≤1, obszar W≤1 pozostaje niezmienniczy. Nierówność Cauchy’ego
daje |x|≤Xref i |i|≤Icap. Dodatkowo wymagamy dokładnie

    Icap² <= Ihardware²
    Re0*(1+alpha*theta_limit)*Icap² <= theta_limit/Rth

Na granicy temperatury prawa strona równania cieplnego jest niedodatnia.
Na granicy θ=0 jest nieujemna. Wspólny obszar W≤1 i 0≤θ≤θlimit jest zatem
niezmienniczy w zadanym modelu. Jest to warunek na stan początkowy,
nie ochrona każdego dowolnego stanu o nieznanej energii i temperaturze.

## Wyszukiwanie i niezależne dokładne sprawdzenie

Wykonano 6804 próby: 7 wybranych λ na rodzinę. CVXPY1.6.5/Clarabel 0.11.1
wyszukiwały kandydatów w osobnym środowisku. Status `optimal` nie był
kryterium dowodu. Zaokrąglone macierze pomniejszono z marginesem i przyjęto
wyłącznie po dokładnym sprawdzeniu liczb wymiernych.

Pierwsza kontrola bada wszystkie minory główne 3×3. Drugi weryfikator,
napisany osobno i bez importowania kodu wyszukującego, używa eliminacji
Schura/LDL oraz stdlib Fraction. Sprawdził 972 dodatnie X i 1944 macierze
końcowe. Zweryfikował też nierówności termiczne i napięcia.
Trzy próby λ odrzucono; każda rodzina ma innego zaakceptowanego świadka.
Odrzucenie próby nie dowodzi niemożliwości większego poziomu.

Przyjęte granice napięcia wynoszą 1,952715–15,37004 V peak w całej puli
scenariuszy. To nie wyznaczone globalne maksimum. Pełny przykład:
[C02/100l/Rth0,6/80K/Xref0,6](../wyniki/p24a_przypadki/cd01847171b1f5a5/C02_V100_Rth0.6_T80_X0.6.json).
Parametry są zdefiniowanymi liczbami dziesiętnymi modelu; dokładna
arytmetyka nie dodaje dokładności do danych producenta.

[Niezależna kontrola972świadków](../wyniki/p24a_weryfikacja_dokladna_LDL.json),
[pięć tożsamości symbolicznych](../wyniki/p24a_tozsamosci_symboliczne.json).

## Koszt względem osobnych sinusów

11664 punkty porównują wspólny świadek napięcia z osobnym sinusem przy
tych samych Xref i Icap oraz szynach 56,57 V peak. Dla diagnostyki liczymy
zamrożone θ=0 iθlimit. Nie jest to temperatura samogrzania stanu ustalonego.
Geometria: idealny monopol 2π/1 m, ciśnienieRMS, osobne ustalone sinusy 20–80 Hz.
Nie przeliczamy tych liczb na pokój 4,6×3,7×2,5 m jako faktu.

| C02/100l/zimny model | Stała granica świadka | Osobny sinus X/I/V | Różnica kryteriów |
|---|---:|---:|---:|
|20 Hz|83,3769 dB|97,4501 dB|14,0732 dB|
|25 Hz|86,8482 dB|101,327 dB|14,4783 dB|
|31.5 Hz|89,8489 dB|105,341 dB|15,4924 dB|
|40 Hz|91,9585 dB|109,491 dB|17,5328 dB|
|63 Hz|93,4308 dB|107,063 dB|13,6319 dB|
|80 Hz|93,5436 dB|105,808 dB|12,2648 dB|

Przykład ma Rth 0,6 K/W, ΔT80 K iXref 0,6Xmax. Duża różnica jest ceną
konkretnego wystarczającego warunku dla dowolnego wejścia, w tym DC.
Nie jest dowodem nieuniknionego kosztu dowolnego innego limitera.
Znane pasmo wejścia, właściwa realizacja filtrów i sterowanie z pamięcią
wymagają osobnej analizy, zanim wykorzystamy większy poziom.

## Ciągłe trajektorie i temperatura

36ODE obejmuje C02, C04, C05, C11, C26P, C26S, po 3 sygnały i 2 temperatury startu.
Sygnały to sinus 20 Hz, ograniczona suma 20+85 Hz i skok. Vb 100 l, Rth 0,6 K/W,
Cth 200 J/K, czas 0,8 s, ruch i prąd początkowo zero. Cth jest założeniem.
Napięcie źródła nie przekracza wartości zaakceptowanego świadka.

Największe próbkowane W wynosi 0,933941; nie znaleziono
naruszeń granic w tych realizacjach. Uniwersalny wniosek wynika z dokładnych
nierówności oraz hipotez modelu, nie z próbkowania 36 przebiegów.

![Przykład funkcji Lapunowa,ruchu i prądu](../wyniki/93_P24A_obszar_ruch_prad_i_czas.png)

Osobna analityczna obwiednia cieplna używa a=Re0*Icap² oraz
b=1/Rth−αa>0:

    theta_upper(t)=a/b+(theta0-a/b)*exp(-b*t/Cth)

To górne porównanie dla chwilowego |i|≤Icap, nie przewidywana temperatura
głośnika podczas muzyki.23328 wartości dla Cth 50/200 J/K oceniono float;
nie są przedziałami z zaokrągleniem na zewnątrz. Dokładna niezmienniczość
granic została sprawdzona oddzielnymi nierównościami.

![Analityczna obwiednia temperatury i wybrane krótkie przebiegi](../wyniki/94_P24A_temperatura_i_obwiednia_porownawcza.png)

## Granice użycia przy budowie

- Dane T/S i Rth nie identyfikują fizycznego egzemplarza. Wynik nie obejmuje
  nieznanej tolerancji BL/Cms/Le, nieliniowej pamięci lub dodatkowego grzania.
- Granica dotyczy napięcia **ciągłego portu źródła**. Ograniczenie samych
  próbek cyfrowych nie gwarantuje jej po rekonstrukcji DAC, zmianie gainu,
  filtrze wyjściowym lub nieznanym overshoot wzmacniacza.
- Projekt nie zakłada dobudowania własnego kontrolera stanu do miniDSP.
  Wzorzec stałego poziomu jest punktem odniesienia; możliwość wdrożenia
  wymaga zbadania rzeczywistego toru i jego kalibracji.
- ADAM Sub 12/Sub 15 są odniesieniem briefu. Te umowne progi nie zastępują
  uzgodnionych progów odbiorowych lub pomiaru THD/SPL gotowego urządzenia.

## Odtwarzanie

Dokładne sprawdzenie zapisanych świadków nie wymaga CVXPY:

    python3 skrypty/sprawdz_swiadkow_P24A.py

Odtworzenie tabel, ODE, wykresów i raportu korzysta ze świadków:

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_obszary_P24A.py

Nowe wyszukiwanie wymaga opcjonalnego środowiska `requirements_p 24.txt`.
Wznowienie zgodnych 972 zapisów nie jest świeżym niezależnym SDP.
Źródła narzędzi: [SRC62/SRC63](../dane/zrodla/P24A_narzedzia_SDP.json).
Użycie danych, ograniczenia i pliki dowodowe pozostają w osobnym manifeście.

**Najbliższa integracja:** główna komoraP21C, wypełnienie i regulacja,
następnie ochrona z filtrami/sygnałami i szerszą niepewnością. Końcowy
wybór głośnika i skrzyni, PDF oraz Release 1 pozostają otwarte. Rozbudowane
podsumowania opinii powstaną po badaniach, zgodnie z decyzją użytkownika.
