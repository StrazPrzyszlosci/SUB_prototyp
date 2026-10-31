# Raport 102 — P40B: 675 kontroli tolerancji i budżetu materiału pierścienia

**1 listopada 2026 — wykonano 675 kombinacji geometrycznych** referencyjnego pierścienia pod Dayton RSS390HF-4. Sprawdzono otwór pod kosz, osiem miejsc śrub, mimośrody osi ring–kołnierz oraz geometryczną możliwość przeprowadzenia trzpienia przez dwa otwory. **To badanie tolerancji płaskiego pierścienia, nie model 3D rzeczywistego kosza ani ocena wytrzymałości połączenia.**

![P40B — budżet promieniowy miejsca](../wyniki/p40b_budzet_promieniowy_pierscienia.svg)

## Podstawy ze specyfikacji producenta

Średnica wycięcia **355,8 mm**, okrąg śrub **368 mm**, średnica otworu w kołnierzu **6,5 mm**. Źródło: https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf. Żaden z tych wymiarów nie jest zaleceniem, jakiej średnicy otwór pilotujący wykonać w MDF.

Nominalny *budżet promieniowy* pomiędzy krawędzią wycięcia a najbliższą krawędzią otworu kołnierza:

\[
B=\frac{368}{2}-\frac{6{,}5}{2}-\frac{355{,}8}{2}
=\mathbf{2{,}85\ mm}.
\]

Dla pierścienia o ID, przy współosiowym montażu:
- **luz do wycięcia** = ID/2 − 177,9 mm;
- **pas metalu w obszarze otworu** = 184 − 3,25 − ID/2 mm.

Ich **suma musi zawsze wynosić 2,85 mm**. Zwiększenie ID poprawia luz montażowy, ale osłabia wąski lokalny pas metalu. Zwiększenie średnicy *zewnętrznej* OD lub grubości pierścienia nie zwiększa tego lokalnego budżetu promieniowego.

## Pełna seria tolerancji

Siatka scenariuszy: **OD=392/400/408mm × ID=356/358/360mm × dx∈{−1,5;−0,75;0;0,75;1,5}mm × dz z tego samego zbioru × referencyjna średnica trzpienia 4/5/6mm = 675 wariantów.**

Użyto dwóch jednakowych otworów Ø6,5mm i idealnie prostego, sztywnego trzpienia. Przy rozbieżności ich osi o δ dopuszczalna geometryczna różnica \`δ≤(6,5−d)\` wynika z nachodzenia dysków możliwych środków trzpienia. Ten test **nie uwzględnia skosu śruby, uszkodzeń gwintu, główki, tolerancji przylegania i montażu**.

Przy przesunięciu środka pierścienia o δ:
- minimalny luz do otworu kosza maleje o δ;
- w przyjętym wariancie otwory pierścienia przesuwają się razem z nim, więc pas metalu względem własnych otworów pozostaje taki sam;
- sprawdzono również odległości do lewego panelu i pierwszej wręgi *wyłącznie w płaskich projekcjach*.

### Liczba wariantów przechodzących poszczególne filtry

| Warunek geometryczny / hipotetyczny próg | Wynik |
|---|---:|
| Brak nominalnego przecięcia wycięcia, panelu, wręgi i dostępnego trzpienia | **171 / 675** |
| Powyższe + próg badawczy **1 mm luzu i 1 mm metalu** | **9 / 675** |
| Powyższe + próg badawczy **1 mm luzu i 2 mm metalu** | **0 / 675** |

**Uwaga:** progi 1+1 i 1+2 to arbitralne scenariusze porównawcze, **nie obowiązujące normy, nie minimalne grubości bezpieczne i nie dane o wytrzymałości stali czy aluminium**. Matematyczna niemożliwość 1+2 przy tych wymiarach jest jednak bezwarunkowa *w ramach zwykłego współosiowego pierścienia z otworami na BCD368*, ponieważ 1+2=3,00 >2,85 mm — brakuje **0,15 mm już nominalnie**.

### Gdy rozpatrujemy ID=358mm i Ø5mm trzpienia

Przy nominalnym zerowym przesunięciu luz do wycięcia = **1,1 mm**, a pas metalu przy otworze = **1,75 mm**. Przy przesunięciu o 0,75 mm w jednym kierunku minimalny luz spada do **0,35 mm**, a po przekątnej ±0,75 mm do **około 0,039 mm**. Powyższe konfiguracje mogą być geometrycznie dopuszczalne mimo bardzo małych rezerw — **to nie oznacza, że nadają się do wykonania**.

**Najważniejszy wniosek:** prosty cienki pierścień z otworami w tej samej osi co kołnierz nie rozwiązuje samodzielnie problemu prowadzenia sił z wąskiego obszaru MDF ani kwestii powtarzalnego montażu. Przed zamówieniem pierścienia należy zaprojektować alternatywną ścieżkę sił, np. szerszy zespół mocujący połączony z frontem poza krytycznym obwodem, albo inny wieloelementowy układ docisku. Żadna alternatywa nie została jeszcze zwalidowana.

## Następne badanie

Konstrukcyjne porównanie **co najmniej dwóch alternatywnych ścieżek przenoszenia sił** z rzeczywistym koszem i pozycją zacisków; 3D CAD z geometrią otworu i obrysem główek; model kontaktowy z parametrami materiału, a następnie próby *wyrywania/ścinania/odrywania* na rzeczywistym MDF 44 mm i opcjonalnym metalowym łączniku.

**Reprodukcja:** [kod 675 przypadków](../skrypty/p40b_tolerancje_pierscieni.js) · [pełne wyniki JSON](../wyniki/p40b_tolerancje_675_20261101.json).

**Werdykt:** żadna konfiguracja nie jest jeszcze produkcyjnie zatwierdzona. **Bramka CNC nadal zamknięta.**