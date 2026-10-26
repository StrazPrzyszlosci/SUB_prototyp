# Raport 044 — P20C: moduł 3D, dwa porty i wymagania kleju

Stan: 2026-10-26. **Obliczenia i symulacje**, bez fizycznego urządzenia.
Kontynuacja [042](042_regulacja_Vb_i_wklady_wypornosciowe.md) i
[043](043_przegroda_dwie_komory_i_materialy.md). Front prototypu pozostaje
stały U-021, a wybór jednego głośnika i jednej obudowy jest nadal otwarty.

## Wniosek do projektu

Pełna bryła ze spoinami jest bardziej podatna niż poprzedni model płyt
z idealnym utwierdzeniem. Dla referencyjnego modułu ze ściągiem i przyjętym
E kleju=1718 MPa model n=12 oddaje przy 20 Hz **11,705 ml równoważnej
podatności**, wobec **8,816 ml** w porównywalnej rodzinie płyt z beta·K.
To około **32,8% różnicy podatności samego modułu**, a nie różnica SPL.

Suma 16 modułów daje około 0,187 l przy 20 Hz wobec 0,141 l modelu płyt. Przegroda 18
z nieruchomym obwodem z raportu 043 oddaje około 0,456 l, ale jest lżejsza.
Nie zamknięto porównania metod samą masą lub jedną liczbą podatności.

W zbadanym zakresie napędu 27 konfiguracji różnica względem modelu płyt
wyniosła maksymalnie około 0,01252 dB, lecz ten rekord jest poza umownym
ekranem amplitudy gazu. W punktach zachowujących oba ekrany maksimum
bezwzględne wyniosło około **0,004572 dB**. To mała korekta liniowej obwiedni
w tym eksperymencie, bez dowodu identycznego THD, temperatury, muzyki lub
kolejności wszystkich finalistów w całym briefie.

**Rekomendacja warunkowa:** moduł 100 mm ze ściągiem pozostaje uzasadnioną
referencją do następnego modelu pola gazu. Sztywno blokowana przegroda
pozostaje alternatywą; nie zaakceptowano jeszcze finalnej konstrukcji.

## Wykonany zakres i dane

| Rodzina | Zakres |
|---|---:|
| Podstawowa bryła: trzy siatki × trzy E kleju × bez/ze ściągiem |18 modeli, do 31266 DOF|
| Dwa porty mechaniczne: pasmo 20–80 Hz i wybrane punkty przy modach |162 wiersze|
| Gaz izotermiczny/adiabatyczny i sześć przewodności przecieku |1944 wiersze|
| Statystyki przestrzenne rzeczywistych warstw kleju przy offsecie 1000 Pa |252 wiersze|
| Kontrole objętości, masy, 9 momentów pracy i ruchów sztywnych |6 odrębnych modeli kontrolnych i kontrole w rodzinie|
| Jednorodne odniesienie hydrostatyczne |2 bryły: bez/ze ściągiem|
| Pełne równania nodalne MES + ciśnienie gazu |24 porównania|
| Osobne kierunki siatki i wspólne Hz przy rezonansach |24 punkty; 8 pierwotnych flag|
| Dalsza siatka n=16 dla czterech rodzin z flagami |8 punktów przy modach +24 w paśmie|
| Ciągły wymagany moduł kleju |6 pierwiastków, 6 kontroli pochodnej, 2 siatki|
| Włączenie pełnego 3D do napędu |11664 punkty, 27 konfiguracji elektrycznych|

Dalsza siatka n=16 rozstrzygnęła wszystkie 8 pierwotnych flag: największa
zmiana macierzy portów wynosi 4,123%, a admitancji z gazem 3,990%.
W tych czterech dodatkowych rodzinach zmiana n12→16 w paśmie wynosi
do 0,951%. Największy model ma 40248 DOF, szczyt RSS około 1514 MiB.
Nie zmieniono progu 5% i zachowano pierwotne wyniki. To nadal skończone
świadki, dla wskazanych punktów i kierunków siatki.

