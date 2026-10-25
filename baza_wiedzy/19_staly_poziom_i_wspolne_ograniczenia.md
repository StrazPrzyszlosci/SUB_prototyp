# Stały poziom i wspólne ograniczenia

Status: matematyka i wykonane modele warunkowe P17, 2026-10-25.
[Raport028](../raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md)
opisuje5184zestawy, dziedzinę i ograniczenia ich zastosowania.

**Różne warunki sterowania:** przy stałym napięciu wzrost Re zmienia
prąd i poziom, jak wP15B. Przy wymaganym utrzymaniu tego samego ruchu
w zamrożonym liniowym napędzie prąd jest zadany przez siły mechaniczne.
Trzeba zwiększyć napięcie. Tego wymagania nie należy mylić z automatyczną
funkcją miniDSP lub realnego wzmacniacza.

**Warunek cieplny:** przy stałym wymaganym I, P0=I²Re0 oraz prawie
Re=Re0(1+alpha*T) pojawia się dodatnie sprzężenie cieplne. Dla portu
Rth warunek stabilności jest1−alpha*Rth*P0>0. Przy zadanym przyroście
i najgorszym przydziale strat pamięci w dwuwęzłowym modelu:
Rth<=T/[I²*(Re0*(1+alpha*T)+Reddy)]. To wymaganie wobec nieznanego
chłodzenia, nie prognoza temperatury produktu.

**Objętość:** dla u=1/Vb, stałego f i tego samego Kgas(s) wymagane I,V
są afiniczne w u. Ich moduły dają wypukłe nierówności kwadratowe.
Każdy limit tworzy przedział, a wspólne warunki są ich przecięciem.
Nie optymalizuj osobnej skrzyni dla każdego f, po czym nie przedstawiaj
sumy takich punktów jako jednej konstrukcji.

**Dziedzina termicznego gazu:** utrzymywanie tau przy zmianie Vb
nie oznacza tego samego H. Jeżeli fizyczna rodzina obudów ma tau(Vb),
współczynniki mogą przestać być afiniczne; trzeba ponownie rozwiązać
problem. Gotowych przedziałów P17 nie przenosi się na dowolne
materiały porowate lub nieszczelności.

**GranicaSdX:** w monopolu przy określonym p i f wymagane X nie zależy
od litrażu. Większa moc i mniejsza sprężystość gazu nie tworzą nowego
Sd*X. Katalogowe definicjeX nie są jednak jednolitym pomiarem THD.
Nominalna granica nie jest automatycznie użytecznym SPL głośnika.

**Rekomendacja:** odróżniać ograniczenie napięcia od ograniczenia
prądu, chłodzenia i ruchu. Sens dopłaty do napędu zależy od aktywnego
ograniczenia. Przed wyborem jednej skrzyni sprawdzić mechanikę,
regulację objętości i miejsce dwóch egzemplarzy w pokoju4,6×3,7×2,5m.
Nie przenosić4pi/1m na sweetspot ani nie dodawać stałego roomgain.
