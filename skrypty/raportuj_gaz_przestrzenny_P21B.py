"""Raport P21B z ukończonych artefaktów;nie końcowyPDF całego projektu."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,json,re
import numpy as np

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def read(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))


def number(value,digits=6):return f'{float(value):.{digits}g}'.replace('.',',')


def main():
    status=json.loads((OUT/'p21b_podsumowanie.json').read_text());assert status['cases']==status['expected_cases']==18
    post=json.loads((OUT/'p21b_ocena_projektowa.json').read_text());assert post['numerical_flagged_rows']==0
    bound=json.loads((OUT/'p21b_granica_obciazenia_podsumowanie.json').read_text());checks=json.loads((OUT/'p21b_kontrole_niezalezne.json').read_text())
    asymptote=json.loads((OUT/'p21b_asymptotyka_podsumowanie.json').read_text())
    models=read('p21b_modele_i_geometria.csv');fields=read('p21b_pola_i_energia.csv');mesh=read('p21b_porownanie_siatek_w_pasmie.csv')
    force_budget=read('p21b_sily_przy_wymuszonym_gradiencie.csv')
    force_table='\n'.join('|'+str(v['outer_modal_pressure_rms_pa'])+' Pa|'+number(v['net_horizontal_force_peak_n'])+' N|'+number(v['minimum_quasistatic_normal_reaction_n'])+' N|'+('tak' if v['within_assumed_outer1pct_pressure_screen']=='True' else 'nie')+'|' for v in force_budget)
    reference='TIED_E1.718e+09_N12';r=next(v for v in models if v['case_id']==reference)
    examples=[]
    for f in [20.,80.]:
        for name in ['uniform','uniform_plus_x_gradient']:
            row=next(v for v in fields if v['case_id']==reference and float(v['f_hz'])==f and v['field']==name)
            mean=abs(complex(float(row['mean_inner_pressure_re_pa']),float(row['mean_inner_pressure_im_pa'])))
            examples.append('|'+('Równomierny' if name=='uniform' else 'Z gradientem')+f'|{f:g} Hz|{number(mean*1000)} mPa|{number(float(row["pressure_deviation_volume_rms_pa"])*1000)} mPa|')
    maxcore={key:max(float(v[key]) for v in read('p21b_porownanie_z0D.csv')) for key in ['energy_residual','mechanical_residual','acoustic_residual','momentum_residual','reciprocity_residual']}
    worst_mode=checks['rigid_eigenmodes'][-1]['max_relative_frequency_error']
    md=f'''# Raport 045 — P21B: przestrzenny gaz, praca granicy i granica0D

Stan: {datetime.now(ZoneInfo('Europe/Warsaw')).date().isoformat()}. **Obliczenia i symulacje do budowy**, bez pomiarów urządzenia.
Zbadano szczelny moduł regulacji objętości z [P20C](044_modul_3D_dwa_porty_i_wymagania_kleju.md).
To etap przejścia do głównej komory, nie zamknięcie całego programu subwoofera.

## Co wynika dla projektu

**Obliczenie:** w sprawdzonych sześciu częstotliwościach20–80Hz największa
zmiana objętościowej admitancji modułu względem jednolitego gazu0D wyniosła
**{number(100*post['max_uniform_admittance_change_at_probes'])}%**.
Dotyczy18rodzin przy jednorodnym nacisku na moduł, założonych materiałach,
bez strat gazu i bez reakcji zewnętrznego pola głównej komory.
Nie jest zmianą SPL, THD lub wynikiem w pokoju.

Przy zadanym niejednorodnym polu zewnętrznym średnia ciśnienia nie opisuje
całego wnętrza. Gaz ma także bezwładność i przenosi pęd. Dlatego zgodność
samej średniej lub samej zmiany objętości nie wystarcza do oceny lokalnych
obciążeń i mocowania. Ruch całej bryły pozostał w równaniach.

**Rekomendacja warunkowa:** zachować prosty port0D jako odniesienie
objętościowe małego modułu przy prawie równomiernym nacisku w badanym
paśmie; do głównej komory przejść z pełną definicją pracy i niejednorodności.
Nie przenosić tej małej korekty na całą skrzynię bez badania jej geometrii.

## Wykonany zakres

| Rodzina | Zakres |
|---|---:|
| Siatki4/8/12 × bez/ześciągiem × trzy E kleju |18przypadków|
| Pełne układy częstotliwościowe |132|
| Równomierne pole i pole z gradientem |264wiersze pól|
| Macierze dwóch portów |528zespolonych wpisów|
| Mody gazu przy sztywnych granicach |6geometrii ×12modów|
| Pojedynczy element:niezależny Kronecker |3geometrie|
| Pusta komora:3siatki i wymuszony tłok1D |12wymuszeń, także przy zerze ciśnienia wejściowego|
| Pełny blok i wydzielona średnia ciśnienia |4porównania stanów|
| Formalna redukcja bezwładności gazu do0D |12realizacji|
| Granica skalarnego obciążenia po Ca i N |108punktów częstotliwościowych z analityczną monotonicznością|

Największa podstawowa liczba niewiadomych wynosi
{max(int(v['total_unknowns']) for v in models)}. Szczyt zapisanej pamięci procesu
wyniósł około{number(max(float(v['peak_rss_mib']) for v in models),5)}MiB.
Wszystkie skonfigurowane punkty zachowały jawne ekrany numeryczne.
Nie oznacza to certyfikatu kontinuum lub potwierdzenia danych fizycznej sztuki.

## Geometria i materiały

Moduł ma obrys180×100×170mm, ściany8mm, rzeczywiste warstwy kleju0,2mm
oraz wariant z nakładkami i prętem. Założenia MDF:E=2,1GPa,nu=0,3,
rho=730kg/m³; klej:E=10/100/1718MPa,nu=0,35,rho=1200kg/m³.
To rodziny porównawcze, nie tolerancje producenta lub wybór produktu.

Referencja n12ześciągiem ma {number(float(r['gas_volume_l']))}l gazu,
{number(float(r['dry_solid_mass_kg']))}kg suchego materiału i
{number(float(r['gas_mass_kg'])*1000)}g gazu przy warunkach Medium.
Gazu nie dopisano drugi raz do masy konstrukcji. To mały element regulatora;
nie są to wymiary głównej obudowy widocznej na banerze repozytorium.

Gaz jest idealizowany, adiabatyczny, bezstratny i bez przecieku. Przyjęto
gamma1,4,p0=101325Pa,T=293,15K. Brak warstw lepko-cieplnych ogranicza
interpretację szczytów wyższych rezonansów. Zewnętrzny nacisk jest zadany,
nie rozwiązano jeszcze pola między modułami i ściankami głównej skrzyni.

## Metoda i niezależne odniesienia

WłasneQ1/H8 dla gazu na dokładnym dopełnieniu bryłyP20C; powierzchnie
materiał/gaz są zgodne. B przenosi ciśnienia na siły i przyspieszenia na gaz:

    Ds*u-B*p=Hext*po
    (A+s²*C)*p=-s²*B.T*u

Sprawdzono B*1=Hi,A*1=0 oraz sumę C równą Vgas/Kbulk. Objętościowe całki
gradientu i r×gradientu są niezależnym sprawdzeniem pracy na granicy
i całkowitego pędu. Do energii sprężystej odjęto tylko numeryczny ruch
sztywny; pełne u pozostaje w masie i warunku gaz/ciało.

Moc wejściowa odpowiada omega²*U*Cs*U. Gaz bez strat ma średnią moc0,
ale przechowuje energię sprężania i ruchu. Fazory są RMS; czynnik1/2
dotyczy średniej energii, nie średniej mocy strat. Wzajemność macierzy
i dodatniość mocy sprawdzono oddzielnie.

Pusty prostopadłościan ma rozwiązanie analityczne. Dla pierwszych12modów
na najgęstszej siatce największa względna różnica wynosi około
**{number(100*worst_mode)}%**. Osobny zadany tłok odtwarza falę1D,
również w punkcie, gdzie ciśnienie na wejściu jest zerowe. Błąd w tym
punkcie oceniano bez dzielenia przez znikające ciśnienie odniesienia.

## Średnia i lokalne ciśnienia

Zewnętrzne pola w lokalnym układzie modułu mają kształt:

    Phi0=1
    Phi1=1+(x-W/2)/W

Amplituda modalna każdego osobnego wymuszenia wynosi1PaRMS. Drugi
profil ma wartości od0,5do1,5razy tej amplitudy; to scenariusz z gradientem,
nie pomiar ani prognoza konkretnego pola w pokoju.

| Pole | Częstotliwość | Amplituda średniej wewnętrznej | Przestrzenny RMS różnic |
|---|---:|---:|---:|
'''+ '\n'.join(examples)+f'''

Duży procent różnic względem małej średniej nie jest dużym ciśnieniem
bezwzględnym. Podano obie wielkości. To zróżnicowanie przestrzenne
w liniowym modelu, nie nowe harmoniczne lub THD.
Port z gradientem opisuje pracę także na ruchu całej bryły: jego
uogólniony przepływ nie jest samą pochodną objętości obrysu.

![0D i3D oraz skala lokalnych różnic](../wyniki/81_P21B_0D_3D_i_zroznicowanie_cisnienia.png)

![Pole ciśnienia w rzeczywistej geometrii gazu modułu](../wyniki/82_P21B_pole_cisnienia_w_module.png)

## Siatki, punkty diagnostyczne i granica0D

Przy wspólnych Hz w20–80Hz największa zmiana admitancji n8→12 wynosi
{number(100*post['max_uniform_admittance_mesh_change_at_probes'])}%.
Zmiany pola ciśnienia i jego odchylenia zapisano osobno, także w Pa na1Pa
wymuszenia. Zgodna pojedyncza liczba nie dowodzi zbieżności każdego punktu.

Przy dodatkowych częstotliwościach500–2200Hz największa znaleziona zmiana
względem0D wynosi {number(100*post['max_uniform_admittance_change_at_diagnostics'])}%.
Nie jest to maksimum ciągłego pasma lub fizyczny szczyt rezonansu.
Nie rozciągamy interpretacji bezstratnego gazu na rzeczywiste tłumienie.

Formalne zwiększanie A przy stałym C oznacza pomijalną bezwładność gazu.
Wydzielenie stałego modu ciśnienia zapobiega mnożeniu prawie stałego p
przez wielkieA. Cztery porównania z pełnym blokiem przy skali1 potwierdzają
zgodność obu zapisów. Skalowanie nie jest ogrzewaniem powietrza.

**Osobna granica niskiej częstotliwości:** przy swobodnej bryle z niezerową
wypadkową siłą z gradientu ruch rośnie jak1/omega². Gaz przyspiesza wraz
z bryłą, a jego gradient ciśnienia nie musi zaniknąć tylko przez obniżenie
częstotliwości. Wiodący wyraz wynosi:

    std(p)/Pmodal -> rho*abs(F_per_Pa)*sigma_x/(mdry+mgas)

Względny błąd pełnej macierzy portów skalarnego odniesienia0D z masą
samego materiału zmierza wtedy do udziału masy gazu mgas/(mdry+mgas).
Nie dotyczy to każdego modelu0D:spójną masę dodaną można uwzględnić
w modelu zredukowanym. Nie dopisuje się jej drugi raz do pełnego gazu3D.
To inne pytanie niż mała zmiana portu objętościowego
przy równomiernym nacisku. Porównano tę niezależną asymptotykę z36próbkami
20/80Hz. Największe odstępstwa przy20Hz wynoszą
{number(100*asymptote['max_std_departure_at20hz'])}%dla zróżnicowania ciśnienia
i{number(100*asymptote['max_matrix_departure_at20hz'])}%dla błędu macierzy.
To porównanie skończonejf z granicą,nie żądanie ich dokładnej równości.
Przy stałej amplitudzie graniczny ruch stałby się duży; fizyczna mała
amplituda wymaga skalowania wymuszenia zomega² albo uwzględnienia podpór.

![Wzorce analityczne i formalne przejście do0D](../wyniki/83_P21B_wzorce_i_granica0D.png)

## Wpływ na skalarne obciążenie głównej komory

Dla identycznych modułów przy równomiernym p, Ca≥Ca_min i N≤16,
przy nieujemnych ReY oraz ImY w badanychf, najgorszą zmianę stosunku
impedancji otrzymujemy przy Ca_min oraz N=16. Uzasadniono monotoniczność
analitycznie, a punkty sprawdzono niezależnymi podstawieniami.

Minimum gazu przyjęto z istniejącej kontrolnej geometrii:około
{number(bound['minimum_active_air_l'])}l, z umownym wyporem głośnika6l.
Wszystkie Ca powyżej tego minimum i Nod0do16 obejmuje warunkowy rachunek
w sześciu zapisanych częstotliwościach. Największa granica względnej
zmiany skalarnej impedancji wynosi około
**{number(bound['maximum_relative_impedance_change'])}**.

To nie dowód przewagi produktu, zmiany SPL w pokoju lub dominacji całego
briefu. Niejednorodny nacisk, wzajemne pole i rzeczywiste mocowanie modułów
pozostają osobnym zadaniem; nie wolno zastąpić ich tą granicą skalarną.

## Ograniczenia i następny krok

**Mocowanie jest odrębnym warunkiem.** Pole z gradientem daje wypadkową
siłę, mimo małej korekty odpowiedzi objętościowej. Dla narzuconego profilu
Phi1 współczynnik poziomej siły wynosi
{number(abs(bound['prescribed_gradient_force_per_modal_pa_n'][0]))}N na1Pa amplitudyRMS.
To wynik całki po zamkniętej powierzchni,nie prognoza gradientu rzeczywistej skrzyni.

Dla modułu utrzymywanego nieruchomo na czterech punktach,przy rozstawie
z konfiguracjiP20A,ciężarze i wyporze w powietrzu,jedynie ściskających
kontaktach oraz bez kotew otrzymujemy następujący budżet quasistatyczny:

| Amplituda pola | Szczyt siły poziomej | Najmniejsza reakcja normalna | W ekranie1%ciśnienia zewnętrznego |
|---:|---:|---:|---|
{force_table}

Ujemna reakcja w tym schemacie oznacza,że założony nieruchomy układ bez
przenoszenia rozciągania nie zachowa czterech kontaktów przy takiej obwiedni.
Nie jest to obliczenie rzeczywistej odpowiedzi harmonicznej:mocowania mogą
mieć rezonans,poślizg,ruch i zmianę rozkładu reakcji. Przykład pokazuje,
dlaczego samego ciężaru lub samej zgodności litrów nie uznajemy za
kwalifikację mocowania. Potrzebne jest pole i dynamika głównej komory.

Największe zapisane reszty w całej rodzinie, w użytych normalizacjach:

| Kontrola | Wartość |
|---|---:|
| Mocy |{number(maxcore['energy_residual'])}|
| Równania konstrukcji |{number(maxcore['mechanical_residual'])}|
| Równania gazu |{number(maxcore['acoustic_residual'])}|
| Pędu całkowitego |{number(maxcore['momentum_residual'])}|
| Wzajemności |{number(maxcore['reciprocity_residual'])}|

To dokładność rozwiązywania i weryfikacji zadanych modeli. Nie zastępuje
danych o kleju,MDF,pełzaniu,S–N,Gc,rzeczywistych stratach lub pomiarów.
Nie wyznaczono własnego THD produktu, bezpiecznej mocy lub końcowego
SPLw pokoju. Referencje i numeryczne progi odbiorowe pozostają odrębne.

**Jeden następny krok:P21C — główna komora z regulacją,wypełnieniem
i mocowaniem modułów.** Uwzględnić rzeczywiste niejednorodne pole
i porównanie sensownych proporcji przy wspólnym netto oraz wymaganym
zakresie regulacji. Obrys504×684×504mm pozostaje wariantem odniesienia,
nie wynikiem ukończonej optymalizacji. Dwie sztuki muszą być wykonalne
w pokoju4,6×3,7×2,5m,RTVpo lewej/kanapa po prawej rzutu.

Opisy opinii z forów użytkownik odłożył do końcowej syntezy. Tutaj
nie rozszerzano ich ani nie przypisano im nowych ocen produktów.
KońcowyPDF iRelease1 powstaną po całym programie,nie po samymP21B.

## Pliki i odtwarzanie

- [Wejścia](../dane/konfiguracje/p21b_gaz_przestrzenny_modulu.json).
- [Pierwotne źródła metody](../dane/zrodla/P21B_sprzezenie_i_postac_slaba.json).
- [Pola i energie](../wyniki/p21b_pola_i_energia.csv).
- [Macierze portów](../wyniki/p21b_macierze_admitancji.csv).
- [Kontrole niezależne](../wyniki/p21b_kontrole_niezalezne.json).
- [Granica obciążenia](../wyniki/p21b_granica_skalarnego_obciazenia.csv).
- [Warunkowy budżet sił gradientu](../wyniki/p21b_sily_przy_wymuszonym_gradiencie.csv).
- [Asymptotyka swobodnego ruchu](../wyniki/p21b_asymptotyka_swobodnego_ruchu.csv).
- [Manifest](../wyniki/manifest_gazu_przestrzennego_P21B.json).

    OPENBLAS_NUM_THREADS=1 python3 skrypty/odtworz_gaz_przestrzenny_P21B.py

Zgodne18rekordów wznawia się po hashu wejść. Ich odczyt nie jest świeżą
niezależną replikacją. Pełny przebieg archiwizujący jest blokowany,
jeśli inny proces rzeczywiście utrzymuje blokadę aktywnegoP21B.
'''
    md=md.replace('Nod0do16','N od 0 do 16').replace('SPLw','SPL w')
    lines=[]
    for line in md.splitlines():
        if not line.startswith('    ') and '](' not in line:
            line=re.sub(r'(?<=[a-ząćęłńóśźż]{2})(?=\d)',' ',line)
            line=re.sub(r'(\d)(?=[a-df-ząćęłńóśźż])',r'\1 ',line)
            line=re.sub(r'(\d)(Hz|MPa|GPa|Pa|MiB|kg|mm|RMS)(?=\b|[/,.;]|[a-z])',r'\1 \2',line)
            line=re.sub(r',(?=[a-zA-Ząćęłńóśźż])',', ',line)
            line=re.sub(r'(?<!\d),(?=\d)',', ',line)
        lines.append(line)
    p=ROOT/'raporty/045_gaz_przestrzenny_praca_i_granica0D.md';p.write_text('\n'.join(lines)+'\n')
    print('Raport045 generated from completed P21B datasets.')


if __name__=='__main__':main()
