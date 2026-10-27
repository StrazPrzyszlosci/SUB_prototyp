# Wspólny obszar ruchu, prądu i temperatury

P24A, 2026-10-27. [Raport 049](../raporty/049_obszar_niezmienniczy_i_koszt_ochrony.md).
Wynik matematyczny dotyczy zapisanej rodziny modeli. Nie potwierdza
dokładności parametrów realnego przetwornika ani gotowej ochrony sprzętowej.

## Pytanie inżynierskie

Jak ograniczyć wejście tak, aby uwzględnić także przejścia w czasie,
zmianę Re z temperaturą i dowolny sygnał ograniczony w amplitudzie?
Osobne sinusy dają użyteczne porównanie, ale nie odpowiadają na całe pytanie.

P24A szuka stałej granicy napięcia fizycznego portu źródła. Nie wymaga
w tym modelu pomiaru stanu w czasie pracy. Ceną tak mocnego założenia
jest konserwatyzm; wynik służy jako punkt odniesienia dalszego projektu.

## Rodzina i jednostki

Mechanika i indukcyjność są liniowe, stałe. Źródło ma Rs, a dodatkowego
zewnętrznego LC nie ma. Jedyną zmianą elektrycznej macierzy stanu jest
Re0*(1+αθ). θ to przyrost temperatury w K. Stan fizyczny to x [m], v [m/s],
i [A], napięcie wejścia u [V].

    xi = (x/Xref, v/(1 m/s), i/Icap)
    xi_dot = A(theta)*xi+b*u
    W = xi.T*inv(X)*xi

X jest dodatnio określoną macierzą. W nie ma jednostki; nie jest sumą
energii mechanicznej i magnetycznej. Parametry M,K,BL,Le,Rms,Re0
to jawne liczby modelu, a nie wartości z określoną tolerancją produkcji.
Le jest tutaj jedną dodatnią stałą. Nie utożsamiamy takiego przybliżenia
z identyfikacją Ld, zespolonego Lgen lub pamięci fizycznego motoru z P12C.

## Warunek na cały przedział temperatury

Wystarczy znaleźć jedną macierz X oraz λ,γ>0 takie, że

    A(theta)*X+X*A(theta).T+lambda*X+gamma*b*b.T <= 0
    X[0,0]<=1, X[2,2]<=1

dla obu końców przedziału θ. A jest afiniczne w θ, więc macierz w środku
przedziału jest kombinacją wypukłą dwóch sprawdzonych macierzy. Stożek
macierzy ujemnie półokreślonych jest wypukły. To argument dla wszystkich
temperatur w zadanym przedziale, także zmiennych w czasie.

Oznaczając `a=xi.T*inv(X)*b`, otrzymujemy

    Wdot <= -lambda*W-gamma*a²+2*a*u
         = -lambda*W+u²/gamma-gamma*(a-u/gamma)²

Jeśli `|u|≤U` i `U²≤lambda*gamma`, zachodzi `Wdot≤lambda*(1-W)`.
Zatem `W(0)≤1` implikuje `W(t)≤1`. Z nierówności Cauchy’ego dla
dodatniej macierzy wynika `|x|≤Xref` oraz `|i|≤Icap`.

## Sprzężenie z temperaturą

Rozpatrywany model cieplny ma wyłącznie straty miedzi:

    Cth*theta_dot = Re0*(1+alpha*theta)*i²-theta/Rth
    Cth>0

Dobieramy Icap tak, by

    Re0*(1+alpha*theta_limit)*Icap² <= theta_limit/Rth

Na górnej granicy temperatury wektor pola jest skierowany do wnętrza
przedziału lub styczny. Na granicy θ=0 jest skierowany do wnętrza.
Razem z warunkiem na W daje to niezmienniczość wspólnego obszaru.
Nie jest to błędne założenie stałej temperatury w modelu ogrzewającej się cewki.

Wymagania dotyczą także stanu początkowego. Sam pomiar temperatury cewki
nie ogranicza dowolnego gorącego węzła innej, wielowęzłowej sieci cieplnej.
Tego rozszerzenia nie należy dopisywać bez sprawdzenia.

## Jak sprawdzono liczby

CVXPY/Clarabel wyszukuje kandydatów. Nie uznajemy statusu `optimal`
za dowód. Parametry modelu, X, λ, γ i U zapisano jako liczby wymierne.
Jedna kontrola sprawdza minory główne 3×3, druga osobno eliminuje Schura/LDL.
Obie działają na dokładnych ułamkach zapisanej rodziny.

972 świadków ma 1944 sprawdzone macierze końców przedziału. Nie jest to
972 pomiarów lub certyfikatów produktów. Siedem wybranych λ na przypadek
i poprawny punkt dopuszczalny nie dowodzą globalnego optimum wejścia.
Odrzucony kandydat także nie dowodzi niemożliwości większego poziomu.

Weryfikator zapisanych świadków wymaga tylko standardowej biblioteki Pythona:

    python3 skrypty/sprawdz_swiadkow_P24A.py

Odczyt zapisanych świadków nie jest nowym niezależnym wyszukiwaniem SDP.

## Co oznacza koszt zapasu

Granica dla dowolnego źródła obejmuje także DC i nietypowe przebiegi.
Może być znacznie niższa niż osobno dopuszczona amplituda ustalonego
sinusa w paśmie 20–80 Hz. Nie wolno nazywać tej różnicy nieuniknioną
stratą każdego limitera. Dalszy projekt może wykorzystać znane pasmo,
przebieg i historię, lecz wymaga to nowej analizy.

Przed fizycznym użyciem trzeba objąć modelem tolerancje i nieliniowości,
wypełnienie i podatne ściany, dodatkowe grzanie, filtrację oraz tor wyjściowy.
Punktowy limit próbek DSP nie jest automatycznie limitem ciągłego napięcia
po DAC. Rekonstrukcja, wzmocnienie i overshoot należą do warunków wdrożenia.
To ograniczenia bezpośrednio wpływające na wybór rozwiązania prototypu.
