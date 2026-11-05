# K30-R1 — 102 nominalne części MDF. CNC HOLD

**NIE FREZOWAĆ. To zestaw do przeglądu konstrukcji, nie gotowe zlecenie.**

Wymiary korpusu: 1080×432×500 mm, dostęp wyłącznie przez otwór głośnika.
Wszystkie pliki DXF są w milimetrach, skala 1:1, jeden element na plik,
jedna sztuka każdego pliku według LISTA_CZESCI.csv. Model SCAD pozwala zmienić
`state=100/120/150`. Nie mieszać części K30 ze starszym K18.

## Bazy i operacje

- U=0,V=0: dolny lewy narożnik prostokątnej formatki.
- Oś normalna i położenie w złożeniu znajdują się w CSV.
- Dla normalnej X: U=Y, V=Z; widok od +X. Dla Y: U=X,V=Z; widok od −Y.
  Dla Z: U=X,V=Y; widok od +Z. Nie odbijać lustrzanie.
- CUT_OUTER: finalny zewnętrzny obrys, przez materiał.
- CUT_INNER: finalny otwór, przez materiał. PORTAL/MID_PORTAL: R4.
- DRILL_THRU: wiercenie Ø6 na wylot w płaszczyźnie, bez wiercenia krawędzi.
- INFO_NO_CUT: opis. Nie obrabiać tej warstwy.
- Kontury NIE są ścieżkami środka frezu. Kompensację, mocowanie, mostki,
  posuw, obroty i kolejność wykonuje technolog CAM. Nie dodawać kompensacji dwa razy.
- Brak operacji od strony B; brak uzgodnionego pogłębiania i kieszeni.
- Nie ma G-code: nie określono maszyny, postprocesora, narzędzia i mocowania.

## Konkretnie czego brakuje

FR1/FR2 mają wyłącznie referencyjny duży otwór. Nie zatwierdzono mocowania
kosza ani produkcyjnego luzu. BACK nie ma docelowego otworu terminala.
Metalowe płytki, śruby, uszczelnienia i wydłużony rygiel nie są częściami MDF
z tego zestawu i wymagają osobnej dokumentacji/kwalifikacji.

Nominalny panel 244 mm może nie zmieścić się pomiędzy ścianami o grubości
8,5 mm: skrajna interferencja wynosi 1,2 mm. Przed zwolnieniem do produkcji
trzeba wprowadzić zmierzone grubości partii płyt i szczeliny klejowe do
wymiarów wszystkich złączy. Nie korygować ich ręcznie na oko.

## Kolejność wstępnego montażu

1. Przymiarka korpusu i wręg, bez zamykania dostępu. Kontrola przekątnych.
2. Połączenie stałych wręg, listew i płatów kanałów; podparcia muszą przenosić
   siły przed zamknięciem obudowy. Ustawić poziomy przyrządem, nie sumą grubości.
3. Zamontować metalowe elementy mocowania blokad przed sklejeniem korpusu.
4. Sprawdzić kompletne tory wkładów, przekładek, blokad i prawdziwego narzędzia.
5. Dopiero po kwalifikacji połączeń i kontroli interfejsów zamknąć korpus.

Instrukcja nie zatwierdza kleju, momentów śrub ani kolejności zamówienia.
Pełne obliczenia i ograniczenia: raport K30 w katalogu raporty repozytorium.
