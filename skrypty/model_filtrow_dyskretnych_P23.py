"""P23: własne biquady, dokładne nierówności Schura/Jury, bez sprzętu.

Konwencja SciPy: H=(b0+b1*z^-1+b2*z^-2)/(1+a1*z^-1+a2*z^-2).
SI: f i Fs w Hz; opóźnienie w s. Dodatnie Q i częstotliwości < Nyquista.
"""
from fractions import Fraction
import math
import numpy as np


def quadratic(f_hz, q):
    if not np.isfinite(f_hz) or f_hz <= 0 or not np.isfinite(q) or q <= 0:
        raise ValueError('Dodatnia skończona częstotliwość i Q')
    w=2*np.pi*f_hz
    return np.array([1., w/q, w*w])


def bilinear_second_order(b, a, fs):
    """Bez prewarpu: s=2Fs(1-z^-1)/(1+z^-1), druga potęga osobno."""
    if not np.isfinite(fs) or fs <= 0:raise ValueError('Fs>0')
    k=2*fs
    def transform(p):
        x,y,z=np.asarray(p,dtype=float)
        return np.array([x*k*k+y*k+z, -2*x*k*k+2*z, x*k*k-y*k+z])
    bd,ad=transform(b),transform(a)
    return np.r_[bd/ad[0],ad/ad[0]]


def chain(fc, qc, ft, qt, hp, lp, fs):
    for f in [fc,ft,hp,lp]:
        if not 0<f<fs/2:raise ValueError('Częstotliwości w (0,Nyquist)')
    return np.array([
        bilinear_second_order(quadratic(fc,qc),quadratic(ft,qt),fs),
        bilinear_second_order([1.,0.,0.],quadratic(hp,qt),fs),
        bilinear_second_order([0.,0.,(2*np.pi*lp)**2],quadratic(lp,qt),fs),
        bilinear_second_order([0.,0.,(2*np.pi*lp)**2],quadratic(lp,qt),fs)])


def represent(sos, name):
    a=np.asarray(sos,dtype=float)
    if name=='float64':return a.copy()
    if name=='float32':return a.astype(np.float32).astype(float)
    if name.startswith('decimal'):
        # Liczba CYFR PO KROPCE,nie cyfr znaczących;to jawny scenariusz pliku.
        digits=int(name[7:])
        return np.array([[float(f'{x:.{digits}f}') for x in row] for row in a])
    raise ValueError(name)


def schur(section):
    """Dokładne Fraction z realnych bitów zapisanych współczynników.

    Dla rzeczywistego monicznego z²+a1*z+a2: |a2|<1 i 1±a1+a2>0.
    Zwrot 'boundary' oznacza brak ścisłej stabilności stanów,nawet przy
    możliwym skasowaniu bieguna zerem transmitancji.
    """
    a0,a1,a2=map(lambda x:Fraction.from_float(float(x)),section[3:])
    if a0!=1:raise ValueError('Moniczny mianownik wymagany')
    m=(1+a1+a2,1-a1+a2,1-a2,1+a2)
    state='strict' if min(m)>0 else ('boundary' if min(m)==0 else 'outside')
    return dict(state=state,min_margin=float(min(m)),p_plus1=float(m[0]),
                p_minus1=float(m[1]),one_minus_a2=float(m[2]),one_plus_a2=float(m[3]),
                exact_margins=[str(x) for x in m])


def polynomial_on_circle(coeff, q_minus1):
    """Ogranicza utratę cyfr dla z≈1;współczynniki pozostają te same."""
    b0,b1,b2=map(float,coeff)
    return math.fsum([b0,b1,b2])+(b1+2*b2)*q_minus1+b2*q_minus1*q_minus1


def frequency_response(sos, freq, fs):
    w=2*np.pi*np.asarray(freq,dtype=float)/fs
    dq=np.expm1(-1j*w);q=1+dq
    h=np.ones(w.shape,complex);delay=np.zeros(w.shape,float)
    for section in sos:
        b,a=section[:3],section[3:]
        num=polynomial_on_circle(b,dq);den=polynomial_on_circle(a,dq)
        h*=num/den
        delay+=np.real(q*((b[1]+2*b[2]*q)/num-(a[1]+2*a[2]*q)/den))/fs
    return h,delay


def analog_response(fc,qc,ft,qt,hp,lp,freq):
    s=2j*np.pi*np.asarray(freq)
    pairs=[(quadratic(fc,qc),quadratic(ft,qt)),
           (np.array([1.,0.,0.]),quadratic(hp,qt)),
           (np.array([0.,0.,(2*np.pi*lp)**2]),quadratic(lp,qt)),
           (np.array([0.,0.,(2*np.pi*lp)**2]),quadratic(lp,qt))]
    h=np.ones(s.shape,complex);delay=np.zeros(s.shape,float)
    for b,a in pairs:
        n,d=np.polyval(b,s),np.polyval(a,s)
        h*=n/d
        delay+=np.real(np.polyval(np.polyder(a),s)/d-np.polyval(np.polyder(b),s)/n)
    return h,delay


def feedback_convention(sos):
    """Własna serializacja dla y=Σbk*x[n-k]+c1*y[n-1]+c2*y[n-2].

    Założenie konwencji sprawdzamy dokładnym round-trip;nie wysyłamy do DSP.
    """
    return [dict(b0=float(s[0]),b1=float(s[1]),b2=float(s[2]),
                 c1=float(-s[4]),c2=float(-s[5])) for s in sos]


def from_feedback(records):
    return np.array([[r['b0'],r['b1'],r['b2'],1.,-r['c1'],-r['c2']] for r in records])
