# Filtr cyfrowy: poprawny wzór, dokładny zapis i zapas poziomu

P23A, 2026-10-27. Własne wyprowadzenia i eksperymenty software. Nie są
to pomiary procesora DSP ani kwalifikacja zabezpieczenia głośnika.

## Trzy odrębne źródła różnic

Projekt analogowy i cyfrowy różnią się przez przekształcenie częstotliwości.
Następnie zapis współczynników wprowadza własny błąd, nawet gdy obliczamy
filtr z bardzo dużą precyzją. Wreszcie skończona arytmetyka stanów może
zmienić przebieg czasowy. Każdy z tych etapów trzeba zbadać osobno.

Dokumentacja Flex Eight wymaga projektu dla 96 kHz. Nie wynika z tego
dowolność wyboru Fs ani precyzja wewnętrznych stanów IIR. Format single
pliku FIR opisuje konkretny plik, a nie wszystkie obliczenia urządzenia.
Źródła i zakres przyjętych faktów: [SRC58–61](../dane/zrodla/P23A_filtry_i_formaty.json).

## Transformacja i jej dziedzina

Przy konwencji mianownika `1+a1*z^-1+a2*z^-2`:

    s = 2*Fs*(1-z^-1)/(1+z^-1)
    Omega = 2*Fs*tan(omega/2)
    omega = 2*pi*f/Fs

Transformacja zachowuje ścisłą stabilność analogowego filtru o biegunach
w lewej półpłaszczyźnie w dokładnej arytmetyce. Nie daje liniowej osi
częstotliwości. Prewarp wybranej częstotliwości to osobna operacja;
SciPy `bilinear` nie wykonuje jej automatycznie. Nie można wyrównać każdej
częstotliwości całej odpowiedzi jednym skalarem prewarpu.

Transformacja Linkwitza skraca model obudowy drugiego rzędu przy Le=0.
Rzeczywisty przetwornik, wypełnienie i podatne panele nie muszą mieć tej
postaci. Prawidłowe współczynniki nie zapewniają dokładnego skrócenia
niezidentyfikowanej fizycznej charakterystyki.

## Dokładne kryterium zapisanych współczynników

Dla rzeczywistego monicznego `p(z)=z²+a1*z+a2`:

    |a2| < 1
    1+a1+a2 > 0
    1-a1+a2 > 0

To konieczne i wystarczające warunki położenia obu biegunów ściśle wewnątrz
koła jednostkowego. Wyprowadzenie: podstawienie `z=(1+s)/(1-s)` daje

    (1-s)²*p((1+s)/(1-s)) = A*s²+B*s+C
    A = 1-a1+a2
    B = 2*(1-a2)
    C = 1+a1+a2

Dodatnie A, B, C są kryterium Hurwitza drugiego rzędu. Równocześnie
`A+C=2*(1+a2)>0`. W kodzie nierówności badają dokładne ułamki z bitów
współczynników, a nie przybliżone pierwiastki numeryczne.

Dla analogowego mianownika `s²+b*s+c`, b,c>0, przy k=2Fs:

    d0 = k²+b*k+c
    1+a1+a2 = 4*c/d0
    1-a1+a2 = 4*k²/d0
    1-a2 = 2*b*k/d0
    1+a2 = 2*(k²+c)/d0

Widać dziedzinę oraz granice: c→0, b→0 i k→∞ zmniejszają wybrane
marginesy. Filtr bardzo niski w stosunku do Fs jest wrażliwy na zapis.
Większe Fs przy tej samej liczbie bitów nie musi pomóc. Stabilność
zapisanej kaskady nadal nie oznacza małego błędu amplitudy lub fazy.

Biegun na kole skasowany zerem może zniknąć z minimalnej transmitancji,
lecz pozostać w realizacji stanów. Nie należy utożsamiać tych dwóch
stwierdzeń. Ustalone warunki Jury nie są analizą nieliniowego zaokrąglania
stanów, cykli granicznych ani przepełnienia akumulatora.

## Dlaczego maksimum sinusa nie wystarcza

Dla stabilnego przyczynowego filtru, zerowych stanów początkowych i
ograniczonego wejścia `|x[n]|≤M`:

    y[n] = sum_k h[k]*x[n-k]
    |y[n]| <= M*sum_k |h[k]|

Norma od ograniczonego wejścia do ograniczonego wyjścia to suma wartości
bezwzględnych impulsu. Skończony świadek ją przybliża: wybieramy
`x[N-1-k]=sign(h[k])`, więc `y[N-1]=sum_{k<N}|h[k]|`.
Nie jest to model typowej muzyki, lecz poprawny kontrprzykład dla tezy,
że największe wzmocnienie sinusa chroni przed każdym sygnałem.

Dla sekcji z parą sprzężonych biegunów r*exp(±jθ), 0<r<1:

    h[k>=1] = r^(k-1)*(h1*cos((k-1)*theta)+d*sin((k-1)*theta))
    sum_{k>=N}|h[k]| <= hypot(h1,d)*r^(N-1)/(1-r)

W kaskadzie czterech sekcji obcinamy każdą do N0 próbek. Ich skończony
splot ma najwyżej 4*(N0-1)+1 próbek. Poza nimi pozostają tylko sploty
zawierające co najmniej jeden ogon. Sumowanie iloczynów norm tych składników
daje ograniczenie reszty całej kaskady. Własne liczby oceniono float;
bez zaokrągleń interwałowych nie jest to certyfikowany przedział.

Ten warunkowy zapas dotyczy wyjścia liniowego filtru. Potrzebna jest także
kontrola poziomu **wewnątrz** kaskady, przetworników ADC/DAC i wzmacniacza.
Nie jest to ogranicznik temperatury, wychylenia lub produktów IMD głośnika.

Wyniki i wykresy: [raport 046](../raporty/046_filtry_cyfrowe_stabilnosc_i_zapas.md).
