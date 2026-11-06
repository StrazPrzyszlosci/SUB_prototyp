"""Independent checks for S01 volume, orientation, DSP and saved findings."""
import json
from math import isclose
from s01 import HERE, cabinet

r=json.loads((HERE/'s01_wyniki.json').read_text())
assert len(r['volume_sweep'])==91
assert [i['litres'] for i in r['volume_sweep']]==list(range(70,161))
for g in r['shapes'].values():
    w,h,d=g['inner_mm']
    free=w*h*d/1e6-sum(g[k] for k in ('driver_L','terminal_L','wiring_glue_L','brace_L'))
    assert isclose(free,r['net_target'],abs_tol=1e-7)
    assert g['body_D']+38+18==450
    turned=cabinet(r['net_target'],h/w)
    assert isclose(turned['W'],g['H'],abs_tol=1e-7)
    assert isclose(turned['rear_center_mm_1kPa'],g['rear_center_mm_1kPa'],abs_tol=1e-8)
for row in r['finalists']:
    assert abs(row['corrected_dB'][3]-95)<1e-7
    assert row['max_V']<40 and row['max_A']<12
assert max(r['stress_minband_dB'],key=lambda k:r['stress_minband_dB'][k]['50'])=='C02'
for room in r['room'].values():
    assert abs(room['ripple_20_80_dB']-room['controls'][-1]['ripple_dB'])<.01
assert len(r['room'])==4
print('S01: zgodne bilanse, obrót, poziom odniesienia, ranking i zbieżność modalna.')
