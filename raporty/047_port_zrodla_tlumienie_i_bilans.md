# Raport 047 — P22A: rzeczywisty port źródła w modelu liniowym

Stan: 2026-10-27. **Obliczenia i symulacje**, bez badania fizycznego
wzmacniacza. Parametry obwodu są jawnie przyjętymi scenariuszami.

## Wniosek dla prototypu

**Rekomendacja:** końcowy model powinien obejmować łączną impedancję
wyjściową źródła i przewodów. Ograniczenie prądu należy przypisać do
właściwego miejsca obwodu. Przy filtrze wyjściowym prąd wzmacniacza może
różnić się od prądu cewki; napięcie źródła też nie musi być napięciem
na zaciskach głośnika. Nie są to dwa określenia tej samej wielkości.

**Obliczenie:** mała rezystancja ma większe znaczenie względne dla
niskoimpedancyjnego połączenia. C26P przy 100 l i Rźródła=0,1 Ω ma
Qtc około 0,6106 zamiast 0,5692 w rzucie Le=0. C26P pozostaje przykładem,
nie wybranym głośnikiem. Nie określono dopuszczalnego R z briefu;
trzeba powiązać ten parametr z końcowym DSP i budżetem napięcia.

![Rezystancja źródła a tłumienie i obwiednia napędu](../wyniki/87_P22A_rezystancja_zrodla_i_obwiednia.png)

## Wykonany zakres i jednostki

27 konfiguracji elektrycznych,4 objętości 30/60/100/150 l,6 rezystancji
0/0,02/0,1/0,5/1/2 Ω i 5 rodzin L/C. Razem 3240 modeli portu i 19440 punktów
napędu przy 20/25/31,5/40/63/80 Hz. Osobno 648 projekcji Q i siatka 10–200 Hz
licząca 807 częstotliwości na model.
R=2 Ω i L=300 µH są próbami stresowymi, nie zaleceniem konstrukcyjnym.

Fazory napięć, prądów i ciśnienia są RMS. Ruch membrany oceniono jako
szczyt sqrt(2)*|X|. Ciśnienie pochodzi z idealnego monopola 2π/1 m;
nie jest prognozą w pokoju 42,55 m³. Każdy punkt oznacza oddzielny ustalony
sinus, bez kwalifikacji czasu pracy, muzyki lub kompresji cieplnej.
Wspólne 40 V RMS/12 A RMS i katalogowe Xmax służą porównaniu.
Nie użyto nieznanej mocy katalogowej C26P jako limitu cieplnego.

[Konfiguracja](../dane/konfiguracje/p22a_port_wzmacniacza.json),
[punkty napędu](../wyniki/p22a_naped_z_portem.csv),
[zmiana transferu](../wyniki/p22a_zmiana_transferu.csv).

## Równania i bilans energii

Pasywny port Thevenina ma szeregowe Rs+sLs i pojemność Cp na zaciskach:

    Zm = Rms+s*Mms+K/s
    K = 1/Cms+rho*c²*Sd²/Vb
    Vt = (Re+s*Le)*Id+BL*v
    Zm*v = BL*Id
    Is = Id+s*Cp*Vt
    Vs = Vt+(Rs+s*Ls)*Is

Te cztery ostatnie równania rozwiązano także niezależną macierzą 4×4
dla wszystkich 19440 opublikowanych punktów. Maksymalna różnica względna
wynosi 1,98908e-15.
Model 5 stanów x, v, Id, Is, Vt dla dodatnich Le, Ls, Cp daje osobną kontrolę 162 punktów:
różnica do 3,45805e-13.

    E = (K*x²+M*v²+Le*Id²+Ls*Is²+Cp*Vt²)/2
    dE/dt = Vs*Is-Rs*Is²-Re*Id²-Rms*v²

Indukcyjności i pojemność magazynują energię. W ustalonym sinusie:

    Re(Vs*conj(Is)) = Rs*|Is|²+Re*|Id|²+Rms*|v|²

Maksymalny względny residual bilansu w 3240 siatkach wynosi
1,25701e-15. To kontrola numeryczna,
nie dokładność przewidywania fizycznego egzemplarza.
Nie dodano kolejny raz masy promieniowania do katalogowego Mms.

