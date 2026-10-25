# Brief projektowy: system audio DIY — subwoofer prototypowy i aktywne monitory trójdrożne

**Wersja:** 0.6 — dokument roboczy dla specjalisty/agentów AI  
**Data:** 2026-10-23  
**Język pracy i raportowania:** polski  
**Rynek zakupowy:** Polska / UE; ceny w PLN, dostępność i koszty dostawy weryfikowane na dzień researchu  
**Zmiany względem v0.5:** optymalizacja pod jeden sweet spot zamiast całej kanapy; ADAM Audio ze średniej i wyższej półki jako mierzalny punkt odniesienia; aktualizacja procedury walidacji i promptu dla agentów

---

## 1. Cel nadrzędny

Zaprojektować i stopniowo zbudować wysokiej klasy system audio DIY, zaczynając od **pierwszego subwoofera w obudowie zamkniętej**, a następnie rozwijając go w stronę systemu złożonego z:

- dwóch subwooferów,
- dwóch aktywnych monitorów trójdrożnych,
- indywidualnego wzmacniacza dla każdego przetwornika/toru, bez pasywnych zwrotnic głośnikowych,
- centralnego lub odpowiednio podzielonego systemu DSP, który realizuje podział pasma, korekcję, opóźnienia, wyrównanie fazy/czasu i integrację subwooferów z monitorami.

Projekt ma być **oparty na pomiarach, modelowaniu i weryfikowalnych danych**, a nie na marketingowych deklaracjach, audiofilskich stereotypach ani samym odsłuchu. System ma zapewnić wysoką jakość dźwięku, duży zapas dynamiki i możliwość dalszego rozwoju. Nie przyjmować z góry limitu budżetowego dla prototypu ani kompletnego systemu: zadaniem agentów jest znaleźć najtańsze rozwiązanie spełniające wymagania, a następnie pokazać, za co warto dopłacić i gdzie rosnące koszty nie dają proporcjonalnych korzyści.

**Klasa docelowa.** Użytkownik chce uzyskać „namiastkę profesjonalnego studia masteringowego”. Parametry i kryteria oceny mają odpowiadać tej klasie. Parametry subwooferów i monitorów mają być porównywane z wybranymi modelami ADAM Audio ze średniej i wyższej półki. Modele należy wybrać na podstawie wiarygodnych danych producenta i zatwierdzić z użytkownikiem; ich parametry są punktem odniesienia, a nie automatycznym wymogiem kopiowania każdej cechy. Osiągi systemu trzeba odnieść do odsłuchu w odległości 2,5–3 m w pomieszczeniu 17–20 m². Konkretne modele referencyjne wskaże agent do zatwierdzenia przez użytkownika.

**Komercjalizacja.** System ma docelowo zostać skomercjalizowany i dostarczany do różnych pomieszczeń (ok. 17–20 m²), także klientom, którzy nie są audiofilami. Rozwiązania mają być więc powtarzalne i udokumentowane, a projekt nie może zależeć od cech jednego pokoju. Pokój użytkownika jest pierwszym egzemplarzem testowym. Na obecnym etapie nie liczyć kosztów produkcji seryjnej.

**Jak rozumieć klasę docelową.** Określenie „namiastka profesjonalnego studia masteringowego” jest celem jakościowym, który trzeba przełożyć na mierzalne wymagania; nie wolno uznać go za spełniony wyłącznie na podstawie maksymalnego SPL lub płaskiej charakterystyki w jednym punkcie. Referencją są reprezentatywne modele ADAM Audio ze średniej i wyższej półki, zarówno monitory, jak i subwoofery. Agent ma wybrać konkretne modele, uzasadnić ich przydatność jako punktów odniesienia i przedstawić ograniczenia dostępnych danych. Użytkownik zatwierdza modele i proponowane progi przed zamknięciem specyfikacji. DIY nie ma być z góry uznane za lepsze ani gorsze: porównanie musi wykazać, w których parametrach osiąga parytet, przewagę lub kompromis.

**Dwa poziomy walidacji.** Rozdzielić (1) osiągi własne urządzenia mierzone w warunkach kontrolowanych oraz (2) osiągi systemu po ustawieniu i kalibracji w konkretnym pomieszczeniu. Korekcja modów i strojenie pomieszczenia pozostają końcowym etapem, po pomiarach. Nie oznacza to odkładania pomiarów bazowych urządzeń ani pomijania wpływu pomieszczenia podczas wstępnego modelowania. Docelowy produkt ma działać w różnych pokojach 17–20 m², więc nie może wymagać jednej, niezmiennej korekcji ani zakładać identycznej odpowiedzi w każdym pomieszczeniu.

## 2. Filozofia i priorytety użytkownika

### Priorytety w kolejności praktycznej

Priorytety oceniać według kryteriów studia masteringowego: neutralność, niskie zniekształcenia, niski szum, rozdzielczość i powtarzalność wyników. Headroom jest wartością o tyle, o ile jest czysty i liniowy. Jeśli któryś punkt poniższej listy wchodzi w konflikt z tą klasą kryteriów, agent pokazuje konflikt wprost i nie rozstrzyga go samodzielnie.

