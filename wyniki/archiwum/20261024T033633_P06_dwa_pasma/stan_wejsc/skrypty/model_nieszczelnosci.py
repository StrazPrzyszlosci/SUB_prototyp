"""N7: Cab||Ra, fazory RMS, dwie diagnostyczne małe monopole w 4π.

Radiacja nie wraca do równania napędu; jej moc jest diagnostyką oddzielną
od bilansu zredukowanego T/S. Nie wolno doliczyć jej drugi raz do strat.
"""
import numpy as np
from model_subwoofera import C, RHO, P_REF


def _positive(value, name, zero=False):
    a = np.asarray(value, dtype=float)
    if not a.size or not np.all(np.isfinite(a)) or np.any(a < 0 if zero else a <= 0):
        raise ValueError(f'{name}: wymagane skończone wartości {">=0" if zero else ">0"}')
    return a


def _point(value, name):
    a = np.asarray(value, dtype=float)
    if a.shape != (3,) or not np.all(np.isfinite(a)):
        raise ValueError(f'{name}: trzy skończone współrzędne w metrach')
    return a


def leakage_response(d, vb_l, f_hz, leak_hz=0., vrms=1.,
                     observer=(0., 0., 1.), membrane=(0., 0., 0.), leak=(0., 0., 0.)):
    """leak_hz=0: szczelna; +inf: granica wyrównanego ciśnienia.

    f=0 obsługiwane analitycznie, bez dzielenia przez omega. Szczelny stan
    statyczny zakłada początkowo zrównoważoną komorę (brak uwięzionego offsetu).
    """
    vb = float(_positive(vb_l, 'Vb')) * 1e-3
    f = _positive(f_hz, 'f', zero=True)
    voltage = _positive(vrms, 'V RMS', zero=True)
    f, voltage = np.broadcast_arrays(f, voltage)
    if np.ndim(leak_hz) or np.isnan(leak_hz) or leak_hz < 0:
        raise ValueError('fleak: nieujemny skalar, dopuszczalne +inf')
    obs, src, hole = (_point(v, n) for v, n in [(observer, 'odbiornik'), (membrane, 'membrana'), (leak, 'przeciek')])
    rm, rl = np.linalg.norm(obs-src), np.linalg.norm(obs-hole)
    if rm <= 0 or rl <= 0:
        raise ValueError('Odbiornik nie może leżeć w punkcie źródła')
    s = 2j*np.pi*f
    cab = vb/(RHO*C*C)
    if leak_hz == 0:
        h, hl, conductance = np.ones_like(s), np.zeros_like(s), 0.
    elif np.isposinf(leak_hz):
        h, hl, conductance = np.zeros_like(s), np.ones_like(s), None
    else:
        a = 2*np.pi*leak_hz
        h, hl, conductance = s/(s+a), a/(s+a), a*cab
    stiffness = 1/d.cms
    dynamic = d.mms*s*s+d.rms*s+stiffness+d.sd**2/cab*h
    ze = d.re_ohm+s*d.le_mh*1e-3
    denominator = ze*dynamic+d.bl*d.bl*s
    x = d.bl*voltage/denominator
    current = dynamic*voltage/denominator
    velocity = s*x
    um = d.sd*velocity
    ul = -hl*um
    usum = h*um  # Stabilnie również przy prawie zupełnym znoszeniu.
    pressure_inside = -d.sd/cab*h*x
    gm, gl = np.exp(-s*rm/C)/rm, np.exp(-s*rl/C)/rl
    pm = RHO*s*um*gm/(4*np.pi)
    pl = RHO*s*ul*gl/(4*np.pi)
    delta = np.log1p((rl-rm)/rm)-s*(rm-rl)/C
    total = RHO*s*um*gl*(h+np.expm1(delta))/(4*np.pi)
    pin = np.real(voltage*np.conj(current))
    pcu = d.re_ohm*abs(current)**2
    pmech = d.rms*abs(velocity)**2
    pra = np.zeros_like(f) if conductance is None else conductance*abs(pressure_inside)**2
    # Stabilna postać dodatniej formy mocy dwóch monopoli, bez obciążenia zwrotnego.
    kd = 2*np.pi*f*np.linalg.norm(src-hole)/C
    small = abs(kd) < 1e-3
    one_minus_sinc = np.empty_like(kd)
    one_minus_sinc[small] = kd[small]**2/6-kd[small]**4/120+kd[small]**6/5040
    one_minus_sinc[~small] = 1-np.sinc(kd[~small]/np.pi)
    uplus = usum/np.sqrt(2)
    uminus = (2-h)*um/np.sqrt(2)
    prad = RHO*(2*np.pi*f)**2/(4*np.pi*C)*(
        (2-one_minus_sinc)*abs(uplus)**2+one_minus_sinc*abs(uminus)**2)
    spl = np.full_like(f, -np.inf)
    np.log10(abs(total)/P_REF, out=spl, where=abs(total)>0)
    spl *= 20
    return {'x_complex_m': x, 'x_peak_m': np.sqrt(2)*abs(x), 'i_complex_a': current,
            'i_rms_a': abs(current), 'v_complex_m_s': velocity,
            'p_inside_pa': pressure_inside, 'u_membrane_m3_s': um, 'u_leak_m3_s': ul,
            'u_sum_m3_s': usum, 'h': h, 'p_membrane_pa': pm, 'p_leak_pa': pl,
            'p_total_pa': total, 'spl_4pi_db': spl,
            'p_input_w': pin, 'p_copper_w': pcu, 'p_mech_effective_w': pmech,
            'p_leak_loss_w': pra, 'energy_residual_w': pin-pcu-pmech-pra,
            'radiation_diagnostic_w': prad, 'cab_m3_pa': cab, 'conductance': conductance}


def state_matrices(d, vb_l, leak_hz):
    """Macierze czasu ciągłego; przy granicach redukcja zbędnego stanu komory."""
    vb = float(_positive(vb_l, 'Vb'))*1e-3
    if np.ndim(leak_hz) or np.isnan(leak_hz) or leak_hz < 0:
        raise ValueError('fleak: nieujemny skalar')
    cab = vb/(RHO*C*C)
    finite_leak = 0 < leak_hz < np.inf
    ks = 1/d.cms+(d.sd*d.sd/cab if leak_hz == 0 else 0.)
    if d.le_mh > 0:
        # Stany [i, x, v, p] lub [i, x, v].
        n = 4 if finite_leak else 3
        a = np.zeros((n,n)); b = np.zeros(n)
        a[0,0], a[0,2], b[0] = -d.re_ohm/(d.le_mh*1e-3), -d.bl/(d.le_mh*1e-3), 1/(d.le_mh*1e-3)
        a[1,2] = 1
        a[2,0], a[2,1], a[2,2] = d.bl/d.mms, -ks/d.mms, -d.rms/d.mms
        if finite_leak:
            a[2,3], a[3,2], a[3,3] = d.sd/d.mms, -d.sd/cab, -2*np.pi*leak_hz
        x_index = 1
    else:
        # Le=0 eliminuje stan prądu, zachowując tłumienie elektromagnetyczne.
        n = 3 if finite_leak else 2
        a = np.zeros((n,n)); b = np.zeros(n)
        a[0,1] = 1
        a[1,0], a[1,1], b[1] = -ks/d.mms, -(d.rms+d.bl*d.bl/d.re_ohm)/d.mms, d.bl/(d.re_ohm*d.mms)
        if finite_leak:
            a[1,2], a[2,1], a[2,2] = d.sd/d.mms, -d.sd/cab, -2*np.pi*leak_hz
        x_index = 0
    return a, b, x_index
