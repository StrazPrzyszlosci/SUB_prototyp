# Raport 056 — macierz luk, audyt pochodzenia i bramki badań

Stan wejściowy: `main` po PR #3, commit `4d79871616ca1fd37a4b12c07de2c3febdb8e054`, 2026-10-30.
Ten raport jest audytem stanu zastanego i zależności. Nie przypisuje wyników przyszłym etapom 057/058, nie jest replikacją dawnych symulacji ani walidacją urządzenia.

## Wynik audytu i decyzja

**Najważniejsza luka jest konstrukcyjna:** model docelowy musi zastąpić zbiorczą rezerwę 8 l, połączyć wręgi i tory wkładów oraz zmieścić cały przedmiot w 500 mm. Dotychczasowe wyniki frontu utwierdzonego i pustych korytarzy montażu nie dowodzą sztywności ani serwisowalności złożonej skrzyni. Następna zależność to port gaz–panele–napęd, potem ochrona czasowa. Badania sygnałów w modelu zredukowanym mogą iść niezależnie, ale nie zamykają integracji przestrzennej.

C02 RSS390HF-4 pozostaje **warunkowym faworytem**, nie udowodnionym zwycięzcą. C11 RSS390HE-22 i C06 STX W.32.800.8.FCX muszą pozostać w porównaniu. Granica 86,813 W z raportu 055 jest granicą scenariusza wspólnego Pcu, a nie zmierzonym chłodzeniem lub dopuszczalną mocą. Próg 0,2 dB nie uzasadnia minimalnych 120 l: poprzednia siatka dawała 100 l, późniejsza 99 l. 120 l jest punktem eksperymentu.

Audyt `skrypty/audyt_manifestow_P30B.py` odczytał bajty **niezmiennego commitu**, a nie ruchomego drzewa roboczego. Sprawdzono 24 manifesty, 3288 odwołań do hashów i 2182 różne ścieżki: **3185 zgodnych, 103 różnych, zero brakujących**. 417/417 wpisów importu jest zgodnych z Git blob SHA-1; manifest rekomendacji P29 ma 338/338 zgodnych SHA-256. 103 odwołania nie oznaczają 103 różnych plików. Różnice dotyczą historycznych dokumentów, indeksów i kodu orkiestracji/postprocessingu; żadna nie wskazuje pliku pod `wyniki/`. Stare manifesty zachowano. Sama różnica nie dowodzi uszkodzenia, ale historycznej wersji nie wolno odtwarzać aktualnym kodem bez ustalenia jej rewizji.

103 różne odwołania dotyczą 21 różnych ścieżek. Dodatkowo trzy reprezentatywne wyliczenia Git blob SHA-1 porównano z identyfikatorami obiektów odczytanymi bezpośrednio z drzewa commitu (brief, wynik P29C i skrypt P29C); wszystkie zgodne. To kontrola metody haszowania, nie nowa weryfikacja fizyczna.

Pełne rekordy: [audyt](../wyniki/p30_audyt_manifestow.json), [wszystkie porównania](../wyniki/p30_audyt_referencje.json). Hashe dowodzą zgodności bajtów, nie poprawności fizyki, źródła pojedynczej tezy ani niezależnej recenzji.

## Macierz P01–P30

Każdy wiersz jest **częściowy na poziomie całego pakietu**. Kolumna zakresu wymienia wykonane rodziny, których nie należy powtarzać bez nowej przesłanki. Brak pomiarów nie unieważnia własności matematycznych tych rodzin. Pozostają jednak także konkretne zadania komputerowe, więc nie ma podstaw do ogłoszenia zakończenia prac bez sprzętu. Priorytet 1: konstrukcja/ochrona/integralność; 2: synteza po geometrii; 3: uzupełnienie śladu źródłowego.

### P01 — Literatura i rejestr twierdzeń

**Wykonany zakres:** Zebrane katalogi i rejestr źródeł, bez pełnego audytu każdej tezy. Dowody: [003](../raporty/003_referencje_i_rynek.md); [010](../raporty/010_szeroka_pula_i_kwalifikacja.md); [038](../raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md); [054](../raporty/054_rekomendowana_konfiguracja_prototypu.md).

**Pozostaje komputerowo:** Uzupełnić źródłowe uzasadnienie nowych praw materiałowych i rejestr twierdzenie–dowód. **Brakujące dane/pomiar:** Brakujące dane producentów i źródłowe krzywe.

**Kryterium zaliczenia dalszego zakresu:** Każdy parametr ma źródło, jednostkę, datę albo jawny przedział założenia. Zależności: P30; priorytet 3.

