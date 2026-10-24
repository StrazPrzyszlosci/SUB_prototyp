# Raport 010 — szeroka pula kandydatów pod brief

Stan: 2026-10-24. Raport cząstkowy badań bez urządzenia. Końcowy PDF jest
odłożony zgodnie z decyzją użytkownika do wykonania programu 30 pakietów.
Na końcu ma powstać jeden wybór głośnika i jednej konstrukcji, nie sama lista.

## Zakres i kwalifikacja

Zebrano tabele producentów dla **24 modeli, 11 producentów**.
Są tu modele 12/15 calowe, klasa 12.5 oraz dwie jawnie oznaczone kontrole 10 calowe
(SEAS i PURIFI). Kontrola spoza głównej klasy nie staje się automatycznie
finalistą. Aktualność starej karty Peerless, statusRSS390HE i niezgodność oznaczenia
jednej karty STX pozostają odrębnymi otwartymi bramkami danych.

Dane: [pula_rozszerzona.json](../dane/przetworniki/pula_rozszerzona.json).
Obliczenia: [CSV](../wyniki/pula_objetosci_i_naped.csv),
[podsumowanie](../wyniki/pula_podsumowanie.csv),
[audytT/S](../wyniki/pula_spojnosc_ts.csv).

## Dane kandydata i granice ruchu

X to przyjęta jednostronna amplituda katalogowa, nie wspólny próg THD.
Wartości w kolumnach SPL to granice modelu RMS dla osobnego sinusa 20 Hz,
idealna półprzestrzeń 2π,1 m. Nie są pomiarami ani poziomem w pokoju.

| ID / model | Klasa [cal] | X [mm] | Sd·X [l] | Tylko ruch 20 Hz [dB] |100 l/40 Vrms/12 Arms 20 Hz [dB]|
|---|---:|---:|---:|---:|---:|
| C01 Dayton RSS315HF-4 |12|14.3|0.736|97.92|97.92|
| C02 Dayton RSS390HF-4 |15|14|1.161|101.89|101.89|
| C03 Dayton RSS315HFA-8 |12|14.3|0.725|97.79|97.79|
| C04 SB Acoustics SB34SWPL76-4 |12|15|0.687|97.33|97.33|
| C05 STX W.32.500.8.MC_v2 |12|7.5|0.368|91.91|91.91|
| C06 STX W.32.800.8.FCX |12|15|0.737|97.93|97.93|
| C07 STX W.38.500.8.MC |15|5|0.428|93.21|93.21|
| C08 STX W.38.800.8.MC |15|8|0.680|97.24|97.24|
| C09 Scan-Speak 30W/4558T00 |12|12.5|0.583|95.89|95.89|
| C10 Scan-Speak 32W/4878T00 |12.5|14|0.736|97.93|97.93|
| C11 Dayton RSS390HE-22 seria |15|27|2.171|107.32|100.62|
| C12 SEAS L26RO4Y XM004-04 |10|15|0.513|94.79|94.79|
| C13 BMS 12N630 8ohm |12|8|0.398|92.59|92.59|
| C14 BMS 15S430v2 |15|7.5|0.673|97.14|97.14|
| C15 FaitalPRO 15XL1400 8ohm |15|12.92|1.087|101.31|99.97|
| C16 LaVoce WAF154.00 |15|12.1|1.035|100.88|99.89|
| C17 Peerless XXLS 830844 4ohm |12|12.5|0.583|95.89|95.89|
| C18 PURIFI PTT10.0X04-NAB-01 |10|14.75|0.531|95.09|95.09|
| C19 Dayton RSS390HO-4 |15|12|0.996|100.55|100.55|
| C20 Dayton UMII12-22 seria |12|22|1.162|101.89|99.60|
| C21 Dayton UMII15-22 seria |15|24|1.898|106.15|100.04|
| C22 Dayton RSS315HO-4 |12|12.3|0.633|96.62|96.62|
| C23 Eminence LAB12 6ohm |12|13|0.659|96.96|96.96|
| C24 Eminence LAB15 6ohm |15|11.8|0.972|100.34|100.34|

