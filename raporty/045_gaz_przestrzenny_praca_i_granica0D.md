# Raport 045 — P21B: przestrzenny gaz, praca granicy i granica 0D

Stan: 2026-10-29. **Obliczenia i symulacje do budowy**, bez pomiarów urządzenia.
Zbadano szczelny moduł regulacji objętości z [P20C](044_modul_3D_dwa_porty_i_wymagania_kleju.md).
To etap przejścia do głównej komory, nie zamknięcie całego programu subwoofera.

## Co wynika dla projektu

**Obliczenie:** w sprawdzonych sześciu częstotliwościach 20–80 Hz największa
zmiana objętościowej admitancji modułu względem jednolitego gazu 0D wyniosła
**0,00525158%**.
Dotyczy 18 rodzin przy jednorodnym nacisku na moduł, założonych materiałach,
bez strat gazu i bez reakcji zewnętrznego pola głównej komory.
Nie jest zmianą SPL, THD lub wynikiem w pokoju.

Przy zadanym niejednorodnym polu zewnętrznym średnia ciśnienia nie opisuje
całego wnętrza. Gaz ma także bezwładność i przenosi pęd. Dlatego zgodność
samej średniej lub samej zmiany objętości nie wystarcza do oceny lokalnych
obciążeń i mocowania. Ruch całej bryły pozostał w równaniach.

**Rekomendacja warunkowa:** zachować prosty port 0D jako odniesienie
objętościowe małego modułu przy prawie równomiernym nacisku w badanym
paśmie; do głównej komory przejść z pełną definicją pracy i niejednorodności.
Nie przenosić tej małej korekty na całą skrzynię bez badania jej geometrii.

## Wykonany zakres

| Rodzina | Zakres |
|---|---:|
| Siatki 4/8/12 × bez/ześciągiem × trzy E kleju |18 przypadków|
| Pełne układy częstotliwościowe |132|
| Równomierne pole i pole z gradientem |264 wiersze pól|
| Macierze dwóch portów |528 zespolonych wpisów|
| Mody gazu przy sztywnych granicach |6 geometrii ×12 modów|
| Pojedynczy element:niezależny Kronecker |3 geometrie|
| Pusta komora:3 siatki i wymuszony tłok 1D |12 wymuszeń, także przy zerze ciśnienia wejściowego|
| Pełny blok i wydzielona średnia ciśnienia |4 porównania stanów|
| Formalna redukcja bezwładności gazu do 0D |12 realizacji|
| Granica skalarnego obciążenia po Ca i N |108 punktów częstotliwościowych z analityczną monotonicznością|

Największa podstawowa liczba niewiadomych wynosi
42356. Szczyt zapisanej pamięci procesu
wyniósł około 5332,9 MiB.
Wszystkie skonfigurowane punkty zachowały jawne ekrany numeryczne.
Nie oznacza to certyfikatu kontinuum lub potwierdzenia danych fizycznej sztuki.

## Geometria i materiały

Moduł ma obrys 180×100×170 mm, ściany 8 mm, rzeczywiste warstwy kleju 0,2 mm
oraz wariant z nakładkami i prętem. Założenia MDF:E=2,1 GPa, nu=0,3,
rho=730 kg/m³; klej:E=10/100/1718 MPa, nu=0,35, rho=1200 kg/m³.
To rodziny porównawcze, nie tolerancje producenta lub wybór produktu.

Referencja n12 ześciągiem ma 2,09998 l gazu,
0,702256 kg suchego materiału i
2,52863 g gazu przy warunkach Medium.
Gazu nie dopisano drugi raz do masy konstrukcji. To mały element regulatora;
nie są to wymiary głównej obudowy widocznej na banerze repozytorium.