1. **Czystość i brak słyszalnych szumów** — bardzo niskie szumy własne elektroniki, brak brumu i pisków, czarne tło także przy cichym odsłuchu.
2. **Dynamika i headroom** — swobodne odtwarzanie głośnych fragmentów bez kompresji, słyszalnego stresu, twardnienia brzmienia ani nadmiernych zniekształceń.
3. **Precyzja, rozdzielczość i neutralność** — dźwięk bez podbarwień, bas kontrolowany, wokale naturalne, dobre różnicowanie nagrań.
4. **Rzeczywista wydajność w pomieszczeniu** — liczy się nie tylko odpowiedź częstotliwościowa przy małym poziomie, ale również maksymalny SPL, zniekształcenia, kompresja mocy i możliwości w zakresie 20–40 Hz.
5. **Możliwość strojenia i rozbudowy** — wymienne przetworniki, regulowana objętość prototypowej skrzyni, zewnętrzna elektronika i odwracalne decyzje konstrukcyjne.
6. **Racjonalny stosunek ceny do efektu** — nie dopłacać za prestiż marki lub egzotyczny materiał membrany, jeżeli pomiary, konstrukcja silnika, liniowość i możliwości zastosowania nie uzasadniają kosztu.
7. **Dokumentacja i powtarzalność** — decyzje powinny być uzasadnione obliczeniami, pomiarami lub wiarygodnymi testami. Każde założenie należy oddzielić od potwierdzonego faktu.

### Charakter brzmienia i priorytety wydajności

- System ma być uniwersalny gatunkowo: techno/DnB i inna muzyka elektroniczna, metal, wokale, akustyka, muzyka klasyczna i fortepian.
- Ma działać dobrze zarówno przy cichym odsłuchu, jak i przy bardzo wysokiej głośności, bez słyszalnej zadyszki, kompresji, ostrości, utraty czytelności ani nadmiernych zniekształceń. **Najważniejszym priorytetem wydajnościowym jest jednak wysoki użyteczny SPL i headroom dla muzyki elektronicznej**, zwłaszcza w basie. Poziom odniesienia: zob. „Klasa docelowa” w sekcji 1.
- Trzeba znaleźć mierzalny kompromis między niskim zejściem (orientacyjny cel: użyteczne 20 Hz), liniowością, maksymalnym SPL, wychyleniem, zniekształceniami i kosztem. Nie zakładać, że pełnopasmowe 20 Hz przy dowolnej głośności jest konieczne lub fizycznie osiągalne w każdej konfiguracji.
- Brzmienie docelowo neutralne, bez sztucznego podbicia basu i bez „efektu kina domowego”. Bas głęboki i kontrolowany, bez dudnienia.
- Nie utożsamiać „szybkości” z samą odpowiedzią impulsową bez uwzględnienia pasma, fazy, pomieszczenia i zniekształceń.
- Priorytetem jest jakość mierzalna i słyszalna, a nie maksymalnie płaska pojedyncza krzywa uzyskana kosztem headroomu lub innych parametrów. W razie konfliktu parametrów pokazać kompromisy wprost.

### Przekład priorytetów na wymagania weryfikowalne

Przed wyborem finalnych przetworników i elektroniki agent ma opracować **specyfikację odbiorową wstępną**. Nie wymyślać progów liczbowych i nie przedstawiać ich jako zatwierdzonych: zaproponować je na podstawie wiarygodnych danych referencyjnych i uzyskać akceptację użytkownika. Co najmniej rozpatrzyć:

- maksymalny SPL szczytowy i długotrwały, z rozdzieleniem pasma, odległości i warunków pomiaru;
- użyteczny SPL w zakresie 20–40 Hz, z ograniczeniami wychylenia, mocy, termiki, zniekształceń i kompresji;
- odpowiedź częstotliwościową na osi i poza osią oraz kierunkowość;
- THD i inne dostępne miary zniekształceń przy kilku poziomach;
- kompresję przy wzroście poziomu sygnału;
- szum własny toru elektronicznego i szum akustyczny słyszalny z typowej pozycji odsłuchowej;
- zgodność czasową/fazową i integrację sekcji;
- powtarzalność między egzemplarzami oraz zakres koniecznej kalibracji.

Wartości takie jak „czarne tło”, „rozdzielczość”, „brak zadyszki” i „neutralność” opisywać przez właściwe pomiary, a jeśli mają pozostać kryteriami odsłuchowymi — zaproponować powtarzalny test odsłuchowy. Nie zakładać, że pojedyncza miara techniczna w pełni opisuje jakość dźwięku.

## 3. Kontekst pomieszczenia i instalacji

Poniższe dane są aktualnymi założeniami roboczymi; przed ostatecznym projektem należy potwierdzić wymiary i warunki montażowe.

- Pomieszczenie odsłuchowe: około **17 m²**, wymiary około **4,6 × 3,7 × 2,5 m**.
- Ściany betonowe.
- Część sufitu: perforowane panele NIDA Sonic C12N0-C z około 10 cm wełny.
- Planowane pułapki basowe w narożnikach.
- Na tylnej ścianie regały w stylu Billy Schröder.
- Ściana przednia jest krótszą ścianą pomieszczenia.
- Odległość odsłuchu około 2,5–3 m; centralna/większa kanapa (szerokość i liczba miejsc do potwierdzenia).
- Subwoofery najprawdopodobniej będą stały **w pobliżu monitorów**. Użytkownik nie może swobodnie umieścić ich w preferowanym układzie z przodu/tyłu pomieszczenia. Należy sprawdzić kilka realnych wariantów położenia i nie zakładać, że dwa subwoofery muszą być ustawione symetrycznie.
- **Obszar odsłuchu: jeden sweet spot** — główne miejsce odsłuchu jest priorytetem dla ustawienia, strojenia i optymalizacji. Pomiary w kilku sąsiednich punktach mogą służyć do oceny wrażliwości ustawienia, ale nie stanowią wymogu równej jakości na całej kanapie. Nie poświęcać precyzji stereo, odpowiedzi czasowej ani integracji subwooferów tylko po to, by poprawić wynik w odległych miejscach kanapy. Rozwiązania muszą nadal być możliwe do ponownej kalibracji w innych pomieszczeniach.
- W projekcie trzeba uwzględnić wpływ pomieszczenia i lokalizacji na bas. Nie obiecywać idealnej odpowiedzi 20 Hz bez danych dotyczących maksymalnego SPL, zniekształceń, położenia i korekcji.
- Zakładać pomieszczenie zaadaptowane akustycznie ustrojami. Korekcję modów pomieszczenia wykonywać na końcu, po pomiarach.

