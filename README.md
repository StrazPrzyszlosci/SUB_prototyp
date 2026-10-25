# SUB_prototyp

Badania naukowe i rozwój prototypu subwoofera zamkniętego.

**Aktualizacja 2026-10-24:** pula obejmuje 24 modele od 11 producentów,
w tym 4 STX. Wykonano 12 576 scenariuszy objętości/napędu, analizę N7,
288 przypadków granic po dodatnich Vb oraz badanie identyfikowalności.
To nadal badania przed prototypem, bez zatwierdzonego rankingu THD.
Zacznij od [raportu 010](raporty/010_szeroka_pula_i_kwalifikacja.md),
[011](raporty/011_granice_globalne_litrazu.md) i
[012](raporty/012_identyfikowalnosc_i_dane_publikowane.md).
Pokój około **4,6 × 3,7 × 2,5 m** jest jawnym wejściem:
[raport 013 — pole zespolone, dwa źródła i ograniczenia gabarytów](raporty/013_pokoj_i_realne_gabaryty.md).
P06 obejmuje globalną czułość i niepewność 24 modeli:
[raport 015 — obwiednie i odporność kolejności](raporty/015_niepewnosc_globalna_i_odpornosc.md).
P09/P10: [raport 016 — gaz, wypełnienie i granice szczelności](raporty/016_gaz_wypelnienie_i_granice.md).
P11: [raport 017 — promieniowanie, konwencje masy i sprzężenie pokoju](raporty/017_promieniowanie_i_sprzezenie_pokoju.md).
Obejmuje wzorcowe geometrie oraz 4 154 112 realizacji częstotliwościowych
reakcji modalnego pokoju; nie jest wynikiem fizycznego prototypu.
Rzut od użytkownika: [raport 018 — orientacja kanapa–RTV i odległość odsłuchu](raporty/018_rzut_pokoju_i_odleglosc_odsluchu.md).
**Aktualizacja U-020:** docelowo RTV po lewej i kanapa po prawej obrazu;
[raport019](raporty/019_zamiana_kanapy_i_RTV.md) zastępuje wcześniejszą orientację.
P12/P13: [raport020 — nieliniowy napęd i sprzężony gaz](raporty/020_nieliniowy_naped_i_sprzezony_gaz.md),
12 096przypadków warunkowych i72przypadki kompensacji; nie jest rankingiem
THD produktów. Identyfikacja rzeczywistych krzywych pozostaje częściowa.
P12C: [raport021 — pamięć cewki, L_gen i siła](raporty/021_pamiec_cewki_i_definicja_Lgen.md).
Wykonano18 676wierszy liniowych,1728pełnychODE i odrębne sprawdzenie
źródłowej definicji/siły. Najbliższy krok: P14/IMD i wielotony zmodelemFLUX.
Ocena stanu badań: [raport022 — postęp i pozostały zakres](raporty/022_stan_badan_i_zakres_pozostaly.md).
Rozpoczęte P14A: [raport023 — wspólne limity i pilot dwutonowy](raporty/023_P14A_dwa_tony_i_wspolne_limity.md).
Pilot nie zamyka P14/P25; dalsze kroki obejmują szersze sygnały i emisję harmonicznych.

**Bieżący zakres: wyłącznie naukowe zagadnienia prototypu (U-010).**
Najnowsze zlecenie: [program30badań](PROGRAM_30_BADAN.md), szeroka pula
producentów w tymSTX, obliczeniowy dobór kleju i końcowa rekomendacja
jednego głośnika oraz jednej konstrukcji. KońcowyPDF po ukończeniu prac
możliwych bez urządzenia. Wykonany N7: [raport009](raporty/009_N7_straty_nieszczelnosci.md).
Zacznij od [planu naukowego](PLAN_BADAN_NAUKOWYCH.md) i
[raportu fizyki/DSP](raporty/007_fizyka_nieliniowosci_i_DSP.md).
Opisy wycen i doboru handlowego w starszym planie dotyczą odłożonych etapów.

