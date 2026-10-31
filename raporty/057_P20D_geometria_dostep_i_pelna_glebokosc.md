# Raport 057 — P20D: wspólna geometria, dostęp i pełna głębokość

Data: 2026-10-31. Baza: main `4d79871616ca1fd37a4b12c07de2c3febdb8e054`.
**Wykonane badanie geometryczne; projekt badawczy, przed kwalifikacją mechaniczną.**

## Pytanie i hipoteza

Czy można połączyć limit całego urządzenia 500 mm, wręgi, tylną matę 50 mm,
regulację około 100/120/150 l i dostęp przez otwór stałego frontu?
Hipoteza: płytszy, szerszy korpus oraz zmienione moduły pozwolą znaleźć
konkretne tory montażowe, ale geometria nie potwierdzi nośności wręg i zamków.
Wynik wpływa na gabaryty i badania mechaniki/portu; nie rozstrzyga THD.

## Dane i granice

Odczytano oryginalne rysunki producenta C02/C11 w PDF oraz tekst STX;
rejestr URL, dostępu i zakresu oględzin: `dane/zrodla/p20d_zrodla_20261030.json`.
Rysunki obejrzano. C02: Ø388,4/otwór355,8/głębokość całkowita178 mm;
C11: Ø388/otwór358/głębokość200 mm; C06: Ø326/otwór288/głębokość174 mm.
Nie zidentyfikowano wyporności kosza ani całej spoczynkowej obwiedni membrany.
Głębokości katalogowej nie nazwano głębokością wystawania za wewnętrzny front.

Nieznane utrzymano jako **scenariusze**: efektywna utrata objętości na
przetwornik 2–8 l, osprzęt 0,05–0,30 l, MDF650–800 kg/m³,
statyczne wystawanie10–22 mm, tył0–8 mm. Nie są tolerancjami producentów.
Efektywna utrata na głośnik odnosi się do prostokątnej komory wewnętrznej:
obejmuje nieznaną korektę gazu w otworze frontu. Nie dodano drugiego razu
objętości całego walca kosza. Walec zawierający służy tylko kontroli kolizji.

## Model i równania

Osie x/y/z = szerokość/głębokość/wysokość, wnętrze od powierzchni frontu.
Wszystkie bryły parametryczne zapisano jako przedziały w mm. Dla AABB:
`V=prod(hi-lo)`; kolizja to dodatnia długość przecięcia na wszystkich osiach.
Objętość sumy kontrolowano odrębnym podziałem przestrzeni na wszystkich
płaszczyznach granicznych. Objętości w litrach otrzymuje się dzieląc mm³ przez10⁶.

`Vnet=Vwnętrza−Vwręg−Vmodułów−Vgłośnika_eff−Vosprzętu−Vciała_maty`.
`Vciała_maty=Vobwiedni_maty*rho_sucha/rho_włókna`.
Przyjęto rho_sucha20 i rho_włókna1380 kg/m³, stąd phi=0,985507;
w stresie10–30 i1300–1400 kg/m³. Wycięcia maty przy wręgach odjęto raz.
Pory maty nadal należą do powietrza. Podatność efektywna nie jest Vnet.

Przebadano25 korpusów: W880/940/980/1000/1020 × D440/450/460/470/480,
H500 mm; front44, pozostałe ściany22 mm. Kolizje wykluczają całą rodzinę
880/940 mm z tym konkretnym układem, bez dowodu niemożliwości innych rozwiązań.

## Dwa konkretne warianty

| W×D×H korpusu [mm] | Puste wnętrze [mm] | Wręgi [l] | Netto bez wkładów, nominalnie [l] | Przedział stresowy [l] |
|---|---|---:|---:|---:|
| 980×450×500 | 936×384×456 | 1,68168 | 156,742 | 151,441–162,032 |
| **1000×440×500** | 956×374×456 | 1,65264 | **155,907** | **150,598–161,205** |

Nominał zakłada efektywną wyporność5 l i osprzęt0,175 l. Przedziały
obejmują rozmiary/grubości: ±2 mm wymiarów wewnętrznych, ±5% objętości wręg
jako dodatkową oś stresu oraz wskazane zakresy materiału/kosza/osprzętu.
Nie są przedziałami ufności. Masa samych paneli wariantu1000 mieści się
w modelu34,18–42,07 kg; wręgi1,07–1,32 kg. Głośnik, wkłady, zamki,
maskownica i powłoka pozostają dodatkowymi masami. Nie podano masy gotowego urządzenia.

Dwie ramy okienne mają x426–448 i691–713 mm dla W1000. Pasy górny,
dolny i tylny22 mm; **przedni pas tylko10 mm głębokości**. To wynik wymogu
dostępu, a nie potwierdzenie odpowiedniej sztywności. Za koszem dodatkowa
trójstronna rama x198–220, od y220; bez przecinania jego obwiedni.
Nie wywodzimy skuteczności wręg z idealnego podparcia płyt P18D.
Nowy podzespół mechaniczny bada P18E; pełne połączenie z frontem pozostaje otwarte.

## Regulacja i kolejność montażu

16 nowych dużych modułów210×150×100 mm, objętość obrysu3,15 l,
oraz4 małe180×100×100 mm,1,8 l. To **nowe geometrie**:
nie przenosi się automatycznie mechaniki modułu3,06 l z P20C.
Duże: dwie kolumny, cztery rzędy, dwie warstwy w głębokości.
Małe: dwa pola za koszem, dwa poziomy; y218–318 mm.
Mata zaczyna się na y324 mm w wariancie440, nominalny prześwit6 mm.

