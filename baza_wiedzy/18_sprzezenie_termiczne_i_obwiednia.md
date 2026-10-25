# Sprzężenie termiczne i obwiednia sygnału

Status: teoria i wykonane modele warunkowe P15B, 2026-10-25.
[Raport027](../raporty/027_P15B_sprzezenie_grzania_i_napedu.md)
zawiera2304trajektorie, granice, parametry i niezależne kontrole.

**Wyprowadzenie:** dla napięciaRMS V i stałego biernego tła a+ib:
I=V/(R+a+ib), Pcu=V²R/[(R+a)²+b²]. Prąd maleje ze wzrostem R>0,
lecz Pcu rośnie, gdy R²<a²+b². Nie wolno utożsamiać spadku prądu
z monotonicznym spadkiem grzania w każdym paśmie.

**Sprzężenie wolne/szybkie:** temperatura zmienia R, aktualne R zmienia
prąd i ruch, te zaś zmieniają źródła ciepła i przyjętą konwekcję.
Nie jest to ta sama metoda co zadane na stałe Re×1,25. Uśredniony model
harmoniczny wymaga rozdzielenia skal czasu i odrębnego sprawdzenia
z pełnym audio ODE. Wybrane zgodne świadki nie certyfikują całej dziedziny.

**Granica napięciowa:** przy stałym biernym tle, stałych dodatnich
parametrach cieplnych, Re=R0(1+alpha*T),alpha>0,stałym przydziale
nieujemnego Peddy i grzaniu zależnym tylko od temperatury cewki,
funkcja H(T)/T jest ściśle malejąca od nieskończoności do zera.
Daje to jeden dodatni stan równowagi tego modelu. Nie jest to próg
idealnego źródła prądu ani twierdzenie o dowolnym zaniku chłodzenia,
clippingu, BL(T) i rzeczywistym uszkodzeniu.

**Nieidentyfikowalność:** po transformacji z=b*Tmagnet równania
zastępczej rodziny zP15A nie zależą od b, gdy Pmagnet=0. Dołączenie
Re(T) i tej samej funkcji chłodzenia od prędkości nie usuwa tej
swobody. Osobne Pmagnet zmienia wynik; dlatego strat pamięci nie
przypisuje się do węzłów cieplnych na podstawie ich elektrycznej nazwy.

**Obwiednia:** równy czas włączenia nie oznacza tej samej energii
ciepła. Porównując stany po impulsach, podaj także czas od ostatniego
wyłączenia. Pamięć magnesu oraz dopływ ciepła do cewki mogą trwać
po ustaniu sygnału. Potrzebny jest stan cieplny w czasie, nie tylko
bieżący wskaźnik mocy.

**Kontrola źródła:** w autorskim manuskrypcieSRC42 oryginał s.6 ma
0,0393K^-1dla miedzi. DaneNBS/SRC44 odnoszone do20°C są rzędu0,0039K^-1.
Nie wolno uznać tej rozbieżności za sam błąd ekstrakcji ani przenieść
liczby bez sprawdzenia. Nasze0,004jest parametrem stresowym; nie
ustalono materiału drutu i jego tolerancji dla każdego produktu.

**Rekomendacja dla prototypu:** wymagania napędu i ochrony integrować
z warunkową termiką, jakością danych i niepewnością chłodzenia.
Nie używać tych samych umownych R/C dla24baz jako zmierzonego rankingu
temperatur głośników. BL(T), powietrze skrzyni, lokalne gradienty,
rzeczywiste krzywe i późniejsza walidacja pozostają otwartymi bramkami.
