# P31C — koncepcja konstrukcyjna i bramki przed wykonaniem pierwszego prototypu

**31 października 2026. Stan: R&D, NIE projekt CAD/CNC.** Celem jest **badawczy prototyp subwoofera zamkniętego**, nie ostateczny produkt z potwierdzonymi zabezpieczeniami.

![Schemat koncepcyjny](P31C_schemat_konstrukcji_1020_425.svg)

## Wstępna geometria bazowa P30E

| Własność | Wariant / źródło |
|---|---|
| Głośnik | Dayton RSS390HF-4, C02, 15″/4Ω; tylko warunkowy faworyt |
| Korpus W×D×H | **1020 × 425 × 500 mm** (skrzynia może stać obrócona, wymaga odrębnej kwalifikacji stateczności) |
| Panele | MDF 22 mm; laminowany front **44 mm** |
| Wnętrze prostopadłościanu | **976 × 359 × 456 mm** (przed odjęciem przetwornika, wręg i wkładów) |
| Otwór w froncie | Ø355,8 mm, zewnętrzny kosz Ø388,4 mm; śruby i pogłębienie do wykonania z realnego szablonu |
| Oś przetwornika | x=231 mm od lewego boku, wysokość 250 mm w orientacji poziomej |
| Wręgi | Dwie pierścieniowe w odległości x≈448 i723 mm od lewej krawędzi zewnętrznej, lokalna rama U (P30E) |
| Mata | Warstwa tylna 50 mm, porowata, wymagane realne mocowanie i wycięcia przy wręgach |
| Regulacja netto (nominalnie) | **100,12 l (16 dużych+4 małe) / 119,92 l (12 dużych) / 150,16 l (1 duży)** |
| Budżet głębokości | Korpus 425mm, całkowity obrys w modelu do 481mm, **19mm zapasu do 500mm** |
| Masa MDF modelowa przy stanie 120l | ~47,2kg bez głośnika, osłony i okuć |
| Montaż przez otwór | 20/20 w modelu przesunięć osiowych przy obwiedni 6mm; 8mm powoduje 12 kolizji statycznych |
| Stateczność | P30F: 324 scenariusze; położenie głośnika i stóp silnie wpływa na przewrócenie |

Głębokość 19mm rezerwy wynika z **niezweryfikowanych** zakresów wystawania, prześwitu i odkształcenia osłony. Wymiary nominalne nie uwzględniają wszystkich zamków, śrub i przewodów. Net volume zależy od efektywnej wyporności głośnika 2–8l. P30E daje przy 120l zakres stresowy 114,25–125,57l — to nie jest tolerancja produkcyjna.

## Co nowe badanie P31B naprawdę rozstrzygnęło

[P31B, raport 081](../raporty/081_P31B_podatnosc_wreg_obudowy_1020_425.md) — 135 scenariuszy pojedynczego panelu Rayleigh–Ritza z dwiema **sprężystymi** liniami. Przy E 2,1GPa i rho 730kg/m³ modelowa pierwsza częstotliwość zmienia się od 115,3Hz (bez podparć) przez 134,0Hz (k=1e6N/m²) do 194,5Hz (k=1e7N/m²). Ta wrażliwość podważa stwierdzenie „panele o małych polach więc sztywne”. Sprężyny do idealnego podłoża nie odwzorowują realnego układu 3D. Nie jest to pełny MES.

## Wymagane następne testy — kolejność i bramki

| Etap | Dowód / test do wykonania | Warunek wejścia do kolejnego etapu |
|---|---|---|
| **G1: zamrożona geometria CAD** | 3D: front z otworem i kołnierzem, kosz, wszystkie wręgi, wkłady, uszczelki, zamki, śruby, terminal, przewody, grill, stopy; pełen obrys w skrajnych tolerancjach | Brak kolizji *w rzeczywistych bryłach*; obrys ≤500mm ze znanym dodatnim zapasem |
| **G2: pełny mechaniczny FEM** | Postacie i przemieszczenia paneli/laminowanego frontu, wręg, złączy, uszczelek i śrub; grawitacja pion/poziom i ciśnienie 20–120Hz | Raport zbieżności 3 siatek, parametry MDF/glue potwierdzone pomiarem lub jawnym badaniem granic; brak kontaktu z membraną |
| **G3: sprzężenie mechanika–akustyka** | Nowa geometria P30E w FV/FEM, 100/120/150l, mata z danymi oporu przepływu, panelowe promieniowanie i faza | Przebiegi zbieżne częstotliwościowo i niezależna kontrola bilansu mocy; kontrola dodatkowej emisji obudowy |
| **G4: projekt trzymania wkładów** | Wytrzymałość i zmęczenie mocowań, montaż przez otwór z narzędziem, bezpieczeństwo transportu i obrotu | Każdy z 20 modułów ma dodatnie mocowanie, policzoną masę/siłę, brak luzu, dostępny demontaż |
| **G5: mechanika zewnętrzna i bezpieczeństwo** | Mocowanie głośnika, stopy/antytip, osłona, przewody, termika końcówki PCB i ochrona 230V | Dokumentacja mechaniczna, niezależna ocena zasilania sieciowego i scenariuszy awarii |
| **G6: próby po zbudowaniu jednej sztuki** | Re(zimne), impedance sweep z trzema litrażami, near-field, accelerometry paneli, THD/IMD przy tym samym SPL, szczelność i powtarzalność, termika oraz weryfikacja MUTE/EN | Rzeczywiste wartości mieszczą się w uzasadnionym obszarze modeli; ewentualna rekonstrukcja i zmiana drivera |

**Uwaga metodologiczna:** pełny MES i próbki zbieżności nie gwarantują poprawności fizycznej bez kalibracji MDF, spoin i warunków brzegowych. Testy akustyczne i cieplne muszą użyć rzeczywistego głośnika. Nie zatwierdza się progów temperatury z wcześniejszych modeli.

## Ochrona i jakość — alternatywa STX
Patrz [raport 080](../raporty/080_P31A_porownanie_kosztowe_STX_Dayton_33.md). Modelowy spadek potencjału 20Hz w tanim STX nie jest rankingiem THD. Rozstrzygający jest eksperyment przy tym samym SPL np. 85/90/95dB w 2π/1m, w kilku częstotliwościach, zanim zacznie się kupować dwie sztuki droższego głośnika. Bez uzgodnienia docelowego SPL i poziomu zniekształceń wybór ekonomiczny jest warunkowy.

## Decyzja
**Kierunek: zachować P30E jako platformę badawczą; NIE zamawiać jeszcze wycinania z samych schematów.** Pierwszy zakup powinien być podporządkowany planowi pomiarów, nie markowemu rankingowi. 