### P02 — Wymagania i hipotezy

**Wykonany zakres:** Brief i późniejsze U-021/U-026; referencje Sub12/Sub15. Dowody: [003](../raporty/003_referencje_i_rynek.md); [054](../raporty/054_rekomendowana_konfiguracja_prototypu.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Przełożyć ograniczenia na warunki odbioru i oddzielić robocze progi od wymagań. **Brakujące dane/pomiar:** Akceptacja progów użytkowych; brak porównywalnych pasmowych danych referencji.

**Kryterium zaliczenia dalszego zakresu:** Nie przedstawiać umownego 0,2 dB lub 50 W jako zatwierdzonego wymagania. Zależności: P01; priorytet 2.

### P03 — T/S, Xmax, korelacje, identyfikowalność

**Wykonany zakres:** 26 produktów/27 konfiguracji; T/S i analiza identyfikowalności. Dowody: [010](../raporty/010_szeroka_pula_i_kwalifikacja.md); [012](../raporty/012_identyfikowalnosc_i_dane_publikowane.md); [038](../raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md).

**Pozostaje komputerowo:** Identyfikowalność po dołączeniu podatnych paneli i strat maty; jawne konwencje Mms/Mmd. **Brakujące dane/pomiar:** T/S egzemplarzy, wyporność kosza, tolerancje; osobne Mmd lub spójna identyfikacja obciążenia.

**Kryterium zaliczenia dalszego zakresu:** Nie dublować masy powietrza; wskazać parametry nierozdzielalne na podstawie Z(f). Zależności: P20, P21; priorytet 1.

### P04 — Formalne równania i granice

**Wykonany zakres:** Równania rodzin, pasywność, granice i bilanse. Dowody: [009](../raporty/009_N7_straty_nieszczelnosci.md); [017](../raporty/017_promieniowanie_i_sprzezenie_pokoju.md); [020](../raporty/020_nieliniowy_naped_i_sprzezony_gaz.md); [021](../raporty/021_pamiec_cewki_i_definicja_Lgen.md).

**Pozostaje komputerowo:** Wyprowadzić wspólny port mechanika–gaz–napęd dla nowej geometrii. **Brakujące dane/pomiar:** Parametry zamknięcia fizycznego modelu.

**Kryterium zaliczenia dalszego zakresu:** Bilans mocy/energii oraz poprawne granice po usunięciu sprzężeń. Zależności: P18, P20, P21; priorytet 1.

### P05 — Niezależna replikacja

**Wykonany zakres:** Kontrole analityczne, odrębne równania, FV i ODE w opisanych rodzinach. Dowody: [009](../raporty/009_N7_straty_nieszczelnosci.md); [011](../raporty/011_granice_globalne_litrazu.md); [017](../raporty/017_promieniowanie_i_sprzezenie_pokoju.md); [052](../raporty/052_komora_warstwy_wklady_i_front.md).

**Pozostaje komputerowo:** Niezależna dyskretyzacja co najmniej istotnych świadków nowego modelu. **Brakujące dane/pomiar:** Walidacja pomiarowa osobno.

**Kryterium zaliczenia dalszego zakresu:** Zgodność metod i oszacowanie błędu w zadanej dziedzinie; nie samo porównanie funkcji. Zależności: P04, P21, P24; priorytet 1.

### P06 — Niepewność globalna i odporność wyboru

**Wykonany zakres:** Rodziny D/L i stres finalistów wykonane w ograniczonej dziedzinie. Dowody: [015](../raporty/015_niepewnosc_globalna_i_odpornosc.md); [053](../raporty/053_porownanie_i_odpornosc_rekomendacji.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Wspólna niepewność konstrukcji, termiki i ochrony; niezależne perturbacje kandydatów. **Brakujące dane/pomiar:** Rozrzut produkcyjny, korelacje parametrów.

**Kryterium zaliczenia dalszego zakresu:** Pokazać zmianę decyzji i kontrprzykłady; częstości próby nie są prawdopodobieństwem jakości. Zależności: P03, P18, P24; priorytet 2.

### P07 — Ciągła objętość

**Wykonany zakres:** Analityczne granice sinusów; siatka C02 70–160 l i korekta 99 l. Dowody: [011](../raporty/011_granice_globalne_litrazu.md); [028](../raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Ponowna ocena rzeczywistego netto i skoków regulacji, bez ogłaszania optimum ciągłego. **Brakujące dane/pomiar:** Rzeczywiste wyporności i objętości.

**Kryterium zaliczenia dalszego zakresu:** Próg odnoszony do określonego zbioru, modelu i metryki; wyjaśnić 120 l jako punkt eksperymentu. Zależności: P20, P29; priorytet 2.

### P08 — N7 — przecieki i straty

**Wykonany zakres:** Cab równolegle z Ra i rodziny przecieków. Dowody: [009](../raporty/009_N7_straty_nieszczelnosci.md); [042](../raporty/042_regulacja_Vb_i_wklady_wypornosciowe.md); [043](../raporty/043_przegroda_dwie_komory_i_materialy.md).

**Pozostaje komputerowo:** Zastosować zakres przecieku do nowych mocowań i regulatora, ocenić wpływ na ochronę. **Brakujące dane/pomiar:** Szczelność rzeczywistej skrzyni i modułów.

**Kryterium zaliczenia dalszego zakresu:** Wyprowadzić wymagany Ra lub dopuszczalny przeciek dla jawnej straty odpowiedzi. Zależności: P20, P21; priorytet 2.

### P09 — Wypełnienie, lepkość i straty cieplne gazu

**Wykonany zakres:** Rodziny porów; warstwy i przestrzenne wkłady bez pełnego kosza/wręg. Dowody: [016](../raporty/016_gaz_wypelnienie_i_granice.md); [039](../raporty/039_wypelnienie_ilosc_polozenie_i_straty.md); [052](../raporty/052_komora_warstwy_wklady_i_front.md).

**Pozostaje komputerowo:** Przeliczyć wspólną geometrię maty, wręg i regulatora, nie bonus litrów. **Brakujące dane/pomiar:** Masa, porowatość i opór przepływu wybranego poliestru.

**Kryterium zaliczenia dalszego zakresu:** Bilans litej części i gazu; zbieżny port, zakres materiałowy i test granic. Zależności: P20, P21; priorytet 1.

### P10 — Adiabatyczne/izotermiczne powietrze

**Wykonany zakres:** Rodziny gazu idealnego i nieliniowej wymiany ciepła. Dowody: [016](../raporty/016_gaz_wypelnienie_i_granice.md); [020](../raporty/020_nieliniowy_naped_i_sprzezony_gaz.md).

**Pozostaje komputerowo:** Włączyć właściwą termikę przestrzennego gazu do końcowego zakresu lub ilościowo ograniczyć pominięcie. **Brakujące dane/pomiar:** Współczynniki wymiany ciepła urządzenia.

**Kryterium zaliczenia dalszego zakresu:** Poprawne granice izotermiczna/adiabatyczna i rozdzielenie temperatury początkowej od ogrzewania masy. Zależności: P09, P21; priorytet 2.

### P11 — Obciążenie promieniowaniem i granice przestrzeni

**Wykonany zakres:** Kontrolne Rayleigh/czasza/pokój; konwencje masy, nie identyfikacja Mmd. Dowody: [017](../raporty/017_promieniowanie_i_sprzezenie_pokoju.md); [051](../raporty/051_P21C1_membrana_kolowa_i_bezwladnosc.md); [052](../raporty/052_komora_warstwy_wklady_i_front.md).

**Pozostaje komputerowo:** Skończony front i wzajemne obciążenie dwóch nowych skrzyń albo uzasadniona obwiednia błędu. **Brakujące dane/pomiar:** Mmd i promieniowanie rzeczywistej membrany.

**Kryterium zaliczenia dalszego zakresu:** Nie dodawać pełnej masy promieniowania do katalogowego Mms; energia portu Re(p v*). Zależności: P03, P20, P21; priorytet 2.

### P12 — BL(x),Cms(x),Le(x,i),Rms(v)

**Wykonany zakres:** Warunkowe BL(x),Cms(x),Le i pamięć cewki. Dowody: [020](../raporty/020_nieliniowy_naped_i_sprzezony_gaz.md); [021](../raporty/021_pamiec_cewki_i_definicja_Lgen.md).

**Pozostaje komputerowo:** Włączyć istotne niepewne nieliniowości finalistów do badania ochrony. **Brakujące dane/pomiar:** Krzywe BL(x,T),Cms(x),Ld(x,i),Rms(v) konkretnych egzemplarzy.

**Kryterium zaliczenia dalszego zakresu:** Wzajemne BL siła/SEM; dodatnia energia, jawna dziedzina modelu. Zależności: P03, P24; priorytet 2.

### P13 — Sprzężony ruch nieliniowy i gaz

**Wykonany zakres:** Hermetyczny gaz, ruch nieliniowy i rodziny pamięci. Dowody: [020](../raporty/020_nieliniowy_naped_i_sprzezony_gaz.md); [021](../raporty/021_pamiec_cewki_i_definicja_Lgen.md).

**Pozostaje komputerowo:** Czasowa reakcja nowej obudowy i materiału lub ilościowa ocena redukcji. **Brakujące dane/pomiar:** Nieliniowe parametry materiału/napędu.

**Kryterium zaliczenia dalszego zakresu:** Energia i granica małosygnałowa; nie przenosić wyników rodzin na produkty. Zależności: P12, P21, P24; priorytet 2.

### P14 — THD i IMD

**Wykonany zakres:** 3312 przypadków P14B, rozstrzygnięte flagi w zadanych rodzinach. Dowody: [024](../raporty/024_P14B_emisja_i_swiadkowie.md); [026](../raporty/026_P14B_pelna_kampania_dwutonowa.md).

**Pozostaje komputerowo:** Ocena błędu harmonicznych/IMD dla nowej integracji tylko w przyjętym modelu. **Brakujące dane/pomiar:** Rzeczywiste THD/IMD i użyteczny skok.

**Kryterium zaliczenia dalszego zakresu:** Wyniki syntetyczne oznaczać jako diagnostykę modelu, próg szumu numerycznego jawny. Zależności: P13, P25; priorytet 2.

### P15 — N8 — model cieplny w czasie

**Wykonany zakres:** Sieci Cauer/Foster i przebiegi Re(T) wykonane zakresowo. Dowody: [025](../raporty/025_P15A_topologia_i_granice_termiki.md); [027](../raporty/027_P15B_sprzezenie_grzania_i_napedu.md).

**Pozostaje komputerowo:** Długie sygnały, pamięć cieplna i obciążenie ciepłem powietrza w nowym modelu. **Brakujące dane/pomiar:** Rth,Cth, temperatury dopuszczalne i warunki chłodzenia.

**Kryterium zaliczenia dalszego zakresu:** Bilans energii cieplnej, granica stanu ustalonego, badanie czasu i kroku. Zależności: P20, P25; priorytet 1.

### P16 — Sprzężenia cieplne i elektromechaniczne

**Wykonany zakres:** Sprzężenie Re(T), ruchu i przyjętej konwekcji. Dowody: [027](../raporty/027_P15B_sprzezenie_grzania_i_napedu.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Wrażliwość BL(T) i wspólne scenariusze cewka–gaz–magnes. **Brakujące dane/pomiar:** BL(T), gradienty i rzeczywiste straty.

**Kryterium zaliczenia dalszego zakresu:** Wskazać minimalny zestaw danych rozstrzygający C02/C11; nie utożsamiać Pe z Pcu. Zależności: P15, P24; priorytet 2.

### P17 — Łączne granice użytecznego zakresu

**Wykonany zakres:** Wspólne V/I/X/Pcu dla osobnych sinusów. Dowody: [028](../raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md); [053](../raporty/053_porownanie_i_odpornosc_rekomendacji.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Obwiednie sygnałów po ochronie i korekcji z docelowym obciążeniem. **Brakujące dane/pomiar:** THD, chłodzenie, granice elektroniki.

**Kryterium zaliczenia dalszego zakresu:** Każdy SPL ma sygnał, czas, pasmo, geometrię i kryterium limitu. Zależności: P21, P24, P25; priorytet 2.

### P18 — Płyty MDF: drgania, naprężenia, promieniowanie

**Wykonany zakres:** Płyty, pełna rama historyczna i przesunięty front 44 mm; nie docelowy zespół. Dowody: [029](../raporty/029_P18A_plyty_sciagi_i_dynamika.md); [033](../raporty/033_front_otwor_kosz_i_styk_jednostronny.md); [035](../raporty/035_pelna_rama_3D_spoiny_i_podparcie.md); [052](../raporty/052_komora_warstwy_wklady_i_front.md).

**Pozostaje komputerowo:** MES docelowego zespołu z wręgami, otworem, masą kosza, stopami i obiema orientacjami. **Brakujące dane/pomiar:** E,nu,rho,tłumienie MDF; nośność i dane mocowania kosza.

**Kryterium zaliczenia dalszego zakresu:** Zbieżność modów/przemieszczeń oraz wymagania naprężeniowe; idealne podparcie nie dowodzi realnej sztywności. Zależności: P20; priorytet 1.

### P19 — Usztywnienia, połączenia i klej

**Wykonany zakres:** Rodziny spoin, styku, listwy i podmodeli; lokalne koncentracje nie wszędzie zbieżne. Dowody: [030](../raporty/030_P19A_obliczenia_spoin_i_material_kleju.md); [034](../raporty/034_czasowy_styk_i_pelny_MES.md); [036](../raporty/036_spoiny_3D_i_wirtualne_odspojenie.md); [037](../raporty/037_staly_front_wymagany_modul_spoin.md); [040](../raporty/040_listwa_stalego_frontu_i_droga_sily.md); [041](../raporty/041_lokalny_podmodel_i_granice_wiarygodnosci.md).

**Pozostaje komputerowo:** Nowe drogi sił, naciski i wymagania sztywności złącza dla docelowego zespołu. **Brakujące dane/pomiar:** Gc, krzywe S–N, pełzanie J(t), adhezja, wilgotność i jakość laminacji.

**Kryterium zaliczenia dalszego zakresu:** Oddzielić wymagany moduł od nośności; bez parametrów nie certyfikować trwałości. Zależności: P18, P20; priorytet 1.

### P20 — Regulacja objętości

**Wykonany zakres:** Moduły 3D, tory w pustym korpusie i hipotetyczna rezerwa 8 l. Dowody: [042](../raporty/042_regulacja_Vb_i_wklady_wypornosciowe.md); [043](../raporty/043_przegroda_dwie_komory_i_materialy.md); [044](../raporty/044_modul_3D_dwa_porty_i_wymagania_kleju.md); [054](../raporty/054_rekomendowana_konfiguracja_prototypu.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Wspólny bilans, dodatnie mocowania, kolizje, przejście przez otwór i całkowite 500 mm. **Brakujące dane/pomiar:** Wyporność i obrys kosza, maskownica, tolerancje oraz szczelność.

**Kryterium zaliczenia dalszego zakresu:** Brak kolizji z zapasem w obu orientacjach; netto policzone bez podwójnych objętości. Zależności: P03; priorytet 1.

### P21 — Wewnętrzne pole i sprzężenie paneli

**Wykonany zakres:** P21B 18/18; C0/C1/C2/C3 w swoich geometrach, brak wręg/kosza w pełnym FV. Dowody: [045](../raporty/045_gaz_przestrzenny_praca_i_granica0D.md); [050](../raporty/050_P21C0_plytka_komora_i_polozenie_zrodla.md); [051](../raporty/051_P21C1_membrana_kolowa_i_bezwladnosc.md); [052](../raporty/052_komora_warstwy_wklady_i_front.md).

**Pozostaje komputerowo:** Sprzężenie właściwego gazu, paneli i napędu z nową geometrią. **Brakujące dane/pomiar:** Identyfikacja maty/paneli i portu rzeczywistej membrany.

**Kryterium zaliczenia dalszego zakresu:** Zbieżność, praca na wspólnej granicy, pasywność i granice 0D; nie utożsamiać portu z SPL. Zależności: P09, P18, P19, P20; priorytet 1.

### P22 — Napęd, impedancja wyjściowa i clipping

**Wykonany zakres:** Pasywne porty i 648 trajektorii nasycenia; brak gwarancji I/X. Dowody: [047](../raporty/047_port_zrodla_tlumienie_i_bilans.md); [048](../raporty/048_nasycenie_SEM_i_stan_pradu.md).

**Pozostaje komputerowo:** Integracja clippingu, SEM, ograniczeń I/V, ciepła i filtrów. **Brakujące dane/pomiar:** Zasilacz, odbiór energii zwrotnej, transfer i limiter prawdziwego wzmacniacza.

**Kryterium zaliczenia dalszego zakresu:** Nie obcinać stanu indukcyjności; bilans energii, test wykonalności wspólnych limitów. Zależności: P21, P23, P24; priorytet 1.

### P23 — Cyfrowa korekcja, faza i opóźnienia

**Wykonany zakres:** Stabilność zapisanych filtrów, arytmetyka software, macierz 2→8. Dowody: [046](../raporty/046_filtry_cyfrowe_stabilnosc_i_zapas.md); [053](../raporty/053_porownanie_i_odpornosc_rekomendacji.md).

**Pozostaje komputerowo:** Korekcja z fizycznym obciążeniem i ochrona po filtrze, zapas rekonstrukcji. **Brakujące dane/pomiar:** Kalibracja DAC/wzmacniacza, latencja i arytmetyka urządzenia.

**Kryterium zaliczenia dalszego zakresu:** Uwzględnić wartości między próbkami i stany; stabilność nie jest ochroną X/T. Zależności: P21, P24; priorytet 1.

### P24 — Dynamiczna ochrona

**Wykonany zakres:** Dokładne świadki P24A dla określonych rodzin; nie dla nowego zespołu. Dowody: [049](../raporty/049_obszar_niezmienniczy_i_koszt_ochrony.md); [054](../raporty/054_rekomendowana_konfiguracja_prototypu.md).

**Pozostaje komputerowo:** Nowe ograniczenia X/I/T po EQ, rozruch, błędy estymatora i opóźnienie. **Brakujące dane/pomiar:** Identyfikacja parametrów oraz czujników/obserwatora, progi sprzętu.

**Kryterium zaliczenia dalszego zakresu:** Dowód tylko w jawnej rodzinie; poza nią brak gwarancji. HP20 nie jest pełną ochroną. Zależności: P12, P15, P21, P22, P23; priorytet 1.

### P25 — Sygnały wielotonowe i realistyczne

**Wykonany zakres:** Dwutony oraz 9 skończonych wielotonów C02, bez rozruchu i dynamicznego T. Dowody: [024](../raporty/024_P14B_emisja_i_swiadkowie.md); [026](../raporty/026_P14B_pelna_kampania_dwutonowa.md); [053](../raporty/053_porownanie_i_odpornosc_rekomendacji.md).

**Pozostaje komputerowo:** Rzeczywiste czasowe symulacje widm muzykopodobnych, impulsów, crest factor, clippingu i ochrony. **Brakujące dane/pomiar:** Reprezentatywność nagrań i parametry rzeczywistego napędu.

**Kryterium zaliczenia dalszego zakresu:** Zapisać sygnały/ziarna/czas, zbieżność i energię, ujawnić przekroczenia. Zależności: P22, P23, P24; priorytet 1.

### P26 — Zespolony model pokoju ze stratami

**Wykonany zakres:** Rodziny modalne i reakcja pola na napęd; scenariusze, nie pomiar pokoju. Dowody: [013](../raporty/013_pokoj_i_realne_gabaryty.md); [017](../raporty/017_promieniowanie_i_sprzezenie_pokoju.md); [019](../raporty/019_zamiana_kanapy_i_RTV.md).

**Pozostaje komputerowo:** Nowa geometria źródeł, niepewność tłumienia i warianty warunków brzegowych. **Brakujące dane/pomiar:** Pozycje, straty, przejście, okna i realna adaptacja.

**Kryterium zaliczenia dalszego zakresu:** Ocena odporności w pobliżu sweet spotu, bez przypisywania modelowi pomiaru. Zależności: P20, P21; priorytet 2.

### P27 — Jeden/dwa subwoofery i ustawienie

**Wykonany zakres:** Cztery scenariusze, gabaryty dawnych skrzyń; aktualna orientacja v2. Dowody: [013](../raporty/013_pokoj_i_realne_gabaryty.md); [019](../raporty/019_zamiana_kanapy_i_RTV.md).

**Pozostaje komputerowo:** Dwie nowe skrzynie przy monitorach, pion/poziom, przesunięcie źródeł i dopuszczalne ustawienia. **Brakujące dane/pomiar:** Rzeczywiste miejsce, kolizje z meblami i ustalone pozycje.

**Kryterium zaliczenia dalszego zakresu:** Gabaryty oraz faza/delay sprawdzone dla każdego jawnego scenariusza. Zależności: P20, P26; priorytet 2.

### P28 — Integracja monitorów i8wyjśćDSP

**Wykonany zakres:** Macierz 2→8 i idealna suma LR4. Dowody: [053](../raporty/053_porownanie_i_odpornosc_rekomendacji.md).

**Pozostaje komputerowo:** Wrażliwość integracji na nieznane fazy/opóźnienia monitorów i zapas po EQ. **Brakujące dane/pomiar:** Transfery monitorów, latencja i późniejsza kalibracja.

**Kryterium zaliczenia dalszego zakresu:** Brak dodatniego EQ do głębokich zer bez bilansu dynamiki; osobne kanały subów. Zależności: P23, P26, P27; priorytet 2.

### P29 — Odporna optymalizacja wielokryterialna

**Wykonany zakres:** Warunkowa rekomendacja C02; granica scenariuszowa C02/C11 86,813 W. Dowody: [053](../raporty/053_porownanie_i_odpornosc_rekomendacji.md); [054](../raporty/054_rekomendowana_konfiguracja_prototypu.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Pareto wspólnego modelu: osiągi, ciepło, ruch, konstrukcja, masa i serwis. **Brakujące dane/pomiar:** Chłodzenie, użyteczny skok, THD oraz realna konstrukcja.

**Kryterium zaliczenia dalszego zakresu:** Nie wybierać jedną miarą; zachować C02/C11/C06, przedstawić stabilność decyzji. Zależności: P06, P17, P18, P20, P24, P27, P28; priorytet 2.

### P30 — Odtwarzalność i przyszły protokół

**Wykonany zakres:** Manifesty i protokoły etapowe; import 417 plików. Dowody: [022](../raporty/022_stan_badan_i_zakres_pozostaly.md); [054](../raporty/054_rekomendowana_konfiguracja_prototypu.md); [055](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md).

**Pozostaje komputerowo:** Pełna macierz dowodów/hipotez, integracyjna replikacja i rozstrzygnięcie historycznych różnic hashów. **Brakujące dane/pomiar:** Niezależna walidacja fizyczna po budowie.

**Kryterium zaliczenia dalszego zakresu:** Odtwarzalność, jawne bramki i brak zamknięcia przez samą liczbę symulacji. Zależności: P01–P29; priorytet 1.

## Kolejność i bramki, których nie można zastąpić planem

| Bramka | Rzeczywisty rezultat potrzebny do przejścia | Co zmieni decyzję |
|---|---|---|
| G1 geometria | Jeden parametryczny zespół: netto, pełna głębokość, tor wkładu, mocowania, tolerancje, obie orientacje | Kolizja lub brak 150 l wymusza zmianę W/H/D, regulatora albo jawne odstępstwo |
| G2 mechanika | Wspólna rama z wręgami i podatnymi złączami; zbieżne przemieszczenia, reakcje i modów; wymagania materiałowe | Podatność/siły mogą zmienić rozstaw wręg, masę i litraż |
| G3 port fizyczny | Gaz przestrzenny + panele + napęd z jednolitą definicją Mms; obwiednia niepewności | Korekty portu i masy mogą zmienić EQ, wychylenie i przewagę kandydata |
| G4 ochrona | Czasowe X/I/T/V po filtrach, clipping i rozruch; dowód tylko we właściwej rodzinie | Zbyt konserwatywny limit lub niepewny obserwator zmienia napęd i użyteczny SPL |
| G5 system/Pareto | Dwie rzeczywiste bryły w scenariuszach pokoju, faza/delay, zapas EQ i wielokryterialna synteza | Miejsce, masa, serwis i straty cieplne mogą zmienić wybór |
| G6 publikacja końcowa | Zamknięte zakresy obliczeniowe, jawne bramki fizyczne, pełny manifest i protokół | Dopiero wtedy końcowy PDF/Release 1 |

Numeryczne kryteria błędów należy zapisać przed nowym przebiegiem zgodnie z metryką: np. port zespolony oceniany względnie z osobnym traktowaniem zer, a lokalne naprężenia osobno od globalnej podatności. Próg siatki nie jest niepewnością materiału. Zmniejszenie reszty algebraicznej nie rozstrzyga błędu dyskretyzacji.

## Minimalny przyszły protokół fizyczny

To protokół późniejszego etapu, nie zamówienie przyrządów i nie wykonane pomiary. Zapis każdego pomiaru: plik surowy, numer egzemplarza, geometria, masa maty, moduły, orientacja, temperatura otoczenia i cewki lub jej estymata, kalibracja amplitudy/czasu, sygnał, częstotliwość próbkowania, czas, filtr, napięcie/prąd terminali oraz kryterium przerwania. Zachować też wynik negatywny i niepewność.

1. **Geometria i montaż przed napędem.** Zmierzyć kosz, jego wyporność w przyjętej definicji granicy gazu, spoczynkowy obrys membrany, otwór, maskownicę, terminal i ugięcia/marginesy. Zważyć panele, wręgi, moduły, matę i całość. Zweryfikować wkładanie/wyjmowanie z narzędziem oraz zatrzymanie modułów w obu orientacjach. Warunek: pełny obrys i przyjęte skrajne tolerancje spełniają 500 mm; nie dopuszczać luźnych modułów.
2. **Małosygnałowa identyfikacja.** Dla tego samego egzemplarza wykonać Z(f) bez maty i z jednakowo zważoną matą przy trzech zweryfikowanych objętościach; kontrolować zimne Re i napięcie. Uzupełnić bliskie pole i kontrolę szczelności. Dopasować wspólnie modele oraz sprawdzić parametry na konfiguracji niewykorzystanej w dopasowaniu. Sama Z(f) nie rozdziela jednoznacznie wszystkich strat i Mmd.
3. **Konstrukcja i połączenia.** Porównać postacie i odpowiedzi paneli przy małym wzbudzeniu w pionie/poziomie; osobno próbki spoin/MDF dla wymaganej adhezji, pełzania i obciążeń cyklicznych. Nie przenosić nominalnej klasy D3/D4 na nośność. Kryteria wytrzymałościowe wymagają danych materiałowych i jawnych obciążeń, zanim można zatwierdzić CNC/budowę w docelowej postaci.
4. **Kalibracja napędu i ochrona.** Ustalić transfer cyfrowe wejście→V terminali, ograniczenie I/V i opóźnienie. Testować działanie limiterów najpierw w warunkach bezpiecznych dla badanego toru; nie wyznaczać granic głośnika przez niekontrolowane zwiększanie poziomu. Osobno sprawdzić wartości między próbkami, włączenie/wyłączenie, awarię sygnału i energię zwrotną.
5. **Rozstrzygnięcie C02/C11/C06.** Przy tych samych zweryfikowanych Vb, warunkach i sygnałach zmierzyć stopniowo ruch/THD/IMD, Re po ogrzaniu, kompresję i ochładzanie. Ustalić Rth/Cth lub obwiednię danych, użyteczny skok i zależność od czasu. Przerwać przed przekroczeniem ustalonych limitów materiału, toru lub dziedziny estymatora. Bez takich danych porównanie chłodzenia pozostaje warunkowe; nie ma podstaw, by traktować 86,813 W jako próg urządzenia.
6. **Pokój i system.** Mierzyć osobno każdy sub i monitory, następnie sumę: sweet spot plus małe przesunięcia kontrolne. Zapisać pozycje i stan drzwi/okien/adaptacji. Dobierać delay/polaryzację oraz EQ z bilansem headroomu; nie kompensować głębokich zer bez kontroli ruchu i napięcia. Wynik pozostaje pomiarem pokoju, nie wolnego pola.

Minimalne dane rzeczywiście rozstrzygające wybór głośnika to: zweryfikowane gabaryty/wyporność, Z(f) w co najmniej dwóch znanych objętościach, użyteczny ruch przy zadanych zniekształceniach i czasie, przebieg Re(T)/kompresji z chłodzeniem oraz ograniczenia V/I rzeczywistego napędu. Przewaga na podstawie samych katalogowych Xmax i Pe jest niewystarczająca.

## Rejestr ryzyka i gotowość

| Ryzyko | Stan dowodu | Skutek | Sposób rozstrzygnięcia |
|---|---|---|---|
| Przekroczenie 500 mm lub kolizja wkładów | Potwierdzony konflikt starego układu przy skracaniu do 470 mm; obrys osprzętu otwarty | Zmiana konstrukcji | G1 i pomiar rzeczywistych elementów |
| Pozorna sztywność idealnego podparcia | Front P18D utwierdzony; brak finalnego zespołu | Błędne mody/naprężenia | G2, zakres sztywności złączy i późniejsza walidacja |
| Przeciek modułów, luźne mocowania | Rodziny modelowe, brak mechanizmu docelowego | Zmiana objętości efektywnej, hałas, uszkodzenie | G1–G3, szczelność i dodatnie mocowanie |
| Podwójne Mms/promieniowanie | W P21C2 dwie konwencje zastępcze, brak Mmd | Błędna odpowiedź i ochrona | G3 i identyfikacja wielokonfiguracyjna |
| Niezidentyfikowana termika | Pułapy Pcu są scenariuszami | Zmiana rekomendacji lub przegrzanie | G4 i czasowe Re/T/kompresja |
| Niepewny limiter/DAC | Stabilne filtry nie gwarantują X/I/T | Przekroczenie ruchu/prądu | G4 i kalibracja całego toru |
| Nieznane monitory/pokój | LR4 idealne, geometrie scenariuszowe | Kasowanie fazowe, strata dynamiki | G5 i pomiary rzeczywiste |
| Historyczne manifesty nie opisują aktualnych indeksów | 103 różne odwołania, wszystkie pliki istnieją | Nieodtwarzalna mieszanka rewizji | Odtwarzać właściwy commit/archiwum; zachować audyt |

**Gotowość modelu:** liczne rodziny zweryfikowane zakresowo, pełna integracja pozostaje otwarta. **Gotowość dokumentacji:** wystarcza do kontynuowania badań, nie do zlecenia końcowej produkcji. **Gotowość fizycznej budowy:** niezatwierdzona przed G1/G2 i zamknięciem wymagań wykonawczych. **Walidacja fizyczna:** niewykonana. **PDF/Release 1:** nie tworzyć na podstawie tej macierzy.

Odtwarzanie audytu: `python skrypty/audyt_manifestow_P30B.py`. Dane macierzy: `dane/p30_macierz_luk.json`. Macierz ma być aktualizowana przez nowe, faktycznie zakończone etapy; sam wpis zadania nie jest dowodem jego wykonania.
