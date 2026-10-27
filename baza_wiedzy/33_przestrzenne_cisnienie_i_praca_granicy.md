# Przestrzenne ciśnienie, praca granicy i bezwładność gazu

P21B, stan 2026-10-26. Metoda badań do budowy. Nie są to pomiary
prototypu ani identyfikacja rzeczywistych strat powietrza i materiałów.

## Po co wychodzić poza jedną wartość ciśnienia

Jednolita średnia może dobrze opisywać zmianę objętości, a pomijać różnice
ciśnienia przy poszczególnych ściankach. Sprawdzamy oba skutki osobno.
Mały moduł regulacji objętości jest pierwszą, znaną geometrycznie domeną
do weryfikacji metody. Nie zastępuje głównej komory subwoofera i jej wypełnienia.

Model obejmuje gaz w przestrzeni nie zajętej przez MDF, klej, nakładki i pręt.
Siatki gazu i ciała mają wspólne powierzchnie. Ciśnienie działa normalnie;
pomijamy lepki opór styczny i termowiskozowe warstwy przy ścianach.
Straty są na razie w konstrukcji. Wyższe częstotliwości są diagnostyką tej
idealizacji, bez prognozy rzeczywistych szczytów rezonansowych.

## Równania i jednostki

Konwencja s=jω, fazory RMS. Gaz: gęstość rho i moduł objętościowy Kb.
Po dyskretyzacji trójliniowym Q1/H8:

    A_ij = integral(grad(Ni) dot grad(Nj) / rho)
    C_ij = integral(Ni*Nj / Kb)
    B_aj = integral_boundary(Nsolid_a*Nfluid_j*n_fluid)

Normalna n_fluid jest skierowana z gazu do materiału. B ma jednostkę m².
C ma jednostkę m³/Pa, A — m³/(Pa*s²). Nacisk po obu stronach ścianki
jest uwzględniony na odpowiednich odsłoniętych powierzchniach.

    Ds = Ks + s*Cs + s²*Ms
    Ds*u - B*p = Hext*po
    (A+s²*C)*p = -s²*B.T*u

Ten sam operator B jest użyty w sile i sprzężeniu przyspieszenia; oddzielne
interpolacje mogłyby utracić zgodność pracy. Powinno zachodzić:

    B*1 = Hi
    1.T*C*1 = Ci = Vgas/Kb
    A*1 = 0

Źródła metody: [rejestr SRC56/SRC57](../dane/zrodla/P21B_sprzezenie_i_postac_slaba.json).
Pierwotne wzory przeczytano także na oryginalnej stronie. To własna
implementacja, nie uruchomienie solvera COMSOL lub DOLFINx.

## Średnia ciśnienia nie jest testem całego pola

Przy jednorodnym Kb i szczelnej granicy równanie testowane stałą funkcją daje:

    mean_p = (1.T*C*p)/Ci
    Ci*mean_p + Hi.T*u = 0

Ta tożsamość obowiązuje także dla pola niejednorodnego. Samo zgodne
ciśnienie średnie nie dowodzi, że model0D odtworzył obciążenie każdej ściany.
Raportujemy również:

    pdev = p - 1*mean_p
    pstd = sqrt(pdev.conj().T*C*pdev/Ci)
    prms_volume = sqrt(p.conj().T*C*p/Ci)

pstd opisuje zróżnicowanie przestrzenne amplitud w modelu liniowym.
Nie jest THD lub nową harmoniczną. Duży procent względem bardzo małego
mean_p trzeba pokazać również w Pa i względem zadanej amplitudy zewnętrznej.
Iloraz pstd/prms_volume jest ograniczony przez1; iloraz pstd/abs(mean_p)
może rosnąć przy zerze średniej i nie jest wtedy stabilną miarą błędu.

## Ruch całego modułu i masa gazu

Pełny gaz ma bezwładność. Jego ciśnienie może przekazywać wypadkową siłę
ciału, choć stałe ciśnienie jednorodne daje zerową wypadkową na zamkniętej
powierzchni. Nie wolno po rozwiązaniu wyzerować ruchu sztywnego samej bryły
i nadal używać tak zmienionego u w warunku płyn–ciało.

Do stabilnego obliczenia energii sprężystej można odjąć ruch sztywny,
ponieważ Ks*R=0. Pełne przemieszczenie pozostaje jednak w Ms, B.T*u,
pędzie i pracy nacisku zewnętrznego. Masa gazu jest zawarta w równaniu
falowym; nie dopisujemy jej drugi raz jako osobnego ciężarka.

Dla rzeczywistej gęstości i bezstratnego gazu jego przemieszczenie wynosi:

    xi_fluid = grad(p)/(rho*omega²)

