"""Clearance screening for the S04 side terminal; dimensions in mm."""
import json
from pathlib import Path

from s04 import evaluate, projected_depth

HERE = Path(__file__).resolve().parent


def compare_routes(shape):
    base = evaluate(shape)
    # Y is depth from the front board. X is distance out from the side wall.
    plate_y, back_y = 270, 350
    width, center_x, face_height = 70, 35, 72
    socket_radius = 50.8 / 2
    socket_budget, plug_length, free_straight = 10, 82.5, 10
    withdrawal = 35  # design allowance; validate by physical withdrawal
    frontmost = plate_y - socket_budget - plug_length - free_straight
    flange_edge = min(center_x, width - center_x, face_height / 2) - socket_radius
    assert flange_edge > 0 and frontmost - withdrawal > 44
    assert 219 < plate_y < back_y < shape['body_D'] - 22
    routes = {'straight_S04': base['side_space_mm'],
              'NL4FRX': socket_budget + 62,
              'external_bracket': width}
    results = {}
    for name, extension in routes.items():
        upright_height = shape['W'] + 20 + 1 + extension
        results[name] = dict(extension_mm=extension,
                             horizontal_width_mm=shape['W'] + extension,
                             upright_height_nominal_mm=upright_height - 1,
                             upright_depth_with_gap_at_half_degree_mm=
                             projected_depth(434, upright_height, .5) + 5)
    assert results['straight_S04']['upright_depth_with_gap_at_half_degree_mm'] == next(
        row['depth_with_gap_mm'] for row in base['cases']
        if row['orientation'] == 'boczna' and row['pitch_deg'] == .5)
    return dict(routes=results, bracket_y_mm=[plate_y, back_y],
                installed_straight_end_y_mm=frontmost,
                withdrawal_limit_y_mm=frontmost-withdrawal, flange_edge_mm=flange_edge,
                saved_side_mm=routes['straight_S04']-width)


if __name__ == '__main__':
    source = json.loads((HERE / 's01_wyniki.json').read_text())
    result = compare_routes(source['shapes']['A'])
    (HERE / 's05_wyniki.json').write_text(json.dumps(result, indent=2) + '\n')
