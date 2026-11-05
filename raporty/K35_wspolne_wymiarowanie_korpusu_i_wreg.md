# K35 — wspólne wymiarowanie korpusu i wręg według grubości płyt

5 listopada 2026. **Generator geometrii roboczej, CNC HOLD.** Kontynuacja K34.
Powstał działający model dziewięciu części: dwie warstwy frontu, tył,
dwa boki, dno, góra, wręga przednia i środkowa. Nie jest jeszcze generatorem
całego banku wkładów ani kompletnym eksportem produkcyjnym.

## Wspólna baza wymiarowa

Wariant zachowuje zewnętrzne1080×432×500 mm. Położenie bazowe przedniej
wręgi X448, środkowej X750, otworu głośnika X231/Z250 oraz wszystkie
osie śrub pozostają stałe. Rzeczywiste grubości zmieniają wymiary części
wewnętrznych i ich współrzędne lokalne. Nie przesuwamy globalnego okna
ani śruby razem z nową krawędzią wręgi.

**Założenia do obliczeń:** szczelina połączenia krawędziowego g0,2 mm
na stronę i szczelina laminacji frontu0,1 mm. Nie wybrano kleju i nie
zakwalifikowano tych wartości. Model opisuje wymaganą geometrię po
ustawieniu w przyrządzie; nie dowodzi uzyskania tych szczelin podczas klejenia.

Jeżeli `F=t_FR1+0,1+t_FR2`, to:

| Wielkość | Reguła |
|---|---|
| Wewnętrzna powierzchnia tyłu | Y=432−t_BACK |
| Początek boków/dna/góry/wręg | Y=F+g |
| Ich rozpiętość w Y | 432−t_BACK−F−2g |
| Początek wręg w Z | t_BOTTOM+g |
| Wysokość wręg | 500−t_BOTTOM−t_TOP−2g |
| Rozpiętość dna/góry w X | 1080−t_SIDE_L−t_SIDE_R−2g |
| Lokalna oś otworu wręgi | oś globalna minus początek wręgi |

Przy **syntetycznych**, niezmierzonych grubościach22 mm otrzymujemy:

- front wewnętrzny Y44,1 zamiast dawnego44;
- początek wręg Y44,3/Z22,2;
- obrys wręg365,5×455,6 zamiast366×456 mm;
- rozpiętość dna/góry w X1035,6 zamiast1036 mm.

To wynik jawnego dodania szczelin, nie gotowa lista cięcia. Front i tył
pozostają pełnymi panelami1080×500; boki zachowują pełną wysokość500.
Przestrzeń wewnętrzna oraz litraż wymagają ponownego bilansu po przyjęciu
rzeczywistych danych. Nie przenosi się automatycznie starych objętości K30.

## Co rzeczywiście zachowano

Przekształcenie zachowuje globalne obrysy wszystkich czterech okien każdej
wręgi. Zachowuje również osie ośmiu M5 i16 M3 wręgi K32: Y55/347,
Z88/204/320/426 oraz Z±32 dla retencji. R4 pozostaje parametrem okien.
Osie wpisane do JSON w układzie lokalnym zmieniają się zgodnie z pomiarem,
a ich ponowne przeliczenie na układ obudowy odtwarza te same wartości.
To kontrola współrzędnych, nie kwalifikacja nośności zwężonego pasa MDF.

Przebadano512 skrajnych kombinacji dziewięciu niezależnych grubości21,5/22,5 mm.
Niezależna kontrola sprawdza gabaryt zewnętrzny, szczeliny front/tył,
góra/dół i boki/dno oraz odtworzenie globalnych okien. Dodatkowy nierównomierny
zestaw grubości sprawdza24 osie otworów. Wszystkie te kontrole przeszły.

## Dlaczego sama poprawka wręgi nie zamyka projektu

Stare prowadnice i osprzęt K30/K32 mają sztywne współrzędne nominalne.
Model oznacza konkretne niezgodności zamiast ukrywać je przez przesuwanie
wkładów:

