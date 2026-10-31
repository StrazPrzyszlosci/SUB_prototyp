# Raport 069 — P24D: opóźnienia, błędy estymacji i awarie zabezpieczeń dwóch subwooferów

**Data:** 2026-10-31. **Baza:** P24B (raport 067) oraz P24C (raport 068, PR #15 scalony). **Status:** wykonano 88 deterministycznych trajektorii numerycznych i 4 porównania kroku. To NIE jest kwalifikacja bezpieczeństwa, pomiar urządzenia ani gotowa konfiguracja miniDSP.

## Zakres i pytanie badawcze

Czy samo dostarczenie oszacowanej temperatury do ogranicznika wystarcza, gdy pomiar następuje co pewien czas, aktuator ma opóźnienie, a pomiar, transmisja lub tor wyciszania może ulec awarii? Badamy odrębne kanały A (80 Hz, obciążenie głównie cieplne) i B (20 Hz, ograniczenie mechaniczne). Oba są modelowane niezależnie; nie wykazano rzeczywistej izolacji kanałów ani sprzężenia przez wspólny zasilacz.

**Model testowy:** Dayton RSS390HF-4 / C02, zamknięte 80 l, parametry P24B, centralna *hipotetyczna* sieć Cauer Cc=40 J/K, Rcm=0,6 K/W, Cm=1000 J/K, Rma=1,5 K/W, Re(T) z alpha=0,00393/K. Napęd testowy NC500MP/4 Vrms, nominalna obwiednia napięcia/mocy i prądu jak w P24B. Dla pojedynczego sinusa zastosowano **idealną modelową osłonę Xpeak≤0,8 Xmax=11,2 mm**, osobno od ochrony cieplnej; nie należy przenosić tego progu do sprzętu.

Dwa kontury **wyłącznie diagnostyczne**: +80 K (obserwacja przekroczeń) i +200 K (stop domeny modelu). **Żaden nie jest producentową temperaturą graniczną.**

Symulowana obserwacja temperatury to **prawdziwy stan cewki plus zadany błąd ujemny**, a NIE rzeczywisty estymator U/I. To uproszczenie testuje skutki błędu P24C, nie dowodzi możliwości uzyskania odczytu co sekundę z muzyki. Kontroler jest modelowany jako żądanie odcięcia sygnału po opóźnieniu 0–5 s; nie zakładamy dostępu do nieudokumentowanego API miniDSP.

## Wyniki rzeczywiście obliczone

Każdy przebieg trwa do 180 s (lub do numerycznego stopu +200 K), dt=0,05 s; temperatura startowa Tcewka=Tm=Totoczenia. Regulator dwustanowy próbuje po przekroczeniu **umownego** progu załączyć mute, a odblokowuje się z 5 K histerezy. Watchdog bez nowych odczytów przechodzi do zablokowanego mute, wymagającego zewnętrznego resetu (niebadany).

| Wariant; f [Hz] | Szczyt dTcewki [K] | Czas powyżej umownego +80 K [s] | Komentarz |
|---|---:|---:|---|
| Brak ochrony T; 80 | 200,008* | 55,55* | Stop modelu po 64 s; brak prawa ekstrapolacji |
| „Naiwny”: próg 80 K, błąd -20 K, 2 s zwłoki; 80 | 116,533 | 171,55 | Spóźniona ochrona nie utrzymuje konturu |
| „Guarded”: próg 45 K, błąd -20 K, zwłoka 0,25 s; 80 | 75,095 | 0 | Kontur zachowany tylko w tych *założeniach* |
| Jak wyżej, ale zwłoka 5 s; 80 | 105,630 | 69,70 | Sama znaczna rezerwa progu nie wystarcza |
| Jak guarded, ale błąd -60 K; 80 | 111,960 | 171,55 | Przekroczenie przy niezidentyfikowanym błędzie modelu |
| Jak guarded, ale wyciszenie sprzętowo nie działa; 80 | 200,008* | 55,55* | Programowy rozkaz odcięcia jest nieskuteczny |
| Brak ochrony T; 20 | 125,727 | 130,45 | Ograniczenie Xpeak do 11,2 mm nie chroni termicznie |
| Guarded; 20 | 66,930 | 0 | Wynik warunkowy, przy idealnym modelowym Xpeak |
| Czujnik A=80 Hz odłączony od t=20 s, watchdog; 80 | 73,766 | 0 | Fałszywy czujnik nie jest interpretowany jako 0 K |
| Brak watchdoga, odłączenie czujnika t=20 s; 20 | 125,727 | 130,45 | Fail-open prowadzi do dalszego grzania |

* Wynik ucięty przy hipotetycznym +200 K; czas powyżej konturu nie obejmuje dalszej części 180 s.

### Siatka opóźnienia i obciążenia błędem

Dodatkowe **72 przypadki**: 2 częstotliwości × 6 ujemnych błędów temperatury (0, −10, −20, −30, −40, −60 K) × 6 opóźnień aktuatora (0,1; 0,25; 0,5; 1; 2; 5 s), wspólny testowy próg 45 K i odczyt co 1 s. **36/72** narusza umowny kontur +80 K; nie jest to prawdopodobieństwo awarii ani statystyka rzeczywistej muzyki.

Macierz: **X = wystąpiło przekroczenie konturu**, „.” = bez przekroczenia w modelu. Kolumny: zwłoka 0,1 / 0,25 / 0,5 / 1 / 2 / 5 s.

| Błąd obserwacji [K] | 20 Hz | 80 Hz |
|---:|:---:|:---:|
| 0 | ...... | .....X |
| −10 | ...... | .....X |
| −20 | ...... | ...XXX |
| −30 | .....X | XXXXXX |
| −40 | XXXXXX | XXXXXX |
| −60 | XXXXXX | XXXXXX |

Kontrola kroku dt=0,05 vs dt=0,025 s dla wariantów „guarded” i „naive_late” przy 20/80 Hz: zmiana szczytu dT odpowiednio 0,003; 0,001; 0,020; 0,024 K. To **kontrola numeryczna**, nie identyfikacja rzeczywistej termiki.

## Ocena zabezpieczeń i zakres wdrażalności

Producent miniDSP dokumentuje dla **Flex Eight** i **Flex HTx** m.in. kompresor wyjściowy z progiem, ratio, attack/release oraz regulację gain/mute na kanał. Wskaźnik RMS dotyczy *sygnału wyjścia DSP*, a nie fizycznego prądu w przewodach głośnika. Nie ma tu potwierdzenia obsługi użytkowego obserwatora Re(T), czujnika U/I ani deterministycznego interfejsu zamkniętej pętli.

Źródła producenta:
- Flex Eight compressor: https://docs.minidsp.com/product-manuals/flex-eight/dsp-reference/compressor.html
- Flex HTx compressor: https://docs.minidsp.com/product-manuals/flex-htx/dsp-reference/compressor.html
- Flex HTx output channels: https://docs.minidsp.com/product-manuals/flex-htx/signal-flow/output-channels.html
- Flex Eight output channels: https://docs.minidsp.com/product-manuals/flex-eight/signal-flow/output-channels.html

**Wykonalne w udokumentowanym DSP:** filtr HPF/LPF, PEQ, niezależna kompresja poziomu sygnału i ręczne mute/gain. **Niewykazane:** zamknięta pętla X/T sterowana z zewnętrznego U/I z gwarantowaną zwłoką i zachowaniem przy błędach. Modelowe gate oznacza **hipotetyczny zewnętrzny aktuator**, a nie zatwierdzone użycie komendy miniDSP.

**Wniosek architektoniczny:** rozważyć zewnętrzny monitor U/I dla każdego kanału, oddzielny nadzorowany tor ograniczenia/mute i niezależne sprzętowe wyłączenie wymagające potwierdzenia działania. Jeżeli sterownik, czujnik lub łączność zawiedzie, stan bezpieczny musi być zdefiniowany na poziomie realnego toru mocy; sam mute w aplikacji nie wystarcza. Dla końcówki ze wspólnym SMPS zbadać współzależności termiczne/zasilania obu kanałów. NIE wykonywać amatorskich modyfikacji części sieciowej 230 V.

## Ograniczenia i dalsze bramki

1. Nie ma pomiarowej temperatury dopuszczalnej C02 ani kalibracji Rth/Cth i BL(x,T), Le(f,I), rzeczywistej kompresji i prądu. **45 K i 80 K nie są zalecanymi nastawami**.
2. Test wymaga rzeczywistego, spójnego czasowo próbkowania zaciskowego U/I, odrzucania niskiego SNR, monitorowania opóźnień i walidacji modelu z niepewnością; pomiar pod obciążeniem klasy D wymaga odpowiednio izolowanego instrumentarium.
3. Ochrona mechaniczna w tym skrypcie jest *idealnym sinusem modelowym*, nie limiterem transientów/wielotonów. Dodać rzeczywiste ślady audio i test dwutonowy P25E.
4. Zrealizować test ze sztucznym obciążeniem, celowym zanikiem czujnika i odłączeniem aktuatora. Sprawdzić fail-closed, restart, preset, volume, reakcję końcówki i rzeczywisty czas od zdarzenia do spadku napięcia głośnikowego.
5. Parametry 2 niezależnych kanałów są podstawione osobno. Test równości przebiegu B przy awarii A jest tylko **kontrolą izolacji w modelu**, a nie dowodem braku wspólnych przyczyn awarii.
6. Wyniki po +200 K są ucinane; nie utożsamiać tego z temperaturą zniszczenia. Bilans energii i pełna walidacja wymagają dodatkowego audytu poza powtórzeniem P24B.

## Odtwarzalność

Kod (biblioteka standardowa Pythona, bez NumPy): skrypty/p24d_opoznienia_ochrony_dwoch_kanalow.py. Uruchomić z katalogu repozytorium:

    python3 skrypty/p24d_opoznienia_ochrony_dwoch_kanalow.py

Skrypt generuje wyniki/p24d_opoznienia_faulty_20261031.json (88 trajektorii, 4 audyty kroku, macierz przypadków). W repo zapisano też wyniki/p24d_podsumowanie_20261031.json z liczbami kontrolnymi. Żaden wynik nie jest pomiarem wzmacniacza ani procesora.
