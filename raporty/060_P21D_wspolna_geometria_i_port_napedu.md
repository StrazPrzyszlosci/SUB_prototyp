# Raport 060 — P21D: port akustyczny wspólnej geometrii i napęd

Data: 2026-10-31. **Symulacja warunkowa sztywnych przeszkód; nie pełne sprzężenie sprężystej konstrukcji ani pomiar.**

## Pytanie i wpływ na decyzję

Czy tę samą geometrię wręg/wkładów z P20D można sprowadzić do litrów
prostokątnej komory? Jak błąd portu wpływa na napęd i czy nieznany kształt
kosza może podważyć wniosek? Hipoteza: port przestrzenny zależy od przeszkód,
a jego względny błąd przy zerze reaktancji może znacznie przewyższać
zmianę samego ruchu napędu. Badanie rozstrzyga potrzebę dalszego sprzężenia
oraz właściwą skalę kontroli numerycznej, nie rzeczywisty ranking produktów.

## Wspólne wejście i jawne zastępstwa

Korpus1000×440×500, wnętrze956×374×456 mm, wszystkie11 brył wręg,
wycięta wokół nich tylna mata50 mm, stany modułów2/0,11/1,16/3
(duże/małe) z raportu057. Współrzędne pochodzą z tego samego generatora.
Przeszkody są sztywne, moduły hermetyczne; ich wewnętrznego gazu
nie dodajemy do głównej komory. Brak szczelin, mocowań i drgań tych ciał.

Kosz nie ma znanego rozkładu wyporności. Zamiast nazywać walec zawierający
ciałem stałym, porównano **dwa jawne zastępcze bloki po5 l**:
A250×100×200 mm, B200×125×200 mm. Oba mieszczą się w konserwatywnej
obwiedni za portem i nie kolidują z wręgami/modułami. Nie są skanem ani
rysunkiem kosza C02/C11/C06. Ten sam blok w porównaniach produktów to
kontrola modelowa; nie dowodzi identycznej wyporności rzeczywistych finalistów.

Mata: ZK z nieruchomym szkieletem, proste pory o promieniu0,2 mm,
rho_sucha20 i rho_włókna1380 kg/m³, phi=0,985507. To scenariusz materiału,
nie identyfikacja poliestru. Powietrze w modelu ma parametry MED z P21C2.
Nie utożsamiać scenariusza0,2 mm z rzeczywistym promieniem włókien.

Objętości geometrycznej domeny przed odjęciem ciała włókien:
150,087 /119,937 /100,587 l. Ciało włókien zajmuje w każdym stanie
0,3051 l. Pozostaje149,782 /119,632 /100,282 l powietrza.
Różnica wobec tabeli057 wynika z jawnego pominięcia osprzętu0,175 l
w polu przestrzennym; nie ukryto jej przez zmianę nazwy netto.
Podatność termiczna z matą pozostaje odrębnym wynikiem modelu.

## Równania, port i napęd

Wykorzystano nową instancję FV Helmholtza z P21C3, na siatkach dokładnie
dopasowanych do płaszczyzn wszystkich prostokątnych przeszkód i warstwy.

`(K−omega² C)p=j omega b Q`, `C=diag(Vcell/Kbulk)`.
Przewodność między komórkami:
`Aface / (rho_left*d_left + rho_right*d_right)`.

Źródło to dysk o Sd z danych T/S, środek x209/z228 mm we wnętrzu.
Udział w komórce całkowany po przecięciu koła z jej ścianą; suma udziałów1.
Port `Zrear=bᵀp/Q + j omega rho correction` uwzględnia odtworzenie
ciśnienia z centrum komórki na ścianę Neumanna. Jednostka Pa·s/m³.
Małe reszty algebraiczne nie są miarą błędu dyskretyzacji.

Dla napędu przy1 V RMS, osobne sinusy20/40/80 Hz:

```
Zm=Rms+j omega (Mms-eta*Mref)+1/(j omega Cms)+Sd² Zrear
Ze=Re+j omega Le
I=1/(Ze+BL²/Zm), v=BL I/Zm
Mref=8 rho a³/3, a=sqrt(Sd/pi), eta=0 lub1
```

