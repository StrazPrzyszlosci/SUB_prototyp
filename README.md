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
Historyczny etap częściowyP14B: [raport024 — fazory, emisja i15zamrożonych świadków](raporty/024_P14B_emisja_i_swiadkowie.md).
Przypadek45+95Hz tworzy ruch5Hz; rozdzielono projekcje stałe i kontrolny
ruchomy monopol. To nie zmierzone THD ani zamknięcie kampanii3312przypadków.
Rozpoczęto termikę: [raport025 — P15A, topologie i granice](raporty/025_P15A_topologia_i_granice_termiki.md).
4225sieci kontrolnych, ciągła niejednoznaczność chłodzenia i warunkowe
wymaganiaRth; nie prognozy temperatur konkretnych produktów.
**Wykonano zakres P14B:** [raport026 —3312przypadków, fazy, amplitudy i rozruch](raporty/026_P14B_pelna_kampania_dwutonowa.md).
23flagi rozstrzygnięto osobno;16560projekcji pola i4niezależneRadau.
**Wykonano rodzinę P15B:** [raport027 —2304przebiegiRe(T),grzania i ruchu](raporty/027_P15B_sprzezenie_grzania_i_napedu.md).
Nie są to zidentyfikowane temperatury24produktów.
**P17:** [raport028 — synteza napięcia,prądu,objętości i chłodzenia](raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md).
5184zestawy i31104punkty wymaganej pracy; analityczne przedziały Vb>0,
bez udawania progów klienta ani SPL w pokoju. Następne wykonane podstawy
mechaniki opisują poniższe raporty.
**Wykonane podstawy mechaniki:** [raport029 —172warianty płyt i ściągów](raporty/029_P18A_plyty_sciagi_i_dynamika.md),
[030 —656normalnych podmodeli spoiny,ścinanie i szczeliny](raporty/030_P19A_obliczenia_spoin_i_material_kleju.md),
[031 —72sprzężone punkty reakcji powietrza](raporty/031_P21A_reakcja_powietrza_i_bilans.md).
Nie są to pełna geometria frontu3D i kwalifikacja trwałości kleju.
Najbliższy krok:P18B — front z otworem,koszem i mocowaniem;
następnie kompletne połączenia,regulacja i pole rzeczywistej skrzyni.

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
24. [024 — P14B, fazory i emisja; raport częściowy](raporty/024_P14B_emisja_i_swiadkowie.md).
25. [025 — P15A, topologia, identyfikowalność i granice termiki](raporty/025_P15A_topologia_i_granice_termiki.md).
26. [026 — wykonany zakres dwutonowy P14B](raporty/026_P14B_pelna_kampania_dwutonowa.md).
27. [027 — P15B, sprzężenie grzania i napędu](raporty/027_P15B_sprzezenie_grzania_i_napedu.md).
28. [028 — P17, wspólne ograniczenia i objętość](raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md).
29. [029 — P18A, panele i ściągi](raporty/029_P18A_plyty_sciagi_i_dynamika.md).
30. [030 — P19A, obliczenia spoin i materiał kleju](raporty/030_P19A_obliczenia_spoin_i_material_kleju.md).
31. [031 — P21A, reakcja powietrza i bilans](raporty/031_P21A_reakcja_powietrza_i_bilans.md).

## Odtworzenie obliczeń

Python 3.12; wersje bibliotek w[requirements.txt](requirements.txt).
W obecnym środowisku potrzebne biblioteki są już dostępne.

```bash
python3 skrypty/odtworz_wszystko.py
```

**Podczas aktywnej kampaniiP14B nie uruchamiać pełnego odtworzenia**,
które archiwizuje bieżące pliki wyników. Samodzielne odtworzenie15świadków
emisji iP15A, bez dotykania aktywnych baz:

```bash
python3 skrypty/odtworz_etap_P14B_P15A.py
```

Zakres i hashe tej części są w `wyniki/manifest_etap_P14B_P15A.json`;
nie jest to manifest zakończonego programu30badań.
Wykonany późniejszy zakresP14B/P15B ma osobny
[manifest z bazami, wejściami, kontrolami i dokumentacją](wyniki/manifest_P14B_P15B.json).
Pełna procedura obejmuje już te etapy; nie oznacza to zamknięcia pozostałych
pakietów. ArchiwumP15B odtwarza zgodne checkpointy,nie nowe2304ODE.
P17ma [osobny manifest wejść, wyników i dokumentacji](wyniki/manifest_P17.json).
Podstawy mechaniki mają[osobny manifest](wyniki/manifest_mechaniki_P18_P19_P21.json)
i odtwarzanie bez powtarzania dawnych kampanii:

```bash
python3 skrypty/odtworz_mechanike_P18_P19_P21.py
```

Przed analizą przywracane są zgodne,sprawdzaneSHAarchiwa172/656checkpointów.
To odtworzenie artefaktów,nie nowy niezależny rachunek828wariantów.

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
Najbliższy krok:P18B — front z otworem,koszem i mocowaniem;
potem pełne połączenia/regulacja,pole3D,ochrona i integracja niepewności.