Wejścia: [konfiguracja](../dane/konfiguracje/p20c_modul_pelny_3D.json).
Podstawowe wyniki: [modele3D](../wyniki/p20c_modele_3D.csv),
[porty gazu](../wyniki/p20c_gaz_i_przeciek.csv),
[kontrole](../wyniki/p20c_kontrole_niezalezne.json),
[napęd27konfiguracji](../wyniki/p20c_naped_27_konfiguracji.csv).
Rejestr kompletnych wejść/wyników i wersji bibliotek:
[manifest P20C](../wyniki/manifest_modulu_3D_P20C.json).

## Geometria, masa i rzeczywista objętość kleju

**Założenia:** obrys 180×100×170 mm, ściany 8 mm, MDF E=2,1 GPa,
nu=0,3, rho=730 kg/m³. Klej: grubość 0,2 mm, nu=0,35, rho=1200 kg/m³,
E=10/100/1718 MPa. To rodziny stresowe, nie tolerancje producenta.
1718 MPa jest wcześniejszą referencją danych folii, nie zidentyfikowanym
modułem rzeczywistej spoiny MDF i nie wyborem produktu.

Zbudowano rozłączne objętości sześciu ścian i warstw kleju. Są12 połączeń
korpusu oraz 4 spoiny ściągu: połączenia nakładka–ściana i pręt–nakładka
na obu końcach. Pręt jest skrócony, aby nie nakładać jego objętości na klej.
Nakładki 30×30×8 mm, pręt ma przekrój 10×10 mm. Całe ciało ma wspólne węzły
na granicach materiałów; w tym modelu nie zastępujemy kleju sprężyną bez objętości.

Dla wariantu ze ściągiem:

| Wielkość | Wartość kontrolna |
|---|---:|
| Obrys |3,06 l|
| Gaz wewnętrzny |2,099984 l|
| MDF |0,95694336 l|
| Klej |0,00307264 l|
| Sucha masa MDF+kleju |0,70225582 kg|
| Sucha masa 16 modułów |11,236093 kg|

Różnica względem dawnego bilansu jest jawna: masa modułu rośnie o około
1,678 g, a gaz maleje o0,32 ml. Nie przepisano dawnej masy ściągu bez
przeliczenia spoin. Obrys modułu pozostaje ten sam, więc geometrycznie
wypierana główna objętość nie zmienia się. Wyporność głośnika 4 l nadal jest
umowną osią, nie daną wybranego SB/Dayton. Osprzęt mocowania modułów
w korpusie pozostaje osobnym bilansem i zadaniem kwalifikacji.

## Równania dwóch portów i granice

**Symulacja:** kartezjańska zgodna siatka brył H8 z własnym EAS9 i zgodną
masą nodalną. Nie jest to implementacja komercyjnego C3D8I. Zastosowano
istniejące [jądro elementu](../skrypty/element_brylowy_P18C.py), którego
odrębne odniesienia zginania/patch 3D są w P18C; dodano nowe odniesienie
hydrostatyczne i pełny bilans portów. Materiały są liniowe i izotropowe.

Dla s=jω i RMS:

    delta_Vi = Hi.T*u
    -delta_Vo = Ho.T*u
    F = Hi*pi + Ho*po
    chi = H.T*inv(K+s*C+s²*M)*H

Objętość gazu i obrys zewnętrzny są różne. Z góry narzucone Hi=−Ho
usunęłoby ściskanie MDF i kleju. Na odsłonięte powierzchnie ściągu również
działa gaz, a na zakryte powierzchnie spoin nie dopisuje się go drugi raz.
Oba jednorodne porty mają zerową wypadkową i moment względem całej swobodnej
bryły; nadal obciążają lokalne panele i spoiny.

Ci=Vi/(kappa*p0), G jest przeciekiem między główną komorą a wnętrzem modułu:

    r = pi/po = (G-s*chi_io)/(G+s*(Ci+chi_ii))
    1-r = s*(Ci+chi_ii+chi_io)/(G+s*(Ci+chi_ii))
    Y = s*(chi_oo+chi_oi*r)+G*(1-r)

Różnica ciśnień liczona jest bez odejmowania bliskich liczb. Przy G→∞
pi/po→1, ale G*(1−r) może pozostać skończone. Poprawna granica:

    Y/s -> Ci + chi_ii+chi_io+chi_oi+chi_oo

