# Raport 100 — P39C: pierwszy edytowalny model 3D frontu, kosza i pierścienia

**1 listopada 2026.** Dodano **parametryczny model OpenSCAD** obudowy w układzie X/Y/Z, z kołowym otworem na Dayton RSS390HF-4 i 8 otworami pierścienia. **Status: szkic konstrukcyjny 3D, NIE zwalidowany CAD/CNC.**

![Parametry geometryczne pierścienia — referencyjny widok w rzucie](../wyniki/p39b_pierscien_i_odstepy.svg)

## Co faktycznie jest w bryle?

Źródło: [P39C model OpenSCAD](../dokumentacja/P39C_front_korpus_pierscien_REFERENCYJNY_NIE_CNC.scad).

- Sześć paneli MDF w układzie globalnym `x=0..1020, y=0..425, z=0..500`, front 44mm (y=0..44), pozostałe 22mm, otwór Ø355,8 w środku X231/Z250 z uwzględnieniem rzeczywistego położenia od zewnątrz;
- Dwie uproszczone ramy/wręgi w pozycjach x448 i x723, z zaznaczonymi belkami obwodowymi; ich **rzeczywisty przekrój, spoiny i prześwity nie zostały zamrożone**;
- Referencyjny pierścień dociskowy za frontem `OD=400, ID=356, t=4`, otwory 8×Ø6,5 na BCD368, faza pierwszego otworu umownie 0°;
- Kołnierz kosza jako cylinder Ø388,4 o grubości 10,5mm oraz **wyłącznie zastępczy walec silnika Ø260mm o głębokości 123,5mm za frontem** — to nie jest rzeczywista bryła Dayton ani bezpieczna strefa wentylacji;
- Opcjonalne reprezentacje wysunięcia maskownicy i złącza, z prostym `assert` łącznego gabarytu 500mm.

Właściwy szkic 3D umożliwia obracanie, przekroje i zmianę parametrów oraz eksport bryły do dalszej analizy w OpenSCAD. **Nie jest modelem zrekonstruowanym z pliku STEP producenta**. Żaden jego wymiar nie dowodzi, że rzeczywisty kosz przejdzie przez wycięcie bez kontaktu z pierścieniem lub narzędziami. Nie ma pełnych 20 modułów, uszczelek, terminala, zacisków i łączników.

## Uwaga o narzędziach i skalowaniu

Zastosowano układ: **X w prawo, Y od zewnętrznego frontu ku tyłowi, Z od dołu ku górze**. Model zawiera geometrię w **mm**. Punkty w lokalnej siatce ciśnienia FV przelicza się jako `x_local=x_external-22, z_local=z_external-22, y_local=y_external-44`; pierwsza wręga w x lokalnym 426mm.

Przy otwieraniu pliku `.scad` należy sprawdzić poprawność kompilacji OpenSCAD i poprawne wygenerowanie różnicy brył (otwór kosza, pierścień, osiem otworów), zanim przechodzi się do eksportu geometrii referencyjnej. Parametry `show_...` pozwalają wyłączyć zasłaniające panele. W repozytorium **nie ma potwierdzonego przemysłowego eksportu STEP z pełnymi tolerancjami**.

## Co blokuje przejście od OpenSCAD do właściwego CAD/CNC?

1. Potrzebny jest **prawdziwy kosz producenta** z obrysem przy poszczególnych głębokościach, śrubami, główkami, oryginalną fazą BCD, zaciskami i przewodami.
2. Trzeba wybrać konstrukcję **8 obciążeń mocowania**, szczególnie sposób przeniesienia sił poza cienki pas MDF 2,85mm i pas metalu 2,75mm w wariancie Ø400/Ø356. Przy montażu z demontażem nie można kierować się jedynie wstępnym CAD.
3. Trzeba wprowadzić pełne 20 modułów wraz z rzeczywistymi blokadami i przeprowadzić w symulacji **montaż przez otwór z narzędziami**, a nie tylko testy statycznych AABB.
4. Wymagane są powierzchnie CAD **dobrze dopasowane do kołowego otworu** i zwalidowany MES oraz próbki MDF/kleju.
5. Zewnętrzna głębokość musi uwzględnić rzeczywistą maskownicę, terminal, stopy, uchwyty i tolerancje — [20 scenariuszy P39B](../wyniki/p39b_kolizje_pierscien_glebokosc_20261101.json) pokazuje przypadki przekroczenia limitu.

**Werdykt: etap CAD rozpoznawczego P39C zrealizowany, kwalifikacja mechaniczna i CNC otwarta.**