Projekt B+R na podstawie [briefu v0.6](brief_system_audio_DIY_v0.6.md).
Stan 2026-10-23: utworzono plan, obszerną bazę wiedzy i pierwsze obliczenia.
Obecny zakres to **badania do budowy prototypu**. Referencje: zatwierdzone
ADAM Sub12 i Sub15. Dobór toru pomiarowego po budowie; później pomiary tylko
w pokoju. Narzędzia CAD odłożone.

## Od czego zacząć

| Dokument | Zawartość |
|---|---|
| [PLAN_B_R.md](PLAN_B_R.md) | Pakiety R0–R5, zależności, rezultaty i warunki zakończenia przed budową |
| [AGENTS.md](AGENTS.md) | Instrukcje kolejnych sesji, postępy i najbliższy krok |
| [WYMAGANIA.md](WYMAGANIA.md) | Wymagania, stan dowodów i otwarte progi |
| [DECYZJE_I_PYTANIA.md](DECYZJE_I_PYTANIA.md) | Aktualne ustalenia użytkownika, nadrzędne wobec pierwotnych założeń |
| [WYKONAWCA_CNC.md](WYKONAWCA_CNC.md) | Ograniczenia wskazanego wykonawcyMDF i checklista dokumentacji |
| [Baza wiedzy](baza_wiedzy/README.md) | Fizyka → model → pokój → mechanika →DSP → późniejsza walidacja |

## Wynik pierwszej iteracji

Policzono RSS315HF-4, RSS390HF-4, RSS315HFA-8 i SB34SWPL76-4 w 30/45/60/80/100/120 l
netto: 24 konfiguracje i 144 wiersze pasmowe. Granice modelu zależą od hipotetycznego
napędu i katalogowych danych; nie są zmierzonym maksymalnym użytecznym SPL.
Brak modelu THD, kompresji cieplnej i zidentyfikowanej odpowiedzi pokoju.

- [Raport obliczeń i wnioski](raporty/002_obliczenia_wstepne.md).
- [Wykresy odpowiedzi i granic modelu](wyniki/01_objetosc_i_granice_modelu.png).
- [Porównanie objętościCSV](wyniki/porownanie_obudow.csv), [pasma i limityCSV](wyniki/pasma_i_limity.csv).
- [Źródła z datami](baza_wiedzy/ZRODLA.md), [dane wejściowe](dane/przetworniki/kandydaci.json), [manifestSHA-256](wyniki/manifest.json).

## Raporty

1. [001 — inicjalizacja i stan projektu](raporty/001_inicjalizacja.md).
2. [002 — obliczenia wstępne](raporty/002_obliczenia_wstepne.md).
3. [003 — referencje i rozpoznanie rynku](raporty/003_referencje_i_rynek.md).
4. [004 — rekomendacje i ryzyka](raporty/004_rekomendacje_i_ryzyka.md).
5. [005 — oględziny wszystkich9obrazów z diyAudio](raporty/005_analiza_obrazow_diyaudio.md).
6. [006 — narzędzia symulacji i rolaMCP](raporty/006_narzedzia_symulacyjne_i_MCP.md).
7. [007 — sprężyna powietrzna, wzrostRe i216wariantówDSP](raporty/007_fizyka_nieliniowosci_i_DSP.md).
8. [008 — kontrole i odtwarzalność pakietu](raporty/008_weryfikacja_pakietu.md).
9. [009 — wykonane badanie strat i nieszczelnościN7](raporty/009_N7_straty_nieszczelnosci.md).
10. [010 — szeroka pula i krytyczna kwalifikacja](raporty/010_szeroka_pula_i_kwalifikacja.md).
11. [011 — analityczne granice po dodatnim litrażu](raporty/011_granice_globalne_litrazu.md).
12. [012 — identyfikowalność i opublikowane parametry](raporty/012_identyfikowalnosc_i_dane_publikowane.md).
13. [013 — pokój, dwa źródła i realne gabaryty](raporty/013_pokoj_i_realne_gabaryty.md).
14. [014 — weryfikacja etapu i odtwarzalność](raporty/014_weryfikacja_etapu_20261024.md).
15. [015 — niepewność globalna, korelacje i kontrprzykłady dominacji](raporty/015_niepewnosc_globalna_i_odpornosc.md).
16. [016 — cieplny gaz, lepkość, wypełnienie, harmoniczne i DC](raporty/016_gaz_wypelnienie_i_granice.md).
17. [017 — promieniowanie, Mmd/Mms, dwa źródła i reakcja pokoju](raporty/017_promieniowanie_i_sprzezenie_pokoju.md).
18. [018 — rzut pokoju i warunkowa geometria odsłuchu](raporty/018_rzut_pokoju_i_odleglosc_odsluchu.md).
19. [019 — docelowa zamiana kanapy i RTV](raporty/019_zamiana_kanapy_i_RTV.md).
20. [020 — nieliniowy napęd, współenergia, gaz i rozruch](raporty/020_nieliniowy_naped_i_sprzezony_gaz.md).
21. [021 — pamięć cewki, moduł/faza L_gen i właściwa siła](raporty/021_pamiec_cewki_i_definicja_Lgen.md).
22. [022 — orientacyjny stan badań i zakres pozostały](raporty/022_stan_badan_i_zakres_pozostaly.md).
23. [023 — P14A, wspólne limity i pilot IMD](raporty/023_P14A_dwa_tony_i_wspolne_limity.md).

