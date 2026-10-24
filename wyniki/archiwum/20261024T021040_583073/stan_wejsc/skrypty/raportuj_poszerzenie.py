"""Raporty cząstkowe z faktycznie wykonanych kampanii; bez końcowego PDF."""
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load_csv(name):
    return list(csv.DictReader((ROOT/'wyniki'/name).open()))


def readable(text):
    """Odstępy w opisie, z zachowaniem kodu, linków i oznaczeń modeli."""
    token=re.compile(r'(`[^`]+`|\[[^\]]*\]\([^)]*\)|RSS\d+[A-Z]*-\d+|UMII\d+-\d+|W\.\d+\.\d+\.\d+\.[A-Za-z_0-9]+|PTT[0-9A-Z.-]+|\d+W/\d+T\d+|LAB\d+|L\d+RO[0-9A-Z]+|[CPN]\d+)')
    code=False;out=[]
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith('```'):code=not code;out.append(line);continue
        if code:out.append(line);continue
        parts=token.split(line)
        for i in range(0,len(parts),2):
            s=parts[i]
            s=re.sub(r'(?<=[a-ząćęłńóśźż])(?=\d)',' ',s)
            s=re.sub(r'(?<=\d)(?=[a-ząćęłńóśźż])',' ',s)
            s=re.sub(r'(?<=\d)(?=(?:Hz|Vrms|Arms|V|W)\b)',' ',s)
            s=re.sub(r'(SPL|RMS)(?=\d)',r'\1 ',s)
            for a,b in [('minimumF3','minimum F3'),('goSPL','go SPL'),('pełnyPDF','pełny PDF'),
                        ('SPLRMS','SPL RMS'),('znaneVb','znane Vb'),('dwie','dwie'),
                        ('znaneRe','znane Re'),('ilość','ilość'),('TSLokoło','TSL około'),
                        ('w4π','w 4π'),('sięP','się P'),('rodzinyP','rodziny P')]:s=s.replace(a,b)
            parts[i]=s
        out.append(''.join(parts))
    return ''.join(out)