## 4. Docelowa architektura systemu

### Docelowy zestaw

- 2 × subwoofer.
- 2 × monitor aktywny, trójdrożny.
- Monitory mają być **aktywne**, bez pasywnych zwrotnic głośnikowych.
- Każdy przetwornik lub każdy niezależnie filtrowany tor ma mieć własny kanał wzmacniacza.
- Docelowo zastosować **DSP z co najmniej 8 niezależnymi wyjściami**: 6 torów dla dwóch monitorów trójdrożnych i 2 tory dla dwóch subwooferów. Zweryfikować liczbę wejść, routing, niezależność filtrów, poziom szumów i headroom; nie traktować samej deklaracji „8 kanałów” jako wystarczającej bez sprawdzenia, czy chodzi o wejścia, wyjścia czy kanały przetwarzania.
- **Założenia elektroniki na obecnym etapie:** DSP to gotowe urządzenie miniDSP (konkretny model do wyboru po weryfikacji liczby wyjść i szumów); wzmacniacze to gotowe, wysokiej jakości moduły klasy D w formie laminatów bez obudowy. Docelowo (po etapie prototypów) planowany jest własny, swobodnie programowalny DSP.
- Moduły wzmacniaczy bez obudowy wymagają przemyślanego zasilania, obudowy elektroniki, uziemienia i ekranowania oraz zabezpieczeń (DC na wyjściu, soft-start, termika). Uwzględnić bezpieczeństwo użytkowania w domu z małym dzieckiem oraz, z perspektywy komercjalizacji, wymagania dla wyrobów sprzedawanych w UE (m.in. bezpieczeństwo elektryczne i kompatybilność elektromagnetyczna). Agent wskazuje, co to zmienia w wyborze modułów, bez udzielania porad prawnych.
- DSP realizuje filtry podziału, wyrównanie poziomów, opóźnienia, korekcję amplitudy/fazy i integrację z subwooferami.
- Preferowana elektronika zewnętrzna; **nie umieszczać wzmacniacza, DSP ani zasilacza w obudowie subwoofera**. Ułatwi to serwis, wymianę i eksperymenty.
- W miarę możliwości ograniczyć zbędną liczbę urządzeń, ale nie kosztem jakości, poziomu szumów, liczby kanałów, możliwości regulacji lub bezpieczeństwa.
- Rozważyć połączenia zbalansowane tam, gdzie pomagają ograniczyć zakłócenia i pozwalają zachować właściwy poziom sygnału. Nie traktować samego złącza XLR jako gwarancji lepszego brzmienia.
- Użytkownik obawia się pogorszenia jakości przez DSP, w tym utraty „czarnego tła”. Należy ocenić to technicznie: szumy, zakres dynamiczny, clipping, konwersje A/D i D/A, poziomy sygnału, jakość filtrów i architektura gain staging. Nie zakładać ani że DSP pogarsza dźwięk, ani że jest całkowicie bezkosztowy.

### Docelowe monitory

- Dwa monitory **trójdrożne**; nie zastępować tego wariantu czterema mniejszymi monitorami.
- Subwoofery przejmują najniższy zakres basu, ale zakresy podziału należy dobrać po analizie przetworników, maksymalnego SPL, kierunkowości i możliwości pomieszczenia.
- Wstępnie rozważana wysokość/szerokość gabarytowa monitora: około 38–45 cm dla jednego z wymiarów obudowy — do doprecyzowania, nie jest to jeszcze zatwierdzony wymiar.
- Rozważyć układ 3-drożny oraz ewentualnie 3,5-drożny wyłącznie wtedy, gdy istnieje mierzalne uzasadnienie (np. kierunkowość, obciążenie przetworników, maksymalny SPL).
- Docelowy punkt odniesienia: wybrane monitory ADAM Audio ze średniej i wyższej półki, wraz z odpowiednimi subwooferami. Nie zakładać, że jeden model jest właściwym wzorcem dla wszystkich parametrów ani że DIY ma przewagę bez pomiarów.
- Estetyka i integracja z wnętrzem są ważne: rozważane są konstrukcje ukryte za tkaniną akustyczną, pionowe i częściowo wpuszczane. Później możliwe są fronty z litego drewna, frezowane CNC lub malowane w kolorze RAL. Rozwiązania wykończeniowe nie mogą pogarszać akustyki bez świadomego kompromisu.

## 5. Etap pierwszy — prototyp subwoofera

### Cel prototypu

Zbudować pierwszy subwoofer do nauki, pomiarów i iteracyjnego rozwoju. Nie musi być od razu ostatecznym modelem. Obudowa ma umożliwiać testowanie różnych objętości i w miarę możliwości późniejszą wymianę przetwornika.

### Dobór gabarytów i objętości

