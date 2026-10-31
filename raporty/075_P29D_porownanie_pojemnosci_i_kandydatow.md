# Raport 075 — P29D: kontrola rekomendacji po rozszerzeniu puli i porównanie pojemności

**31.10.2026. Status:** wykonano 25 niezależnie odtwarzalnych obliczeń prostego modelu zamkniętego T/S. To **uzupełnienie** istniejących 74 raportów, nie zmiana końcowego wyboru, certyfikowany ranking albo model zmierzonych zniekształceń.

## Pytanie i uczciwy stan wybrania głośnika
- `main` po P24I zawiera **34 unikalne produkty, 35 konfiguracji elektrycznych, 33 wstępnie analizowane**; dwa przypadki HOLD: EMS B15EX (niekompletny fabryczny T/S) i SUPRAVOX 400-2000 EXC (niespójne Mms w dokumentacji).
- Ostatnia wspólna **kampania z zakresem niepewności na wszystkich 27 starych konfiguracjach** (P29A/C, raporty 053 i 055) preferuje **Dayton RSS390HF-4 C02** dla założonych strat `Pcu ≈ 27–86 W` przy 120 l. Przy `Pcu >=87 W` w tej próbie wygrywa RSS390HE-22 C11. Te W są *budżetami modelu*, nie potwierdzoną pracą ciągłą.
- Nowszy przesiew 35 konfiguracji (33 kompletnych) ma inny zakres, brak pełnych wariacji Sobola, a ograniczenia wejścia wzmacniacza mają wspólny uproszczony budżet 4 Ω również dla 8 Ω. **Nie dowodzi, że nowy produkt zastąpił C02**.
- P24B–P24I badały wyłącznie model C02, nie wszystkie nowe głośniki; nie ma podstaw, aby ekstrapolować ich Rth/Cth na PHL, HE lub STX.

## Prosty model własny — 25 kombinacji
Parametry fabryczne `Fs,Qts,Vas,Sd,Xmax` dla C02, C11, C19, STX C06 i nowego PHL N07 pochodzą z kart producentów (odnośniki w JSON).
Dla `Vb` netto 75/80/100/120/150 l, szczelnego modelu 2. rzędu:
```text
r = sqrt(1+Vas/Vb)
fc = Fs*r
Qtc = Qts*r
H(jw) = (j*w/wc)^2 / ((j*w/wc)^2+(j*w/(wc*Qtc))+1)
y=(f3/fc)^2; y²+(2−1/Qtc²)y−1=0, y>0
F3=fc*sqrt(y)
```
Przy obliczaniu `f3` sprawdzono numerycznie dokładnie `|H(j2πf3)|=1/sqrt(2)`. Znormalizowany poziom przy 20 Hz pokazuje wymagany kształt korekcji, **nie maksymalny SPL**.

### Daytona RSS390HF-4 — zależność od litrażu
| Netto Vb [l] | Qtc | fc [Hz] | Idealne F3 [Hz] |
|---:|---:|---:|---:|
| 75 | 0.841 | 38.1 Hz | 33.0 Hz |
| 80 | 0.822 | 37.3 Hz | 32.8 Hz |
| 100 | 0.760 | 34.4 Hz | 32.2 Hz |
| 120 | 0.715 | 32.4 Hz | 32.1 Hz |
| 150 | 0.668 | 30.3 Hz | 32.2 Hz |

Z 100 do 150 l idealne F3 zmienia się nieznacznie; należy rozpatrywać również Qtc, szczytowe X, efektywne napięcie i realne usztywnienie paneli. Raport 055 pokazuje, że przy wybranym konserwatywnym kryterium **99 l na siatce 1 l** jest już w 0,2 dB od plateau — nie jest to gwarancja identycznego SPL w pokoju.

