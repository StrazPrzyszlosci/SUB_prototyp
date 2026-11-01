# Raport 105 — P41C: dwie edytowalne koncepcje nośne w OpenSCAD

**1 listopada 2026.** Utworzono **edytowalny plik brył referencyjnych** [\`P41C_porownanie_nosne_A_B_NIE_CNC.scad\`](../dokumentacja/P41C_porownanie_nosne_A_B_NIE_CNC.scad), gdzie zmienna \`concept\` przyjmuje wartość \`"A"\` lub \`"B"\`.

![P41C — rzut hipotetycznych kotew konstrukcji A i B](../wyniki/p41a_punkty_carrier_szyny.svg)

## Warianty

**A:** hipotetyczny C-kształtny fragment ramy nośnej za frontem MDF44mm: obrys odniesienia x70..435mm, z30..470mm i grubość 6mm w osi Y, odjęty walec Ø370mm. Otwory ośmiu hipotetycznych kotew są zobrazowane, ale **nie określają śrub ani technologii mocowania**.

**B:** dwie szyny przy dolnej i górnej strefie frontu (x70..466mm, y44..69mm), dodatkowe taby w okolicy x434..467mm mają pokazać zamiar połączenia z pierwszą wręgą. Są to uproszczone bryły, nie zaprojektowane złącza. Brakuje faktycznej geometrii kosza, łbów i dróg montażu 20 wkładów.

**Zamiennik kosza:** referencyjny walec Ø360mm, h120mm *wyłącznie do wizualizacji* oraz kołnierz Ø388,4mm. Prawdziwa geometria żeber, magnesu i zacisków Dayton nie jest znana. Kołnierz i masa z dokumentacji producenta nie oznaczają kompletnego modelu 3D.

OpenSCAD sprawdza część obrysu gabarytowego i zewnętrznych marginesów, ale nie wykonuje automatycznego dowodu kolizji wolnych kształtów 3D ani analizy MES. Położenie tabów względem wręgi oznacza **zamierzony kontakt**, który trzeba dopracować geometrycznie i wytrzymałościowo.

## Reprodukcja

Po zainstalowaniu OpenSCAD:

\`\`\`bash
openscad -o /tmp/p41_A.csg -D 'concept="A"' dokumentacja/P41C_porownanie_nosne_A_B_NIE_CNC.scad
openscad -o /tmp/p41_B.csg -D 'concept="B"' dokumentacja/P41C_porownanie_nosne_A_B_NIE_CNC.scad
\`\`\`

Są to **eksporty drzewa CSG do kontroli poprawności składni**, a nie frezowalne pliki CAD/CNC. Nie wykonano porównania montażowego z fizycznym głośnikiem.

## Co dalej przed wyborem rozwiązania

1. Fizyczny kosz Dayton i sześć przekrojów kontrolnych 3D na kolejnych głębokościach, z rzeczywistymi zaciskami i przebiegiem przewodów.
2. Zweryfikowane bryły ośmiu śrub, podkładek, tulei, węzłów ramy A i szyn B oraz dostęp narzędzi i możliwość powtarzalnego demontażu.
3. Geometria i wytrzymałość połączenia szyn do pierwszej wręgi; ponowne przeliczenie bilansu zajętej objętości i dostępności wkładów 100/120/150 l.
4. Pomiary k i E na próbkach. Dopiero po nich kontaktowy MES z odrywaniem MDF i kleju, lokalnymi naprężeniami i zmęczeniem.
5. Pomiar pierwszego prototypu i sprawdzenie szczelności oraz wibracji.

**Bramka CNC: zamknięta. Pliki są wyłącznie materiałem konstrukcyjnym do dalszego projektowania.**