Gaz jest idealizowany, adiabatyczny, bezstratny i bez przecieku. Przyjęto
gamma 1,4, p0=101325 Pa, T=293,15K. Brak warstw lepko-cieplnych ogranicza
interpretację szczytów wyższych rezonansów. Zewnętrzny nacisk jest zadany,
nie rozwiązano jeszcze pola między modułami i ściankami głównej skrzyni.

## Metoda i niezależne odniesienia

WłasneQ1/H8 dla gazu na dokładnym dopełnieniu bryłyP20C; powierzchnie
materiał/gaz są zgodne. B przenosi ciśnienia na siły i przyspieszenia na gaz:

    Ds*u-B*p=Hext*po
    (A+s²*C)*p=-s²*B.T*u

Sprawdzono B*1=Hi, A*1=0 oraz sumę C równą Vgas/Kbulk. Objętościowe całki
gradientu i r×gradientu są niezależnym sprawdzeniem pracy na granicy
i całkowitego pędu. Do energii sprężystej odjęto tylko numeryczny ruch
sztywny; pełne u pozostaje w masie i warunku gaz/ciało.

Moc wejściowa odpowiada omega²*U*Cs*U. Gaz bez strat ma średnią moc 0,
ale przechowuje energię sprężania i ruchu. Fazory są RMS; czynnik 1/2
dotyczy średniej energii, nie średniej mocy strat. Wzajemność macierzy
i dodatniość mocy sprawdzono oddzielnie.

Pusty prostopadłościan ma rozwiązanie analityczne. Dla pierwszych 12 modów
na najgęstszej siatce największa względna różnica wynosi około
**0,45148%**. Osobny zadany tłok odtwarza falę 1D,
również w punkcie, gdzie ciśnienie na wejściu jest zerowe. Błąd w tym
punkcie oceniano bez dzielenia przez znikające ciśnienie odniesienia.

## Średnia i lokalne ciśnienia

Zewnętrzne pola w lokalnym układzie modułu mają kształt:

    Phi0=1
    Phi1=1+(x-W/2)/W

Amplituda modalna każdego osobnego wymuszenia wynosi 1PaRMS. Drugi
profil ma wartości od 0,5 do 1,5 razy tej amplitudy; to scenariusz z gradientem,
nie pomiar ani prognoza konkretnego pola w pokoju.

| Pole | Częstotliwość | Amplituda średniej wewnętrznej | Przestrzenny RMS różnic |
|---|---:|---:|---:|
|Równomierny|20 Hz|5,45613 mPa|0,000125891 mPa|
|Z gradientem|20 Hz|5,45613 mPa|1,38198 mPa|
|Równomierny|80 Hz|5,4643 mPa|0,00201808 mPa|
|Z gradientem|80 Hz|5,4643 mPa|1,3832 mPa|

Duży procent różnic względem małej średniej nie jest dużym ciśnieniem
bezwzględnym. Podano obie wielkości. To zróżnicowanie przestrzenne
w liniowym modelu, nie nowe harmoniczne lub THD.
Port z gradientem opisuje pracę także na ruchu całej bryły: jego
uogólniony przepływ nie jest samą pochodną objętości obrysu.

![0D i3D oraz skala lokalnych różnic](../wyniki/81_P21B_0D_3D_i_zroznicowanie_cisnienia.png)

![Pole ciśnienia w rzeczywistej geometrii gazu modułu](../wyniki/82_P21B_pole_cisnienia_w_module.png)

## Siatki, punkty diagnostyczne i granica 0D

Przy wspólnych Hz w20–80 Hz największa zmiana admitancji n8→12 wynosi
3,9105%.
Zmiany pola ciśnienia i jego odchylenia zapisano osobno, także w Pa na 1 Pa
wymuszenia. Zgodna pojedyncza liczba nie dowodzi zbieżności każdego punktu.

Przy dodatkowych częstotliwościach 500–2200 Hz największa znaleziona zmiana
względem 0D wynosi 2,13387%.
Nie jest to maksimum ciągłego pasma lub fizyczny szczyt rezonansu.
Nie rozciągamy interpretacji bezstratnego gazu na rzeczywiste tłumienie.

