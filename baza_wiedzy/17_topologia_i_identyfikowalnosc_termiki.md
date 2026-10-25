# Topologia i identyfikowalność termiki

Status: teoria i wykonane kontrole P15A, 2026-10-25. Parametry cieplne
naszych produktów nie zostały zidentyfikowane.
[Raport025](../raporty/025_P15A_topologia_i_granice_termiki.md) zawiera
równania, świadków, granice i warunkowe wymagania chłodzenia.

**Źródła pierwotne:** AN18/SRC40 pokazuje szereg gałęzi R||C.
Rysunek heat_flow/SRC41 pokazuje własne pojemności przy węzłach,
konwekcję i grzanie metalu. Oryginały trzeba obejrzeć: podobne symbole
Rtv/Ctv nie oznaczają tej samej topologii ani tych samych stanów.

**Teoria:** dodatnią dwuwęzłową sieć Cauer można przekształcić na
dodatni Foster zgodny na porcie cewki. Zgodność całej funkcji Zth(s)
nie oznacza zgodności temperatur wewnętrznych. Nie przeliczaj więc
automatycznie zastępczego C na masę miedzi lub stali bez określenia
struktury i zakresu identyfikacji. Źródłowe tau=R*C są poprawne dla
odpowiednich gałęzi Foster; nie są ogólnym wzorem na bieguny Cauer.

**Dowód warunkowej nieidentyfikowalności:** z dodatkowym bezpośrednim
chłodzeniem port identyfikuje kombinacje Cv,a,D,E. Cały przedział
E/D<b<a opisuje różne dodatnie sieci Cauer o identycznym Zth(s), ale
innych temperaturach magnesu i odpowiedzi na jego osobne grzanie.
Konieczne są dodatkowe dane lub fizyczne ograniczenia. Nie jest to
twierdzenie o nieidentyfikowalności każdej zadanej topologii.

**Energia fizycznych węzłów:** przy stałych Cp i otoczeniu
d(Cv*theta_v+Cm*theta_m)/dt=P_v+P_m−theta_v/Rva−theta_m/Rma.
Gałęzie elektromagnetycznej pamięci z P12C nie są automatycznie
fizycznymi węzłami cieplnymi. Dla Rva=inf:
theta_v,ss=Pcu*(Rvm+Rma)+Peddy*Rma, jeśli Peddy trafia do magnesu.
Ta sama łączna moc daje inną temperaturę przy innym przydziale strat.

**Sprzężenie z prądem:** idealne utrzymanie I i liniowe Re(T) daje
próg P0*alpha*Rth=1. Nie jest to limit temperatury ani próg awarii
wzmacniacza/głośnika. Przy zadanym napięciu, zmiennej impedancji,
ograniczeniach napędu i chłodzeniu zależnym od ruchu potrzeba innego
sprzężonego rachunku. Po P15A jest to kolejny etap P15B/P16.

**Granice:** zerowa rezystancja połączenia scala węzły; nieskończona
odcina ścieżkę. Nieskończona pojemność zamraża temperaturę w skończonym
czasie. Granica Cv→0 daje węzeł algebraiczny i może być niezamienna
z t→0. Pełna izolacja cieplna i dodatnia moc wykluczają skończony stan
ustalony; kod nie powinien udawać jego wyliczenia.

**Rekomendacja dla prototypu:** oddzielić znane straty elektryczne od
nieznanego chłodzenia. Tabele wymagań Rth z zamrożonego Pcu są warunkami
projektowymi, nie temperaturą produktu ani zatwierdzonym limitem kleju.
Rzeczywiste hot spoty, identyfikacja R/C i testy po budowie pozostają otwarte.
