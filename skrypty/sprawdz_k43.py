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
card.update(protokol='TEST', wymagane_pelne_zazebienie_mm=4, wymagany_luz_dna_mm=1,
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
