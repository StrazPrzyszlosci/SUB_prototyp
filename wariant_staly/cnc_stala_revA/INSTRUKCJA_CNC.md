# S17. CYFROWY PROJEKT CNC - obudowa STALA 102 l, rewizja A0

Status projektu: W TRAKCIE OPRACOWYWANIA CAD/CNC. Nie jest to zatwierdzony pakiet CAM; pliki są rzeczywistymi wektorowymi obrysami DXF do uzgodnienia z wykonawcą, bez ścieżek narzędzia i kompensacji średnicy frezu.

## NOWA KOLEJNOŚĆ PRAC - DECYZJA INWESTORA 13.11.2026

Najpierw ukończyć całe cyfrowe opracowanie konstrukcyjne: komplet geometrii wszystkich części, rysunków produkcyjnych, CNC, połączeń, kaset, zabudowy, BOM i kontroli kolizji na danych producentów. Dopiero PO ukończeniu kompletnego projektu CNC wykonuje się prototyp. Pomiary rzeczywistych przetworników, próby wytrzymałościowe materiałów, klejów, połączeń i inne badania fizyczne są ETAPEM NASTĘPNYM i nie należy ich żądać ani planować jako działań poprzedzających ukończenie projektu CNC.

Nie mylić tej kolejności z gwarancją wykonania: bez kwalifikacji konkretnego materiału i urządzeń etap fizycznej produkcji zawsze wiąże się z ryzykiem, lecz projekt cyfrowy można i należy dokończyć wcześniej.

## Zakres obecnego generatora

Pliki w katalogu generated/ powstają komendą:

    python wariant_staly/cnc_stala_revA/generator.py --t 22.0 --out wariant_staly/cnc_stala_revA/generated
    python wariant_staly/cnc_stala_revA/sprawdz_s17.py

Kod oparty wyłącznie na standardowej bibliotece Python. Wygenerowane tekstowe DXF R12 są osobne dla każdej części, mają warstwy określające proces i nie są G-code. Wspólna baza frontu X prawo, Z góra; orientacja FR2 to powierzchnia STYKAJĄCA SIĘ z FR1; nie wolno jej lustrzanie odbijać względem FR1. Pozycja złącza na prawym boku opisana od przodu.

Wariant t=22.0:
- Zewnętrzny gabaryt W816,8 H473,3 D394,0 mm;
- FR1 i FR2 816,8 x 473,3, obie t22;
- TYŁ 816,8 x473,3 t22;
- BOK lewy/prawy 328,0x473,3 t22;
- DNO i GÓRA 772,8x328,0 t22;
- WRĘGA po uzgodnieniu pasowania 772,4 x 428,9 t22, okno 712,4 x 368,9 R3;
- RING stal Ø400/Ø358 x6, 8x M5 na PCD368, kołki K42;
- RAMKA zewnętrzna kasety MDF12 784x436, otwór 744x396, 4x M6;
- panel gniazda aluminium3 64x66, Ø24 i 4x3,4 w kwadracie 29,2;
- tuleje dystansowe metal 8 szt na parę, Ø16/Ø6,6 x24.

Powyższe pozycje MDF22 to razem 16 formatek na DWIE skrzynie, identyczne moduły bez ruchomej komory. Kasety, stal, terminal i dystanse są dodatkowe. Jeden komplet frontu ma 44 mm grubości. Nominalne netto około 102 l pozostaje celem bez regulacji.

## Poprawka nominalnego pasowania wręgi

S06 przewidywał 0,2 mm łącznego luzu, co groziło wciskaniem przy tolerancji grubości MDF. W generatorze wszystkie formatki boczne, dolne, górne i wręgi zależą od JEDNEJ ustawionej grubości nominalnej t. Wręga dostaje 0,4 mm ŁĄCZNEGO luzu wymiarowego, 0,2 mm po stronie przy nominalnym ustawieniu. Przy zmianie t w 21,7-22,3 mm geometria obudowy jest automatycznie przeliczana. Wykonawca może przyjąć jego grubość materiału w przygotowaniu CAM, bez wykonywania badan fizycznych; nie należy wykorzystywać zmian t jako ruchomego litrażu.

Samo przeliczenie wymiarów według jednej średniej grubości dostarczonej partii nie gwarantuje pasowania każdej indywidualnej płyty. Projekt produkcyjny musi rozwiązać również łańcuch tolerancji i wybrać system styku/połączeń. Wygenerowany DXF jest bazą CAD dla tego etapu.

## Źródła internetowe producentów

Dayton RSS390HF-4: https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf - Ø388,4, cutout Ø355,8, PCD Ø368, Ø6,5 w koszu, 178 głębokości. Nie utożsamiać otworów kosza z otworami w MDF.
EGGER Raw MDF Rec. 501 (odmiana referencyjna, nie zatwierdzenie zakupowe): https://www.egger.com/get_download/1850d441-43b8-4bb6-bc27-54822733e626/Technical_datasheet_E1_TSCA_ST_CE_TD-501_English.pdf?country=AZ - >19-30 mm tolerancja grubości ±0,3 mm; przed zakupem wybrać aktualny produkt dostawcy.
Neutrik NL4MPRXX: https://www.neutrik.com/media/14274/download/st-nl4mprxx.PDF?v=1 - Ø50,8, rozstaw29,2 ±0,1, zalecany otwór co najmniej Ø24, mocowanie co najmniej Ø3,2.
LAPP SKINTOP ST-M16x1,5 art.53111210: https://www.lapp.com/en_US/us/skintop-st-m/skintop-str-m/p/53111210 - zakres kabla 4-10 mm, gwint długości 8 mm. NIE umieszczać dławnicy w grubości MDF22. Aktualne rozwiązanie S18: otwór przez bok Ø30 oraz osobna szczelna metalowa podstawa AL3, w której dławnica ma otwór Ø16,5. Cztery inserty RAMPA M6x18 na zewnętrznym boku.
RAMPA SKD330 M6 art.420618001 do MDF22: https://www.rampa.com/media/e2/ed/d4/1699524202/RAMPA_Produktdatenblatt_MDF-EN.pdf - Ø12, długość18, otwór wstępny Ø10. 4 insert-y na moduł do przykręcenia kasety frontowej. Zakres nośności w konkretnym MDF pozostaje niezadeklarowany.
KLEIBERIT 303.0: https://www.kleiberit.com/fileadmin/Content_new/Produktinformationen/303.0/dbe3030_KSE.pdf - dane procesu, nie certyfikat wytrzymałości połączenia.
Stalowy pierścień Ø400/358x6 z K42 jest własnym założeniem konstrukcyjnym, nie fabrycznym produktem Daytona.

