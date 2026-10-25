"""Pusta szeroka szczelina: liniowy w pełni rozwinięty przepływ Stokesa.

Nie przepływ turbulentny,lepkie pękanie kleju ani kanał o dowolnej geometrii.
exp(+jwt); impedancja p/Q,DCpochodzi zPoiseuille'a,aWo z dokładnego profilu.
"""
import numpy as np
from model_gazu import Medium


def slit_impedance(f_hz,height_m,width_m,length_m,medium=Medium()):
    if min(height_m,width_m,length_m)<=0:raise ValueError('Dodatnia geometria otwartego kanału')
    f=np.atleast_1d(np.asarray(f_hz,float))
    if np.any(f<0) or np.any(~np.isfinite(f)):raise ValueError('f>=0, skończone')
    Rdc=12*medium.viscosity_pa_s*length_m/(width_m*height_m**3)
    y=height_m/2*np.sqrt(2j*np.pi*f*medium.rho/medium.viscosity_pa_s)
    z=np.full(f.shape,Rdc,dtype=complex);positive=f>0
    yp=y[positive];small=abs(yp)<.05;F=np.empty_like(yp)
    a=yp[small]
    F[small]=a*a/3-2*a**4/15+17*a**6/315-62*a**8/2835+1382*a**10/155925
    a=yp[~small];F[~small]=1-np.tanh(a)/a
    z[positive]=Rdc*(yp*yp/3)/F
    return z
