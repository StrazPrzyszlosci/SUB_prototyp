# Bieżący plan naukowy prototypu

Aktualizacja: użytkownik zlecił [program30pakietów](PROGRAM_30_BADAN.md),
szeroką pulę kandydatów obejmującąSTX i innych producentów, obliczeniowy
dobór kleju oraz końcowy wybór jednego głośnika i jednej obudowy.
KońcowyPDF dopiero po wykonaniu programu bez sprzętu. N7/P08 wykonano
w modelu zredukowanym: [raport009](raporty/009_N7_straty_nieszczelnosci.md).
Poniższy zapisN7 zachowuje wyprowadzenie i zakres, nie oznacza już zadania
nierozpoczętego. Niezamknięte rozszerzenia są opisane w macierzy programu.

Stan 2026-10-23. **Aktywny zakres: wyłącznie fizyka, źródła techniczne,
obliczenia i symulacje potrzebne do budowy** — decyzjaU-010. Główny
[planB+R](PLAN_B_R.md) zachowuje dalsze etapy jako kontekst, ale wyceny,
dobór handlowy, zakupy, narzędzia CAD i dobór toru pomiarowego są odłożone.
ReferencjeSub12/Sub15 zatwierdzone; nie stanowią jeszcze liczbowej specyfikacji.

## Wyniki uzyskane

| Pakiet | Pytanie naukowe | Obecny rezultat | Granica wniosku |
|---|---|---|---|
| N1 | Czy daneT/S są spójne? |4 zestawy, kontrola tożsamości; PDFHF4 wyjaśniaBL13,99 Tm kontra 1 TmWWW | Nadal katalog, bez rozrzutu egzemplarzy |
| N2 | JakVb zmienia odpowiedź i ograniczenia? |24 konfiguracje, Fc/Qtc/F3, impedancja, ruch, prąd i SPL | Model liniowy bez strat skrzyni i termiki |
| N3 | Ile kosztuje cel 20/25/30 Hz z HP? |216 wariantów filtrów/objętości, wspólna kontrola napięcia/prądu/ruchu | Osobne sinusy, pasmo kontroli 10–200 Hz, bez muzyki i limitera czasowego |
| N4 | Jaki wkład nieliniowości ma sprężyna gazowa? |72 przypadki; FFT siły, szeregTaylora i kontrola zbieżności | Zadany ruch; nie rozwiązano nieliniowej dynamiki aniTHD akustycznego |
| N5 | Co powoduje wzrostRe? |72 wiersze pasmowe; Re×1/1,25/1,5 przy zachowaniuBL i mechaniki | Nie znamy temperatury, czasu ani dynamiki grzania |
| N6 | Co wynika z geometrii pokoju? | Częstotliwości idealnych modów i scenariusze room gain | Brak amplitud, strat, czasów zaniku i transferu rzeczywistego pokoju |

Kod i dane są dostępne, a [raport 007](raporty/007_fizyka_nieliniowosci_i_DSP.md)
rozwija nowe wyniki. Nie wyciągamy z nich rankinguTHD, jakości odsłuchowej
lub gotowości produktu do komercjalizacji.

## Wykonany pakiet N7 — zachowane wyprowadzenie strat i nieszczelności

**Pytanie:** jak wrażliwe są odpowiedź, impedancja i ochrona na skończoną
szczelność regulowanego frontu/przegrody oraz dodatkowe tłumienie?

Wejścia: obecne 4 zestawyT/S,24 objętości i model bazowy; bez nowych zakupów
i bez zależności od narzędziCAD. Zbudować model akustycznej podatności
`Cab=Vb/(ρc²)` równolegle z dodatnią rezystancją przecieku `Ra`.
Impedancja mechaniczna obciążenia skrzyni:

```text
Zbox(ω) = Sd² / (1/Ra + jωCab)
τ = Ra Cab
fleak = 1/(2πτ)
```

Model szczelny jest granicą `Ra→∞`; przy skończonymRa obciążenie ma składnik
rozpraszający i zmienia się poniżej częstotliwości relaksacji. Jest to
uproszczony przeciek rezystancyjny, bez bezwładności kanału i nieliniowego przepływu.

