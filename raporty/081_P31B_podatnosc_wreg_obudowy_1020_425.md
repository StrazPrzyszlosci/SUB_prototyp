# Raport 081 — P31B: badania podatnego podparcia dwóch wręg nowej obudowy

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
| 0.0e+0 | 115.3 | 179.61 | 1.00 |
| 1.0e+5 | 117.3 | 172.84 | 1.02 |
| 1.0e+6 | 134.0 | 128.89 | 1.16 |
| 1.0e+7 | 194.5 | 35.15 | 1.69 |
| 1.0e+8 | 210.9 | 2.44 | 1.83 |

Zakres f1 przy wszystkich 45 kombinacjach E/ρ/k w tej geometrii: **93.1–266.1Hz**. To nie jest fizyczna tolerancja, nie model częstotliwości własnej całej skrzyni ani wynik pomiarowy.

## Kontrole
- Gdy k=0, `f11=(π/2)√(D/ρh)·(1/a²+1/b²)`; zgodność do 0.001Hz dla wszystkich trzech geometrycznych przypadków.
- Statyka z dwóch baz: 5×3 vs 7×5 funkcji. Dla E=2.1GPa, rho=730, k=1e6:
  - 1000×440: 138.43 → 138.59µm, zmiana -0.11%.
  - 1020×425: 128.72 → 128.89µm, zmiana -0.13%.
  - 1040×430: 134.46 → 134.76µm, zmiana -0.22%.
- Kontrola dodatniości energii i brak własnych wartości ujemnych. To kontrole równania redukcji, a nie walidacja spoiny.

## Wniosek dla projektu
**Główną blokadą mechaniki jest nieznana sztywność kontaktu wręga–pozostałe panele i wytrzymałość połączeń**, a nie wyłącznie wybór 22/25/28mm MDF. Zwiększanie grubości bez identyfikacji otoczenia może przenieść rezonans, ale nie musi zlikwidować promieniowania drgających ścian; pełny obciążony MES z koszem, matą, wkładami i spoinami jest niezbędny. Należy zaprojektować wzmocnienia bez blokowania **20 dróg montażowych** i ponownie uruchomić geometrię P30E.

Szczegóły bramek prototypu: odwzorowanie fizycznych łączników i stopek, pełne W,D,H z promieniowaniem paneli oraz charakterystyką jakości przy równym SPL (raport 080). Brak zgody na zamówienie CNC.

## Odtwarzanie
`node skrypty/p31b_plyta_i_podatne_linie.js` zapisuje pełne 135 przypadków do `wyniki/p31b_podatnosc_dwoch_linii_135_20261031.json`. Model liniowy, bez zależności.
