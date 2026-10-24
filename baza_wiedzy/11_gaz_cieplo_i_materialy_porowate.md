# 11. Gaz, wymiana ciepła i materiały porowate

Stan: 2026-10-24. Własne równania i obliczenia P09/P10; źródła SRC24–SRC27.
Wyniki ilościowe są w [raporcie 016](../raporty/016_gaz_wypelnienie_i_granice.md).
Nie zidentyfikowano materiału w fizycznej skrzyni. Pojemność akustyczna,
geometria i straty pozostają różnymi wielkościami.

## Ośrodek i parametry głośnika

Przyjmujemy idealny gaz o danych pierwotnych p0, T0, R i gamma. Wynikają z nich
`rho=p0/(R*T0)`, `c=sqrt(gamma*R*T0)`, `Kadiab=gamma*p0` i `Kiso=p0`.
Przy ustalonym ciśnieniu zmiana T0 nie zmienia gamma*p0. Zmienia gęstość,
prędkość dźwięku i czas wymiany ciepła dla ustalonego przewodnictwa.
Ogrzanie uwięzionej, stałej masy gazu jest innym eksperymentem.

Mms, Cms, BL i Rms wyprowadzono raz z wejściowych T/S i zachowano przy
zmianie ośrodka. Re także pozostaje stałe, aby wydzielić wpływ gazu;
nie jest to model nagrzewania cewki. Ponowne obliczenie mechaniki z niezmienionego katalogowego
Vas i zmienionej rho*c² wprowadzałoby pozorną zmianę przetwornika.
Do regresji starszego N7 służy dokładnie dopasowany ośrodek `Medium.legacy()`.

## Relaksacja cieplna idealnego gazu

Małosygnałowe równania masy, stanu i ciepła można zapisać przez względne
zaburzenia gęstości xi i temperatury theta. Dla chwilowego strumienia
zwiększającego objętość gazu `Q=Sd*v+G*p`, z `G=1/Ra`:

```text
xi_dot = -Q/V
theta_dot + theta/tau = -(gamma-1)*Q/V
p = p0*(xi+theta)
```

W otwartej komorze bilans energii uwzględnia entalpię transportowaną z masą;
nie wystarczy dopisać przecieku do równania masy, pozostawiając termikę
niezmienionej zamkniętej masy. Powyższy model liniowy daje:

```text
K(s) = p0*(1+gamma*s*tau)/(1+s*tau)
     = p0 + (gamma-1)*p0*s*tau/(1+s*tau)
```

To dodatni model relaksacyjny. W wersji wieloczasowej zastępujemy ostatni
składnik sumą nieujemnych wag o sumie 1. Pozwala to badać rozkład czasów
wymiany ciepła zamiast jednego arbitralnego „bonusu litrów”.
Gdy `omega*tau<<1`, zachowanie zbliża się do izotermicznego; przy
`omega*tau>>1` do adiabatycznego. Przy przejściu pojawia się Im(K)>0,
czyli mechaniczne rozpraszanie energii. F3 nie musi maleć wraz z Re(K).

Granice nie są zamienne: najpierw f→0, potem tau→∞ daje p0; odwrócenie
kolejności daje gamma*p0. W kodzie tau=∞ jest odrębną granicą adiabatyczną
z zamrożoną entropią, a nie bardzo dużym skończonym czasem w równowadze DC.

## Energia, przeciek i stan

Dla mechanicznej reprezentacji komory `F=K0*y+sum(Dk_j*(y-q_j))`:

```text
K0 = Sd²*p0/V
Dk_j = Sd²*(gamma-1)*p0*w_j/V
y_dot = v-G*F/Sd²
q_j_dot = (y-q_j)/tau_j
Egas = K0*y²/2 + sum[Dk_j*(y-q_j)²/2]
```

F jest dodatnio zdefiniowaną siłą przywracającą, a ciśnienie w komorze
`p=-F/Sd`. Dla szczelnej komory z zerowym offsetem początkowym y=x;
redukujemy zbędny stan. Przy całkowicie otwartej komorze gaz nie dodaje
obciążenia. Końce tau=0/∞ i Le=0 także mają zredukowane realizacje.

Po dodaniu elektrycznej i mechanicznej energii:

```text
dE/dt = V*i - Re*i² - Rms*v²
        - G*F²/Sd² - sum[Dk_j*(y-q_j)²/tau_j]
```

Straty przecieku i cieplne występują osobno i są nieujemne. Promieniowania
diagnostycznego nie dodajemy ponownie do Rms ani do bilansu T/S.
Weryfikacja wykorzystuje osobny układ pięciu równań termodynamicznych,
przestrzeń stanu, macierz energii i tożsamości SymPy.

## Materiał ma skończoną pojemność cieplną

Przy gazie i materiale o pojemnościach Cg, Cs:

```text
Cg*Tg_dot = -p0*V_dot - Hgs*(Tg-Ts)
Cs*Ts_dot = Hgs*(Tg-Ts) - Hs0*Ts
```

Temperatury oznaczają tu zaburzenia względem otoczenia. Gdy Hs0=0,
materiał jest izolowany od dalszego otoczenia. Model ma wtedy:

```text
Klow = p0*[1+(gamma-1)*Cg/(Cg+Cs)]
tau_eff = Cg*Cs/[Hgs*(Cg+Cs)]
K(s) = Klow+(gamma*p0-Klow)*s*tau_eff/(1+s*tau_eff)
```

