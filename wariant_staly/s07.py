"""RSS390HF-4 axial installation check. Dimensions in mm, no CAM output."""
import argparse
import json
from decimal import Decimal
from math import isfinite
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYERS = ('FR1', 'pierscien', 'FR2')


def nominal(s06):
    width, height, depth = s06['outer_mm']
    layout = s06['layout']
    brace_y = layout['brace_start_y_mm']
    rear_y = depth - s06['nominal_t_mm']
    # K42 front bores and the equivalent largest centred circle inside the window.
    cutout, ring_bore = 355.8, 358
    return dict(center_xz_mm=[width/2, height/2],
                flange_to_nearest_edge_mm=(min(width, height)-388.4)/2,
                ring_radial_step_mm=(ring_bore-cutout)/2,
                window_vs_bore_radial_mm=(min(layout['opening_mm'])-cutout)/2,
                brace_gap_from_full_178_mm=brace_y-178,
                brace_gap_from_167_5_mm=brace_y-(178-10.5),
                rear_gap_from_full_178_mm=rear_y-178)


def check_card(card):
    required = ['promien_obwiedni_max', 'blad_prowadzenia_max', 'luz_wymagany']
    for layer in LAYERS:
        required.extend([f'{layer}_srednica_wpisana_min', f'{layer}_blad_osi_max'])
    missing = [key for key in required if card.get(key) is None]
    for key in required:
        value = card.get(key)
        if value is None:
            continue
        if type(value) not in (int, float) or not isfinite(value) or value < 0:
            raise ValueError(f'{key}: oczekiwano nieujemnej liczby w mm')
        if value == 0 and 'blad' not in key:
            raise ValueError(f'{key}: wymagany wymiar dodatni')
    if missing:
        return dict(status='brak_pomiarow', brak=missing)
    margins = {}
    for layer in LAYERS:
        radius = Decimal(str(card[f'{layer}_srednica_wpisana_min'])) / 2
        deductions = [f'{layer}_blad_osi_max', 'promien_obwiedni_max',
                      'blad_prowadzenia_max', 'luz_wymagany']
        margins[layer] = float(radius - sum(Decimal(str(card[key])) for key in deductions))
    return dict(status='spelniony_warunek_promieniowy' if min(margins.values()) >= 0
                else 'do_przymiarki', rezerwa_po_odjeciu_luzu_mm=margins)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--karta', type=Path, default=HERE/'s07_karta.json')
    args = parser.parse_args()
    result = dict(nominal=nominal(json.loads((HERE/'s06_wyniki.json').read_text())),
                  przejscie=check_card(json.loads(args.karta.read_text())))
    print(json.dumps(result, ensure_ascii=False, indent=2))
