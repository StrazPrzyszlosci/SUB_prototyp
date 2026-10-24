# Raport009 — wykonanie N7/P08: przeciek i promieniowanie

Data:2026-10-23. Status: obliczenia i weryfikacja zredukowanego modelu,
bez identyfikacji rzeczywistej skrzyni. To raport cząstkowy; końcowyPDF
pozostaje odłożony do przejścia [programu30badań](../PROGRAM_30_BADAN.md).

## Pytanie i hipotezy

Czy rezystancyjny przeciek wpływa na ruch oraz SPL w sposób wymagający
uwzględnienia w regulowanym prototypie? Sprawdzamy:

1. H-N7-1: model redukuje się do wcześniejszego sealed przyRa→∞.
2. H-N7-2: straty są nieujemne, a zredukowany bilans mocy zamyka się.
3. H-N7-3: doSPL potrzeba sumy fazorów membrany i przecieku; sama membrana
   nie opisuje całkowitego pola.
4. H-N7-4: granice niskiej częstotliwości, szczelności i geometrii nie są
   automatycznie zamienne.

## Model, konwencje i dziedzina

Kod: [model_nieszczelnosci.py](../skrypty/model_nieszczelnosci.py).
FazoryRMS, konwencja exp(jωt), jednostkiSI, jednorodne ciśnienie komory,
sztywne ściany i liniowy przetwornik. Źródła akustyczne są małymi monopolami
w4π, w jawnej geometrii; nie ma pokoju ani dyfrakcji rzeczywistej skrzyni.

```text
Cab = Vb/(rho*c²)
a = 1/(Ra*Cab) = 2*pi*f_leak
h = s/(s+a)
U_mem = Sd*v
p_inside = -U_mem/(1/Ra+s*Cab)
U_leak = -a/(s+a)*U_mem
U_sum = h*U_mem
Z_box = Sd²/(1/Ra+s*Cab)
```

Prędkość membrany jest dodatnia na zewnątrz, dlatego wzrost objętości
komory obniża jej ciśnienie. Postać ze sztywnością dynamiczną unika
dzielenia przezω i pozwala osobno rozwiązaćDC:

```text
D = Mms*s² + Rms*s + 1/Cms + Sd²/Cab*h
Delta = (Re+s*Le)*D + BL²*s
x = BL*V/Delta
I = D*V/Delta
```

Przeciek rozpraszający nie jest modelem włókniny. Nie wyznaczono przekroju
szczeliny, jej bezwładności, szumu przepływu ani nieliniowości. Takie cechy
nie wynikają z samegoRa. Dwa eksperymenty rozdzielono: stałe f_leak oraz
stałeRa przy zmianieVb. Opisują inne warunki fizyczne.

## Promieniowanie i bilans energii

Sumujemy zespolone ciśnienia:

```text
p_total = rho*s/(4*pi) * [U_mem*exp(-s*r_mem/c)/r_mem
                         + U_leak*exp(-s*r_leak/c)/r_leak]
P_input = Re*|I|² + Rms*|v|² + (1/Ra)*|p_inside|²
```

Nie ma czynnika1/2, ponieważ fazory mają wartościRMS. Rms jest efektywnym
tłumieniem parametrówT/S; bez rozdzielenia danych nie utożsamiamy go wyłącznie
z ciepłem materiału. Moc dwóch monopoli policzono dodatkowo z członem
interferencyjnym i skontrolowano całką kątową. Jest diagnostyką pola,
**nie składnikiem ponownie doliczanym do powyższego bilansu**.

Nie zamknięto w tym etapie reakcji promieniowania skończonych powierzchni
w równaniu ruchu. Należy to wykonać wP11, rozdzielając masę powietrza i straty
już zawarte w katalogowychMms/Rms, aby uniknąć podwójnego naliczania.

## Wykonany eksperyment

Cztery modele źródłowe, objętości30/45/60/80/100/120l, f_leak0/1/3/10Hz,
trzy geometrie: równe drogi, przeciek35cm za membraną, przeciek35cm z boku.
Napięcie2,83Vrms, obserwator1m od środka membrany. To288konfiguracji oraz
1728rekordów dla20/25/31,5/40/63/80Hz. Osobno432rekordy dla stałegoRa.

| Kandydat / netto | f_leak | ZmianaSPL20Hz | ZmianaSPL40Hz | X20Hz / Xszczelne |
|---|---:|---:|---:|---:|
| RSS315HF-4 /60l |10Hz|−1,867dB|−0,918dB|0,9018|
| RSS390HF-4 /100l |10Hz|−2,120dB|−1,141dB|0,8759|
| RSS315HFA-8 /60l |10Hz|−1,964dB|−1,057dB|0,8918|
| SB34SWPL76-4 /60l |10Hz|−1,781dB|−0,712dB|0,9107|

