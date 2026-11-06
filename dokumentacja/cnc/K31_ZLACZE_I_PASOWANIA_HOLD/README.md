# K31 — korekta pięciu części, CNC HOLD

Nie frezować. Nie jest to pełny zestaw obudowy.

| Nowy plik | Zastępuje w wariancie K31 |
|---|---|
| PORTAL_K31_HOLD.dxf | K30 PORTAL.dxf |
| STOP_0_K31_HOLD.dxf | K30 STOP_0.dxf |
| STOP_1_K31_HOLD.dxf | K30 STOP_1.dxf |
| STOP_2_K31_HOLD.dxf | K30 STOP_2.dxf |
| STOP_3_K31_HOLD.dxf | K30 STOP_3.dxf |

Stosować wyłącznie całą piątkę razem. Jednostki mm, skala 1:1, jedna sztuka
każdego pliku. MDF22 dla PORTAL, MDF18 dla STOP. Te części leżą w płaszczyźnie
YZ: U=Y, V=Z, widok od +X. Baza (0,0) na dolnym lewym narożniku formatki.
Wszystkie otwory są przelotowe Ø6; wycięcia wręgi mają R4. CUT_OUTER/CUT_INNER
opisują obrys części, nie skompensowany tor frezu. INFO_NO_CUT nie obrabiać.

PANELE_WKLADOW_PODGLAD.csv zawiera dane syntetyczne, dopóki nie ma kompletnych
pomiarów. Nie przekazywać tego CSV jako listy cięcia. Brakuje kwalifikacji
szczeliny klejowej, retencji metalowych płytek i pozostałych interfejsów.

K31_ZLOZENIE_HOLD.scad pokazuje całą propozycję z poprawkami; state=100/120/150.
Pełna analiza: raporty/K31_zlacze_blokady_i_pasowania_MDF.md w repozytorium.
