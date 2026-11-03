# K08 — nominalne mocowanie Daytona: główka, podkładka, długość śruby i osprzęt za frontem

**3 listopada 2026 · obliczenia geometryczne na podstawie karty Dayton RSS390HF-4, normowego łba ISO 4762 i jawnych hipotetycznych części M6. Nie jest to pomiar nośności ani dobór do wykonania. CNC HOLD.**

## 1. Najważniejszy wniosek — nie zgadujmy wymiarów głośnika

[Dayton Audio, rysunek wymiarowy RSS390HF-4, nr 295-468 (PDF producenta)](https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf) podaje: zewnętrzny kołnierz **Ø388,4 mm**, wycięcie **Ø355,8 mm**, osiem otworów w kołnierzu **Ø6,5 mm** na okręgu **PCD Ø368 mm**, grubość kołnierza **10,5 mm** oraz głębokość przetwornika **178 mm**. Cztery żebra są widoczne, ale ich pełna geometria przestrzenna oraz przestrzeń przy terminalach nie są zwymiarowane. **Producent nie wybiera rodzaju kotwienia w MDF 44 mm.**

![Oryginalny rysunek wymiarowy Daytona — boczny widok, kopia na serwerze dystrybutora Speaker&Co; nie rysunek FSzP](https://www.speakerenco.nl/images/uploaded/295-468_3.jpg)

*Źródło grafiki: Dayton Audio, RSS390HF-4, arkusz wymiarowy 295-468; obraz reprodukowany przez [Speaker&Co](https://www.speakerenco.nl/dayton-rss390hf-4). Oryginalny kompletny [PDF producenta](https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf) obejmuje także widok kosza od tyłu z rozmieszczeniem 8 otworów. Grafika jest osadzona **z zewnętrznego serwera**, a nie przedstawiona jako nasz prototyp ani skopiowana do plików binarnych repozytorium. Weryfikacja pełnej aktualności wymiarów u producenta jest konieczna przed wykonaniem.*

## 2. Krawędź otworu i kontakt łba

Oś śruby znajduje się `(368−355,8)/2 = 6,1 mm` poza otworem i `(388,4−368)/2 = 10,2 mm` od zewnętrznej krawędzi metalowego kołnierza. To **dwie różne odległości**: istotne dla drewna i główki, ale nie identyczne z wytrzymałością połączenia.

Normowo wymiarowany łeb cylindryczny z gniazdem sześciokątnym [ISO 4762 / DIN 912](https://tengtoolsusa.com/blogs/news/socket-capscrews-dimensions-chart): **M5 Ø8,5 / wys.5 mm / klucz 4 mm**, **M6 Ø10 / wys.6 mm / klucz 5 mm** (wymiary nominalne odniesienia, tolerancje i użyty model wymagają audytu). Podkładki Ø10 (M5) i Ø12 (M6) są **przykładowe**, nie zaleceniem producenta.

| Element wokół osi | Średnica obwiedni | Nominalny prześwit do krawędzi wycięcia |
|---|---:|---:|
| Łeb ISO 4762 M5 | 8,5 mm | **1,85 mm** |
| Łeb ISO 4762 M6 | 10 mm | **1,1 mm** |
| Przykładowa podkładka M5 | 10 mm | **1,1 mm** |
| Przykładowa podkładka M6 | 12 mm | **0,1 mm** |
| Przykładowa większa podkładka | 14 mm | **−0,9 mm** (nominalnie wystaje nad wycięcie) |

Wariant Ø12 ma nominalnie tylko **0,1 mm** od wewnętrznej krawędzi, więc *bez tolerancji* nie wolno go uznać za bezkolizyjny. Nie zakładamy, że koniecznie musi leżeć w tej samej płaszczyźnie lub że dostępny jest pełny kontakt łba z żebrowanym kołnierzem. K08 nie modeluje sprężystości kołnierza ani rozkładu docisku.

Dla przykładowego otworu MDF: Ø5/5,5/6/6,4/6,5/6,6 mm nominalny najkrótszy pas drewna od krawędzi otworu do wycięcia wynosi odpowiednio **3,6 / 3,35 / 3,1 / 2,9 / 2,85 / 2,8 mm**. **Otwór kołnierza Ø6,5 mm nie wymusza w drewnie takiego samego wiercenia**. Wybór śruby M5/M6, wkrętu do drewna lub wkładki gwintowanej musi uwzględniać rzeczywisty wymagany otwór oraz wyrywanie i rozwarstwienie krawędzi.

## 3. Ile wynosi śruba przez MDF44 i klocek20?

![Schemat badawczy autora projektu na podstawie wymiarów Daytona i hipotetycznego M6 — NIE CNC](../wyniki/k08_przekroj_zlacze_M6_NIE_CNC.svg)

Zakładamy **tylko do porównania** wariant M6 z przykładową podkładką pod łbem **1,6 mm**, nakrętką o nominalnej grubości **5 mm** (dane referencyjne [DIN934](https://hudsonfasteners.blob.core.windows.net/specs/MetDin934.pdf)) i śrubą, której długość mierzymy **od spodu łba**, a nie łącznie z łbem. **Nie wybrano jeszcze typu nakrętki ani miejsca wbudowania gwintu.** W scenariuszu A nakrętka zaczyna się za samym frontem MDF44, w scenariuszu B **za klockiem o dodatkowych 20 mm**.

Minimalna długość dla hipotetycznego przejścia przez komplet części i **pełne 5 mm grubości nakrętki** wynosi:

- A — nakrętka od razu za MDF: `44 + 10,5 + 1,6 + 5 = 61,1 mm`; przykładowa śruba **65 mm** ma teoretyczny nadmiar 3,9 mm.
- B — nakrętka dopiero za klockiem MDF20: `44 + 20 + 10,5 + 1,6 + 5 = 81,1 mm`; przykładowa śruba **85 mm** ma teoretyczny nadmiar 3,9 mm.

Dla przypadku B **M6 × 85** (nominalnie): od tylnej powierzchni całego frontu wystaje koniec trzpienia **28,9 mm**, w tym 20 mm założonego klocka, 5 mm nakrętki i 3,9 mm nadmiaru. To interesująca zgodność ze stosowaną w K04 zastępczą bryłą **28,8 mm** — różnica 0,1 mm — ale NIE dowodzi, że K04 przedstawiał taki właśnie prawdziwy osprzęt ani że szerokości boczne są takie same. Elementy rzeczywiste mogą zajmować inną przestrzeń i zupełnie inaczej kolidować z wkładami.

**38,1 mm** śruby **1½″ z gotowego zestawu 1/4″-20 260-778**, wykorzystanego przez innego konstruktora [w galerii Parts Express](https://projectgallery.parts-express.com/speaker-projects/dayton-subwoofers/), nie przechodzi nawet przez sam front **44 mm** (a jeszcze pozostaje kołnierz 10,5 mm). Podobna rodzina łącznika jest inspiracją, ale ta **długość** nie pasuje do naszego wariantu. 1/4″-20 to nie M6; średnic i skoku gwintów nie należy zamieniać bez zmiany nakrętki.

## 4. Decyzja konstrukcyjna po K08

**S-front (priorytet do zaprojektowania i prób):** osadzenie złącza obsługiwanego od frontu tak, aby nie dodawać za tylną powierzchnią klocka20 nadmiernie wystającej nakrętki i śruby. To może ułatwić serwis wkładów, ale szczególnie mocno wymaga sprawdzenia wyrywania, średnicy otworu pod wkładkę, rozwarstwienia 2,8–3,6 mm pasa MDF, utraty docisku przy wielokrotnym dokręcaniu i faktycznej przestrzeni na gniazdo.

**N-late (wariant alternatywny):** śruba przelotowa z zachowaną wewnątrz nakrętką lub nośnikiem zabezpieczonym przed wypadaniem. K08 wyjaśnia potrzebę dłuższego łącznika (M6x85 dla **konkretnych** hipotez B) i możliwość gabarytu ok. 28,9 mm za MDF, lecz nie pokazuje, jak po zamknięciu skrzyni założyć i obsługiwać tę nakrętkę ani jak zmienić stan 120 → 100 l.

**Najbliższe odtwarzalne zadania:** (1) dobrać 1–2 katalogowe, dostępne od frontu wkładki gwintowane o *rzeczywistych* średnicach otworów i długościach osadzenia, (2) zastąpić w planerze K04 pryzmat 28,8 mm obrysem prawdziwej, wybranej części, (3) przygotować makietę 0° (kolizja ID16) i 180° (narzędzie i ściana), (4) porównać próbki MDF44 + klocek20, (5) dopiero po wynikach zdecydować o osprzęcie i bilansie litrażu. Bez próby fizycznej i realnych zamków wkładów nie wolno zatwierdzić wykonania. **CNC HOLD.**

[Skrypt źródłowy K08](../skrypty/k08_nominalne_mocowania_dayton.py) · [Dane obliczeń i warianty długości](../wyniki/k08_nominalne_mocowania_dayton.json) · [Regresja CI](../.github/workflows/k08-fastener-geometry.yml) · [K07](K07_serwis_wkladow_i_audyt_mocowan.md).
