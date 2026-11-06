# K32 — płytka pozostająca na miejscu po wykręceniu blokady

5 listopada 2026. **Projekt nominalny i obliczenia przybliżone; CNC HOLD.**
Kontynuacja K31, bez klapy serwisowej. Korpus 1080×432×500 mm.

## Konkretna zmiana konstrukcyjna

Zamiast luźnej płytki 18×30×4 mm przyjmujemy osiem płytek metalowych
**18×80×4 mm**, każdą z centralnym gwintem M5 oraz dwoma gwintami M3
w odległości ±32 mm od osi M5. Dwie dodatkowe śruby M3 przechodzą przez
wręgę MDF22, pozostając zamontowane podczas odkręcania głównej śruby M5.
Zapewniają geometryczne ograniczenie obrotu oraz zatrzymanie płytki w osi X.
Nie polegamy na kleju przyklejającym metal do MDF.

| Element | Wymiar / położenie nominalne | Status |
|---|---|---|
| Płytka, 8 szt. | X470–474; Y względem osi ±9; Z względem osi ±40 mm | Metal i obróbka do kwalifikacji |
| Osie główne | Y55 i347; Z88,204,320,426 mm | Jak w K31 |
| Gwinty M3, 16 szt. | Z osi głównej ±32 mm | Rozstaw 64 mm |
| Przeloty we wrędze | Ø4 dla M3; istniejące Ø6 dla M5 | Wiercenie w płaszczyźnie, nie w krawędzi |
| Śruba retencyjna | M3×30, długość pod łbem | Kandydat wymiarowy, nie wybrany produkt |
| Obwiednia łba | Ø6×3 mm; X445–448 | Założenie do modelu |
| Odsunięcie łba od poprzeczki | 4 mm w Z | Nominalne, przed tolerancjami |

M3 przechodzi przez 22 mm wręgi, 4 mm płytki i nominalnie wystaje 4 mm.
Nie zakłada się zatapiania łba w MDF. Dodatkowe otwory są poza zakresem
wysokości 50 mm poprzeczki, więc nie wymagają jej podfrezowania.
Przy nominalnym luzie Ø4/M3 maksymalny mały obrót do kontaktu pary trzpieni
jest rzędu 1/64 rad ≈0,90°. To ograniczenie obrotu, nie bezluzowe ustalenie.
Nie przenosić dokładności tego oszacowania na rzeczywisty gwint i otwory.

Płytki należy przykręcić do wręgi **przed zamknięciem korpusu**. Potem regulacja
objętości nadal wymaga tylko wykręcenia M5 przez otwór głośnika; M3 pozostają
na miejscu. Nie wykazano drogi wymiany uszkodzonej płytki w gotowej skrzyni.
Zabezpieczenie M3 przed samoodkręcaniem pod wpływem drgań nie jest jeszcze
wybrane ani zbadane; retencja działa pod warunkiem pozostawania śrub w gwincie.

## Co sprawdzono geometrycznie

Generator odczytuje geometrię K30 oraz zapisane trasy montażowe i stosuje
poprawione położenia K31. Sprawdza osiem wydłużonych płytek, 16 łbów i16
trzpieni względem stałej konstrukcji oraz 21 ciągłych przesunięć: osiem wkładów,
pięć wariantów blokady i osiem podejść modelowego narzędzia. Brak kolizji
w tych nominalnych scenach. Trzpienie celowo przecinają wręgę w przelotach;
tego zamierzonego kontaktu nie klasyfikujemy jako kolizji.

Sprawdzenie jest przyrostowe względem K30/K31, z prostopadłościennymi
obwiedniami. Nie obejmuje pełnego stosu tolerancji nowego złącza, dłoni,
konkretnego klucza ani ugiętej konstrukcji. Nie jest globalnym dowodem
przeprowadzenia dowolnej części dowolnym ruchem 6DOF.

Niezależny test ponownie odczytuje dwa DXF: wręga ma24 przeloty (8 głównych
+16 nowych); płytka ma obrys18×80 oraz trzy symbole gwintów we właściwych
miejscach. **Okręgi na warstwach THREAD_M3/M5 oznaczają średnice nominalne
gwintów, nie średnice wierteł pod gwint.** Nie wolno potraktować ich jako
ścieżek frezowania. Płytka wymaga odrębnej obróbki metalu; ograniczenie
minimalnego boku50 mm oferty MDF nie jest specyfikacją wykonania metalu.

## Droga siły i istotny wynik dla poprzeczki

