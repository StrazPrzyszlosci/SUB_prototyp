# K33 — sztywna blokada i połączenie długiego ogranicznika

5 listopada 2026. **Wariant konstrukcyjny, CNC HOLD.** Kontynuacja K32.
Serwis nadal wyłącznie przez otwór głośnika. Nie zamówiono części.

## Zmiana, która usuwa spoinę klejową noska

Rekomendowany do dalszej kwalifikacji wariant krótkiej blokady to **jeden
frezowany element metalowy**: poprzeczka312×50×18 mm i integralny nosek
80×50×22 mm. Przestrzenny obrys zasadniczy pozostaje jak K31; w nasadzie
noska dodano dwa wewnętrzne promienieR4. Frezowanie wymaga osobnego wykonawcy
metalu, nie wynika z możliwości oferty na MDF. Kosztu i dostępności stopu
nie badano. Nie zakładamy, że wykonawca MDF wyfrezuje również metal.

Nie przyjęto dodatkowej płaskiej blachy przyklejonej do MDF: w tej konstrukcji
cała poprzeczka jest metalowa, a nosek nie ma oddzielnego połączenia.
W nastawie100 są cztery takie części; w120 druga krótka blokada jest
zastępowana wariantem długim. Zmianie nie ulegają osie M5 Y55/347 ani
płytki retencyjne K32. Kandydat M5×50 pozostaje wymiarowo zgodny nominalnie,
ale wymaga ponownego stosu tolerancji dla rzeczywistej obróbki metalu.

| Cecha | Wariant krótszy | Wariant długi, drugi rząd |
|---|---|---|
| Poprzeczka | metal312×50×18 | metal312×50×18 |
| Kontakt z wkładem | integralny nosek + nominalna podkładka4 mm | profil20×20×2, końcówka i nominalna podkładka2 mm |
| Połączenie ogranicznika | ciągły materiał | kołnierz80×50×4, cztery M4 |
| Obsługa | całe złożenie wyjmowane po odkręceniu dwóch M5 | tak samo; M4 nie są odkręcane wewnątrz skrzyni |

Promienie u nasady mieszczą się w oknie wręgi; ich obwiednie4×4×50 mm
ujęto w kontroli ruchu. Dokładny kontur z łukami jest w DXF obrysu XY.

## Długi ogranicznik: określona geometria połączenia

Płaski kołnierz znajduje się w X448–452, Y160–240, Z179–229.
Cztery otwory Ø5 mają osie Y180/220 i Z189/219. W poprzeczce odpowiadają
im gwinty M4 od strony X448, o **nominalnej użytecznej głębokości10 mm**.
Kandydat M4×12 przechodzi przez4 mm kołnierza i wchodzi8 mm w gwint.
Nie stosujemy podkładki w tym stosie wymiarowym. Gwint musi mieć
odpowiedni wybieg i głębszy otwór technologiczny; DXF nie określa jego
wiertła ani całej głębokości wiercenia. Pozostaje margines na to w18 mm
poprzeczki, lecz finalną technologię trzeba uzgodnić.

Obwiednia każdego łba to Ø8×4 mm. Profil20×20×2 zaczyna się na X452,
kończy na X747,1, ma długość295,1 mm i oś Y200/Z204. Jego końcowa zaślepka
2 mm ma być umieszczona **wewnątrz obrysu**, nie dodana do długości.
Podkładka2 mm dochodzi do wkładu zaczynającego się na X749,1.
Podkładki pozostają niezakwalifikowanym elementem kontaktowym.

Profil jest łączony z kołnierzem spoiną obwodową. Do przesiewu przyjęto
modelową grubość gardzieli2 mm i obwiednię spoiny24×24×2 mm; nie jest to
zatwierdzona instrukcja spawania. Gatunek metalu, spawalność, technologia,
odkształcenie kołnierza i właściwości strefy wpływu ciepła pozostają otwarte.
**Model SCAD zawiera obwiednie serwisowe**, także pełny prostopadłościan
profilu zamiast jego czterech ścian; nie należy eksportować go jako gotowej
bryły produkcyjnej. Kołnierz zamyka drugi koniec profilu; szczelność spoin
i zaślepki wymaga sprawdzenia, zanim doliczy się zamknięty gaz do wyporności.

Drogą obciążenia ściskającego jest wkład → podkładka → zaślepka/profil →
kołnierz → kontakt z poprzeczką → M5/płytki → wręga → korpus.
Śruby M4 zatrzymują zespół i przejmują ewentualne oderwanie; w osiowym
ściskaniu nie przypisuje się całej siły wyrywającej gwintom.
Połączenie nie polega na kleju, ale nie jest jeszcze zakwalifikowane.

## Sztywność z uwzględnieniem własnej masy

