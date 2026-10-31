# Raport 062 — P25D: próbkowanie bariery energetycznej głośnika

**31.10.2026. Status: wykonana analiza matematyczna i kampania numeryczna.**
To **nie jest** gotowy limiter miniDSP, zweryfikowany wzmacniacz ani pomiar subwoofera. Badanie rozwija ograniczenie ciągłe z [P25C, raport 058](058_P25C_sygnaly_czasowe_i_bariera_energii.md).

## Pytanie, hipoteza i wynik

Poprzednia bariera energii wymagała znajomości stanów x, v, i, θ w czasie ciągłym. Czy stosowanie jej tylko co 2/0,5/0,167 ms, ze stałym napięciem pomiędzy decyzjami (zero-order hold, ZOH), chroni ten sam obszar?

**W badanej rodzinie modeli: nie.** 12/12 trajektorii dla każdej częstotliwości sterownika przekroczyło limit energii przy próbkowaniu punktowej bariery. Wyprowadzono nową **konserwatywną granicę energii między próbkami**, która ma gwarancję matematyczną w przyjętym modelu i nie przekroczyła progu w 72/72 badanych trajektoriach dwóch wariantów (bieżący stan oraz opóźniona próbka).

## Model i dane wejściowe

Liniowy model elektro-mechano-termiczny zamkniętej skrzyni 0D:

