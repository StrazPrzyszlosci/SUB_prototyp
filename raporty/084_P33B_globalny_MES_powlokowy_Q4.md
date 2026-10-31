# Raport 084 — P33B: zintegrowany MES powłokowy Q4 całej obudowy

> **KRYTYCZNE SPROSTOWANIE P33C (31.10.2026):** [Raport 085](085_P33C_audyt_hourglass_elementu_Q4.md) wykazał **dwa nadmiarowe mechanizmy hourglass** pojedynczego elementu Q4 w P33B. Wartości ugięć i częstotliwości w dalszej części są HISTORYCZNYM, NIEZWALIDOWANYM eksperymentem; nie używać ich do ustalania wymiarów, nośności lub wyboru spoin bez stabilizacji elementu i ponownego, poprawnego rozwiązania całego korpusu. Sama zbieżność prostej płyty nie wykryła tej wady.


**31.10.2026. Wykonane: 15 modeli numerycznych, trzy zagęszczenia siatki, trzy poziomy podatności naroży i sześć prób masy/wręg, plus niezależna kontrola płyty.**

**Status:** opracowano działający, globalny **MES powłokowy z obrotami węzłów (Q4 Reissnera–Mindlina)**. To nie jest jeszcze zwalidowany model CAD produkcyjny: połączenia i geometria kosza/wkładów są uproszczone, a sztywności spoin i stopki nie zmierzone. Wnioski konstrukcyjne dotyczą **wrażliwości**, nie rzeczywistych rezonansów ani wytrzymałości.

![Rozbieżność P33A i powłokowego P33B](../wyniki/p33b_rozbieznosc_modeli.svg)

## 1. Co nowego względem P33A?

P33A (083) miał trzy translacyjne stopnie swobody węzła. P33B używa Q4 5 DOF lokalnie: dwa przesunięcia styczne, jedno normalne i dwa obroty związane ze zginaniem. W globalnej konstrukcji stosuje **6 DOF na węzeł**; obrót „drilling” normalny do płaszczyzny panelu jest jedynie słabo stabilizowany. Dodatkowo modele przekazują między ścianami także **momenty przez sprężyny obrotowe**, czego P33A nie robił.

Płytę Q4 całkowano 2×2 Gaussa dla rozciągania/zginania i 1 punktem dla ścinania Reissnera–Mindlina, co ogranicza zablokowanie poprzeczne (shear locking). Jest to model metodą elementów skończonych; nie dowodzi jednak braku modów klepsydrowych (hourglass). *Deklarowanego w kodzie słabego stabilizatora nie należy utożsamiać z pełnym testem hourglass.*

Geometria jak P30E: 1020×425×500 mm, MDF22 mm / front44 mm, otwór Ø355,8 mm o środku x=231, z=250 mm, wręgi na x≈426 i701 mm. Otwór reprezentują **ułamkowe pola elementów kwadratowych**, a nie siatka dopasowana do koła. Dwa obwody wręg to dodatkowe energie belek; rama U, zamki, śruby, detale MDF i przekroje spoin wymagają kolejnej iteracji.

## 2. Test analityczny osobnej płyty — wykonany

Dla prostokąta 976×359×22 mm, E=2,1GPa, ν=0,3, ρ=730kg/m³ przy krawędziach po prostu podpartych mamy analityczny wzór Kirchhoffa f₁₁=**156,243 Hz**. Osobno zestawiony model Q4 dał:

| Siatka Q4 | f₁ [Hz] | Odchylenie od analitycznego Kirchhoffa |
|---|---:|---:|
| 8×4 | 153,649 | −1,66% |
| 16×8 | 153,968 | −1,46% |
| 32×12 | 154,004 | −1,43% |

Różnica zawiera efekt odkształcenia poprzecznego Mindlina i dyskretyzacji, nie tylko błąd numeryczny. Test dotyczy **jednej swobodnie podpartej płyty**, nie zatwierdza spoin lub całej skrzyni.

## 3. Odpowiedź globalnej skrzyni

