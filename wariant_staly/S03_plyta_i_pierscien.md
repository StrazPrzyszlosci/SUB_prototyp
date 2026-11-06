# S03. Zginanie tylnej płyty i docisk pierścienia

Rekomendacja konstrukcyjna: kontynuować wariant A 102 l. We wszystkich rozpatrzonych sposobach podparcia tył A ugina się najmniej. Dla frontu zachować do próby uwięziony pierścień i osiem gwintów M5 z K42. Rozkład docisku zależy na tyle silnie od lokalnej podatności MDF, że przy doborze połączenia należy sprawdzać odcisk wokół pojedynczych śrub oraz szczelność całego obwodu.

## Niezależne obliczenie płyty

Obliczenia przy 1 kPa równomiernego ciśnienia, grubości 22 mm, E = 2 GPa, ν = 0,30 i gęstości 800 kg/m³. Rozpiętość to światło korpusu z S01. Dla obu warunków podporowych przemieszczenie na obwodzie wynosi zero. Przegub pozwala na obrót przekroju, utwierdzenie dodatkowo narzuca zerowe nachylenie.

| Wariant | Ugięcie środka przy utwierdzeniu / przegubie, mm | Pierwsza częstotliwość płyty przy utwierdzeniu / przegubie, Hz |
|---|---:|---:|
| A | 0,043 / 0,162 | 230 / 117 |
| B | 0,071 / 0,229 | 182 / 100 |
| C | 0,050 / 0,182 | 213 / 111 |

Metoda Ritza w teorii cienkiej płyty Kirchhoffa. Iloczyny wielomianów Legendre’a z czynnikiem zerującym wartość lub wartość i pochodną na brzegu. Minimalizacja energii zginania pod obciążeniem powierzchniowym oraz uogólnione zagadnienie własne. Obliczono bazy 4 × 4, 6 × 6, 8 × 8. Skrypt porównuje wyniki dwóch ostatnich baz, trzy wielkości z rozwiązaniem Naviera z S01 i bezwymiarową częstość utwierdzonej płyty kwadratowej z wartością 35,99. Odniesienie do drgań płyt: A. W. Leissa, [NASA SP-160, Vibration of Plates](https://ntrs.nasa.gov/citations/19700009156), dostęp 6 listopada 2026.

W S02 wybrzuszenie tyłu A względem jego naroży wyniosło 0,043 mm. Bliskość wyniku dla utwierdzenia uzasadnia sprawdzenie podatności obrotowej złącza, ale sama nie potwierdza dokładności siatki 3D. Płyta ma nieruchome krawędzie, a w skrzyni także krawędzie przemieszczają się wraz z sąsiednimi ścianami. Częstotliwości płyty i całej skrzyni dotyczą innych układów. W tym obliczeniu pominięto ścinanie poprzeczne, bezwładność obrotową i kierunkowość MDF.

## Wpływ pierścienia na korpus A

Na tej samej siatce 30 mm przeliczono S02 z identyczną masą stali i jednakowymi podporami. Porównano idealnie zespolony pierścień E = 200 GPa z zastępczą warstwą E = 2 GPa o masie stali. W drugim przypadku wyłączono premię sztywności wynikającą ze stalowego materiału, zachowując ciągłość frontu.

| Model | Podatność korpusu, cm³/kPa | Wybrzuszenie tyłu, mm | Trzy najniższe częstotliwości odkształcenia, Hz |
|---|---:|---:|---|
| Pełne zespolenie | 8,49 | 0,0427 | 147 / 171 / 199 |
| Warstwa zastępcza | 8,76 | 0,0424 | 140 / 153 / 163 |

Zmiana podatności wynosi około 3,2%. Trzecia częstotliwość w uporządkowanym widmie zmienia się o około 36 Hz. Identyfikacja odpowiadających sobie postaci wymaga porównania wektorów drgań. Oba warianty są próbą wrażliwości na sztywność; lokalny kontakt, luz kieszeni i poślizg mogą prowadzić do innych wyników.

## Nacisk pod pierścieniem

Osobny model zginania obwodowego wyprostowanego pasa stalowego z okresowymi końcami. Wymiary z [K42](../raporty/K42_pierscien.md): Ø400/358 × 6 mm, średni promień 189,5 mm. Podłoże reaguje tylko na ściskanie. Przyjęto trzy sztywności zastępcze, siłę porównawczą 800 N łącznie i obciążenie rozłożone na łuku 6 mm przy każdej osi. Przypadek siedmiu aktywnych śrub zachowuje tę samą siłę całkowitą przez równomierne zwiększenie obciążenia pozostałych. Wielkość 800 N normalizuje obliczenia; moment dokręcania i rzeczywistą siłę należy dobrać po próbach. Średni nacisk odniesienia liczony po całym pierścieniu wynosi 0,032 MPa.

| Sztywność podłoża, N/m³ | Szczyt / średnia, 8 śrub | Szczyt / średnia, 7 śrub | Udział długości w kontakcie, 8 / 7 śrub |
|---:|---:|---:|---:|
| 2 × 10⁹ | 1,33 | 1,58 | 100% / 91% |
| 2 × 10¹⁰ | 2,53 | 2,97 | 80% / 68% |
| 2 × 10¹¹ | 4,70 | 5,43 | 38% / 33% |

Są to scenariusze bez kalibracji. Model 1D uśrednia nacisk przez szerokość 21 mm. Pomija mimośród osi śrub względem linii środkowej pierścienia (5,5 mm), skręcanie, otwory, kołki, kosz, uszczelkę i nierówności. Udział kontaktu dotyczy stalowego pierścienia z MDF. Szczelność kosza trzeba ocenić osobno. Sprawdzono równowagę sił, zgodność zbioru stref ściskania oraz zmianę szczytowego nacisku po podwojeniu liczby węzłów z 512 do 1024.

## Następna decyzja przed CNC

Przygotować kartę próby pełnego obwodu FR1/FR2 z docelowym MDF i uszczelką. Zmierzyć rzeczywiste grubości oraz luz osiowy pierścienia. Przy stopniowanym, mierzonym docisku sprawdzić obwodowy ślad kontaktu, osiowe przemieszczenie pierścienia, rozrzut między ośmioma osiami i trwały odcisk po odciążeniu. Po relaksacji oraz ponownym montażu sprawdzić docisk i szczelność. Te dane pozwolą dobrać połączenie i skalibrować kontakt, zanim będzie można określić tolerancję kieszeni i wydać front do frezowania.

[Model](s03.py) · [pełne wyniki](s03_wyniki.json) · [wcześniejszy model korpusu](S02_korpus.md). Odtworzenie z katalogu projektu: `OPENBLAS_NUM_THREADS=1 python wariant_staly/s03.py`.
