# Raport 092 — P36B: Dayton i dwa STX przy podatności ścian obudowy

**31 października 2026 | Wykonano 972 warianty modeli liniowych 3 przetworników w zamkniętej skrzyni.**

> **Ograniczenie:** F3, Fc i Qtc to charakterystyki **małosygnałowego liniowego modelu akustyczno-mechanicznego**, nie pomiar brzmienia, SPL, zniekształceń ani kompresji. Podatność MDF jest wzięta z **statycznego** modelu P36A i użyta jako ekwiwalent objętości, co nie jest prawidłowym dynamicznym modelem przy rezonansach ścian. Wyniki nie zastępują pełnego sprzężenia akustyka–konstrukcja.

![Porównanie F3 trzech przetworników w 120 l](../wyniki/p36b_F3_Dayton_STX_P36.svg)

## Dane wejściowe — wprost z repozytorium

Źródło: `dane/przetworniki/pula_rozszerzona.json`, konfiguracje C02/C06/C08.

| Id | Głośnik | Fs | Vas | Qes | Qms |
|---|---|---:|---:|---:|---:|
| C02 | Dayton RSS390HF-4 | 19,5 Hz | 212 l | 0,50 | 3,02 |
| C06 | STX W.32.800.8.FCX | 24 Hz | 96 l | 0,45 | 3,34 |
| C08 | STX W.38.800.8.MC | 28 Hz | 247 l | 0,27 | 3,71 |

Uwaga na podobne nazwy przetworników Dayton: **C02 to 15-calowy RSS390HF-4**, a nie RSS315HF-4. Rzeczywiste T/S zakupionego egzemplarza mogą się różnić od wartości katalogowych.

## Model

```text
Qts = Qes*Qms/(Qes+Qms)
Veff = Vb + Veq_wall              [tylko zastępczy scenariusz statyczny]
Fc = Fs*sqrt(1+Vas/Veff)
Qtc = Qts*sqrt(1+Vas/Veff)
A = 1/(Qtc²) - 2
F3 = Fc*sqrt((A+sqrt(A²+4))/2)
```

Policzono bez DSP i bez pomieszczenia `3 przetworniki × 324 warianty P36A = 972`. Dla każdego zapisano odpowiedź 25/35/50 Hz, Fc, Qtc, F3, różnicę między sztywną skrzynią a P36A oraz osobno diagnostykę ważenia ciśnieniem z P35A (nie traktować jako częstotliwościowo poprawnego sprzężenia).

## Wyniki bazowe — 120 l, MDF 22 mm, E=2,1 GPa, ρ=730 kg/m³

| Głośnik | F3 sztywna skrzynia | F3 + modelowa podatność bez wręg | F3 + dwie idealne linie |
|---|---:|---:|---:|
| **Dayton RSS390HF-4** | **32,15 Hz** | **32,16 Hz** | **32,14 Hz** |
| STX W.32.800.8.FCX | 45,83 Hz | 46,23 Hz | 45,95 Hz |
| STX W.38.800.8.MC | 90,97 Hz | 92,07 Hz | 91,31 Hz |

**Wniosek:** Dayton RSS390HF-4 w **liniowym** modelu tej obudowy daje znacznie niższe F3 niż STX C06 i C08. Dla C02 dodana statyczna podatność ścian nie zmienia prawie F3, co jest konsekwencją jego Fs, Vas i dobroci. **Nie oznacza to, że niegroźne są rezonanse ścian lub ich własne promieniowanie.** W górnym paśmie basu mogłyby zabarwiać dźwięk mimo niezmienionej liczby F3.

STX W.38.800.8.MC nadal może być znacznie tańszym rozwiązaniem, jeśli przyjęto **inne docelowe wymagania** dla głębokości pasma, korekcji i maksymalnego wysterowania. Nie wynika z tych obliczeń, że marka STX ma gorszą subiektywną jakość; nie policzono THD/IMD przy tym samym SPL ani wzmacniacza 8Ω względem 4Ω.

## Ograniczenia kluczowe dla dalszej decyzji

1. Efektywny litraż dynamiczny jest zespolony i zależny od częstotliwości, ponieważ ściany mają masę, tłumienie i rezonanse. **Nie zastępuj rzeczywistej podatności po prostu sumą litrów z P36A** przy projektowaniu DSP.
2. Nie symulowano amplitudy membrany, nieliniowości Bl(x), Cms(x), Le(i), przepływu powietrza, przecieku, termiki, obciążenia wzmacniacza ani odpowiedzi pomieszczenia.
3. Idealizacja frontu bez otworu, idealnych wręg i nieznanych spoin z P36A powoduje nieograniczoną niepewność rzeczywistej podatności.
4. Dopóki nie ma dokładnego projektu CAD i pomiarów, **nie zmieniać głównej rekomendacji C02** ani nie zamawiać paneli pod ostateczny CNC.

**Reprodukcja:** najpierw `node skrypty/p36a_podatnosc_i_grubosc_MDF.js`, następnie `node skrypty/p36b_przetworniki_i_podatnosc.js`. Zapis: `wyniki/p36b_trzy_glosniki_972_20261031.json`. Bez pakietów zewnętrznych.
