"""Geometry gate for a measured, clamped K42 front. All input dimensions in mm."""
import json
import math
import sys
from pathlib import Path

BORES = ('FR1', 'kosz', 'ulga_FR2')


def positive(value, zero=False):
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0 or (not zero and value == 0):
        raise ValueError('Brak dodatniego pomiaru lub wpisano niepoprawną granicę')
    return value


def evaluate(card):
    if not isinstance(card['protokol'], str) or not card['protokol'].strip():
        raise ValueError('Wpisz identyfikator protokołu')
    axes = card['osie']
    if set(axes) != {str(k) for k in range(1, 9)}:
        raise ValueError('Wymagane osie 1 do 8')
    target = positive(card['wymagane_pelne_zazebienie_mm'])
    tip_gap = positive(card['wymagany_luz_dna_mm'])
    diam = positive(card['sruba_srednica_max_mm'])
    thread = positive(card['dlugosc_od_konca_do_poczatku_pelnego_gwintu_przy_lbie_min_mm'])
    tip = positive(card['niepelny_gwint_na_koncu_max_mm'], True)
    lmin = positive(card['sruba_dlugosc_min_mm'])
    lmax = positive(card['sruba_dlugosc_max_mm'])
    if lmax < lmin or thread <= tip or thread > lmin:
        raise ValueError('Niespójne wymiary śruby')
    results = {}
    lower = thread
    upper = math.inf
    blocked = []
    for key, row in sorted(axes.items()):
        # Depth from the washer-bearing underside of the bolt head in the compressed stack.
        a = positive(row['glebokosc_pierwszego_pelnego_zwoju_max_mm'])
        b = positive(row['glebokosc_ostatniego_pelnego_zwoju_min_mm'])
        bottom = positive(row['glebokosc_dna_min_mm'])
        if not a < b <= bottom:
            raise ValueError('Niespójna głębokość na osi ' + key)
        margins = {}
        for name in BORES:
            bore = row[name]
            d = positive(bore['srednica_min_mm'])
            offset = positive(bore['odchylka_osi_max_mm'], True)
            margins[name] = (d-diam)/2-offset
        # Full internal thread [a,b] and full external thread [L-thread,L-tip].
        # At least target must fit in each interval and across both facing ends.
        axis_lower = max(thread, a+target+tip)
        axis_upper = min(b+thread-target, bottom-tip_gap)
        lower = max(lower, axis_lower)
        upper = min(upper, axis_upper)
        if min(margins.values()) <= 0 or min(b-a,thread-tip) < target or axis_lower > axis_upper:
            blocked.append(key)
        # Minimum positive overlap or zero over the supplied lot length range.
        engagement = min(max(0, min(b,L-tip)-max(a,L-thread)) for L in (lmin,lmax))
        reserve = bottom-lmax
        results[key] = {'luz_promieniowy_mm': margins, 'pelny_gwint_min_mm':engagement,
                        'luz_dna_min_mm':reserve,
                        'geometria': min(margins.values())>0 and engagement>=target and reserve>=tip_gap}
    return {'osie':results, 'pasuje_geometrycznie':all(r['geometria'] for r in results.values()),
            'wspolny_zakres_dlugosci_rzeczywistej_mm': (
                [lower,upper] if not blocked and lower<=upper else None),
            'osie_bez_rozwiazania':blocked,
            'status_cnc':'HOLD'}


if __name__=='__main__':
    try:
        print(json.dumps(evaluate(json.loads(Path(sys.argv[1]).read_text())),indent=2))
    except (ValueError,KeyError,TypeError,OSError,IndexError) as error:
        sys.exit('Brak oceny: '+str(error))
