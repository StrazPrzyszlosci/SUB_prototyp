# Raport 031 — P21A: reakcja powietrza na elastyczne ściany

Stan: 2026-10-25. Wykonano **72 sprzężone punkty kontrolne** oraz
odrębne projekcje pola i kontrole masy. Jest to odniesienie:
nieskończona odgroda, para identycznych ścian, jednorodne ciśnienie
komory i cztery pozostałe ściany sztywne. Nie jest to pole3D realnej
skrzyni z otworem, koszem i podparciem ani odpowiedź pokoju.

## Dlaczego dodano sprzężenie

**Wynik wcześniejszej kontroli:** w13z27projekcji obliczona moc
promieniowania przekraczała10% założonego tłumienia suchej płyty.
Próg10% był bramką adekwatności modelu, nie słyszalności lub odbioru.
Nie można było traktować takiej projekcji jako pełnej energetycznej
prognozy hałasu przy ruchu obliczonym bez reakcji powietrza.

Dodano więc rezystancję radiacyjną i przybliżoną reakcję masową do
równań ruchu. Nie przedstawiamy samoistnego spadku amplitudy jako
uniwersalnej korzyści: masa powietrza może przesunąć odpowiedź bliżej
rezonansu i zwiększyć amplitudę przy danej częstotliwości.

## Operator zewnętrzny

**Wyprowadzenie z całki Rayleigha:** dla zadanych prędkości w odgrodzie
przy exp(+jwt), jądro ciśnienia ma postać

```text
p(x) = j*rho*omega/(2*pi) * integral(v(y)*exp(-j*k*R)/R dS)
```

Rzeczywista część reakcji wynika z sin(kR)/R. W punkcie R=0 granica
jest skończona. Jest to dodatnio półokreślona forma mocy, równoważna
odrębnej całce kierunkowej w półprzestrzeni.

Urojona część ma słabą osobliwość. Własny składnik zastąpiono lokalną
masą dysku o polu wagi kwadratury, wykorzystując sprawdzoną wP11
granicę8*rho*a³/3. Poza diagonalą użyto jądra Rayleigha. To aproksymacja
numeryczna z kontrolą siatki, nie dokładny samoczynny elementBEM.
Nie dodano tej masy do Mms przetwornika: nowy model dotyczy płyt,
a stożek jest zadanym źródłem objętości.

```text
[K-omega²*M+j*omega*Cstruct+j*omega*Zrad] q = Fpressure
```

R i X są wzajemne, a R jest nieujemne z dokładnością arytmetyki.
Ujemne pozostałości znormalizowanych wartości własnych R rzędu10^-16
to poziom zaokrągleń. Nie wyprowadzamy z tego globalnego certyfikatu czasowej
przyczynowości każdej aproksymacji jądra.

## Komora i para ścian

**Model wewnętrzny0D:** Cab=V/Kgas, gaz z dodatnią relaksacją tau=5ms,
V=100l jako kontrola. Cw=Fᵀq jest podatnością jednej ściany z danej pary.
Zewnętrzne pole i pozostałe ściany nie zostały utożsamione z pokojem.

Podatność ścian zmienia podatność akustyczną zależnie od częstotliwości,
nie geometryczny litraż netto. Nie traktować jej jako stałego bonusu
pojemności lub równoważnika większej sztywnej skrzyni: panel ma własne
rezonanse,tłumienie i pole promieniowane.

```text
pinside = Qsource / [j*omega*(Cab+2*Cw)]
Psource = Pgas_relaxation + 2*Pstructural + 2*Pradiation
```

Źródło odniesienia odpowiada ruchowi stożka95dB RMS/4pi/1m. To
definicja wymuszenia, **nie zatwierdzony próg użytkownika ani wynik całej
obudowy**. Zewnętrzny panel w odgrodzie ma inne warunki niż stożkowy
monopol4pi; nie dodawano mechanicznie ich liczb SPL.

