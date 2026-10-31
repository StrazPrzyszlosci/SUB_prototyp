# Raport 082 — P32A: dynamiczne drgania panelu i tłumienie podatnych wręg

**31.10.2026. Wyniki: 36 modeli × 17 częstotliwości = 612 analiz harmonicznych**, wraz z kontrolą zbieżności i bilansu mocy. Nie jest to pełny MES ani akustyczne promieniowanie gotowej obudowy.

## Co chcemy zrozumieć?
Nie wystarczy sprawdzić, przy jakiej częstotliwości ścianka ma pierwszy rezonans. Dla jakości subwoofera równie ważne jest to, **jak mocno rzeczywiście drga pod wymuszeniem**. W ramach nowego etapu, po korekcie wymiarów P31B, rozwiązano odpowiedź zespoloną płyty z dwiema sprężystymi liniami podparcia w paśmie 20–180 Hz.

![Odpowiedź płyty](../wyniki/p32a_widmo_drganiowe.svg)

![Porównanie wpływu wręg i tłumienia](../wyniki/p32a_wregi_i_tlumienie.svg)

## Model i zakres
Korpusy 1000×440 oraz 1020×425mm, płyta rozpięta wewnętrznie (W−44)×(D−66)mm i grubość 22mm; zakres E=1,5/2,1/3,0GPa, ρ=730kg/m³. Dwa podatne podparcia do nieruchomego podłoża, k=0/10⁶/10⁷ N/m². Założona strata modelowa ζ=2%/5%. Jednorodne, sinusoidalne ciśnienie 1000Pa *peak* (wyłącznie scenariusz, nie pomiar). Baza Kirchhoffa 7×5:
```
(K − ω² M + jω C) q = F
C = α M + β K,  α = 2ζω₁ω₃/(ω₁+ω₃), β = 2ζ/(ω₁+ω₃), ω₃ = 3ω₁
```
Sprawdzono bilans mocy zespolonej `P_in=-ω Im(Fᵀq)/2` i strat `P_loss=ω² q* C q/2`; zgodność na dokładność liczbową, nie test fizyczny.

## Reprezentatywne wyniki: 1020×425mm, E=2,1GPa, ζ=2%
| Linia k N/m² | Modelowa f1 Hz | Środek 20Hz µm | Środek 80Hz µm |
|---:|---:|---:|---:|
| 0.0e+0 | 156.2 | 98.0 | 132.8 |
| 1.0e+6 | 171.1 | 79.3 | 101.5 |
| 1.0e+7 | 228.5 | 28.3 | 31.3 |

**Wynik:** w tym modelu podatność wręg znacznie zmienia wymuszoną amplitudę ścianki w całym paśmie. Sama skala drgań nie jest znormalizowanym SPL promieniowania, więc nie wolno z niej wyprowadzać udziału THD/IMD gotowej skrzyni.

## Weryfikacja
1. Pierwsza częstość płyty bez wręg: **156,243 Hz**, zgodna z poprawionym P31B.
2. 36×17 analiz miało dodatnie straty i zamknięty bilans mocy, resztę poniżej 10⁻⁷.
3. Porównanie bazy 7×5 do 9×7 dla przypadku k=10⁶:
- 20Hz: 79.298 vs 79.367 µm (0.087%).
- 80Hz: 101.520 vs 101.599 µm (0.078%).
- 130Hz: 192.852 vs 193.035 µm (0.094%).
- 160Hz: 642.092 vs 644.081 µm (0.309%).

## Ograniczenia i następne bramki
Podparcia są nieruchome, a rama rzeczywista jest podatna; materiał MDF i klej nie zostały skalibrowane. Wymuszenie 1000Pa i tłumienie Rayleigha założono; nie odpowiadają określonemu poziomowi SPL. Żaden wynik nie jest zgodą na CNC, prognozą realnego promieniowania paneli ani trwałością spoin.

**Następne badanie powinno obejmować komplet paneli, wręgi, front, kosz, mocowania i sprzężenie akustyczne**, z weryfikacją zbieżności siatki. Jeśli brak rzeczywistych modułów E/G/strat spoin, trzeba podać przedziały wrażliwości i testy próbek, a nie udawać pełnej walidacji.

## Odtwarzanie
`node skrypty/p32a_dynamika_panelu.js`; zapisze `wyniki/p32a_dynamika_panelu_612_20261031.json`. Bez bibliotek zewnętrznych.
