# Raport 081 — P31B (ERRATA 31.10.2026, skorygowano wymiary): badania podatnego podparcia dwóch wręg nowej obudowy

> **Sprostowanie krytycznego błędu jednostek (31.10.2026):** Poprzedni skrypt używał `(W−0,044)/1000` i `(D−0,066)/1000`, odejmując 0,044 i 0,066 mm zamiast 44 i 66 mm. Podane wcześniej częstotliwości (np. 115,3 Hz bez wręg) i ugięcia są **nieważne**. Poprawione dla 1020×425mm: rozpiętości panelu 976×359mm, f1 bez wręg **156.24 Hz**. Sprawdzono niezależnie wzorem analitycznym; to nadal nie pełen MES.

**31.10.2026. Wyniki: 135 scenariuszy modelu Rayleigha–Ritza dla jednej płyty plus kontrole podstawowego przypadku i zmiany liczby funkcji.** Nie wykonano pełnej symulacji MES obudowy; to test pułapek projektowych.

## Geometria
Obudowa P30E: **1020×425×500mm** korpus, wewnętrzny rozpiętościowy panel: 976 × 359 mm, grubość 22mm; MDF E 1.5–3 GPa, rho 650–800kg/m³, ν=.3. Dwa hipotetyczne linowe podparcia przy **x=426 i 701mm** na górnej/dolnej płaszczyźnie. Z rzeczywistych wręg P30E przeniesiono tylko ich **położenia w rzucie**; nie przypisano im idealnej sztywności ani nie pominięto ograniczenia dostępu przez otwór po głośniku.

**UWAGA:** Sprężyny do nieruchomego podłoża nie modelują ruchu poprzecznego całej ramy; dostarczają *kierunkowej wrażliwości* na sztywność podparć. Nie wolno uznać policzonego f1 za pierwszą częstotliwość własną kompletnej skrzyni. Raport 059 P18E wykazał już około 143Hz w innym modelu starej geometrii.

## Model
Płyta Kirchhoffa o podporach po obwodzie SSSS, baza `sin(mπx/a)sin(nπy/b)` (7×5). Sztywność `D=E h³/[12(1−ν²)]`. Wzorcowy diagonalny element energii `Kmn,mn=D π⁴ [(m/a)²+(n/b)²]² ab/4`; masa `Mmn,mn=ρ h ab/4`. Dwie linie `x=x_i` dodają `k_line (b/2) sin(mπx_i/a) sin(m'πx_i/a)`, jeżeli `n=n'`. `k_line` N/m². Przestrzeń małe ugięcia, jednostajne pole 1000Pa. Rozwiązano statykę macierzową i najmniejszą wartość własną dla każdego przypadku.

**Siatka:** 3 korpusy (1000×440, 1020×425, 1040×430) × 3 E × 3 gęstości × 5 sztywności k=0,1e5,1e6,1e7,1e8 = **135 przypadków**.

## Analiza wybranego wariantu 1020×425, E=2.1GPa, rho=730kg/m³
| Hipotetyczna sztywność linii k [N/m²] | Pierwsze f1 płyty [Hz] | Ugięcie w środku na 1000Pa [µm] | f1/f1 bez wręg |
|---:|---:|---:|---:|
| 0.0e+0 | 156.2 | 96.27 | 1.00 |
| 1.0e+5 | 157.8 | 94.10 | 1.01 |
| 1.0e+6 | 171.1 | 78.15 | 1.10 |
| 1.0e+7 | 228.5 | 28.16 | 1.46 |
| 1.0e+8 | 249.1 | 2.18 | 1.59 |

Zakres f1 przy wszystkich 45 kombinacjach E/ρ/k w tej geometrii: **126.1–314.2Hz**. To nie jest fizyczna tolerancja, nie model częstotliwości własnej całej skrzyni ani wynik pomiarowy.

## Kontrole
- Gdy k=0, `f11=(π/2)√(D/ρh)·(1/a²+1/b²)`; zgodność do 0.001Hz dla wszystkich trzech geometrycznych przypadków.
- Statyka z dwóch baz: 5×3 vs 7×5 funkcji. Dla E=2.1GPa, rho=730, k=1e6:
  - 1000×440: 87.45 → 87.23µm, zmiana 0.25%.
  - 1020×425: 78.35 → 78.15µm, zmiana 0.26%.
  - 1040×430: 82.50 → 82.34µm, zmiana 0.19%.
- Kontrola dodatniości energii i brak własnych wartości ujemnych. To kontrole równania redukcji, a nie walidacja spoiny.

## Wniosek dla projektu
**Główną blokadą mechaniki jest nieznana sztywność kontaktu wręga–pozostałe panele i wytrzymałość połączeń**, a nie wyłącznie wybór 22/25/28mm MDF. Zwiększanie grubości bez identyfikacji otoczenia może przenieść rezonans, ale nie musi zlikwidować promieniowania drgających ścian; pełny obciążony MES z koszem, matą, wkładami i spoinami jest niezbędny. Należy zaprojektować wzmocnienia bez blokowania **20 dróg montażowych** i ponownie uruchomić geometrię P30E.

Szczegóły bramek prototypu: odwzorowanie fizycznych łączników i stopek, pełne W,D,H z promieniowaniem paneli oraz charakterystyką jakości przy równym SPL (raport 080). Brak zgody na zamówienie CNC.

## Odtwarzanie
`node skrypty/p31b_plyta_i_podatne_linie.js` zapisuje pełne 135 przypadków do `wyniki/p31b_podatnosc_dwoch_linii_135_20261031.json`. Model liniowy, bez zależności.
