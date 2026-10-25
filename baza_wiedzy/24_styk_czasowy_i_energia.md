# Zmienny styk: jak sprawdzić odpowiedź czasową

Wykonane badanie: [raport034](../raporty/034_czasowy_styk_i_pelny_MES.md).

Przekroczenie warunku kontaktu w liniowaniu jest flagą,nie trajektorią
po otwarciu. Model czasowy musi zachować offset docisku i warunki
jednostronnej pracy wszystkich elementów przenoszących obciążenie.
Uszczelka ściskana i śruba rozciągana nie mogą być bezwarunkowo zastąpione
dwustronnymi sprężynami,jeśli odpowiedź zmienia znaki ich sił.

Wypukła energia z max(z,0)² daje ciągłą siłę i styczną zależną od aktywności.
To miękki kontakt sprężysty,bez prawa tarcia i restytucji twardego zderzenia.
Nie identyfikuje lepkosprężystości ani udarowej trwałości realnego materiału.

## Redukcja wymaga kontroli pełnego pola

Baza modów jest ortonormalna względem M. Kierunki statyczne z portów
ciśnienia,siły i rozkładów przestrzennych można dołączyć po usunięciu
rzutu na dotychczasową bazę. Mały błąd amplitudy jednego DOF nie jest
sam w sobie dowodem małego błędu kontaktu lub naprężeń.

Zapisujemy osobno: amplitudy i fazy,obszar bez kontaktu,resztę pełnych
równań,zbieżność bazy,kroku i metody czasu. Propagacja pełnego MES
z historii przygotowanej przez ROM nie jest niezależnym zimnym rozruchem.

## Względny ruch stożka i energia

Masa całego głośnika zawiera już fizyczną poruszającą się część.
Przy zadanym ruchu względnym pojawia się człon mieszany energii
Mmoving*xrelative'*vbasket. Jego pominięcie zmienia wymagany port siły
i może pozostawić pozorny bilans tylko dla części układu.

Gaz z relaksacją można realizować przez stan lag objętości:

```text
lag'=(xi-lag)/tau
p=-(p0/Vb)*[gamma*xi-(gamma-1)*lag]
Ugas=(p0/2Vb)*[xi²+(gamma-1)*(xi-lag)²]
Dgas=(p0/Vb)*(gamma-1)/tau*(xi-lag)²
```

Całkę mocy porównujemy ze zmianą osobno wyprowadzonej energii.
Sprawdzamy także tożsamość symboliczną,ponieważ samo mnożenie reszty
własnego ODE przez prędkość nie jest wystarczająco niezależną kontrolą.

## Szczelina i tłumienie pozostają hipotezami fizycznymi

Pole bez kontaktu nie określa połączonej drogi powietrza. Screening
ciśnieniowego przepływu wymaga geometrii wysokości i długości kanału;
przy ruchomych granicach sprawdzamy również dodatkową objętość i squeeze flow.
Ograniczenie policzone tylko dla zapisanych chwil nie jest certyfikatem
wszystkich momentów ciągłego czasu.

Zamrożony Rayleigh z Kt zawiera kierunki wcześniejszego styku. Jego
dodatnia moc strat nie identyfikuje fizycznego tłumika po otwarciu.
Dlatego porównujemy go z hipotezą wykorzystującą samą masę i płyty.
Wyniki harmonicznych tego modelu pozostają diagnostyką kontaktu;
nie stają się THD głośnika ani dźwięku na podstawie samego FFT.
