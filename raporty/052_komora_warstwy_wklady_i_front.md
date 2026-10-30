# Raport 052 — P21C2/P21C3/P18D: warstwa, wkłady i nowy front

Data: 2026-10-30. Wyniki obliczeń; brak pomiarów urządzenia.

## Komora z kołowym źródłem i porowatą warstwą

Zastosowano rozdzielenie modów poprzecznych w prostokątnej komorze.
Dla każdego modu kappa i warstwy: q²=omega²*rho/K−kappa²,
Zc=omega*rho/q, Ztył=−j Zc cot(qd). Kolejne warstwy składa rekurencja
Zin=(Zload+j Zc tan(qd))/(1+j Zload tan(qd)/Zc).
Port tłoka to suma epsilon_n epsilon_l b_nl² Zin/(W H),
gdzie b jest transformatą kołowego tłoka z raportu 051.

To model 3D ze zmianami ośrodka po głębokości; warstwa zajmuje cały
przekrój. Nie utożsamiać jej z matą na pięciu ścianach. ZK z nieruchomym
szkieletem, porowatość 0,98, promienie porów 0,05/0,2/1 mm są scenariuszami,
nie identyfikacją produktu. Warstwa tylna 0/25/50/100 mm; 9 finalistów,
100/120/140 l, 7 częstotliwości 20–80 Hz, zimne/gorące Re, dwie
konwencje tylnej masy powietrza i diagnostyczna podatność ścian:
**15120 punktów napędu**. Te prostokąty odpowiadają objętości netto,
ale nie odwzorowują rozpraszania przez kosz lub usztywnienia.

Mms jest efektywne. Zamiast dopisać bez kontroli cały port gazu, odjęto
0 lub 1 razy jedną stronę niskoczęstotliwościowej masy tłoka w odgrodzie
8 rho a³/3. To dwie jawne konwencje zastępcze, nie wyznaczenie Mmd.
Nie dodano ponownie frontowego promieniowania. Prawdziwy brak Mmd
pozostaje otwarty. Minimalne Re(Z) jest nieujemne w badanym zakresie.

Kontrole: redukcja do pustego portu P21C1 z błędem 7,8e−16; redukcja
jednorodnego modu do warstw 1D. Odrębna drabinka FV dla 12 kombinacji
mod/f (20/80/160 Hz, mody 00/10/12/33) i siatek 64/128/256/512:
największa końcowa różnica około 2,71e−5 względnie. Trzy świadki
ucięcia poprzecznego 100→200 zmieniają port do 3,53e−5 względnie.
To nie certyfikat całej ciągłej dziedziny materiału.

## Wkłady: rzeczywiste przeszkody przestrzenne

Zbudowano niezależny, trójwymiarowy model objętości skończonych
Helmholtza na siatce dopasowanej do prostokątnych granic wkładów.
Komora 836×414×456 mm, źródło C02 w (209,228) mm na froncie.
0/10/16 sztywnych zamkniętych modułów 180×170×100 mm, ułożonych
w prawej połowie. Ich gaz wewnętrzny nie został ponownie doliczony.
Tylna warstwa 50 mm albo brak warstwy. Model nie zawiera jeszcze
kosza, wszystkich wręg, okuć i podatności samych modułów.

Równanie FV: (K−omega² C)p=j omega Q. K zawiera harmoniczne
przejścia 1/rho przez granice ośrodków, C=V/Kbulk. Źródło całkowano
po przecięciu dysku z komórkami. Do ciśnienia środka komórki dodano
rekonstrukcję na powierzchnię z warunku Neumanna. Bez niej porównanie
z analitycznym naciskiem na tłok jest błędne.

36 rozwiązań: 3 liczby modułów × 2 wypełnienia × 2 siatki × 3 f.
Dodatkowe 4 rozwiązania przy 80 Hz: do 44990 niewiadomych.
Błąd portu pustej komory z warstwą względem niezależnego szeregu
spadł z 0,651% przy kroku 25 mm do 0,209% przy 16 mm.
Dla 16 wkładów i maty zmiana 40→25 mm wynosiła 1,08%; po dogęszczeniu
25→16 mm nadal 0,840%. Nie nazwano tego certyfikatem dokładności <1%.

| Wkłady | Mata | Różnica portu względem prostokąta o tej samej objętości, 80 Hz | Zmiana ostatniej siatki |
|---:|---|---:|---:|
| 0 | True | 0.210% | 0.443% |
| 10 | True | 3.469% | 0.451% |
| 16 | True | 5.871% | 0.840% |
| 16 | False | 3.649% | 0.269% |

Różnica dotyczy zespolonego p/Q, nie zewnętrznego SPL. Wniosek:
regulacja wkładami jest wykonalnym eksperymentem, ale nie jest dokładnie
równoważna pustej skrzyni o mniejszej głębokości.

## Nowy front z przesuniętym otworem

MITC4 z otworem wielokątnym zbieżnym do koła Ø355,8 mm, front 880×500 mm.
Warianty 22/33/44 mm, otwór centralny lub x=231 mm od lewej krawędzi,
12/24/36 podziałów na bok, kosz sztywny 10/15 kg. Łącznie 36 modeli,
do 7347 współrzędnych po redukcji. Masa kosza jest scenariuszem, nie
potwierdzonym Mnet RSS390HF-4. Brzeg zewnętrzny utwierdzony, kosz ciągle
sztywno związany z otworem: nie odwzorowuje ośmiu realnych śrub/uszczelki.

Przy przesuniętym otworze i 15 kg pierwsza postać wynosi około
180,5 / 289,6 / 388,0 Hz dla 22/33/44 mm. Statyczna podatność całego
portu frontu spada z 5,02e−9 do 0,813e−9 m³/Pa. Nowa siatka centralna
odtwarza macierz wcześniejszego kodu dokładnie; każda zachowuje pole
prostokąta po dodaniu otworu. Nie przenosimy tych liczb na pełną ramę,
luźny styk, naprężenia śrub, klej lub zmęczenie.

Diagnostyka innych ścian: nieusztywniony panel 836×456×22 mm przy
E=2 GPa, rho=800 kg/m³ ma pierwszą postać SSSS około 103 Hz.
Dlatego rekomendacja wymaga usztywnień. Umowne podparte pola około
280×300 mm dają około 395 Hz. Podparcia SSSS nie są dowodem, że konkretna
wręga zapewni takie zamocowanie; jej połączenie musi zachować tę drogę siły.

## Odtworzenie

`komora_warstwowa_P21C2.py`, `integracja_P29B.py`,
`wklady_przestrzenne_P21C3.py`, `dogesc_P21C3.py`,
`front_przesuniety_P18D.py`, `weryfikacja_i_geometria_P29.py`.
Uruchamiać kolejno z OPENBLAS_NUM_THREADS=1. Wyniki: p29b_*, p21c3_*, p18d_*.