Wszystkie liczby odnoszą się do sztucznego ciśnienia 1000 Pa, hipotetycznego E MDF 2,1 GPa, umownych sprężyn stopki 1,5MN/m, masy kosza 15kg i wkładów 8kg. Współczynniki k_trans/k_rot są **scenariuszami**, nie badaniami klejów.

| Docelowy krok siatki | Naroża podatne, µm | Naroża pośrednie, µm | Naroża sztywniejsze, µm |
|---|---:|---:|---:|
| 150 mm | 185,95 | 100,02 | 60,02 |
| 110 mm | 162,16 | 83,28 | 49,13 |
| 85 mm | 162,60 | 86,34 | 51,82 |

W wariancie pośrednim najniższa częstotliwość zespołu wynosi dla kolejnych siatek: 30,34; 32,87; 33,65 Hz. Są to częstotliwości **całego umownie podpartego układu**, mogą zawierać ruchy podporowe, a nie tylko rezonanse ścian. Ostatnie dwa wyniki ugięcia różnią się o około 3,7%; siatki bardziej precyzyjne oraz kontrola postaci przez MAC są wciąż potrzebne.

Dla średniej siatki i pośrednich naroży wariant bez modelowych wręg daje 221,96 µm, z dwoma obwodami wręg 83,28 µm. Tak duża zmiana pokazuje wrażliwość na **idealizację geometrii wręg i ich przenoszenia momentów**, nie potwierdza rzeczywistej redukcji drgań w gotowej skrzyni.

## 4. Niezgodność metody P33A i P33B jest wynikiem badawczym

Przy zbliżonej, ale **nie równoważnej** siatce i założonych połączeniach:
- P33A model 3DOF, krok 105mm: modelowe maksimum **330,68 µm**;
- P33B model Q4 6DOF, krok 110mm: modelowe maksimum **83,28 µm**.

Różnica bliska **4×** pokazuje, że obliczenia są **wrażliwe na klasę modelu i opis połączeń**. Nie wolno wybierać „lepszego” wyniku ani traktować średniej obu jako przewidywanego fizycznego ugięcia. Do właściwego porównania potrzebna jest wspólna energia, identyczny model spoin, odniesienie siatkowe i dane pomiarowe. P33A nie jest modelem wyższej lub niższej gwarantowanej sztywności względem P33B.

## 5. Co pozostaje do faktycznie wykonawczego MES?

1. **Model CAD wszystkich elementów**: realny kształt kosza, ośmiu lub faktycznej liczby otworów śrubowych, maskownica, wręgi wraz z tylną ramą U, szczelne wkłady, zamki, terminal, tuleje i stopy.
2. **Siatka frontu dopasowana do koła** i lokalnie zagęszczona przy śrubach/spoinach; testy hourglass oraz poprawne przeniesienie mimośrodowych sił.
3. **Materiał MDF i klej**: ortotropia, moduły zależne od kierunku, temperatury, wilgotności i czasu, sztywność połączeń na obrót i odrywanie, nośność oraz zmęczenie.
4. **Prawdziwy model obciążenia**: siła reakcji kosza i silnika, grawitacja w obu ustawieniach, rozkład ciśnienia 3D z nowej komory P21G dla 100/120/150 l.
5. **Walidacja akustyczno-mechaniczna**: drgania paneli, nieszczelności, promieniowanie obudowy i testy THD/IMD po zbudowaniu pierwszej sztuki.

## Decyzja

**Dalszy projekt nadal opierać na korpusie 1020×425×500mm z regulacją 100/120/150l, stan bazowy 120l.** Po P33B brakuje przede wszystkim danych dla spoin i rzeczywistej geometrii mocowań, a nie kolejnych teoretycznych litrów skrzyni. **Nadal nie wolno zamrażać projektu do frezowania CNC.**

## Odtwarzanie

`python skrypty/p33b_powlokowy_fem.py --out wyniki/p33b_shell_15_przypadkow.json`

Wymaga NumPy, SciPy. Wersja skrótowych wyników: `wyniki/p33b_shell_podsumowanie_15_20261031.json` (w tym kontrola osobnej płyty); program tworzy wszystkie 15 przypadków. Wszystkie masy i obciążenia warunkowe.