Obliczenie przybliżone: rozstaw podpór292 mm, przekrój50×18 mm, siła od
wkładów165,943 N według scenariusza K32, przyspieszenie5g. Dodano własną
bezwładność poprzeczki jako obciążenie równomierne i noska jako skupione.
Rzeczywiste podparcie, otwory, kontakt i naprężenie wstępne wymagają modelu
złącza. Model przyjmuje gęstość2700 kg/m³ i E=70000 MPa dla kandydata
metalowego — **są to wejścia modelu, nie certyfikowane parametry wybranego
stopu**. Dla MDF pozostają800 kg/m³ i E=2000 MPa.

| Wielkość | Odniesienie MDF | Kandydat metalowy |
|---|---:|---:|
| Masa poprzeczki | 0,225 kg | 0,758 kg |
| Masa noska z promieniami | 0,071 kg | 0,239 kg |
| Ugięcie w punkcie obciążenia | 1,881 mm | 0,061 mm |
| Naprężenie zginające przekroju nominalnego | 4,729 MPa | 5,305 MPa |
| Reakcje przy M5 | 90,79 /89,63 N | 108,02 /106,80 N |

Ugięcie maleje około31 razy, ale większa masa podnosi reakcje podpór.
Cztery krótkie blokady ważą brutto około3,987 kg zamiast1,181 kg;
otwory nie zostały odjęte. Trzeba uwzględnić ten wzrost w bilansie masy
całej skrzyni. Wynik1,881 mm różni się od1,771 mm K32 przez dodanie własnej
bezwładności; nie jest zmianą wynikającą z innej siły od wkładów.

Dla profilu pod przykładową siłą165,943 N: przekrój144 mm²,
naprężenie osiowe1,152 MPa i skrócenie0,00486 mm. Idealny Euler przy
przegubowych końcach daje62,45 kN, lecz **nie jest nośnością zespołu**:
nie obejmuje utraty stateczności lokalnej, mimośrodu, uszkodzenia spoin,
zaślepki i MDF. Średni wskaźnik obciążenia spoiny F/(80×2) wynosi1,037 MPa;
nie zastępuje oceny rzeczywistej spoiny. Przy hipotetycznym odrywaniu i
równym podziale siły przypada41,49 N na M4; nie zakładamy, że podział
pozostanie równy przy mimośrodzie. Nie podano momentów dokręcania,
naprężeń dopuszczalnych ani współczynników bezpieczeństwa.

## Kontrole montażu i dokumentacji

- Pięć pełnych zapisanych tras K30: cztery krótkie i jedna długa blokada,
  po poszerzeniu do312 mm i dodaniu promieni, kołnierza, obwiedni spoiny
  oraz łbów M4. Ciągłe osiowe przesunięcia nie kolidują nominalnie ze stałą
  konstrukcją, matą, wkładami odpowiedniego stanu ani retencją K32.
- Długi wariant sprawdzany bez przedniego wkładu M1N, zgodnie ze stanem120.
- Najmniejszy nominalny zapas promieniowy w otworze głośnika dla tego
  złożenia to17,39 mm. Nie jest to zapas dla dłoni, obracania lub tolerancji.
- Niezależny odczyt czterech DXF: liczby i położenia otworów/gwintów,
  zamknięte kontury oraz oba promienieR4. Jednostki mm.
- Ugięcie z całkowania sprawdzono niezależnym wzorem zamkniętym dla siły
  skupionej i obciążenia równomiernego; sprawdzono równowagę reakcji.
- SCAD kompiluje się do CSG. Nie wykonano fizycznego prototypu ani prób
  zmęczeniowych. Nowe trasy narzędzi M4 w skrzyni nie są potrzebne:
  kołnierz montuje się na wyjętej blokadzie. Wcześniejszy dostęp M5 ma
  niezmienione osie; konkretna nasadka i dłoń nadal niezakwalifikowane.

[Pliki i instrukcja](../dokumentacja/cnc/K33_BLOKADA_METAL_HOLD/README.md)
· [generator](../skrypty/k33_sztywna_blokada.py)
· [test niezależny](../skrypty/sprawdz_k33.py)
· [wyniki](../wyniki/k33_sztywna_blokada.json)
· [manifest](../wyniki/k33_manifest.json).

Odtworzenie: `python skrypty/k33_sztywna_blokada.py` oraz
`python skrypty/sprawdz_k33.py`.

## Następny krok

Geometria blokady przestała wymagać spoiny klejowej noska, a droga siły
w długim ograniczniku jest określona. **Następnie trzeba sprawdzić kontakt
M5/płytka/wręga i przeniesienie siły z wręgi do korpusu**, uwzględniając
większą masę blokad, napięcie wstępne i podatność MDF. Równolegle potrzebna
kwalifikacja konkretnego metalu, gwintów i spoiny. Nie należy wyprowadzać
nośności całego węzła ze sztywności samej poprzeczki. Rzeczywiste tolerancje,
MDF, kosz, terminal i bilans objętości nadal blokują wydanie produkcyjne.