| Duże/małe wkłady | Nominał1000×440 [l] | Stres1000×440 [l] | Nominał980×450 [l] |
|---|---:|---:|---:|
| 2/0 | 149,607 | 144,230–154,972 | 150,442 |
| 11/1 | 119,457 | 113,752–125,148 | 120,292 |
| 16/3 | 100,107 | 94,187–106,012 | 100,942 |
| 16/4 | 98,307 | 92,364–104,235 | 99,142 |

Wkłady wymagają kalibracji liczby/małych elementów po określeniu rzeczywistej
wyporności. Nie zagwarantowano dokładnie100/120/150 l dla każdego egzemplarza.
Rozmiary modułów ±0,5 mm uwzględniono w obwiedniach objętości.

Ruch jest czystą translacją prostopadłościanów. Wyznaczono graf położeń
środka przy płaszczyznach rozszerzonych przeszkód. Każdy zwrócony odcinek
sprawdzono **ciągle**, przez sumę Minkowskiego przesuwanej bryły.
Powiększenie o3 mm obejmuje obwiednię montażową; nie identyfikuje konkretnego zamka.
Przez otwór przechodzi przekrój z narożnikiem w odległości120,30 mm,
poniżej najmniejszego badanego promienia otworu144 mm.

Dla obu wariantów: **20/20 torów, po270 odcinków**, z uwzględnieniem
wcześniej włożonych modułów, wręg i maty. Małe montowane pierwsze;
dalej dalsza kolumna dużych, warstwa tylna przed przednią, rzędy skrajne
przed środkowymi. Usunięcie części modułów nie dodaje przeszkód:
wybrane stany litrażu mają te same zachowane tory. Demontaż w odwrotnej kolejności.

Pierwszy układ z pasem22 mm blokował kolejne wkłady mimo bezkolizyjnych
pozycji końcowych. Zmiana kolejności pomogła tylko częściowo; tor całej
warstwy uzyskano dopiero po zmniejszeniu przedniego pasa do10 mm.
To ujawniona zależność serwisu i sztywności, nie ukryta korekta wyniku.

Niezależna kontrola zajętości na17/33 stacjach każdego odcinka dała zgodność
z ciągłym testem. Samo próbkowanie nie stanowi dowodu; dowodem dla klasy
translacji jest test objętości omiatanej. Sprawdzono też permutację osi
przy obrocie90°. Obrót bryły zachowuje kolizje; **nie weryfikuje sił grawitacji**.
Dla maty wymagane są wycięcia i podtrzymanie w obu orientacjach.

## Pełny limit głębokości

`Dcałość=Dkorpusu+Pspoczynek+Xpeak+5+2+3+Ptył+2 [mm]`.
5 to szczelina,2 ugięcie maskownicy,3 jej grubość,ostatnie2 to budżet tolerancji.
Są to wymagania/scenariusze nowego projektu osłony, bez danych konkretnego wyrobu.
Xpeak równy katalogowemu Xmax jest jedynie ekranem geometrycznym;
nie utożsamia się Xmax z bezpiecznym niskim THD.

| Korpus | C02 pełny obrys [mm] | C11 [mm] | C06 [mm] |
|---|---:|---:|---:|
| 440 mm | **476–496** | 489–509 | **477–497** |
| 450 mm | 486–506 | 499–519 | 487–507 |
| Dawne480 mm | 516–536 | 529–549 | 517–537 |

**Wariant440 jest roboczym kandydatem do dalszego sprzężenia dla C02.**
450 mm nie spełnia całego przyjętego zakresu osłony. C11 wymaga innej
maskownicy, płytszego korpusu lub ograniczenia ruchu; nie jest odrzucony
z porównania elektroakustycznego. Nie znamy jeszcze rzeczywistego
Pspoczynek i reakcji osłony na nacisk, więc obrys nie jest fizycznie zatwierdzony.

![Geometria i głębokość](../wyniki/100_P20D_geometria.png)

## Zamki, szczelność i bramki

Model zawiera obwiednię3 mm dla mocowania modułów, a terminal/przewody
jako zakres objętości i wystawania. Nie zawiera zidentyfikowanego zamka,
dłoni, śrubokręta, łuku gięcia przewodów ani przewodów przecinających tory.
Żaden luźny stos nie jest dopuszczoną konstrukcją. Trzeba doprojektować
mocowanie dodatnie z dostępem od otworu, obliczyć jego siły/ugięcia oraz
uwzględnić w geometrii. Rezerwa obwiedni nie zamyka tej pracy.
Nowe wkłady wymagają ponownego modelu ich podatności i szczelności.

Status: geometria i tory w opisanej klasie sprawdzone; **pełna zintegrowana
konstrukcja nadal niezamknięta**. Potrzebne: skończona sztywność wręg,
spoiny i mocowania, front/basket/grawitacja, wytrzymałość i zmęczenie,
przestrzenny port tej geometrii oraz szczegóły osłony. Brak parametrów
materiału pozostawia warunki pomiarowe, ale nie zwalnia z obliczalnego
badania wariantów sztywności. Brak zgody na CNC/produkcję z tego raportu.

## Odtwarzanie i dowody

`OPENBLAS_NUM_THREADS=1 python skrypty/geometria_zintegrowana_P20D.py`.
Wejście `dane/konfiguracje/p20d_geometria.json`; wynik zawiera wszystkie
bryły, tory i rozstrzygnięcia, nie tylko tabelę: `wyniki/p20d_geometria_wyniki.json`.
Dokładny podział objętości i suma rozłącznych brył zgadzają się do1e−4 mm³
w wybranych wariantach. To kontrola arytmetyczna, nie fizyczna dokładność wykonania.
Przyszłe kroki i macierz P01–P30: raport056 oraz aktualizacja programu.