Formalne zwiększanie A przy stałym C oznacza pomijalną bezwładność gazu.
Wydzielenie stałego modu ciśnienia zapobiega mnożeniu prawie stałego p
przez wielkieA. Cztery porównania z pełnym blokiem przy skali 1 potwierdzają
zgodność obu zapisów. Skalowanie nie jest ogrzewaniem powietrza.

**Osobna granica niskiej częstotliwości:** przy swobodnej bryle z niezerową
wypadkową siłą z gradientu ruch rośnie jak 1/omega². Gaz przyspiesza wraz
z bryłą, a jego gradient ciśnienia nie musi zaniknąć tylko przez obniżenie
częstotliwości. Wiodący wyraz wynosi:

    std(p)/Pmodal -> rho*abs(F_per_Pa)*sigma_x/(mdry+mgas)

Względny błąd pełnej macierzy portów skalarnego odniesienia 0D z masą
samego materiału zmierza wtedy do udziału masy gazu mgas/(mdry+mgas).
Nie dotyczy to każdego modelu 0D:spójną masę dodaną można uwzględnić
w modelu zredukowanym. Nie dopisuje się jej drugi raz do pełnego gazu 3D.
To inne pytanie niż mała zmiana portu objętościowego
przy równomiernym nacisku. Porównano tę niezależną asymptotykę z36 próbkami
20/80 Hz. Największe odstępstwa przy 20 Hz wynoszą
0,022812%dla zróżnicowania ciśnienia
i1,39028%dla błędu macierzy.
To porównanie skończonejf z granicą, nie żądanie ich dokładnej równości.
Przy stałej amplitudzie graniczny ruch stałby się duży; fizyczna mała
amplituda wymaga skalowania wymuszenia zomega² albo uwzględnienia podpór.

![Wzorce analityczne i formalne przejście do0D](../wyniki/83_P21B_wzorce_i_granica0D.png)

## Wpływ na skalarne obciążenie głównej komory

Dla identycznych modułów przy równomiernym p, Ca≥Ca_min i N≤16,
przy nieujemnych ReY oraz ImY w badanychf, najgorszą zmianę stosunku
impedancji otrzymujemy przy Ca_min oraz N=16. Uzasadniono monotoniczność
analitycznie, a punkty sprawdzono niezależnymi podstawieniami.

Minimum gazu przyjęto z istniejącej kontrolnej geometrii:około
78,8352 l, z umownym wyporem głośnika 6 l.
Wszystkie Ca powyżej tego minimum i N od 0 do 16 obejmuje warunkowy rachunek
w sześciu zapisanych częstotliwościach. Największa granica względnej
zmiany skalarnej impedancji wynosi około
**5,80229e-07**.

To nie dowód przewagi produktu, zmiany SPL w pokoju lub dominacji całego
briefu. Niejednorodny nacisk, wzajemne pole i rzeczywiste mocowanie modułów
pozostają osobnym zadaniem; nie wolno zastąpić ich tą granicą skalarną.

## Ograniczenia i następny krok

**Mocowanie jest odrębnym warunkiem.** Pole z gradientem daje wypadkową
siłę, mimo małej korekty odpowiedzi objętościowej. Dla narzuconego profilu
Phi 1 współczynnik poziomej siły wynosi
0,017N na 1 Pa amplitudyRMS.
To wynik całki po zamkniętej powierzchni, nie prognoza gradientu rzeczywistej skrzyni.

Dla modułu utrzymywanego nieruchomo na czterech punktach, przy rozstawie
z konfiguracjiP20A, ciężarze i wyporze w powietrzu, jedynie ściskających
kontaktach oraz bez kotew otrzymujemy następujący budżet quasistatyczny:

| Amplituda pola | Szczyt siły poziomej | Najmniejsza reakcja normalna | W ekranie 1%ciśnienia zewnętrznego |
|---:|---:|---:|---|
|1.0 Pa|0,0240416 N|1,71156 N|tak|
|100.0 Pa|2,40416 N|0,989025 N|tak|
|300.0 Pa|7,21249 N|-0,470645 N|tak|
|500.0 Pa|12,0208 N|-1,93032 N|nie|

Ujemna reakcja w tym schemacie oznacza, że założony nieruchomy układ bez
przenoszenia rozciągania nie zachowa czterech kontaktów przy takiej obwiedni.
Nie jest to obliczenie rzeczywistej odpowiedzi harmonicznej:mocowania mogą
mieć rezonans, poślizg, ruch i zmianę rozkładu reakcji. Przykład pokazuje,
dlaczego samego ciężaru lub samej zgodności litrów nie uznajemy za
kwalifikację mocowania. Potrzebne jest pole i dynamika głównej komory.

Największe zapisane reszty w całej rodzinie, w użytych normalizacjach:

| Kontrola | Wartość |
|---|---:|
| Mocy |6,93642e-12|
| Równania konstrukcji |1,01389e-09|
| Równania gazu |7,37095e-12|
| Pędu całkowitego |1,79633e-08|
| Wzajemności |1,21605e-13|

To dokładność rozwiązywania i weryfikacji zadanych modeli. Nie zastępuje
danych o kleju, MDF, pełzaniu, S–N, Gc, rzeczywistych stratach lub pomiarów.
Nie wyznaczono własnego THD produktu, bezpiecznej mocy lub końcowego
SPL w pokoju. Referencje i numeryczne progi odbiorowe pozostają odrębne.

**Jeden następny krok:P21C — główna komora z regulacją, wypełnieniem
i mocowaniem modułów.** Uwzględnić rzeczywiste niejednorodne pole
i porównanie sensownych proporcji przy wspólnym netto oraz wymaganym
zakresie regulacji. Obrys 504×684×504 mm pozostaje historycznym wariantem odniesienia,
wykluczonym przez limit głębokości 500 mm (U-026). Nowe geometrie muszą
spełniać ten limit w obu orientacjach; pilot pustej komory opisuje raport 050. Dwie sztuki muszą być wykonalne
w pokoju 4,6×3,7×2,5 m, RTVpo lewej/kanapa po prawej rzutu.

Opisy opinii z forów użytkownik odłożył do końcowej syntezy. Tutaj
nie rozszerzano ich ani nie przypisano im nowych ocen produktów.
KońcowyPDF iRelease 1 powstaną po całym programie, nie po samymP21B.

## Pliki i odtwarzanie

- [Wejścia](../dane/konfiguracje/p21b_gaz_przestrzenny_modulu.json).
- [Pierwotne źródła metody](../dane/zrodla/P21B_sprzezenie_i_postac_slaba.json).
- [Pola i energie](../wyniki/p21b_pola_i_energia.csv).
- [Macierze portów](../wyniki/p21b_macierze_admitancji.csv).
- [Kontrole niezależne](../wyniki/p21b_kontrole_niezalezne.json).
- [Granica obciążenia](../wyniki/p21b_granica_skalarnego_obciazenia.csv).
- [Warunkowy budżet sił gradientu](../wyniki/p21b_sily_przy_wymuszonym_gradiencie.csv).
- [Asymptotyka swobodnego ruchu](../wyniki/p21b_asymptotyka_swobodnego_ruchu.csv).
- [Manifest](../wyniki/manifest_gazu_przestrzennego_P21B.json).

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_gaz_przestrzenny_P21B.py

Zgodne 18 rekordów wznawia się po hashu wejść. Ich odczyt nie jest świeżą
niezależną replikacją. Pełny przebieg archiwizujący jest blokowany,
jeśli inny proces rzeczywiście utrzymuje blokadę aktywnegoP21B.
