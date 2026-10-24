"""Liniowy model zamkniętego subwoofera; SI, napięcia/prądy RMS, Xmax peak.

Model nie przewiduje THD, kompresji cieplnej, pomieszczenia ani nieszczelności.
Zestaw pierwotny: Fs, Qes, Qms, Vas, Sd, Re, Le. Pozostałe T/S są wyprowadzone.
"""
from dataclasses import dataclass
import numpy as np

RHO = 1.2041
C = 343.0
P_REF = 20e-6


@dataclass(frozen=True)
class Driver:
    name: str
    fs_hz: float
    qes: float
    qms: float
    vas_l: float
    sd_cm2: float
    re_ohm: float
    le_mh: float
    xmax_mm: float
    nominal_ohm: float
    rated_w: float

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError('Nazwa przetwornika musi być niepusta')
        for key, value in vars(self).items():
            if key == 'le_mh':
                if not np.isfinite(value) or value < 0:
                    raise ValueError('Le musi być skończone i nieujemne')
            elif key != 'name' and (not np.isfinite(value) or value <= 0):
                raise ValueError(f'{self.name}: {key} musi być dodatnie i skończone')

    @property
    def sd(self):
        return self.sd_cm2 * 1e-4

    @property
    def cms(self):
        return self.vas_l * 1e-3 / (RHO * C**2 * self.sd**2)

    @property
    def mms(self):
        return 1 / ((2 * np.pi * self.fs_hz)**2 * self.cms)

    @property
    def bl(self):
        return np.sqrt(2 * np.pi * self.fs_hz * self.mms * self.re_ohm / self.qes)

    @property
    def rms(self):
        return 2 * np.pi * self.fs_hz * self.mms / self.qms

    @property
    def qts(self):
        return 1 / (1 / self.qes + 1 / self.qms)


def alignment(d, vb_l):
    if not np.isfinite(vb_l) or vb_l <= 0:
        raise ValueError('Objętość netto musi być dodatnia')
    scale = np.sqrt(1 + d.vas_l / vb_l)
    fc, qtc = d.fs_hz * scale, d.qts * scale
    # H(s)=s²/(s²+w0*s/Q+w0²); F3 względem asymptoty wysokoczęstotliwościowej.
    # Dokładne dodatnie rozwiązanie y²+(2-1/Q²)y-1=0, y=(F3/Fc)².
    # Unika arbitralnego przedziału szukania pierwiastka dla bardzo niskiego Q.
    b = 2-1/qtc**2
    discriminant = np.hypot(b, 2.)
    y = 2/(b+discriminant) if b >= 0 else (-b+discriminant)/2
    f3 = fc*np.sqrt(y)
    return fc, qtc, f3


def sealed_shape(f_hz, fc, qtc):
    s = 2j * np.pi * np.asarray(f_hz)
    w0 = 2 * np.pi * fc
    return s**2 / (s**2 + s * w0 / qtc + w0**2)


def response(d, vb_l, f_hz, vrms=1., distance_m=1., solid_angle=2 * np.pi):
    """Idealny monopól w 2pi/4pi; obciążenie promieniowaniem zawarte w T/S.

    Nieruchome sztywne ściany, brak dodatkowego tłumienia wypełnieniem.
    Zm: impedancja mechaniczna odniesiona do prędkości membrany.
    """
    alignment(d, vb_l)
    f = np.asarray(f_hz, dtype=float)
    if (not f.size or not np.all(np.isfinite(f)) or np.any(f <= 0)
            or not np.isfinite(distance_m) or distance_m <= 0
            or not np.isfinite(solid_angle) or solid_angle <= 0
            or not np.all(np.isfinite(vrms)) or np.any(np.asarray(vrms) < 0)):
        raise ValueError('Niepoprawna częstotliwość, geometria lub napięcie')
    w = 2 * np.pi * f
    stiffness = 1 / d.cms + RHO * C**2 * d.sd**2 / (vb_l * 1e-3)
    zm = d.rms + 1j * (w * d.mms - stiffness / w)
    ze = d.re_ohm + 1j * w * d.le_mh * 1e-3
    z = ze + d.bl**2 / zm
    current = np.asarray(vrms) / z
    velocity = d.bl * current / zm
    x_peak = np.sqrt(2) * np.abs(velocity) / w
    pressure = RHO * w * d.sd * np.abs(velocity) / (solid_angle * distance_m)
    return {'z': z, 'i_rms': np.abs(current), 'x_peak_m': x_peak,
            'spl_rms_db': 20 * np.log10(np.maximum(pressure, 1e-30) / P_REF),
            'p_real_w': np.asarray(vrms)**2 * np.real(1 / z),
            'p_copper_w': np.abs(current)**2 * d.re_ohm}