Przebieg: najpierw wyprowadzić równania i kontrolę jednostek, potem scenariusze
`fleak=1/3/10Hz` oraz granica szczelna. Są to parametry analizy wrażliwości,
nie stwierdzenie, że skrzynia ma taki przeciek. Porównać 20–80 Hz i niskie pasmo
ochrony; ująć impedancję, ruch i różnicęSPL przy tym samym napięciu.

**Uzupełnienie po kontroli:** nie wystarczy zmienić obciążenia membrany.
Przeciek promieniuje; jego wkład może znosić przednią stronę membrany.
Przy konwencji `Umem=Sd*v` dodatniej na zewnątrz i dodatnim wypływie przez
przeciek model bilansu komory daje:

```text
p_inside = -Umem / (1/Ra + jωCab)
Uleak = p_inside/Ra = -Umem/(1+jωτ)
```

Do całkowitegoSPL sumować **zespolone** wkłady membrany i przecieku
z odpowiednimi odległościami, fazą i wspólną zdefiniowaną geometrią promieniowania.
Pierwszy przypadek kontrolny może traktować oba jako bliskie monopole w4π.
W granicy małego rozstawu `Utotal=Umem+Uleak`; dlaωτ→0 przepływy prawie się znoszą,
a dlaRa→∞ przeciek zanika. Nie sumować samych poziomówdB ani modułów ciśnienia.
Jeśli geometria przecieku nie jest określona, wolno raportować tylko wkład
membrany i impedancję; całkowitySPL oraz wymaganyEQ pozostają nierozstrzygnięte.

Kryteria końca: dodatnia moc strat, zgodność z obecnym modelem w granicy
szczelnej, poprawna niskoczęstotliwościowa suma przepływów, stabilność siatki
częstotliwości i raport różnic. Stop dla wniosków
o konkretnej skrzyni: brak pomiaru przecieku. Nie dobieraćRa tak, aby uzyskać
z góry pożądany wynik. Nie przechodzić automatycznie do konstrukcji ani zakupów.

## Kolejne pakiety po N7

Aktualizacja 2026-10-24: wykonano szeroką pulę 24 modeli / 11 producentów,
globalne granice po Vb, identyfikowalność oraz scenariusze P26/P27 dla pokoju
4,6 × 3,7 × 2,5 m. Bieżący następny krok to P06 z
[programu 30 badań](PROGRAM_30_BADAN.md); poniższa lista N8–N11 pozostaje
historycznym opisem zależności, nie kompletną aktualną kolejką.

1. N8: zakres identyfikowalności modelu cieplnego. Wyprowadzić bilans
   `Cth dT/dt = Pcu − (T−Tamb)/Rth`; wskazać potrzebneRth/Cth, współczynnikRe(T),
   zmianyBL i straty dodatkowe. Bez tych danych tylko scenariusze, bez
   deklarowania temperatur i czasu pracy z samego Pe.
2. N9: zweryfikować definicje liniowościXmax i dostępneBL(x)/Cms(x)/Le(x)
   lub niezależne pomiary wszystkich 4 modeli. Różne kryteria utrzymać osobno.
3. N10: osobna kontrola wybranych przypadków rachunkiem niezależnym od kodu
   bazowego oraz porównanie opublikowanych pomiarów w tych samych warunkach.
4. N11: wyprowadzić naukowe ograniczenia porównania zSub12/Sub15: sygnał,
   pasmo, geometria, czas i kryterium zniekształceń. Brak danych oznacza
   nieporównywalność, a nie domyślny parytet.

## Zasady rozstrzygania

Każdy pakiet kończy się danymiCSV/JSON, wykresem, kontrolą i raportemMD.
Wyraźnie oznaczać: tożsamość modelu, scenariusz, wynik numeryczny, pomiar
producenta i pomiar niezależny. Dokumentować wyniki negatywne i brakujące
parametry. Złożoność modelu zwiększać w odpowiedzi na konkretne pytanie,
a zakres twierdzenia ograniczać dostępnymi wejściami.
