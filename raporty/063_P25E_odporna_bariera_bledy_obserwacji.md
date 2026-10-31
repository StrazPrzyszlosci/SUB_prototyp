# Raport 063 — P25E: niepewność obserwacji, parametrów i próbkowana bariera ochronna

**Data obliczeń: 2026-10-31.** Nowe badanie analityczne i numeryczne modelu 0D, kontynuacja [P25D/raportu 062](062_P25D_probkowana_bariera_energetyczna.md). **Nie jest to pomiar, certyfikacja bezpieczeństwa, nastawa miniDSP ani ocena THD.**

## Pytanie naukowe i hipoteza

W P25D wyprowadzono ograniczenie energii dla cyfrowego sterownika z utrzymywaniem napięcia między próbkami (ZOH). Nadal zakładano dokładną znajomość parametrów oraz położenia, prędkości i prądu. Sprawdzamy:

1. Czy naiwne podstawienie obarczonych błędem pomiarów do tej samej formuły utrzymuje zadany obszar energetyczny?
2. Czy da się wyprowadzić *wystarczający warunek* bezpieczeństwa modelowego dla ograniczonych, lecz nieznanych błędów obserwacji i parametrów?
3. Jakiego spadku wykorzystania sygnału można się spodziewać przy bieżącym pomiarze i przy obserwacji opóźnionej o dokładnie jedną próbkę?

Hipoteza: kontrola samej nominalnej energii nie daje gwarancji przy rozbieżnych modelach; konserwatywny górny estymator rzeczywistej energii oraz minimalny opór cewki pozwalają przywrócić ścisły warunek niezmienniczości.

## Model, pochodzenie i dziedzina

Stosujemy **liniowy, skupiony** model zamkniętej obudowy P25C/P25D:

\[
\dot x=v,\qquad M\dot v=BL\,i-R_m v-Kx,
\]
\[
L\dot i=u-R_e(\theta)i-BL\,v,\qquad
C_{\rm th}\dot\theta=R_e(\theta)i^2-\theta/R_{\rm th},
\quad R_e(\theta)=R_{e0}(1+\alpha\theta).
\]

