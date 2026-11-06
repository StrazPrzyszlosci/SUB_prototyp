"""Synthetic regression cases, never workshop data."""
import json
from pathlib import Path
from k43_front_pomiar import evaluate

card=json.loads((Path(__file__).resolve().parents[1]/'dane/k43_karta_frontu.json').read_text())
try:
    evaluate(card)
except ValueError:
    pass
else:
    raise AssertionError('Pusta karta')
card.update(protokol='TEST', wymagany_luz_promieniowy_mm=.05, wymagane_pelne_zazebienie_mm=4, wymagany_luz_dna_mm=1,
            sruba_srednica_max_mm=5, dlugosc_od_konca_do_poczatku_pelnego_gwintu_przy_lbie_min_mm=20,
            niepelny_gwint_na_koncu_max_mm=1, sruba_dlugosc_min_mm=39.8, sruba_dlugosc_max_mm=40.2)
for row in card['osie'].values():
    row.update(glebokosc_pierwszego_pelnego_zwoju_max_mm=34,
               glebokosc_ostatniego_pelnego_zwoju_min_mm=39.5,glebokosc_dna_min_mm=43.7)
    for key in ('FR1','kosz','ulga_FR2'):
        row[key].update(srednica_min_mm=5.6,odchylka_osi_max_mm=.1)
assert evaluate(card)['pasuje_geometrycznie']
card['osie']['8']['kosz']['odchylka_osi_max_mm']=.4
assert not evaluate(card)['osie']['8']['geometria']
card['osie']['8']['kosz']['odchylka_osi_max_mm']=.1
card.update(sruba_dlugosc_min_mm=44.8,sruba_dlugosc_max_mm=45.2)
assert abs(evaluate(card)['osie']['1']['luz_dna_min_mm']+1.5)<1e-8
card.update(sruba_dlugosc_min_mm=39.8,sruba_dlugosc_max_mm=40.2,
            dlugosc_od_konca_do_poczatku_pelnego_gwintu_przy_lbie_min_mm=3)
assert not evaluate(card)['pasuje_geometrycznie']
print('K43 OK')

# Independent 0.01 mm sweep including infeasible lengths at each end.
card['dlugosc_od_konca_do_poczatku_pelnego_gwintu_przy_lbie_min_mm']=20
card['osie']['2']['glebokosc_pierwszego_pelnego_zwoju_max_mm']=34.5
card['osie']['7']['glebokosc_dna_min_mm']=42.75
field='wspolny_zakres_dlugosci_rzeczywistej_mm'
assert evaluate(card)[field]==[39.5,41.75]
for hundredths in range(3800,4401):
    length=hundredths/100
    card.update(sruba_dlugosc_min_mm=length,sruba_dlugosc_max_mm=length)
    assert evaluate(card)['pasuje_geometrycznie']==(39.5<=length<=41.75)
# Individually possible rows can have disjoint ranges.
card['osie']['2'].update(glebokosc_pierwszego_pelnego_zwoju_max_mm=38,
                         glebokosc_ostatniego_pelnego_zwoju_min_mm=43,
                         glebokosc_dna_min_mm=46)
assert evaluate(card)[field] is None and evaluate(card)['osie_bez_rozwiazania']==[]
card['osie']['7']['FR1']['odchylka_osi_max_mm']=.4
assert evaluate(card)['osie_bez_rozwiazania']==['7']
print('K44 OK')

# Exact decimal boundaries on a single limiting bore. All other axes fit.
card.update(sruba_dlugosc_min_mm=39.8,sruba_dlugosc_max_mm=40.2)
for row in card['osie'].values():
    row.update(glebokosc_pierwszego_pelnego_zwoju_max_mm=34,
               glebokosc_ostatniego_pelnego_zwoju_min_mm=39.5,glebokosc_dna_min_mm=43.7)
    row['FR1'].update(srednica_min_mm=5.6,odchylka_osi_max_mm=.1)
for diameter,expected in [(5.18,False),(5.20,False),(5.28,False),(5.30,True),(5.32,True)]:
    card['osie']['8']['FR1']['srednica_min_mm']=diameter
    result=evaluate(card)
    assert result['pasuje_geometrycznie']==expected
    assert (result[field] is not None)==expected
print('K46 granice luzu OK')