Zatem skończone Cs nie daje dokładnie izotermicznego gazu. Przy Cs=Cg
i gamma=1,4 mamy Klow=1,2*p0. Dopiero Cs/Cg→∞ przybliża p0. To ważne
rozróżnienie między idealnie izotermiczną ścianą poru i prawdziwym włóknem.
Pojemność cieplna elementu może dotyczyć także ścianki skrzyni.
Straty Hgs*|Tg−Ts|²/T0 oraz Hs0*|Ts|²/T0 odpowiadają Im(K).

W obliczeniach usunięto odejmowanie dużych składników wyznacznika przy f→0.
Rozwinięty wielomian i skrócenie wspólnego s zachowują małe straty zamiast
gubić je w odejmowaniu Hgs². Kontrola bilansu wykryła ten problem.

## Pory, lepkość i termika przestrzenna

Używamy analitycznego modelu Zwikkera–Kostena dla prostych okrągłych porów.
Oryginalne równania obejrzano w [dokumentacji COMSOL](https://doc.comsol.com/6.3/doc/com.comsol.help.aco/aco_ug_pressure.05.182.html).
Przy `s=j*omega`, promieniu poru a, porowatości phi i przewodności gazu k:

```text
F(z) = 2*J1(z)/(z*J0(z))
zv = a*sqrt(-j*omega*rho/eta)
zt = a*sqrt(-j*omega*rho*Cp/k)
rho_rigid = rho/[phi*(1-F(zv))]
Kporous = gamma*p0/[phi*(1+(gamma-1)*F(zt))]
```

Przy niskiej częstotliwości `s*rho_rigid→8*eta/(phi*a²)=sigma`:
odtwarzamy przepływ Poiseuille'a. Kporous przechodzi od p0/phi do
gamma*p0/phi. Oryginalny parametr promienia poru nie jest średnicą włókna.
Dla bardzo małych argumentów stosujemy szereg Bessela, a dla dużych
skalowane funkcje jve. Kontrolą jest niezależne rozwiązanie radialnej
dyfuzji pędu i temperatury metodą objętości skończonych.

Model wiotkiego szkieletu zmienia gęstość na:

```text
rho_av = rho_dry+phi*rho
rho_limp = (rho_rigid*rho_av-rho²)/(rho_av+rho_rigid-2*rho)
```

Nie wolno uznawać luźnej włókniny i unieruchomionej maty za ten sam warunek
brzegowy. Żaden z tych dwóch modeli nie zastępuje pełnego poroelastycznego
opisu, gdy szkielet podtrzymuje własne fale. Nie zidentyfikowano takiego
szkieletu dla konkretnego produktu.

## Warstwa i objętość równoważna

Dla przekroju A, grubości d i sztywnego zakończenia:

```text
k_wave = omega*sqrt(rho_eq/K_eq)
Zc = sqrt(rho_eq*K_eq)/A
Zin = -j*Zc*cot(k_wave*d)
C_dynamic = 1/(s*Zin)
V_equivalent = gamma*p0*C_dynamic
```

Warstwy powietrza i materiału łączymy przez dokładną rekurencję impedancji.
To model portu o uśrednionym ciśnieniu, nie gotowy model przepływu wokół
kosza ani dowód montażu głośnika w danej geometrii. Wysokie mody i masy
powietrza wymagają uzgodnienia z P11/P21 oraz z konwencją Mmd/Mms.

V_equivalent jest zespolone i zależne od częstotliwości; jego część
rzeczywista nie zastępuje fizycznego litrażu. Reaktancja bezwładnościowa
i rezonanse portu mogą dać większą lub nawet ujemną Re(V_equivalent),
bez takiej zmiany statycznej podatności. Dla zwykłego modelu
termicznego bez sorpcji i przy nieodkształcalnej geometrii maksymalna statyczna podatność wynosi
`Ciso=V_air/p0`, gdzie V_air uwzględnia wyparcie powietrza przez materiał.
Pełne wypełnienie o phi=0,98 daje w idealnym końcu izotermicznym
odpowiednik 1,4*0,98=1,372 początkowej objętości przy gamma=1,4.
Nie wolno drugi raz odjąć tej samej objętości włókien.

## Dane materiałowe i wyjątek sorpcji

Karta [ISOVER Aku-Płyta](https://www.isover.pl/documents/karta-produktu-pds/kt-aku-plyta-aku-plat-202206.pdf)
deklaruje AFr≥5 kPa*s/m². Jest to dolna granica oporności właściwej,
nie dokładny opór warstwy, promień poru ani pełny zestaw mikrostruktury.
Podane lambda_D=0,037 W/(m K) dotyczy materiału, a nie przewodności gazu k.

Model Delany–Bazleya ma w odczytanej dokumentacji zakres
`0,01<=rho*f/sigma<=1`. Dla tego ograniczenia sigma przy 20–40 Hz górna
granica rho*f/sigma wypada poniżej 0,01. Nie uzasadnia to jego ekstrapolacji
do dolnego basu. ZK jest kontrolowaną alternatywą dla określonej geometrii
porów; nie staje się przez to zidentyfikowanym modelem tej płyty.

Zwiększenie podatności przez adsorpcję/desorpcję jest odrębnym mechanizmem.
W [Venegas et al. 2023](https://dael.euracoustics.org/confs/fa2023/data/articles/000280.pdf)
porowatość pozorna Phi może przekraczać 1; nie jest porowatością geometryczną.
Odczytano i obejrzano oryginalne równanie oraz rysunki. Ich krzywe dotyczą
teoretycznego bass-reflexu, nie pomiaru naszego sealed. Dodatkowa dodatnia
podatność z relaksacją może być pasywna, ale jej czas i amplituda wymagają
identyfikacji. Nie proponujemy tu konkretnego granulatu ani bonusu litrów.
