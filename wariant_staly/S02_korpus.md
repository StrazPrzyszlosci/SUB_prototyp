# S02. Złożony korpus i cztery podpory dla stałej komory 102 l

Do dalszych obliczeń wybrano A, niski korpus 816,8 × 473,4 × 394 mm. W trzech rozdzielczościach uzyskał najmniejsze wybrzuszenie tyłu i najmniejszą podatność całej obudowy. Najważniejsza zmiana względem [S01](S01_architektura.md) dotyczy doboru podpór. Rozkład masy wzdłuż głębokości powoduje wyraźną różnicę osiadania przodu i tyłu.

## Porównanie przy ciśnieniu 1 kPa

Jedna sztuka, korpus ustawiony na dolnej ścianie. Wspólne materiały, grubości i założenia obciążenia. Wyniki symulacji dla maksymalnego kroku 30 mm.

| Korpus | Masa modelu, kg | Wybrzuszenie tyłu względem naroży, mm | Podatność, cm³/kPa | Pierwsze trzy częstotliwości odkształceń korpusu, Hz |
|---|---:|---:|---:|---|
| A niski | 48,57 | 0,043 | 8,49 | 147 / 171 / 199 |
| B kwadratowy | 47,79 | 0,070 | 11,83 | 135 / 181 / 181 |
| C wysoki | 48,30 | 0,051 | 9,25 | 146 / 178 / 198 |

W modelu A i C dzieli około 1 Hz dla pierwszego modu korpusu, mniej niż zmiana przy zagęszczeniu siatki. Wybór A opiera się na podatności oraz możliwości wstawienia go do dolnej zabudowy i obrócenia do bocznej. Podatność to praca rozkładu sił odpowiadającego zamkniętej powierzchni, podzielona przez kwadrat ciśnienia. Służy do porównania reakcji mechanicznej na wspólne wymuszenie. Wyznaczenie SPL od ścian wymaga prędkości poszczególnych powierzchni, fazy, tłumienia i modelu promieniowania.

## Montaż i obrót

Na siatce 30 mm przednie stopy A przenoszą po 174 N i osiadają o 5,51 mm, tylne po 64 N i osiadają o 2,03 mm. Przy rozstawie rzędów 302,5 mm odpowiada to pochyleniu około 0,66°. W S01 podano 123 N na stopę przy równym rozkładzie. Dobór czterech jednakowych stóp na tę średnią pominąłby różnicę wysokości i zakres pracy elastomeru. Do prób przewidzieć poziomowanie pod obciążeniem i osobny dobór przedniej oraz tylnej pary na podstawie krzywych siła-ugięcie.

Rozkład masy przetwornika przyjęto zastępczo: 15 kg w płaszczyźnie frontu. Przesunięcie jego środka ciężkości o 60 mm w głąb przeniosłoby około 29 N z przedniej pary na tylną (15 × 9,81 × 0,060 / 0,3025). To analiza wrażliwości, rzeczywiste położenie środka masy i masy osprzętu trzeba wprowadzić z pomiaru. Przyjąć reakcje jako obciążenia roboczego modelu, a udźwig konkretnych podpór sprawdzić po zważeniu modułu.

Przy tej samej siatce 45 mm najniższa częstotliwość ruchu na stopach zmienia się z 3,2 Hz w poziomie do 2,2 Hz po obrocie A. Pierwsza częstotliwość odkształcenia korpusu wynosi w obu położeniach około 162 Hz. Małe drgania wokół równowagi z liniowymi stopami i nieruchomą podstawą pozwalają porównać położenia. Stateczność przy przechyle, utrata kontaktu i drgania cokołu oraz GK wymagają osobnego sprawdzenia.

## Model i kontrola dokładności

Model bryłowy HEX8 z pełnym całkowaniem 2 × 2 × 2 obejmuje wszystkie ściany, dwie warstwy frontu, zastępczy pierścień i jedną wręgę okienną. MDF ma E = 2 GPa i gęstość 800 kg/m³, stal odpowiednio 200 GPa i 7850 kg/m³. Przyjęto wspólny współczynnik Poissona 0,30. Udział otworu i stali w komórkach frontu wynika z próbkowania 8 × 8. Uśrednienie sztywności zakłada pełną współpracę pierścienia z płytą i pomija luz, osiem punktów docisku oraz poślizg. Węzły paneli na stykach połączono sprężynami proporcjonalnymi do powierzchni o jednakowej sztywności normalnej i stycznej. Nominalne 2 × 10¹¹ N/m³ jest założeniem. Przy zmianie o rząd wielkości w dół i w górę podatność A na siatce 45 mm wynosi odpowiednio 10,90 i 6,66 cm³/kPa, wobec 7,19 nominalnie.

Rozłożono ciśnienie na rzuty wewnętrznych ścian. Wypadkową brakującego parcia w otworze przeniesiono na obrzeże frontu. Lokalne pole ciśnień przy wrędze, reakcje pracującego napędu i sprzężenie z powietrzem wymagają kolejnego modelu. Stopy są sprężynami punktowymi, 31,6 kN/m w pionie i po 16 kN/m w obu kierunkach poziomych. Wybrano węzły najbliższe pozycji nominalnej 12 i 88 procent obu wymiarów podstawy. Współrzędne dla każdej siatki zapisano w wynikach. Analiza własna używa skupionej masy i wydziela ruch bryły sztywnej przez rzut ważony masą. Pierwsze sześć postaci odpowiada ruchowi na podporach.

| A, maksymalny krok siatki | Wybrzuszenie, mm | Podatność, cm³/kPa | Pierwszy mod odkształcenia, Hz |
|---|---:|---:|---:|
| 70 mm | 0,026 | 5,72 | pominięto |
| 45 mm | 0,035 | 7,19 | 162 |
| 30 mm | 0,043 | 8,49 | 147 |

Zmiana z 45 na 30 mm zwiększa podatność A o około 18%. W ścianie tylnej pozostaje jeden element przez grubość. Pełne całkowanie elementów liniowych może przesztywnić zginanie. Bezwzględne ugięcia i częstotliwości wymagają sprawdzenia elementami powłokowymi lub kwadratowymi, z niezależnym zagęszczeniem przez grubość oraz ustalonymi pozycjami podpór. Oddzielnie należy sprawdzić wpływ sposobu osadzenia pierścienia, przebieg postaci drgań i transmisję na rzeczywisty cokół.

Model i dane: [obliczenia](s02.py), [wyniki wszystkich przypadków](s02_wyniki.json), [kontrole](sprawdz_s02.py). Uruchomienie z katalogu projektu: najpierw `OPENBLAS_NUM_THREADS=1 python wariant_staly/s02.py`, następnie `python wariant_staly/sprawdz_s02.py`. Workflow na gałęzi porównuje przeliczone dane z zapisem referencyjnym, sprawdza równowagę podpór, sześć swobodnych ruchów elementu oraz energię odkształcenia przy jednoosiowym naprężeniu.

Przed zatwierdzeniem architektury do CNC priorytetem jest niezależne sprawdzenie zginania oraz zastąpienie idealnego pierścienia i punktowych stóp rzeczywistymi warunkami mocowania. Weryfikacja prototypowa obejmuje ważenie reakcji stóp, osiadanie po czasie i pomiar drgań korpusu oraz cokołu w obu orientacjach.