**Nie ma obecnie zadeklarowanego limitu wymiarów zewnętrznych.** Agent ma dobrać optymalną objętość i proporcje obudowy na podstawie wymagań akustycznych, wybranego przetwornika, sztywności konstrukcji, praktycznego ustawienia w pomieszczeniu, masy, kosztu i możliwości wykonania. Porównać sensowne warianty wielkości, a nie ograniczać research do wcześniej rozważanych wymiarów. W obliczeniach zawsze rozdzielać objętość brutto i netto oraz uwzględniać grubość ścian, wzmocnienia, kosz przetwornika i inne elementy.

### Konstrukcja wstępna

- Pierwszy wariant: **obudowa zamknięta (sealed)**.
- Użytkownik chce regulować objętość obudowy na etapie prototypu, aby porównać różne ustawienia i później udoskonalać konstrukcję. Elementy będą wycinane na **CNC**, więc można projektować obudowę i moduły regulacyjne pod precyzyjną obróbkę; nie trzeba sztucznie upraszczać projektu do wykonania wyłącznie ręcznymi narzędziami.
- Wymiary i objętości muszą być policzone jako objętość netto, z uwzględnieniem przetwornika, wzmocnień i ewentualnego wypełnienia.
- Nie przyjmować z góry, że obudowa zamknięta jest najlepsza dla każdego głośnika. Najpierw porównać kilka sensownych przetworników i ocenić osiągi w sensownym litrażu wynikającym z optymalizacji.
- Zewnętrzny wzmacniacz i DSP; bez elektroniki w skrzyni.
- Uwzględnić sztywność paneli, wzmocnienia, uszczelnienie, dostęp serwisowy, bezpieczeństwo mechaniczne i możliwość mocowania osłony chroniącej przed dziećmi.

### Dobór głośnika i wzmacniacza

Wielkość przetwornika **12″ vs 15″ nie została jeszcze rozstrzygnięta**. Należy porównać je na podstawie danych i symulacji, nie samej średnicy ani deklarowanej mocy.

Dla każdego kandydata należy zebrać:
- pełne parametry T/S z wiarygodnego źródła,
- powierzchnię membrany Sd, liniowy i maksymalny wychył (z rozróżnieniem metod deklaracji), Xmax/Xmech, Re, Le, BL, Mms, Cms, Qes/Qms/Qts, Fs, Vas, Pe i zalecane warunki pracy,
- wiarygodne dane o zniekształceniach i kompresji, jeśli są dostępne,
- symulację w docelowej obudowie i w kilku objętościach,
- przewidywane pasmo, spadek odpowiedzi, zapotrzebowanie na EQ, wychylenie membrany przy zadanym napięciu/mocy, SPL oraz ograniczenia termiczne/mechaniczne,
- rzeczywistą cenę, dostępność, koszty dostawy i warunki gwarancji w Polsce/UE.

Nie wybierać przetwornika wyłącznie na podstawie mocy RMS, ceny, popularności albo marketingowych wykresów. Zweryfikować, czy deklarowane parametry T/S są spójne z niezależnymi pomiarami, gdy takie istnieją.

Wstępny punkt odniesienia do sprawdzenia, nie obowiązkowy wybór: Dayton Audio RSS315HF-4 (12″). Należy też znaleźć konkurencyjne przetworniki 12″ i 15″ o dobrym stosunku ceny do osiągów, dostępne w UE. Nie zakładać, że Dayton musi wygrać.

Wzmacniacz:
- dobrać do impedancji i wymagań napięciowo-prądowych konkretnego przetwornika,
- sprawdzić moc ciągłą i rzeczywistą moc przy odpowiedniej impedancji, napięcie maksymalne, limit prądowy, zabezpieczenia, szumy, chłodzenie, pobór mocy, niezawodność i dostępność,
- zostawić rozsądny zapas, ale nie dobierać mocy bez uwzględnienia wychylenia przetwornika i filtrów,
- sprawdzić, czy wzmacniacz przy wymaganym poziomie nie będzie ograniczał osiągów i czy DSP może bezpiecznie chronić przetwornik,
- preferować konstrukcję zewnętrzną.

### Jak porównywać obudowy i przetworniki

Co najmniej trzy scenariusze, jeśli dane pozwalają:
1. 12″ w obudowie zamkniętej,
2. 15″ w obudowie zamkniętej,
3. alternatywny przetwornik/objętość, który może dać lepszy kompromis.

Dla każdego pokazać:
- rzeczywistą objętość netto,
- odpowiedź częstotliwościową bez EQ i po realistycznej korekcji,
- maksymalny przewidywany SPL w funkcji częstotliwości,
- wychylenie membrany i granice liniowej pracy,
- wymagany boost EQ i koszt w headroomie,
- szacowane zniekształcenia/kompresję, jeśli są wiarygodne,
- wymagania wzmacniacza,
- zalety, wady, ryzyka i cenę kompletnego rozwiązania.

Szczególną uwagę poświęcić zakresowi **20–40 Hz**: nie tylko temu, czy system teoretycznie sięga 20 Hz, ale jaki poziom może tam osiągnąć z akceptowalnymi zniekształceniami i bez nadmiernego wychylenia. Najważniejsze jest porównanie rzeczywistego kompromisu między zejściem w okolice 20 Hz a wysokim SPL w basie elektronicznym. Wyniki symulacji oznaczać jako prognozy, a nie pomiary gotowego urządzenia.

Narzędzia symulacyjne zostaną wybrane na późniejszym etapie; do tego czasu agent opisuje metodę i założenia, bez fikcyjnych liczb. Korekcja modów pomieszczenia jest wykonywana na końcu, po pomiarach; mimo to przy szacowaniu wychylenia i SPL w zakresie 20–40 Hz przedstawić scenariusze z i bez wzmocnienia pomieszczenia (room gain) jako jawne założenie. Jeśli dane pozwalają, przedstawić maksymalny SPL w funkcji częstotliwości i poziomy ograniczone wychyleniem, mocą oraz termiką.

