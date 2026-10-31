# Raport 098 — P39A: ponowne obliczenie względnych nacisków na sześć ścian po korekcie osi głośnika

**1 listopada 2026.** Wykonano **36 pełnych, nowych rozwiązań FV** z położeniem głośnika **x=209, z=228 mm w układzie wnętrza** (odpowiada x=231, z=250 mm od zewnętrznych krawędzi MDF). Zestawiono każdy wynik z archiwalnym P35A przy x231/z250 we wnętrzu. Zapisano wszystkie częstotliwości 20/40/60/80 Hz, objętości 100/120/150 l i trzy siatki 80/55/36 mm.

![Naciski po zmianie współrzędnych źródła](../wyniki/p39a_cisnienie_scian_po_korekcie.svg)

## Metoda

Powtórzono model P35A bezstratnego powietrza Helmholtza metodą FV, pozostawiając **sztywne ściany, uproszczony cylinder kosza ~5 l, prostopadłościenne wkłady i wręgi, brak absorpcji maty 50 mm**. Skorygowano wyłącznie współrzędne osi źródła i modelowego kosza. Ciśnienie na poszczególnych ścianach uśredniono z wagami otwartej części komórek brzegowych. To przybliżenie, nie integracja po pełnej powierzchni CAD.

Definicja `p/pmean` to średnie ciśnienie na ścianie podzielone przez średnie ciśnienie w jej komorze. Liczby nie są SPL, THD ani zmierzoną siłą w N; do obliczenia siły potrzeba **fizycznego ciśnienia w Pa**, właściwej powierzchni i prawidłowej geometrii połączeń.

## Wyniki 120 l / 80 Hz / siatka ~36 mm

| Ściana | P35A historyczny p/pmean | P39A po korekcie | Zmiana |
|---|---:|---:|---:|
| Front | 0,945733 | **0,950001** | +0,004268 |
| Tył | 1,098816 | **1,099924** | +0,001108 |
| Lewa | 0,772883 | **0,735469** | −0,037414 |
| Prawa | 1,368966 | **1,383758** | +0,014792 |
| Góra | 0,993341 | **1,007211** | +0,013870 |
| Dół | 1,018311 | **1,006199** | −0,012112 |

Względna niejednorodność RMS całej komory wynosi po korekcie **21,7156%** zamiast **20,4226%** w P35A. Siatka modeluje około **120,03 l** powietrza (stary model około 120,07 l). Przestrzenne zmiany wynikają tylko z przesunięcia zastępczego kosza i źródła w tym modelu — nie z żadnej fizycznej ingerencji w gotowy subwoofer.

### Porównanie trzech objętości przy 80 Hz, siatka 36 mm

| Konfiguracja | RMS pierwotny | RMS po korekcie | Różnica |
|---|---:|---:|---:|
| 100 l | 31,5410% | **32,6719%** | +1,1309 pp |
| 120 l | 20,4226% | **21,7156%** | +1,2930 pp |
| 150 l | 27,1152% | **28,5747%** | +1,4594 pp |

Należy zachować starą historię dla audytowalności. **Nie wolno mieszać nacisków P35A i P39A** w jednym obliczeniu MES bez jawnego opisania konfiguracji.

## Wniosek projektowy i bramki

Korekta układu odniesienia **jest obowiązkowa** we wszystkich przyszłych modelach konstrukcyjno-akustycznych. P39A nadal nie przedstawia realnego kosza, połączeń wręg, tłumienia maty ani sprzężenia z podatnymi ścianami; nie powinien być używany do wyznaczania progów DSP lub wytrzymałości śrub. Kolejne sprzężenie FSI powinno wykorzystywać rzeczywisty CAD kosza i otwór z siatką konformalną, razem z danymi o oporze przepływowym maty.

**Reprodukcja:** `node skrypty/p39a_sciany_FV_po_korekcie.js` → `wyniki/p39a_pola_na_scianach_36_20261101.json` (Node.js, bez zależności NPM; porównuje z zapisanym oryginalnym P35A).