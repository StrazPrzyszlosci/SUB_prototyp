# Raport 073 — P24H: cykliczne grzanie, stan okresowy i powrót po chłodzeniu

**31.10.2026.** Wykonano 60 obliczeń stanów okresowych, 3 testy chłodzenia oraz 3 niezależne kontrole numeryczne. Jest to wyłącznie **nieskalibrowany model Cauer** dla wstępnego Daytona RSS390HF-4; nie pomiar i nie dobór dopuszczalnej mocy.

## Motywacja i metoda
P24G ujawnił konserwatyzm jednorazowego odcinania. Potrzebne są cykle grzanie–przerwa i oszacowanie temperatury pozostałej w układzie magnetycznym.

Równania liniowe dwuwęzłowego Cauer:
```
Cc*dTc/dt = Pcu -(Tc-Tm)/Rcm
Cm*dTm/dt = (Tc-Tm)/Rcm - Tm/Rma
x(t+τ) = exp(Aτ) x(t) + [I-exp(Aτ)] x_eq(Pcu)
x_eq(Pcu) = [Pcu(Rcm+Rma), Pcu Rma]
```

Dla naprzemiennej **stałej mocy strat cewki** 1 W w fazie ON i 0 W w OFF rozwiązano stan okresowy:
`x0=Foff Fon x0 + Foff(I−Fon)x_eq(1W)`. Maksimum Tc wyznaczono z dokładnego rozwiązania czasowego próbkowanego w 401 punktach okresu. Zależność od mocy P jest liniowa. Jest to analiza strat w miedzi, **nie mocy zasilania wzmacniacza**.

Siatka: 3 hipotetyczne termiki z P24B × okresy 2/10/30/120 s × udział pracy 5/10/25/50/100% = **60 modeli**. +80 K jest jedynie konturem porównawczym.

## Przykładowy stan okresowy: 7,5 s ON / 22,5 s OFF
Wyliczono poziom stałej mocy strat cewki w ON prowadzący w danym modelu do szczytowego przyrostu +80 K w stanie okresowym:

| Zestaw Cauer | Strat miedzi podczas ON [W] | Średnia moc strat [W] |
|---|---:|---:|
| favorable | 270.1 | 67.5 |
| central | 133.2 | 33.3 |
| adverse | 74.3 | 18.6 |

Zwiększenie udziału pracy lub okresu może zwiększyć maksimum Tc nawet przy zbliżonej średniej mocy. **Nie interpretować tych wartości jako dopuszczalnego obciążenia Daytona.** Rzeczywista moc strat zależy od Re(T), zespolonego Z(f), zawartości widma i sterowania.

## Chłodzenie po 30 sekundach hipotetycznych strat 200 W
Test rozpoczyna się ze stanu zimnego, po 30 s wymuszenia Pcu=200 W wyłącza się grzanie. W raporcie +20 K jest kolejnym arbitralnym znacznikiem:

| Zestaw Cauer | Przyrost Tc po 30 s [K] | Przerwa aż oba modelowe węzły znajdą się poniżej +20 K [s] |
|---|---:|---:|
| favorable | 37.44 | 16 |
| central | 86.47 | 40 |
| adverse | 172.95 | 68 |

Dwa węzły magazynują energię w różnym czasie. Dlatego sam upływ czasu od wyciszenia ani szybki spadek rezystancji cewki nie potwierdzają gotowości do ponownego pełnego wysterowania.

## Testy wiarygodności numerycznej
1. Dla sygnału ciągłego (100% ON) zweryfikowano tożsamość `Tc=Pcu(Rcm+Rma)`.
2. Stan końca okresu odtwarzany z eksponenty macierzy zgadza się ze stanem początkowym do 1e−6 K/W.
3. Osobne całkowanie Eulera dt=0.02 s po 1000 cykli 30s z 20% ON (1 W) dało:
- favorable: |Euler − analityczny| = 0.000014 K/W
- central: |Euler − analityczny| = 0.000029 K/W
- adverse: |Euler − analityczny| = 0.000059 K/W

Testy nie weryfikują fizycznych parametrów Cauer, jedynie matematyczną spójność.

## Braki do rzeczywistej ochrony
- Dane Rth/Cth producenta nie są zweryfikowane. Moc 80K ani czas do 20K nie są normą bezpieczeństwa.
- Nie połączono elektrycznego `Re(T)`, ruchu membrany, oddychania membrany, silnej nieliniowości ani różnych częstotliwości z P24B/P24F.
- Nie wykonano walidacji DSP ani płytek wzmacniacza, pomiaru prądu, sterowania MUTE/EN i testów na dwóch fizycznych kanałach.
- Nie ma projektu schematu zabezpieczeń 230 V.

**Dalszy etap P24I:** sprzęgnąć okresowe Pcu z zależnym od temperatury prądem i nieliniowym, szerokopasmowym programem oraz przetestować logikę restartu, a nie nazywać powyższego algorytmem gotowym do instalacji.

## Odtwarzanie
`node skrypty/p24h_cykle_recovery.js`

Dane: `wyniki/p24h_cykle_recovery_20261031.json`. Brak zależności zewnętrznych.
