"""P23A:własne wykresy i jawne wnioski z ukończonego eksperymentu."""
from pathlib import Path
import csv,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
import numpy as np
from model_filtrow_dyskretnych_P23 import chain,represent,frequency_response

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))


def num(x,d=5):return f'{float(x):.{d}g}'.replace('.',',')


def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=170);fig.savefig(OUT/(name+'.svg'));plt.close(fig)


def main():
    j=json.loads((OUT/'p23a_podsumowanie.json').read_text());assert j['quantized_chains']==4860
    checks=json.loads((OUT/'p23a_kontrole_niezalezne.json').read_text())
    order=json.loads((OUT/'p23a_kolejnosc_podsumowanie.json').read_text())
    rows=read('p23a_kaskady_i_kwantyzacja.csv');warp=read('p23a_blad_transformacji_vs_analog.csv')
    stress=read('p23a_granice_rozdzielczosci.csv');time=read('p23a_czas_i_arytmetyka.csv')
    fslist=[48000,96000,192000];reps=['float32','decimal6','decimal9'];col=['#007c91','#cb4b16','#6c4797']
    fig,ax=plt.subplots(1,2,figsize=(12,5.1),constrained_layout=True)
    values=[max(float(r['max_abs_gain_error_db']) for r in warp if int(r['sample_rate_hz'])==fs) for fs in fslist]
    ax[0].bar([str(fs//1000) for fs in fslist],values,color='#007c91')
    ax[0].set(title='Sam zapis cyfrowy float64 vs wzorzec analogowy',xlabel='Fs scenariusza [kHz]',ylabel='Największy znaleziony błąd amplitudy [dB]')
    ax[0].ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax[0].grid(axis='y',alpha=.25)
    for k,rep in enumerate(reps):
        vals=[max(float(r['max_abs_gain_error_db']) for r in rows if r['representation']==rep and int(r['sample_rate_hz'])==fs) for fs in fslist]
        ax[1].bar(np.arange(3)+(k-1)*.25,vals,width=.24,label={'float32':'Współczynniki float32','decimal6':'6 miejsc po kropce','decimal9':'9 miejsc po kropce'}[rep],color=col[k])
    ax[1].set(xticks=np.arange(3),xticklabels=[str(fs//1000) for fs in fslist],yscale='log',
        xlabel='Fs scenariusza [kHz]',ylabel='Największy znaleziony błąd [dB]',title='Sam zapis współczynników vs float64')
    ax[1].legend(fontsize=9);ax[1].grid(axis='y',alpha=.25)
    fig.suptitle('27 konfiguracji × 4 objętości × 3 cele LT; siatka 20–80 Hz\nModel software; nie pomiar miniDSP lub THD głośników',fontsize=12)
    save(fig,'84_P23A_transformacja_i_zapis_wspolczynnikow')
    fig,axes=plt.subplots(1,3,figsize=(13,7.2),constrained_layout=True)
    cmap=ListedColormap(['#d4e9dd','#f7d988','#d26a5c']);norm=BoundaryNorm([-.5,.5,1.5,2.5],3)
    qs=[.5,1/np.sqrt(2),2.,10.];cutoffs=[.5,2.,5.,18.,80.]
    labels=[f'{fs//1000}k / Q={q:.3g}' for fs in fslist for q in qs]
    for axis,rep in zip(axes,reps):
        matrix=np.zeros((12,5),int)
        for r in stress:
            if r['representation']!=rep:continue
            i=fslist.index(int(r['sample_rate_hz']))*4+min(range(4),key=lambda k:abs(qs[k]-float(r['q'])))
            k=cutoffs.index(float(r['cutoff_hz']));matrix[i,k]={'strict':0,'boundary':1,'outside':2}[r['jury_state']]
        axis.imshow(matrix,aspect='auto',cmap=cmap,norm=norm)
        axis.set(xticks=np.arange(5),xticklabels=['0,5','2','5','18','80'],yticks=np.arange(12),yticklabels=labels,
            xlabel='Zadany cutoff analogowy [Hz]',title={'float32':'Współczynniki float32','decimal6':'6 miejsc po kropce','decimal9':'9 miejsc po kropce'}[rep])
        for i in range(12):
            for k in range(5):axis.text(k,i,['S','G','P'][matrix[i,k]],ha='center',va='center',fontsize=9)
    fig.suptitle('Dokładne nierówności Jury dla ZAPISANYCH współczynników HP2\nS: ściśle stabilne · G: granica · P: poza obszarem; nie diagnoza konkretnego sprzętu',fontsize=12)
    save(fig,'85_P23A_dokladna_stabilnosc_i_granice')
    cfg=json.loads((ROOT/'dane/konfiguracje/p23a_filtry_dyskretne.json').read_text());case=cfg['software_time_case']
    fig,ax=plt.subplots(1,2,figsize=(12,5.2),constrained_layout=True)
    for fs in fslist:
        r=next(x for x in time if int(x['sample_rate_hz'])==fs and x['signal']=='four_tone')
        ax[0].plot([fs/1000],[100*float(r['coefficient_only_error_rms_relative'])],'o',color='#cb4b16')
        ax[0].plot([fs/1000],[100*float(r['state_arithmetic_error_rms_relative'])],'s',color='#007c91')
    ax[0].plot([],[],'o',color='#cb4b16',label='Tylko zapis współczynników float32')
    ax[0].plot([],[],'s',color='#007c91',label='Arytmetyka SOS float32 przy tych samych wejściach')
    ax[0].set(xlabel='Fs scenariusza [kHz]',ylabel='RMS błędu / RMS odniesienia [%]',
        title='C04 / 100 l / LT25 / HP18 / LR4 80; cztery tony',xticks=[48,96,192])
    ax[0].legend(fontsize=8);ax[0].grid(alpha=.25)
    h=j['headroom_bounds'][1];sine=20*np.log10(h['sine_grid_peak_gain']);witness=20*np.log10(h['finite_cascade_l1_lower_float']);upper=h['cascade_l1_sufficient_attenuation_db_float']
    ax[1].bar(['Największy znaleziony\nsinus','Skonstruowany\nsygnał ograniczony','Ograniczenie l1\nz ogonem'],[sine,witness,upper],color=['#007c91','#cb4b16','#6c4797'])
    ax[1].set(ylabel='Wzmocnienie szczytu względem wejścia [dB]',title='Ten sam filtr / 96 kHz; różne kryteria zapasu')
    for k,v in enumerate([sine,witness,upper]):ax[1].text(k,v+.12,f'{v:.3f} dB',ha='center')
    ax[1].set_ylim(0,9);ax[1].grid(axis='y',alpha=.25)
    fig.suptitle('Oddzielne błędy software i zapas dla sygnałów w czasie\n4 s / stany początkowe zero; ogon l1 oceniony float, bez certyfikatu interwałowego',fontsize=12)
    save(fig,'86_P23A_arytmetyka_i_zapas_sygnalu')
    maxima={}
    for rep in cfg['representations']:
        selected=[r for r in rows if r['representation']==rep]
        maxima[rep]={key:max(float(r[key]) for r in selected) for key in ['max_abs_gain_error_db','max_abs_phase_error_deg','max_abs_group_delay_error_ms']}
    table='\n'.join(f'|{rep}|{num(v["max_abs_gain_error_db"])} dB|{num(v["max_abs_phase_error_deg"])}°|{num(v["max_abs_group_delay_error_ms"])} ms|' for rep,v in maxima.items())
    md=f'''# Raport 046 — P23A: cyfrowa korekcja, stabilność i zapas sygnału

Stan: 2026-10-27. **Obliczenia i symulacje software przed budową.**
P21B liczy się osobno; numer045 zarezerwowano dla jego raportu.
Nie jest to pomiar miniDSP ani gotowy preset do urządzenia.

## Wniosek przydatny przy budowie

**Rekomendacja:** współczynniki trzeba projektować dla właściwego Fs,
zapisywać z wystarczającą precyzją i sprawdzać po ponownym odczycie.
Sama stabilność nie wystarcza do zachowania właściwej charakterystyki.
Nie należy traktować największego wzmocnienia sinusa jako pełnej ochrony
przed przesterowaniem przez dowolny sygnał ograniczony w amplitudzie.

**Symulacja:** w zbadanej siatce20–80Hz największa różnica między
realizacją float64 a analogowym wzorcem to {num(j['max_warp_gain_error_db'])}dB.
Zaokrąglenie samych współczynników do float32 dało do
{num(maxima['float32']['max_abs_gain_error_db'])}dB, a do sześciu miejsc
po kropce — {num(maxima['decimal6']['max_abs_gain_error_db'])}dB.
Ta ostatnia duża wartość obejmuje silnie zmienione zera charakterystyki.
Nie jest THD,różnicą SPL w pokoju lub wynikiem konkretnego procesora.

![Cyfrowy projekt i osobny błąd zapisu](../wyniki/84_P23A_transformacja_i_zapis_wspolczynnikow.png)

## Pula i wykonany zakres

27konfiguracji elektrycznych /26produktów, w tym STX i nowe SB Acoustics.
Wspólne założenia:30/60/100/150l netto powietrza,LT20/25/30Hz z Q=1/√2,
HP drugiego rzędu18Hz i LP Linkwitz–Riley czwartego rzędu80Hz.
Fs48/96/192kHz są scenariuszami programu. Dokumentacja Flex Eight
potwierdza96kHz,nie przełączanie tego urządzenia na wszystkie trzy Fs.

Wykonano972projekty,4860reprezentacji kaskad,19440rekordów sekcji,
300granicznych filtrów HP,9przebiegów czasowych i9przypadków niezgodnego Fs.
Każda kaskada ma4sekcje:LT,HP2 i dwa LP2. Nie zrównujemy tych obliczeń
z identyfikacją przetwornika lub kwalifikacją czasu pracy.

Wejścia i ograniczenia są w [konfiguracji](../dane/konfiguracje/p23a_filtry_dyskretne.json),
pełne wyniki w [podsumowaniu](../wyniki/p23a_podsumowanie.json).
Rekordy zawierają nazwy modeli i połączeń,nie tylko identyfikator scenariusza.

## Model i interpretacja korekcji

Model drugiego rzędu ma Le=0,stałe T/S,sztywne ściany i gaz0D:

    Hbox(s) = s²/(s²+s*wc/Qc+wc²)
    HLT(s) = (s²+s*wc/Qc+wc²)/(s²+s*wt/Qt+wt²)
    Hbox*HLT = s²/(s²+s*wt/Qt+wt²)
    s = 2*Fs*(1-z^-1)/(1+z^-1)

Ostatnią transformację zastosowano bez prewarpu we wspólnym porównaniu.
Analogowy głośnik pozostaje układem ciągłym;cyfrowa LT nie usuwa dokładnie
każdego rzeczywistego bieguna produktu. Indukcyjność,termika,pamięć,
przecieki,panele i wypełnienie zaburzają idealne skracanie.
Wpływ samego przekształcenia w tym paśmie jest mały,lecz to nie usuwa tych
braków modelu. Odrębny test HP z jawnym prewarpem zgadza się z pierwotnym
wzorem W3C i SciPy w12punktach.

Obliczono błąd amplitudy,argumentu ilorazu i analitycznie wyznaczonego
opóźnienia grupowego. To opóźnienie samej kaskady;nie obejmuje ADC,DAC,
buforów,całkowitej latencji DSP lub wyrównania monitorów.

| Zapis | Max błąd amplitudy | Max błąd fazy | Max błąd opóźnienia grupowego |
|---|---:|---:|---:|
{table}

To maksima znalezione w określonej skończonej siatce,nie dowód globalnego
ekstremum ciągłego pasma. decimal6/9/17 oznacza liczbę miejsc po kropce.
17miejsc po kropce nie jest tą samą regułą co17cyfr znaczących lub
gwarancja dokładnego odtworzenia każdego float64.

## Stabilność i przypadki graniczne

Własna konwencja zgadza się z SciPy:

    H(z)=(b0+b1*z^-1+b2*z^-2)/(1+a1*z^-1+a2*z^-2)
    |a2|<1, 1+a1+a2>0, 1-a1+a2>0

Warunki obliczono jako **dokładne ułamki zapisanych współczynników**.
Nie oparto decyzji wyłącznie na zaokrąglonych pierwiastkach wielomianu.
Wyprowadzenie Cayleya i dodatnie współczynniki Hurwitza zapisano w
[kontrolach](../wyniki/p23a_kontrole_niezalezne.json).
Wszystkie4860głównych kaskad są ściśle stabilne w tej definicji,mimo że
część ma bardzo duży błąd charakterystyki.

W 300odrębnych filtrach kontrolnych cutoff0,5/2/5/18/80Hz i Q=0,5/0,707/2/10:
float32 daje12przypadków na granicy i6poza obszarem,sześć miejsc17na
granicy i4poza,dziewięć miejsc1poza. float64 i decimal17 nie dały takich
przypadków w tej siatce. **To granice hipotetycznej reprezentacji**,
nie zarzut wobec arytmetyki miniDSP,której tu nie zidentyfikowano.

![Dokładna stabilność dla zapisanych współczynników](../wyniki/85_P23A_dokladna_stabilnosc_i_granice.png)

Przy cutoff→0 lub Q→∞ margines dąży do0. Przy Fs→∞,gdy zachowujemy
fizyczną częstotliwość filtru,bieguny dążą do z=1;stały krok kwantyzacji
staje się wtedy problemem. Zwiększenie Fs nie oznacza automatycznie
lepszej dokładności niskiego filtru o tej samej precyzji współczynników.

Przykład bieguna z=1 skasowanego zerem pokazuje różnicę między stabilną
minimalną transmitancją a marginalnym stanem niewidocznym na wyjściu.
Nie deklarujemy stabilności każdej implementacji przez samo skasowanie.

## Sygnał w czasie i zapas poziomu

9przebiegów po4s:cztery tony20/31,5/63/80Hz o zadanych fazach,skok0,1
od stanu zerowego i impuls jednostkowy. Referencja C04/100l/LT25/HP18/LR4 80
jest kontrolą,nie wyborem docelowego głośnika. Odróżniono:

- współczynniki float32 przy arytmetyce float64,
- SciPy SOS float32 i float64 z **tymi samymi** współczynnikami i wejściem.

Porównanie pokazuje osobny wpływ stanów i obliczeń. Różnic nie nazywamy
szumem lub zniekształceniami konkretnego hardware. Skończony przebieg nie
dowodzi braku cykli granicznych,przepełnienia lub problemów przy zmianie
nastaw w locie.

**Obliczenie:** dla stabilnego liniowego filtru i |x[n]|≤1 zachodzi
|y[n]|≤Σ|h[k]|. To inna norma niż największa amplituda sinusa.
Dla referencji96kHz największy znaleziony sinus ma wzmocnienie
{num(sine)}dB,zaś skonstruowany ograniczony sygnał daje {num(witness)}dB.
Suma bezwzględnych wartości impulsu do1s wynosi {num(h['finite_cascade_l1_lower_float'],9)}.
Oszacowanie reszty z obciętych splotów daje ogon≤
{num(h['truncated_convolution_cascade_tail_upper_float'])};liczby oceniono
zmiennoprzecinkowo,bez certyfikowanego zaokrąglania na zewnątrz.

Przy tych założeniach potrzebny zapas dla dowolnego ograniczonego wejścia
wynosi około{num(upper)}dB. Skonstruowany sygnał nie jest reprezentatywną
muzyką. To świadek obalający utożsamienie sinusowego maksimum z pełnym
zapasem. Osobny,luźniejszy iloczyn norm sekcji pozostawiono w danych.
Wartość7,44dB dotyczy wyjścia całego liniowego filtru.

Zbadano też12różnych kolejności tych samych sekcji,48wyjść pośrednich.
Przy założeniu identycznego limitu każdego wyjścia,najmniejsze znalezione
ograniczenie maksymalnej normy pośredniej to
{num(order['best_example']['order_max_intermediate_gain_bound'])}
dla {order['best_example']['order']};największe to
{num(order['worst_example']['order_max_intermediate_gain_bound'])}
dla {order['worst_example']['order']}.
Pełna transmitancja pozostaje ta sama,lecz porty pośrednie mogą potrzebować
innego zapasu. Nie obejmuje to wewnętrznych stanów DF2T lub nieznanego
skalowania rzeczywistego procesora. Nie jest zaleceniem zmiany jego topologii.
Szczegóły: [kolejność i poziomy](../wyniki/p23a_kolejnosc_i_poziomy_posrednie.csv).

![Błędy arytmetyki i inny zapas dla sygnału czasowego](../wyniki/86_P23A_arytmetyka_i_zapas_sygnalu.png)

## Źródła,znaki i granice wdrożenia

[SRC58–61](../dane/zrodla/P23A_filtry_i_formaty.json):oryginalny HPF W3C
obejrzano w browser-harness,nagrywanie wyłączone. Oficjalna dokumentacja
miniDSP potwierdza96kHz oraz przykładowy plik biquad. Dodatnie sprzężenie
w tym przykładzie wymaga zmiany znaków względem naszej konwencji.
To interpretacja sprawdzona algebraicznie:bez zmiany znaków przykład
traci ścisłą stabilność. Nie zastępuje sprawdzenia importu w urządzeniu.
Własny serializer odtwarza współczynniki dokładnie,lecz nie wgrano nic do DSP.

Dokumentacja FIR wymaga pliku IEEE754single,co **nie określa** formatu
stanów IIR,akumulatora,FMA,skalowania lub wewnętrznego zapasu poziomu.
SciPy online opisuje1.18.0,użyty pakiet to1.17.1;wzór sprawdzono osobno.
Niepewnych cech sprzętu nie uzupełniono domysłem.

## Odtwarzanie i dalszy krok

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_filtry_P23A.py

Odrębne kontrole:9tożsamości/granic,45porównań transmitancji z80cyframi,
45pochodnych fazy,12kontroli współczynników,3przebiegi DF1 vs DF2T,
4dokładne przypadki znaków/granic i3dodatkowe sprawdzenia największych
błędów kwantyzacji z80cyframi.

**Następny krok DSP:** P23B/P24 — skorygowany fizyczny układ
elektroakustyczny,stany przejściowe i dynamiczna ochrona V/I/X/T,z uwzględnieniem
sygnałów P25. Filtr HP na wejściu nie usuwa produktów IMD powstających
później w głośniku. Równolegle pozostaje P21C:główna komora,regulacja,
położenie wypełnienia,mocowanie i dobór proporcji. Pojedynczy wybór,
końcowy PDF i Release1 czekają na syntezę całego programu.
'''
    # Proste odstępy w nowej prozie;bez ingerencji w kod,adresy i dane surowe.
    import re
    md='\n'.join(re.sub(r'(?<=[a-ząćęłńóśźż])(?=\d)|(?<=\d)(?=[a-ząćęłńóśźż])',' ',line)
        if not line.startswith(('    ','|')) and '](' not in line and '://' not in line else line for line in md.splitlines())+'\n'
    md=md.replace('float 32','float32').replace('float 64','float64').replace('decimal 6','decimal6').replace('decimal 17','decimal17')
    lines=[]
    for line in md.splitlines():
        if not line.startswith(('    ','|')) and '](' not in line and '://' not in line:
            line=re.sub(r',(?!\d)(?=\S)',', ',line)
            line=re.sub(r'([;:])(?=[^\s*])',r'\1 ',line)
            line=re.sub(r'(\d)(k?Hz|dB|ms)\b',r'\1 \2',line)
            line=re.sub(r'(?<=\d) e([+-]\d)',r'e\1',line)
        lines.append(line)
    md='\n'.join(lines)+'\n'
    (ROOT/'raporty/046_filtry_cyfrowe_stabilnosc_i_zapas.md').write_text(md)
    print('P23A:report046,figures84–86;software only;next protection/main chamber.')


if __name__=='__main__':main()