Pozostaje gaz i ściskanie materiału. Przy G=0 odtwarza się Schur
chi_oo−chi_oi*chi_io/(Ci+chi_ii). Symbolicznie sprawdzono także redukcję
do wzoru cienkich ścian P20 A oraz niezamienność DC i G→0.
Przewodność G jest stała fizycznie dla wybranego przypadku: etykieta
100 l-ref nie jest rzeczywistym biegunem małego modułu. W porównaniu płyt
i pełnego 3D użyto tego samego G, nie tak samo nazwanych różnych fc.

Tłumienie C=beta*K jest dodatnie: beta odpowiada zeta 0,02 przy 200 Hz.
Ta rodzina jest wspólna z P20B; nie nadpisuje dawnych danych P20 A ze stałym
modalnym zeta. Re(Y) zgadza się z mocą strat mechanicznych i przecieku.
W tym etapie brak sprzężenia promieniowania zewnętrznego i pokoju.

## Siatka, postacie i obszar ważności

Parametr n określa maksymalną długość komórki przy zachowaniu wszystkich
płaszczyzn geometrii; nie jest liczbą jednakowych elementów na bok.
Podstawowe siatki mają n4/8/12, dwie warstwy przez MDF i jedną przez klej.
Zagęszczono je także oddzielnie: MDF2→4 i klej 1→2 warstwy.

W paśmie 20–80 Hz zmiana n8→12 daje około 1,2–3,9% zespolonej admitancji
w sześciu rodzinach. Przy wspólnych częstotliwościach przy modach było
8 przekroczeń roboczego 5%, do około 9,6%. Zachowano je w
[pierwotnym audycie](../wyniki/p20c_niezalezna_siatka_i_wspolne_Hz.csv).
Nie porównywano różnych Hz wokół modów różnych siatek.
[Dalsza siatka](../wyniki/p20c_dalsza_siatka_przy_modach.csv) dotyczy
wszystkich czterech rodzin z flagami, przy tym samym progu i Hz.
Zmiana warstw MDF daje w wybranych punktach do około 3,6%, kleju do 0,24%.
Są to skończone świadki zbieżności, nie certyfikat całego kontinuum.

24 mody są diagnostyką i potencjalną bazą redukcji z dodatnią resztą
statyczną. Podane suche mody obejmują MDF i klej. Bezwładność przestrzenna gazu
i reakcja pola zewnętrznego pozostają do P21. Porty głównej tabeli
i napędu policzono pełnym rozwiązaniem
macierzy, nie obcięciem do 24 modów. Zachowano błędy projekcji i pełne pole
referencyjne n12 z węzłami, elementami, stanami i wektorami modalnymi.

Dla sztywnej referencji ze ściągiem n12 pierwsza sucha postać ma około 781 Hz,
a pierwsza spośród 24 z wagą portu powyżej przyjętego 1e-6 śladu statycznego
około 1195 Hz. To nie wszystkie możliwe wzbudzenia fizycznego wyrobu.
Odniesienie pustej komory wynosi około 1046 Hz. Ściąg zmienia dziedzinę gazu;
ta liczba nie jest uniwersalną ścisłą granicą. Model gazu 0D nie potwierdza
fizycznego rezonansu gazowo-strukturalnego w tym obszarze.

![Siatka i porównanie metod regulacji](../wyniki/78_P20C_siatka_i_porownanie_regulatorow.png)

## Obliczeniowe wymaganie sztywności kleju

Przy stałych nu, geometrii, grubości i izotermicznym gazie statycznym:

    Keff(E) = Kmdf + E*Kglue_unit + Hi*Hi.T/Ci
    Ceff(E) = Ho.T*inv(Keff(E))*Ho
    dCeff/dE = -q.T*Kglue_unit*q <= 0

To dowód monotoniczności w tej dodatniej rodzinie statycznej, nie przy
rezonansie dynamicznym. Wyznaczono pierwiastki w ciągłym E, sprawdzono
pochodną niezależnymi różnicami i zachowano świadków po obu stronach progu.

**Kryterium porównawcze, nie brief:** Ceff(E)≤(1+epsilon)*Ceff(1718 MPa).

| epsilon | Wymagane E, siatka 8 | Wymagane E, siatka 12 |
|---:|---:|---:|
|1%|966,43 MPa|992,87 MPa|
|5%|309,15 MPa|320,57 MPa|
|10%|152,70 MPa|156,60 MPa|