### Porównanie przy 120 l netto (z fabrycznych T/S, bez EQ)
| Przetwornik | Qtc | Idealne F3 | 20 Hz względem wysokiego pasma |
|---|---:|---:|---:|
| Dayton RSS390HF-4 | 0.715 | 32.1 Hz | -8.9 dB |
| Dayton RSS390HE-22 (series nominal T/S) | 0.644 | 40.6 Hz | -11.3 dB |
| Dayton RSS390HO-4 | 0.496 | 52.4 Hz | -11.6 dB |
| STX W.32.800.8.FCX | 0.523 | 46.9 Hz | -10.8 dB |
| PHL 6301MNd | 0.383 | 118.8 Hz | -19.3 dB |

W szczególności PHL ma duże Vd i moc katalogową, ale niskie `Qts=0.26`, `Fs=36 Hz`; w prostej szczelnej 120 l wymagałby bardzo znacznej korekcji, której budżet mocy/X/THD nie został potwierdzony. RSS390HE-22 jest znacznie bardziej obiecujący w **kompaktowym 75–80l** niż PHL, choć jego rodzima odpowiedź niskiego basu 20–40Hz w tym modelu też nie jest płaska i wymaga oceny EQ.

**Uwaga o interpretacji F3:** to bezstratny T/S 0D, bez rzeczywistej dobroci strat `Ql`, włókniny, nieszczelności, paneli, pomieszczenia ani końcowych filtrów; producent może podawać inne F3 ze swojego symulatora. Duże Xmax nie oznacza małego F3, małe F3 nie potwierdza czystego basu przy dużym poziomie.

## Co sugeruję wykonać dla rzeczywistych wymagań
1. **Pierwszy prototyp badawczy C02** o regulowanej objętości **100/120/150 l**, stan startowy 120 l. Dwie sztuki, kanały 7/8 niezależnego DSP, po uprzednim zatwierdzeniu wymiarów.
2. Jeśli gabaryt/podłoga priorytetowe, **100 l netto** jest bardziej racjonalnym celem pierwszego stałego projektu niż 150 l; modelowy kompromis przy 20–40 Hz jest mały względem 120 l, ale niezwalidowany akustycznie.
3. Jeżeli *muszą* być dwa mniejsze pudełka **75–80 l**, przeanalizować od nowa C11 HE-22 (27mm szczytowy katalogowy Xmax i Vas 71,3l), C02 HF oraz 12″ STX FCX na identycznym dopasowaniu DSP/AMP, analizie X/T i rzeczywistych kosztach.
4. W nowej puli **PHL 6301MNd** warto zachować jako wysokowydajny punkt porównawczy, ale *nie* ogłaszać nowym liderem 20Hz z samej mocy 1300W AES. Inne nowe modele także nie zastąpiły C02 na podstawie dostępnych danych.
5. Zanim będzie decyzja zakupowa: masa i gabaryt obu pudełek w pokoju, kosztorys dwóch głośników i dwóch końcówek klasy D, i niepewności BL(x)/Cms(x)/Re(T), dane rzeczywistego nieliniowego X, pełny rysunek ze wszystkimi elementami do 500 mm głębokości.
6. Dotychczasowy korpus `880×480×500mm` (W×D×H) może stać pionowo `500×480×880mm`. **480 mm to głębokość samego drewnianego korpusu**, zostawia tylko 20mm do całkowitego limitu 500mm. Wariant skrócony do 470mm ma konflikt wkładów z matą 6mm (raport 055); nie rekomendować jego CNC bez ponownego planu maty i mocowania.

**Konkluzja:** *wstępny faworyt nie został obalony*. Najbardziej praktyczna pojemność dla prototypu 100–120 l, badawczy stan startowy 120 l i dodatkowe 150 l jako kontrola. Nowa kampania tych samych kryteriów dla całej puli 33 jest nadal konieczna, aby nazywać nowy ranking kompletnym.

## Odtwarzanie
`node skrypty/p29d_kontrola_ts_objetosc.js`

`wyniki/p29d_t_s_objetosc_20261031.json` — pełne parametry wejściowe, źródła i 25 wyników.