Dodatnie \`K,M,L,Rm,Re0,Rth,Cth\` oraz *identyczne BL w sile i SEM* są wymaganiami modelu. \`K=1/Cms+\rho c^2 Sd^2/Vb\`, \`Vb=120 l\`, \`\rho=1.2 kg/m³\`, \`c=343 m/s\`, \`\alpha=0.004 1/K\`. Brak zależności BL(x), Cms(x), Le(x,i), strat konstrukcji, rzeczywistej maty, pełnego pola gazu P21D, nieliniowości powietrza i końcowej impedancji wzmacniacza.

Wykorzystano trzy wiersze parametrów T/S z \`dane/przetworniki/pula_rozszerzona.json\`: C02 (Dayton RSS390HF-4), C11 (Dayton RSS390HE-22 w połączeniu szeregowym) i C06 (STX W.32.800.8.FCX). Ich nominalne liczby wpisano jawnie do konfiguracji jako zamrożony punkt odniesienia. **Nie zmierzono** rozrzutu tych parametrów.

Narzuciliśmy hipotetyczne obwiednie stresowe: \`K ±10%\`, \`M ±8%\`, \`L ±15%\`, \`BL ±10%\`, \`Rm ±15%\`, \`Re0 ±10%\`. W kampanii wykorzystano *dwa skorelowane narożniki* tych przedziałów, a nie wszystkie niezależne kombinacje. Błędy obserwacji są deterministycznymi sinusami ograniczonymi bezwzględnie: \`|δx|≤0.2 mm\`, \`|δv|≤0.03 m/s\`, \`|δi|≤0.15 A\`. Przy porównaniu strategii zachowano tę samą realizację błędu dla odpowiadającej sobie trajektorii.

Scenariusze cieplne z P25C: \`Rth=0.3 K/W, Cth=200 J/K, θ0=0 K\` oraz \`Rth=1.2 K/W, Cth=50 J/K, θ0=60 K\`. Każda trajektoria trwa 0,8 s; nie zastępuje to testu pracy ciągłej. \`Rth\`, \`Cth\` i \`α\` są **ustalone wewnątrz scenariusza**, a nie objęte dowodem na niezależną niepewność. Przyjęty próg \`θlim=80 K\` nie jest danymi producenta.

## Dowód: warunek wystarczający mimo błędów stanu

Energia rzeczywistego, lecz nieznanego modelu z ustalonymi dodatnimi parametrami:

\[
E=\frac12(Kx^2+Mv^2+Li^2),\quad
\dot E=ui-R_m v^2-R_e(\theta)i^2.
\]

Jeśli \`θ≥0\` i \`Re0≥Rmin>0\`, przez domknięcie kwadratu:

\[
\dot E\le ui-R_{\min}i^2\le \frac{u^2}{4R_{\min}}.
\]

Prawa nierówność jest niezależna od nieznanego \`BL\`, o ile zachowuje się wzajemność siła–SEM; nie wymaga szacowania prądu podczas interwału.

Mamy przedziały \`K∈[K-,K+]\`, \`M∈[M-,M+]\`, \`L∈[L-,L+]\`. W chwili próbkowania otrzymujemy \`(xm,vm,im)\` z błędami nie większymi niż \`(εx,εv,εi)\`. Wobec tego

\[
E(t_k)\le \overline E_k =
\frac12\big[K_+(|x_m|+\epsilon_x)^2+
M_+(|v_m|+\epsilon_v)^2+
L_+(|i_m|+\epsilon_i)^2\big].
\]

Dobieramy jedno **wspólne**, odporne ograniczenie energii
\[
E_\star=\frac12\min(K_- X_{\rm ref}^2,L_- I_{\rm cap}^2),
\]
gdzie \`Xref=0.6 Xmax\` jest *umowną* granicą ruchu, nie gwarancją niskiego THD, a
\[
I_{\rm cap}=\min\left(I_{\rm hardware},
\sqrt{\frac{\theta_{\rm lim}}
{R_{\rm th}R_{e0,+}(1+\alpha\theta_{\rm lim})}}\right).
\]

Dla przedziału ZOH o długości \`Δ\` i **dokładnie przyłożonym** napięciu \`u_k\`:

\[
|u_k|\le \min\left(U_{\rm rail},
\sqrt{\frac{4R_{\min}}{\Delta}
\max(0,E_\star-\overline E_k)}\right).
\]

Jeśli \`E(0)≤E★\`, to przy \`Ebar≤E★\` całka nierówności daje \`E(t)≤E★\` również **między próbkami**. Jeśli oszacowanie jest nadmiernie konserwatywne i \`Ebar>E★\`, reguła wybiera \`u_k=0\`; wtedy energia nie rośnie, nawet jeśli estymator jest zbyt pesymistyczny. Indukcja zapewnia \`E(t)≤E★\`, a przez dodatniość formy \`|x|≤Xref\` oraz \`|i|≤Icap\`. Na granicy \`θ=80 K\` zastosowany \`Icap\` wyklucza dodatnią pochodną temperatury; przy \`θ=0\` pochodna jest nieujemna.

**Opóźnienie jednej próbki:** jeżeli jedyna dostępna obserwacja pochodzi z \`t(k-1)\`, zastosowano
\[
\overline E_{k,\mathrm{delay}}=
\overline E_{k-1}+\frac{u_{k-1}^2\Delta}{4R_{\min}}
\]
i tę obwiednię w tej samej regule. Wariant gwarantuje warunek **tylko** dla dokładnie znanego poprzedniego napięcia i czasu ZOH, bez większej latencji. Opóźniony estymator nie jest wyidealizowanym, pełnym obserwatorem nieznanego głośnika.

Dowód nie przechodzi na sprzęt, jeśli np. DAC/wzmacniacz przyłoży napięcie różne od komendy, \`Re<Rmin\`, parametry mechaniczne zmieniają się ze stanem, lub rzeczywisty \`BL\` jest niewzajemny. Czujniki x/v/i i ich błędy nie zostały zidentyfikowane w docelowym systemie.

## Kampania numeryczna

Przeprowadzono **288 trajektorii**: \`3 przetworniki × 2 cieplne × 2 skorelowane perturbacje × 2 sygnały × 3 częstotliwości sterownika × 4 strategie\`.

Sygnały: ośmiotonowy od 20 do 100 Hz o zgodnych fazach oraz 7/35 Hz z krótkim impulsem; software BW2 HP20 + LR4 LP80 przy częstotliwości integratora, 70 V RMS *przed filtrami* i szyny ±56,5685 V. Nie jest to normalizacja do jednakowej głośności. Sterowniki \`500/2000/6000 Hz\`, integrator RK4 \`24000 Hz\`, zero-order hold. Start \`x=v=i=0\`.

Strategie: \`ideal\` (dokładny stan i parametry, ten sam E★), \`naive\` (nominalna energia wyliczana z zaszumionego pomiaru), \`robust_now\` (górny estymator energii i Re_min), \`robust_delay\` (ten sam, lecz jedna próbka opóźnienia).

| Sterownik | Dokładny stan: max E/E★ | Naiwny: max E/E★ | Odporny bieżący | Odporny opóźniony |
|---:|---:|---:|---:|---:|
| 500 Hz | 0,990737 | **1,518564** | 0,965471 | 0,917550 |
| 2000 Hz | 0,999892 | **1,643903** | 0,993140 | 0,986146 |
| 6000 Hz | 0,999995 | **1,654971** | 0,996486 | 0,995782 |

Każda komórka to **maksimum spośród 24 prób**, nie wartość dla jednego modelu. Naiwny sterownik przekroczył \`E★\` w **72/72** próbach, odporne strategie w **0/144**. W żadnej z 288 prób nie stwierdzono przekroczenia osobnych \`Xref\` lub \`Icap\`. To rozróżnienie jest kluczowe: **naruszenie konserwatywnego E★ nie oznacza automatycznie uszkodzenia ani przekroczenia ruchu/prądu**.

![Porównanie granic energii dla P25E](../wyniki/103_P25E_odpornosc_obserwacji.svg)

## Koszt zachowawczości

Porównano *parami te same scenariusze* przy tej samej częstotliwości sterownika. Mediana stosunku RMS ruchu \`x\` do wariantu \`ideal\` wyniosła:

| Hz | Odporna bieżąca | Odporna z opóźnieniem |
|---:|---:|---:|
| 500 | 0,8235 | 0,7338 |
| 2000 | 0,8139 | 0,7948 |
| 6000 | 0,8133 | 0,8076 |

Są to **stosunki RMS przemieszczenia modelowej membrany**, a nie dB SPL, głośność muzyki lub sprawność rzeczywistego systemu. Mniejszy poziom ruchu może oznaczać nieakceptowalną ingerencję ochrony; badanie nie rozstrzyga kompromisu jakościowego.

## Zbieżność, kontrola energii i ograniczenia

Wszystkie 288 trajektorii przeliczono także dla \`48000 Hz\` (filtr cyfrowy projektowany oddzielnie dla nowego próbkowania). **Wszystkie klasyfikacje przekroczeń E★, Xref, Icap pozostały identyczne**. Maksymalna różnica \`max(E/E★)\` w parach kroków integracji wyniosła:
- stan dokładny: \`2,45×10⁻⁵\`;
- naiwny: \`7,16×10⁻⁵\`;
- odporny bieżący: \`1,53×10⁻⁴\`;
- odporny opóźniony: \`3,26×10⁻⁴\`.

Największa reszta zintegrowanego bilansu energii, normalizowana przez \`E★\`, wyniosła \`0,001095\` przy 24 kHz i \`0,0000643\` przy 48 kHz. To oszacowanie na *badanych siatkach*, nie globalny certyfikat błędu; niezależnej integracji DOP853 nie wykonano. Matematyczny dowód bezpieczeństwa warunkowego nie zależy od tej zbieżności.

**Bramki nadal otwarte:** niezależne, nie skorelowane perturbacje i parametry rzeczywistych egzemplarzy; identyfikacja Rth/BL/Le; błędy modelu zmienne w czasie i nieliniowości; dokładna latencja, jitter, rzeczywisty DAC, wzmacniacz klasy D i przepływ energii zwrotnej; możliwość uzyskania x/v/i lub obserwatora z zadaną granicą błędu; DSP o mniejszej utracie amplitudy; sprzężenie przestrzennego portu P21D z podatnymi ścianami P18E.

## Odtwarzalność

- [Kod](../skrypty/p25e_robustna_bariera.py) (NumPy, SciPy, Numba; bez danych handlowych i pomiarów).
- [Konfiguracja, w tym pełne nominalne T/S i granice błędów](../dane/konfiguracje/p25e_odpornosc_obserwacji.json).
- [Wszystkie 288 wierszy wyników](../wyniki/p25e_kampania.csv), [agregaty](../wyniki/p25e_podsumowanie.json).
- [Kontrola 48 kHz](../wyniki/p25e_zbieznosc_48000.json), [porównanie par i koszt](../wyniki/p25e_zbieznosc_porownanie.json).
- [Manifest SHA-256 dla programu, wejścia i wyników podstawowych](../wyniki/p25e_manifest.json).

Uruchomienie z katalogu repo:

\`\`\`bash
OPENBLAS_NUM_THREADS=1 python skrypty/p25e_robustna_bariera.py
OPENBLAS_NUM_THREADS=1 python skrypty/p25e_robustna_bariera.py --fs 48000
\`\`\`

Program tworzy odtwarzalne CSV i JSON; plik porównujący oba kroki można odtworzyć poprzez skojarzenie identycznych scenariuszy po kolumnach \`candidate, theta_init_k, uncertainty_sign, signal, mode, controller_hz\`.

**Wniosek:** w badanej klasie układów można sformułować rygorystyczny, lecz bardzo zachowawczy warunek ochrony mimo ograniczonych błędów obserwacji i parametrów. Nie wolno go mylić z zatwierdzeniem zabezpieczenia fizycznego subwoofera.
