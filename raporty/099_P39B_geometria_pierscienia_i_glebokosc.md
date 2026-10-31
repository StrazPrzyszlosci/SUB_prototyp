# Raport 099 — P39B: parametryczna kontrola miejsca dla hipotetycznego pierścienia mocowania

**1 listopada 2026.** Przebadano **54 warianty geometryczne** pierścienia pod kosz Dayton RSS390HF-4: średnice zewnętrzne 392/400/408 mm, wewnętrzne 356/360 mm, grubości 2/4/6 mm i przesunięcia osi w X −2/0/+2 mm. Dodatkowo przebadano **20 wariantów całkowitej głębokości** ze zmienną maskownicą i tylnym terminalem. **Jest to sprawdzenie kolizji brył uproszczonych; nie ma badań wyrywania, odrywania i zmęczenia mocowań.**

![Przykład pierścienia wzmacniającego pod kołnierzem](../wyniki/p39b_pierscien_i_odstepy.svg)

## Przykładowa geometria, nie rekomendacja gotowego mocowania

Dla jednego wariantu pierścienia **zewn. Ø400 mm, wewn. Ø356 mm, grubości 4 mm**, w płaszczyźnie za frontem MDF44 mm, współosiowo z koszem:

| Cecha referencyjna | Wynik |
|---|---:|
| Od lewej wewnętrznej ścianki MDF | 9 mm |
| Do pierwszej wręgi w projekcji osi X | 17 mm |
| Do górnej/dolnej wewnętrznej powierzchni | 28 mm |
| Pozostały przekrój metalu promieniowo przy otworze Ø6,5 | 2,75 mm |
| Orientacyjna masa pierścienia stalowego (ρ 7850 kg/m³) | 0,812 kg |
| Orientacyjna masa aluminiowego (ρ 2700 kg/m³) | 0,279 kg |
| Zajmowana objętość bez otworów i innych złączy | 0,1034 l |
| Nominalna różnica promieniowa między ID356 a wycięciem Ø355,8 | **0,1 mm** |

**Ostatnia pozycja jest ostrzeżeniem:** 0,1 mm promieniowo to niezweryfikowany luz technologiczny. Realny kosz i możliwość demontażu mogą wymagać większej średnicy wewnętrznej pierścienia, kosztem jeszcze mniejszego przekroju w obszarze śrub. W wariancie **ID360** luz od wycięcia wynosi 2,1 mm, ale z kolei promieniowy pas metalu między Ø6,5 a ID360 ma tylko **0,75 mm**. Bez konstrukcji przenoszącej siły poza ten wąski pas nie należy zatwierdzać żadnej alternatywy.

**Uwaga:** 2,85 mm MDF pomiędzy wycięciem Ø355,8 a kołnierzem Ø6,5 z P38A **nie znika** tylko dlatego, że po drugiej stronie frontu pojawia się metalowy pierścień.

## Co to mówi o śrubach?

Jeżeli hipotetyczny kosz z głośnikiem waży 15 kg, scenariusz 5g daje obciążenie bezwładności około **736 N**, a 10g około **1471 N**. Równy rozkład na 8 połączeń dałby 92/184 N na punkt, ale ten rozkład nie uwzględnia momentów, dynamiki, naprężeń od wstępnego dokręcenia, uszkodzenia MDF, odkształcenia kołnierza czy utraty szczelności. **Nie są to wyniki testu ani podstawa doboru wkrętów.** W szczególności nie wolno zakładać, że wszystkie 8 śrub przenoszą zawsze równą część rzeczywistego obciążenia.

## Budżet zewnętrznych 500 mm

Model referencyjny przyjął korpus 425 mm, wystawanie kołnierza 10,5 mm, hipotetyczne maskownice 20/40/50/60/80 mm i wystawanie tylnego złącza 0/10/20/30 mm. Wykonano 20 zestawień: **7 przekracza głębokość 500 mm.**

- Przykład **40 mm maskownica + 30 mm terminal** → 425+40+30 = **495 mm**, tylko 5 mm na rzeczywiste tolerancje.
- **50 mm maskownica + 30 mm terminal** → **505 mm**, przekroczenie o 5 mm.
- **60 mm maskownica + 20 mm terminal** → **505 mm**, przekroczenie o 5 mm.

Nie ma zatwierdzonej maskownicy i terminala, zatem nie można twierdzić, że ostateczna obudowa zmieści się w limicie.

## Ograniczenia i wymagana weryfikacja

Mocowanie pierścienia do frontu jest tylko zaproponowaną **geometrią porównawczą**, a nie projektem inżynierskim: nie wybrano materiału, połączenia, śrub, gwintów, tulei, podkładek ani technologii klejenia. Zbadano dodatnią i ujemną tolerancję osi X ±2 mm — ale przy takich przesunięciach **szablon otworów pierścienia nie musi się pokrywać z otworami kołnierza**. Przyjęta oś BCD pozostaje stała i musi być zweryfikowana.

Prawdziwe sprawdzenie wymaga: skanu/makiety kosza i zacisków, montażu/demontażu z narzędziem, pełnych brył pierścienia i wręg, próby obciążeniowej MDF oraz weryfikacji szczelności.

**Reprodukcja:** `node skrypty/p39b_obwiednie_pierscien_mocowanie.js` → `wyniki/p39b_kolizje_pierscien_glebokosc_20261101.json`. [Parametryczny model 3D](../dokumentacja/P39C_front_korpus_pierscien_REFERENCYJNY_NIE_CNC.scad). **Nie frezować na podstawie tych danych.**