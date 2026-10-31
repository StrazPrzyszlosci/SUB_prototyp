# Raport 085 — P33C: audyt *hourglass* elementu Q4 w P33B

**31 października 2026. Wykonano 8 testów własnych pojedynczego elementu oraz 18 testów płyty o trzech gęstościach siatki.** Skrypt `skrypty/p33c_hourglass_audyt.py` reprodukuje obliczenia NumPy/SciPy, importując dokładnie element `shell_element` z P33B.

> **Uwaga naukowa:** w P33B (raport 084) zidentyfikowano **dwa nadmiarowe zerowe mechanizmy pojedynczego elementu**, nazywane *hourglass*. Historyczne liczby przemieszczeń i częstości globalnych P33B **nie są zweryfikowanymi osiągami konstrukcji**. Wnioski z tamtego raportu oznaczamy jako obarczone błędem dyskretyzacji i stabilizacji; wymagają ponownego policzenia przed jakimikolwiek decyzjami wykonawczymi.

## Co sprawdzono i dlaczego?

Dla płaskiej powłoki Reissnera–Mindlina Q4 z 5 stopniami swobody na węzeł, jeden niepodparty element ma 20 DOF i **sześć ruchów bryły sztywnej**. Pozostałych 14 kombinacji powinno mieć dodatnią energię odkształcenia. W dotychczasowym P33B całkowanie ścinania poprzecznego w jednym punkcie prowadzi do **8, a nie 6** wartości własnych bliskich zeru. Sześć zadanych kinematycznie ruchów sztywnych odtwarza zerową energię zgodnie z dokładnością numeryczną; dodatkowe dwa wektory to mechanizmy artefaktowe.

Badany numeryczny parametr `γ` miesza pełne (2×2) i zredukowane (1×1) całkowanie ścinania, bez zmiany części membranowo-zginającej:

```text
K(γ) = K_P33B + γ (K_shear[2×2] − K_shear[1×1])
```

Nie jest to kalibracja MDF ani przemysłowo kwalifikowana stabilizacja.

## Wynik elementarny

| γ | Liczba zerowych postaci | Wniosek |
|---:|---:|---|
| 0 | **8** | dwa nadmiarowe mechanizmy |
| 0,00001 | 6 | dodatnia, ale bardzo słaba stabilizacja |
| 0,001 | 6 | usunięcie dwóch mechanizmów lokalnie |
| 0,01 | 6 | usunięcie dwóch mechanizmów lokalnie |
| 0,1 | 6 | usunięcie mechanizmów, ryzyko usztywnienia |
| 1 | 6 | pełne całkowanie, silne ryzyko *shear locking* |

## Test drugiego rodzaju: 976 × 359 × 22 mm

Porównano własną częstość płyty swobodnie obracanej na krawędziach i podpartej w przemieszczeniu poprzecznym z analitycznym wzorem Kirchhoffa **156,24 Hz**.

| γ | Q4 8×4 | Q4 16×8 | Q4 32×12 |
|---:|---:|---:|---:|
| 0 | 153,65 | 153,97 | 154,00 |
| 0,001 | 153,98 | 154,05 | 154,04 |
| 0,01 | 156,92 | 154,75 | 154,34 |
| 0,03 | 163,13 | 156,29 | 155,02 |
| 0,1 | 182,62 | 161,52 | 157,35 |
| 1 | **337,51** | 216,51 | 184,31 |

Przy γ=1 na siatce 8×4 częstotliwość wynosi 337,5 Hz zamiast 156,2 Hz. **Stabilizacja mechanizmów zerowych i zablokowanie ścinania są różnymi błędami, które trzeba testować równocześnie**. Dobór γ=0,001 lub 0,01 tylko dlatego, że daje wartość bliską wzorowi płyty, nie uzasadnia identycznego wyboru dla dowolnej siatki pełnej obudowy.

## Co to zmienia w projekcie?

1. Otworzyć ponowną kontrolę P33B przed przypisywaniem konkretnego ugięcia całej skrzyni. Jedyny poprzedni wynik 83,3 µm (dla danego ustawienia) **nie jest zatwierdzonym parametrem mechanicznym**.
2. Wprowadzić element odporny na hourglass/shear locking albo zbadaną metodę stabilizacji i przeprowadzić testy płatka, patch tests, różne grubości, obrót siatki i modele 6-DOF/krawędzi.
3. Dopiero następnie powtórzyć siatki całego korpusu, porównać identyczne obciążenia i spoiny, obliczyć MAC modów, szacować niepewność oraz wykonać współmodelowanie komory.

Nie zmienia się konstrukcyjny punkt startowy **1020×425×500 mm**, 100/120/150 l i Dayton RSS390HF-4 jako wstępny faworyt. Brakuje też pełnego CAD, rzeczywistych właściwości kleju, MDF i mocowań. **Nie wydano zgody na cięcie CNC.**

## Odtwarzanie

`python skrypty/p33c_hourglass_audyt.py --out wyniki/p33c_hourglass_audyt.json`

Wynik zawiera 26 testów. Nie należy porównywać liczby z P33A i P33B jako „dokładniejszej” bez wspólnych warunków brzegowych.