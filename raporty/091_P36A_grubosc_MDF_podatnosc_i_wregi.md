# Raport 091 — P36A: podatność paneli, grubość MDF i skuteczność idealnych wręg

**31 października 2026 | 324 wykonane scenariusze i kontrola zbieżności szeregu Fouriera.**

> **Status: matematyczny model analityczny prostokątnych płyt, NIE zwalidowany model całej obudowy ani dokumentacja CNC.** W szczególności nie modeluje osłabienia frontu przez otwór Ø355,8 mm, sztywności rzeczywistych spoin, kontaktu wręg, rezonansów struktury ani promieniowania akustycznego.

![P36A — podatność MDF i hipotetycznych wręg](../wyniki/p36a_podatnosc_MDF_i_wreg.svg)

## Czego szukamy?

Wcześniejsze raporty P33–P35 wykazały, że wyniki globalnego MES zależą od opisu połączeń oraz siatki. Zanim powstanie kwalifikowany pełny model z rzeczywistym CAD, policzyliśmy niezależnym wzorem **podatność objętościową paneli** i jej wrażliwość na grubość MDF, sprężystość oraz hipotetyczne linie wzmocnień. Celem nie jest wybranie z góry grubszego MDF, lecz **ustalenie, które parametry trzeba rzeczywiście zmierzyć**.

## Matematyka i odniesienie jednostek

Dla każdej prostokątnej płyty Kirchhoffa, po prostu podpartej na czterech brzegach (SSSS), pod jednolitym ciśnieniem `p`, użyto dwuwymiarowego szeregu Naviera, maksymalnie 25×25 nieparzystych składników:

```text
D = E*h³ / (12*(1-nu²))
w_mn/p = 16 / [D*pi⁶*m*n*((m/a)² + (n/b)²)²]   (m,n nieparzyste)
Cpanel = ∫w dA / p
       = Σ 64*a*b/[D*pi⁸*m²*n²*((m/a)²+(n/b)²)²]
Cgas = V/(rho_air*c²)
Veq_wall = Cwall*rho_air*c²            [m³]
```

Równoważnik `Veq_wall` **nie jest wolnym litrażem skrzyni**. To liniowa podatność sprężysta przy powolnym/stałym wymuszeniu, wyrażona jako objętość gazu dająca analogiczną podatność. Nie obejmuje bezwładności, strat MDF, rezonansów ani ruchu kosza. Nie należy traktować go jako efektywnej objętości akustycznej we wszystkich częstotliwościach.

Wymiary zewnętrzne 1020×425×500 mm; front 44 mm; pozostałe panele 18/22/25/28 mm. Dla podstawowych 22 mm prostokątne rozpiętości płyt wynoszą około 976×359×456 mm. Front w modelu jest **pełną, nieprzebitą płytą**; w fizycznym projekcie ma duży otwór, a podatność pierścienia może być inna. Dwa idealne podparcia wzdłuż szerokości rozmieszczono w x=426 i 701 mm od lewego brzegu rozpiętości, co wyidealizowuje pełne przeniesienie przemieszczenia w każdej linii.

Przebadano `4 grubości × 3 moduły E(1,5/2,1/3,0GPa) × 3 gęstości(650/730/800kg/m³) × 3 nominalne objętości(100/120/150l) × 3 warianty podpór = 324 przypadki`. Gęstość zmienia modalne f11 i masę, ale nie zmienia statycznej podatności przy zadanym E. Warianty różnych grubości **nie mają automatycznie prawidłowych wymiarów wkładów** ani identycznych geometrii przejścia.

## Wynik bazowy — MDF 22 mm, front 44 mm, E=2,1GPa, rho=730kg/m³, V=120l

| Model podparć | Równoważnik podatności Veq_wall | Cwall/Cgas | Najniższa lokalna f11 płyt w modelu |
|---|---:|---:|---:|
| Brak wręg | **12,26 l** | 10,21% | 103,9 Hz |
| Jedna idealna linia | **6,29 l** | 5,24% | 143,9 Hz |
| Dwie idealne linie | **3,59 l** | 2,99% | 183,0 Hz |

To modelowe częstotliwości własne **pojedynczych idealnie podpartych płyt**, nie mody całego subwoofera. W szczególności rzeczywista spoinowana skrzynia może mieć częstotliwości znacząco niższe przez ruch wręg, stóp i masy kosza.

## Czy MDF 25 lub 28 mm zastąpi wręgi?

| Grubość ścian | Waga modelowych paneli* | Veq bez wręg | Veq z dwiema idealnymi liniami |
|---|---:|---:|---:|
| 18 mm | 36,87 kg | 23,51 l | 6,85 l |
| **22 mm** | **42,13 kg** | **12,26 l** | **3,59 l** |
| 25 mm | 46,07 kg | 8,10 l | 2,37 l |
| 28 mm | 50,02 kg | 5,62 l | 1,65 l |

*Uproszczona masa powierzchni płyt bez fizycznego kosza, wszystkich wręg, wkładów, kleju, maskownicy i złącz. Może nie sumować się z bilansem mas P30E. Front odjęto tu od masy geometrycznie kołem, mimo że model jego podatności pozostaje nieprzebity — wyraźna niespójność idealizacji, dlatego **masy i podatności nie używać jako wspólnego projektu wykonawczego**.*

**Wniosek:** zwiększenie grubości poprawia modelową sztywność, ale modelowe podparcie ma większy potencjalny wpływ. **Nie jest to rekomendacja zmiany 22 mm na 18 mm**, gdyż sztywność i wytrzymałość fizycznych wręg nie są wyznaczone.

## Kontrola zbieżności

Dla 22 mm, E=2,1 GPa, zakres nieparzystych funkcji 7→15→25: Veq bez wręg **12,25444 → 12,25581 → 12,25586 l**, z dwiema idealnymi liniami **3,58502 → 3,58512 → 3,58513 l**. To poprawna zbieżność matematyczna **tego** modelu, nie walidacja rzeczywistej skrzyni.

## Diagnoza dotycząca obciążenia z P35A

Dla 80 Hz przygotowano dodatkowe, **wyłącznie diagnostyczne** ważenie udziału ścian ich średnim `p/p̄` z P35A. Dla 120l i bazowego MDF: Veq bez wręg zmienia się z 12,26 na ~12,92 l, a z dwiema idealnymi liniami z 3,59 na ~3,77 l. **To nie jest pełne rozwiązanie dynamiczne** — średnia nierównomiernego ciśnienia nie jest identyczna z przestrzennym wymuszeniem panelu, a reakcja ściany na gaz zmienia samo pole ciśnienia. Obliczone różnice jedynie wskazują kierunek dalszej analizy.

## Co trzeba zmierzyć i policzyć

Najwyższy priorytet ma rzeczywisty moduł i kierunkowość MDF oraz **sztywność obrotowa i przesuwna połączeń wręga–panel i panel–panel**. Dalej: rzeczywisty front z otworem, masa i mocowanie kosza, 20 wyjmowanych modułów, stopy. Bez pełnego modelu powłokowego i kontroli postaci MAC nie ma podstaw do zastępowania aktualnego projektu przez 18mm MDF.

**Reprodukcja:** `node skrypty/p36a_podatnosc_i_grubosc_MDF.js` → `wyniki/p36a_podatnosc_MDF_324_20261031.json`. Kod bez zależności.
