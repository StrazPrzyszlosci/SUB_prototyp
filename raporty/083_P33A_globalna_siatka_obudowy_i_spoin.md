# Raport 083 — P33A: pierwszy zintegrowany model siatkowy korpusu, frontu i połączeń

**31 października 2026 | Wykonane: 14 modeli globalnych, trzy gęstości siatki, trzy scenariusze sztywności spoin, pięć testów masy i wręg.**

> **Granica dowodu:** to **uproszczony globalny model płytowo-belkowy o trzech translacyjnych stopniach swobody na węzeł**. Nie jest to zweryfikowany pełny MES powłokowy (MITC4, 6 DOF/węzeł) ani 3D C3D8. Nie nadaje się do kwalifikacji konstrukcji do CNC, do obliczania naprężeń miejscowych w spoinach ani do deklarowania rzeczywistych częstotliwości rezonansów gotowego subwoofera.

## 1. Po co liczymy cały korpus?

Poprzedni etap P31B/P32A badał jedną płytę z dwiema sprężystymi liniami podparcia. Rzeczywista skrzynia przenosi siły przez **sześć ścian, ich naroża, wręgi, masę kosza i układ podparcia**. W takim układzie każde z tych miejsc może zmienić sposób ruchu całości. Celem P33A jest **badanie wrażliwości**, przygotowanie spójnego portu obciążeń i odnalezienie błędów geometrii przed dojrzałym MES.

![Sześć ścian, wręgi i kosz — model energetyczny](../wyniki/p33a_siatka_calej_skrzyni.svg)

![Wrażliwość odpowiedzi statycznej na siatkę i połączenia](../wyniki/p33a_zbieznosc_ugiec.svg)

## 2. Geometria i zakres wejścia

Korpus P30E/P31C **1020×425×500 mm**, płyty MDF 22 mm, front 44 mm, otwór Ø355,8 mm, oś kosza x=231 mm, z=250 mm. Wewnętrzne dwie wręgi uproszczono do belek na x=426 i 701 mm. **Nie odwzorowano** tylnej ramy U ani szczegółowych geometrii modułów, kołków, szyn, kosza i uszczelki. Wkłady reprezentuje tylko sztuczny rozkład masy. Mata 50 mm nie otrzymuje tu sztywności.

Płyty reprezentuje siatka o 3 translacyjnych DOF/węzeł, ze składnikami energii rozciągania, zginania i skręcania. Pozwala ona objąć sześć ścian i sprzężenie naroży. Nie odwzorowuje pełnego stanu skręcenia/obrotu powłok ani rzeczywistych tensorów naprężeń. Połączenia naroży są sprężynami przesunięć o nieznanym współczynniku, **bez odrębnej energii momentu obrotowego**. Wybór modeli tłumaczą poniższe warunki.

| Warunek | Wartość hipotetyczna |
|---|---|
| E MDF, rho, nu | 2,1 GPa; 730 kg/m³; 0,30 |
| Rozmiar docelowej siatki | 140, 105, 80 mm |
| Sztywność wiązań naroży i wręg | 3×10⁶ / 3×10⁷ / 3×10⁸ N/m² |
| Obciążenie statyczne | 1000 Pa ciśnienia na powierzchnię, z umownym przeniesieniem przez kosz |
| Mocowanie na stopach | 1,5 MN/m dla składowych przesunięcia na 4 narożach |
| Przykładowe masy | kosz 15 kg, moduły 8 kg; osobne warianty 0/12/18 kg oraz 14 kg modułów |

**Żadna z mas, wartości sztywności lub sił nie pochodzi z kalibracji fizycznej obudowy.** To celowo jawny przegląd zależności. Wszystkie częstotliwości własne w raporcie są częstotliwościami sztucznego układu modelowego, w którym również stopy mogą drgać.

## 3. Walidacja poprawności odwzorowania otworu

W pierwszej wersji testu zwykłe odrzucanie całych komórek siatki zbyt mocno powiększało otwór. Ten błędny wariant **odrzucono**. Zastosowano całkowanie obszaru MDF na 10×10 podkomórkach każdego czworokąta frontu.

| Krok siatki | Numerycznie usunięte pole | Pole koła Ø355,8 mm |
|---|---:|---:|
| 140 mm | 0,100110 m² | 0,099426 m² |
| 105 mm | 0,100025 m² | 0,099426 m² |
| 80 mm | 0,099400 m² | 0,099426 m² |

W najdrobniejszej siatce błąd *pola* spadł do około 0,027%, lecz **błąd sztywności przy krawędzi otworu nie jest tak samo ograniczony**. Dla realnego zwolnienia do CNC konieczne są wyższej jakości elementy powłokowe/sześcienne z dokładnym pierścieniem frontu.

## 4. Wynik 9 podstawowych analiz

Maksymalne modelowe ugięcia normalne przy zadanym porównawczym ciśnieniu:

| Krok siatki | Podatne wiązania 3×10⁶ | Pośrednie 3×10⁷ | Sztywniejsze 3×10⁸ |
|---|---:|---:|---:|
| 140 mm | 430,75 µm | 347,59 µm | 338,30 µm |
| 105 mm | 411,45 µm | 330,68 µm | 321,59 µm |
| 80 mm | 420,62 µm | 335,56 µm | 325,88 µm |

Między dwiema najdrobniejszymi siatkami w wariancie pośrednim ugięcie zmienia się o **1,47%**. Najniższa obliczona częstość całego, **umownie podpartego** zespołu zmienia się z 34,128 na 33,878 Hz, czyli o 0,73%. Wcześniejsze błędy z P31B pokazują, dlaczego nie wolno mylić zbieżności liczb z walidacją fizyczną.

W tym modelu usztywnienie połączeń od 3×10⁶ do 3×10⁸ N/m² zmniejsza modelowe maksymalne ugięcie w siatce 80 mm z 420,62 do 325,88 µm. **Nie wynika z tego, że wymiana kleju zapewni taki sam efekt w realnym korpusie** — model naroży jest uproszczony.

## 5. Masa i wręgi

Przy siatce 105 mm i pośredniej sztywności wiązań:
- model bez dodatkowych mas głośnika i wkładów: najniższa częstość ok. **43,45 Hz**;
- sztuczna masa 12 kg kosza, bez modułów: **37,97 Hz**;
- masa 18 kg kosza, bez modułów: **35,63 Hz**;
- masa 15 kg kosza i 8 kg wkładów: **34,13 Hz**;
- masa 15 kg kosza i 14 kg wkładów: **32,14 Hz**.

Te częstotliwości obejmują również podporowe ruchy całości, nie są przypisanymi pomiarami „pierwszego rezonansu ściany”.

Usunięcie dwóch obwodów belek/wręg daje ugięcie 346,19 µm zamiast 330,68 µm. Spadek po ich dołożeniu wynosi w tym modelu około **4,5%**, a zmiana częstotliwości najniższego trybu nie jest jednoznacznie korzystna z powodu dodatkowej masy i sposobu podparcia. **Nie oznacza to, że wręgi są zbędne** — brakuje lokalnej ramy U, pełnych przekrojów, spoin i rzeczywistych obciążeń.

## 6. Co badanie naprawdę wykazało, a czego nie?

**Wykazano w ograniczonym modelu:**
- jest możliwe numeryczne sprzęgnięcie sześciu ścian, dwóch wręg, sprężystych naroży, kosza i wkładów w jednym układzie energetycznym;
- masa kosza i modułów silnie wpływa na częstotliwości globalnego układu;
- podatność naroży jest krytycznym parametrem i nie może być z góry utożsamiana ze sztywnym połączeniem;
- poprawne pole otworu frontu wymaga całkowania geometrycznego, a nie wycinania całych komórek.

**Nie wykazano:** globalnej rzeczywistej pierwszej częstotliwości skrzyni, lokalnej wytrzymałości i zmęczenia spoin, ugięcia kosza w mm przy rzeczywistej mocy, zniekształceń akustycznych lub bezpieczeństwa transportowego. Wcześniejsza masa MDF P30E dla 120 l (~47 kg) zawiera inne składniki niż masa płyt i samych belek w P33A (~43 kg): nie wolno utożsamiać tych modeli masowych.

## 7. Następna konieczna bramka — P33B

Aby przejść z wrażliwości numerycznej do dokumentacji konstrukcyjnej, potrzebne są **pełne elementy powłokowe 6DOF lub bryłowe C3D8/C3D20**, rzeczywiste krzywe moment–obrót spoiny, rzeczywisty szablon otworu i mocowania, kontakty oraz lokalna siatka wokół ośmiu (lub właściwej liczby) śrub kosza. Potem ponowna analiza 20–120 Hz z portem ciśnienia P21G dla 100/120/150 l i co najmniej trzema zagęszczeniami.

**Decyzja:** zostawić **1020×425×500 mm, 120 l nominalnie** jako hipotezę konstrukcyjną; **nie akceptować jeszcze cięcia CNC**. Główne badania blokujące to kalibracja MDF/spoin, odwzorowanie kosza i przejście na poprawny model powłokowy.

## Odtwarzanie

`python skrypty/p33a_global_shell_network.py --out wyniki/p33a`

Python 3, NumPy, SciPy, Matplotlib. Skrypt odtwarza 14 przypadków, pełen JSON oraz 2 wykresy PNG lokalnie. W repozytorium dodatkowo zamieszczono krótsze `wyniki/p33a_globalny_model_podsumowanie_20261031.json` i 2 objaśniające wykresy SVG. Wyników nie należy mylić ze zwalidowanym MES całej obudowy.
