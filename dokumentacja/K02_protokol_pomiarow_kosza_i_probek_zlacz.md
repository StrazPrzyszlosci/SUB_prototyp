# K02 — karta kontroli prawdziwego kosza i próbek lokalnego mocowania

**3 listopada 2026 · karta badań do wykonania fizycznie, NIE dokument przeprowadzonych pomiarów, NIE CNC.**

## Cel: podjąć decyzję pomiędzy klockiem 20 mm, 30 mm a ramą

W modelu K02 osiem klocków 20 mm pozwoliło na pełny montaż 20/20 modułów regulacji, a dla klocków 30 mm dotychczasowa kolejność osiągała tylko 16/20 w stanie 100 l. **Rozstrzygnięcie geometrii transportowej nie rozstrzyga nośności.** Rzeczywiste wyniki poniższych pomiarów są jeszcze PUSTE i nie wolno ich zastępować symulacjami.

## 1. Pomiary kosza RSS390HF-4

Karta producenta: https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf

Wymiary fabryczne: kołnierz Ø388,4; wycięcie Ø355,8; okrąg śrub Ø368; 8 otworów Ø6,5; grubość kołnierza 10,5; głębokość 178 mm. Cztery żebra na rzucie producenta nie wystarczają do wyznaczenia ich brył przy tylnej powierzchni MDF.

| Id osi śruby | Położenie kątowe w szkicu względem otworu 0 | Rzeczywisty obrys kosza/żebra w miejscu Y=44–64 | Dodatkowe części/terminale | Dostęp śruby i narzędzia | Status |
|---:|---:|---|---|---|---|
| 0 | 0° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |
| 1 | 45° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |
| 2 | 90° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |
| 3 | 135° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |
| 4 | 180° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |
| 5 | 225° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |
| 6 | 270° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |
| 7 | 315° | NIE ZMIERZONO | NIE ZMIERZONO | NIE ZMIERZONO | OTWARTE |

**Pomiary krytyczne:** rzeczywisty promień obrysu w funkcji kąta θ i głębokości Y; prześwity na Y=44,54,64,74 mm; terminale i przewody; wentylacja zespołu magnetycznego; szczelina pod uszczelką; pełne gabaryty osłony i złącza z tyłu skrzyni. Dane z fotografii forów są inspiracją autorów zewnętrznych, nie pomiarem Fundacji.

## 2. Dwie próbki klocka i niezależna alternatywa

Przed wykonaniem skrzyni odtworzyć **tę samą lokalizację osi mocowania i materiał MDF** na odcinku próbki frontu, a następnie wykonać porównawczo:

| Wariant | Wymiary bryły z modelu K01/K02 | Co należy sprawdzić |
|---|---|---|
| Lokalny klocek C20 | długość promieniowa 26,1 mm, szerokość 36 mm, głębokość **20 mm** | Dostęp modułów; wkładka/gwint, wyrywanie, odrywanie spoiny, obrót wkładki, relaksacja docisku, szczelność |
| Lokalny klocek C30 | te same wymiary podstawy, głębokość **30 mm** | Nośność porównawcza; sprawdzić alternatywną kolejność 20 modułów lub inne położenie klocków |
| Konstrukcja ramowa R | rzeczywisty komplet mocowań: kołnierz→rama→wręgi/MDF | Nośność wszystkich złączy, masa, miejsce na wkłady i narzędzia; nie przyjmować idealnie sztywnej ramy |

**To NIE jest lista cięcia lub zamówienia.** Realne wymiary próbek mogą wymagać zmiany po obejrzeniu kosza i wybraniu wkładki.

### Parametr krytyczny, którego skrócenie do 20 mm nie naprawia

Osie śrub mają promień **184 mm**. Modelowy klocek zaczyna się na promieniu **178,9 mm**. Jeśli zewnętrzna średnica hipotetycznej wkładki wynosi 6/8/10 mm, pozostający **radialny pas drewna do wewnętrznej krawędzi** wynosi odpowiednio **2,1 / 1,1 / 0,1 mm**. To tylko geometria — nie zakładamy ani 2 mm jako normatywnego minimum, ani że istnieje właściwa wkładka o Ø6 mm dla rozważanego gwintu.

**Nie wyznaczać momentu dokręcania bez materiału i dokumentacji łącznika.** Kołnierzowe Ø6,5 mm nie determinuje średnicy otworu montażowego w MDF.

## 3. Protokół prób: co uzasadnia wybór?

Dla konkretnej partii MDF, kleju, wkładek i systemu śrub:
- co najmniej **3 próbki pilotażowe** na wariant i warunek do oceny rozrzutu; nie jest to liczebność do normowej certyfikacji;
- zmierzyć siłę–przemieszczenie przy wyrywaniu i odrywaniu spoiny, siłę poprzeczną przy ścinaniu, obrót wkładki i powtarzalność gwintu;
- zmierzyć lub kontrolować **rzeczywistą siłę wstępnego docisku**, nie wyprowadzać jej wyłącznie z nominalnego momentu śruby;
- sprawdzić ponowny montaż (minimum kilka pełnych cykli), relaksację w czasie, wpływ wilgotności i uszkodzenia MDF;
- wykonać suchy montaż i demontaż próbek w obecności reprezentatywnego kosza lub pełnego wymiarowo szablonu, bez zasłaniania odpowietrzeń i zacisków;
- odtworzyć **20 rzeczywistych wkładów z zamkami i uchwytami**, prowadzić je przez otwór, w obu docelowych orientacjach skrzyni.

Po otrzymaniu pomiarów porównujemy C20/C30/R na tej samej ścieżce sił, uwzględniając dostęp do naprawy i utratę jednego mocowania. Dopiero na podstawie rzeczywistej nośności i zmienności ustalić margines oraz finalny system łączników.

## 4. Bramka techniczna przed frezowaniem

- G1: prawdziwa geometria 3D kosza, zacisków, osłony i przewodów oraz dodatni prześwit wokół ośmiu punktów.
- G2: działający montaż **20/20 fizycznych** modułów z zamkami i narzędziami po osadzeniu mocowań.
- G3: próbki MDF, spoiny, wkładki i śruby z udokumentowanym rozkładem siły–przemieszczenia i awariami.
- G4: potwierdzony bilans netto 100/120/150 l i pełny obrys urządzenia **≤500 mm**.
- G5: porównanie lokalnego systemu C20/C30 do kompletnej ramy, jeśli mocowanie lokalne nie spełnia sprawdzonych wymagań.
- G6: kontrola szczelności, drgań, elektroniki DSP, napędu klasy D i ochrony przy prototypie.

**Stan 3 listopada 2026: G1–G6 OTWARTE. Żadne złącze nie zostało dopuszczone do CNC; brak fizycznego prototypu i wyników wytrzymałościowych.**
