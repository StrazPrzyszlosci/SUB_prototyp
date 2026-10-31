# Raport 071 — P24F: estymator wieloczęstotliwościowy U/I w pętli ochronnej

**Data:** 2026-10-31. **Status:** wykonano 192 deterministyczne symulacje programowe. Wyniki nie są pomiarem głośnika ani sprawdzonym firmware i **nie uprawniają do ustawienia temperatury granicznej**.

## Pytanie badawcze

P24B wykorzystywał idealny odczyt temperatury (oracle). P24C wykazał wrażliwość estymatora `Re(T)` na zmianę BL i rezystancji przewodów. P24D wykazał wpływ opóźnień i zablokowanego aktuatora. P24E zademonstrował numeryczną identyfikację `ΔRe`, `Δ(BL²)` i `ΔLe` z kilku punktów częstotliwościowych. W P24F łączymy **rzeczywiste w ramach symulacji** estymacje zespolonej impedancji z czasową, dwuwęzłową termiką i dyskretnym wyłączaniem napędu po opóźnieniu.

## Model i metodologia

- Referencyjny model C02 Dayton RSS390HF-4: `Re25=3Ω`, `alpha=0.00393/K`, `BL=15Tm`, `Le=0.92mH`, `Fs=19.5Hz`, `Xmax=14mm peak` w obudowie `80l`. Użyte pozostałe parametry P24B.
- Trzy **hipotetyczne** zestawy `Cc/Rcm/Cm/Rma`: favorable, central, adverse według P24B, bez danych producenta.
- Testy ciągłego sinusa **20 Hz i 80 Hz** (odrębne symulacje), `dt=0.05s`, `150s`, maksymalny napęd modelowego NC500MP z wejściem TRS 4Vrms i mechanicznym ograniczeniem `0.8 Xmax peak` (hipotetyczna idealna obwiednia).
- Obserwator z P24E: na podstawie **syntetycznych** spójnych fazowo odczytów `Z(f)=U/I` przy 80, 150 i 300 Hz dopasowuje LS do `ΔRe + Δ(BL²)/Zm(f) + jωΔLe`; następnie `ΔT = ΔRe/(Re0·alpha)`. Próbkowanie maksymalnie co 0.5s, szum amplitudy 0.5% sigma i fazy 0.2° sigma, zaszumiona **jednokrotna** kalibracja zimna. Powyższe punkty pomiarowe NIE są gwarantowane przez rzeczywisty sygnał muzyczny i nie obliczono emisji akustycznej dodatkowego tonu.
- 8 scenariuszy: pomiary nominalne; BL−3%/Le+10%/Cms+5%; rezystancja przewodów ±0.1 Ω i −0.25 Ω; utrata pomiarów w sekundach 20–45; pomiary tylko co 5s; całkowity brak wiarygodnego pobudzenia.
- Cztery strategie: bez termiki; próg zmierzonego +80K; wcześniejsze wyciszanie na zmierzonym +55K; predykcja `T_est + 15K + (age+0.25s)×5K/s >= 80K`. **15K oraz 5K/s to wyłącznie założenia testowane, a nie udowodnione granice.**
- Wszystkie strategie inne niż „bez termiki” mają fail-closed: po **2s** bez pomiaru zatrzaskują wyciszenie; czas wykonania polecenia wynosi umowne **0.25s**. W modelu komendy wykonały się poprawnie. P24D oddzielnie badał uszkodzenie aktuatora.
- `+80K` to wyłącznie kontur porównawczy, a `+200K` to koniec ważności symulacji (przerwanie liczenia), **żadna z tych wartości nie jest dopuszczalnym wzrostem temperatury rzeczywistego Dayton**.

Kombinacje: `2 f × 3 termiki × 8 scenariuszy odczytu × 4 polityki = 192 trajektorie`, każda maksymalnie 3000 kroków. Niezależnie porównano 3 przypadki przy `dt=0.05/0.025s`; różnica szczytu od 0.017 do 0.052K. Test separacji dwóch niezależnych kanałów potwierdza tylko niezmiennik modelu software (nie niezależność sprzętową).

## Wyniki główne