## 6. DSP, pomiary i integracja

Docelowo system musi umożliwiać:
- niezależne filtry dla każdego toru,
- filtry podziału o regulowanej częstotliwości i nachyleniu,
- regulację opóźnienia, polaryzacji/fazy i poziomu,
- parametryczne EQ,
- limity ochronne (high-pass, limiter napięcia/mocy lub odpowiedni limiter),
- integrację dwóch subwooferów z monitorami,
- eksport/zapis ustawień i możliwość odtworzenia konfiguracji.

Na obecnym etapie DSP ma być gotowcem miniDSP, a wzmacniacze gotowymi modułami klasy D; poniższa lista służy porównaniu i wyborowi konkretnych modeli oraz zachowaniu opcji na etap własnego DSP.

Kandydaci/rodziny urządzeń wcześniej rozważane: miniDSP Flex/Flex Eight, Helix DSP Ultra oraz rozwiązania oparte na wzmacniaczach Hypex (NCore/FusionAmp/FA503/UcD/Nilai) i ICEpower. To lista do zbadania, nie lista zatwierdzonych zakupów. Należy porównać również inne rozwiązania, jeśli mają lepszą relację parametrów, liczby kanałów, szumów, funkcji i ceny.

Pomiary i narzędzia rozważane:
- REW,
- mikrofon pomiarowy UMIK-1 lub odpowiedni alternatywny,
- interfejs MOTU M2, jeśli potrzebny do danego toru pomiarowego,
- pomiary impedancji i odpowiedzi przetworników, jeśli użytkownik będzie budował monitory,
- pomiary bliskiego pola i w pomieszczeniu oraz pomiary maksymalnego SPL/kompresji w bezpiecznych warunkach.

Nie należy utożsamiać pomiaru REW w jednym punkcie z kompletną walidacją. Plan pomiarowy powinien rozdzielać: charakterystykę przetwornika/obudowy, integrację czasową i fazową, wpływ pomieszczenia, szumy, maksymalny SPL i zniekształcenia.

### Dwa subwoofery

Dwa subwoofery mają być wykorzystywane do poprawy równomierności basu i/lub zwiększenia headroomu, nie tylko dla samego faktu posiadania dwóch sztuk. Ponieważ ich położenie będzie ograniczone, należy:
- przeanalizować realne możliwe lokalizacje,
- zmierzyć każdy subwoofer osobno,
- sprawdzić polaryzację, opóźnienia i filtry,
- zmierzyć przede wszystkim główny sweet spot; dodatkowe pomiary w sąsiednich punktach wykonać diagnostycznie, by sprawdzić, czy wynik nie zależy nadmiernie od przesunięcia mikrofonu,
- dobrać oddzielne ustawienia dla każdego subwoofera, jeśli DSP na to pozwala i pomiary wskazują korzyść,
- nie zakładać, że dwa identyczne subwoofery muszą otrzymać identyczne EQ/opóźnienie.

## 7. Późniejszy projekt monitorów trójdrożnych

Nie dobierać ostatecznych przetworników, częstotliwości podziału ani wymiarów obudowy przed zebraniem wymagań i wykonaniem porównawczego researchu.

Dla każdej propozycji zestawu przetworników trzeba ocenić:
- liniowość i zniekształcenia w przewidywanym zakresie pracy,
- kierunkowość i zgodność kierunkowości między sekcjami,
- maksymalny SPL i kompresję,
- odpowiedź poza osią i wpływ geometrii frontu,
- głębokość montażową, objętość i wymagania obudowy,
- częstotliwości podziału możliwe do uzyskania bez nadmiernego obciążenia przetworników,
- wymagania wobec DSP i liczby kanałów wzmacniacza,
- koszt całego systemu, w tym wzmacniaczy, DSP, zasilania, okablowania i obudów.

Należy sprawdzić, czy lepiej użyć osobnych wzmacniaczy dla każdego przetwornika, czy wielokanałowych wzmacniaczy o niezależnych kanałach. „Indywidualny wzmacniacz” oznacza tu niezależny kanał napędzający dany przetwornik; nie musi oznaczać osobnej fizycznej obudowy dla każdego kanału, o ile nie pogarsza to parametrów i niezawodności.

## 8. Koszt i strategia zakupowa — bez z góry narzuconego limitu

Nie przyjmować z góry budżetu ani dla prototypu subwoofera, ani dla całego systemu. Nie oznacza to zgody na niekontrolowane wydatki: zadaniem agentów jest znaleźć **najniższy realny koszt spełnienia wymagań**, a potem wskazać, ile kosztują kolejne poziomy osiągów i które dopłaty mają mierzalny sens. Nie wolno z góry odrzucać większej obudowy, droższego przetwornika lub mocniejszego wzmacniacza, jeśli okażą się potrzebne; nie wolno też zakładać, że droższe rozwiązanie będzie lepsze.

Dla każdego etapu przedstawić:
- wariant o najniższym koszcie, który spełnia zdefiniowane wymagania,
- wariant o najlepszej relacji kosztu do osiągów,
- wariant o wyższych osiągach i jego konkretne korzyści, jeśli dopłata jest uzasadniona.

Dla każdego wariantu rozdzielić koszt:
1. przetwornika,
2. materiałów i wykonania skrzyni,
3. wzmacniacza,
4. DSP/kanałów i okablowania,
5. pomiarów, narzędzi i akcesoriów,
6. dostawy i ewentualnych opłat.

