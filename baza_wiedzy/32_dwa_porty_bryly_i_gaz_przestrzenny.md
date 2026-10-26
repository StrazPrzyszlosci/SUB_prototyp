# Dwa porty bryły, sztywność kleju i granica gazu jednolitego

Metoda P20C, stan 2026-10-26. **Modele warunkowe**, bez identyfikacji
fizycznego MDF, partii kleju i gotowego subwoofera.

## Dwie powierzchnie wymagają dwóch portów pracy

Dla zamkniętego modułu istnieją dwie różne objętości: gazu wewnątrz Vi
i całego zewnętrznego obrysu Vo. W modelu bryłowym:

    delta_Vi = Hi.T @ u
    -delta_Vo = Ho.T @ u
    F_pressure = Hi*pi + Ho*po
    chi = H.T @ inv(K+s*C+s*s*M) @ H

H=[Hi, Ho], a s=jω i fazory są RMS. Siła ciśnienia na każdej odsłoniętej
powierzchni jest skierowana do materiału. Wewnętrzny gaz naciska także
na odsłonięte powierzchnie ściągu i nakładek. Zakryte powierzchnie spoin
nie dostają równocześnie nacisku gazu.

Praca wynosi pi·dVi−po·dVo. W cienkich nieściśliwych ścianach można
przybliżyć Hi≈−Ho. W pełnej bryle nie wolno tego założyć: różnica obejmuje
zmianę objętości MDF i kleju. Przy jednakowym ciśnieniu po obu stronach
jednorodna bryła ma podatność Vs/Kbulk, gdzie Kbulk=E/[3(1−2 nu)].
To użyteczne analityczne odniesienie hydrostatyczne dla kodu.

## Gaz i przeciek bez utraty skończonego strumienia

Niech Ci=Vi/(kappa*p0), G jest przewodnością pomiędzy główną komorą
a wnętrzem modułu. Nie jest to przeciek całego subwoofera na zewnątrz.
Z równania ciągłości:

    s*Ci*pi + s*(chi_ii*pi + chi_io*po) = G*(po-pi)
    r = pi/po = (G-s*chi_io)/(G+s*(Ci+chi_ii))
    1-r = s*(Ci+chi_ii+chi_io)/(G+s*(Ci+chi_ii))
    Y = s*(chi_oo+chi_oi*r) + G*(1-r)

Drugi zapis różnicy jest stabilniejszy od odejmowania liczb bliskich 1.
Admitancja Y opisuje przyrost objętości głównej komory przez ściskanie
obrysu oraz strumień przecieku do modułu.

Dla G=0 otrzymujemy:

    Y/s = chi_oo - chi_oi*chi_io/(Ci+chi_ii)

Dla G→∞ r→1, ale G*(1−r) może mieć skończoną granicę. Poprawnie:

    Y/s -> Ci + chi_ii + chi_io + chi_oi + chi_oo

To podatność gazu i ściskania całego materiału. Samo podstawienie r=1
i wyzerowanie G*(1−r) usunęłoby część odpowiedzi. W szczególnej granicy
cienkich ścian chi_ii=chi_oo=h, chi_io=chi_oi=−h odtwarza się wzór P20 A.

Przy stałej rzeczywistej podatności statycznej różnica między kolejnościami
DC i G→0 dla wzajemnej macierzy wynosi:

    (Ci+chi_ii+chi_io)^2/(Ci+chi_ii) >= 0

Warunki: Ci>0, dodatnia statyczna podatność i fizyczny zakres modelu.
Nie jest to dowód monotoniczności dynamicznej przy rezonansie.

## Bilans mocy i niezależna kontrola

Przy po=1 Pa RMS straty mechaniczne to ω²u*Cu, a straty przecieku
G|1−r|². Dla rzeczywistego Ci ich suma jest Re(Y). Przy stratnym gazie
dochodzi Re(sCi)|pi|². Sprawdzaj pełną hermitowską macierz Re(s*chi),
nie tylko jeden dodatni element lub sam moduł odpowiedzi.

Pełne równania nodalne do niezależnej kontroli redukcji to:

    (K+s*C+s*s*M)*u - Hi*pi = Ho*po
    s*Hi.T*u + (G+s*Ci)*pi = G*po

Macierz chi jest wygodną redukcją, nie nowym pomiarem. Rozwiązanie tych
równań na tej samej siatce sprawdza eliminację i znaki, a nie fizyczne
parametry produktu.

## Jak liczyć warunkowy wymagany moduł kleju

Przy stałej geometrii, grubości, Poissonie i liniowej sprężystości:

    Keff(E) = Kmdf + E*Kglue_unit + Hi*Hi.T/Ci
    Ceff(E) = Ho.T @ inv(Keff(E)) @ Ho
    dCeff/dE = -q.T @ Kglue_unit @ q <= 0

Rachunek wykonuje się po usunięciu sześciu ruchów sztywnych. Kglue_unit
jest dodatnia półokreślona. Pozwala to wyznaczyć ciągły próg E dla jawnego
kryterium sztywności, z numerycznymi świadkami po obu stronach pierwiastka.
W P20C zastosowano kryteria porównawcze względem Eref, nie progi briefu.

Nie przenoś tej pochodnej na dynamiczne maksimum, inną grubość, zmienny nu,
odspajanie lub nieliniowy kontakt. Moduł sprężystości nie jest wytrzymałością.
D3/D4, naprężenie w stali i moduł folii nie identyfikują adhezji do MDF,
pełzania, Gc lub krzywej S–N rzeczywistej spoiny.

Przestrzenne RMS naprężeń i maksima w punktach Gaussa są różnymi
obserwablami. Stabilna podatność całej bryły nie dowodzi zbieżności
lokalnego naroża. Maksimum próbek nie jest fizycznym osobliwym pikiem.

## Siatka i zakres gazu 0D

Porównuj reakcję przy tych samych Hz. Próbki wokół modów każdej siatki
oddzielnie nie są porównaniem wspólnego wymuszenia. Kierunki zagęszczenia
MDF, spoiny i powierzchni są odrębnymi doświadczeniami numerycznymi.
Zachowuj pierwotne flagi i ich dalsze rozstrzygnięcia.

Dla pustej prostokątnej komory c/(2*max(L)) jest użyteczną referencją
przestrzenną. Ściąg i nakładki zmieniają dziedzinę gazu; nie nazywaj tej
referencji ścisłą granicą ich rzeczywistych modów. Jednolity gaz nie
waliduje fizycznego rezonansu w pobliżu lub powyżej tej częstotliwości.

W następnym etapie potrzebne są przestrzenne ciśnienia, praca na wspólnej
granicy gaz/ciało i kontrola przejścia do modelu 0D. Dopiero potem pole
głównej komory z wkładami oraz porowatym wyklejeniem może wejść do syntezy
całego prototypu. Te badania nie zastępują pomiaru urządzenia po budowie.
