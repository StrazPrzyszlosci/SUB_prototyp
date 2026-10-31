# Raport 077 — P30D: stateczność wysokiej obudowy z przetwornikiem przesuniętym na froncie

**31.10.2026; 324 obliczenia scenariuszowe. Model quasi-statyczny bryły sztywnej, NIE test bezpieczeństwa, NIE certyfikacja zapobiegania przewróceniu.**

## Dlaczego potrzebne

P30A–C (raport 076) zaproponował do dalszego CAD/MES korpus 1040×430×500 mm (W×D×H); ustawiony pionowo ma około **1040 mm wysokości**, a powierzchnia podstawy około **430×500 mm**. Przetwornik jest przesunięty w jedną stronę frontu. Dotychczasowe sprawdzenia układu wkładów i grawitacji P18E nie obejmowały pełnego środka ciężkości z ciężkim koszem oraz podatności na wywrócenie.

## Model masowy i równania

Sześć rozłącznych brył płyt MDF: front 44 mm z **odjętym otworem kołowym Ø355,8 mm i korektą środka ciężkości**, pozostałe 22 mm, gęstość MDF 650/800 kg/m³. Zintegrowano 11 wręg AABB P20D. Dla wkładów przyjęto puste w środku, zamknięte ściankami MDF **8 mm**, a nie masę pełnych brył. Przeliczono trzy nominalne układy: ~150 l (2 duże), ~120 l (11 dużych i 1 mały), ~100 l (16 dużych i 3 małe). Masa tylnej maty z hipotetyczną gęstością 20 kg/m³. Kosz/głośnik reprezentowany jest masą punktową **10, 15 lub 20 kg** w dwóch wymiarach na osi zewnętrznego frontu x=231, z=250 mm, przy y=90/130/170 mm od przedniej krawędzi. **Nie są to zweryfikowane masy ani centra masy produktu.**

Statyka bryły po obróceniu do pionu: `hCOM = xCOM` z przetwornikiem nisko (odwrócenie daje `hCOM = W−xCOM`). Najmniejszy poziomy dystans rzutu środka masy do krawędzi podstawy `dmin`. Dla idealnie sztywnej bryły na sztywnym, nieruchomym podłożu:

`theta = arctan(dmin / hCOM)` oraz `F_top = M g dmin / W` dla poziomej siły przyłożonej na samej górze urządzenia. Wzory **nie obejmują** pchnięcia impulsowego, ślizgania, przechyłu, spoin, miękkich nóżek, dywanu, kabli i ludzi/zwierząt. Uwaga: `F_top` jest równowagą idealną przed zmianą geometrii kontaktu, nie bezpiecznym limitem siły użytkownika.

Siatka: `3 korpusy × 3 objętości × 2 gęstości × 3 masy kosza × 3 głębokości środka masy × 2 ustawienia przetwornika = 324 scenariusze`.

## Wyniki statyczne — zakres scenariuszy

| Korpus W×D [mm] | Przetwornik | Najmniejszy kąt sztywnej bryły | Największy kąt w siatce | Minimalna modelowa siła przy górze |
|---|---|---:|---:|---:|
| 1000×440 | nisko | 20,68° | 24,64° | 84,9 N |
| 1000×440 | wysoko | 16,32° | 22,59° | 84,9 N |
| **1040×430** | **nisko** | **19,68°** | **23,50°** | **81,1 N** |
| 1040×430 | wysoko | 15,39° | 21,32° | 81,1 N |
| 1050×425 | nisko | 19,34° | 23,14° | 79,5 N |
| 1050×425 | wysoko | 15,08° | 20,93° | 79,5 N |

Minimalne wartości pochodzą z **różnych punktów** siatki i nie muszą występować razem. Przedział nie jest oszacowaniem prawdopodobieństwa.

Przykładowy punkt 1040×430, układ nominalnych ~120 l, MDF 800 kg/m³, głośnik 15 kg z punktem masy y=130mm:
- masa całego modelu **68,80 kg**, z częściami konstrukcyjnymi i wkładami, ale bez stopek/uchwytów;
- przy głośniku nisko: wysokość środka masy **504,48 mm**, statyczny próg modelu **20,61°**;
- przy głośniku wysoko: wysokość środka masy **535,52 mm**, próg modelu **19,51°**;
- odległość środka masy od przedniej krawędzi **189,69 mm**; dla tego idealnego punktu nacisk przyłożony na szczycie około **123,1 N** odpowiada równowadze granicznej. To NIE jest dopuszczalna siła ani norma bezpieczeństwa.

## Weryfikacja

Kontrola 162 par przy tej samej geometrii i masie potwierdziła: zmiana góra/dół nie może zmienić masy ani poziomego położenia COM, a sumy dwóch wysokości są równe całkowitej wysokości W z tolerancją 0,001 mm. Wszystkie statyczne środki ciężkości znalazły się wewnątrz podstawy. Nie wykonano niezależnego MES odkształcalnej konstrukcji; nie należy rozszerzać kontroli algebraicznej na rzeczywiste przewracanie.

## Decyzja konstrukcyjna

**Przy ustawieniu pionowym preferować głośnik nisko** i zaprojektować mocowanie stopek/ewentualną blokadę przewrócenia z uwzględnieniem rzeczywistej masy, środka masy, posadzki, obciążeń bocznych i przejścia przewodów. Inna pozycja akustyczna dwóch subwooferów może być potrzebna z powodu pokoju; nie należy rozstrzygać tego bez pomiaru. Po wykonaniu próbnej makiety i po doborze elementów trzeba ocenić stateczność obu orientacji, siły w mocowaniach i powtarzalność montażu.

**Nie zaleca się używania modelowych wartości kąta albo siły jako specyfikacji bezpieczeństwa**. Wartości służą wykryciu ryzyka i nadaniu mu priorytetu w prototypie.

## Reprodukcja

`python3 skrypty/p30d_stabilnosc_pionowa.py` (NumPy; importuje model P30A z poprzedniego raportu).

Wyniki: `wyniki/p30d_stabilnosc_pionowa_20261031.json`.
