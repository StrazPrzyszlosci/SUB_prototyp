# S11. Katalog producentow i granice przenoszenia danych do stalej komory 102 l
Data audytu: 12.11.2026. Status: dane zewnetrzne, NIE weryfikacja probki, bez zatwierdzenia CNC. Dane do odtworzenia: s11_parametry_zrodel.json.

## 1. RSS390HF-4
Pierwotna karta Daytona nr 295-468: srednica zewnetrzna 388,4 mm; cutout 355,8 mm; PCD 368 mm, 8 otworow 6,5 mm w koszu; glebokosc 178 mm; kolnierz 10,5 mm. T/S: Fs 19,5 Hz; Qts 0,43; Vas 212 l; Re 3 Ω; Le 0,92 mH/1 kHz; Sd 829,6 cm2; Xmax jednostronne 14 mm. Masa katalogowa 30 lbs pochodzi ze strony producenta i wymaga weryfikacji masy konkretnego egzemplarza.

Zrodla:
- https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf
- https://daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm

Brakujace dane: pelna trasa wlozenia realnego kosza z zaciskami i przewodem; wypornosc kosza; BL(x), Cms(x), Le(x), rzeczywista termika i THD/IMD. Nie zastapiono ich przyblizonym walcem Ø355,8 z S10. Otwory Ø6,5 fabrycznego kosza NIE sa otworami projektowymi w MDF.

## 2. MDF 22 mm, EGGER ST Rec. 521
Zindeksowana karta producenta EGGER Raw MDF ST E1 TSCA ELS Rec. 521 dla >19-30 mm podaje srednia (nie charakterystyczna!) wartosc E w zginaniu 2100 N/mm2, srednia wytrzymalosc na zginanie 18 N/mm2, internal bond 0,55 N/mm2, tolerancje grubosci plyty >19 mm ±0,3 mm. Gęstosc oznaczona jako zalezna od zakladu produkcji. Dane dotycza okreslonego gatunku, NIE dowolnego MDF o grubosci 22 mm. W czasie audytu bezposrednie pobranie pdf zwracalo 404, chociaz tresc karty producenta byla indeksowana; wymagany swiezy oryginal od dostawcy przed decyzja o zakupie.

Zrodlo:
- https://www.egger.com/get_download/ddc06952-07b2-4139-9292-d51a6087f1a9/Technical_datasheet_ST_E1_TSCA_Pine_TD-521_English.pdf

S02 i S03 zakladaly E = 2000 MPa i gęstosc = 800 kg/m3. Nie podmieniac tych zalozen po prostu na tablice 2100 MPa, bo 2100 to wartosc srednia innego, niezakupionego produktu. Zrobiono tylko wražliwosc porownawcza S13.

## 3. Neutrik NL4MPRXX i NL4FXX-W-S
Rysunek fabryczny gniazda: srednica kola kolnierza 50,8 mm, rozstaw otworow 29,2±0,1 mm w kwadracie, panel cutout >=24 mm, otwory mocowania >=3,2 mm. Gniazdo deklaruje 25 A RMS ciagle dla pojedynczego styku. Wtyk NL4FXX-W-S ma obejme przewodu Ø6-12 mm i akceptowany przekroj zyly 1,5-4 mm2. Gniazdo i kabel same nie gwarantuja szczelnosci przepustu przez obudowe. Stary NL4MPR z deklaracja 'airtight' jest innym modelem; nie przenosic tej deklaracji na NL4MPRXX.

Zrodla:
- https://www.neutrik.com/media/14274/download/st-nl4mprxx.PDF?v=1
- https://www.neutrik.com/en/product/nl4mprxx
- https://www.neutrik.com/en/product/nl4fxx-w-s

## 4. Kleiberit 303.0
Karta: PVAc D3, D4 po dodaniu 5% 303.5; 6-10 min czasu otwartego w 20 C; od 15 min prasowania dla polaczen w 20 C; koncowe wlasciwosci D3/D4 po 7 dniach; dla klejenia POWIERZCHNIOWEGO orientacyjne 100-130 g/m2, dla drewna litego 150-200 g/m2. 0,7-1 N/mm2 opisuje klejenie lameli/drewna, nie udowodniony docisk dla calego laminatu MDF z uwięzionym stalowym pierscieniem. Przestrzegac karty SDS.

Zrodlo:
- https://kleiberit.com/fileadmin/Content_new/Infoblaetter/englisch/303_D3_Leim_GBUS.pdf

## 5. miniDSP i ICEpower
miniDSP Flex Eight (analog RCA): 2 kanaly wejsciowe, 8 wyjsc analogowych RCA niesymetrycznych, maksymalnie 2 Vrms. Uwaga: Flex Eight NIE jest Flex/Balanced ani Flex HTx. ICEpower 300AS1 jest KANDYDATEM do weryfikacji, ze zbalansowanym wejsciem, nominalnym gain 28,15 dB (28,0-28,3), typowym limitem wyjscia 50 Vpeak i 20 Apeak. Parametry te nie kwalifikuja ukladu po podlaczeniu. S14 prowadzi analize dopasowania.

Zrodla:
- https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight
- https://docs.minidsp.com/product-manuals/flex-eight/signal-flow/index.html
- https://shop.icepoweraudio.com/wp-content/uploads/2023/02/ICEpower300AS1_Datasheet_2_2.pdf

## Zasada dowodowa
Zrodla katalogowe sluza porownaniu i zakresom do prob. NIE wpisywac nieznanych cech jako zmierzone; przy braku danych w s11_parametry_zrodel.json pozostawic null i zachowac HOLD. Zdjecia oraz dokumentacja PDF pozostaja na serwerach producentow, bez kopiowania do repo. Historycznego README nie modyfikowano.
