# Raport 094 — P37A: śledzenie 18 globalnych postaci drgań MES metodą MAC

**1 listopada 2026.** Wykonano **6 globalnych przebiegów modelu powłokowego** z eksportem 18 par wartości i wektorów własnych, **5 przyporządkowań × 18 postaci = 90 porównań MAC**. Wyniki stanowią **kontrolę numerycznej powtarzalności istniejącego modelu**, a nie walidację jego zgodności z fizyczną obudową.

![Jak stabilne są globalne mody MES?](../wyniki/p37a_mac_globalny_18_modow.svg)

## Problem, którego nie widzimy na wykresie samej f1

Poprzedni raport 093 pokazał MAC dla pojedynczej płyty. Cała skrzynia może jednak drgać globalnie (w tym na stopkach), a postacie lokalne przeskakują przy zmianach siatki lub spoin. Porównanie tylko pierwszej wartości własnej nie wykrywa pomylenia dwóch odmiennych kształtów ruchu.

Dla dwóch wektorów odpowiednio odwzorowanych w tych samych punktach pomiarowych:

\[
\mathrm{MAC}(u,v)=\frac{|\langle u,v\rangle|^2}{\langle u,u\rangle\,\langle v,v\rangle}
\]

Zastosowano próbki wewnątrz **sześciu ścian** na wspólnych punktach w fizycznych współrzędnych i trzy składowe przemieszczenia globalnego. Wykluczono próbki wewnątrz obwodu głośnika oraz blisko wręg. Wektory z różnych siatek interpolowano metodą czterech najbliższych węzłów z wagami odwrotnie proporcjonalnymi do kwadratu odległości. Punkty ważono przybliżonym polem panelu, normalizowano i dopasowano **maksymalną sumę MAC** algorytmem węgierskim, bez zakładania identycznej kolejności f1, f2 itd.

**To MAC na wspólnych próbkach przemieszczeń**, a nie dokładny iloczyn skalarny z macierzą masy dwóch identycznych siatek. Dla modów zdegenerowanych należałoby ponadto stosować MAC podprzestrzeni.

## Badane warunki

Korpus 1020×425×500 mm; płyty MDF 22 mm, front 44 mm; bazowy E=2,1GPa, rho=730kg/m³. Przyjęto numeryczny stabilizator Q4 gamma=0,001, niekalibrowane sprężyny spoin: k_trans=3×10⁷N/m², k_rot=3×10³ (jednostka wynikająca z uproszczonego sprzężenia). Utrzymano masę głośnika 15kg, wkładów 8kg i umowne podpory. Porównano siatki docelowe **150/110/85mm**, gamma=0,01 i spoiny 0,1×/10×.

Uwaga: sama zmiana sztywności spoin (i 18-modowe obcięcie widma) może powodować wypadanie modów poza rozważany zbiór; niska wartość MAC **nie rozstrzyga automatycznie o niestabilności fizycznej**.

## Wyniki

| Porównanie | Średni MAC (18) | MAC pierwszej postaci | Ile spośród 18 ma MAC poniżej 0,90? | Przestawienia kolejności |
|---|---:|---:|---:|---:|
| Siatka 150 → 110mm | 0,8060 | 0,9919 | **10** | 6 |
| Siatka 110 → 85mm | 0,8596 | 0,9975 | **5** | 7 |
| gamma=0,001 → 0,01 (110mm) | 0,9900 | 1,0000 | 1 | 0 |
| Spoiny 0,1× (110mm) | 0,5589 | 0,7031 | **15** | 11 |
| Spoiny 10× (110mm) | 0,7508 | 0,9992 | **11** | 6 |

**Pierwsze cztery globalne postacie** między siatkami 110→85mm miały MAC od **0,9957 do 0,9975**, lecz pierwsza częstotliwość wciąż zmieniła się z 32,874 do 33,660Hz (+2,39%). Część wyższych postaci nie jest stabilnie dopasowana, a dla znacznie podatniejszych spoin nawet pierwsza postać spadła do MAC 0,7031. Oznacza to, że nie wolno traktować całej grupy 18 częstotliwości jako zweryfikowanych rezonansów obudowy.

## Kryteria następnego przejścia

1. Zbudować pełny **CAD z siatką dopasowaną do otworu** i łączników, usunąć sztuczne mody przez zweryfikowany element/patch tests.
2. Dla zgodnych modalnych podprzestrzeni ocenić nie tylko f i MAC, ale **uczestnictwo masowe i energię w panelach względem stopek i spoin**.
3. Powtórzyć trzy siatki po wprowadzeniu **zmierzonych** współczynników sprężystości i nośności spoin.
4. Porównywać kształty z rzeczywistymi pomiarami drgań pierwszej sztuki, z jednakowymi punktami rejestracji.

**Weryfikacja:** skrypt [P37](../skrypty/p37_mac_globalny_i_wrazliwosc.py) odtwarza 18 wektorów dla każdego modelu. Nie modyfikuje historycznego P33B w repozytorium — tymczasowo rozszerza jego funkcję o eksport wektorów i używa elementu Q4 z P33C. [Skrót wyników](../wyniki/p37_globalny_mac_wrazliwosc_PODSUMOWANIE_20261101.json). **Bramka CNC: nadal zamknięta.**