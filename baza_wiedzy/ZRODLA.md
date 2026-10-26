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
- SRC24: [COMSOL6.3 — modele porowate](https://doc.comsol.com/6.3/doc/com.comsol.help.aco/aco_ug_pressure.05.182.html).
  Obejrzano oryginalne wzory obrazowe ZK, wiotkiego szkieletu i dziedziny DB.
- SRC25: [Wright/KEF — ACE, reprint](https://techtalk.parts-express.com/filedata/fetch?id=1163933&d=1422900645).
  Tekst przez Firecrawl; przeglądarka403. Automatycznych tablic z wykresów nie przyjęto.
- SRC26: [ISOVER Aku-Płyta, karta2022](https://www.isover.pl/documents/karta-produktu-pds/kt-aku-plyta-aku-plat-202206.pdf).
  AFr≥5kPa*s/m² nie jest kompletem mikrostruktury ani oporem całej warstwy.
- SRC27: [Venegas et al., ForumAcusticum2023](https://dael.euracoustics.org/confs/fa2023/data/articles/000280.pdf).
  OryginalnyPDF obejrzany na stronach2–5. Rysunki opisują modelBR; nie pomiar sealed.
- SRC28: [COMSOL6.3 — Baffled Piston Radiation](https://www.comsol.com/model/download/1340691/models.aco.baffled_piston_radiation.pdf).
  Oryginał: równania i rysunki na stronach2–8; uzgodnić amplitudę/RMS przy mocy.
- SRC29: [FaitalPRO15XL1400,8Ω](https://faitalpro.com/en/products/LF_Loudspeakers/product_details/datasheet.php?id=201060150).
  Obejrzano kartę: Mms190,0g/Mmd162,4g i osobny zestaw Cms/BL/Rms; protokół powietrza nieustalony.
- SRC30: [Bellows2024, JASA155,3302–3305](https://sambellows.github.io/assets/pdf/2024_spherical_cap.pdf).
  Równania4–6 i rysunki1–3 obejrzane w oryginale. Odtworzono drukowane minimum poprawki czaszy;
  promień rzutu nie jest promieniem koła o powierzchniSd. DOI10.1121/10.0026023.

P11: [fakty, hashe i ograniczenia odczytu](../dane/zrodla/P11_promieniowanie_i_konwencje_mas.json).
Automatyczne tablice punktów z wykresów odrzucono. Link Southampton przekierował
na stronę główną; nie jest przeczytaną pracą. Data dostępu SRC28–30:2026-10-24.

- SRC31: [Klippel — Loudspeaker Nonlinearities: Causes, Parameters, Symptoms](https://www.klippel.de/fileadmin/_migrated/content_uploads/Loudspeaker_Nonlinearities%E2%80%93Causes_Parameters_Symptoms_01.pdf).
  Sekcja3; oryginał stron7/8/14 obejrzany, Kms jest sieczne. Nie przeczytano całego dokumentu.
- SRC32: [KLIPPEL LSI3 — instrukcja identyfikacji](https://docs.klippel.de/db-lab/latest/transducer-parameter-identification/lsi3/lsi3.html).
  Definicje, względna/absolutna identyfikacja i oryginalne cztery przykładowe krzywe;
  przykładowy przetwornik nie jest kandydatem z naszej puli.
- SRC33: [PurifiNAB-01 — karta0.95/June2024](https://purifi-audio.com/shop/ptt10-0x04-nab-01-ptt10-0x04-nab-01-2043/document/583).
  Oryginalne tabele oraz BL/Kms i Le(x,f). Nie przyjęto automatycznych tablic Firecrawl.
- SRC34: [Vance Dickason — niezależny test dokładnego PTT10.0X04-NAB-01](https://audioxpress.com/article/test-bench-purifi-audio-ptt10-0x04-nab-01-10-midbass-woofer).
  Publikacja29.01.2025; Klippel/Redrock, oryginalneFig5/7/9 obejrzane,
  progi sprawdzone w DOM. Nie przenosić warunków testu na20HzTHD sealed.

P12/P13: [fakty, hashe, obrazy i luki](../dane/zrodla/P12_P13_nieliniowosci_i_luki.json),
[stan źródeł24modeli](../dane/przetworniki/dostepnosc_nieliniowych_P12.json).
Data dostępu SRC31–34:2026-10-24. Puste wyszukiwania STX nie dowodzą braku danych.

- SRC35: [Risbo et al., Force Factor Modulation in Electro Dynamic Loudspeakers, AES141/2016](https://purifi-audio.com/documents/content/WT1Pkt9-SxijAvNyifNN4Ao2a2).
  Oryginalne strony2/4/7 i sekcje2–4: równanie6 definiuje zespoloneLgen,
  równanie18 określa siłę dla L2R2.4″DUT iMagNet nie są naszymi produktami.
- SRC36: [PURIFI Ushindi/PureDrive](https://purifi-audio.com/ushindi).
  Opis producenta; deklaracji marketingowych10x i ocen odsłuchowych
  nie przyjęto jako dowodu ilościowego.

P12C: [pochodzenie i definicje](../dane/zrodla/P12C_definicja_Lgen_i_sila.json).
Źródła pobrano24.10.2026, analizę zakończono25.10.2026.
Oryginalny wykres4SRC33 ma oś **|Lgen|**; [30odczytów](../dane/zrodla/digitalizacja/Purifi_NAB01_Lgen_fig4.csv)
z kalibracją i modelem niepewności odczytu są digitalizacją danych producenta,
nie surowym pomiarem ani tolerancją populacji.

Przekazane przez użytkownika oceny i program są zachowane w
[materialach źródłowych](../dane/zrodla/materialy_uzytkownika/indeks.json).
To wymagania i komentarze do badań, a nie niezależna walidacja osiągów.

- SRC37: [KLIPPEL — Intermodulation Distortion](https://www.klippel.de/know-how/measurements/nonlinear-distortion/intermodulation-distortion.html).
  Metoda i znaczenie faz; nie przyjęto ogólnych liczb jako wyników naszych modeli.
- SRC38: [KLIPPEL AN10 — Loudspeaker FM and AM Distortion](https://www.klippel.de/fileadmin/klippel/Files/Know_How/Application_Notes/AN_10_Loudspeaker_FM_and_AM_Distortion.pdf).
  Obejrzano oryginalne strony2/3/5/6 i wykresy. Warunki>8:1 oraz1:4
  nie odpowiadają naszym parom. Wzór d_AMD ze s.3 ma czynnik sqrt(2)
  względem naszej miary RMS obwiedni; nie deklarujemy ich tożsamości ani zgodności IEC.
- SRC39: [Cotté — MF208, Aeroacoustics and Acoustic Propagation in Moving Media](https://perso.ensta.fr/~cotte/files/Poly_MF208_2023.pdf).
  Oryginał stron30/32: punktowe źródło, funkcja Greena i czynnik1−Mr.
  Nie jest to rozwiązanie ruchomej granicy finalnego subwoofera.

P14B: [fakty, daty, oryginały i ograniczenia](../dane/zrodla/P14B_IMD_AM_FM_i_emisja.json).
Data dostępu2026-10-25; kopiePDF i renderów pozostają prywatne w.firecrawl.

- SRC40: [KLIPPEL AN18 — Thermal Parameter Measurement,rev1.5](https://www.klippel.de/fileadmin/klippel/Files/Know_How/Application_Notes/AN_18_Measurement_of_Linear_Thermal_Parameters.pdf).
  Oryginalne strony2/3/6: topologia R||C, wzory i wykresy procedury.
  Nie przenosić parametrów Foster bez transformacji na fizyczne węzły Cauer.
- SRC41: [KLIPPEL — Thermal Analysis and Heat Transfer](https://www.klippel.de/know-how/measurements/power-handling-heat-dissipation/thermal-analysis-and-heat-transfer.html).
  Obejrzano oryginalne heat_flow.jpg i bypass.jpg; własne pojemności
  węzłów, konwekcja i ciepło prądów wirowych. Liczb przykładu nie przeniesiono.

P15A: [fakty, obrazy i hashe](../dane/zrodla/P15A_topologie_i_cieplo.json).
Data dostępu2026-10-25. Brak identyfikacjiRth/Cth naszych24produktów.

- SRC42: [W.Klippel — Nonlinear Modeling of the Heat Transfer in Loudspeakers](https://pearl-hifi.com/06_Lit_Archive/15_Mfrs_Publications/24_Klippel/AES_ALMA_and_Other_Papers/2003_Nonlinear_Modeling_of_Heat_Transfer.pdf).
  Oryginalny manuskrypt w archiwumPEARL,wybrane strony6/7/38/42–44
  i wykresy obejrzane. Rok2003 wynika z nazwy pliku. Liczba0,0393K^-1
  ze s.6 zablokowana jako wejście z powodu rozbieżności zSRC44.
- SRC43: [KLIPPEL — Voice Coil Temperature](https://www.klippel.de/know-how/measurements/power-handling-heat-dissipation/voice-coil-temperature.html).
  Rezystancyjne odniesienie zależy od materiału; obejrzano oryginalny
  wykres temperatur/mocy przy muzyce. Bez transferu temperatur na kandydatów.
- SRC44: [J.H.Dellinger/NBS — The Temperature Coefficient of Resistance of Copper](https://nvlpubs.nist.gov/nistpubs/bulletin/07/nbsbulletinv7n1p71_A2b.pdf).
  OryginałTableI,s.76 i podsumowanie,s.96 (PDF6/26) obejrzane.
  Alpha20 jest względemR20,liczby rzędu0,0039K^-1; nie tolerancja naszych cewek.

P15B: [pochodzenie, obrazy i konflikt liczbowy](../dane/zrodla/P15B_sprzezenie_i_konflikt_alpha.json).
Data dostępu2026-10-25. Parametr0,004K^-1pozostaje założeniem scenariusza.

- SRC45: [Kronospan Luxembourg — DoP1607101012,Kronogen+UM](https://kronospan.com/en_FR/ajax/express_services/download?args%5B0%5D=express-services&args%5B1%5D=downloads&args%5B2%5D=France&args%5B3%5D=certificates-and-datasheets&args%5B4%5D=en&args%5B5%5D=1607101012-do-p-mdf-k-um-en.pdf&show=1).
  Obejrzano2oryginalne strony; E/MOR/IB zależne od grubości. Referencja2016,
  nie identyfikacja materiału wykonawcy ani danych zmęczeniowych.
- SRC46: [Ko,Lee,Bathe — A new MITC4+ shell element,2017](https://web.mit.edu/kjb/www/Principal_Publications/A_new_MITC4+_shell_element.pdf).
  Oryginał stron2/3,sekcja2 iFig2. Użyto wzorca ścinaniaMITC4 w prostokątnej
  płycie; nie implementowano całej powłoki lub membranMITC4+.
- SRC47: [KLEIBERIT303.0 — TDS,wersja08:05:2026](https://pim.kleiberit.com/Datenblaetter/303-0-00/technical/en/dbe3030_KSE.pdf).
  Oryginałs.2:proces,docisk lameli i utwardzanie. Brak modułów,J(t),S–N
  oraz dopuszczalnej nośności połączeniaMDF.
- SRC48: [Henkel — LOCTITEEA9466,TDSMarch2025](https://datasheets.tdx.henkel.com/LOCTITE-EA-9466-en_GL.pdf).
  Obejrzano oryginalne strony1/2 i krzywe. Typowy modułfolii1718MPa
  nie jest wytrzymałościąMDF; krzywych stali nie przeniesiono naMDF.

P18A/P19A: [fakty,oryginały i granice](../dane/zrodla/P18_P19_materialy_i_metoda.json).
Data dostępu2026-10-25. ReakcjaRayleigha rozwija źródłaP11 i własne kontrole.

## Pliki zachowane lokalnie

**SRC51**,2026-10-25: [Abaqus2025 — continuum elements with incompatible modes](https://docs.software.vt.edu/abaqusv2025/English/SIMACAETHERefMap/simathe-c-incompatible.htm).
Odczytano liniowy kontekst i oryginalne MathML warunków pól dodatkowych.
C3D8I ma13modów;własnyEAS9niejest jegoimplementacją. Wykorzystanie i
hash prywatnej ekstrakcji są w [rejestrzeP18C](../dane/zrodla/P18C_teoria_3D_i_metoda.json).
Wcześniejszy timeout nawigacji rozstrzygnięto ponownym odczytem tej samej
karty;nie oznaczał niedostępności publikacji. Prac Wilson/Simo nie
uznajemy za przeczytane na podstawie znalezienia odnośników.

P18B/P19B,2026-10-25: **SRC49** — oryginalny rysunekDaytonRSS390HF-4
z PDFproducenta; **SRC50** — oryginalny rysunekSTXW.32.800.8.FCX.
Ponownie obejrzano SRC03/SB34REV2. Wymiary i ich płaszczyzny odniesienia,
masy nieznane oraz hashe są w
[rejestrzeP18B](../dane/zrodla/P18B_geometria_i_ograniczenia.json).
DaytonWeight30lb nie stało się zweryfikowanymMnet,STXnetmass jest puste.
Nie pobierano automatycznych tablic punktów wykresów.

- [Wejścia katalogowe i konflikty](../dane/przetworniki/kandydaci.json).
- [PDF SB Acoustics](../dane/zrodla/SRC03_SB34SWPL76-4.pdf).
- [Transkrypcja PDF Dayton przez Firecrawl](../dane/zrodla/SRC01_PDF_transkrypcja_firecrawl.md).
- [Wyciąg metadanych](../dane/zrodla/rejestr.json).
- [Załączniki dyskusji z adresami](../dane/zrodla/obrazy_diyaudio_360765/indeks.json).
- [Manifest z SHA-256](../wyniki/manifest.json), obejmujący źródła, kod, konfigurację i wyniki.

Zachowanie pliku i hash dowodzą, z jakich danych wykonano obliczenia; nie
potwierdzają poprawności deklaracji producenta. Transkrypcję danych trzeba
kontrolować z oryginałem, szczególnie jednostki p-p/peak i mm/N/m/N.

## Rozszerzenie SB Acoustics — sprawdzone oryginały

Rozszerzenie SB,2026-10-26: **SRC52** — SB34SWNRX-S75-6, PDF REV.0
(17.10.2012); **SRC53** — SB34SWPL76-3-DV, PDF REV.1 (03.10.2017).
Oryginały pobrano przez browser-harness i obejrzano w całości na stronie1:
tabele,rysunki,osie,legendy i przypisy. Nie zaakceptowano automatycznych
tablic odczytu krzywych Firecrawl. C25: konflikt22.5mm p-p wPDF /22mm WWW.
C26:300Woznaczone ser.;Le1.4/6.1mH dla różnych połączeń. Dane,hashe,
ocena czterech odczytów/awarii opinii i zakres użycia:
[rejestrSB](../dane/zrodla/SB_rozszerzenie_pochodzenie.json),
[raport038](../raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md).
ForumZelfbouwaudio zwróciło503/dostęp po zalogowaniu;nie jest przeczytaną
dyskusją. Publiczne własne parametry i rachunki; oryginały prywatne.firecrawl.

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