Wnioski dla f>80Hz oznaczono jako ekstrapolację komory0D. Przestrzenne
mody, siły kosza i wzajemna radiacja różnych ścian wymagają pełniejszej
geometrii. Idealnie sztywne cztery ściany są hipotezą odniesienia.

## Wynik i znaczenie dla konstrukcji

Zbadano6wariantów K2/22mm: SSSS/CCCC oraz0/1/2ściągi. Uwzględniono
20/40/80Hz i próbki wokół dominującej w ciśnieniu postaci suchej płyty.
Nie należy mylić tej postaci z pierwszą w posortowanej liście modów.

W72punktach stosunek maksimum amplitudy z powietrzem do suchej płyty
przy tej samej presji mieścił się około0,8475–1,0860. To maksimum
próbkowanego zbioru, nie globalna obwiednia ciągłego pasma.

W SSSS/20–80Hz wpływ był niewielki: bez ściągu stosunek przy80Hz
wyniósł1,01055, z jednym1,00142, z dwoma1,00074. Nie oznacza to braku
znaczenia powietrza w pobliżu rezonansów lub przy innym tłumieniu.

**Rekomendacja:** kontynuować porównanie usztywnień wraz z geometrią
frontu i rzeczywistymi ścieżkami sił. Nie optymalizować wyłącznie f1
suchej ściany i nie przedstawiać odrębnej projekcji pola jako pełnego
bilansu całej skrzyni.

![Odpowiedź i reakcja](../wyniki/44_P18A_dynamika_i_reakcja_powietrza.png)

## Niezależne kontrole

- Wcześniejsze27projekcji Rayleigha porównano dwiema całkami mocy:
  oporem sin(kR)/R oraz odrębną całką kierunkową. Różnica do3,93e−15.
- Jednorodnie poruszany prostokąt ma masę odniesienia0,09041754kg,
  obliczoną niezależną całką nakładania i transformacją Duffy.
  Dyskretyzacja16×16 dała0,08977191kg, różnicę0,714%; błąd malał
  przy zagęszczaniu. Nie jest to masa panelu lub realnego kosza.
- Ostatnia zmiana zespolonej podatności między siatkami16×24i20×28
  wyniosła0,268% przy20Hz oraz0,422% przy80Hz.
- Alternatywny własny składnik masy zmienił podatność o2,23e−6
  i5,86e−5 względnie. Są to dwie aproksymacje, nie dwie niezależne prawdy.
- Kontrola wzajemności z dwoma kanałami siły i granica zerowej reakcji
  powietrza przeszły poprawnie.
- Reszty bilansów płyty oraz pary z gazem były rzędu10^-13,
  poniżej przyjętej bramki1e−8. Nie tracono lub nie tworzono energii
  przez samo dopisanie odrębnie wypromieniowanej mocy.

## Artefakty i zakres pozostały

- [72sprzężone punkty](../wyniki/p21a_para_scian_z_reakcja_powietrza.csv).
- [Masa i bilanse](../wyniki/p21a_sprzezenie_podsumowanie.json),
  [siatka i wzajemność](../wyniki/p21a_kontrole_siatki_i_wzajemnosci.json).
- [Wcześniejsze projekcje](../wyniki/p18a_Rayleigh_panelu.csv),
  [para ścian i gaz](../wyniki/p18a_para_scian_i_gaz.csv).

```bash
python3 skrypty/emisja_i_sprzezenie_plyty_P18.py
python3 skrypty/reakcja_powietrza_P21A.py
python3 skrypty/sprawdz_reakcje_powietrza_P21A.py
```

**P21 pozostaje częściowy.** Potrzebne są front z otworem i podparciem
przetwornika, kompletna geometria, lokalne ciśnienia i rzeczywiste
połączenia. Nie jest to jeszcze prognoza szumu gotowej skrzyni ani
poziomu w sweetspocie. Pokój4,6×3,7×2,5m, układ RTVlewo/kanapaprawo
i miejsce dwóch egzemplarzy nadal obowiązują przy wyborze konstrukcji.