- \`x'=v\`; \`M v'=BL*i-Rm*v-K*x\`; \`L i'=u-Re(theta)*i-BL*v\`
- \`Cth*theta'=Re(theta)*i²-theta/Rth\`, \`Re(theta)=Re0*(1+alpha*theta)\`
- \`K=1/Cms+rho*c²*Sd²/Vb\`; \`E=(K*x²+M*v²+L*i²)/2\`.

Pochodzenie parametrów: katalogowe T/S 26 modeli w \`dane/przetworniki/pula_rozszerzona.json\`; użyte trzy modele C02 (RSS390HF-4), C11 (RSS390HE-22 seria), C06 (STX W.32.800.8.FCX). Odstępstwa od rzeczywistych przetworników są możliwe: skuteczne T/S wyznaczono przez \`Cms=Vas/(rho*c²*Sd²)\`, \`M=1/((2*pi*Fs)²*Cms)\`, \`Rm=2*pi*Fs*M/Qms\`, \`BL=sqrt(2*pi*Fs*M*Re0/Qes)\`. Bez drugiego dodawania masy powietrza do skutecznego Mms. Przyjęto \`rho=1,2 kg/m³\`, \`c=343 m/s\`, \`Vb=120 l\`.

P25C definiuje \`Xref=0,6 Xmax\`, \`Icap=min(16,97 A, sqrt(theta_lim/[Rth*Re0*(1+alpha*theta_lim)]))\`, \`theta_lim=80 K\`, \`Ecap=min(K*Xref²,L*Icap²)/2\`. Liczby cieplne to **założenia stresowe**, nie rzeczywista specyfikacja głośnika.

## Dowód: nowa niezmiennicza granica ZOH

Przy dodatnich K,M,L,Rm, ciągłej wzajemności BL oraz \`Re(theta)>=Re0>0\` dla \`theta>=0\`:

\`E'=u*i-Rm*v²-Re(theta)*i² <= u*i-Re0*i² <= u²/(4*Re0)\`.

Jeżeli w czasie \`Delta=1/f_controller\` napięcie \`u_k\` pozostaje stałe, to **dla każdej chwili interwału**:

\`E(t)<=E(t_k)+u_k²*Delta/(4*Re0)\`.

Wystarcza zastosować ograniczenie:

\`|u_k| <= min(U_rail, sqrt(4*Re0*max(0,Ecap-E(t_k))/Delta))\`.

Przy początkowym \`E<=Ecap\` warunek indukcyjnie utrzymuje \`E<=Ecap\` w każdym interwale i między próbkami. Ponieważ \`E>=K*x²/2\` oraz \`E>=L*i²/2\`, zapewnia to \`|x|<=Xref\` i \`|i|<=Icap\` **wyłącznie w tym modelu**. Przy właściwie ograniczonym \`Icap\` temperatura pozostaje w \`0<=theta<=theta_lim\`: na theta=0 pochodna jest nieujemna, na theta=theta_lim nie dodatnia.

**Pomiar opóźniony o dokładnie jedną próbkę:** w powyższym wzorze można konserwatywnie przyjąć \`Eupper=E(t_{k-1})+u_{k-1}²*Delta/(4*Re0)\` zamiast nieznanego \`E(t_k)\`. To obejmuje dopływ energii podczas jednego pełnego interwału; wymaga dokładnego historycznego pomiaru energii i dokładnie znanego poprzedniego u. Żadna z tych gwarancji **nie** obejmuje błędów czujników, dodatkowej latencji, realnego toru DAC, zmian BL/Le/K, nasycenia zasilacza ani nieliniowej sprężyny powietrznej.

## Symulacja numeryczna

**144 trajektorie**, każda 1 s: 3 kandydaci × 1 objętość (120 l) × 2 rodziny termiczne × 2 sygnały (ośmiotonowy zgodnofazowy i subsoniczny z impulsem) × 3 częstotliwości decyzji (500/2000/6000 Hz) × 4 strategie:

- **rail:** sam limit szyn, napięcie ZOH.
- **sample_pointwise:** ciągła formuła P25C zastosowana tylko w chwilach próbkowania; potem ZOH.
- **zoh_energy_bound:** powyższa granica z energią stanu na początku próbki.
- **zoh_delayed_state:** ta sama granica z pomiarem o jedną próbkę starszym i zachowawczą estymacją.

Dwa nieidentyfikowane scenariusze cieplne: \`Rth/Cth/theta0 = 0,3 K/W / 200 J/K / 0 K\` oraz \`1,2 K/W / 50 J/K / 60 K\`. Pobudzenie 70 V RMS **przed** filtrem BW2 HP20 + LR4 LP80 (software dla 24 kHz), szyny ±56,5685 V. Porównanie różnych strategii **nie utrzymuje jednakowej głośności**. RK4: \`h=1/24000 s\`. Stanów x/v/i nigdy sztucznie nie obcinano.

| Strategia / sterownik | Naruszenia Ecap na 12 | Maks. E/Ecap | Maks. x/Xref | Maks. i/Icap |
|---|---:|---:|---:|---:|
| Szyny / 500 Hz | 12 | 367,459 | 2,713 | 4,362 |
| Szyny / 2000 Hz | 12 | 368,567 | 2,718 | 4,097 |
| Szyny / 6000 Hz | 12 | 368,929 | 2,718 | 4,139 |
| Punktowa bariera / 500 Hz | 12 | 135,425 | 1,513 | 4,738 |
| Punktowa bariera / 2000 Hz | 12 | 91,376 | 1,364 | 4,414 |
| Punktowa bariera / 6000 Hz | 12 | 26,165 | 0,626 | 2,347 |
| ZOH, obecny stan / 500 Hz | **0** | 0,990748 | 0,346 | 0,619 |
| ZOH, obecny stan / 2000 Hz | **0** | 0,999815 | 0,349 | 0,833 |
| ZOH, obecny stan / 6000 Hz | **0** | 0,999995 | 0,349 | 0,923 |
| ZOH, próbka opóźniona / 500 Hz | **0** | 0,965027 | 0,341 | 0,568 |
| ZOH, próbka opóźniona / 2000 Hz | **0** | 0,998747 | 0,348 | 0,757 |
| ZOH, próbka opóźniona / 6000 Hz | **0** | 0,999960 | 0,349 | 0,884 |

![P25D: energia w zależności od sposobu próbkowania](../wyniki/102_P25D_bariera_probkowana.svg)

Duże wychylenia w wariantach bez skutecznej ochrony wykraczają poza dziedzinę liniowego modelu. Nie są prognozą uszkodzenia głośnika. Liczba 12/12 dotyczy *skończonej macierzy przypadków*, nie prawdopodobieństwa awarii.

## Sprawdzenie zbieżności

Dla **96 przypadków** (2000/6000 Hz) powtórzono obliczenia z \`h=1/48000 s\` i filtrem przeliczonym na 48 kHz. Względem pierwszego przebiegu największa bezwzględna różnica \`max(E/Ecap)\`: dla \`zoh_energy_bound\` **1,54×10⁻⁷**, dla \`zoh_delayed_state\` **1,36×10⁻⁶**. Maksymalne różnice \`max(x/Xref)\`: **1,37×10⁻⁶** i **1,70×10⁻⁶**; prądu **1,60×10⁻⁴** i **1,90×10⁻⁴**. To kontrola zagęszczenia RK4 z jednoczesnym zagęszczeniem filtru.

**Istotna uwaga:** punktowa bariera wykazała brak odpowiedniej zbieżności: nawet **9,625** różnicy maksimum \`E/Ecap\`, **0,515** maksimum \`x/Xref\`. Nie wolno podawać tych maksimów jako numerycznie ustalonych dokładnych ekstremów ani porównywać ich jak wyników pomiarowych. Oba kroki wskazały jednak przekroczenia w badanych przypadkach. Nie wykonano niezależnej integracji DOP853; dowód wyłącznie dla konserwatywnej bariery ZOH jest analityczny i nie polega na zgodności samych trajektorii.

## Wniosek, ograniczenia i dalszy krok

**Nie przenosić idealnej, ciągłej bariery P25C wprost na próbkowany regulator.** Granica ZOH daje bezpieczny *matematycznie* punkt odniesienia, ale może być skrajnie konserwatywna i ograniczać sygnał w stopniu nieakceptowalnym akustycznie. Kolejny eksperyment powinien sprawdzić predykcję stanu i obwiednie błędów obserwacji, identyfikacji, rekonstrukcji i opóźnień oraz koszt zachowawczości w poziomie akustycznym. Nie wybrano presetu dla miniDSP ani nowych parametrów głośnika.

**Odtwarzanie:** \`OPENBLAS_NUM_THREADS=1 python skrypty/p25d_probkowana_bariera.py\`.
Konfiguracja: \`dane/konfiguracje/p25d_probkowanie.json\`. Wejściowe T/S: \`dane/przetworniki/pula_rozszerzona.json\`. Program generuje pełne \`wyniki/p25d_probkowanie.csv\` (144 trajektorie), \`wyniki/p25d_podsumowanie.json\`, \`wyniki/p25d_slady.json\` oraz manifest SHA-256. Weryfikacja zagęszczenia: zmienić \`integration_rate_hz\` na 48000 i \`controller_rates_hz\` na \`[2000,6000]\` i porównać maksima.
