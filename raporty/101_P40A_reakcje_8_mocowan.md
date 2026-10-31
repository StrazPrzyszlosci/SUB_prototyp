# Raport 101 — P40A: rozkład sił i momentów na osiem śrub głośnika

**1 listopada 2026 — 432 wykonane przypadki statycznej równowagi grupy śrub.** To badanie mechaniki idealnej grupy połączeń dla wstępnego Dayton RSS390HF-4, **nie wytrzymałości MDF ani sprawdzian bezpieczeństwa rzeczywistych wkrętów**.

![P40A — reakcje w idealizowanej grupie śrub](../wyniki/p40a_reakcje_grup_srub.svg)

## Dlaczego osiem śrub nie zawsze oznacza F/8?

Producent Dayton podaje masę głośnika **30 lb ≈ 13,6 kg**; dla analizy obciążenia i dodatkowego osprzętu zbadano **12/15/18 kg**. Dane katalogowe i wymiary kosza: https://www.daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm oraz https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf.

Siła bezwładności F=m·a, przy a w [1,3,5,10] g; r=184 mm, a środek masy umownie odsunięty od powierzchni śrub **e=60/120/180 mm**. Siła działa w kierunku poziomym X, pionowym Z lub normalnie do frontu Y. Zbadano **4 wzorce czynnych połączeń**: wszystkie osiem; cztery symetrycznie naprzemienne; sześć kolejnych oraz cztery kolejne. Ostatnie wzorce to hipotetyczne warianty awaryjne i **nie są zalecanym sposobem użytkowania**.

Dla czynnych punktów o współrzędnych (xᵢ,zᵢ), liczonych względem środka ciężkości grupy, założono jednakową podatność, wymuszono trzy warunki równowagi normalnych reakcji:

- ΣNᵢ = Fᵧ;
- Σxᵢ·Nᵢ = M_z, po uwzględnieniu momentu wynikającego z ramienia e oraz przesunięcia środka czynnych punktów;
- Σzᵢ·Nᵢ = −M_x.

Rozwiązano układ 2×2 dla liniowego rozkładu Nᵢ względem xᵢ i zᵢ. W płaszczyźnie frontu przyjęto **równy rozkład siły tnącej Fₓ/n, F_z/n**. Wynik \`sqrt(Nᵢ² + Tᵢ²)\` to jedynie modelowa wypadkowa **reakcji**, nie naprężenie śruby, nośność złącza ani siła wyrywająca MDF. Model nie rozstrzyga faktycznych sił ściskających przenoszonych przez kołnierz, a nie śrubę; liczba N ujemna to umowna reakcja kontaktu.

**Kontrola matematyczna:** każde z 432 rozwiązań sprawdzono niezależnie względem sumy sił i dwóch sum momentów (błąd bezwzględny poniżej 1e−5 N/N·mm w przyjętym algorytmie).

## Reprezentatywny przykład: 15 kg, 5g, r=184 mm, e=120 mm

F = 15×5×9,80665 = **735,50 N**. Naiwny równy podział siły na osiem: **91,94 N/połączenie**.

| Czynne mocowania | Kierunek X: max wypadkowa | Kierunek Z: max wypadkowa | Kierunek Y: max wypadkowa |
|---|---:|---:|---:|
| Osiem (8) | **151,11 N** | 151,11 N | 91,94 N |
| Cztery równomierne (4) | 302,21 N | 302,21 N | 183,87 N |
| Sześć kolejnych (6) | 221,08 N | 254,73 N | 196,34 N |
| Cztery kolejne (4) | 417,03 N | 527,32 N | **562,78 N** |

Dla wszystkich ośmiu przy obciążeniu w osi X:

\[
T = F/8 \simeq 91{,}94\ \mathrm{N},\qquad
N_{\max}=\frac{F\,e}{4r}\simeq119{,}92\ \mathrm{N},
\]
\[
R_{\max}=\sqrt{T^2+N_{\max}^2}\simeq151{,}11\ \mathrm{N}.
\]

Wzrost do 151,11 N wynika w całości z ramienia momentu, **nawet przy ośmiu idealnie pracujących połączeniach**. Przy układach asymetrycznych odpowiedź zależy też od utraty symetrii i od położenia środka czynnej grupy. Wyniki **nie określają** czy pojedyncza śruba, kołnierz czy MDF są bezpieczne.

## Co trzeba zmierzyć albo zamodelować przed podaniem nośności?

1. **Geometrię rzeczywistego złącza**: kształt łba, średnicę trzpienia i prowadzenia, długość zazębienia, kontakt z kołnierzem, odległości krawędzi, materiał pierścienia i kierunek przenoszenia sił.
2. **Rzeczywiste założenia obciążeń** do transportu, przenoszenia, położenia pionowego/poziomego, odsunięcie środka masy od frontu i grawitację. **5g i 10g są hipotetyczne**, a nie normatywne ani zmierzone.
3. **Naprężenia kontaktowe, odrywanie warstw MDF, ścinanie, wyrwanie, utratę wstępnego docisku, pełzanie spoin i cykle** w modelu kontaktowym oraz testach próbek.
4. **Rozdział reakcji na tarcie i docisk**: przy wstępnym ścisku część obciążeń poprzecznych może przechodzić przez tarcie, a siły normalne przez lokalny nacisk kołnierza. Nie wolno bez tego bezpośrednio porównywać wypadkowej Rᵢ z katalogową nośnością śruby.

**Reprodukcja:** [kod P40A](../skrypty/p40a_reakcje_osmiu_srub.js) · [pełne 432 scenariusze JSON](../wyniki/p40a_reakcje_432_20261101.json).

**Werdykt:** obciążenie „F/8” jest niewystarczającym modelem, ale sam model 432 scenariuszy **nie pozwala jeszcze wybrać ani zatwierdzić mocowania**.