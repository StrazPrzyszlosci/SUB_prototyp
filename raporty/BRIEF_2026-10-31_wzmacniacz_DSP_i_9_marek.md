# Nowy brief klienta — RSS390HF-4 tylko jako faworyt wstępny; dziewięć nowych marek i aktywna elektronika

**Data aktualizacji: 31.10.2026. Status: nowy zakres i przeprowadzony etap weryfikacji źródeł/obliczeń przesiewowych. Nie ukończono ponownej pełnej kampanii badawczej wszystkich modeli ani kwalifikacji bezpieczeństwa.**

## 1. Zmiana celu, brak narzuconego zwycięzcy

Nowy brief klienta oznacza, że dotychczasowa C02 Dayton RSS390HF-4 jest **jednym z kandydatów**. Nie przepisujemy statusów C02/C11/C06 jako zatwierdzenia zakupowego.

Przestrzeń projektowa obejmuje odtąd **75, 80, 100, 120 i 150 l netto** (jako scenariusze, *nie* potwierdzone objętości konkretnej geometrii P20D). Limit głębokości obudowy z dotychczasowego projektu pozostaje **500 mm z wszystkimi wystającymi elementami**, do ponownego sprawdzenia dla każdej membrany/kosza. Projekt to **dwa subwoofery sterowane niezależnie**, centralny DSP o 8 wyjściach; 6 kanałów monitorów trójdrożnych + kanały 7/8 dla subwooferów.

Celem nie jest najniższe F3 kosztem wszystkiego. Zmiennymi oceny są: maksymalny czysty SPL, obwiednia X(f,V), THD/IMD i kompresja, termika/limity czasu, kompatybilność napięcia wejściowego, szum, bezpieczeństwo, gabaryt i koszt kompletnego zestawu na *dwa* kanały. **Nie przyjmować 300W lub 500W z samego napisu na przetworniku.**

## 2. Zamrożone źródła w repozytorium

Centralny plik [9 marek — zweryfikowane parametry techniczne](../dane/karty_producentow/2026-10-31_9_marek_weryfikacja.json) zawiera pierwotne nazwy, status źródła, adres producenta, adres oryginalnej karty PDF (gdy jest), przypisane wartości T/S z jednostkami, wymiary i dane montażowe, definicje mocy/wychylenia oraz uwagi do niejednoznaczności.