Uwzględniać polską i europejską dostępność. Import spoza UE wymaga policzenia VAT, cła (jeśli dotyczy), kosztów dostawy i ryzyka serwisu. Ceny muszą mieć datę sprawdzenia i linki do sprzedawców.

## 9. Procedura porównania z urządzeniami referencyjnymi ADAM Audio

Agent ma wybrać do zatwierdzenia przez użytkownika reprezentatywne modele monitorów i subwooferów ADAM Audio ze średniej i wyższej półki. Nie wolno porównywać jedynie liczb „max SPL” z różnych kart katalogowych bez sprawdzenia warunków. Dla każdego modelu odnotować źródło, datę dostępu, odległość, rodzaj sygnału, czas trwania, zakres częstotliwości, sposób pomiaru i kryterium ograniczenia, o ile producent je podaje. Brakujące warunki wyraźnie oznaczyć.

Następnie przygotować porównanie w trzech odrębnych warstwach:

1. **Dane katalogowe producenta** — bez modyfikacji, z pełnym opisem warunków i ograniczeń.
2. **Porównanie w ujednoliconych warunkach** — przeliczenia wyłącznie tam, gdzie uzasadniają je prawa akustyki i znane warunki pomiaru. Nie udawać, że proste przeliczenie odległości odtwarza wynik w pomieszczeniu ani że wynik szerokopasmowy dowodzi wydajności przy 20–40 Hz.
3. **Przewidywane działanie w pomieszczeniu 17–20 m²** — przedstawić jako scenariusz, nie jako wynik pomiaru. Wpływ room gain, granic pomieszczenia, adaptacji i położenia musi być opisany jako zależny od konkretnego pokoju.

Dla monitorów oddzielić maksymalny SPL szerokopasmowy od zdolności do odtwarzania wymaganych poziomów przy niskich częstotliwościach i od jakości poza osią. Dla subwooferów porównać pasmowy maksymalny SPL, szczególnie 20–40 Hz, o ile dane pozwalają. Nie wyprowadzać jakości masteringowej wyłącznie z maksymalnego SPL.

Jeśli dane referencyjne nie są porównywalne lub producent nie publikuje potrzebnych informacji, agent ma to wskazać i zaproponować równoważny protokół pomiarowy dla prototypu. Nie dopisywać brakujących liczb przez zgadywanie.

## 10. Bramki decyzyjne i audyt rekomendacji

Pracę prowadzić etapami; każdy etap kończy się wnioskiem, listą nierozstrzygniętych kwestii i decyzją, czy są wystarczające podstawy do dalszych wydatków.

1. **Bramka wymagań:** modele referencyjne, wstępne scenariusze SPL, kryteria pomiarów i obszar odsłuchu opisane oraz przedstawione użytkownikowi do zatwierdzenia.
2. **Bramka wykonalności:** kandydaci odrzuceni tylko na podstawie jawnych ograniczeń fizycznych/technicznych, a nie ceny lub preferencji marki.
3. **Bramka prototypu:** uzasadnienie, dlaczego wybrany przetwornik, obudowa i wzmacniacz są najlepszym eksperymentem; wskazanie, czego prototyp nie pozwoli jeszcze zweryfikować.
4. **Bramka pomiarowa:** plan pomiarów, procedura bezpieczeństwa, zapis ustawień i kryteria sukcesu przed wykonaniem testów.
5. **Bramka przejścia do systemu:** decyzja o drugim subwooferze i monitorach na podstawie wyników, bez automatycznego przyjmowania, że pierwsza konfiguracja musi zostać docelowa.

Przed rekomendacją końcową agent ma wymienić trzy najważniejsze założenia, których błędność zmieniłaby wybór, najsilniejszy argument przeciw rekomendacji, najtańszą wiarygodną alternatywę oraz pomiar/eksperyment, który najszybciej rozstrzygnie najważniejszą niewiadomą. Każdy wynik oznaczyć jako: pomiar niezależny, dane producenta, symulacja, obliczenie przybliżone albo założenie.

## 9. Zasady researchu dla agenta AI

1. **Oddziel fakty, założenia i rekomendacje.** Każdy parametr ma mieć źródło albo być wyraźnie oznaczony jako niepotwierdzony.
2. Korzystaj z kart katalogowych producentów, niezależnych pomiarów, wiarygodnych testów i narzędzi symulacyjnych. Fora mogą wskazywać problemy lub doświadczenia, ale nie zastępują danych.
3. Podawaj bezpośrednie linki do źródeł i datę dostępu.
4. Weryfikuj kluczowe parametry w więcej niż jednym źródle, zwłaszcza T/S, moc wzmacniacza i dostępność.
5. Nie porównuj urządzeń na podstawie samych haseł marketingowych typu „audiophile”, „ultra-low distortion” czy „reference”.
6. Nie twierdź, że coś „brzmi lepiej”, jeśli nie ma podstaw do takiego wniosku. Rozróżniaj mierzalną różnicę, prawdopodobną korzyść i subiektywną preferencję.
7. Uwzględnij wpływ DSP/EQ na headroom i wychylenie membrany.
8. Uwzględnij ograniczenia pomieszczenia oraz poziom odsłuchu. Samo F3 lub wykres przy małym sygnale nie określa użyteczności subwoofera.
9. Przed rekomendacją końcową pokaż tabelę porównawczą i uzasadnij wybór. Wskaż również, jakie dane mogłyby zmienić rekomendację.
10. Nie kupuj niczego i nie podejmuj zobowiązań w imieniu użytkownika. Celem jest research i plan, nie automatyczne zamówienie.
11. Nie wymyślaj wyników symulacji ani pomiarów. Jeśli model narzędziowy nie jest dostępny, podaj metodę i ograniczenia zamiast fikcyjnych liczb.
12. Przed przejściem do monitorów ustabilizuj wnioski z prototypu subwoofera, ale unikaj przedwczesnego zamknięcia architektury, jeśli wyniki pomiarów wskażą lepszą drogę.
13. Nie używaj budżetu jako kryterium odrzucenia. Najpierw określ rozwiązania spełniające wymagania, potem pokaż krzywą koszt–osiągi, najtańszy wariant wystarczający i punkty, w których dopłata przestaje być opłacalna.
14. **Porównuj SPL jak do jak.** Maksymalny SPL z kart katalogowych Adam Audio (i innych producentów) ma określone warunki pomiaru: odległość, wolne pole lub półprzestrzeń, rodzaj sygnału, pasmo i kryterium zniekształceń. Nie przenoś tych liczb wprost na odsłuch z kanapy w pokoju 17–20 m². Podaj warunki pomiaru producenta i przelicz je na odległość 2,5–3 m, wskazując założenia. Priorytetem jest poziom i jakość w jednym głównym sweet spocie.