## Porównywalne warunki

Policzono **12576 kombinacji**: objętości 20–150 l co 1 l,
dwa hipotetyczne napędy 40 Vrms/12 Arms i 60 Vrms/20 Arms oraz ruch równy 0.7 i 1.0
wartości katalogowej. To scenariusze inżynierskie;0.7X nie gwarantuje niskiego THD.
Pasma:20/25/31.5/40/63/80 Hz. Pe różnych protokołów nie jest wspólną granicą
termiczną. Nie zadeklarowano bezpiecznej mocy ciągłej ani temperatury.

Przeskanowany zakres 20–150 l nie jest limitem wymiarów. Analiza wszystkich
dodatnichVb dla pojedynczego sinusa jest w[raporcie011](011_granice_globalne_litrazu.md).
MinimumF3 to inny problem niż najlepsza skrzynia pod pełny brief.

## Wyniki zmieniające interpretację wcześniejszych czterech modeli

- UMII12-22 ma katalogoweSd·X praktycznie równe RSS390HF-4. Rozmiar 12/15 sam
  nie określa wydajności; przy wspólnych 40 Vrms różni się wymagany napęd.
- RSS390HE-22 ma wyższą nominalną granicę ruchu, ale przy 100 l i 20 Hz
  model potrzebuje około 86.5 Vrms do 27 mm, wobec 29.3 Vrms do 14 mm dla RSS390HF-4.
  Tych napięć nie należy utożsamiać z dopuszczalną pracą ciągłą.
- STXW.32.500.8.MC_v2 podaje 15 mm p-p, czyli 7.5 mm jednostronnie;
  W.32.800.8.FCX podaje 30 mm p-p, czyli 15 mm jednostronnie.
- PURIFI używa określeniaXmax dla granicymechanicznej 25 mm, aXlin 14.75 mm
  dla ruchu liniowego. Do porównania użytoXlin. DlaLaVoce 42.8 mm p-p
  jest powiązane zXmech, nie z katalogowymXmax 12.1 mm.
- Faital dodaje do geometrycznego overhangu 1/3 wysokości szczeliny.
  DefinicjeX nie są wspólną kalibracją jakości; nie utworzono rankinguTHD.

## Krytyczna ocena opinii

Dla każdego modelu zapisano zapytanie, trafienia, odczyt oraz ocenę zgodności
modelu. Nie przyjęto liczbowych twierdzeńSPL/THD zforów bez odpowiednich warunków.
[Rejestr wyszukiwań](../dane/zrodla/opinie_puli_przeglad.json),
[ocena treści](../dane/zrodla/opinie_puli_ocena.json).

