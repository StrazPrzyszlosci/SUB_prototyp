# Raport 093 — P36C: niezależny test dopasowywania postaci drgań metodą MAC

**31 października 2026. Wykonano 36 rozwiązań modów płytowych (12 postaci × 3 rozdzielczości) oraz 24 dopasowania między siatkami.**

> **Zakres dowodu:** zweryfikowano implementację **modal assurance criterion (MAC)** na *odrębnym, analitycznie kontrolowalnym modelu pojedynczej płyty SSSS*, a nie na globalnym MES obudowy P33B. Test służy metodologii przyszłej analizy; **nie dowodzi prawidłowego przyporządkowania rezonansów całej skrzyni ani nie zwalnia konstrukcji do frezowania**.

![Weryfikacja MAC w trzech siatkach](../wyniki/p36c_zgodnosc_MAC_plyta.svg)

## Dlaczego potrzebny jest MAC?

Dotychczas porównywano głównie najmniejszą częstotliwość własną `f1` całego modelu. Przy zmianie siatki, sztywności stóp i masy kosza kolejność modów może się zmieniać. Dopóki nie porównamy **kształtu drgań**, nie wiemy, czy dwie podobne częstotliwości należą do tego samego fizycznego zjawiska.

Dla dwóch wektorów postaci wyrażonych w tych samych punktach obserwacyjnych:

```text
MAC(phi, psi) = |phiᵀ psi|² / [(phiᵀ phi)(psiᵀ psi)]
```

W przypadku rzeczywistych wektorów znak amplitudy nie ma znaczenia. Wartość 1 oznacza zgodne proporcjonalne postacie, 0 oznacza ortogonalność w wybranych punktach. Nie można porównywać wektorów z różnych siatek **bez przeniesienia ich do tej samej przestrzeni fizycznej**.

## Co rzeczywiście wykonano?

Użyto płyty 976 × 359 × 22 mm, E=2,1 GPa, rho=730kg/m³, nu=0,3 i oddzielnego schematu różnic skończonych dla płyty prostokątnej (SSSS). Dokładne postacie podstawowe z `sin(mπx/a)sin(nπy/b)` umożliwiają weryfikację tożsamości modów; częstotliwości dyskretne wynikają z wartości własnych dwuwymiarowego dyskretnego laplasjanu (odpowiedź płyty uzyskuje się przez operator zginania). Dla każdego z 12 modów `m=1..4,n=1..3` na siatkach **8×4, 16×8, 32×12** obliczono amplitudy i interpolowano je na tę samą siatkę obserwacyjną 17×13 punktów wewnętrznych.

Następnie utworzono macierz 12×12 współczynników MAC i rozwiązano problem przyporządkowania metodą programowania dynamicznego (dokładne dopasowanie o maksymalnej sumie MAC, nie proste porównanie kolejności `f1,f2,...`). Dodatkowo sprawdzono, że przyporządkowanie odzyskuje te same pary `m,n`.

## Wyniki

| Porównanie siatek | Średni MAC | Minimalny MAC | Poprawnie dopasowane postacie |
|---|---:|---:|---:|
| 8×4 → 16×8 | **0,98444** | **0,95678** | **12/12** |
| 16×8 → 32×12 | **0,99889** | **0,99705** | **12/12** |

Dla pierwszej postaci (1,1) odrębny schemat różnicowy dał f11 na siatkach 8×4 / 16×8 / 32×12 odpowiednio **151,586 / 154,798 / 155,560 Hz**, przy wartości ciągłej Kirchhoffa **156,243 Hz**. Błąd częstotliwości maleje około **2,98% → 0,92% → 0,44%**. Ten wynik nie jest tożsamy z wcześniej analizowanym elementem Q4 Mindlina, gdyż stosuje odrębną dyskretyzację i mechanikę.

## Ograniczenia

- W płycie wybrano 12 znanych, rozdzielnych postaci; prawdziwa obudowa ma silne sprzężenia paneli i może mieć postacie lokalne, podporowe i prawie zdegenerowane.
- MAC oparty na obserwacji wielu punktów i interpolacji może działać gorzej dla lokalnych modów przy otworze, spoinach i koszu.
- Nie wyznaczono **globalnego MAC dla modelu P33B**. Najpierw trzeba poprawić element i geometrię frontu, a potem eksportować wektory własne i masy dla jednakowych fizycznych punktów pomiaru.
- Kryterium MAC 0,90 w teście jest progiem **diagnostycznym**, nie normowym zwolnieniem MES ani konstrukcji.

## Następny krok

Dodać do globalnego solvera P33B/P35B eksport wektorów własnych i węzłów dla 3 siatek, przenieść postacie na wspólne punkty obserwacyjne sześciu paneli, obliczyć globalną macierz MAC z uwzględnieniem masy oraz ocenić udział modu podporowego. Jeżeli dopasowanie modów nie będzie stabilne, **nie wolno formułować wniosków na podstawie pierwszej częstotliwości**. Dopiero potem możliwe jest rzeczywiste sprzężenie z przestrzennym polem gazu P35A.

**Reprodukcja:** `node skrypty/p36c_test_MAC_plyty.js` → `wyniki/p36c_plate_mode_MAC_20261031.json`. Bez bibliotek zewnętrznych.