## 12. Oczekiwane rezultaty pierwszego etapu

Agent powinien dostarczyć:

1. **Krótki wniosek wykonawczy**: co wybrać i dlaczego.
2. **Tabelę minimum 3 kandydatów na przetwornik** — z parametrami, cenami, dostępnością, linkami i wiarygodnością danych.
3. **Porównanie 12″ i 15″** w dostępnej obudowie zamkniętej.
4. **Rekomendowaną objętość netto** oraz praktyczny projekt skrzyni z optymalnymi wymiarami wewnętrznymi/zewnętrznymi, grubością płyt, wzmocnieniami i metodą regulacji objętości; bez z góry narzuconego limitu gabarytów.
5. Symulacje lub jawnie opisane obliczenia dla odpowiedzi, wychylenia, SPL i zapotrzebowania na moc.
6. **Rekomendację wzmacniacza i ochrony DSP**, z uzasadnieniem dopasowania elektrycznego i poziomów.
7. Listę materiałów i narzędzi oraz kosztorys w PLN.
8. Plan walidacji prototypu: co mierzyć, jak, w jakiej kolejności i jakie wyniki uznać za satysfakcjonujące. Progi liczbowe zaproponować na podstawie parametrów referencyjnych urządzeń ADAM Audio ze średniej i wyższej półki (maks. SPL, pasmo, zniekształcenia, szum) do zatwierdzenia przez użytkownika; głównym punktem oceny jest sweet spot, a sąsiednie punkty służą diagnostyce.
9. Listę ryzyk i niewiadomych oraz krótką listę decyzji, które trzeba zatwierdzić przed zakupem.
10. Na koniec: plan przejścia do dwóch subwooferów i aktywnych monitorów trójdrożnych, z listą danych, które trzeba zebrać w trakcie testów prototypu.

## 13. Ustalone decyzje i pozostałe niewiadome

### Decyzje potwierdzone przez użytkownika

- **Bez narzuconego budżetu:** nie ustalać z góry limitu kosztów ani prototypu, ani całego systemu. Optymalizować pod wymagane osiągi i szukać najtańszego rozwiązania, które je spełni; jawnie pokazać zależność koszt–osiągi.
- **Rola prototypu:** platforma eksperymentalna. Można zmieniać przetworniki, objętość i rozwiązania konstrukcyjne; nie trzeba zakładać, że pierwszy wariant zostanie docelowym subwooferem.
- **Priorytet basu:** znaleźć kompromis między zejściem w okolice 20 Hz, liniowością, wysokim maksymalnym użytecznym SPL i niskimi zniekształceniami. Wydajność przy głośnym odtwarzaniu muzyki elektronicznej ma szczególnie wysoki priorytet.
- **Uniwersalność:** system ma sprawdzać się przy cichym i bardzo głośnym słuchaniu oraz z różnymi gatunkami muzyki, bez słyszalnej kompresji i „zadyszki”.
- **Obszar odsłuchu:** jeden główny sweet spot, około 2,5–3 m od systemu. Dodatkowe punkty pomiarowe są diagnostyczne, nie stanowią wymogu optymalizacji całej kanapy.
- **Gabaryty:** brak z góry ustalonego limitu wymiarów obudów. Agent ma dobrać wymiary i objętość optymalne dla osiągów i praktycznego ustawienia.
- **Wykonanie prototypu:** elementy będą wycinane na CNC; projekt może uwzględniać precyzyjne łączenia, modułowe przegrody i regulację objętości.
- **DSP docelowe:** minimum 8 niezależnych kanałów wyjściowych dla 6 torów monitorów i 2 subwooferów.
- **Klasa docelowa:** namiastka profesjonalnego studia masteringowego; maksymalny SPL na poziomie dobrych subwooferów i monitorów studyjnych Adam Audio, dostosowany do pomieszczeń 17–20 m²; priorytety i parametry według kryteriów studia masteringowego.
- **Komercjalizacja:** system ma docelowo być sprzedawany i dostarczany do różnych pomieszczeń.
- **Pomieszczenie i korekcja:** zakładamy pomieszczenie zaadaptowane akustycznie ustrojami; korekcja modów dopiero na końcu, po pomiarach. Narzędzia symulacyjne zostaną wybrane później.
- **Elektronika:** gotowy DSP miniDSP i gotowe moduły wzmacniaczy klasy D bez obudowy; docelowo własny, swobodnie programowalny DSP.

