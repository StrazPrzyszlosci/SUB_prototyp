# Port wzmacniacza, tłumienie i wykonalność ograniczeń

P22A, 2026-10-27. Własny model obwodu i wyprowadzenia. R/L/C są scenariuszami,
bez przypisania do konkretnego modułu. [Raport 047](../raporty/047_port_zrodla_tlumienie_i_bilans.md).

## Najpierw trzeba wskazać miejsce pomiaru wielkości

Napięcie źródła Thevenina, napięcie terminali głośnika, prąd wzmacniacza
i prąd cewki to odrębne wielkości. Bez dodatkowego obwodu dwa prądy mogą
być równe, a idealne źródło wymusza napięcie terminali. Dodanie przewodów
lub filtracji wyjściowej zmienia te relacje.

W badanym obwodzie szeregowym Rs/Ls i równoległym Cp:

    Vs = Vt+(Rs+s*Ls)*Is
    Is = Id+s*Cp*Vt
    Vt = (Re+s*Le)*Id+BL*v
    (Rms+s*Mms+K/s)*v = BL*Id

Pojemność może oddawać energię do obciążenia w części cyklu. Dlatego
moduł prądu źródła może być większy lub mniejszy od modułu prądu głośnika.
Nie należy zakładać, że limit Is automatycznie jest tym samym limitem Id.

## Co daje sam rezystor źródła

Przy Le=Ls=Cp=0 dodanie Rs zmniejsza elektromagnetyczną część tłumienia:

    damping = Rms+BL²/(Re+Rs)
    Q = sqrt(M*K)/damping

Q rośnie z Rs. Nie zwiększa się przy tym mechaniczna częstotliwość
własna sqrt(K/M). Ogólny układ RLC może mieć więcej biegunów, więc pojedynczy
Q jest wtedy jedynie jawną projekcją uproszczonego modelu.

Przy każdym f>0 pasywny liniowy głośnik ma Re(Zdriver)>0. Pochodna
`d|Zdriver+Rs|²/dRs=2*(Re(Zdriver)+Rs)>0` dowodzi, że sam rezystor nie
poprawia obwiedni napędu przy tych samych limitach Vs/Is/X. Nie wolno
rozszerzać tego dowodu na dowolny filtr LC, źródło aktywne lub grzanie.

## Energia jako kontrola całego obwodu

Dla dodatnich Le, Ls, Cp i liniowej mechaniki:

    E = (K*x²+M*v²+Le*Id²+Ls*Is²+Cp*Vt²)/2
    dE/dt = Vs*Is-Rs*Is²-Re*Id²-Rms*v²

Średnio w ustalonym sinusie energia magazynowana nie rośnie. Moc czynna
wejścia równa się sumie strat. Kontrola dotyczy zgodności modelu, a nie
znajomości realnego Rs, strat rdzenia lub wewnętrznej pętli wzmacniacza.

## Dlaczego nie można po prostu obciąć prądu w równaniu ruchu

Poniższy rachunek jest **analitycznym warunkiem dla osobnego uproszczenia**:
bez zewnętrznego LC, z Le>0, sterowanym napięciem terminali ograniczonym
do ±Vmax i granicą prądu cewki ±Imax.

    Le*dId/dt = Vt-Re*Id-BL*v

Przy Id=+Imax należy wymusić dId/dt≤0. Jest to wykonalne tylko wtedy, gdy
istnieje Vt w przedziale napięciowym spełniające

    Vt <= Re*Imax+BL*v
    -Vmax <= Re*Imax+BL*v

Przy Id=-Imax wymagamy dId/dt≥0:

    Vt >= -Re*Imax+BL*v
    BL*v <= Vmax+Re*Imax

Duża SEM od ruchu może zatem uniemożliwić jednoczesne dotrzymanie limitu
napięcia i prądu na danej granicy. Zastąpienie stanu indukcyjności funkcją
`clip(Id)` usuwałoby energię bez wyjaśnienia fizycznej drogi jej przepływu.
To motywacja dla P22B/P24: model sterowania, SEM, energii, nasycenia
i ochrony, a nie dowód gotowego zabezpieczenia. Dodatkowy L/C wymaga
warunków dla właściwych stanów i portów.

Do czasu takiego badania liniowa obwiednia osobnych sinusów pozostaje
porównaniem V/I/X. Nie jest gwarancją zachowania przy impulsie, rozruchu,
regeneracji energii lub produktach IMD powstających po filtrze wejściowym.
