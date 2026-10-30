# Raport 055 — P29C: kiedy zmienia się wybór i co mieści się w 50 cm

Data: 2026-10-30. Dalsze badanie modelowe po rekomendacji 054.
Nie są to pomiary prototypu ani identyfikacja chłodzenia produktów.

## Nowa kampania

Przeliczono 27 konfiguracji dla 176 pułapów strat miedzi 25–200 W
co 1 W, przy 120 l i napędzie 40 V RMS / 12 A RMS. Zachowano 512
scenariuszy Sobola, 121 częstotliwości 20–80 Hz i wszystkie zakresy P29A.
Osobne sinusy ustalone; równoważny monopól 2π, 1 m, ciśnienie RMS.
Dodatkowo C02: 91 objętości od 70 do 160 l co 1 l, przy 50 W.
To skończona próba stresowa, nie certyfikat całej dziedziny ani rozkład
rzeczywistych egzemplarzy. Nie wolno utożsamiać pułapu Pcu z mocą Pe.

Dla stałych parametrów odpowiedź liniowa pozwala rozdzielić obwiednię:

`L_min(Pcu) = min(A, B + 10 log10(Pcu / 1 W))`.

A to minimum po częstotliwościach i scenariuszach z ograniczeniami V/I/X;
B to minimum dla samego limitu strat 1 W. Operacje minimum są przemienne.
Ta redukcja jest dokładna dla zapisanej siatki i modelu; nie zakłada,
że ten sam punkt siatki zawsze ogranicza obie gałęzie. Parametry zależne
od temperatury pozostają ustalonymi scenariuszami, nie rozwiązaniem termiki.
Porównanie 81 punktów z wcześniejszym pełnym obliczeniem P29A daje
maksymalną różnicę 1,43e−14 dB. Nie stanowi to walidacji fizycznej.

## Wynik i korekta uzasadnienia

| Założony limit strat miedzi | Najlepsze minimum w całej puli przy 120 l |
|---|---|
| 25–26 W na siatce całkowitej | C19 |
| 27–86 W na siatce całkowitej | C02 RSS390HF-4 |
| 87–200 W na siatce całkowitej | C11 RSS390HE-22 |

Przecięcie gałęzi C02/C11 wypada przy **86,813 W**. To granica
konkretnego modelu i wspólnego założenia Pcu, nie zmierzony próg opłacalności
lub bezpieczna moc któregokolwiek głośnika. Faktyczne Rth, Cth, BL(T),
nieliniowości i użyteczny skok mogą przesunąć lub unieważnić tę granicę.
Samo słowo „konserwatywny” nie uzasadnia każdego małego Pcu: przy 25 W
wygrywa inny kandydat. Wybór C02 pozostaje jawnie zależny od scenariusza.

**Korekta reguły objętości z roboczej syntezy:** najmniejszą objętością
na pierwotnej siatce, która traci nie więcej niż 0,2 dB wobec plateau,
jest 100 l, nie 120 l. Na nowej siatce 1 l pierwszy taki punkt to 99 l.
Nie jest to ciągłe optimum: odniesieniem jest maksimum skończonej siatki
70–160 l (95,7968 dB w zdefiniowanym teście).

Zachowano **około 120 l jako start eksperymentu**, a nie jako matematycznie
najmniejszą skrzynię: jedna konstrukcja umożliwia porównanie 100/120/150 l,
a stan środkowy wymaga mniej wkładów niż stan 100 l. Próg 0,2 dB sam
nie dowodzi przewagi 120 l; wybór startu jest decyzją inżynierską.
Skorygowano raporty 053–054 i generator, aby nie odtwarzał błędnego wniosku.

## Limit głębokości obejmuje cały przedmiot

Założone 880×480×500 mm to korpus drewniany. Pozostaje 20 mm do limitu
500 mm na elementy wystające. Nie znamy jeszcze kompletnego obrysu
maskownicy, spoczynkowego wystawania membrany i terminala. Ruch peak,
ugięcie maskownicy i tolerancje muszą zmieścić się we wspólnym bilansie;
20 mm nie jest zatwierdzonym prześwitem ruchomej membrany.