### Niewiadome, które realnie wpływają na projekt

Poniższe braki nie powinny zatrzymywać researchu. Agent ma przyjąć scenariusze, jawnie opisać założenia i pokazać, jak wpływają na wybór.

1. **Docelowy SPL.** Poziom odniesienia to wybrane modele monitorów i subwooferów ADAM Audio ze średniej i wyższej półki (konkretne modele wskaże agent do zatwierdzenia przez użytkownika; liczby z kart katalogowych przeliczyć z uwzględnieniem warunków pomiaru producenta). Nadal nie podano wartości szczytowej i długotrwałej w pokoju użytkownika. Przygotować co najmniej trzy scenariusze docelowego poziomu w głównym punkcie odsłuchowym, w tym odległość 2,5–3 m, oraz wskazać, który jest realistyczny dla pokoju 17 m² i muzyki elektronicznej. Oddzielić SPL szczytowy od długotrwałego i pokazać ograniczenia pasmowe, zwłaszcza 20–40 Hz. Nie dobierać wymagań na podstawie arbitralnej liczby bez wyjaśnienia.
2. **Położenie sweet spotu.** Potwierdzić dokładną pozycję głowy względem monitorów, odległość odsłuchu i wysokość uszu; na razie przyjmować 2,5–3 m.
3. **Wrażliwość na pozycję.** Wykonać dodatkowe pomiary w niewielkim obszarze wokół sweet spotu, aby oszacować stabilność wyniku, ale nie optymalizować całego systemu pod całą kanapę.

### Co nie powinno blokować researchu

- Wybór MDF/sklejki: porównać koszty, sztywność, masę, łatwość obróbki i wykończenia; wskazać preferowany materiał.
- Ostateczny wybór 12″, 15″ lub innej średnicy: to wynik researchu, nie wymaganie ustalone z góry.
- Dokładna objętość i wymiary skrzyni: agent ma je wyznaczyć na podstawie parametrów T/S, symulacji, wymagań SPL, ustawienia i wykonalności. Nie ma limitu wymiarów narzuconego przez użytkownika.
- Ostateczny model DSP i wzmacniacza: można wskazać rozwiązanie tymczasowe i docelową architekturę, unikając podwójnych zakupów; docelowy DSP musi zapewnić minimum 8 niezależnych wyjść.
- Szczegółowe parametry monitorów: należy je opracować w dalszym etapie, ale od początku sprawdzać zgodność architektury, liczby kanałów i wymagań SPL całego systemu.

---

## 14. Pierwsze polecenie dla agenta

> Przeprowadź niezależny, źródłowy research dotyczący pierwszego subwoofera DIY w obudowie zamkniętej. Nie narzucaj budżetu ani maksymalnych wymiarów skrzyni. Celem jest znalezienie najtańszego rozwiązania spełniającego wymagania oraz określenie, kiedy większy koszt daje mierzalną poprawę. To ma być platforma eksperymentalna do zmiany przetworników i regulacji objętości, a niekoniecznie finalny model. Porównaj co najmniej trzy realnie dostępne przetworniki, w tym sensowne warianty 12″ i 15″ (oraz inne, jeśli uzasadnione), i odpowiednie wzmacniacze. System ma być uniwersalny gatunkowo i działać od cichego do bardzo głośnego odsłuchu; priorytetem jest jednak wysoki użyteczny SPL i headroom dla muzyki elektronicznej. Znajdź kompromis między liniowością i zejściem w okolice 20 Hz a SPL, wychyleniem, kompresją i zniekształceniami w zakresie 20–40 Hz. Za poziom odniesienia przyjmij osiągi dobrych subwooferów i monitorów studyjnych ADAM Audio. Najpierw zidentyfikuj konkretne modele referencyjne i przedstaw je użytkownikowi do zatwierdzenia. Udokumentuj warunki pomiaru producenta i porównuj dane wyłącznie w porównywalnych warunkach; oddziel dane katalogowe, przeliczenia i scenariusze dla pomieszczenia 17–20 m². Przygotuj propozycję specyfikacji odbiorowej obejmującą SPL szczytowy i długotrwały, pasmowy maksymalny użyteczny SPL, zniekształcenia, kompresję, szumy i kierunkowość. Optymalizuj pod jeden główny sweet spot w odległości 2,5–3 m. Dodatkowe punkty wokół niego wykorzystaj diagnostycznie, by ocenić stabilność ustawienia, ale nie traktuj całej kanapy jako obszaru równorzędnej optymalizacji. Dobierz optymalne wymiary/objętość i zaprojektuj prototyp z regulacją objętości; elementy będą wycinane na CNC. Uwzględnij zewnętrzną elektronikę oraz przyszłą integrację dwóch subwooferów z aktywnymi monitorami trójdrożnymi. Zakładaj gotowy DSP miniDSP i gotowe moduły wzmacniaczy klasy D bez obudowy (docelowo własny, swobodnie programowalny DSP). Docelowy DSP ma mieć minimum 8 niezależnych wyjść: 6 dla monitorów i 2 dla subwooferów. Nie podejmuj decyzji na podstawie niezweryfikowanych deklaracji. Przedstaw źródła, daty, obliczenia, założenia, ryzyka i rekomendację, a nie tylko listę produktów. Gdy brakuje danych użytkownika, przygotuj scenariusze i oznacz założenia zamiast ich ukrywać.