Tabela dotyczy równych dróg i jednego napięcia, nie limitu maksymalnegoSPL.
Nie dowodzi stałej utraty poziomu ani wzrostu ruchu we wszystkich pasmach.
W pobliżu dolnego basu straty mogą zmniejszać ruch; przyDC mechaniczne
zachowanie jest inne niż dla szczelnego układu.

## Przypadki graniczne i wyniki kontroli

Weryfikator [sprawdz_nieszczelnosci.py](../skrypty/sprawdz_nieszczelnosci.py)
rozwiązuje osobno cztery równania pierwotne dlaI,x,p,U. Sprawdzono także
realizację w przestrzeni stanów i integracjęODE metodąRadau.

| Kontrola | Wynik |
|---|---|
|120modeli stanu, w tym granice szczelna iotwarta|Wszystkie zredukowane realizacje stabilne|
|Bilans zredukowany|Maksymalna względna reszta7,29e−16|
|Odrębny układ równań|Maksymalny względny błąd przemieszczenia7,03e−16|
|Regresja sealed przy4π|Maksymalna różnica względna ruchu8,88e−16|
|AsymptotyDC, Le=0 i wysoka częstotliwość|Zgodne w zbadanych granicach algebraicznych|
|Kwadratura kątowa promieniowania|Zgodna z analityczną formą interferencyjną|
|14klas błędnych wejść|NaN,inf, niedopuszczalne zera i znaki odrzucone|

To weryfikacja matematyki/numeryki, nie walidacja rzeczywistych osiągów.
Tak małe reszty nie są niepewnością fizyczną modelu ani parametruRa.

Najważniejsze rozstrzygnięcia graniczne:

- Przy dowolnym skończonymRa i f→0: x→BL·V/(Re·Ks), a gaz nie dodaje
  statycznej sztywności. W granicy szczelnej pozostajeKs+Kb. Kolejność granic
  ma znaczenie; początkowy statyczny stan szczelnej komory trzeba określić.
- Przy równych drogach przepływy znoszą się do pierwszego rzędu i formalnie
  p_total~ω³ przy stałym napięciu. Dla nierównych ustalonych odległości
  ogólnie pozostaje człon~ω². Nie przenosimy jednej asymptoty na każdą geometrię.
- PrzyRa→0 zerowa suma przepływów nie zeruje automatycznie pola dwóch
  przestrzennie rozdzielonych źródeł: pozostaje przypadek dipolowy.
- Le=0 jest prawidłową granicą; usunięto wcześniejszy zakaz tego wejścia.
  Dodano stabilne analityczneF3 dlaQ od1e−6 do1e6 zamiast arbitralnego bracketu.

## Pomocnicze warunki szczelności

Przebadano72progi pomocnicze maksymalnej zmianySPL w20–80Hz:0,1/0,5/1dB.
To **scenariusze badawcze, nie zatwierdzona specyfikacja**. DlaRSS390HF-4/100l
i równych dróg:

| Dopuszczona zmiana | f_leak graniczne | Ra minimalne [Pa·s/m³] | Stała czasowa minimalna |
|---|---:|---:|---:|
|0,1dB|0,4683Hz|481460|0,3399s|
|0,5dB|2,3322Hz|96671|0,06824s|
|1,0dB|4,6620Hz|48361|0,03414s|

Wykorzystano siatkę1001punktów i kontrolę2001punktów. To numeryczna ocena
siatki; nie jest globalnym dowodem przedziałowym w całym kontinuum.
Wyniki nie określają jeszcze dopuszczalnej szerokości szczeliny bez modelu
jej geometrii i przepływu. Są ilościowym wejściem doP19/P20.

## Wpływ na konstrukcję i dalszą pracę

Uszczelnienie frontu i regulacji objętości jest parametrem badawczym,
którego wpływ trzeba kontrolować podczas zmiany litrażu. Kompensowanie
znoszenia akustycznego samymEQ nie zastąpi kontroli ruchu i strat.
Klej i spoina muszą być ocenione także pod kątem zachowania szczelności
po cyklicznym obciążeniu i pełzaniu; obliczenie rodzaju kleju pozostajeP19.

Wybór jednego głośnika nie jest jeszcze zamknięty: użytkownik rozszerzył pulę
oSTX i inne marki. N7 będzie zastosowany także do modeli zakwalifikowanych
na podstawie pełnych danych producenta.

Artefakty: [CSV](../wyniki/n7_pasma.csv), [stałyRa](../wyniki/n7_stala_rezystancja.csv),
[kryteria](../wyniki/n7_kryteria_szczelnosci.csv), [kontroleJSON](../wyniki/n7_weryfikacja.json),
[wykres1](../wyniki/07_nieszczelnosc.png), [wykres2](../wyniki/08_przeciek_geometria_i_ruch.png).