| Strategia | Liczba przypadków przekraczających modelowe +80 K z 48 | Maks. modelowy przyrost cewki |
|---|---:|---:|
| Bez zabezpieczenia termicznego | 40/48 | +200.128 K — stop dziedziny |
| Ogranicznik przy oszacowanych +80 K | 24/48 | +113.931 K |
| Ogranicznik przy oszacowanych +55 K | **3/48** | +87.028 K |
| Predyktor z błędem 15K i przyrostem 5K/s | **7/48** | +94.160 K |

Wynik pokazuje, że **modelowy predyktor nie zapewnił mniejszej częstości przekroczeń niż prosty, wcześniejszy próg**, ponieważ założone `5K/s` było zbyt małą rezerwą w niektórych okresach nagrzewania. Nawet przy **błędzie pomiarowym mniejszym niż zakładane 15K** wystąpiły przekroczenia przy najbardziej niekorzystnym modelu Cauer w 80 Hz: scenariusz `cable_minus_0p1`: maks. **83.147K**, oraz `dropout_20to45`: maks. **81.851K**.

W scenariuszu dodatkowej, **niezidentyfikowanej** rezystancji −0.25Ω przewidziana koperta 15 K również nie jest dotrzymana. Przy `80Hz/adverse` uzyskano:
- pomiarowy błąd maksymalny **22.8–23.6K** w zależności od strategii;
- `margin_measured_55`: maks. **87.028K**, czas ponad konturem **37.75s**;
- `predicted_bound_15K_5Kps`: maks. **94.160K**, czas ponad konturem **104.65s**.

To nie znaczy, że w prawdziwym układzie jedna strategia jest bezpieczna, a druga nie: ich ranking odnosi się wyłącznie do przyjętych 192 modeli z hipotetycznymi limitami i pełnym dostępem do zestawu częstotliwości (poza jawnie brakującymi pobudzeniami). Przedwczesne ustawienie progów byłoby metodologicznym błędem.

## Wnioski techniczne

1. **Nie wystarcza łączenie P24E z P24D metodą `T_est>threshold`.** Trzeba uwzględnić przerwy pomiarowe, stały błąd kalibracji, błąd strukturalny `Zm`, czas działania i możliwość, że przyjęta górna granica tempa grzania jest fałszywa.
2. Utrata pobudzenia pomiarowego nie może być interpretowana jako spadek temperatury. W symulacji watchdog odcina napęd (fail-closed) — rzeczywisty przekaźnik/EN/MUTE musi zostać osobno potwierdzony jako **skuteczny także przy awarii kontrolera**.
3. Niezależnie od termiki konieczny jest osobny tor ochrony mechanicznej i elektrycznej. Przyjęty tutaj idealny `Xpk <= 0.8Xmax` nie jest implementacją prawdziwego limitera.
4. 80/150/300Hz może być poza użytecznym widmem sygnału subwoofera; diagnoza z celową iniekcją wymaga rozliczenia szumu, emisji, ADC, intermodulacji, obciążenia i kosztu.
5. Wprowadzanie U/I przy mostkowych wyjściach klasy D wymaga właściwej izolacji, kalibracji i projektu uwzględniającego napięcia wspólne; brak projektu PCB i badań bezpieczeństwa zasilania sieciowego.

## Kolejna bramka: P24G

Zamiast kolejnego arbitralnego marginesu zalecane są: (a) formalna obwiednia niepewności identyfikacji i temperatury z uwzględnieniem ograniczenia pobudzenia, (b) sprawdzenie szybkości przyrostu termicznego na obszarze niepewnych parametrów, (c) separacja oraz hardware fail-safe i testy *black-box* DSP/wzmacniacza, (d) próby na rzeczywistym przetworniku z referencyjnym odczytem `Re(T)` i kalibracją przewodów. Bez tego **zakaz kwalifikacji jako ochrony dopuszczającej pełną moc**.

## Odtwarzanie

`python3 -m pip install numpy`

`python3 skrypty/p24f_obserwator_i_ochrona.py`

Pliki: `wyniki/p24f_192_trajektorii_20261031.json` (dane pełne), `wyniki/p24f_192_przypadkow.csv` i `wyniki/p24f_podsumowanie_20261031.json`. Kod jest deterministyczny; żaden przypadek nie korzysta z pomiarów rzeczywistych urządzeń.