Niezależnie całkujemy grad(p) oraz r cross grad(p) po objętości.
Suma pędu liniowego i momentu pędu gazu oraz konstrukcji musi odpowiadać
wypadkowej sile i momentowi zewnętrznego wymuszenia. Te całki objętościowe
są porównywane z pracą na granicy, a nie zastępowane tą samą macierzą B.

## Równomierny nacisk i pole z gradientem

Kontrolne pola zewnętrzne w lokalnych współrzędnych modułu:

    Phi0 = 1
    Phi1 = 1+(x-W/2)/W

Drugi przypadek ma wartości od0,5do1,5razy amplituda modalna.
Jest scenariuszem, nie zmierzonym polem w głównej skrzyni lub pokoju.
Port pracy to:

    Qj = integral_outer(Phi_j * velocity dot inward_normal)

Dla Phi0 przepływ jest minus pochodną objętości obrysu. Dla Phi1
jest uogólnionym przepływem energii i zawiera także pracę ruchu całej bryły.
Nie wolno przeliczyć jego admitancji na „litry gazu” ani użyć jak zwykłego
równoległego elementu podatności w modelu głównej komory.

## Energia i wzajemność

Przy Y=s*Hext.T*u i jednostkowych kolumnach wymuszenia:

    Hermitian(Y) = omega² * U.conj().T * Cs * U

Gaz bez strat nie zużywa średniej mocy w cyklu. Ma jednak energię:

    Efluid_compression_avg = 0.5*p.conj().T*C*p
    Efluid_kinetic_avg = 0.5/omega²*p.conj().T*A*p

Wartość1/2 dotyczy średniej energii dla fazorów RMS; nie dodaje się jej do
średniej mocy strat. Macierz odpowiedzi jest wzajemna: chi.T=chi, co jest
innym warunkiem niż hermitowska dodatniość mocy. Zbieżność, pasywność i
wzajemność są sprawdzane osobno.

## Stabilny średni mod i granica0D

A ma znane stałe jądro Neumanna. Dla bardzo dużej skali A bezpośrednie
mnożenie A przez prawie stałe p może wzmacniać błąd zaokrągleń.
Rozdzielamy p=1*pbar+eta, z ograniczeniem 1.T*C*eta=0. Osobny mnożnik
Lagrange'a pozwala zachować rzadkie macierze i dokładny średni mod.
Wersję tę porównujemy z pełnym standardowym blokiem przy fizycznej skali1.

Formalne powiększenie A przy stałym C odpowiada zmniejszaniu efektywnej
gęstości przy stałym module objętościowym. Gaz traci bezwładność,
zmienność ciśnienia zanika, a model przechodzi do skalara Ci.
Nie jest to fizyczne ogrzewanie powietrza lub tolerancja producenta.

Mała częstotliwość nie zastępuje tej granicy przy każdym wymuszeniu.
Swobodna bryła obciążona siłą z gradientu ma ruch rosnący jak1/omega².
Gaz przyspiesza z nią, a jego gradient ciśnienia może pozostać skończony
w transmitancji na jednostkę amplitudy. Wiodące zróżnicowanie wynosi
rho*abs(F_per_Pa)*sigma_x/(mdry+mgas). W rzeczywistym wymuszeniu mały ruch
wymaga zmniejszania amplitudy zomega² lub dodania podpór.

Skalarny model Ci wraz z suchą masą konstrukcji pomija ten wkład masy gazu.
Model zredukowany może go odzyskać odpowiednią macierzą masy dodanej.
Nie dodaje się jej jednak drugi raz tam, gdzie gaz3D jest już rozwiązany.
To rozróżnienie dotyczy bezwładności, a nie samej podatności sprężania.

## Odniesienia przed interpretacją wyników

- Operator pojedynczego elementu porównujemy z niezależnym iloczynem
  macierzy1D Kroneckera, również dla silnie rozciągniętej komórki.
- W pustej sztywnej komorze porównujemy mody z analitycznym prostopadłościanem.
- Przy zadanym ruchu jednej ściany porównujemy ciśnienia z rozwiązaniem
  jednowymiarowej fali, także przy zerze ciśnienia wejściowego.
- Sprawdzamy różne siatki, pełny blok i wydzielony mod średni, pracę,
  pęd, wzajemność oraz formalne przejście do0D.

Są to skończone weryfikacje rodziny modeli. Nie identyfikują rzeczywistej
lepkości przyściennej, strat cieplnych, kleju ani mocowania. Dalsze badanie
dotyczy głównej komory z regulacją i wypełnieniem, gdzie wymuszenie modułu
oraz jego reakcja muszą pochodzić ze wspólnego pola.