![Oddzielne prądy i udział strat czynnych](../wyniki/88_P22A_dwa_prady_i_bilans_mocy.png)

## Co można wyprowadzić po całej dodatniej rezystancji

Dla Le=Ls=Cp=0 i Rtotal=Re+Rs:

    Q(Rs) = sqrt(M*K)/(Rms+BL²/(Re+Rs))
    dQ/dRs > 0
    f_mechanical = sqrt(K/M)/(2*pi)

Zmienia się tłumienie, nie mechaniczna częstotliwość własna tej projekcji.
Nie przypisujemy jednego Q ogólnemu układowi RLC z dodatkowymi biegunami.

| Przykład 100 l / R źródła 0,1 Ω | Qtc przy R=0, Le=0 | Qtc z Rs, Le=0 | Zmiana pułapu przy 80 Hz, pełne Le |
|---|---:|---:|---:|
|C02: Dayton RSS390HF-4|0,757725|0,779293|-0,230862 dB|
|C04: SB Acoustics SB34SWPL76-4|0,423366|0,434951|-0,237921 dB|
|C26P: SB Acoustics SB34SWPL76-3-DV parallel|0,569166|0,610563|0 dB|
|C26S: SB Acoustics SB34SWPL76-3-DV series|0,569166|0,579568|-0,158235 dB|

**Dowód dla samego Rs:** przy stałej częstotliwości>0 pasywny głośnik
ma Re(Zdriver)>0. Wówczas

    d|Zdriver+Rs|²/dRs = 2*(Re(Zdriver)+Rs) > 0

Przy wspólnych limitach Vs, Is i X obwiednia dopuszczalnego prądu głośnika
nie rośnie po dodaniu Rs. Jej trzy ograniczenia to
Vmax/|Zdriver+Rs|, Imax i Xmax/(sqrt(2)*|X/Id|).
To wniosek dla wszystkich Rs≥0 i każdego dodatniego f w tym modelu,
nie tylko tabeli.648 grup porównano również numerycznie.
Gdy aktywny jest sam katalogowy limit ruchu, ten sam ruch daje ten sam
pułap monopola. Rezystor nie zwiększa Sd ani Xmax.

Nie przenosimy tego dowodu na dowolny obwód LC, aktywną pętlę,
model temperatury lub realny wzmacniacz. L/C mogą zmieniać rozkład napięć
i prądów przy zachowaniu pasywności całego obwodu.

## Granice oraz brakujące zjawiska

- Rs=Ls=Cp=0 odtwarza wcześniejszy model głośnika.
- Ls→0 i Cp→0 redukują odpowiednie elementy równań bez dodawania strat.
- Rs→∞ przy ustalonym Vs i f oznacza zanik prądu oraz ruchu. Świadkowie
  przy 10⁴/10⁸Ω zachowują zbieżność Rs*|Is|→1 dla Vs=1 V.
- Le=0 to osobna projekcja drugiego rzędu; nie pomiar nieliniowej cewki.
- Katalogowe Le i liniowe T/S nie obejmują PWM, sprzężenia wzmacniacza,
  zasilacza, clippingu, dynamicznego ograniczenia prądu lub regeneracji energii.

Zerowy Rs jest prawidłową granicą źródła idealnego, nie stwierdzeniem o
rezystancji przewodów. Dane R/L/C nie zostały przypisane żadnemu producentowi.
Nie wykonywano doboru handlowego ani zakupu elektroniki.

## Odtwarzanie i kolejny krok

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_port_P22A.py

[Kontrole i tożsamości](../wyniki/p22a_kontrole_niezalezne.json),
[manifest](../wyniki/manifest_portu_P22A.json).
Kolejny etap P22B/P24 ma objąć saturację, SEM od ruchu, wykonalność
jednoczesnego ograniczenia V/I oraz dynamiczną ochronę X/T po korekcji DSP.
Badanie P21B nadal ma osobny aktywny przebieg; następnie P21C wiąże główną
komorę, wypełnienie i regulację. Wybór jednego głośnika i konstrukcji,
końcowy PDF i Release 1 pozostają otwarte.
