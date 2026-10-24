"""P06: wektoryzowana rodzina dodatnich parametrów pierwotnych.

Zmienne M,C,B,R,Re,Le,Sd są pierwotne; nie losujemy niezależnie wszystkich T/S.
Przeciek ma stały Ra względem referencji100l, nie stałe fleak przy zmianie Vb.
"""
import json
from pathlib import Path
import numpy as np
from scipy.special import ndtr, ndtri
from model_subwoofera import C, RHO, P_REF

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'dane/konfiguracje/p06_niepewnosc.json').read_text())
FACTORS = CFG['factor_order']


def correlated_design(u, rho):
    u = np.array(u, dtype=float, copy=True)
    if not np.isfinite(rho) or abs(rho) > 1:
        raise ValueError('Korelacja kopuli musi należeć do [-1,1]')
    if rho:
        eps = np.finfo(float).eps
        z0, z1 = (ndtri(np.clip(u[:, i], eps, 1-eps)) for i in [0, 1])
        u[:, 1] = ndtr(rho*z0 + np.sqrt(1-rho*rho)*z1)
    return u


def physical(d, u, vb_l, amp_vrms, amp_irms, family='L'):
    u = np.asarray(u, dtype=float)
    if u.ndim != 2 or u.shape[1] != len(FACTORS) or np.any(~np.isfinite(u)) or np.any((u < 0) | (u > 1)):
        raise ValueError('Projekt punktów musi należeć do [0,1]^13')
    if family not in ['D', 'L']:
        raise ValueError('Nieznana rodzina')
    if not all(np.isfinite(x) and x > 0 for x in [vb_l, amp_vrms, amp_irms]):
        raise ValueError('Dodatnie skończone Vb, Vmax i Imax')
    factors = {key: bounds[0] + (bounds[1]-bounds[0])*u[:, i]
               for i, key in enumerate(FACTORS) for bounds in [CFG['ranges'][key]]}
    if family == 'D':
        factors.update(leak_ref_hz=np.zeros(len(u)), extra_r_over_rms=np.zeros(len(u)),
                       x_fraction=np.ones(len(u)))
    values = dict(mms=d.mms*factors['mms'], cms=d.cms*factors['cms'],
                  bl=d.bl*factors['bl'], rms=d.rms*factors['rms'],
                  re=d.re_ohm*factors['re'], le=d.le_mh*1e-3*factors['le'],
                  sd=d.sd*factors['sd'], vb_l=vb_l*factors['vb'],
                  vmax=amp_vrms*factors['vmax'], imax=amp_irms*factors['imax'],
                  xmax_m=d.xmax_mm*1e-3*factors['x_fraction'],
                  extra_r_fraction=factors['extra_r_over_rms'])
    values['leak_hz'] = factors['leak_ref_hz']*CFG['leak_reference_volume_l']/values['vb_l']
    return values


def evaluate(d, u, vb_l=100., amp_vrms=40., amp_irms=12., family='L', frequencies_hz=(20., 40.)):
    p = physical(d, u, vb_l, amp_vrms, amp_irms, family)
    f = np.asarray(frequencies_hz, dtype=float)
    if f.ndim != 1 or np.any(~np.isfinite(f)) or np.any(f <= 0):
        raise ValueError('Dodatnie częstotliwości')
    w = 2*np.pi*f[None, :]
    s = 1j*w
    v = {key: value[:, None] for key, value in p.items()}
    a = 2*np.pi*v['leak_hz']
    h = s/(s+a)
    kb = RHO*C*C*v['sd']**2/(v['vb_l']*1e-3)
    zm = (v['rms']*(1+v['extra_r_fraction']) + s*v['mms'] +
          1/(s*v['cms']) + kb/(s+a))
    ze = v['re'] + s*v['le']
    velocity_per_v = v['bl']/(ze*zm+v['bl']**2)
    current_per_v = zm/(ze*zm+v['bl']**2)
    limits = np.stack([v['vmax'] + np.zeros_like(w),
                       v['imax']/abs(current_per_v),
                       v['xmax_m']*w/(np.sqrt(2)*abs(velocity_per_v))])
    voltage = limits.min(axis=0)
    velocity = velocity_per_v*voltage
    pressure = RHO*w*v['sd']*abs(velocity)*abs(h)/(2*np.pi)
    spl = 20*np.log10(pressure/P_REF)
    return dict(spl_db=spl, voltage=voltage,
                current=abs(current_per_v)*voltage,
                x_peak_m=np.sqrt(2)*abs(velocity)/w,
                active_limit=np.argmin(limits, axis=0),
                velocity_complex_m_s=velocity, h=h, zm=zm, physical=p)


def derived_ts(p):
    omega = 1/np.sqrt(p['mms']*p['cms'])
    return dict(fs=omega/(2*np.pi), qes=omega*p['mms']*p['re']/p['bl']**2,
                qms=omega*p['mms']/p['rms'], vas_l=RHO*C*C*p['sd']**2*p['cms']*1000)