## Co jest ukończone, a co nadal trzeba WYPROJEKTOWAĆ przed zamknięciem CNC

Ukończone cyfrowo: spójna geometria płaskich formatek, strona obróbki FR1/FR2, otwory głośnika, pierścień do gwintowania, wręga, panel Neutrik, przepust w prawym boku, bazowa rama kasety i dystanse. Generator tworzy warstwy operacji, BOM/cutlist oraz testuje skrajne grubości 21,7, 22,0 i 22,3 mm.

DO OPRACOWANIA - WYŁĄCZNIE PROJEKTOWO, BEZ BADAŃ FIZYCZNYCH:
1. Doprecyzować spoiny i blokady panelu serwisowego M3 nowej metalowej osłony S18, jej gasket oraz odciążenie przewodu; zweryfikować modele STEP Neutrik i LAPP.
2. Ostateczne pasowania, tolerancje, spoiny, śruby, kołki pierścienia, zagłębienia pod łby i szczelność, sprawdzone w 3D na rysunkach producentów.
3. Dwa wykończenia frontu (tkanina i ochronna siatka) z mocowaniem, przepuszczalnością akustyczną oraz kompletną obwiednią wychylenia.
4. Podpory, zabezpieczenie przed przewróceniem przy pionowym obrocie i integracja z zabudową.
5. Pełny model 3D części metalowych i złożeń, kontrola kolizji w obu orientacjach oraz analiza wytrzymałościowa MES z przyjętymi wartościami producenta.
6. Rozkrój arkuszy MDF i metalu, promień naroży rzeczywistego frezu, CNC dogbones/tabs, CAM, kontrola poszczególnych łańcuchów wymiarów, dokumentacja końcowa.

Stan: PROJEKT CNC W TRAKCIE, nie komplet! Nie zastępować tych zadań rejestrem badań materiałowych do wykonania przed projektem.


## S18. Wymiarowana kaseta terminala - koncepcja metalowa, bez testu fizycznego

Poprzednia koncepcja S17 dławnicy w pocienionej ściance MDF zostaje WYCOFANA: 8 mm gwintu LAPP i niepewna tolerancja gniazda nakrętki tworzyły zbyt wąski łańcuch wymiarowy. Nowy projekt przenosi dławnicę na 3 mm metalową podstawę, która uszczelnia okno w korpusie.

- Osłona terminala zewnętrznie 70 mm od boku × 80 mm w głąb Y × 72 mm pionowo Z. Globalnie Y=270..350, oś Z=236,65.
- BOK_R: Ø30 przez MDF22 w Y330/Z236,65; 4 piloty Ø10 do głębokości18 od zewnątrz, Y282/338 i Z212,65/260,65. Inserty RAMPA SKD330 M6x18 art420618001.
- OBUDOWA_BAZA_AL3: 80×72, Ø16,5 dla LAPP ST-M16 (gwint8 mm) w Y330; 4×Ø6,6 pod wkręty M6. Podstawę oddzielić od MDF jednym ciągłym uszczelnieniem płaskim ~1mm, wymagana kompresja do ustalenia katalogowo.
- GNIAZDO_PANEL_AL3: 64×66 wewnątrz kasety 70×72. Neutrik ma cztery otwory Ø3,4 na kwadracie29,2, środkowy Ø24. Cztery kolejne Ø3,4 pozwalają wyjąć panel serwisowy M3. Nie przenosić deklaracji szczelności ze starego NL4MPR na NL4MPRXX.
- OBL: 6 oddzielnych formatek AL3 na JEDNĄ kasetę: podstawa80×72, ściana zewnętrzna80×72, panel frontowy64×66, tylny64×66, góra/dół64×74. Zaprojektowane na zewnętrzną obwiednię 70×80×72, ale spoiny, narożniki i małe bloki M3 muszą zostać doprojektowane cyfrowo. Szkice DXF nie są jeszcze gotowym rysunkiem spawalniczym.
- Koncepcja przewodu: Neutrik NL4MPRXX → przewody zabezpieczone izolacją, odciążone w osłonie → dławnica ST-M16 na płytce AL3 → Ø30 w MDF → głośnik, bez przejścia zasilania AC.

Bezpieczeństwo: metalowa kaseta musi wykluczyć zwarcie styków speakON i zapewnić serwis bez dotykania niezabezpieczonych części. Nie wyciągać gniazda pod obciążeniem. Potwierdzić wybrany przewód 4-10mm średnicy na podstawie karty przewodu, nie tylko oznaczenia 2x2,5 mm².

Zmieniono tylko cyfrowy projekt obudowy stałej. Nie zakładano żadnych prób fizycznych przed ukończeniem CNC.