| Kandydat | Rodzaj dowodu / istotne ograniczenie |
|---|---|
| C01 Dayton RSS315HF-4 | [RELACJA_WLASCICIELA_BEZ_PROTOKOLU](https://techtalk.parts-express.com/forum/tech-talk-forum/39966-dayton-rss315hf-4-12-sealed-questions) — Relacja oRSS315HF wsealed zPEQ i wpływie ustawienia narożnego; wynik dotyczy pokoju. Nie przyjęto deklarowanego zejścia jako parametrów wolnego pola; starsza rewizja i nieznane napięcie. |
| C02 Dayton RSS390HF-4 | [SPRZECZNE_RELACJE_WLASCICIELI](https://www.diyaudio.com/community/threads/looking-for-help-with-dayton-audio-rss390hf-4-sealed.434829/) — mayhem 13 zgłasza oil-can/popping wsealed; mordikai podaje brak tego objawu w swoich zamkniętych skrzyniach. Brak wspólnego sygnału, napięcia, egzemplarzy i częstości występowania. Hipoteza krytyczna do P12/P30, nie dowód wady całej serii. |
| C03 Dayton RSS315HFA-8 | [DYSKUSJA_PROJEKTOWA](https://www.diyaudio.com/community/threads/subwoofer-choice-why-not-dayton-audio-rss315hfa-8.389894/) — Pytania oHFA8 oraz modelowanieBR/membrany biernej. Nie jest testem gotowego subwoofera ani dowodem jakościsealed. |
| C04 SB Acoustics SB34SWPL76-4 | [RELACJA_PROBLEMU_POMIAROWEGO](https://www.audiosciencereview.com/forum/index.php?threads/help-with-my-faulty-12-subwoofer-design.28117/page-2) — Yevhen opisuje problem odpowiedzi i zniekształceń, próby wypełnienia i zmian odległości; dyskusja wiąże przypadek zSB34SWPL76-4. Nie ustalono pełnego protokołu, źródła nieliniowości ani kalibracji; nie przypisanoTHD samego przetwornika. |
| C05 STX W.32.500.8.MC_v2 | [NIEPOTWIERDZONA_REWIZJA_I_INNY_MODEL](https://www.diyaudio.com/community/threads/stx-w32-500-8-mc-any-experience.402178/) — Wątek pyta oW32.500; pozytywna relacjaHicoco dotyczyW22.200.8.MCX_v 2. Nie wolno przypisać tej opinii doW32.500.8.MC_v 2 ani potraktować prośby o test jako pomiaru. |
| C06 STX W.32.800.8.FCX | [REKOMENDACJA_KONSTRUKTORA_NIE_POMIAR](https://diyaudio.pl/threads/kino-domowe-huberta-by-pawel-s-stx-awx.21172/page-4) — PawelS wskazujeW32.800.8.FCX jako propozycję w dyskusji o zestawiekinowym. WątekAWX zawiera wiele innych przetworników; brak kontrolowanego testu tegoFCX sealed 20 Hz. |
| C07 STX W.38.500.8.MC | [DYSKUSJA_Z_INNYM_MODELEM_W_RELACJI](https://www.elektroda.pl/rtvforum/topic3583142.html) — Dyskusja oW32.500 vsW38.500; relacja posiadacza dotyczyW32.500. PoradyBR80/90L40 Hz nie są wynikiem naszejopt. Opinia oinnym modelu nie przechodzi automatycznie na C07. |
| C08 STX W.38.800.8.MC | [POSREDNIE_I_INNA_IMPEDANCJA](https://www.elektroda.pl/rtvforum/topic4093514.html) — Rozmowa oPA iW38.500;W38.800 jest proponowanym następcą, także w wersji 4Ω. Nie znaleziono w odczytanym wątku bezpośredniego testu C08 8Ω sealed. |
| C09 Scan-Speak 30W/4558T00 | [DYSKUSJA_PROJEKTOWA](https://www.diyaudio.com/community/threads/need-help-with-sealed-subwoffer-and-scanspeak-discovery-30w-4558t00.250287/) — Pytania oScan 30Wsealed i poradyobjętości 50–60L. Podawanych mocy i braku ruchu nie potraktowano jako pomiaru ani ochrony. |
| C10 Scan-Speak 32W/4878T00 | [RELACJA_BUDOWY_Z_POMIARAMI_NF](https://www.audiosciencereview.com/forum/index.php?threads/my-2x-diy-scan-speak-revelator-32w-subs-build.65896/) — concorde 1 opisuje własną parę 32 W w 25 mmHDF oraz pomiaryREW przy 5 cm. Nearfield nie daje automatycznie absolutnego SPL/THD w 1 m. Potrzebne nastawy i geometria; materiał do P18/P20. |
| C11 Dayton RSS390HE-22 seria | [RELACJE_WLASCICIELI_Z_INNYCH_KONFIGURACJI](https://www.avsforum.com/threads/dual-sealed-rss390he-22-build.3278625/) — Dyskusja zawiera opisy cichej pracy oraz hałasu przy zasłoniętym otworze wentylacji. Pozytywne relacjeChrisPopovich i innego użytkownika dotyczą teżBR i wolnego powietrza, nie są dowodem wyniku sealed ztytułu. |
| C12 SEAS L26RO4Y XM004-04 | [PORADY_TECHNICZNE](https://www.audiosciencereview.com/forum/index.php?threads/high-le-problematic-seas-l26ro4y-d1004.58786/) — Dyskusja odużymLe w L26RO4Y i zastosowaniu jako subwoofer. Brak testu 20–80 Hz w tej konfiguracji; nie wyprowadzono wartościTHD. |
| C13 BMS 12N630 8ohm | [RELACJA_OGOLNEGO_DOSWIADCZENIA](https://www.audiosciencereview.com/forum/index.php?threads/one-hell-of-a-12%E2%80%9D-woofer.47066/page-5) — Positivevibrations podaje wcześniejsze używanieBMS12N630/12S330. Większość strony dotyczyCelestion/Beyma. Ich wykresów i wyników nie przypisanoBMS. |
| C14 BMS 15S430v2 | [ODRZUCONE_TRAFIENIA](https://forum.speakerplans.com/bms-15s430v2-15tbx100-or-tham15_topic97122.html) — Pierwszy trafiony wątekSpeakerplans jest ogłoszeniemwanted. Drugi odczyt dotyczy 15N850v 2, nie 15S430v2. Brak przyjętej opinii o C14 w tym przebiegu; dwa nietrafne odczyty zapisano zamiast pozornej pozytywnej recenzji. |
| C15 FaitalPRO 15XL1400 8ohm | [WLASCICIEL_I_PORADY_W_INNYM_ZASTOSOWANIU](https://www.talkbass.com/threads/faital-15xl1400-for-bass.1441013/) — WłaścicielFaital 15XL1400 pyta oobudowę basugitarowego; rozmówcy analizują skuteczność, pasmo i napęd. To nie test liniowości 20 Hz zamkniętego subwoofera. Dane dotyczące podobnegoBMS nie są pomiaremFaital. |
| C16 LaVoce WAF154.00 | [DYSKUSJA_MODELOWA](https://techtalk.parts-express.com/forum/tech-talk-forum/1402720-high-powered-sealed-sub-room-eq) — WAF154.00 pojawia się jako kandydat w rozmowie ostudyjnymsealed iEQ. Brak relacji zukończonegoWAF154 i porównywalnych pomiarów; deklaracje owyższości topologii nie są przyjętym dowodem. |
| C17 Peerless XXLS 830844 4ohm | [RELACJA_WLASCICIELA_I_ODSLUCHU](https://techtalk.parts-express.com/forum/tech-talk-forum/28304-subwoofer-recommendation-3-3cf-sealed-cabinet) — jAy opisuje własny 830844 wsealed 1.7 ft 3 i domowe porównanie zRSS315HF. WybórPeerless jest preferencją bez kontrolowanego protokołu/THD; stare modele i niezweryfikowane liczbySPL pozostają relacją. |
| C18 PURIFI PTT10.0X04-NAB-01 | [RELACJE_UZYTKOWNIKOW_BRAK_PEWNOSCI_WERSJI](https://www.audiosciencereview.com/forum/index.php?threads/got-my-little-hands-on-the-purifi-10-s.54042/page-4) — Dyskusja właścicieliPurifi 10 obejmuje jakość średnicy i linkowane krzywe. Nie utożsamiono opinii o PTT10 ogólnie lubNAB-02 zNAB-01. Wyników>100 Hz nie przeniesiono na 20 Hz. |
| C19 Dayton RSS390HO-4 | [ODRZUCONY_INNY_MODEL_I_PRAWIDLOWY_PROJEKT](https://www.avsforum.com/threads/can-someone-help-me-with-a-box-for-a-dayton-15-rss390ho-4.3335548/) — Pierwszy wątek oHF odrzucono dlaHO. Odczytano osobny wątek RSS390HO-4 zposiadaczem planującym skrzynię. Brak potwierdzonego wyniku ukończonegoHO. Uwagi oil-can oHF nie są dowodem dlaHO. |
| C20 Dayton UMII12-22 seria | [MODELOWANIE_NIE_TEST_UMII](https://techtalk.parts-express.com/forum/tech-talk-forum/1505407-modeling-the-new-umii12-22) — Autor modeluje nowyUMII12. Starsze zwroty zpowodu rozrzutuT/S dotyczą poprzedniejgeneracjiUM. Nie przypisano problemów starychUM doUMII. WykresyBR ihipotezy dużejmocy nie są wynikami naszego sealed. |
| C21 Dayton UMII15-22 seria | [DZIENNIK_BUDOWY_BEZ_POTWIERDZONEJ_WALIDACJI](https://www.avforums.com/threads/2-x-sealed-dayton-audio-ultimax-2-umii15-22-15-build-thread.2523939/) — Booty 67 rozpoczyna projekt dwóchUMII15 sealedokoło 90L; w odczytanej części są decyzje i oczekiwanie na przetworniki. Tytułbuild thread nie dowodzi ukończenia aniTHD; nie przeanalizowano dalszychstron jako eksperymentu. |
| C22 Dayton RSS315HO-4 | [RELACJA_WLASCICIELA_BEZ_KONTROLI_ZMIENNYCH](https://techtalk.parts-express.com/forum/tech-talk-forum/1433658-my-upgrade-to-the-dayton-rss315ho-4-not-so-successful-need-ideas) — Autor opisuje niezadowolenie po zamianieDCS305 naRSS315HO w tej samej skrzyni i zmianie elektroniki. Brak wyrównania poziomów/pasma i kontroli napędu; określenia tight/slow nie są pomiarem transjentów aniTHD. |
| C23 Eminence LAB12 6ohm | [RELACJA_BUDOWY_Z_NEGATYWNYM_DALSZYM_CIAGIEM](https://www.diyaudio.com/community/threads/best-encl-volume-for-eminence-lab-12-in-a-sealed-sub.177283/) — Rewind opisuje LAB12 sealedokoło 36–39L, a później zgłaszaocieranie cewki. Nie wyznaczono przyczyny awarii, sygnału i wychylenia; nie jest to statystyka zawodności. Początkowej opinii pozytywnej nie odczytywać bez późniejszej korekty. |
| C24 Eminence LAB15 6ohm | [RELACJE_Z_INNEJ_TOPOLOGII](https://www.diyaudio.com/community/threads/eminence-lab15-sound-quality.333967/) — Dyskusja o LAB15;Zwiller opisuje własny przetwornik w konstrukcjiKeystone. Nie jest to kontrolowany test sealed 20 Hz. Ogólnych opinii oserii LAB12/15 nie przypisano jakoTHD konkretnej konfiguracji. |

Istotna uwaga dlaRSS390HF: w jednym wątku są zgłoszenie odgłosu oil-can
oraz relacja użytkownika bez tego objawu. Nie znamy częstości ani wspólnych
warunków. To hipoteza do sprawdzenia P12/P30, nie statystyka awarii.
Pozytywne opisyRSS390HE obejmują teżBR i wolne powietrze; nie są dowodem
osiągów sealed. Dla LAB12 uwzględniono dalszy wpis oocieraniu cewki po
początkowym zadowoleniu. Nietrafne ogłoszeniezakupuBMS i opis innego modelu
zostały odrzucone jako opinia o 15S430v2.

## Bramka profesjonalnego doboru

Każdy model musi przejść ślad wymagań:20–40 Hz, liniowość, napęd i ochrona,
korekcja, konstrukcja, możliwość późniejszego układu dwóch subwooferów
i niepewność. Nominalna granica ruchu nie zamyka tej bramki. Nadal potrzebne
są P06/P12–P17,P18–P25i P29, a nie wybór marki z jednej kolumny tabeli.

Nie wybrano jeszcze końcowego głośnika. Wybór ma być pojedynczy i uzasadniony
po integracji badań. Rodzaj kleju oraz kompletna konstrukcja są obowiązkowe P19/P20.