Nie są to wartości minimalnej wytrzymałości ani gwarancja wybranego kleju.
Rzeczywisty moduł efektywny może zależeć od czasu, temperatury, wilgotności,
grubości i powierzchni MDF. Brak J(t), S–N, Gc i adhezji partii nadal pozostaje
bramką. Oznaczenie D3/D4 nie zastępuje tych danych.

Pełny klej 3D daje także przestrzenne statystyki naprężeń: dla referencji
n=12 i zadanego małego offsetu zewnętrznego 1000 Pa przestrzenny RMS dodatniej
części normalnej w wybranych spoinach frontu wynosi około 10 kPa, ścinania podobnie.
To **statyczny offset**, nie czasowy RMS sygnału akustycznego; RMS dotyczy
uśrednienia przestrzennego pola. Maksimum w punktach Gaussa nie jest
fizycznym pikiem naroża. Liczby nie wyznaczają nośności lub trwałości.

![Ciągłe wymaganie modułu i przestrzenne naprężenia](../wyniki/79_P20C_modul_kleju_i_statystyki_spoin.png)

## Napęd i znaczenie dla wyboru głośnika

Dołożono nową fizykę do porównania 27 konfiguracji: trzy E kleju, po 4/8/12/16
modułów, przeciek G0/1/10 Hz-ref oraz napędy 40 V/12 A i 60 V/20 A.
Geometria wyklejenia jest uwzględniona w gazie, bez nowej identyfikacji
termiki porów; wyporność głośnika 4 l jest umowna. Każdy punkt to oddzielny
ustalony sinus 20–80 Hz, frontowe SPLRMS2 pi/1 m, limit V/I/katalogoweX.
Nie zadano kwalifikowanego czasu pracy lub niskiego THD produktu.

2575 z11664 rekordów przekracza umowny ekran szczytu ciśnienia/p0≤1%
lub maksymalnej składowej ruchu względnego węzła/grubość≤0,2.
Nie jest to licznik uszkodzeń. Maksymalny formalny efekt 0,01252 dB dotyczy
C21, miękkiego kleju i20 Hz; rekord jest poza ekranem. Największa wartość
wewnątrz ekranów to około 0,004572 dB przy 63 Hz w tej samej rodzinie.
Nie wyciągnięto stąd rankingu THD lub masteringowej jakości.

![Postacie,granica gazu i wpływ korekty na napęd](../wyniki/80_P20C_mody_dziedzina_gazu_i_wplyw_na_naped.png)

## Ograniczenia i następny eksperyment

Pozostają: rzeczywiste właściwości MDF/kleju, straty, pełzanie, odspajanie,
wyrywanie i mocowanie modułu do korpusu, niejednorodne naciski i drgania
całej obudowy. Port swobodnej bryły przy jednorodnym nacisku nie kwalifikuje
tych zjawisk. Gaz wewnętrzny nie jest dopisany drugi raz do głównego netto.
Materiał porowaty jest odrębnym bilansem z039; sklejka nie otrzymała tutaj
fikcyjnego kompletnego tensora. Dwie sztuki, układ RTVlewo/kanapaprawo
i przybliżony pokój 4,6×3,7×2,5 m pozostają kontekstem dalszej integracji.

**Jeden najbliższy krok po rozstrzygnięciu siatek: P21B — przestrzenne
pole gazu wewnątrz modułu ze sprzężeniem do pełnych ścian 3D.** Sprawdzić
pracę na wspólnej granicy, moc, wzajemność i zbieżność do 0D przy stłumieniu
zmienności przestrzennej. Osobno wyznaczyć mody rzeczywistej dziedziny
z prętem i nakładkami. Potem główna komora z regulacją i włókniną, P22–25
oraz synteza. Nie ponawiać pełnych dawnych kampanii 24 baz bez nowej hipotezy.

Odtworzenie etapu:

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_modul_3D_P20C.py

Zgodne 18 rekordów są wznawiane po hashu; ich odczyt nie jest nowym
niezależnym rachunkiem. Odrębne hydrostatyka i pełne równania MES+gaz
opisane wyżej sprawdzają inne zależności. Końcowy PDF powstanie po całym
programie, ze wskazaniem jednego głośnika i jednej konstrukcji prototypu.
