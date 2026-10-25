# 15. Pamięć cewki, siła i identyfikowalność indukcyjności

Stan analizy: 2026-10-25. P12C rozszerza rodziny P12/P13 bez zmiany ich
wcześniejszych wejść i wyników. To modelowanie przed budową. Źródła i
pochodzenie odczytów: [SRC35 i SRC33](../dane/zrodla/P12C_definicja_Lgen_i_sila.json).
Lokalne x cewki jest jej wychyleniem; nie jest osią x geometrii pokoju.

## Co oznacza L_gen

[Risbo et al., AES141/2016, równanie6](https://purifi-audio.com/documents/content/WT1Pkt9-SxijAvNyifNN4Ao2a2)
definiuje zespoloną wielkość dla cewki zablokowanej w pozycji x:

```text
Lgen(s,x) = [Zblocked(s,x)-Re]/s
Re(Lgen(jw)) = Im(Zblocked)/w
Im(Lgen(jw)) = -[Re(Zblocked)-Re]/w
```

Nie jest to automatycznie indukcyjność różniczkowa partial(lambda)/partial(i).
Oryginalny wykres4 karty Purifi NAB-01 ma na osi **|L_gen|**. Jego odczyt
nie identyfikuje osobno części rzeczywistej, fazy i strat. Nie wolno
traktować krzywej modułu jako samej Im(Z)/omega.

## Pasywna pamięć w zablokowanej pozycji

Dla dodatnich L_instant,Lj i tauj:

```text
Zblocked(s)=Re+s*Linstant+sum[s*Lj/(1+s*tauj)]
Lgen(s)=Linstant+sum[Lj/(1+s*tauj)]
Rj=Lj/tauj
```

Część rzeczywista Zblocked jest co najmniej Re. To dodatnia rodzina
relaksacji, nie jedyny możliwy model prądów wirowych. Skończona liczba
gałęzi może przybliżać rozproszone widmo; stała tau nie opisuje histerezy
magnetycznej i nie identyfikuje miejsca wydzielania ciepła w konstrukcji.

Przy x stałym każda gałąź ma filtr G=1/(1+s*tau). Zmiana geometrii
(x zależnego od czasu) wymaga również określenia siły i całego napięcia
indukowanego. Poprawna impedancja zablokowana nie zamyka tego zadania.

## Dlaczego samo L2–R2 nie wystarcza do policzenia siły

Dla tau niezależnego od x źródłowy wzór18 daje:

```text
F = 0.5*Linstant'(x)*i²+0.5*L2'(x)*i*(G*i)
```

Zastosowanie do pomocniczego L2 wzoru dla niezależnej fizycznej cewki
daje zamiast tego człon 0.5*L2'*(G*i)². To kontrola **NAIVE**, która może
pozostawać pasywna. Nie jest przez to prawidłowym modelem mechaniki motoru.
Pasywność jest koniecznym sprawdzeniem bilansu, nie niezależną walidacją siły.

Przy narzuconym i=Ipeak*cos(omega*t) i nieruchomej pozycji obie wersje
dają tę samą składową DC. Dla samego członu pamięci różnią się jednak H2:

```text
H2_FLUX/H2_NAIVE, amplituda = sqrt(1+(omega*tau)²)
roznica faz = atan(omega*tau)
```

Dlatego zgodność samego DC i impedancji nie wykrywa tego błędu.
Zreplikowano równanie i skok prądu0,5→1A w znormalizowanym czasie t/tau.
Nie odtwarzano pomiarów4″DUT ani danych MagNet z artykułu.

## Własna realizacja sprzężona z ruchem

Przyjmujemy Lj(x)=Lj0*a_j(x)², a_j=exp[(c1*q+c2*q²)/2],q=x/Xref,
i stałe tauj. Współrzędna j_j jest pomocniczą pamięcią strumienia
w odniesieniu do geometrii x=0; nie jest zmierzonym prądem w metalu.

```text
j_j_dot = [a_j(x)*i-j_j]/tauj
lambda_total = lambda_0(x,i)+sum[Lj0*a_j(x)*j_j]
Frel = Frel_0+sum[Lj0*a_j'(x)*i*j_j]
Efield = Efield_0+0.5*sum[Lj0*j_j²]
Deddy = sum[Lj0/tauj*(a_j*i-j_j)²] >= 0
```

W równaniu elektrycznym występuje pochodna **całego** lambda_total:

```text
V=Re*i+BL*v+Ld_0*i_dot+lambda_0_x*v
  +sum[Lj0*(a_j*j_j_dot+a_j_x*j_j*v)]
```

Przy zamrożonej pozycji j_j=a_j*(G_j*i), a siła zgadza się ze źródłowym
wzorem18. Dla ruchu jest to nasza jawna realizacja o dodatniej energii,
sprawdzona także niezależną macierzą sprzężonych induktorów. Pochodna
po x zależy od tego, jakie stany utrzymujemy; nie kopiujemy bez analizy
prądu pomocniczego z obwodu jako wielkości fizycznej. Nie deklarujemy
uniwersalnej identyfikacji dowolnego rzeczywistego motoru.

Z mechaniką i gazem z P13 bilans ma postać:

```text
Edot=V*i-Re*i²-Rms_effective(v)*v²-Dgas-Deddy
```

I²Re opisuje stratę rezystancjiDC. Deddy jest osobną modelową stratą;
nie przypisujemy jej w całości cewce ani konkretnemu węzłowi termicznemu.
To będzie wymagało danych lub scenariuszy w P15/P16.
Nazwa pola mean_structural_loss_w oznacza w kodzie Rms_effective*v²,
nie niezależnie wyizolowaną stratę materiałową. Rms pozostaje efektywne.

## Granice modelu i kolejność przejść

| Dziedzina | Wynik |
|---|---|
| N=0 | Dokładna redukcja do modelu P12/P13 |
| tau→0 | j=a*i; gałąź przechodzi w dodatkową indukcyjność natychmiastową |
| f→0 przy skończonym tau | Lgen→Linstant+sumLj |
| f→∞, skończone tau | Lgen→Linstant; Re(Z) ma dodatkowe straty |
| tau→∞ przed f→0, zerowe j | Gałąź nie reaguje na prąd; zostaje Linstant |
| tau=∞ i niezerowe j początkowe | Stan pozostaje zamrożony; nie wolno go wyrzucić z siły/energii |
| Linstant=0, Re>0 | Dokładna algebraiczna redukcja prądu, bez sztucznego małego L |

Formalny nieskończony zakres częstotliwości sprawdza równania rodziny;
nie jest zakresem pomiarowym rzeczywistej cewki. Wewnątrz modelu czasowego
zachowano również dodatnią objętość gazu i ograniczoną dziedzinę q.

## Co wolno wyznaczyć z wykresu producenta

Zdigitalizowano30punktów Fig4 dokładnej wersji NAB-01:6częstotliwości
i5pozycji. Kalibracja osi jest zapisana jawnie; oś y jest logarytmiczna.
Czarną krzywą odróżniono od cienkiej siatki przez sprawdzenie ciągłych
grup pikseli. Źródłowy PDF i osie obejrzano. Odrzucono automatyczne
tablice punktów wygenerowane przez Firecrawl.

Przedziały odczytu obejmują wyłącznie zadany model pikseli, osi i grubości
linii. Nie są niepewnością pomiarową producenta, tolerancją produkcji ani
rozkładem parametrów populacji. „Typical Performance” nie określa tu
jednoznacznie, które dane są pomiarem, a które symulacją.

Dla jednej gałęzi można wyprowadzić dokładnie:

```text
|Lgen|²=A+B/[1+(f/fc)²], A>=0, B>0
(Yi²-Yj²)/(Yj²-Yk²)
 = [(fj²-fi²)/(fk²-fj²)]*[(fc²+fk²)/(fc²+fi²)]
```

Konieczne przedziały fc² z różnych trójek danych są sprzeczne.
Obliczenie na liczbach wymiernych wyklucza **wszystkie dodatnie fc** tej
jednogałęziowej rodziny dla zapisanych przedziałów, a nie tylko skończoną
siatkę biegunów. Nie odrzuca fizycznego motoru ani modeli z dodatkowymi
gałęziami; nie obejmuje nieznanej, pełnej niepewności źródła.

Znaleziono trójgałęziowe modele spełniające odczyty i nominalny konieczny
warunek Re(Zblocked156Hz)≤4,7Ω z tej samej karty. Wyszukiwanie wielostartowe
nie dowodzi globalnego minimum liczby gałęzi: brak dopasowania N=2
w naszej kampanii nie jest dowodem jego niemożliwości.

Faza20Hz pozostaje modelową ekstrapolacją poniżej najniższych danych30Hz.
Dwa różne dopasowania mają różną fazę i stratę przy tych samych
dopuszczonych modułach. Pochodna zespolona po x tym bardziej nie wynika
z samego modułu:

```text
Lgen=M(x)*exp(j*phi(x))
|partial_x Lgen|² = [M'(x)]²+[M(x)*phi'(x)]²
```

Osobna dodatnia rodzina R–L pokazuje stały moduł przy100Hz i niezerową
pochodną fazy. To kontrprzykład utożsamienia płaskiego modułu z zerową
modulacją siły, nie charakterystyka Purifi.

## Dobór pod brief

Jedna liczba Le ani pasywny schemat nie wystarczają do rankingu niskich
zniekształceń. W porównaniu24baz sprawdzamy jawne hipotezy straty i
biegunów, zmiany tłumienia elektrycznego w Fs oraz zachowanie V/I/X.
Nie uznajemy, że kalibracja jednej liczby zachowuje pełny zestawT/S.
Nieznana częstotliwość/definicja katalogowegoLe pozostaje luką danych.

Kampanie ruchu porównują to samo napięcie i te same efektywne parametry
mechaniczne, z gazem, bez nowej reakcji frontu. To wpływ mechanizmu i
niepewności na model, nie rzeczywiste THD produktów. C18 pozostaje kontrolą10″.
Następny etap: P14/IMD i promieniowanie harmonicznych, z zachowaniem tych
ograniczeń przed końcowym wyborem jednego przetwornika i jednej skrzyni.

Kod: [pamięć](../skrypty/model_cewki_z_pamiecia.py),
[kontrola fizyki](../skrypty/sprawdz_pamiec_cewki.py),
[kampania](../skrypty/analiza_cewki_z_pamiecia.py),
[digitalizacja](../skrypty/digitalizuj_Lgen_Purifi.py),
[identyfikowalność](../skrypty/analiza_ident_Le_i_dopasowania.py),
[audyt wykluczenia](../skrypty/audyt_wykluczenia_1_bieguna.py).
