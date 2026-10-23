# SUB_prototyp

Badania naukowe i rozwój prototypu subwoofera zamkniętego.

**Bieżący zakres: wyłącznie naukowe zagadnienia prototypu (U-010).**
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

## Organizacja danych

`dane/przetworniki/` — katalogowe wejścia z pochodzeniem i konfliktami.
`dane/konfiguracje/` — jawne scenariusze. `dane/zrodla/` — wyciągi,PDF iobrazy.
`dane/pomiary/` — miejsce na przyszłe pomiary, obecnie bez wyników urządzenia.
`skrypty/` — modele i kontrole. `wyniki/` — wygenerowane tabele,wykresy,manifest.
`raporty/` — interpretacje i rekomendacje. `szablony/` — karty przyszłych prac.

Źródła z internetu: browser-harness oraz dopuszczonyFirecrawl. Kosztorys,
dostępnośćPL/UE, pełne opinie wszystkich kandydatów i finalny napęd pozostają
otwarte i są obecnie odłożone. Najbliższy krok naukowy: model strat
i nieszczelności N7, z kontrolą granicy szczelnej i dodatniej mocy strat.
