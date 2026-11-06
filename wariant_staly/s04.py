"""Installed bounding box of S01 geometry. Linear dimensions in mm."""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def projected_depth(depth, height, pitch_deg):
    angle = math.radians(abs(pitch_deg))
    return depth * math.cos(angle) + height * math.sin(angle)


def evaluate(shape):
    body = shape['body_D']
    front = 38
    # Upper allowances for the finished body and either front cassette.
    depth = body + 1 + front + 1
    cable_radius = 7.8 / 2
    # Socket protrusion budget plus full unmated plug length: conservative.
    side_space = 10 + 82.5 + 10 + 80 + cable_radius
    axis_depth = 295
    # Right-angle bend toward the front, before continued lateral service routing.
    axial_min = axis_depth - max(25.4, 80 + cable_radius)
    axial_max = axis_depth + max(25.4, cable_radius)
    assert 219 < axis_depth - 25.4 and axial_max < body - 22
    assert 0 < axial_min < axial_max < body
    cases = []
    for orientation, height in [('dolna', shape['H']), ('boczna', shape['W'])]:
        height += 20 + 1  # feet plus dimensional allowance
        if orientation == "boczna":
            height += side_space  # service side faces up after rotation
        for pitch in (0, .5, 1):
            projected = projected_depth(depth, height, pitch)
            cases.append(dict(orientation=orientation, pitch_deg=pitch,
                              device_depth_mm=projected, depth_with_gap_mm=projected + 5,
                              reserve_mm=450 - projected - 5))
    # Worst-case inside face: outer cassette minus its tolerance, facing, sag and clearance.
    max_rest = (front - 1) - 4 - 3 - 2 - 14
    return dict(reference_net_L=shape['net_L'], side_space_mm=side_space,
                bend_depth_span_mm=[axial_min, axial_max], front_rest_limit_mm=max_rest,
                rear_route_nominal_mm=body + front + 18,
                rear_route_upper_mm=depth + 18, cases=cases)


if __name__ == '__main__':
    shape = json.loads((HERE / 's01_wyniki.json').read_text())['shapes']['A']
    result = evaluate(shape)
    assert math.isclose(result['reference_net_L'], 102)
    assert all(c['reserve_mm'] > 0 for c in result['cases'] if c['pitch_deg'] <= .5)
    assert result['cases'][-1]['reserve_mm'] < 0
    (HERE / 's04_wyniki.json').write_text(json.dumps(result, indent=2) + '\n')