## Odtworzenie obliczeń

Python 3.12; wersje bibliotek w[requirements.txt](requirements.txt).
W obecnym środowisku potrzebne biblioteki są już dostępne.

```bash
python3 skrypty/odtworz_wszystko.py
```

Skrypty ustalają katalog projektu na podstawie własnej ścieżki. Dla osobnego
środowiska można utworzyć`.venv` i zainstalować`requirements.txt`. Nie trzeba
zmieniać globalnej instalacji. Wykresy są zapisywane jakoPNG iSVG bez interfejsu
graficznego, dane jakoCSV/JSON. Manifest zapisuje wersje, konfigurację i hashe.

Pełny przebieg zachowuje poprzedni stan roboczy w `wyniki/archiwum/`,
uruchamia wszystkie analizy i na końcu zapisuje manifest.
Kontrole modelu obejmują bilans mocy, skalowanie, porównanie z analityką,
F3 i granice ruchu/napędu. Nie potwierdzają osiągów fizycznego egzemplarza.
KampaniaP12/P13 zapisuje dziennik z hashem kodu i wejść; zgodne przypadki
wznawia. Użycie dziennika jest kontrolowanym odtworzeniem artefaktów,
nie niezależną nową replikacją ODE. Procedura świeżego rachunku jest w raporcie020.
P12C także wznawia zgodny dziennik. Odtworzenie samej digitalizacji jest
osobnym etapem: [opcjonalne wymagania źródeł](requirements_zrodla.txt),
oryginalnyPDF o wskazanymSHA i `python3 skrypty/digitalizuj_Lgen_Purifi.py`.
Standardowe obliczenia korzystają z wersjonowanych odczytówCSV, bez pobierania
materiałów i bez włączania prywatnych kopiiPDF do repozytorium.

## Organizacja danych

`dane/przetworniki/` — katalogowe wejścia z pochodzeniem i konfliktami.
`dane/konfiguracje/` — jawne scenariusze. `dane/zrodla/` — wyciągi,PDF iobrazy.
`dane/pomiary/` — miejsce na przyszłe pomiary, obecnie bez wyników urządzenia.
`skrypty/` — modele i kontrole. `wyniki/` — wygenerowane tabele,wykresy,manifest.
`raporty/` — interpretacje i rekomendacje. `szablony/` — karty przyszłych prac.

Źródła z internetu: browser-harness oraz dopuszczony Firecrawl. Kosztorys,
dostępność PL/UE i dobór handlowy pozostają odłożone. Przegląd opinii wszystkich
24 kandydatów wykonano z jawnymi brakami; nie stanowi rankingu jakości.
Najbliższy krok: P14/IMD i wielotony z modelemFLUX;
następnie promieniowanie harmonicznych, termika, mechanika z klejem i integracja.
