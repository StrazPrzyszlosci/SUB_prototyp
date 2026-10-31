# Raport 089 — P35A: obciążenia ścian z przestrzennego pola ciśnienia P34B

**31 października 2026. Wykonano 36 pełnych obliczeń pola FV dla 100/120/150 l × 20/40/60/80 Hz × trzy kroki siatki 80/55/36 mm.** Nowością nie jest kolejne liczenie średniego SPL: wyodrębniono **ciśnienie na każdej z sześciu ścian** jako potencjalny warunek brzegowy do późniejszego sprzężenia z poprawionym MES.

![Średnie ciśnienie na sześciu ścianach](../wyniki/p35a_cisnienie_scian_80hz.svg)

## Co zostało rzeczywiście policzone?

Bazą jest odtwarzalny P34B ze sztywnymi ścianami, zmodyfikowany tak, by po rozwiązaniu równania Helmholtza wydzielić ciśnienie na warstwie komórek przylegających do frontu, tyłu, boków, góry i dołu. Dla każdej ściany obliczono:

- **Średnią p/średnie(p) w komorze**, liczona w przybliżeniu z wagą udziału powietrza w komórce brzegowej.
- **Obciążenie jednostkowe w N/Pa średniego ciśnienia**, czyli powierzchniową całkę względnego ciśnienia. To NIE rzeczywista siła bez znajomości ciśnienia w paskalach.
- RMS odchylenia i maksimum lokalne jako diagnostykę przestrzenną.

Równanie `(K−k²M)p=q` i projekcja modu zerowego pochodzą wprost z P34B. Ściany są nieruchome; mata 50 mm pozostaje porowatą **objętością powietrza bez strat**, zatem jej pochłanianie nie zostało policzone. Kosz zastąpiono walcem nominalnych 5 l. Dla obciążeń frontu potrzebna jest dodatkowa poprawka: udział tarczy otworu nie jest dokładnie odejmowany przez siatkę dopasowaną do obwodu kosza.

## Wyniki przy 80 Hz — najdrobniejsza siatka około 36 mm

| Ściana | 100 l: p/p̄ | 120 l: p/p̄ | 150 l: p/p̄ |
|---|---:|---:|---:|
| Front | 0,930 | 0,946 | 0,946 |
| Tył | 1,134 | 1,099 | 1,043 |
| Lewa | 0,697 | 0,773 | 0,617 |
| Prawa | 1,542 | 1,369 | 1,350 |
| Góra | 0,991 | 0,993 | 0,980 |
| Dół | 1,016 | 1,018 | 0,987 |

Wartości liczone są **względem innego średniego ciśnienia dla każdej objętości**. Nie oznacza to, że lewy bok ma bezwzględnie mniejszą siłę w realnym subwooferze ani że którykolwiek wariant ma mniejsze zniekształcenia. Przykładowo dla 120 l modelowa uśredniona prawa ściana ma `p/średnie(p)=1,369` przy 80 Hz, ale nie znamy jeszcze rzeczywistej wartości średniego ciśnienia, tłumienia i podatności MDF.

## Kontrola i ograniczenia

36 wyników zawiera także pola `area_m2`, `force_N_per_Pa`, `rms_relative_percent`, `peak_relative_percent` i liczbę komórek. Przy siatkach 80→55→36 mm zmieniają się reprezentowane pola sztywnych wkładów; **nie można twierdzić, że rozkład rzeczywisty jest zbieżny z jedną wartością**. Użyto wagi otwartej objętości komórki, nie dokładnej całki po powierzchni z geometrii CAD. Nie policzono sił na **ścianach wewnętrznych wręg i wkładów**, które również przenoszą ciśnienie. Taki brak uniemożliwia użycie wyniku jako bilansu sił całej skrzyni.

Jest to obecnie **mapa zależności do następnego modelu, a nie przeniesienie rzeczywistych obciążeń do MES P33B**. Audyt P33C wykazał dwa mody hourglass elementu P33B, więc jego niezweryfikowane ugięcia nie mogą służyć do zatwierdzania obudowy.

## Co trzeba wykonać dalej?

1. Siatka 3D CAD dopasowana do otworu, wszystkich 20 modułów i wręg, z poprawnym obliczaniem powierzchni oraz rozdzieleniem otwartego głośnika od frontu.
2. Model strat porowatej maty na podstawie **zmierzonego oporu przepływowego**. Bez takiego pomiaru należy badać zakresy jako scenariusze, nie jako rzeczywiste tłumienie.
3. Naprawiony i zweryfikowany globalny MES z identycznym podziałem ścian i spoin, a następnie iteracja sprzężenia ciśnienie–przemieszczenie.
4. Po wykonaniu jednej sztuki — pomiar akustyczny i drgań paneli oraz szczelności.

**Reprodukcja:** `node skrypty/p35a_graniczne_cisnienie_FV.js` → `wyniki/p35a_sily_sciany_36_20261031.json`. Bez pakietów NPM, bazuje na geometrii skopiowanej z P34B. **Status: badanie modelowe, nie projekt wykonawczy.**