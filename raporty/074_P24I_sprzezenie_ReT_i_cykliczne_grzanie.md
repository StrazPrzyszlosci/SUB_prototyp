# Raport 074 — P24I: jak Re(T) zmienia cykliczną moc cewki w zależności od częstotliwości

**31.10.2026. Status: 162 deterministyczne przebiegi elektrotermiczne i 3 kontrole połowienia kroku.** To obliczenia na nieskalibrowanym modelu Daytona RSS390HF-4 (C02), a nie realny pomiar głośnika lub zabezpieczenia.

## Nowa hipoteza
P24H obliczył okresową temperaturę przy stałej mocy strat `Pcu`. W prawdziwym obwodzie o stałym napięciu źródła prąd zmienia się po ogrzaniu cewki. Zmiana rezystancji może **zwiększyć albo zmniejszyć** Pcu zależnie od impedancji mechanicznej na danej częstotliwości. To zjawisko zmienia kierunek błędu, jeśli do ochrony stosuje się tylko moc zimnej cewki.

## Model i wyprowadzenie
```text
Re(T) = Re0 * (1 + alpha * ΔTc)
Z(f,T)=Re(T)+Zother(f)
Zother(f) = Rs + jωLe + BL²/Zm(f,Vb)
I_rms=U_rms / |Z(f,T)|
Pcu(f,T)=Re(T)*|I_rms|²
dPcu/dRe przy stałym U = U² [|Zother|²-Re²] / |Re+Zother|⁴
```
Jeśli `|Zother|>Re`, wzrost Re początkowo **zwiększa** wydzielaną moc (dla ustalonego napięcia), a przy `|Zother|<Re` ją **zmniejsza**. Ograniczenia prądu i wychylenia zmieniają ten prosty warunek; dlatego w symulacji stosowano osobne modelowe obwiednie `Ipeak≤27A` i `Xpeak≤11.2mm`, a nie wyciągano wniosków wyłącznie z pochodnej.

C02: `Re0=3Ω`, `alpha=0.00393/K`, `Le=0.92mH`, `BL=15Tm`, `Fs=19.5Hz`, `Vb=80l`, topologia termiczna Cauer z P24B, `Rs=0.0026Ω`. Brak zweryfikowanych termicznych i nieliniowych parametrów rzeczywistej sztuki.

## Siatka i kontrola impulsywności
`3 termiki × 3 f (20/40/80Hz) × 3 napięcia zadane (10/20/30Vrms) × 2 okresy (10/30s) × 3 duty (10/25/50%) = 162 przypadki`.

Każdy przypadek porównuje dwa równoległe modele przez maksymalnie 3600 s przy `dt=0.2s`:
1. pełne obliczenie `Pcu(Re(T))` w każdym kroku (model dynamiczny),
2. niezmieniona `Pcu` wyznaczona dla zimnej cewki przy tym samym programie i napięciu (model porównawczy P24H).

Część impulsu wewnątrz kroku obliczono jako **dokładne pokrycie czasowe przedziałów ON/OFF**, nie proste próbkowanie stanu na początku kroku. To zapewnia identyczny całkowity czas pobudzenia w obu porównaniach. Przy osiągnięciu przez którykolwiek model umownego +200 K przerwano obie trajektorie. To koniec zakresu ekstrapolacji, **nie rzeczywista temperatura awarii**.

## Główne wyniki
| f [Hz] | Nominalne |Zother| [Ω] | Zwiększenie maks. Tc | Zmniejszenie maks. Tc | Największa dodatnia różnica [K] | Największa ujemna różnica [K] |
|---:|---:|---:|---:|---:|---:|
| 20 | 2.47 | 18/54 | 32/54 | 20.23 | -14.56 |
| 40 | 13.78 | 28/54 | 0/54 | 0.96 | 0.00 |
| 80 | 1.40 | 0/54 | 54/54 | -0.01 | -49.79 |

Wszystkie grupy mają po 54 przypadki. Dodatnie/ujemne liczby oznaczają `peak(Tdynamic)-peak(Tfixed)` (z tolerancją 0,01 K). **8 przypadków** przerwano na umownym konturze +200K i ich danych nie należy porównywać ze stanem stacjonarnym.

Przykład reprezentatywny: centralna termika, wejście 20 Vrms, cykl 30s/25%:
| f [Hz] | Maks. ΔTc modelu Re(T) [K] | Maks. ΔTc przy zimnej mocy [K] | Różnica [K] |
|---:|---:|---:|---:|
| 20 | 38.69 | 39.70 | -1.02 |
| 40 | 2.57 | 2.56 | 0.01 |
| 80 | 50.60 | 55.60 | -5.00 |

**Interpretacja:** przy 40 Hz w tym uproszczeniu Re(T) zwiększa modelowe grzanie w części scenariuszy, choć wzrost często jest niewielki z uwagi na duży wkład impedancji ruchowej i mniejszy prąd. Przy 80 Hz dodatni efekt nie występuje w siatce, a spadek mocy z temperaturą zmniejsza wynik względem stałej mocy zimnej cewki. Przy 20 Hz znak zmienia się w zależności od aktywnych ograniczeń X/I i amplitudy. Nie oznacza to prawdziwego rozkładu zmian w głośniku.

## Audyt numeryczny
Testy zmiany `dt=0.2s → 0.1s` (porównywanie maks. temperatury):
- `["favorable",20,30,30,0.1]`: różnica **0.0021 K**, obie trajektorie 3600/3600s
- `["central",80,20,10,0.5]`: różnica **0.0138 K**, obie trajektorie 3600/3600s
- `["adverse",40,20,30,0.25]`: różnica **-0.0072 K**, obie trajektorie 3600/3600s
Dodatkowo wszystkie 162 przebiegi przeszły kontrolę idealnego modelowego `Xpeak≤11.2mm`. Tak zdefiniowana kontrola nie jest fizycznym czujnikiem ruchu.

## Decyzje, otwarte bramki
- Nie wolno stale zakładać, że większe Re(T) chroni głośnik przez ograniczenie prądu. Kierunek zależy od Z(f) i aktualnej aktywnej bariery napędu.
- Nie stosować P24H jako końcowego regulatora mocy bez sprzężenia prądu i temperatury oraz bez kalibracji Rth/Cth.
- Ustalenie `Rth/Cth`, niezależny pomiar Re(T) na prawdziwym głośniku, BL(x), Cms(x), Le(f,I), fizyczne U/I, opóźnienia sterownika i badanie akustycznych zniekształceń pozostają wymagane.
- Nie zakładać, że miniDSP ma dostęp do U/I albo może realizować taką pętlę. Płytkowy wzmacniacz musi mieć zweryfikowaną ścieżkę wyciszenia i ochrony zasilania.

## Odtwarzanie
`node skrypty/p24i_sprzezenie_re_cykle.js`

Pełne dane: `wyniki/p24i_sprzezenie_re_cykle_20261031.json`.
