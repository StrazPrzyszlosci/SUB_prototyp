# Raport 090 — P35B: ponowne obliczenia globalnego Q4 po audycie hourglass

**31 października 2026. Wykonano 16 obliczeń pełnej siatki obudowy P33B z lokalnie stabilizowanym elementem Q4, plus testy płyty wzorcowej i jądra elementu.** Wszystkie wyniki są **numerycznym badaniem wrażliwości**, a nie zwalidowanym modelem produkcyjnym.

![Wrażliwość ugięć na stabilizację i siatkę](../wyniki/p35b_stabilizacja_Q4_siatki.svg)

## Dlaczego to istotne?

P33C wykazał, że element Q4 P33B ma **8 zamiast 6** zerowych mechanizmów: dwa sztuczne *hourglass*. Dodanie pełnego całkowania ścinania usuwa je, ale na grubej siatce blokuje ścinanie i zawyża częstotliwość testowej płyty. Nie można uznać, że sam test jednej płyty zatwierdza całą skrzynię.

W tej kampanii podmieniono funkcję elementu w **tym samym globalnym modelu P33B** na rodzinę macierzy z audytu P33C:

```text
K_gamma = K_membrane+bending(2x2)
        + K_shear(1x1) + gamma * (K_shear(2x2) - K_shear(1x1))
```

Badano gamma=0;0,001;0,01;0,03 oraz siatki 150/110/85mm; dodatkowo 4 scenariusze podatności naroży. Całą kampanię **wykonano lokalnie na Python/NumPy/SciPy**, odtworzenie w repo przez `skrypty/p35b_globalne_gamma_Q4.py`.

## Poprawność elementu i płyty

- gamma=0: **8 mechanizmów zerowych** pojedynczego Q4 (2 sztuczne).
- gamma=0,001;0,01;0,03: **6 mechanizmów** w pojedynczym swobodnym elemencie, czyli usunięcie dodatkowych zerowych postaci **lokalnie**.
- Dla swobodnie obracanej płyty 976×359×22mm, analityczne f11 Kirchhoffa =156,243Hz. Przy siatce 32×12: gamma=0,001 daje **154,038Hz** (−1,41%); gamma=0,01 daje **154,343Hz** (−1,22%); gamma=0,03 daje **155,018Hz** (−0,78%). To test płyty, **nie** całości, i różnica zawiera teorię Mindlina.

## Globalna odpowiedź z tymi samymi hipotetycznymi spoinami — przy siatce ~110 mm

| gamma | Pierwsza częstotliwość modelowego zespołu | Maksymalne ugięcie przy umownym 1000 Pa |
|---:|---:|---:|
| 0 (niestabilizowany) | 32,870 Hz | 83,28 µm |
| 0,001 | 32,874 Hz | 83,09 µm |
| 0,01 | 32,904 Hz | 81,44 µm |
| 0,03 | 32,961 Hz | 78,06 µm |

To **częstotliwości umownie podpartej całej bryły**, niekoniecznie drgania poszczególnych ścian. Dla gamma=0,001 na siatkach 150/110/85mm kolejno modelowe f1: **30,367/32,874/33,660Hz**, ugięcia **99,51/83,09/86,18µm**. Różnice między siatkami nie są monotoniczne — potrzebne są lepsze elementy, zgodność postaci przez MAC i dokładna siatka otworu.

## Co zmienia sztywność hipotetycznych spoin?

Przy gamma=0,001, siatce ~110mm, wraz ze zmianą trans/rot-spoin od 3×10⁶/300 do 3×10⁸/30000, modelowe ugięcie zmienia się od **161,94 do 48,99µm**. To ponad trzykrotna różnica **w tym samym modelu**. Zatem nawet lokalnie stabilizowany element nie rozstrzygnie konstrukcji bez danych materiałowych dla połączeń.

**Kluczowy wniosek:** przyjęta stabilizacja gamma zmienia wyniki tylko umiarkowanie w części zakresu, ale nie stanowi testu fizycznego. Nie odzyskano kwalifikacji globalnego MES P33B do frezowania CNC. Należy odróżniać stabilizację, shear locking, podatność spoin i geometrię kosza. Każdy z tych problemów wymaga oddzielnej kontroli.

## Blokady przed zwolnieniem dokumentacji wykonawczej

1. Testy patch/h​ourglass przy różnych proporcjach i orientacjach elementów, 3 siatki **z kołowym, dopasowanym otworem** i lokalnymi wkrętami, pomiar E/nu/rho i strat MDF.
2. Faktyczny model połączeń klejonych i łączników: sztywność translacyjna, obrotowa, odrywanie i pełzanie; pomiar próbek.
3. Porównanie postaci modów przez MAC i przypisanie do paneli zamiast porównywania tylko najmniejszej częstotliwości.
4. Mapowanie sił akustycznych P35A na ściany wraz z oporem przepływowym maty i modelem reakcji kosza.
5. Dopiero po zbudowaniu pierwszego prototypu: pomiary drgań, impedancji i THD przy równoważnym SPL.

**Dalsza rekomendacja projektowa:** korpus 1020×425×500mm i 100/120/150l traktować jako platformę badawczą, **nie** projekt do zatwierdzenia frezowania. Nie znamy jeszcze rzeczywistej sztywności MDF i spoin, a masa kosza i wkładów jest w modelu tylko przykładowa.

**Reprodukcja:** `python skrypty/p35b_globalne_gamma_Q4.py --out wyniki/p35b_stabilizacja_globalna_16_20261031.json` (NumPy/SciPy, import oryginalnych modeli P33B/P33C).