Mms pozostaje efektywnym parametrem T/S. Dwie konwencje eta są jawnym
zakresem interpretacji tylnej masy powietrza, jak w052; żadna nie identyfikuje
Mmd. **Nie dodano ponownie frontowego promieniowania.** Zastępcza tylna
masa wynosi13,779 g dlaC02,13,146 g dlaC11,6,274 g dlaC06.
Rzeczywisty Mmd i promieniowanie skończonego frontu pozostają otwarte.

## Wykonany eksperyment i wyniki

45 rozwiązań z matą: trzy stany wkładów,20/40/80 Hz, C02 na dwóch
siatkach50/35 mm i dwóch blokach, C11/C06 na35 mm z blokiemA.
54 obliczenia napędu dla dwóch konwencji masy. Dodatkowe12 rozwiązań
C02 przy80 Hz: kroki25/18 mm dla obu bloków i trzech stanów,
do42496 niewiadomych. Cztery porównania pustej komory z niezależnym
szeregiem warstwowym i trzy granice0,2 Hz to osobne kontrole.

W pierwotnej siatce35 mm zmiana amplitudy przyspieszenia względem
adiabatycznego modelu0D o tej samej geometrycznej domenie, ze wszystkimi
stanami i obiema konwencjami masy:

| Kandydat | Zakres zmiany w skończonej próbie [dB] |
|---|---:|
| C02 | −0,905 do+0,413 |
| C11 | −0,628 do+0,255 |
| C06 | −0,623 do+0,212 |

To zmiana przy zadanym napięciu, nie maksymalny SPL ani THD. Odniesienie0D
ma Mms bez korekty i nie zawiera przestrzennej maty; tabela obejmuje razem
wpływy portu i dwóch konwencji masy. Nie interpretuje się jej jako samej
poprawy przez włókninę. Nie przeprowadzono wielokryterialnego rankingu
z tych trzech częstotliwości. Próbę C11/C06 należy rozszerzyć po określeniu
ich własnego obrysu w limicie głębokości.

## Flagi siatki i ich rozstrzygnięcie

Na50→35 mm znaleziono zmianę względną portuC02 przy80 Hz do29%.
Nie nazwano takiej siatki zbieżną. Dodatkowe25→18 mm dają:

| Stan | Blok | Re(Z),18 mm | Im(Z),18 mm | Zmiana portu względna | Zmiana względem skali0D | Zmiana amplitudy v [dB] |
|---|---|---:|---:|---:|---:|---:|
| 150 | A | 33,02 | −130,36 | 7,58% | 0,543% | −0,00327 |
| 150 | B | 33,32 | +27,81 | **42,86%** | 0,990% | −0,00592 |
| 120 | A | 63,43 | −636,98 | 1,48% | 0,403% | −0,00316 |
| 120 | B | 63,80 | −480,47 | 3,59% | 0,741% | −0,00568 |
| 100 | A | 306,31 | −284,07 | 4,20% | 0,626% | −0,00611 |
| 100 | B | 307,69 | −130,41 | 7,57% | 0,903% | −0,00858 |

Skala0D to `gamma*p0/(omega*Vdomain)`; nie wybierano jej po to, by
ogłosić mały względny błąd samego Z. Względna zmiana42,86% pozostaje
flagą portu bliskiego zeru. **Nie wykazano dokładności portu<1%.**
Jednocześnie jego wpływ na amplitudę prędkości C02 w tych sześciu
świadkach zmienił się do0,00858 dB. To właściwa dodatkowa informacja
dla decyzji o napędzie, bez certyfikatu błędu kontinuum lub całego pasma.
Nie przenosimy jej automatycznie naC11/C06 ani na naprężenia ścian.

Przy tej samej objętości5 l zmiana kształtu blokuA→B na18 mm daje
w trzech stanach zmianę portu równą5,48–8,42% skali0D, lecz zmianę
amplitudy v przy80 Hz około−0,0485 do−0,0502 dB. To dwa świadki
nieidentyfikowalności kształtu na podstawie samych litrów; nie są globalną
obwiednią wszystkich możliwych koszy.

