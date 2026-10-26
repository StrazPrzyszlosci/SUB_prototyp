# 30 — Wkłady: objętość, gaz i mocowanie

**Wyprowadzenie i symulacja:** [raport 042](../raporty/042_regulacja_Vb_i_wklady_wypornosciowe.md).

Wkład masywny wyłącza prawie cały swój obrys, lecz jego masa może być
duża. Wkład pusty ma własne ściany, gaz i drogi przecieku. Geometria
nie wystarcza do określenia zmiany podatności akustycznej komory.

## Dwie podatności i przeciek

Niech chi będzie podatnością objętościową ścian, Ci=Vi/(kappa*p0)
podatnością gazu wkładu, a G jego admittancją przecieku. Dla małych sygnałów:

    pi/p = (G+s*chi)/(G+s*(chi+Ci))
    Ymodule = s*Ci*(pi/p)

Wkład szczelny daje Cmodule=chi*Ci/(chi+Ci). Wkład otwarty przywraca Ci.
Przy dowolnym G>0 DC różni się od granicy najpierw hermetycznej.
W komorze głównej odejmujemy obrys, a potem dodajemy ten port. Osobne
dopisanie całego gazu Vi drugi raz byłoby podwójnym liczeniem.

Przy chi=a−j*b, b≥0 i stałym g≥0:

    Re(Ymodule) = omega²*Ci²*(g+omega*b)
                  / [(g+omega*b)²+omega²*(a+Ci)²] >= 0

Nie wymaga to dodatniej Re(chi) w całym paśmie. Ujemna dynamiczna
reaktancja lub równoważna objętość przy rezonansie nie jest ujemnym
fizycznym litrażem albo aktywnym źródłem energii.
W bezstratnej granicy g=b=0 mianownik może zniknąć: w biegunie nie ma
skończonego sinusoidalnego stanu ustalonego. Nie interpretujemy tego jako
ujemnej rezystancji lub poprawnego skończonego wyniku solvera.

## Kanał z masą jest inną rodziną niż sam opór

Krótki kanał ma opór i bezwładność. Po podstawieniu G(s)=1/Zneck(s)
otrzymujemy rodzinę rezonatora. Niskoczęstotliwościowa bezwładność
rozwiniętego przepływu w rurce kołowej wynosi 4/3 masy przepływu tłokowego;
nie wolno przenosić współczynnika 6/5 z wcześniejszej szczeliny płaskiej.
Końce, geometria, straty i nieliniowa separacja przepływu są odrębne.

Wyniku przy znormalizowanym 1 Pa nie przenosimy automatycznie na setki Pa.
Trzeba zapisać amplitudę, Mach, Reynolds i przemieszczenie cząstek/r.
Umowny ekran małej amplitudy nie jest normą ani pomiarem rzeczywistej wady.

## Montaż i podparcie są elementami modelu

Przekątna mniejsza od otworu potwierdza tylko przejście w danej orientacji.
Droga może kolidować ze ściągiem lub wcześniej umieszczonym modułem.
W P20A sprawdzono pełne odcinki translacji i odwróconą kolejność demontażu.
Nie dowodzi to globalnego maksimum pakowania lub możliwości ruchów z obrotami.

Jednorodne ciśnienie na zamkniętej bryle ma zerową wypadkową siłę.
Obciążenia paneli i ich złączy nadal istnieją. Mocowanie od przyspieszeń
zależy od całkowitej masy, CG, rozstawu i podatności podpór. Luźny docisk
może zniknąć przy rezonansie; model trzymający na rozciąganie nie opisuje
rzeczywistego stukania po otwarciu kontaktu.

Formalna częstotliwość modułu z jednolitym gazem może leżeć powyżej
wewnętrznych modów akustycznych. To granica interpretacji modelu, a nie
potwierdzenie bardzo wysokiej częstotliwości rezonansu rzeczywistego wkładu.
