"""Nominal butt-joint panel schedule and dimensional screening for cabinet A (mm)."""
import json
import math
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def schedule(width, height, depth, thickness, brace_gap=.2, rim=30, radius=3):
    """Ideal zero-thickness shell bond lines. Gap is total across both edges."""
    wi, hi, di = width-2*thickness, height-2*thickness, depth-3*thickness
    bw, bh = wi-brace_gap, hi-brace_gap
    ow, oh = bw-2*rim, bh-2*rim
    if min(di, thickness, rim) <= 0 or not 0 <= 2*radius <= min(ow, oh) or brace_gap < 0:
        raise ValueError('Invalid panel geometry')
    # Independent material-volume closure before front machining.
    solid_shell = 3*width*height*thickness + 2*di*height*thickness + 2*wi*di*thickness
    assert math.isclose(width*height*depth-solid_shell, wi*hi*di, rel_tol=1e-12)
    opening_area = ow*oh - (4-math.pi)*radius**2
    brace = (bw*bh-opening_area)*thickness / 1e6
    rows = [('FR1', 1, width, height), ('FR2', 1, width, height),
            ('TYL', 1, width, height), ('BOK', 2, di, height),
            ('DNO_GORA', 2, wi, di), ('WREGA', 1, bw, bh)]
    panels = [dict(id=name, per_unit=n, per_pair=2*n, length_mm=a, width_mm=b)
              for name, n, a, b in rows]
    return dict(panels=panels, clear_mm=[wi, hi, di], opening_mm=[ow, oh],
                brace_start_y_mm=2*thickness+(di-thickness)/2,
                gross_L=wi*hi*di/1e6, brace_L=brace,
                pair_blank_m2=sum(2*n*a*b for _, n, a, b in rows)/1e6)


def study(shape):
    width, height, depth = round(shape['W'], 1), round(shape['H'], 1), shape['body_D']
    extras = sum(shape[key] for key in ('driver_L', 'terminal_L', 'wiring_glue_L'))
    layout = schedule(width, height, depth, 22)
    def net(model):
        return model['gross_L'] - model['brace_L'] - extras
    # Outer size/thickness envelope for parts re-dimensioned to each stock.
    values = [net(schedule(width+dw, height+dh, depth+dd, t, radius=r))
              for dw, dh, dd, t, r in product((-.2,.2), (-.2,.2), (-.2,.2),
                                              (21.7,22.3), (3,4))]
    offsets = {}
    for t in (21.7, 22, 22.3):
        # Fixed nominal side heights and bottom widths, flush side-to-side assembly.
        actual_width = layout['clear_mm'][0] + 2*t
        actual_depth = layout['clear_mm'][2] + 3*t
        clear_height = height - 2*t
        brace_height = layout['panels'][-1]['width_mm']
        offsets[str(t)] = dict(body_width_mm=actual_width, body_depth_mm=actual_depth,
                               vertical_brace_clearance_mm=clear_height-brace_height)
    assert sum(p['per_pair'] for p in layout['panels']) == 16
    assert math.isclose(layout['brace_start_y_mm'], 197)
    assert abs(net(layout)-shape['net_L']) < .05
    assert offsets['22.3']['vertical_brace_clearance_mm'] < 0
    return dict(outer_mm=[width,height,depth], nominal_t_mm=22, layout=layout,
                assumed_other_displacement_L=extras, net_L=net(layout),
                fit_range_mm=[.2-.2-.2, .2+.2+.2],
                dimensional_net_range_L=[min(values),max(values)], fixed_cuts=offsets,
                radius_3_to_4_added_solid_mL=(4-math.pi)*(4**2-3**2)*22/1000)


if __name__ == '__main__':
    shape = json.loads((HERE/'s01_wyniki.json').read_text())['shapes']['A']
    (HERE/'s06_wyniki.json').write_text(json.dumps(study(shape), indent=2)+'\n')
