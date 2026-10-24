# 10. Niepewność, korelacje i odporność decyzji

Stan: 2026-10-24. Metoda zastosowana w [raporcie 015](../raporty/015_niepewnosc_globalna_i_odpornosc.md).
Rozróżniamy: niepewność nominalnych danych, niepewność postaci modelu,
błąd numeryczny i wybór kryterium. Nie mają tej samej interpretacji.

## Zmiennymi powinny być parametry pierwotne

Dla dodatnich M, C, B, R, Re, Le i Sd można obliczyć:

```text
omega_s = 1/sqrt(M*C)
Fs = omega_s/(2*pi)
Qes = omega_s*M*Re/B²
Qms = omega_s*M/R
Vas = rho*c²*Sd²*C
Qts = 1/(1/Qes+1/Qms)
```

Zmiana C porusza równocześnie Fs, Qes, Qms i Vas. Niezależne zmienianie
wszystkich tych T/S niszczy informację o wspólnej identyfikacji. Dopuszczalna
jest jawna rodzina różnych fizycznych parametrów, lecz nie wolno nazywać jej
zmierzonym rozrzutem egzemplarzy. Ścisła spójność tożsamości T/S również
nie dowodzi, że katalog dobrze opisuje konkretny egzemplarz.

Dwa opublikowane egzemplarze zachowujemy jako wspólne wektory. Ich otoczka
po pojedynczych współrzędnych tworzy dodatkowe kombinacje, których nikt nie
zmierzył. To może być świadomie konserwatywny zbiór scenariuszy, ale nie
zwiększa liczebności populacji pomiarowej. Przykład Scan32 w P06 pokazuje
różnicę między zakresem F3 wspólnych zestawów a sztucznych narożników.

## Miara obliczeniowa a rozkład wiedzy o produkcie

[JCGM 101:2008](https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf)
opisuje propagację przypisanych rozkładów wejściowych i uwzględnianie
zależności wspólnym rozkładem. Same końce dowolnie przyjętego zakresu nie
ustanawiają znanej tolerancji produktu. Uzasadnienie wiedzy wejściowej jest
osobnym zadaniem od poprawnego wykonania generatora liczb.

Można zdefiniować jednostajną miarę na umownym prostopadłościanie i zbadać
własności funkcji modelu względem tej miary. Taki eksperyment ma wartość
naukową, jeżeli jest tak nazwany. Średnia, kwantyle i częstości są wtedy
cechami wybranego projektu obliczeń. Nie stają się prawdopodobieństwem
spełnienia wymagań fizycznego głośnika bez uzasadnienia rozkładu wejść.
Równomierne ważenie mnożnika i równomierne ważenie jego logarytmu dają
inne miary; wyników nie wolno traktować jako niezależnych od tej decyzji.

## Czułość lokalna i globalna

Pochodna w jednym punkcie mówi o lokalnym otoczeniu. Dla ograniczenia
`min(limit_V,limit_I,limit_X)` zmiana aktywnego ograniczenia tworzy załamanie.
Zerowa pochodna względem BL w punkcie ograniczonym X nie dowodzi, że BL
nie ma znaczenia w całej dziedzinie. Trzeba kontrolować krok pochodnej
i wykonać analizę globalną.

Indeksy Sobola dla niezależnych czynników i wybranej miary μ:

```text
S_i = Var_mu(E_mu[Y|X_i])/Var_mu(Y)
ST_i = E_mu[Var_mu(Y|X_~i)]/Var_mu(Y)
```

Wynik zależy od Y, μ i zakresów. W P06 Y to dB równoważnego limitu
osobnego sinusa przy 20/25/31,5/40/63/80 Hz. Nie jest to wskaźnik jakości brzmienia.
Całkowite indeksy obejmują interakcje, więc ich suma może przekraczać 1.
Ujemne małe estymaty pierwszego rzędu są błędem estymacji, nie ujemnym
fizycznym udziałem. Nie przycinamy ich po cichu przed kontrolą zbieżności.

