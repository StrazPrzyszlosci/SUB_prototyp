# Raport 064 — P21E: sprzężenie podatnych ścian z gazem i napędem

**Data: 2026-10-31. Zakres: wykonane obliczenia nowego modelu zredukowanego, bez pomiarów.**
**Nie jest to** pełny przestrzenny MES–FV, zidentyfikowana charakterystyka MDF ani predykcja THD/SPL konkretnego urządzenia.

## Pytanie badawcze

Czy przy geometrii P20D i podatności mechanicznej z P18E można nadal traktować
obudowę jako idealnie sztywną podczas oceny napędu 20–80 Hz? Jaka jest
wrażliwość C02, C11 i C06 na *ten sam* hipotetyczny port podatnych ścian?

P18E ([059](059_podatne_wregi_i_panele.md)) dostarcza **statycznej podatności
jednej płyty** 1,9034748·10⁻⁸ m³/Pa i pierwszej postaci 143,30533 Hz
w **zadanym** modelu podpór. Nie jest to zmierzona podatność całej skrzyni.
W P21E zbudowano nową, jawnie warunkową redukcję, zamiast przypisywać
tej geometrii idealne utwierdzenie.

## Definicje i założenia

- Trzy katalogowe zestawy T/S: C02 Dayton RSS390HF-4, C11 Dayton
  RSS390HE-22 (połączenie szeregowe) i C06 STX W.32.800.8.FCX,
  na podstawie \`dane/przetworniki/pula_rozszerzona.json\`.
- Powietrze: \`rho=1,2 kg/m³\`, \`c=343 m/s\` (warunki przyjęte, nie pomiar).
- \`Vb=100/120/150 l\`; wszystkie są **objętościami założonymi jako netto
  gazu**, nie nowymi pomiarami wyporności.
- Dwie równe, skutecznie poruszające się płyty zastąpione **jednym**
  uogólnionym stopniem swobody objętości \`y\` [m³].
  Przyjęto \`Cw=2*C_panel*s\`, gdzie \`s=0,5/1/2\`.
- \`f_panel=123/143,30533/152,44 Hz\`, \`zeta=0,03\`.
  Przecięcie skrajnych częstotliwości ze skrajnymi podatnościami
  jest **stresowym iloczynem scenariuszy**, nie zmierzoną korelacją parametrów.
- Jednorodne ciśnienie w komorze, tłok membrany o katalogowym Sd;
  brak rzeczywistego położenia ugięć i gradientów P21D, lokalnego
  obciążenia wręg, wypełnienia, szczelin, kosza, podpór i 3D promieniowania.
  Nie zakładamy rzeczywistej niezależności dwóch płyt sprzęganych wręgami.
- Stałe małosygnałowe K/M/BL/Le/Rm/Re; brak zmian cieplnych, skoku,
  nieliniowości zawieszenia i pełnego modelu zewnętrznego promieniowania.

## Sprzężone równania i zgodność energii

Dla przemieszczenia membrany \`x\` [m], objętości odkształcenia
ścian \`y\` [m³], prądu \`i\` [A]:

\`Cg=Vb/(rho*c²)\` [m³/Pa], \`Kg=1/Cg\` [Pa/m³],
\`Kw=1/Cw\` [Pa/m³], \`Mw=Kw/(2*pi*f_panel)²\` [kg/m⁴],
\`Rw=2*zeta*sqrt(Kw*Mw)\` [N s/m⁵].

\`p=(Sd*x-y)/Cg\` [Pa],

\`M*x'' + Rm*x' + x/Cms + Sd*p = BL*i\`,

\`Mw*y'' + Rw*y' + Kw*y = p\`,

\`Le*i' + Re*i + BL*x' = u\`.

Mechaniczną masę M/Cms/Rm z T/S rekonstruujemy dokładnie jak w skrypcie
(uwzględniając skuteczną masę Mms; nie dodajemy drugi raz powietrza).

Funkcja energii modelu (objętość y ma własną jednostkę uogólnioną):

\`H=[M*x'²+Mw*y'²+Le*i² + x²/Cms + (Sd*x-y)²/Cg + Kw*y²]/2\`.

Po zsumowaniu równań otrzymujemy
\`H'=u*i-Re*i²-Rm*x'²-Rw*y'²\`.
Jest to układ pasywny przy dodatnich parametrach i wzajemnym BL.
Gaz nie jest dodatkowym, niezależnym źródłem energii.

Dla harmonicznych \`e^(j*omega*t)\`:

\`Cw(omega)=Cw/[1-(omega/omega_panel)²+j*2*zeta*omega/omega_panel]\`;

\`Zgas(omega)=Sd²/[j*omega*(Cg+Cw(omega))]\`;

\`Zm=Rm+j*omega*M+1/(j*omega*Cms)+Zgas\`;

\`Ze=Re+j*omega*Le+BL²/Zm\`, \`i=U/Ze\`, \`v=BL*i/Zm\`.

Jednostki \`Zgas\`: N·s/m. \`U=1 V RMS\`, porównywane z taką samą
pobudką i sztywnymi ścianami \`Cw=0\`. Badamy **zmianę amplitudy
prędkości**, nie absolutny SPL ani zniekształcenia.

## Próba liczbowa — 9 801 świadków

\`3 przetworniki × 3 objętości × 3 współczynniki Cw × 3 częstotliwości
panelu × 121 częstotliwości od 20 do 80 Hz co 0,5 Hz = 9 801\`.

W modelowym punkcie odniesienia \`s=1\`, \`f_panel=143,30533 Hz\`:
\`Cw=3,8069496·10⁻⁸ m³/Pa\`. W granicy statycznej jest to ekwiwalent
**5,3746 l dodatkowej podatności gazu**, lecz *nie* pięć litrów
fizycznie wolnej przestrzeni.

| Vb | Cw/Cg | Spadek samej sztywności gazowej w granicy statycznej |
|---:|---:|---:|
| 100 l | 0,053746 | 5,100% |
| 120 l | 0,044788 | 4,287% |
| 150 l | 0,035831 | 3,459% |

Obliczono wpływ na napęd, *z uwzględnieniem reakcji prądu i SEM*:

| Przetwornik | Δ prędkości przy 120 l, nominalny wariant, 20–80 Hz | Zakres Δ w całej siatce scenariuszy |
|---|---:|---:|
| C02 RSS390HF-4 | **−0,05753 do +0,13243 dB** | **−0,16338 do +0,37434 dB** |
| C11 RSS390HE-22 | −0,03252 do +0,08306 dB | −0,10130 do +0,22824 dB |
| C06 STX W.32.800.8.FCX | −0,02724 do +0,06034 dB | −0,08386 do +0,17358 dB |

![P21E: prędkość przetworników względem idealnie sztywnej skrzyni](../wyniki/104_P21E_podatne_sciany.svg)

Zmiana znaku po częstotliwości wynika z przesunięcia charakterystyki
sprzężonego układu, nie z ujemnej energii. Porównanie dotyczy
**tej samej obwiedni hipotetycznych ścian**, nie indywidualnych
właściwości paneli dopasowanych do konkretnego kosza.
Wniosek nie zmienia automatycznie kolejności finalistów P29.

## Kontrole i ograniczenia wiarygodności

Każdy z 9 801 świadków obliczono równaniem portu.
Niezależnie zestawiono liniowy **układ macierzowy 2×2** dla x,y,
eliminując prąd z równania elektrycznego. Maksymalna względna
rozbieżność prędkości: **8,12·10⁻¹⁶**.
Druga postać impedancji portu zgadza się do **4,42·10⁻¹⁶**.
To niezależne algebraiczne zestawienie *tego samego modelu*,
nie walidacja eksperymentalna ani niezależna dyskretyzacja 3D.

Przez identyczne konwencje napięcia i prądu RMS kontrolowano
\`Re(Zgas)*|v|² = Rw*|j*omega*y|²\`: maksymalna reszta
względna **1,31·10⁻¹⁵**. Dla wszystkich 9 801 przypadków
\`Re(Zgas)>=0\` oraz \`Re(Ze)>0\`.
Te kontrole pokazują prawidłowość bilansu mocy *w modelu*.

Siatka 0,5 Hz jest skończonym próbkowaniem; podane minima i maksima
**nie są certyfikatami ekstremów ciągłego pasma**.
Dodatkowe mody ścian, lokalne kształty drgań, rzeczywiste rozłożone
ciśnienie P21D, podatność wręg i uszczelnienia mogą istotnie zmienić
reakcję gaz–konstrukcja. Wartości f1/C_panel z P18E opisują
jeden model z zadanym otoczeniem; przypisanie tego f1 uogólnionemu
trybowi \`y\` jest kolejnym jawnym założeniem.

## Decyzja i dalsza bramka

**W rozpatrywanym zakresie podatność ścian daje mierzalną modelowo,
lecz niewielką korektę napędu względem sztywnej obudowy.**
To uzasadnia kontynuację P21, a nie zamknięcie całej integracji:
trzeba sprzęgnąć przestrzenny port gazu P21D z modułami
konstrukcyjnymi P18E/F i wprowadzić wielomodowe, rozłożone pole
ciśnienia na rzeczywistych panelach. Równocześnie należy zbadać
lokalne naprężenia, radiację paneli i podatność frontu.

Dopiero po modelowaniu i kalibracji rzeczywistej konstrukcji można
odnosić tę korektę do wyboru przetwornika, THD, SPL i DSP.

## Reprodukcja

\`OPENBLAS_NUM_THREADS=1 python skrypty/p21e_gaz_podatne_sciany.py\`

Wejścia: [konfiguracja](../dane/konfiguracje/p21e_podatne_sciany.json),
[oryginalna pula T/S](../dane/przetworniki/pula_rozszerzona.json).
Program zapisuje pełną tablicę **9 801 punktów** w
\`wyniki/p21e_podatne_sciany.csv\`, \`p21e_podsumowanie.json\`
i manifest SHA-256. W repo zamieszczono raport, skrypt,
[podsumowanie](../wyniki/p21e_podsumowanie.json) oraz
[39 przykładów dla nominalnych warunków](../wyniki/p21e_nominal.csv);
pełną tabelę CSV odtwarza skrypt.
