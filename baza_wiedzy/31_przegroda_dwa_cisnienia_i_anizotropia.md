# Przegroda: dwa ciśnienia, podparcie i anizotropia materiału

Stan 2026-10-26. Metody i ograniczenia
[raportu043](../raporty/043_przegroda_dwie_komory_i_materialy.md).
Nie są to pomiary fizycznego prototypu.

## Gaz za przegrodą nie znika

Idealnie nieruchoma, szczelna przegroda wyłącza tylną objętość z małego
sygnału przodu. Rzeczywista płyta ugina się, a jej podparcie może przesuwać
całość. Najpierw rozwiązuje się wspólną mechanikę:

    chi(s) = H.T @ inv(K+s*C+s*s*M) @ H

chi ma jednostkę m³/Pa. H rozdziela nacisk na mechaniczne współrzędne.
Jeżeli rama i płyta mają wspólny ruch, ich macierz masy ma człony krzyżowe.
Suma dwóch oscylatorów z całą masą płyty policzoną dwa razy zmienia rezonans.
Dla czterech łat trzeba pozostawić ruchy swobodne pomiędzy łatami, a nie
zastępować ich nieruchomym obwodem.

Dwie komory spełniają:

    Qa = s*Ca*pa + (Gseal+s*chi)*(pa-pb)
    0  = (s*Cb+Gvent)*pb - (Gseal+s*chi)*(pa-pb)

Qa jest dopływem do komory, więc przy ruchu membrany na zewnątrz ma znak
przeciwny do Qmem. To ustala także znak zewnętrznego źródła wentylacji.
Sprawdzaj moc jako sumę strat wszystkich gałęzi, nie sam dodatni moduł Z.

## Sztywność mocowania i granice

Gdy tył jest szczelny, a chi=h jest quasistatyczne, odtwarzana podatność
wynosi Cb*h/(Cb+h). Przy sztywnej przegrodzie h→0 znika, przy bardzo miękkiej
staje się Cb. Dynamika wnosi bezwładność i możliwe ujemne Re(chi_eff).
Nie nazywaj tego ujemną fizyczną objętością. Nie utożsamiaj częstotliwości
suchej płyty z częstotliwością układu po dołączeniu dwóch objętości gazu.

Dla dowolnie małego dodatniego Gseal stan DC może udostępniać cały tył,
choć przy Gseal=0 pozostaje odcięty. Granice DC i zerowego przecieku nie
muszą się zamieniać. Etykieta przewodności odniesionej do100l nie oznacza
stałego rzeczywistego bieguna po zmianie komory.

Tylny wypływ i membrana sumują się zespolenie z przeciwnymi znakami.
Ich formalna współlokowana granica może być zerem, podczas gdy dwa
rozdzielone źródła dają dipolową odpowiedź. Bez sprzężenia zewnętrznego
nie jest to projekt rzeczywistego kanału lub prognoza pokoju.

## Statyka hermetycznego gazu

Przy zadanym ciśnieniu przednim p0*p, końcowym T/T0=theta z tyłu i liniowym
h oznacz epsilon=ubytek tylnej objętości/Vb, lambda=h*p0/Vb. Wtedy:

    epsilon = lambda*(p-theta/(1-epsilon))
    epsilon = 2*lambda*(p-theta) /
              (1+lambda*p+sqrt((1-lambda*p)**2+4*lambda*theta))

Drugi zapis unika odejmowania bliskich pierwiastków. Dopuszczalna objętość
wymaga epsilon<1, ale to nie wystarcza do dziedziny liniowej mechaniki:
sprawdzaj ruch, ugięcie/grubość, naprężenia i prześwity. Zadane ogrzanie
gazu nie jest rozwiązaniem sprzężonego grzania cewki i korpusu.

## Dostęp i rzeczywiste netto

Stały front nie wyklucza regulowanej przegrody zainstalowanej przed klejeniem
korpusu. Wyklucza jednak założenie, że dowolną całą płytę da się później
przełożyć przez otwór. Środkowy wpisany dysk daje konieczny warunek
średnicy otworu podczas dowolnego ciągłego przejścia sztywnego elementu.
Nie rozszerzaj tego dowodu na element elastyczny lub segmentowany.

Rozróżniaj: gaz z przodu, gaz z tyłu, plaster przegrody/uszczelnienia,
bryły usztywnień, masę i objętość włókien oraz osprzęt. Ta sama ilość gazu
nie oznacza tej samej ilości maty przy przesunięciu tylnej granicy komory.
Szczelina geometryczna wypełniona uszczelnieniem nie jest otwartym kanałem.

## Co mówi Em sklejki, a czego nie identyfikuje

Oryginalne tabele producenta podają kierunki, grubość, warunki wilgotności
i produkt. Zestawienie [SRC54/SRC55](../dane/materialy/sklejka_pierwotne_P20B.json)
oddziela powlekane Form/FormPLUS od surowego Birch oraz od Spruce.
Nie przenoś gęstości, adhezji lub układu S2 na inną odmianę.

B=Em*t³/12 jest użytecznym nominalnym wskaźnikiem sztywności pasa.
Nie identyfikuje całego tensora płyty: brakuje sprzężenia Poissona,
skręcania i strat dynamicznych. „Planar shear” Gr nie jest automatycznie
modułem Gxy do modelu ortotropowego. Wysoki Em wzdłuż nie kompensuje
każdego słabego kierunku. Porównanie z założonym MDF nie staje się
eksperymentem w jednakowej wilgotności i nie rozstrzyga jeszcze kleju.

Przy ograniczonym zestawie danych raportuj wskaźnik i braki. Kolejne
rachunki płyt ortotropowych wymagają danych albo jawnej rodziny niepewności;
nie wpisuj wygodnego Gxy/nu jako rzekomej wartości producenta.