Stosowana implementacja [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.sobol_indices.html)
wymaga niezależnych wejść. Profile kopul liczymy osobno; Sobola nie przypisujemy
niezależnie fizycznym parametrom, które powiązano kopulą. Dopuszczalna jest
analiza niezależnych zmiennych ukrytych, ale to inne pytanie niż przypisanie
udziału każdemu zależnemu parametrowi.

## Cała dziedzina a skończona próba

Skończona próba MC/QMC może dostarczyć kontrprzykładu, ale sama nie dowodzi
nierówności dla wszystkich wejść. Dotyczy to także 8192 wygranych na 8192:
to nie dowód dominacji poza tymi punktami. Wspólne względne zmiany obu
głośników badają przekątną większej dziedziny, a nie wszystkie niezależne
pary możliwych parametrów.

Jeżeli obwiednie ciśnienia są `P_A in [L_A,U_A]`, `P_B in [L_B,U_B]`,
to `L_A>U_B` wystarcza do dominacji A w tej dziedzinie. Nakładanie przedziałów
nie dowodzi, że dominacja nie istnieje, bo obwiednie mogą być za szerokie.
Jeden dopuszczalny punkt z `P_A<P_B` wystarcza do jej obalenia.
Heurystyczny optymalizator może znaleźć taki punkt, nawet jeśli nie osiągnie
globalnego ekstremum lub własnego kryterium końca. Wtedy trzeba odtworzyć
sam punkt niezależnie i sprawdzić jego dopuszczalność.

## Obwiednia elektromechaniczna i pasywność

Dla wybranego sinusa zapisujemy `Zm=R+jX`, gdzie R zawiera wyłącznie
dodatnie straty mechaniczne i przecieku. Dostępna prędkość RMS:

```text
vV = Vmax*B / |(Re+j*omega*Le)*(R+jX)+B²|
vI = Imax*B / sqrt(R²+X²)
vX = omega*Xpeak/sqrt(2)
v = min(vV,vI,vX)
```

Każdą funkcję obejmujemy przedziałem w dodatniej dziedzinie parametrów.
Minimum ograniczeń jest monotoniczne względem ich wartości, co pozwala
złożyć dolne i górne końce bez zakładania niezależności tych funkcji.
Pominięcie ich zależności zwykle poszerza obwiednię.

Osobne ograniczenie wynika z bilansu mocy:

```text
R*|v|² <= V*I-Re*I² <= V²/(4*Re)
|v| <= V/(2*sqrt(Re*R))
```

To ograniczenie nie wymaga strojenia reaktancji ani znajomości BL. Nie jest
limitem termicznym: nie mówi, jaką temperaturę osiągnie cewka ani jak długo
można podawać sygnał. W P06 poprawia górną obwiednię prędkości.

Przeciek dodaje `Kb/(s+a)` do Zm, gdzie `a=1/(Ra*Cab)`. Przepływ netto
jest równy `Sd*v*s/(s+a)` dla zbieżnych faz propagacji. Ustawienie źródeł
przecieku w przestrzeni wymaga oddzielnej funkcji Greena; wspólnofazowy
wskaźnik nie zastępuje P11/P26.

## Arytmetyka i zakres gwarancji

Używamy podstawowych działań, kwadratu i dodatniego pierwiastka w IV;
[mpmath](https://mpmath.org/doc/current/contexts.html#arbitrary-precision-interval-arithmetic-iv)
opisuje gwarancję zawierania i jednocześnie oznacza obsługę przedziałów jako
eksperymentalną. Stałe binarne nominalnego modelu zostały zamrożone jawnie.
Końce ciśnienia rozszerzamy przy konwersji do IEEE. Logarytm dB służy
prezentacji; relacje przedziałów porównujemy w Pa.

Podział dziedziny zachowuje pokrycie, choć nie gwarantuje żądanej ostrości
przy skończonym budżecie. Weryfikujemy objętość podziału, rozłączność wnętrz,
zgodność z niezależnym N7, bilans energii, przypadek Le=0 i wzorzec Sobola
o znanych indeksach. Nie ogłaszamy formalnego certyfikatu całej biblioteki
na podstawie skończonego testu. Nie utożsamiamy precyzji solvera z dokładnością
nieznanego fizycznego parametru.
