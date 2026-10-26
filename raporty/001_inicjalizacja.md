# Raport 001 — uruchomienie projektu badawczego

Data: 2026-10-23. Zakres: plan i pierwsza iteracja prac badawczych do budowy.

Przeczytano cały brief v0.6. Jego SHA-256:
`3bd9f8d43a92b96256073e66cd0f4f105336e969a37c29fc42f17cda9d66736f`.
Brief zachowano bez zmian. Katalog początkowo zawierał wyłącznie ten dokument.

## Wykonane

- Utworzono [instrukcję i dziennik](../AGENTS.md), [plan R0–R5](../PLAN_B_R.md),
  [macierz wymagań](../WYMAGANIA.md) i [rejestr decyzji](../DECYZJE_I_PYTANIA.md).
- Opracowano bazę wiedzy: fizyka, model, pokój, mechanika, elektronika/DSP,
  późniejsze badania, niepewność i opinie. Nie stanowi ona zamkniętego przeglądu rynku.
- Odczytano karty trzech Daytonów oraz arkusz SB Acoustics; do modelu włączono
  4 przetworniki, 6 objętości i 6 częstotliwości raportowych.
- Odczytano strony kandydatów referencyjnych ADAM oraz miniDSP; braki
  protokołów i wersji zapisano w [raporcie źródłowym](003_referencje_i_rynek.md).
- Zebrano pierwsze opinie historyczne i porady konstruktorów z diyAudio.
  Obejrzano i zachowano 9 załączników wątku 360765, w tym wykresy WinISD.
- Przygotowano ogólną [listę kwestii do uzgodnienia przed obróbką CNC](../WYKONAWCA_CNC.md).
- Wykonano model, kontrole fizyczne i obliczenia; wynik w [raporcie002](002_obliczenia_wstepne.md).

## Doprecyzowania użytkownika

Obecna praca kończy się przygotowaniem do budowy. Dobór toru pomiarowego
po wykonaniu prototypu; istnieją multimetr, oscyloskop i lutownica. Późniejsze
pomiary tylko w pokoju. Opinie i obrazy z forów są częścią materiału badawczego.
Narzędzia CAD i ich integracje odłożone. Dopuszczono Firecrawl do gromadzenia
informacji potrzebnych do badań, obliczeń i symulacji.

## Stan narzędzi i dowodów

Python 3.12.3, NumPy 1.26.4, SciPy 1.17.1, Matplotlib 3.10.8, SymPy 1.12.
Nie instalowano MathPy; obecne obliczenia nie wymagają tej biblioteki.
Matplotlib zgłasza problem lokalnej instalacji projekcji 3 D; wykresy 2 D
zostały wygenerowane i obejrzane. Nie zmieniano globalnego środowiska Pythona.

browser-harness: po uruchomieniu poza ograniczeniem zapisu runtime poprawnie
odczytywał realne strony i obrazy; nagrywanie wyłączone. Część wejść diyAudio
początkowo pokazywała walidację przeglądarki, późniejszy zwykły odczyt zadziałał.
Pierwszy adres produktu 126 odnaleziono przez wyszukiwarkę i zweryfikowano
bezpośrednio; błędny adres 123 prowadził do HFA8, którego dane zapisano oddzielnie.

Odczyt SB PDF początkowo przekroczył limit pojedynczego wywołania. Pobranie
asynchroniczne w browser-harness zakończyło się powodzeniem; dokument
wyrenderowano i obejrzano. Nie oparto parametrów na samym urywku wyszukiwarki.

## Co pozostaje otwarte

Nie wybrano finalnego głośnika, litrażu, wzmacniacza, DSP ani presetów ochrony.
Zatwierdzono referencjeSub12/Sub15, ale brak progów odbiorowych, pełnej analizy ofert
PL/UE, kompletu aktualnych opinii wszystkich kandydatów ani niezależnego THD.
Nie sporządzono wykonawczych plików CNC ani pełnego kosztorysu. Nie zbudowano
urządzenia i nie wykonano pomiarów gotowego subwoofera.

## Aktualizacja naukowa i następna iteracja

Najnowsze ustalenie U-010 zawęża aktywną pracę do nauki. Dodano 72 przypadki
siły gazu, 72 wiersze scenariuszy Re i 216 kombinacji DSP. BL 13,99 Tm potwierdzono
w odczycie PDF przez Firecrawl. Narzędzie działa z zapisanymi poświadczeniami;
CLI umieszczono tymczasowo w `/tmp/sub-krystian-firecrawl`, bez zmiany środowiska projektu.

Następny pakiet: model strat/nieszczelności N7 z kontrolą granicy szczelnej
i pasywności. Szczegóły w [planie naukowym](../PLAN_BADAN_NAUKOWYCH.md).
Wyceny, dobór handlowy, narzędzia CAD oraz tor pomiarowy są odłożone.