## Niezależne kontrole i prawa fizyczne

Pusta komora z tą samą matą i źródłem: porównanie z rozdzielonym szeregiem
modów poprzecznych/rekurencją warstw, bez siatki FV. Na35 mm błąd portu
wynosi0,0231% przy20 Hz i1,1799% przy80 Hz. Nie wystarcza to do przyznania
tej dokładności przeszkodom. Prawdziwie niezależna kontrola dotyczy tej
granicy modelu, a nie całego rozwiązania z wręgami.

Przy0,2 Hz bez maty, ze wszystkimi przeszkodami/blokiemA, port zgadza się
z `−j gamma p0/(omega V)` do5,02e−6 względnie. To granica kompresji;
bezstratna komora nie tworzy dodatniej mocy czynnej. W badanych punktach
z matą Re(Z)≥0. Sumy gazu, integracja powierzchni źródła i reszty układów
są kontrolowane przy każdym budowaniu/rozwiązaniu.

Dodatkowo dwa pola przy80 Hz sprawdzono bilansem mocy samego gazu: moc portu odpowiada sumie strat lepkościowych na połączeniach i cieplnych w komórkach; obie składowe nieujemne. Równanie kontroli to `Re(Z)=sum(Im(g)/omega*|dp|²)−omega*sum(Im(C)*|p|²)` dlaQ=1. Wyniki `p21d_bilans_gazu.json`; to kontrola dyskretnej pasywności, nie osobna walidacja materiału.

Bilans wejścia napędu: `Re(I)=Re*|I|²+Re(Zm)*|v|²` przy1 V RMS;
54 reszty względne do4,21e−16. To algebraiczna kontrola mocy w danym
modelu; nie dowód poprawności materiału, Mmd lub promieniowania.

![Port i napęd](../wyniki/101_P21D_komora_i_naped.png)

## Decyzja, niepewność i zakres dalszej pracy

Zintegrowano **geometrię sztywnych wręg i wkładów** z przestrzennym
polem i napędem, lecz nie zamknięto sprężystego sprzężenia zespołu.
Macierz podatności paneli z P18E nie została tutaj bez kontroli dodana jako
pojedynczy „bonus litrów”. Konieczny jest wspólny port pracy gaz/panele,
a następnie aktualizacja ochrony czasowej; P25C nadal jest modelem0D.

C02 pozostaje rekomendacją warunkową. Ten etap nie wykazał nowej przewagi
C11 aniC06, ale również nie dowodzi, że ich odrzucenie jest zasadne.
Nieznane: pełne bryły koszy, moduły materiału/połączeń, podatność nowych
wkładów, parametry maty, promieniowanie frontu i własności termiczne napędów.
Część wymaga identyfikacji fizycznej; scenariusze podatności, wspólne
sprzężenie i dalsza numeryka nadal są możliwe komputerowo. Pełny program
pozostaje otwarty, bez końcowego PDF/Release1.

Odtwarzanie, w podanej kolejności:

```
OPENBLAS_NUM_THREADS=1 python skrypty/pole_zintegrowanej_geometrii_P21D.py
OPENBLAS_NUM_THREADS=1 python skrypty/dogesc_zintegrowana_komore_P21D.py
OPENBLAS_NUM_THREADS=1 python skrypty/raportuj_zintegrowana_komore_P21D.py
OPENBLAS_NUM_THREADS=1 python skrypty/bilans_gazu_P21D.py
```

Wejście geometryczne: p20d_geometria.json; parametry fizyczne i bloki
są jawnie zapisane w kodzie oraz `dane/konfiguracje/p21d_komora.json`.
Wyniki pierwotne i zagęszczenie zachowano osobno. Kod FV pochodzi zP21C3;
użycie go nie jest niezależną replikacją całej metody. Całościowy manifest
bieżącego etapu opisuje wersje i rzeczywiste zależności wejściowe.
