# Rejestr źródeł

Rozszerzenie 2026-10-24: [24 modele z danymi producentów](../dane/przetworniki/pula_rozszerzona.json),
[jawny przegląd źródeł opinii](../dane/zrodla/opinie_puli_przeglad.json) i
[krytyczna ocena trafień](../dane/zrodla/opinie_puli_ocena.json).
Tabele producenta są danymi katalogowymi, a opinie źródłami problemów i hipotez.
Nie są automatycznie niezależnymi pomiarami. Źródła i konwersje jednostek
przypisano indywidualnie do każdego kandydata.

Data dostępu: **2026-10-23**, o ile nie zaznaczono inaczej. Strony i obrazy
odczytywano przez browser-harness. Firecrawl odczytał również PDF RSS315HF-4
oraz dwie dodatkowe dyskusje. Samo znalezienie linku nie oznacza analizy źródła.

| ID | Źródło bezpośrednie | Odczyt / zastosowanie | Ograniczenie |
|---|---|---|---|
| SRC01 | [Dayton RSS315HF-4](https://www.daytonaudio.com/product/121/rss315hf-4-12-reference-hf-subwoofer-4-ohm) | WWW przez browser-harness, PDF przez Firecrawl | WWW podaje BL1Tm; PDF 13,99Tm. Zachowano konflikt; model wyprowadza BL |
| SRC02 | [Dayton RSS390HF-4](https://www.daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm) | WWW, T/S, model 15″ | Brak niezależnego THD i pełnej definicji Xmax |
| SRC03 | [SB34SWPL76-4 PDF](https://sbacoustics.com/wp-content/uploads/2022/03/12in-SB34SWPL76-4.pdf), [strona](https://sbacoustics.com/product/12in-sb34swpl76-4/) | PDF pobrano przez przeglądarkę i obejrzano; REV2 z 17.02.2022 | Katalog, nie pomiar niezależny; 30 mm p-p przeliczono na 15 mm jednostronnie |
| SRC04 | [ADAM Sub12](https://www.adam-audio.com/en/subwoofers/sub12/) | Główne deklaracje katalogowe, kandydat referencyjny | Brak pełnego pasmowego SPL i protokołu w odczytanym opisie |
| SRC05 | [ADAM Sub15](https://www.adam-audio.com/en/subwoofers/sub15/) | Główne deklaracje, wyższy kandydat referencyjny | Nie utożsamiać maxSPL z osiągami 20 Hz ani SPL ciągłym |
| SRC06 | [ADAM A8H](https://www.adam-audio.com/en/a-series/a8h/) | Referencja aktywnego 3-way; znaleziono link do raportu | Raport pomiarowy nie został jeszcze przeanalizowany |
| SRC07 | [ADAM S3V](https://www.adam-audio.com/en/s-series/s3v/) | Referencja wyższa; strona ma linki do danych pomiarowych | MaxSPL na parę; inne warunki niż A8H; skrót pasma wymaga kontroli |
| SRC08 | [miniDSP Flex Eight](https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight) | Aktualny opis producenta:8 wyjść analogowych, wejścia cyfrowe i opcje | Wersja, napięcia, szum i limitery wymagają audytu instrukcji; brak oferty PL |
| SRC09 | [Dayton RSS315HFA-8](https://www.daytonaudio.com/product/123/rss315hfa-8-12-reference-hf-subwoofer-8-ohm) | WWW, T/S, porównanie 8Ω | Inny model niż HF-4; brak cen UE i niezależnego THD |
| SRC10 | [diyAudio, wątek72895](https://www.diyaudio.com/community/threads/diy-sub-with-dayton-rss315hf-4-in-progress-can-someone-check-my-math.72895/) | Odczyt wpisów, doświadczenia i korekta błędnego Vas | Relacje historyczne 2006; stare parametry i subiektywne oceny |
| SRC11 | [diyAudio, wątek360765](https://www.diyaudio.com/community/threads/help-finalising-enclosure-design-dayton-rss315hf-4.360765/) | Odczyt dyskusji i wszystkich 9 załączników | Projekt BR2020, brak wyniku gotowego subwoofera |
| SRC12 | [Allegro, wykonawca17586111495](https://allegro.pl/oferta/elementy-obudowa-glosnika-mdf-na-zamowienie-subwoofer-cnc-na-wymiar-17586111495) | Pełny opis przekazał użytkownik; [wyciąg technologiczny](../WYKONAWCA_CNC.md) | Bez niezależnego audytu aktualnej oferty i wyceny |
| SRC13 | [diyAudio386102, strona2](https://www.diyaudio.com/community/threads/sealed-ported-convertible-subwoofer.386102/page-2) | Firecrawl; relacja o obudowie przełączanej, wzmianki o testach | Mieszane modele; SB3DVC to inny przetwornik; wzmianki oTHD wymagają oryginalnych testów |
| SRC14 | [ASR28117, strona3](https://www.audiosciencereview.com/forum/index.php?threads/help-with-my-faulty-12-subwoofer-design.28117/page-3) | Firecrawl; dyskusja o pomiarzeTHD i obudowieSB | Brak pełnego protokołu; nie przyjmować ogólnej porady o 70l jako dowodu optimum |

## Nowe źródła teoretyczne i pomiarowe

- SRC15: [Small, Closed-Box Loudspeaker Systems, 1972](https://aes.org/publications/elibrary/elibrary-page/?id=2022).
  Odczytano abstrakt i metadane; nie zadeklarowano przeczytania pełnego artykułu.
- SRC16: [KLIPPEL — single-valued nonlinear parameters](https://www.klippel.de/know-how/measurements/transducer-parameters/single-valued-nonlinear-parameters.html).
  Odczyt definicji i kryteriów. Nie utożsamiać wszystkich katalogowych Xmax.
- SRC17: [Kleiberit 303.0 — karta producenta](https://pim.kleiberit.com/Datenblaetter/303-0-00/technical/en/dbe3030_KSE.pdf).
  [Zapis faktów procesu i braków obliczeniowych](../dane/zrodla/SRC17_klej_Kleiberit303_fakty.json).
  Klasa D3/D4 nie zastępuje danych nośności połączenia MDF; kleju nie wybrano.
- SRC18: [Voice Coil — Scan-Speak 32W/4878T00, materiał z 2013](https://www.scan-speak.dk/datasheet/reviews/32W-4878T00-VoiceCoil_2013-3.pdf).
  Obejrzano strony 2–5; [zweryfikowane dane](../dane/zrodla/pomiary_opublikowane/scan32_voicecoil_2013.json).
  Tabela dwóch próbek nie jest tolerancją populacji. Automatycznych tablic z krzywych nie przyjęto.
- SRC19: [Meissner i Wiśniewski (2020), tłumienie i pole niskoczęstotliwościowe](https://pmc.ncbi.nlm.nih.gov/articles/PMC7481690/).
  Odczyt metod i ograniczeń; własny model diagonalny jest uproszczeniem ich teorii.
- SRC20: [COMSOL — Eigenmodes of a Room](https://www.comsol.com/model/download/1166101/models.mph.eigenmodes_of_room.pdf).
  Odczyt analitycznej podstawy i granic modelu sztywnych ścian; nie uruchamiano CAD/COMSOL.
- SRC21: [JCGM 101:2008](https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf).
  Odczyt warunków przypisania rozkładów i wspólnych PDF dla zależnych wejść.
- SRC22: [SciPy — sobol_indices](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.sobol_indices.html).
  Definicje, metoda Saltelli2010 i niezależność; przyjęta miara nie jest rozkładem produktów.
- SRC23: [mpmath — arytmetyka IV](https://mpmath.org/doc/current/contexts.html#arbitrary-precision-interval-arithmetic-iv).
  Gwarancja zawierania i ostrzeżenie o eksperymentalnej obsłudze; zakres P06 opisano jawnie.

Przekazane przez użytkownika oceny i program są zachowane w
[materialach źródłowych](../dane/zrodla/materialy_uzytkownika/indeks.json).
To wymagania i komentarze do badań, a nie niezależna walidacja osiągów.

## Pliki zachowane lokalnie

- [Wejścia katalogowe i konflikty](../dane/przetworniki/kandydaci.json).
- [PDF SB Acoustics](../dane/zrodla/SRC03_SB34SWPL76-4.pdf).
- [Transkrypcja PDF Dayton przez Firecrawl](../dane/zrodla/SRC01_PDF_transkrypcja_firecrawl.md).
- [Wyciąg metadanych](../dane/zrodla/rejestr.json).
- [Załączniki dyskusji z adresami](../dane/zrodla/obrazy_diyaudio_360765/indeks.json).
- [Manifest z SHA-256](../wyniki/manifest.json), obejmujący źródła, kod, konfigurację i wyniki.

Zachowanie pliku i hash dowodzą, z jakich danych wykonano obliczenia; nie
potwierdzają poprawności deklaracji producenta. Transkrypcję danych trzeba
kontrolować z oryginałem, szczególnie jednostki p-p/peak i mm/N/m/N.

## Znalezione dokumenty do dalszej analizy

- [RSS315HF-4 Specification Sheet](https://www.daytonaudio.com/images/resources/295-464-dayton-audio-rss315hf-4-specifications-46174.pdf).
- [RSS390HF-4 Specification Sheet](https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf).
- [A8H Measurement Report v4](https://www.adam-audio.com/content/uploads/2024/04/adam-audio-a-series-a8h-studio-monitor-measurement-report-v4-english.pdf).
- [S3V Product Sheet](https://www.adam-audio.com/content/uploads/2021/03/ADAM_Audio_S3V_Product_Sheet.pdf).

PDF RSS315HF-4 został już odczytany przez Firecrawl; rozstrzygnięto konfliktBL.
Pozostałe linki znaleziono, ale nie utożsamiamy znalezienia z przeczytaniem dokumentu.

## Luki do uzupełnienia przed decyzją zakupową

Oferty PL/UE z ceną brutto i dostawą, potwierdzenie dostępności, niezależne
T/S/THD/kompresja, aktualne opinie wszystkich finalistów, instrukcje napędu,
zasilaczy i DSP oraz spójne warunki referencji ADAM. Braków nie wypełniamy
wartościami z historycznego projektu ani wynikami samej wyszukiwarki.