Przy stałych W/H, froncie 44 mm i tyle 22 mm każdy 1 mm skrócenia korpusu
odbiera 0,381216 l brutto. Zachowano rezerwę 8 l i matę phi=0,98.

| Głębokość korpusu [mm] | Budżet wystawania [mm] | Netto z 10 wkładami [l] | Odstęp obecnych wkładów od maty [mm] |
|---:|---:|---:|---:|
| 450 | 50 | 107,41 | −26 |
| 460 | 40 | 111,22 | −16 |
| 466 | 34 | 113,51 | −10 |
| 470 | 30 | 115,03 | −6 |
| 476 | 24 | 117,32 | 0 |
| 480 | 20 | 118,84 | 4 |

Ujemny odstęp oznacza **kolizję ze zdefiniowaną obwiednią maty**;
liczba litrów dla takiego wariantu jest tylko arytmetyczna, nie oznacza
wykonalnego układu. Zero nie zapewnia tolerancji montażowej. Nie wolno
skrócić korpusu i przenieść walidacji P21C3 lub torów montażu bez zmian.
Możliwe drogi to zmiana położeń/wymiarów wkładów, zmiana W/H albo inny
obrys maskownicy; każda wymaga powtórzenia bilansu i obliczeń przestrzennych.
Nie wybrano automatycznie cieńszej maty tylko po to, by ukryć kolizję.

## Macierz kolejnych decyzji

| Kryterium | Dostępne dane | Brakujące dane | Warunek akceptacji | Następny krok |
|---|---|---|---|---|
| Głośnik | 27 konfiguracji, warunkowa przewaga C02 w P29A/C | Rzeczywiste BL(x,T), użyteczny skok, chłodzenie | Zmierzone ograniczenia pokrywają przyjętą dziedzinę; inaczej przeliczyć wybór | Zachować C02 jako rekomendację warunkową i C11 jako kontrkandydata cieplnego |
| Objętość | 99 l spełnia próg modelowy na siatce; regulacja około 100/120/150 l | Wyporność kosza, wręg, mocowań | Dokładny bilans netto zamiast rezerwy 8 l | Domknąć geometrię wewnętrzną i ponownie policzyć port |
| Głębokość | 480 mm korpusu, tylko 20 mm pozostałego obrysu | Membrana, maskownica, terminal, tolerancje | Całkowity obrys ≤500 mm z zapasem dla ruchu | Bilans wymiarowy; po zmianie korpusu ponownie tory wkładów i P21C3 |
| Sztywność | Model frontu 44 mm; wstępny rozstaw podpór | Rzeczywiste wręgi i spoiny, ich kolizje z dostępem | Wspólny model spełnia jawne progi ruchu/naprężeń i montażu | Zintegrować wręgi, front, wkłady i gaz bez podwójnego liczenia mas |
| DSP/ochrona | Stabilne filtry software; wcześniejsze rodziny P24 | Kalibracja napięcia, model X/T nowej skrzyni | Ochrona obejmuje rozruch, clipping i wspólne ograniczenia | Nowy model czasowy z filtrem i pamięcią cieplną; potem pomiary |
| Wypełnienie/pokój | Modele przestrzenne, przybliżone wymiary pokoju | Parametry konkretnej maty i pozycje odsłuchu | Porównanie tych samych stanów przy kontrolowanym napięciu/temperaturze | Pomiary dopiero po budowie; nie przypisywać symulacjom poziomu w sweet spocie |

Najbliższy etap badawczy: wspólny model wręg, torów wkładów i obrysu,
a następnie ochrona czasowa tej geometrii. Wyniki nie zamykają P30 ani
nie upoważniają do końcowego PDF/Release lub zamówienia CNC.

Odtwarzanie: `OPENBLAS_NUM_THREADS=1 python skrypty/wrazliwosc_P29C.py`.
Wyniki: `p29c_grzanie.csv`, `p29c_objetosc.csv`, `p29c_podsumowanie.json`.
Wejścia pochodzą z zamrożonej puli i scenariuszy P29A; nie dodano danych
producentów ani nie zmieniono briefu.
