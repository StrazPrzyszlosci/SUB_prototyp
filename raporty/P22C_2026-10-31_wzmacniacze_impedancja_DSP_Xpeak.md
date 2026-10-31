# P22C — rzeczywista impedancja małosygnałowa, gain DSP, prąd wzmacniacza i prawidłowe szczytowe Xmax

**31.10.2026 | wykonane 99 900 przypadków; niezależnie odtworzone w Pythonie.**
**To model 0D skrzyni zamkniętej dla sinusoid, nie wynik pomiaru, certyfikat ochrony ani zmierzony czysty SPL/THD.**

## Cel

Brief klienta nie zatwierdza przetwornika Dayton RSS390HF-4 ani wzmacniacza. Celem jest wyznaczenie, **czy ogranicza nas gain i napięcie DSP, dostępne napięcie końcówki, prąd, wychylenie szczytowe, czy modelowe straty miedziane cewki** na *tym samym częstotliwościowo zmiennym obciążeniu*. Porównujemy cztery gotowe moduły i trzy ścieżki sygnału. Oddzielamy krótkotrwałą moc deklarowaną przez producenta od mocy ciągłej.

**Błąd poprzednich obliczeń:** w oryginalnych 180 i 274 725 obliczeniach z briefu porównano wychylenie **RMS** z katalogowym **jednostronnym szczytowym** Xmax. Poprawne kryterium dla sinusoidy: \`X_peak=sqrt(2)*|v_RMS|/omega <= Xmax\`. Dotychczasowe limitujące amplitudy były zawyżone \`sqrt(2)\`, a poziom w części mechanicznie ograniczanej mógł być zawyżony o **3,0103 dB**. Zaktualizowano dane źródłowe [180 przypadków](../wyniki/brief20261031_180_swiadkow_Dayton.csv) i [274725 przypadków](../wyniki/brief20261031_pelna_pula_35_wstepna_analiza.json) oraz skrypt pierwotnego przesiewu. Historyczne wyniki w commitach pozostają widoczne, lecz nie powinny być używane.

## Model i ściśle określone jednostki

Dla \`s=j*2*pi*f\`, liniowych producentowych T/S, idealnie zamkniętej obudowy \`Vb\` oraz efektywnego wyjściowego \`Rs\` wzmacniacza:

\`Zm = Rms + s*Mms + 1/(s*Cms) + Sd^2 * rho*c^2/(s*Vb)\` [N s/m].

\`Zterminal(f)=Re+s*Le+BL²/Zm\` [Ω] — **zespolona impedancja** widziana na zaciskach głośnika, nie rezystor 4Ω.

\`I/U_source=1/[Zterminal + Rs]\` [A/V], \`v/U_source = BL*(I/U_source)/Zm\` [m/(s V)].

Dla 1 V skutecznego sinusa \`Xpk/U=sqrt(2)*|v/U|/omega\`.
Dla próby każdej konfiguracji \`Umax=min(...)\` z sześciu źródeł:

1. \`U_DSP=Vin_max * 10^(gain_dB/20)\`; źródło sygnału 2 lub 4 Vrms.
2. \`U_P4=sqrt(4Ω * P4_1kHz_1%THD)\` — **napięcie referencyjne rezystora 4Ω, nie moc rzeczywista na Z(f) ani moc ciągła**.
3. \`U_vpk=Vout_peak/sqrt(2)\`, gdy producent podał szczyt napięcia.
4. \`U_ipk=Iout_peak/(sqrt(2)*|I/U_source|)\` — jawna granica prądu szczytowego dla sinusa.
5. \`U_X = Xmax / (sqrt(2)*|v/U_source|/omega)\`.
6. \`U_cu = sqrt(Pcu_scen/(Re*|I/U_source|²))\` przy **hipotetycznych** budżetach \`Pcu=100/250/500 W\`, nie ograniczeniach termicznych zatwierdzonych przez producenta.

W modelu bez strat wewnętrznych gazu testujemy \`Re(U_source*conj(I)) = (Re+Rs)*|I|² + Rms*|v|²\`, przy 1V RMS. Porównywanie \`Pcu\` dla osobnych sinusów nie stanowi modelu nagrzewania przy muzyce, a samo \`I\` jest tutaj prądem cewki, nie poborem z sieci ani z szyny zasilania SMPS.

Modelowy \`SPL_2pi(1m)=20 log10(rho*omega*Sd*|v|/(2*pi*1m*20µPa))\` to **idealizowane, liniowe ciśnienie w półprzestrzeni**, bez geometrii frontu, pomieszczenia, emisji ścian, efektywnej korekcji DSP, THD, kompresji oraz promieniowania nieliniowego. Dane znamionowe głośników o różnych impedancjach są obciążane hipotetycznym **limitem napięcia zaczerpniętym z mocy przy 4Ω**, zatem *nie przewiduje to rzeczywistej mocy końcówek przy obciążeniu 6/8Ω lub 1,5Ω*. Nie przypisywać modelowi dokładności instrukcji wzmacniacza.

## Modele i źródła

Przetworniki:
- C02 [Dayton RSS390HF-4](https://daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm), z parametrami briefu: \`Mms=306g, BL=15Tm, Xmax=14mm peak\`;
- C11 Dayton RSS390HE-22 seria oraz C06 STX W.32.800.8.FCX (historyczna, zamrożona tabela T/S);
- N07 [PHL 6301MNd](https://www.phlaudio.com/fileadmin/user_upload/phl_audio/6301MNd_SpecSheet.pdf) i N05 [PURIFI PTT10.0X04-NAB-01](https://purifi-audio.com/shop/ptt10-0x04-nab-01-ptt10-0x04-nab-01-2043). Dla PHL i PURIFI katalogowe Le jest opisane dla 1kHz; stałe Le w całym paśmie to jawne przybliżenie.

Wzmacniacze i ich ograniczenia (dane producentów):
 
| Końcówka | P deklarowana 4Ω, 1 kHz/1% | Fabryczne gain | Maks. I szczyt | Maks. U szczyt | Moc ciągła 25°C producenta |
|---|---:|---:|---:|---:|---:|
| [ICEpower 300AS1](https://shop.icepoweraudio.com/product/300as1/) | 300 W | 28,15 dB | 20 A | 50 V | **Nie wpisano** nieporównywalnego parametru |
| [Hypex NC500MP](https://www.hypex.nl/media/64/53/92/1646059344/NC500_OEM_02xx_R11.pdf) | 500 W | 25,5 dB | 27 A | niepodany | **100 W** |
| [Hypex NCx252MP](https://www.hypex.nl/media/86/f4/49/1752661533/Hypex_NCx252MP_Datasheet_01xx_R03.pdf), kanał | 250 W | 25,5 dB | 17,5 A | niepodany | **50 W/kanał** |
| [Hypex NC252MP](https://www.hypex.nl/media/7f/85/fa/1708610358/NC252MP_04xx_R14.pdf), kanał | 250 W | 25,5 dB | 17,5 A | niepodany | **50 W/kanał** |

Dla wzmacniaczy Hypex moc 1kHz/1% to **maksymalna wartość czasowo ograniczona**, a ciągłe 100/50 W przy 25°C odnoszą się do osobnego testu producenta. Nie użyto 100/50W jako sztywnego dodatkowego limitu napięciowego przy każdej częstotliwości, ponieważ bez termicznego modelu czasu sygnału byłoby to sztuczne obcięcie. W raporcie nie ma błędnej deklaracji „500 W ciągłej” dla NC500MP.

DSP: [miniDSP Flex Eight](https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight) RCA 2Vrms; [miniDSP Flex HTx](https://www.minidsp.com/products/ht-series/flex-htx) RCA 2Vrms lub TRS symetryczne 4Vrms. Połączenie RCA HTx nie ma przewagi gain nad Flex Eight. Fabryczny kompresor nie jest dowodem ochrony X(t) lub temperatury cewki.

## Kampania i niezależny test

**99 900 obliczeń**: 5 przetworników × 5 objętości (75/80/100/120/150l) × 111 częstotliwości 10..120Hz × 4 wzmacniacze × 3 drogi sygnału DSP × 3 scenariusze strat miedzianych. **900 grup** wynikowych z liczebnościami aktywnych ograniczeń oraz świadkami 20,40,80Hz.

Program testowy wykonał weryfikację energii dla każdej sinusoidy; maksimum względnej reszty **7,99e-16**. Całość **niezależnie odtworzono w Pythonie** (druga implementacja obliczeń zespolonych, ta sama zamrożona parametryzacja), ponownie 99 900 punktów, maksymalna względna reszta **7,97e-16** i brak przypadków przekroczenia Xmax/Ipeak/przyjętego Pcu po zadziałaniu obwiedni. Na wybranych świadkach wyniki obu implementacji zgadzają się do prezentowanych 5 miejsc po przecinku.

Dane [900 grup, podsumowanie](../wyniki/p22c_napiecie_prad_wychylenie_analiza.json), [36 wybranych świadków](../wyniki/p22c_swiadkowie_36.csv), [przygotowany skrypt odtworzenia 99 900 próbek](../skrypty/p22c_naped_dsp_zespolona_impedancja.py), [konfiguracja ze źródłami](../dane/konfiguracje/p22c_dsp_naped_impedancja_20261031.json). Pełny zbiór CSV 99 900 wierszy udostępniono jako osobne archiwum z bieżącego przebiegu; skrypt w repo generuje \`wyniki/p22c_pelna_kampania.csv.gz\`, kompletny JSON i manifest SHA256 po uruchomieniu. Nie przedstawiono pełnego 100 000-wierszowego CSV jako bezpośrednio zapisanego w Git, ponieważ w PR umieszczono agregaty i kod.

### Kluczowy świadek: C02, 80 l, scenariusz Pcu ≤250 W

| Wariant | 20 Hz: U [Vrms] / SPL model | 40 Hz: U / SPL model | 80 Hz: U / SPL model |
|---|---|---|---|
| ICEpower 300AS1 + RCA 2V | 32,63 / 101,86 dB | 34,64 / 111,93 dB | 31,80 / 113,06 dB |
| NC500MP + Flex Eight RCA 2V | 32,61 / 101,86 dB | 37,67 / 112,66 dB | 31,77 / 113,06 dB |
| NC500MP + Flex HTx TRS 4V | 32,61 / 101,86 dB | 43,47 / 113,90 dB | 31,77 / 113,06 dB |

**Zysk HTx TRS 4V względem 2V RCA przy 40 Hz w tym scenariuszu: +1,244 dB** idealizowanego poziomu, nie rzeczywistego czystego SPL. Przy 20 Hz obie konfiguracje kończą na Xmax, a przy 80 Hz na **hipotetycznym** budżecie strat cewki: wzrost gain nie poprawia limitu. Samą różnicą 1,244 dB nie można uzasadnić ceny ani kupna droższego DSP; wbudowane symetryczne tory mogą dodatkowo poprawiać odporność na zakłócenia i wymagają właściwego złącza.

![P22C: warunkowa obwiednia 80 l wzmacniacza i DSP przy ograniczeniu Xmax](../wyniki/107_P22C_wzmacniacz_DSP_Xmax.svg)

Ważna uwaga przy 100% głośności streamera: \`NC500MP\` osiąga nominalne \`500W/4Ω\` przy ok. **2,374 Vrms** wejściowego sygnału dla fabrycznych 25,5dB. HTx TRS 4V potrafi teoretycznie przekroczyć to wejściowe wymaganie, dlatego **musi mieć ustalony gain structure/trim i zabezpieczenie przed przesterowaniem**, a nie zostać podłączony z założeniem, że „4V zawsze lepsze”. Wprowadzenie trimu nie jest testem zabezpieczeń sprzętu.

## Co badanie realnie rozstrzyga i co pozostaje otwarte

1. **Katalogowe jednostronne Xmax w sinusie musi porównywać się ze szczytem, nie RMS.** Błąd w starych raportach obniżał wiarygodność całego P29; wykonano korektę 180 i 274725 danych.
2. **Wydajność końcówki musi być oceniana przy rzeczywistym Z(f)**, z osobnym ograniczeniem prądu, napięcia i gain DSP. Same \`sqrt(P*4Ω)\` są tylko uproszczonymi limitami porównawczymi, a nie zastępują krzywych wydajności producenta przy konkretnym f i temperaturze.
3. Przy 80l/20Hz C02 jest w badanym modelu **mechanicznie ograniczony** już przy ok. 32,6 Vrms, podczas gdy 300AS1 i NC500MP mają wystarczający nominalny zapas napięcia. W innym paśmie odpowiedź może być ograniczona napięciem lub hipotetyczną termiką. To nie zmienia wyboru przetwornika.
4. **Nie znamy** rzeczywistych nieliniowych \`BL(x)\`, \`Cms(x)\`, \`Le(x,f)\`, \`Re(T)\`, \`Rth/Cth\`, czasowej zależności prądowego ograniczenia modułu i rzeczywistej objętości/wypełnienia/kosza. Brak THD/IMD, SPL w pokoju, długich multitonów i certyfikacji limiterów. Żadnych wartości z raportu **nie wolno wpisać jako końcowych progów ochrony**.
5. Kolejna bramka to czasowe zestawienie P25E z *prawdziwym* sprzętem miniDSP i ciągłym pomiarem U/I oraz test na obudowie P21G. Wcześniej potrzebne są testy oscyloskopem/analizatorem prądowym i pomiary temperatury/wychylenia.
