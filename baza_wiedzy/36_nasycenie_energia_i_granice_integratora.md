# Nasycenie źródła, energia i granice integratora

P22B, 2026-10-27. [Raport 048](../raporty/048_nasycenie_SEM_i_stan_pradu.md).
To teoria i symulacja warunkowych rodzin, bez kwalifikacji zabezpieczenia.

## Co pozostaje stanem fizycznym

Przy Le>0 prąd cewki ma dynamikę. Arbitralne obcięcie jego wartości usuwa
lub dodaje energię bez wskazania drogi przepływu. Dlatego nasyca się port
napięcia, a równania wyznaczają prąd i ruch:

    xdot=v
    M*vdot=BL*i-Rms*v-K*x
    Le*idot=u-(Re+Rs)*i-BL*v

Umowny sterownik P22B ma statyczne sprzężenie o skończonym wzmocnieniu:

    u=clip(cmd-G*sign(i)*max(|i|-Ipróg,0),-Vrail,+Vrail)

G ma jednostkę Ω. Nie oznacza szerokości pasma sprzętowej pętli. Taki
sterownik może ograniczyć przekroczenie, lecz nie narzuca `|i|≤Ipróg`.
Nie kontroluje automatycznie wychylenia lub historii cieplnej.

## Zachowanie energii jako wymóg metody

    E=(K*x²+M*v²+Le*i²)/2
    Edot=u*i-(Re+Rs)*i²-Rms*v²

Napięciowy port modelu przyjmuje również u*i<0. W realnym urządzeniu
trzeba ustalić drogę energii zwrotnej; nie wolno przypisać tej idealizacji
każdemu zasilaczowi lub mostkowi klasy D.

Dla stałych dodatnich współczynników implicit midpoint daje tożsamość:

    zmid=(znew+zold)/2
    znew-zold=h*(A*zmid+B*u_mid)
    Enew-Eold=h*(u_mid*i_mid-(Re+Rs)*i_mid²-Rms*v_mid²)

Energia jest oceniana w końcach kroku, a praca w środku. Zapis danych
rozróżnia te czasy. Tożsamość kwadratowa nie oznacza dokładności przebiegu
ciągłego; tę sprawdzają osobne ODE i zagęszczenie czasu.

## Nieliniowy port w środku kroku

Eliminacja liniowego stanu daje `i_mid=a+b*u_mid`. Współczynnik b jest
dodatni; odpowiada dodatniej admitancji obwodu przy rzeczywistym s=2/h.
Funkcja sprzężenia jest nierosnąca w i. Stąd równanie dla u ma jedno
rozwiązanie. Własny wzór zamknięty sprawdzono odrębnie przez brentq.

Nie należy opóźniać sprzężenia o pełny krok i nadal deklarować tej samej
tożsamości energii. Nie należy też zastępować rozwiązania `clip(i)`.

## Pasywność numeryczna nie zamyka wszystkich granic

Dla skalarnego `zdot=-lambda*z`, lambda>0, implicit midpoint ma mnożnik

    r=(1-lambda*h/2)/(1+lambda*h/2)
    lambda*h→∞: r→-1

Metoda jest A-stabilna, ale nie L-stabilna. Bardzo szybki tłumiony stan
może naprzemiennie zmieniać znak zamiast zaniknąć w jednym kroku.
W granicy Le→0 przy stałym h sam bilans energii nie wystarcza do oceny.
Trzeba wtedy zmniejszyć krok, użyć odpowiedniej metody L-stabilnej lub
wyprowadzić i sprawdzić odrębny model algebraiczny.

W tym badaniu Le katalogowych rodzin wynosi 0,5–6,1 mH. Siedem świadków
sprawdzono ciągłym LSODA i krokami 12/24/48/96 tys. na sekundę. Nie jest
to certyfikat całej dziedziny parametrów lub nieliniowego fizycznego motoru.

## Dlaczego sam prąd nie wystarcza

Połączenie prądu, prędkości i wychylenia zależy od częstotliwości oraz
stanu dynamicznego. Głośnik może przekroczyć katalogowe odniesienie ruchu,
choć prąd nie uruchamia pętli. P22B zawiera taki matematyczny świadek.
Poza liniową dziedziną nie nazywamy ilościowego ruchu prognozą produktu.

Lokalny warunek wykonalności na granicy prądu opisuje
[osobny rozdział portu](35_port_zrodla_i_wykonalnosc_ochrony.md).
Stan kinematycznie dopuszczony nie musi być osiągalny przy użytym sygnale
i regulatorze. Rozróżnienie jest konieczne przy ocenianiu ryzyka oraz
projektowaniu P24 z ruchem, prądem, napięciem, ciepłem i rzeczywistą EQ.