def linear_envelope(d, vb_l, f_hz, amp_vrms, amp_irms):
    """Granica modelu dla pojedynczego sinusa, bez gwarancji termicznej/THD.

    rated_w i nominal_ohm dają tylko orientacyjny limit napięcia katalogowego.
    Moc katalogowa nie jest utożsamiana z dopuszczalnym grzaniem cewki.
    """
    if not np.isfinite(amp_vrms) or not np.isfinite(amp_irms) or amp_vrms <= 0 or amp_irms <= 0:
        raise ValueError('Limity wzmacniacza muszą być skończone i dodatnie')
    one = response(d, vb_l, f_hz)
    limits = np.array([
        (d.xmax_mm * 1e-3) / one['x_peak_m'],
        np.full_like(np.asarray(f_hz, dtype=float), amp_vrms),
        amp_irms / one['i_rms'],
        np.full_like(np.asarray(f_hz, dtype=float), np.sqrt(d.rated_w * d.nominal_ohm))
    ])
    v = limits.min(axis=0)
    result = response(d, vb_l, f_hz, v)
    result.update(v_rms=v, limit=np.argmin(limits, axis=0), voltage_limits=limits)
    return result


def dsp_shape(f_hz, fc, qtc, target_hz=25., target_q=1 / np.sqrt(2), hp_hz=18., lp_hz=80.):
    """Roboczy LT + HP Butterworth 2 + LP LR4; analogowy wzorzec, nie preset DSP."""
    s = 2j * np.pi * np.asarray(f_hz)
    wc, wt, wh, wl = 2 * np.pi * np.array([fc, target_hz, hp_hz, lp_hz])
    lt = (s**2 + wc / qtc * s + wc**2) / (s**2 + wt / target_q * s + wt**2)
    hp = s**2 / (s**2 + np.sqrt(2) * wh * s + wh**2)
    lp = (wl**2 / (s**2 + np.sqrt(2) * wl * s + wl**2))**2
    return lt * hp * lp


def room_modes(dimensions_m, max_hz=200., c=C):
    """Częstotliwości własne sztywnego prostopadłościanu, bez amplitud i RT."""
    dims = np.asarray(dimensions_m, dtype=float)
    if dims.shape != (3,) or not np.all(np.isfinite(dims)) or np.any(dims <= 0):
        raise ValueError('Potrzebne trzy dodatnie wymiary')
    if not np.isfinite(max_hz) or max_hz < 0 or not np.isfinite(c) or c <= 0:
        raise ValueError('Niepoprawna częstotliwość maksymalna lub prędkość dźwięku')
    modes = []
    for nx in range(int(2 * max_hz * dims[0] / c) + 1):
        for ny in range(int(2 * max_hz * dims[1] / c) + 1):
            for nz in range(int(2 * max_hz * dims[2] / c) + 1):
                order = (nx, ny, nz)
                if not any(order):
                    continue
                f = c / 2 * np.sqrt(np.sum((np.array(order) / dims)**2))
                if f <= max_hz:
                    kind = {1: 'osiowy', 2: 'styczny', 3: 'ukosny'}[np.count_nonzero(order)]
                    modes.append({'nx': nx, 'ny': ny, 'nz': nz, 'f_hz': float(f), 'typ': kind})
    return sorted(modes, key=lambda row: row['f_hz'])
