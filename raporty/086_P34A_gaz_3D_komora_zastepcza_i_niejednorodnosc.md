# Raport 086 — P34A: niejednorodność ciśnienia 3D w komorze o objętości zastępczej

**31 października 2026. Wykonano 90 rozwiązań modalnych**: 3 objętości × 6 częstotliwości × 5 poziomów obcięcia modalnego. To **nie jest** ponowne pełne P21G dla rzeczywistych wkładów P30E — taka symulacja nadal pozostaje do wykonania.

## Pytanie przewodnika

W modelu T/S zamknięta obudowa działa jak sprężyna powietrzna o jednym ciśnieniu. Czy takie uproszczenie zachowuje dokładność do 80 Hz? Żeby oddzielić efekt fal stojących od wpływu rzeczywistych wkładów, obliczono **idealną sztywną komorę** z kolistą membraną o średnicy 355,8 mm. Rozkład ciśnienia wyznaczono z modów własnych Neumanna i Besselowskiego uśrednienia źródła na tarczy.

![RMS przestrzennej różnicy ciśnienia](../wyniki/p34a_modalny_gaz_100_120_150.svg)

## Ważne ograniczenie geometrii

Nominalne wymiary wewnętrzne korpusu: **976×359×456 mm**. Jego geometryczna objętość przed odjęciem konstrukcji wynosi około 159,8 l. Rzeczywiste stany P30E 100/120/150 l osiąga się dzięki przestrzennie rozmieszczonym zamkniętym modułom, wręgom i innym elementom.

**W tym eksperymencie kontrolnym nie odtworzono modułów.** Dla 100/120/150 l przyjęto sztywne **prostopadłościany zastępcze**, zachowując głębokość 359 mm i wysokość 456 mm oraz skracając szerokość do odpowiednio około 611 / 733 / 916 mm. Nie przenosić wyników wprost na docelową komorę ani nie uznawać ich za oszacowanie gwarantowane (dolne/górne) przy przeszkodach.

Źródło: dysk promieniujący na przedniej ścianie, środek x=231, z=250 mm, promień 177,9 mm; jednorodna prędkość tłoka. Równoważne ciśnienie jednorodne p₀ użyto do normalizacji. **C=343 m/s**, wszystkie mody z umownym **ζ=3%**, sztywne ściany, brak wypełnienia i brak pomiarowej kalibracji materiału.

## Równania i metoda

Po odjęciu modu stałego, ciśnienie znormalizowane rozwiązano rozwinięciem Neumanna
```text
p(r)/p0 = 1 − k² Σ_(n,m,l)≠(0,0,0) [2^s · φ_nml(r) · a_nml(source)] /
                                      [ k_nml² − k² + 2j ζ k_nml k ]
k_nml² = (nπ/Lx)² + (mπ/Ly)² + (lπ/Lz)²
a_nml(source) = cos(nπxc/Lx) cos(lπzc/Lz) · 2 J1(R sqrt(kx²+kz²))/(R sqrt(kx²+kz²))
```
gdzie s jest liczbą niezerowych indeksów. Wzdłuż głębokości źródło leży na ścianie y=0. Wyznaczono moduł i fazę ciśnienia na siatce 13×7×9 punktów we wnętrzu. Porównano granice sumowania modalnego N=4,6,8,10,12 na każdej osi.

## Wyniki w paśmie 20–80 Hz: RMS przestrzennej różnicy modułu |p| względem |p0|

| Częstotliwość | 100 l (zastępcze) | 120 l (zastępcze) | 150 l (zastępcze) |
|---:|---:|---:|---:|
| 20 Hz | 0,40% | 0,63% | 1,16% |
| 40 Hz | 1,60% | 2,57% | 4,78% |
| 60 Hz | 3,65% | 5,95% | 11,38% |
| 80 Hz | **6,63%** | **11,05%** | **22,05%** |

Wartości maksymalne lokalnego modułu od p₀ przy 80 Hz: **21,5%, 30,9%, 51,5%** odpowiednio. To **wyniki idealnych prostopadłościanów**, a nie przewidywanie rzeczywistej skrzyni.

Dla trzech modelowych szerokości pierwsza częstość osiowa wynosi około **280,8 / 234,0 / 187,2 Hz**. Idealna *pusta* komora o pełnej szerokości 976 mm ma pierwszą osiową częstość około **175,7 Hz**. To potwierdza, że rozkład przestrzenny może być niejednorodny **nawet poniżej pierwszej częstotliwości osiowej**, szczególnie przy 80 Hz, jeśli port jest lokalny.

## Zbieżność i zastrzeżenia

Między N=10 i N=12 modu/osi przy 80 Hz zmiana diagnostycznego maksimum różnicy amplitudy wynosi **0,26 / 0,28 / 0,51 punktu procentowego** dla 100/120/150 l. Wyniki RMS są stabilniejsze. Nie jest to certyfikat zbieżności całego fizycznego rozwiązania (brak tłumienia porowatego, sztywnych wkładów i sprężystych paneli).

## Co dalej?

1. **P34B**: wykonać właściwe 3D FVM/FEM dla pełnej komory **P30E** z modelowanymi objętościami i położeniem wszystkich wkładów, wręgami oraz matą 50 mm.
2. Obliczyć lokalne rozkłady ciśnienia oraz rzeczywistą siłę działającą na panele jako port obciążeń do poprawionego powłokowego FEM (po zakończeniu P33C).
3. Włączyć straty porowate i podatność ścian z niepewnością; przeprowadzić kontrolę zachowania energii i trzech siatek oraz pomiar impedancji obudowy po budowie.

**Decyzja:** P34A nie zmienia wyboru głośnika ani litrażu. **120 l pozostaje punktem bazowym**. Zjawisko przestrzennej niejednorodności jest istotnym powodem, aby nie kończyć modelu na T/S 0D.

## Odtwarzanie

`python skrypty/p34a_modalny_gaz_3d.py --out wyniki/p34a_modalny_gaz_20261031.json`

Wymaga NumPy i SciPy. Skrypt odtwarza 90 wyników i zapisuje szczegółowy JSON; w repozytorium umieszczono również skrót **18 punktów kontrolnych N=10**.
