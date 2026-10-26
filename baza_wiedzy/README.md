# Baza wiedzy projektu

Uzupełnienie 2026-10-24: wykonane N7 oraz rozszerzenie do 24 modeli,
analiza globalnych granic litrażu i identyfikowalności opisano w
[raportach 009–012](../README.md). [Program 30 badań](../PROGRAM_30_BADAN.md)
pozostaje aktywny; końcowy PDF i pojedynczy wybór dopiero po integracji badań.

Stan 2026-10-23. Rozdziały opisują metodę, wiedzę inżynierską i aktualne
ograniczenia. Konkretnych prognoz szukaj w [raportach](../README.md),
a potwierdzonych ustaleń użytkownika w [rejestrze](../DECYZJE_I_PYTANIA.md).

| Kolejność | Temat | Zastosowanie |
|---|---|---|
|01|[Zamysł i fizyka](01_zamysl_i_fizyka.md)|Co oznacza jakość i headroom; jak czytaćT/S|
|02|[Modelowanie elektroakustyczne](02_modelowanie_elektroakustyczne.md)|Równania, jednostki, Fc/Qtc/F3, impedancja, ruch, SPL i EQ|
|03|[Pokój i integracja](03_pokoj_i_integracja.md)|Mody, ustawienie, jeden sweet spot i przyszłe dwa subwoofery|
|04|[Mechanika iCNC](04_mechanika_i_CNC.md)|Brutto/netto, regulacja, wręgi, materiał i wykonawca|
|05|[Elektronika iDSP](05_elektronika_i_DSP.md)|Napęd, zasilanie, gain staging, filtry i ochrona|
|06|[Metrologia iwalidacja](06_metrologia_i_walidacja.md)|Plan po budowie; pomiary tylko w pokoju, bez bieżącego doboru toru|
|07|[Niepewność iorganizacja badań](07_niepewnosc_i_organizacja_badan.md)|Tolerancje, czułość, Pareto, wersje i granice wniosków|
|08|[Opinie iocena dowodów](08_opinie_i_ocena_dowodow.md)|Relacje właścicieli, korekty wątków i odczyt wykresów|
|09|[Zespolony model pokoju](09_zespolony_model_pokoju.md)|Straty modalne, kompresja, dwa źródła, normalizacja i niezależny Green 1D|
|10|[Niepewność globalna](10_niepewnosc_globalna.md)|Korelacje, Sobol/MC, obwiednie dziedzin, świadkowie i granice dominacji|
|11|[Gaz i materiały porowate](11_gaz_cieplo_i_materialy_porowate.md)|Relaksacja, lepkość, pory, dwa Cp, sorpcja i dane producenta|
|12|[Nieliniowa termodynamika i DC](12_nieliniowa_termodynamika_i_DC.md)|Energia, FFT/ODE, niezamienne granice i wyrównanie barometrii|
|13|[Promieniowanie, masy i reakcja pokoju](13_promieniowanie_masy_i_reakcja_pokoju.md)|Tłok/Rayleigh, czasza/komora, Mmd/Mms, wzajemne obciążenia, moc i granice sprzężenia|
|14|[Nieliniowy napęd i gaz](14_nieliniowy_naped_i_gaz.md)|Kms sieczne/styczne, strumień/coenergia, bilans gazu, DC, kompensacja i granice identyfikacji|
|15|[Pamięć cewki i identyfikowalność](15_pamiec_cewki_i_identyfikowalnosc.md)|ZespoloneLgen, poprawka siłyL2R2, dodatnia realizacja, digitalizacja i dokładne wykluczenie jednej gałęzi|
|16|[IMD, fazy i emisja](16_IMD_fazy_i_emisja.md)|Produkty poniżej pasma wejściowego, zespolone AM/PM, normalizacja AN10 i kontrolny czas opóźniony|
|17|[Topologia i identyfikowalność termiki](17_topologia_i_identyfikowalnosc_termiki.md)|Cauer/Foster, niejednoznaczność dodatkowego chłodzenia, podział strat i warunkowe granice|
|18|[Sprzężenie termiczne i obwiednia](18_sprzezenie_termiczne_i_obwiednia.md)|Re(T),impedancja i grzanie, rozdzielenie skal czasu, pamięć cieplna i kontrola współczynników|
|19|[Stały poziom i wspólne ograniczenia](19_staly_poziom_i_wspolne_ograniczenia.md)|CiągłeVb,prąd/napięcie/chłodzenie,SdX i aktywne ograniczenia|
|20|[MES paneli i ściągów](20_MES_paneli_i_sciagow.md)|Blokada ścinania,postacie,skończone łaty,masa i weryfikacja|
|21|[Mechanika spoin](21_mechanika_spoin_i_kwalifikacja.md)|PodatnośćMDF/kleju,lokalne odrywanie,ścinanie,S–N i szczelność|
|22|[Reakcja powietrza na panele](22_reakcja_powietrza_na_panele.md)|Rayleigh,masa powietrza,nieujemna moc i sprzężony bilans|
|23|[Front,otwór,kosz i docisk](23_front_otwor_kosz_i_docisk.md)|KowariantnyMITC,masa i siły,portkomory,uszczelka i śruby jednostronne|
|24|[Zmienny styk i energia](24_styk_czasowy_i_energia.md)|Trajektoria,docisk,energia portu,rampy,pełnyMES i granice szczelności|
|25|[Pełna rama i spoiny 3D](25_pelna_rama_i_spoiny_3D.md)|Bryły,EAS,niezgodne siatki,ciężar,podparcie i wirtualne odspojenie|
|26|[Dwie cewki i porównywanie SB](26_dwie_cewki_i_porownywanie_SB.md)|Transformacja portu, limity V/I/X, konflikty katalogowe i zakres rozszerzenia|
|27|[Ilość i położenie wypełnienia](27_ilosc_i_polozenie_wypelnienia.md)|Masa, porowatość, objętość gazu, warstwy i niezależna sieć FV|
|28|[Listwa i lokalna droga siły](28_listwa_i_lokalna_droga_sily.md)|Dodatkowe spoiny, masa/ciśnienie, globalna podatność i lokalna zbieżność|
|29|[Podmodel i transfer obciążeń](29_podmodel_i_transfer_obciazen.md)|Cięcia, fizyczne podpory, okna obserwacji i zależność od danych globalnych|
|30|[Wkłady: objętość, gaz i mocowanie](30_wklady_objetosc_gaz_i_mocowanie.md)|Podatność, szczelność, rezonans kanału, droga montażu i siły mocowania|
|31|[Przegroda, dwa ciśnienia i anizotropia](31_przegroda_dwa_cisnienia_i_anizotropia.md)|Podatne mocowanie, hermetyczny gaz, dostęp, znaki źródeł i ograniczenia Em sklejki|
|Źródła|[Rejestr z datami](ZRODLA.md)|Co przeczytano, co tylko znaleziono i jakie są braki|

## Od wiedzy do wykonania

W obecnym etapie zamykamy wiedzę potrzebną projektowi prototypu. Samo
istnienie rozdziału o pomiarach nie oznacza rozpoczynania zakupów aparatury.
Opis geometrii i mechaniki nie jest zgodą na uruchomienie prac nad narzędziamiCAD.

Nie ma tu wyników badań gotowego produktu. Na te dane przygotowano
[szablon raportu](../szablony/raport_pomiarowy.md) i katalog pomiarów.
Powstaną po budowie i doborze metody, z surowymi plikami oraz warunkami.

## Rozszerzanie bazy

Każde nowe źródło: identyfikator, URL, data publikacji/dostępu, dokładny model,
warunki i typ dowodu. Każda decyzja: pytanie, warianty, argumenty, niewiadome,
konsekwencje. Każdy wykres: oryginał, osie, legenda, sygnał, poziom, typ
model/pomiar i odczyt z niepewnością. Każda symulacja: wejścia, kod, wersje,
wyniki i interpretacja. Korekty dopisywać ze śladem, nie usuwać niewygodnych wyników.
