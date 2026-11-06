"""Regression for the nominal datums and the incomplete / marginal / eccentric field card."""
import json
from math import isclose
from s07 import HERE, LAYERS, check_card, nominal

data = nominal(json.loads((HERE/'s06_wyniki.json').read_text()))
assert data['brace_gap_from_full_178_mm'] == 19
assert isclose(data['window_vs_bore_radial_mm'], 6.65)
card = json.loads((HERE/'s07_karta.json').read_text())
assert check_card(card)['status'] == 'brak_pomiarow'
card.update(promien_obwiedni_max=177.4, blad_prowadzenia_max=.2, luz_wymagany=.2)
for layer in LAYERS:
    card[f'{layer}_srednica_wpisana_min'] = 355.8
    card[f'{layer}_blad_osi_max'] = .1
assert check_card(card)['status'] == 'spelniony_warunek_promieniowy'
card['FR2_blad_osi_max'] = .11
result = check_card(card)
assert result['status'] == 'do_przymiarki'
assert result['rezerwa_po_odjeciu_luzu_mm']['FR2'] == -.01
for invalid in (-.1, False, float('nan')):
    try:
        check_card(dict(card, luz_wymagany=invalid))
    except ValueError:
        continue
    raise AssertionError('Invalid required clearance accepted')