**Odtwarzanie:** [skrypt pobrania oryginalnych źródeł](../skrypty/odtworz_dokumentacje_producentow.py) tworzy lokalne pliki źródłowe i \`SOURCE_MANIFEST.json\` z SHA-256; [audyt spójności](../skrypty/audyt_danych_9_marek.py) przelicza Qts z Qes/Qms i kontroluje Mms/BL/Vd. Jeśli odnośnik przestanie działać, źródłem faktów liczbowych pozostaje utrwalony w Git plik JSON i historia zmian. **Oryginalnych kart objętych nieustalonym prawem redystrybucji nie dołączono jako PDF do repo.** Pełne wykresy impedancji/FRD i rysunki CAD nie są jeszcze replikowane jako dane numeryczne. Zatem **to nie jest jeszcze pełne archiwum binarne 1:1 dokumentów producentów**, choć numeryczne parametry, na których bazuje ten etap, są utrwalone.

Źródła pierwotne:
- Great Plains Audio, 416-8B — oficjalny [opis](https://greatplainsacoustics.com/products/416-8b-alnico-16-in-low-frecuency-loudspeaker-each) i [oryginalna karta producenta 2013](https://soundbox.co.jp/GPA/Classic-Series-416-8B-Spec-Sheet.pdf) hostowana przez dystrybutora. Stary link PDF na archiwalnej stronie GPA zwraca obecnie 404.
- [VOLT RV3863](https://voltloudspeakers.co.uk/speaker/rv3863-15inch/): pełna tabela producenta na stronie produktu, wartości 400W AES i ±7,5mm.
- [SUPRAVOX 400-2000 EXC](https://supravox.fr/en/products/copie-de-400-2000-exc-haut-parleur-de-grave): trzy oddzielne zestawy T/S dla 9/12/15V uzwojenia pola.
- [EMS B15EX](https://www.emspeaker.com/ems_products.html): strona firmowa potwierdza model i typ napędu, **nie zawiera wystarczających oficjalnych danych T/S**. Dane z innych baz nie mają statusu zweryfikowanych przez producenta; **status HOLD**.
- [PURIFI PTT10.0X04-NAB-01](https://purifi-audio.com/shop/ptt10-0x04-nab-01-ptt10-0x04-nab-01-2043): pełne oficjalne tabele. Zweryfikowano [oryginalną kartę PDF wersji **-01**, wyd. 0.95 (czerwiec 2024)](https://ptt.purifi-audio.com/shop/ptt10-0x04-nab-01-ptt10-0x04-nab-01-2043/document/583). Jej wartości mocy oznaczono **TBD**, więc wartości 450 W (long term maximum) oraz 135 W (100 h noise) pochodzą z **aktualnej strony produktu**, a nie ze starego PDF. Nie mylić liniowych ±14,75 mm z mechanicznymi ±25 mm.
- [Kartesian Wom265_vKi-6, datasheet v1.6](https://www.kartesian-acoustic.com/_files/ugd/f62092_f4db69c69657404f8edce8f61ada3010.pdf).
- [PHL 6301MNd, datasheet](https://www.phlaudio.com/fileadmin/user_upload/phl_audio/6301MNd_SpecSheet.pdf).
- [ETON Symphony II 12-212/C8/62](https://eton-hifi.com/en/products/symphony-ii-12-212-c8-62-hex) i [oryginalna karta PDF](https://www.eton-hifi.com/out/media/12_212_C8_62.pdf). ETON opisuje 92,7g jako Mmd, nie należy jej bez kontroli nazywać Mms.
- [Davis 39 GPA 15, karta producenta](https://davis-acoustics.com/wp-content/uploads/2024/04/39GPA15-OK_compressed.pdf). Skrót GPA w oznaczeniu modelu Davis nie jest marką Great Plains Audio.

### Szybka kontrola zdolności do najniższego basu

Poniżej \`Vd=Sd·Xmax\` (jeden kierunek) i przybliżone zamknięte Qtc,fc przy 75 l:

| Model | Vd [cm³] | Qtc 75 l | fc 75 l [Hz] | Ocena tej jednej bramki |
|---|---:|---:|---:|---|
| **Dayton RSS390HF-4 (brief)** | 1161 | 0,841 | 38,2 | Punkt odniesienia |
| **PHL 6301MNd** | 915 | 0,440 | 61,0 | Kandydat do dalszej kontroli, zwłaszcza mocy i DSP |
| VOLT RV3863 | 570 | 0,599 | 56,0 | Znacznie mniejszy zapas wychylenia |
| PURIFI PTT10.0X04 | 531 | 0,477 | 34,7 | Mniejsze Sd, wymaga odrębnej oceny SPL |
| ETON Symphony II 12-212 | 438 | 0,567 | 43,9 | Niższe Vd i nominalne 200W IEC |
| Kartesian Wom265 | 390 | 0,541 | 47,7 | Niższe Vd mimo dobrego jakościowo napędu |
| Davis 39 GPA 15 | 357 | 0,836 | 66,8 | Xmax tylko ±4mm |
| GPA 416-8B | 329 | 0,908 | 64,3 | Xmax ±4mm, 150W AES |
| SUPRAVOX 400-2000 EXC | brak zweryfikowanej jednostronnej definicji Xmax | 0,687* | 70,1 | *Przy zasilaniu elektromagnesu 12V; osobny zasilacz* |
| EMS B15EX | brak oficjalnych kompletnych T/S | — | — | **HOLD**, najpierw katalog/karta producenta |

Wzory \`Qtc=Qts sqrt(1+Vas/Vb)\`, \`fc=Fs sqrt(1+Vas/Vb)\`. **Nie są predykcją zmierzonego F3**, nie uwzględniają strat, rozkładu wypełnienia, parametrów rzeczywistych i nieliniowości. Porównanie samego Vd nie zastępuje rzeczywistego THD, mocy ani ceny. PHL AES 1300W nie należy stawiać na równi z Dayton RMS 500W bez znormalizowanego testu.

## 3. Elektronika: porównanie pięciu architektur i DSP

Konfiguracja [dane/konfiguracje/brief_klienta_20261031_wzmacniacz_dsp.json](../dane/konfiguracje/brief_klienta_20261031_wzmacniacz_dsp.json) zawiera producentów i definicje limitów testowych. Poniższe wyniki dotyczą wyłącznie **4Ω czystej rezystancji** i nominalnego fabrycznego wzmocnienia. Przy rzeczywistym \`Z(f)\`, pełnym ograniczeniu prądowym i nagrzewaniu dostępne poziomy mogą być inne.

| Architektura | Moc zadeklarowana przy 4Ω (warunki katalogowe) | Wzmocnienie | 1Vrms wej. | 2Vrms wej. | 4Vrms wej. |
|---|---:|---:|---:|---:|---:|
| ICEpower 300AS1, zasilacz na module | 300W przy 1% THD+N | 28,15dB | 163W | 300W† | 300W† |
| Hypex NC500MP, zasilacz na module | 500W | 25,5dB | 89W | **355W** | 500W† |
| Hypex NCx252MP (2×250W), wspólny SMPS | 250W / kanał | 25,5dB | 89W | 250W† | 250W† |
| Hypex NC252MP (2×250W), wspólny SMPS | 250W / kanał | 25,5dB | 89W | 250W† | 250W† |
| Hypex NC500 OEM + osobny SMPS | **nieokreślona konfiguracja** | — | — | — | — |

† Ograniczenie deklaracją mocy, nie bezpieczne napięcie przy dowolnym sygnale i czasie. Do rzeczywistego dopasowania modułu wymagane są aktualne pomiary przy 20–100Hz, zespolonym Z(f), pełnym czasie trwania i warunkach chłodzenia.

**Punkt przesterowania wejścia 4Ω:** ICEpower około 1,36 Vrms (dla jego 300W), NC500MP około 2,37 Vrms (dla 500W), NCx252MP/NC252MP około 1,68 Vrms (dla 250W). Wartości są **punktami nominalnego osiągnięcia mocy referencyjnej**, nie certyfikowanymi progami clip LED ani limiterów.

**miniDSP:** [Flex Eight](https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight/) ma 8 wyjść RCA maks. 2 Vrms, DSP 32/96kHz, cena producenta **549 USD**; [Flex HTx](https://www.minidsp.com/products/ht-series/flex-htx/) ma 8 kanałów wyjść RCA 2 Vrms i TRS symetryczne 4 Vrms, DSP 32/48kHz, cena producenta **949 USD**. Cena nie zawiera podatków i wysyłki. **HTx poprzez RCA nie podwyższa napięcia**; TRS 4V ma sens wyłącznie z poprawnym wejściem symetrycznym modułu. Połączenie balanced może poprawić odporność na zakłócenia i pętle mas, ale tylko przy rzeczywiście symetrycznych wejściach i prawidłowym prowadzeniu ekranów. Opcja Dirac zmienia dostępne funkcje i częstotliwość próbkowania Flex Eight, weryfikować przed zakupem.

**Nie można na tym etapie wskazać najtańszego kompletnego rozwiązania ani zwycięzcy koszt/SPL.** Wiemy o cenie samego ICEpower 300AS1 **88–176 USD w zależności od wariantu opakowania/sklepu producenta**, nie cenie kompletnej końcówki. Nie są zweryfikowane koszty modułów Hypex, obudowy/shieldingu, okablowania, chłodzenia, uziemienia, bezpieczników i montażu. Porażką metodologiczną byłoby przemnożenie cen PCB i nazwanie tego kompletą ofertą dla dwóch kanałów. Jednostka centralnego DSP jest wspólna dla wszystkich 8 głośników i jej koszt nie może być liczony jako dwa pełne, niezależne procesory.

## 4. Nowy test mechaniczny, cieplny i napięciowy dla Dayton

Wykonano **180 niezależnie przeliczonych świadków** (5 litraży×6 częstotliwości×2 budżety strat cewki 300/500W×3 hipotetyczne limity idealnej końcówki 300/400/500W). [Wyniki CSV](../wyniki/brief20261031_180_swiadkow_Dayton.csv), [założenia i 9 szczegółowych świadków](../wyniki/brief20261031_180_swiadkow_podsumowanie.json). Dodatkowy [skrypt Python](../skrypty/brief20261031_pomiarowe_bramki_i_porownanie.py) odtwarza szerszą kampanię T/S dla dotychczasowej puli i nowych źródeł. **Nie raportujemy wyników tego szerszego uruchomienia jako wykonanych, dopóki nie zostaną zweryfikowane jego pliki wynikowe.**

Kolejność weryfikacji:
\`I/U=1/[Re+jwLe+BL²/Zm]\`,
\`v/U=BL(I/U)/Zm\`,
\`Zm=Rms+jwMms+1/(jwCms)+Sd² rho c²/(jwVb)\`.
Na jednej częstotliwości i dla RMS \`X=|v|/w\`, \`Pcu=Re|I|²\`. Ogranicznikiem próbnym jest
\`Umax=min(Xmax/X_perV,sqrt(Pcu_scenariusz/Pcu_perV),sqrt(4 Pamp_4ohm))\`.

**To nie jest model narastania temperatury** ani wielotonowa bariera energii. Parametr 500W w członie strat cewki jest tylko scenariuszem, a nie zatwierdzonym ciągłym limitem temperatury. Zwiększenie mocy końcówki może zwiększyć SPL tylko, gdy aktualnie ogranicza napięcie/prąd wzmacniacza, a nie Xmax lub rzeczywisty limit termiczny.

Świadkowie przy *hipotetycznym* 500W limitu strat cewki i 500W/4Ω idealnej końcówki:

| Vb | f | Dominujące przyjęte ograniczenie | Zastosowane napięcie RMS | Modelowy poziom w półprzestrzeni, 1m |
|---|---:|---|---:|---:|
| 75l | 20Hz | limit napięcia wzmacniacza | 44,72V | 104,29dB |
| 75l | 40Hz | limit napięcia wzmacniacza | 44,72V | 114,16dB |
| 75l | 80Hz | limit napięcia wzmacniacza | 44,72V | 116,12dB |
| 80l | 20Hz | limit napięcia wzmacniacza | 44,72V | 104,60dB |
| 120l | 20Hz | **Xmax** | **38,40V** | 104,87dB |
| 120l | 80Hz | hipotetyczny limit cewki | 44,06V | 115,52dB |

Uwaga: 104–116dB to idealizowana liniowa **jednometrowa presja półprzestrzenna** z prędkości membrany. Nie uwzględnia emisji paneli, odpowiedzi pokoju, frontu, wzbudzania modów, kompresji, realnego zniekształcenia, szumu ani pełnego modelu prądowego DSP. Nie należy nazywać tego „maksymalnym czystym SPL”.

## 5. Schemat toru na jedną sztukę subwoofera

\`\`\`mermaid
flowchart LR
    S[WiiM Ultra / streamer z regulacją] --> DSP[centralny Flex Eight / HTx 8 kanałów]
    DSP -->|kanał 7 lub 8| EQ[PEQ i zwrotnica, HPF, opóźnienie, limiter programowy]
    EQ --> AMP[moduł klasy D: niezależny kanał]
    AMP --> MON[opcjonalny izolowany pomiar U i I]
    MON --> DRIVER[RSS390HF-4 albo kandydat po badaniach]
    U230[230V AC, PE, uziemiona osłona, EMC] --> PSU[certyfikowany zasilacz modułu/SMPS]
    PSU --> AMP
    MON -.-> EST[obserwator stanu i temperatury - badawczy]
    EST -.-> EQ
\`\`\`

Pozostałe kanały centralnego DSP: 1–6 — aktywne monitory, 7/8 — lewy/prawy subwoofer z **oddzielną ochroną i niezależnymi torami mocy**. Ochrona P25E nie może być uznana za dostępny, natywny algorytm miniDSP bez potwierdzenia interfejsu i czasu opóźnienia; przy braku takich możliwości wymagane może być osobne urządzenie nadzorujące. Wbudowane fabryczne OCP/OTP/DC chronią przede wszystkim elektronikę, a **nie wymuszają Xmax lub temperatury cewki**.

Dwie warstwy ochrony: (a) w DSP HPF, realistyczny limiter napięcia i filtracja impulsów; (b) niezależny model X(t), I(t), Re(T) oraz opcjonalne U/I na wyjściu, zależnie od możliwości sprzętu. Wszelkie wartości końcowe wymagają pomiarów. Nieznane Bl(x), Cms(x), Le(x), Rth/Cth i termistor/obserwator oznaczają, że finalny czasowy próg limiterów i THD/IMD **nie są określone**.

Moc sieciowa 230V: preferowane certyfikowane moduły z SMPS, bez samodzielnego przerabiania części pierwotnej. Wewnętrzną końcówkę PCB montować wyłącznie w bezpiecznie wydzielonym, zabezpieczonym i uziemionym przedziale zgodnie z dokumentacją producenta. To wymaganie dla konstrukcji finalnej, nie gotowy schemat elektryczny.

## 6. Dalsze bramki naukowe

1. Zweryfikować fabryczną specyfikację EMS B15EX u producenta oraz uzupełnić brakujące oryginalne charakterystyki FRD/ZMA, duże sygnały BL(x)/Cms(x)/Le(x) i kryteria mocy dla wszystkich dziewięciu marek. Nie nadawać niezweryfikowanej tabeli rangi źródła fabrycznego.
2. Rozszerzyć rzeczywistą siatkę porównawczą o 75–80l z dokładną geometrią P20D, także wypełnieniem i koszami. Sprawdzić możliwe bryły/wkłady przy limicie głębokości 500mm oraz Vb rzeczywistą.
3. Uruchomić i niezależnie skontrolować skrypt T/S dla **całej puli 26 + maksymalnie 9 nowych**, wraz z ograniczeniami kompatybilności; T/S nie generują bez dodatkowych pomiarów THD czy IMD.
4. Porównać stopnie Hypex/ICEpower z **rzeczywistą zespoloną impedancją** i limitem prądu, mocą ciągłą przy termice, napięciem wejścia i szumem. Zamówić pełne ceny BOM dla jednego/dwóch kanałów i osobno koszt centralnego DSP.
5. Wykonać pomiary Klippel lub równoważne na stanowisku: U/I/Z(f), T/S i Re(T), X(f), BL(x), Cms(x), zniekształcenia/intermodulacja, kompresja i czas nagrzewania. Bez nich **brak zatwierdzenia limiterów**.
6. Dokończyć P21G/P21H z przestrzennym gazem i drganiami ścian, powiązać z modelem termicznym i osłoną mechaniczną. Zaktualizować macierz decyzyjną P29 bez fikcyjnej pewności.

**Decyzja etapu:** zachować Dayton C02 jako *warunkowego faworyta*, wprowadzić PHL 6301MNd do poważnej próby porównawczej, pozostali nowi kandydaci wymagają analizy strat i użyteczności; żadnego nowego zwycięzcy ani wzmacniacza nie uznano za wybranego.