Obciążenie wkładu w kierunku otworu przechodzi kolejno przez jego ściankę,
podkładkę kontaktową, nosek lub wydłużony ogranicznik, poprzeczkę,
śruby M5, płytki i wręgę, a następnie połączenia wręgi z korpusem.
Nowe M3 zabezpieczają pozycję płytki; **nie przypisujemy im całej osiowej
siły zatrzymującej wkłady**, gdy płytka opiera się o wręgę.

Przesiew statyczny przyjmuje dwa duże zamknięte wkłady, przekładkę8×260×96,
gęstość MDF800 kg/m³ i dodatkowe0,2 kg na każdy wkład. Wszystkie te założenia
obciążeniowe są scenariuszem, nie pomiarem ani wymaganiem normowym.
Nominalną masę MDF obliczono jako różnicę objętości prostopadłościanów;
nie odjęto szczelin klejowych. Przy przyspieszeniu5g otrzymano:

| Wielkość | Wynik modelu |
|---|---:|
| Masa obciążająca blokadę | 3,384 kg |
| Siła w kierunku X | 165,943 N |
| Reakcje przy osiach Y55 i347 | 83,540 /82,403 N |
| Maksymalny moment poprzeczki | 12,113 N·m |
| Naprężenie zginające MDF | 4,486 MPa |
| Ugięcie w punkcie siły, przy E=2000 MPa | 1,771 mm |

Model: belka swobodnie podparta na rozstawie292 mm, przekrój50×18 mm,
siła skupiona na Y200, I=50×18³/12 mm⁴. Ugięcie sprawdzono niezależnie
całkowaniem pracy wirtualnej. Nacisk noska uśredniony po80×50 wynosi0,0415 MPa;
**nie jest to naprężenie maksymalne ani nośność kleju**.

Podparcie rzeczywiste jest bardziej złożone: występują docisk do wręgi,
napięcie wstępne, podatność podkładek i odrywanie. Ten wynik nie jest
potwierdzeniem awarii, ale 1,8 mm przemieszczenia nie pozwala uznać poprzeczki
za sztywny ogranicznik bez dalszej analizy. Nie wyznaczono naprężenia
dopuszczalnego, współczynnika bezpieczeństwa ani momentu dokręcania.
Nie uwzględniono udaru po zamknięciu luzu, zmęczenia ani pełzania.

Osobno przeliczono hipotetyczny moment montażowy M5 0,5/1/2 N·m.
Para M3 o rozstawie64 mm musiałaby reagować siłami7,81/15,63/31,25 N,
bez przypisywania nośności tarciu. Średnie wskaźniki docisku trzpienia do
MDF wynoszą0,118/0,237/0,473 MPa. Nie stanowią instrukcji dokręcania.
Duża płytka nie gwarantuje równomiernego wykorzystania całego jej pola:
ugięcie metalu i lokalny docisk wokół M5 wymagają odrębnej oceny.

## Pliki i dalsza decyzja

[Katalog K32](../dokumentacja/cnc/K32_RETENCJA_HOLD/README.md),
[kod](../skrypty/k32_retencja_plytek.py), [test](../skrypty/sprawdz_k32.py),
[wyniki](../wyniki/k32_retencja.json), [manifest wejść](../wyniki/k32_manifest.json).
Zachowano stare części. Wręga K32 zastępuje wręgę K31 i wymaga nowych ośmiu
płytek oraz16 śrub retencyjnych; poprzeczki pozostają K31. Model SCAD jest
wyłącznie detalem retencji, nie nowym kompletnym złożeniem skrzyni.
Przyrost objętości brutto samych płytek wynosi0,0288 l; otwory, śruby
oraz rzeczywiste zamknięte objętości wymagają końcowego bilansu.

**Następny krok: usztywnić poprzeczkę i nadać noskowi oraz długiemu
ogranicznikowi mechaniczne połączenie o policzalnej drodze siły.**
Należy połączyć to z ponownym sprawdzeniem tras montażu. Dopiero później
kwalifikować złącza na rzeczywistym MDF i osprzęcie. Nadal otwarte:
retencja śrub wobec drgań, materiał i gwinty, pełzanie MDF, połączenie
wręgi z korpusem, rzeczywiste grubości, głośnik i terminal.

Odtworzenie: `python skrypty/k32_retencja_plytek.py`, następnie
`python skrypty/sprawdz_k32.py`. Kompilacja SCAD do CSG sprawdza składnię,
nie zastępuje kontroli mechanicznej. GitHub Actions nie uznano za wykonane
na podstawie samego dodania workflow.
