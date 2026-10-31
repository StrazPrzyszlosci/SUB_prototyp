# Raport 095 — P37B: czułość i identyfikowalność E, gęstości oraz spoin

**1 listopada 2026.** Przeprowadzono **8 dodatkowych globalnych rozwiązań MES** do metody różnic centralnych, w sumie z P37A **14 przebiegów** dla tych kampanii. Weryfikowano wrażliwość na: E MDF, gęstość MDF, sprężyste połączenia translacyjne i obrotowe.

![Które parametry wpływają na obliczone ugięcie i częstotliwość?](../wyniki/p37b_wrazliwosc_material_spoiny.svg)

## Dlaczego nie wystarczy kupić MDF o znanej grubości?

Elektryczne i akustyczne cechy subwoofera nie pozwalają określić prawdziwego modelu spoin. Nawet poprawnie stabilizowany element Q4 może dawać nieprawidłowe ugięcia, jeśli **sprężystość klejonych naroży i wręg** jest tylko zgadywana. Chcemy oddzielić:
- parametry mierzalne bez niszczenia materiału: gęstość i wymiary MDF;
- parametry możliwe do odtworzenia z ugięcia próbki: moduł Younga i kierunkowość;
- parametry wymagające osobnej próbki połączenia: sztywność ścinania i obrotu, odrywanie, pełzanie;
- niepewności wynikające z samej dyskretyzacji i mocowania.

## Zakres obliczeń

Model bazowy: 1020×425×500mm, E=2,1GPa, rho=730kg/m³, gamma=0,001, siatka ~110mm, k_trans=3×10⁷N/m², k_rot=3×10³ (hipotetyczny parametr modelowy). Analiza po jednej zmiennej naraz: **E ±10%**, **rho ±10%**, **k_trans ×0,1 i ×10**, **k_rot ×0,1 i ×10**. Wszystkie pozostałe parametry niezmienne.

Znormalizowaną elastyczność oszacowano:

\[
S_{y,x}=\frac{\ln[y(x_+)/y(x_-)]}{\ln(x_+/x_-)}
\]

Jest to pochodna skończona **modelu**, nie zmierzona niepewność rzeczywistego materiału i nie fizyczna tolerancja ±10% producenta. Współczynniki dla spoin liczono przez bardzo szeroki zakres, więc nie są bezpośrednio porównywalnymi „ważnościami” przy tej samej niepewności.

## Wyniki numeryczne

| Zmieniana cecha | Przedział | Elastyczność f1 | Elastyczność ugięcia |
|---|---|---:|---:|
| Moduł E MDF | 0,9×–1,1× | +0,188 | **−0,774** |
| Gęstość MDF | 0,9×–1,1× | **−0,307** | 0,000 |
| Sztywność translacyjna spoin | 0,1×–10× | +0,062 | −0,149 |
| Sztywność obrotowa spoin | 0,1×–10× | +0,002 | −0,117 |

Dla k_trans ×0,1 / ×10 ugięcie w przyjętym modelu zmienia się **149,5 → 75,1 µm**, a dla k_rot ×0,1 / ×10 **95,5 → 55,7 µm**. Zmiana E ±10% daje **90,1 → 77,2 µm**. Gęstość nie zmienia odpowiedzi statycznej przy tych samych siłach, ale zmienia obliczaną częstość własną.

**Wniosek metodologiczny:** nie da się z samego f1 niezawodnie rozdzielić wpływu E, gęstości i spoin; podobne zmiany częstotliwości mogą być spowodowane różnymi parametrami. Do identyfikowalności potrzebne są **oddzielne pomiary masy, ugięć, sztywności spoin i kilku modalnych kształtów**, a nie tylko jeden pomiar f1. Nie wykonano jeszcze rzeczywistych prób materiałowych.

## Rekomendowana kolejność pomiarów

1. **Gęstość / wilgotność MDF**: masa i objętość próbek 22 i 44mm (min. 3 powtórzenia na grupę), zapis daty i warunków.
2. **E i anizotropia**: ugięcie belki z MDF w dwóch orientacjach przy trzech znanych obciążeniach + weryfikacja metodą swobodnych drgań. Obliczyć przedziały niepewności.
3. **Spoiny**: osobne próbki docelowego kleju i sposobu montażu, rejestracja siła–przemieszczenie i moment–kąt. Nie wyznaczać nośności wyłącznie ze sprężyn FEM.
4. **Wręga z panelem**: pomiar podatności fragmentu zespołu, nie samej pojedynczej płyty.
5. **Przed CNC**: uzupełnienie CAD otworu, kosza, śrub, stopek i blokad oraz porównanie trzech siatek z MAC globalnym.

Jeśli próbki i przyrządy nie są dostępne, można przygotować **protokół pomiarowy i listę brakujących danych**, ale nie wolno wpisywać fikcyjnych wyników do repozytorium.

**Ograniczenie:** amplitudy Q4 są obciążeniem hipotetycznym 1000Pa i nie reprezentują rzeczywistego SPL, THD/IMD ani wytrzymałości spoin. [Skrypt](../skrypty/p37_mac_globalny_i_wrazliwosc.py) · [Wyniki skrócone](../wyniki/p37_globalny_mac_wrazliwosc_PODSUMOWANIE_20261101.json). **Nadal brak podstaw do wydania plików CNC.**