| Zmiana rzeczywistej grubości | Niezgodność starego banku |
|---|---|
| Przednia wręga22,5 przy przedniej powierzchni X448 | płytka4 mm kończy się na474,5 i zachodzi na płat kanału zaczynający się na474 |
| Środkowa wręga22,5 przy X750 | koniec772,5 zachodzi na szyny zaczynające się na772 |
| Wręga21,5 | zostaje0,5 mm przerwy do dotychczasowego końca szyny |
| Dno22,5 | przecina nominalne dolne części banku zaczynające się na Z22 |
| Góra22,5 | jej powierzchnia Z477,5 przecina nominalne górne części banku do478 |
| Prawy bok22,5 | wewnętrzna powierzchnia X1057,5 przecina ogranicznik do1058 |

**Żaden z512 narożnych zestawów nie jest automatycznie zgodny z całym
starym bankiem** — w szczególności obie skrajne grubości wręg wymagają
zmiany styku szyny lub osprzętu. Nie oznacza to niewykonalności konstrukcji;
oznacza, że współzależne części trzeba wymiarować razem. Diagnostyka obejmuje
wymienione styki, a nie wszystkie tolerancje skrzyni. Cieńsze dno/góra/bok
mogą też otwierać spoiny; tego nie należy traktować jako potwierdzonego
podparcia tylko dlatego, że nie ma kolizji.

Dodatkowa szczelina laminacji frontu zmienia położenie tylnej powierzchni
frontu. Kontrola24 osi nie zastępuje ponownej kontroli całej drogi wkładów,
rzeczywistej grubości frontu i kosza głośnika. Takie kontrole muszą korzystać
z jednego kompletnego modelu wszystkich zależnych części.

## Dane pomiarowe i zabezpieczenie eksportu

[Szablon pomiarów](../dane/k35_pomiary_korpusu.json) zawiera dziewięć `null`.
Nie wprowadzono fikcyjnych pomiarów. Wpis dotyczy lokalnej grubości konkretnej
części; pojedyncza wartość nominalna nie opisuje automatycznie całej partii.

Domyślny przebieg tworzy opisany jako syntetyczny JSON geometrii. Tryb
`--require-measured` wymaga dziewięciu skończonych liczb w badanym zakresie
21,5–22,5, statusu `measured` oraz rekordu pomiarowego. Przy pustym szablonie
odmawia działania **przed zapisem**. Test potwierdził niezmienność istniejących
wyników po odmowie. To walidacja formatu i zakresu, nie dowód prawdziwości
wprowadzonego pomiaru. Nawet po uzupełnieniu danych wynik pozostaje HOLD.

Nie wydano nowych DXF, bo generator uczciwie wskazuje otwarte styki banku.
Historycznych DXF K30–K33 nie nadpisano. W K35 nie ma kwalifikacji kleju,
pełzania, momentu śrub, metalu ani spoin K33.

[Kod](../skrypty/k35_korpus_z_pomiarow.py) · [test](../skrypty/sprawdz_k35.py)
· [wyniki512 zestawów](../wyniki/k35_korpus_z_pomiarow.json)
· [manifest](../wyniki/k35_manifest.json).

Odtwarzanie:

```
python skrypty/k35_korpus_z_pomiarow.py
python skrypty/sprawdz_k35.py
python skrypty/k35_korpus_z_pomiarow.py --require-measured
```

Ostatnie polecenie powinno odmówić przy dołączonym szablonie.

**Następny krok: dołączyć do tego samego modelu końce szyn, płaty kanałów,
ograniczniki i płytki mocujące, zachowując położenie wkładów.** W szczególności
rozwiązać dodatkowe0,5 mm za płytką i styki z dnem/górą, a potem ponownie
sprawdzić tory montażu. Dopiero spójny model z pomiarami i zakwalifikowanymi
szczelinami będzie podstawą nowych konturów CNC.
