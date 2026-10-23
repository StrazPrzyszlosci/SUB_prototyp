# Wykonawca elementów MDF — wymagania do projektu

Źródło: opis oferty **dostarczony przez użytkownika 2026-10-23**:
[Allegro, oferta 17586111495](https://allegro.pl/oferta/elementy-obudowa-glosnika-mdf-na-zamowienie-subwoofer-cnc-na-wymiar-17586111495).
Kalkulator wskazany w opisie: [diykraft.pl](https://diykraft.pl/kalkulatory-allegro-mdf-cnc/).
Opis jest podstawą roboczą; ceny i warunki nie zostały jeszcze potwierdzone
w bieżącej ofercie. Nie wysłano formularza, zapytania ani zamówienia.

## Ograniczenia deklarowane w ofercie

| Pozycja | Deklaracja | Konsekwencja dla dokumentacji |
|---|---|---|
| Materiał | Surowy MDF | Wycena bazowa MDF; sklejka wymaga innego potwierdzenia/oferty |
| Grubości | 8, 10, 12, 18, 22, 25 mm | Każdy element z przypisaną grubością; 36 mm jako laminowanie 2 × 18 mm |
| Wymiary XY | Tolerancja ±0,1 mm | To deklaracja wykonawcy; uwzględnić też rzeczywistą grubość i montaż |
| Głębokość frezowania | Tolerancja ±0,5 mm | Krytyczne dla podfrezowania kosza i zgniotu uszczelki |
| Naroża wewnętrzne | R4, frez Ø8 mm | Wpusty i wręgi muszą uwzględniać promień; ostre wewnętrzne kąty niewykonalne standardowo |
| Obróbka | Standardowo jednostronna; dwustronna dodatkowo oznaczana | Każda operacja z nazwą strony i głębokością |
| Wiercenie w krawędziach bocznych | Niewykonywane | Nie projektować połączeń zależnych od takich otworów wykonanych na CNC |
| Najdłuższy bok | 1400 mm | Kontrola każdego elementu, nie tylko gabarytu gotowej skrzyni |
| Długość + szerokość | ≤2700 mm | Kontrola formatek i opakowania |
| Masa pojedynczego elementu | ≤30 kg | Wyliczyć z rzeczywistej grubości/gęstości, zachować zapas |
| Projekt akustyczny i kompletność | Po stronie zamawiającego | Potrzebny własny przegląd zestawu i kolejności montażu |

Limity wysyłkowe elementów nie stanowią przyjętego limitu gabarytów akustycznych.
Jeśli optymalny projekt je przekroczy, należy rozważyć podział lub inną usługę,
a nie potajemnie zmienić wymagania SPL.

## Pakiet do późniejszej wyceny

Dokumentacja ma obejmować:

1. Rysunek złożeniowy z orientacją front/tył/góra i bilans objętości netto.
2. Oddzielny plik elementu, identyfikator, materiał, grubość, ilość i jednostki mm.
3. Zamknięte kontury w DXF/DWG/SVG; PDF z wymiarami kontrolnymi i uwagami.
4. Położenia i średnice otworów: głośnik, śruby, terminal, wymienne mocowania.
5. Dla rowków, kieszeni i podfrezowań: wymiary XY, głębokość od wskazanej strony.
6. Osobne oznaczenie obróbki dwustronnej, faz, promieni i kieszeni na nakrętki.
7. Rozpiska wręg oraz modułów wypornościowych, ich mocowań i dostępu serwisowego.
8. Wyjaśnienie, które połączenia kleimy, a które rozbieramy na uszczelce.
9. Rewizja projektu i identyczne nazwy w plikach, BOM i kalkulatorze.

Format STEP może być użyteczny wewnętrznie jako model 3D, ale oferta nie podaje
go jako formatu wejściowego. Do wyceny wyeksportować jeden z akceptowanych formatów.

## Kontrole przed wysłaniem

- Model kosza i wycięcia z rysunku producenta, nie średnica nominalna 12″/15″.
- Sprawdzony prześwit magnesu, wentylacji, przewodów i wręg przy całym ruchu.
- Naroża R4 pasują do drugiego elementu; kompensacja frezu uzgodniona z wykonawcą.
- Szerokość rowka uwzględnia tolerancję płyty, klej i możliwość wsunięcia elementu.
- Krytyczne podfrezowania nie zakładają lepszej tolerancji Z niż zadeklarowane ±0,5 mm.
- Podwójny front ma czytelne ustawienie warstw; śruby kosza nie blokują demontażu.
- Nie dodano otworów na wzmacniacz/DSP/zasilacz w skrzyni subwoofera.
- Przewidziano ochronę membrany i stabilność ciężkiej skrzyni w domu z dzieckiem.
- Komplet zawiera wszystkie panele, wręgi i elementy regulacji; wykonawca tego nie sprawdza.

## Otwarte kwestie technologiczne

Przed R5 ustalić: faktyczną grubość MDF, dostępne frezy, minimalne szerokości
mostków i odległości od krawędzi, oznaczanie warstw DXF, pochodzenie osi i stron,
zakres tolerancji dla otworów, możliwość kieszeni na wkładki, zabezpieczenie
w transporcie i cenę brutto z dostawą. Są to pytania do przyszłej wyceny,
nie powód do zatrzymania badań elektroakustycznych.

Kalkulator wylicza jednostki aukcyjne. **Jedna sztuka aukcyjna nie oznacza
jednej skrzyni ani jednej formatki.** Liczbę jednostek można wyznaczyć dopiero
z kompletnej listy operacji; obecnie nie ma wiarygodnej wyceny CNC.