def main():
    catalog=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())
    cases=json.loads((ROOT/'wyniki/pula_weryfikacja.json').read_text())
    summaries=load_csv('pula_podsumowanie.csv')
    assessments=json.loads((ROOT/'dane/zrodla/opinie_puli_ocena.json').read_text())['records']
    bounds=json.loads((ROOT/'wyniki/pula_granice_globalne_Vb.json').read_text())
    ident=json.loads((ROOT/'wyniki/p03_identyfikowalnosc.json').read_text())
    assert len(summaries)==len(catalog['drivers'])==len(assessments)==cases['driver_count']
    lines=[f'''# Raport 010 — szeroka pula kandydatów pod brief

Stan: 2026-10-24. Raport cząstkowy badań bez urządzenia. Końcowy PDF jest
odłożony zgodnie z decyzją użytkownika do wykonania programu30pakietów.
Na końcu ma powstać jeden wybór głośnika i jednej konstrukcji, nie sama lista.

## Zakres i kwalifikacja

Zebrano tabele producentów dla **{len(summaries)} modeli, {cases['manufacturer_count']} producentów**.
Są tu modele12/15calowe, klasa12.5oraz dwie jawnie oznaczone kontrole10calowe
(SEAS iPURIFI). Kontrola spoza głównej klasy nie staje się automatycznie
finalistą. Aktualność staregoPeerless, statusRSS390HE i niezgodność oznaczenia
jednej kartySTX pozostają odrębnymi otwartymi bramkami danych.

Dane: [pula_rozszerzona.json](../dane/przetworniki/pula_rozszerzona.json).
Obliczenia: [CSV](../wyniki/pula_objetosci_i_naped.csv),
[podsumowanie](../wyniki/pula_podsumowanie.csv),
[audytT/S](../wyniki/pula_spojnosc_ts.csv).

## Dane kandydata i granice ruchu

X to przyjęta jednostronna amplituda katalogowa, nie wspólny prógTHD.
Wartości w kolumnachSPL to granice modeluRMS dla osobnego sinusa20Hz,
idealna półprzestrzeń2π,1m. Nie są pomiarami ani poziomem w pokoju.

| ID / model | Klasa [cal] | X [mm] | Sd·X [l] | Tylko ruch20Hz [dB] |100l/40Vrms/12Arms20Hz [dB]|
|---|---:|---:|---:|---:|---:|''']
    for r in catalog['drivers']:
        s=next(x for x in summaries if x['candidate_id']==r['candidate_id'])
        lines.append(f"| {r['candidate_id']} {r['model']['name']} |{r['nominal_size_class_in']}|{r['model']['xmax_mm']:g}|{float(s['vd_catalog_l']):.3f}|{float(s['motion_only_20hz_spl_rms_2pi_1m_db']):.2f}|{float(s['at100l_20hz_40v12a_db']):.2f}|")
    lines.append(f'''
## Porównywalne warunki

Policzono **{cases['scenarios']} kombinacji**: objętości20–150l co1l,
dwa hipotetyczne napędy40Vrms/12Arms i60Vrms/20Arms oraz ruch równy0.7i1.0
wartości katalogowej. To scenariusze inżynierskie;0.7X nie gwarantuje niskiegoTHD.
Pasma:20/25/31.5/40/63/80Hz. Pe różnych protokołów nie jest wspólną granicą
termiczną. Nie zadeklarowano bezpiecznej mocy ciągłej ani temperatury.

Przeskanowany zakres20–150l nie jest limitem wymiarów. Analiza wszystkich
dodatnichVb dla pojedynczego sinusa jest w[raporcie011](011_granice_globalne_litrazu.md).
MinimumF3 to inny problem niż najlepsza skrzynia pod pełny brief.

## Wyniki zmieniające interpretację wcześniejszych czterech modeli

- UMII12-22 ma katalogoweSd·X praktycznie równeRSS390HF-4. Rozmiar12/15sam
  nie określa wydajności; przy wspólnych40Vrms różni się wymagany napęd.
- RSS390HE-22 ma wyższą nominalną granicę ruchu, ale przy100l i20Hz
  model potrzebuje około86.5Vrms do27mm, wobec29.3Vrms do14mm dlaRSS390HF-4.
  Tych napięć nie należy utożsamiać z dopuszczalną pracą ciągłą.
- STXW.32.500.8.MC_v2 podaje15mm p-p, czyli7.5mm jednostronnie;
  W.32.800.8.FCX podaje30mm p-p, czyli15mm jednostronnie.
- PURIFI używa określeniaXmax dla granicymechanicznej25mm, aXlin14.75mm
  dla ruchu liniowego. Do porównania użytoXlin. DlaLaVoce42.8mm p-p
  jest powiązane zXmech, nie z katalogowymXmax12.1mm.
- Faital dodaje do geometrycznego overhangu1/3wysokości szczeliny.
  DefinicjeX nie są wspólną kalibracją jakości; nie utworzono rankinguTHD.

## Krytyczna ocena opinii

Dla każdego modelu zapisano zapytanie, trafienia, odczyt oraz ocenę zgodności
modelu. Nie przyjęto liczbowych twierdzeńSPL/THD zforów bez odpowiednich warunków.
[Rejestr wyszukiwań](../dane/zrodla/opinie_puli_przeglad.json),
[ocena treści](../dane/zrodla/opinie_puli_ocena.json).

| Kandydat | Rodzaj dowodu / istotne ograniczenie |
|---|---|''')
    for r in assessments:
        lines.append(f"| {r['candidate_id']} {r['model']} | [{r['status']}]({r['reviewed_url']}) — {r['observation']} {r['limitations']} |")
    lines.append('''
Istotna uwaga dlaRSS390HF: w jednym wątku są zgłoszenie odgłosu oil-can
oraz relacja użytkownika bez tego objawu. Nie znamy częstości ani wspólnych
warunków. To hipoteza do sprawdzeniaP12/P30, nie statystyka awarii.
Pozytywne opisyRSS390HE obejmują teżBR i wolne powietrze; nie są dowodem
osiągów sealed. DlaLAB12 uwzględniono dalszy wpis oocieraniu cewki po
początkowym zadowoleniu. Nietrafne ogłoszeniezakupuBMS i opis innego modelu
zostały odrzucone jako opinia o15S430v2.

## Bramka profesjonalnego doboru

Każdy model musi przejść ślad wymagań:20–40Hz, liniowość, napęd i ochrona,
korekcja, konstrukcja, możliwość późniejszego układu dwóch subwooferów
i niepewność. Nominalna granica ruchu nie zamyka tej bramki. Nadal potrzebne
sąP06/P12–P17,P18–P25iP29, a nie wybór marki z jednej kolumny tabeli.

Nie wybrano jeszcze końcowego głośnika. Wybór ma być pojedynczy i uzasadniony
po integracji badań. Rodzaj kleju oraz kompletna konstrukcja są obowiązkoweP19/P20.
''')
    (ROOT/'raporty/010_szeroka_pula_i_kwalifikacja.md').write_text(readable('\n'.join(lines)))
    lines=[f'''# Raport 011 — globalne granice po objętości bez sztucznego limitu

Stan:2026-10-24. Zakres: model liniowy, jeden sinus, stałe limityV/I/X,
idealne2π/1m. Nie jest to optymalizacja całego pasma, muzyki, termiki i konstrukcji.

## Wyprowadzenie

NiechB=BL, Ks=1/Cms, Kb=rho*c²*Sd²/Vb, kappa=Ks+Kb−Mms*omega².
Zmienna kappa jest ograniczona od dołu przezkappa0=Ks−Mms*omega².
PrzyRMS i stałymLe:

```text
A = Re²+(omega*Le)²
B2 = 2*omega²*Le*B²
C0 = omega⁴*Le²*Rms²+omega²*(Re*Rms+B²)²
den² = A*kappa²+B2*kappa+C0
vV = Vmax*B*omega/sqrt(den²)
vI = Imax*B*omega/sqrt(kappa²+(omega*Rms)²)
vX = omega*Xpeak/sqrt(2)
v_available = min(vV,vI,vX)
```

Kandydaci maksimum: dolna granica kappa0, stacjonarne punktyvVivI,
przecięcia ich krzywych. Przykappa→∞ oba ograniczenia elektryczne dążą
dozera. OgraniczenieX może tworzyć plateau; nie zmienia kompletności
zbioru kandydatów na maksymalną wartość. Objętość wynika z
`Vb=rho*c²*Sd²/(kappa-kappa0)`. Granica kappa=kappa0 odpowiadaVb→∞.

Wyznaczono też przedziałVb osiągający wynik niegorszy niż0.5dB poniżej
granicy: nierównościvV>=vcelivI>=vcel są kwadratowymi nierównościami
przedziałowymi wkappa. To próg scenariusza, nie zatwierdzona specyfikacja.

## Kontrole i dziedzina wniosku

Sprawdzono symbolicznie rozwinięcie mianownika i punkt stacjonarny.
Policzono{bounds['cases']}przypadki: wszystkie modele puli,6pasm i2napędy.
Odrębna ocena w modelu bazowym:1200objętości0.01–10^7l oraz lokalna
optymalizacja numeryczna. Maksymalne przewyższenie granicyanalitycznej
przez wynik numeryczny: {bounds['max_numeric_excess_over_analytic_bound_db']:.3g}dB.
Sprawdzono takżeLe=0 i zdegenerowane przecięcie dlaVmax=Re*Imax.

To kontrola algebry i obliczeń zmiennoprzecinkowych, nie końcowe obudowy
ani przedziałowa certyfikacja wszystkich błędów zaokrągleń.

## Przykład20Hz: nie więcej niż0.5dB poniżej granicy

| Model |Vmax [Vrms]|GranicaSPLRMS [dB]|MinimalneVb w tym scenariuszu [l]|
|---|---:|---:|---:|''']
    for r in bounds['selected_20hz']:
        val=r['vb_min_within_tolerance_l']
        lines.append(f"| {r['driver']} |{r['amp_vrms']:g}|{r['single_frequency_spl_2pi_1m_db']:.2f}|{val:.1f}|")
    lines.append('''
Nie jest to „minimalna bezpieczna skrzynia”. Inne częstotliwości,EQ,THD,
termika, masa i panele mogą wymagać innego wyboru. Duże wartości pokazują
koszt dążenia do granicy jednego punktu20Hz, a nie obowiązek budowy ogromnej
skrzyni.100/150l nie przyjęto jako odgórnego limitu briefu.

Analogicznie minimumF3 samo w sobie nie wybiera prototypu. Dla modelu2.rzędu
minimalizacja poVb, gdyQts<1/sqrt(2), dajeQtc=1/sqrt(2). DlaUMII15-22
takie kryterium prowadzi do około5m³ z powoduQts bliskiego0.707; nie jest
to rekomendacja konstrukcyjna. Wybór wymaga połączenia całego briefu.

Kod:[granice_litrazu.py](../skrypty/granice_litrazu.py),
[eksperyment](../skrypty/analiza_granic_litrazu.py).
Wyniki:[CSV](../wyniki/pula_granice_globalne_Vb.csv),
[JSON](../wyniki/pula_granice_globalne_Vb.json).
''')
    (ROOT/'raporty/011_granice_globalne_litrazu.md').write_text(readable('\n'.join(lines)))
    text=f'''# Raport 012 — identyfikowalność i opublikowane parametry

Stan:2026-10-24. Kod:[audyt_identyfikowalnosci.py](../skrypty/audyt_identyfikowalnosci.py).
Rozdzielamy dowód modelowy, dane opublikowane i eksperyment syntetyczny.

## Nieidentyfikowalność z samej impedancji w wolnym powietrzu

```text
Z(s)=Re+s*Le+(B²/M)*s/(s²+(R/M)*s+K/M)
```

Przekształcenie B→sqrt(alpha)B, M→alpha*M, R→alpha*R, K→alpha*K
nie zmienia tej funkcji. Jakobian kombinacjiB²/M,R/M,K/M ma rząd3
dla4niewiadomych. Symbolicznie sprawdzono wektor zerowy[B/2,M,R,K].
Nie wolno więc uważać wszystkich parametrów mechanicznych wyprowadzonych
z jednej impedancji za niezależnie zmierzone.

GdyRe,Le,Sd są znane, dwa idealne znaneVb przełamują tę swobodę:
różnica zidentyfikowanych współczynnikówKeff/M jest równa
`(Kb1-Kb2)/M`. Wykonano osobne dopasowanie liniowego układu równań
do syntetycznych zespolonych impedancji60/100l dla{ident['drivers']}modeli.
Maksymalny względny błąd odzyskaniaMms: {ident['max_relative_two_volume_mass_recovery_error']:.3g}.
To nie jest próba z szumem ani pomiar egzemplarzy. Współczynników nie
odczytuje się po prostu z położenia szczytu impedancji.

Przy nieznanymSd istnieje dalsza swoboda: równoległa zmianaSd i parametrów
mechanicznych może zachować zarówno impedancję znanej skrzyni, jak iSPL,
zmieniając faktyczny ruch. Test numeryczny potwierdził taki kontrprzykład.
Do identyfikacji potrzebna jest dodatkowa informacja geometryczna, masa
lub niezależny pomiar ruchu. Nie dodajemy fikcyjnych wartości do danych.

## Dane publikowane Scan-Speak 32W/4878T00

Obejrzano strony2–5 oryginalnego skanuVoiceCoil z2013roku,
[źródło](https://www.scan-speak.dk/datasheet/reviews/32W-4878T00-VoiceCoil_2013-3.pdf).
Zachowano wspólne zestawy dwóch próbek i metodTSL/LTD. Nie zrobiono
z dwóch egzemplarzy rozkładu tolerancji produkcyjnej. Tekst podaje ograniczenia
XBl70%=14.9mm iXC50%=12.3mm dla przyjętego tam kryterium20%.
Nie oznacza to niskiegoTHD przy12.3mm. Nie przyjęto automatycznych tablic
wartości z wykresów, w tym niezweryfikowanegoTHD20Hz z ekstrakcji.

Policzono{ident['published_parameter_projections']}klasycznych projekcji kształtu
odpowiedzi2.rzędu dla tabeli źródłowej i aktualnej karty. Nie jest to odtworzenie
częstotliwościowo zależnegoLEAP5LTD ani jego modeli wypełnienia.
Dla50l fabryczny zestaw dajeF3około40.39Hz, a dwie klasyczne projekcje
zmierzonychTSLokoło37.38i38.81Hz. Ta różnica jest większa od błędu
numerycznego samego rozwiązania; nie wolno nadawać ostatnim cyfrom znaczenia
większego niż jakość danych.

Wnioski dla prototypu: porównywać wspólne zestawy parametrów, rozróżniać
metodę i egzemplarz, kontrolowaćSd i rzeczywisty litraż, badać szczelność
przed identyfikacją podatności. Znana geometria i sterowalna objętość mają
wartość identyfikacyjną; nie zastępują późniejszego pomiaru.

Dane:[publikacja](../dane/zrodla/pomiary_opublikowane/scan32_voicecoil_2013.json).
Wyniki:[identyfikacja](../wyniki/p03_identyfikacja_syntetyczna.csv),
[projekcje](../wyniki/p03_scan32_zestawy_opublikowane.csv),
[kontrole](../wyniki/p03_identyfikowalnosc.json).
'''
    (ROOT/'raporty/012_identyfikowalnosc_i_dane_publikowane.md').write_text(readable(text))
    print('Zapisano raporty010–012; końcowegoPDF nie utworzono.')


if __name__=='__main__':main()
