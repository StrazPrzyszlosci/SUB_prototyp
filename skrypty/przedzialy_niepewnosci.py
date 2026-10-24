"""Konserwatywne obwiednie P06 z arytmetyką przedziałową mpmath.

Dziedzina to jawne przedziały mnożników i zamrożone binarne stałe nominalne.
Podział poprawia ostrość; nawet budżet1 zachowuje pokrycie całej dziedziny.
Nie jest to certyfikacja prawdziwości danych producenta lub modelu fizycznego.
"""
import numpy as np
from mpmath import iv
from model_subwoofera import C, RHO, P_REF
from model_niepewnosci import CFG, FACTORS

iv.dps = CFG['interval_decimal_precision']


def ends(value):
    """Końce IEEE rozszerzone o jeden ulp po konwersji z precyzji IV."""
    return (np.nextafter(float(value.a), -np.inf),
            np.nextafter(float(value.b), np.inf))


def pressure_bounds(d, unit_box, vb_l, vmax, imax, family, f_hz):
    u = np.asarray(unit_box, dtype=float)
    if u.shape != (len(FACTORS), 2) or np.any(~np.isfinite(u)) or np.any(u[:, 0] > u[:, 1]) or np.any((u < 0) | (u > 1)):
        raise ValueError('Przedziały współrzędnych muszą być podzbiorami [0,1]')
    if family not in ['D', 'L'] or not all(np.isfinite(x) and x > 0 for x in [vb_l, vmax, imax, f_hz]):
        raise ValueError('Niepoprawna rodzina lub parametry doświadczenia')
    g = {}
    for i, key in enumerate(FACTORS):
        low, high = CFG['ranges'][key]
        g[key] = iv.mpf(low) + (iv.mpf(high)-iv.mpf(low))*iv.mpf(u[i].tolist())
    if family == 'D':
        g.update(leak_ref_hz=iv.mpf(0), extra_r_over_rms=iv.mpf(0), x_fraction=iv.mpf(1))
    m, compliance, b = iv.mpf(d.mms)*g['mms'], iv.mpf(d.cms)*g['cms'], iv.mpf(d.bl)*g['bl']
    r = iv.mpf(d.rms)*g['rms']*(1+g['extra_r_over_rms'])
    re, le, sd = iv.mpf(d.re_ohm)*g['re'], iv.mpf(d.le_mh*1e-3)*g['le'], iv.mpf(d.sd)*g['sd']
    vb = iv.mpf(vb_l)*g['vb']
    vlim, ilim = iv.mpf(vmax)*g['vmax'], iv.mpf(imax)*g['imax']
    w = iv.mpf(float(2*np.pi*f_hz))
    a = iv.mpf(float(2*np.pi))*g['leak_ref_hz']*iv.mpf(CFG['leak_reference_volume_l'])/vb
    kb = iv.mpf(RHO)*iv.mpf(C)**2*sd**2/(vb*iv.mpf(0.001))
    # Zm = R + jX; część rzeczywista jest ściśle dodatnia.
    rm = r + kb*a/(w**2+a**2)
    xm = w*m - 1/(w*compliance) - kb*w/(w**2+a**2)
    zmag = iv.sqrt(rm**2+xm**2)
    dr = re*rm - w*le*xm + b**2
    di = re*xm + w*le*rm
    den = iv.sqrt(dr**2+di**2)
    vv = vlim*b/den
    vi = ilim*b/zmag
    vx = w*iv.mpf(d.xmax_mm*1e-3)*g['x_fraction']/iv.sqrt(2)
    bounds = [ends(x) for x in [vv, vi, vx]]
    v_low = min(x[0] for x in bounds)
    v_high = min(x[1] for x in bounds)
    # Niezależna granica z bilansu mocy V*I >= Re*I² + R*v².
    passivity_high = ends(vlim/(2*iv.sqrt(re*rm)))[1]
    v_high = min(v_high, passivity_high)
    v_interval = iv.mpf([max(0., v_low), max(0., v_high)])
    habs = w/iv.sqrt(w**2+a**2)
    pressure = iv.mpf(RHO)*w*sd*habs*v_interval/iv.mpf(float(2*np.pi))
    low, high = ends(pressure)
    return max(0., low), high


def refine_enclosure(d, vb_l, vmax, imax, family, f_hz, leaves=24, include_cells=False):
    if not isinstance(leaves, int) or leaves < 1:
        raise ValueError('Budżet liści >=1')
    root = np.tile([0., 1.], (len(FACTORS), 1))
    root_bounds = pressure_bounds(d, root, vb_l, vmax, imax, family, f_hz)
    # Wagi są heurystyką podziału. Ich trafność nie warunkuje pokrycia.
    weights = []
    for i in range(len(FACTORS)):
        cell = np.full_like(root, 0.5)
        cell[i] = [0., 1.]
        a, b = pressure_bounds(d, cell, vb_l, vmax, imax, family, f_hz)
        weights.append(max(0.01, np.log(b/a)))
    if family == 'D':
        weights[10:] = [0., 0., 0.]
    cells = [(root, root_bounds)]
    for _ in range(leaves-1):
        index = int(np.argmax([np.log(bound[1]/bound[0]) for _, bound in cells]))
        cell, _ = cells.pop(index)
        axis = int(np.argmax((cell[:, 1]-cell[:, 0])*weights))
        mid = (cell[axis, 0]+cell[axis, 1])/2
        for edge in [0, 1]:
            new = cell.copy()
            new[axis, 1 if edge == 0 else 0] = mid
            cells.append((new, pressure_bounds(d, new, vb_l, vmax, imax, family, f_hz)))
    low = min(bound[0] for _, bound in cells)
    high = max(bound[1] for _, bound in cells)
    # Każdy wynik jest liczbą ciśnienia; logarytm do prezentacji rozszerzamy.
    lower_db = np.nextafter(20*np.log10(low/P_REF), -np.inf)
    upper_db = np.nextafter(20*np.log10(high/P_REF), np.inf)
    result = dict(lower_pa=low, upper_pa=high, lower_db=float(lower_db), upper_db=float(upper_db),
                leaves=len(cells), root_lower_pa=root_bounds[0], root_upper_pa=root_bounds[1],
                partition_volume=sum(float(np.prod(cell[:, 1]-cell[:, 0])) for cell, _ in cells),
                proof_scope='Przedział ciśnienia z IV; końce dB to prezentacja IEEE, nie formalnie certyfikowany logarytm.')
    if include_cells:
        result['cells'] = [cell.tolist() for cell, _ in cells]
    return result
