"""Pasywny port Thevenina:R+sL w szereg,C na terminalach głośnika.

SI,exp(+jwt),fazoryRMS;głośnik zamknięty z liniowymi T/S,bez cyfrowej EQ.
Nie jest modelem konkretnego wzmacniacza lub jego kontrolera prądu.
"""
import numpy as np
from model_subwoofera import RHO,C


def port_response(d,volume_l,freq_hz,rs_ohm=0.,ls_h=0.,cp_f=0.):
    if volume_l<=0 or min(rs_ohm,ls_h,cp_f)<0:raise ValueError('V>0,RLC>=0')
    freq=np.asarray(freq_hz,dtype=float)
    if np.any(freq<=0) or not np.all(np.isfinite(freq)):raise ValueError('f>0 skończone')
    s=2j*np.pi*freq;stiff=1/d.cms+RHO*C*C*d.sd*d.sd/(volume_l*.001)
    zm=d.rms+s*d.mms+stiff/s
    zdriver=d.re_ohm+s*d.le_mh*.001+d.bl*d.bl/zm
    source_impedance=rs_ohm+s*ls_h;load_y=1/zdriver+s*cp_f
    vt=1/(1+source_impedance*load_y)
    current=vt/zdriver;source_current=vt*load_y;velocity=d.bl*current/zm;x=velocity/s
    pin=np.real(np.conj(source_current))
    ps=rs_ohm*abs(source_current)**2;pcu=d.re_ohm*abs(current)**2;pm=d.rms*abs(velocity)**2
    loss_residual=abs(pin-ps-pcu-pm)/np.maximum(pin,1e-30)
    # Ciśnienie RMS monopola od ruchu,geometria2pi/1m;znak nie wpływa na |p|.
    pressure=RHO*d.sd*s*s*x/(2*np.pi)
    return dict(terminal_voltage=vt,driver_current=current,source_current=source_current,
        velocity=velocity,x=x,pressure=pressure,driver_impedance=zdriver,
        source_loss=ps,coil_loss=pcu,mechanical_loss=pm,input_power=pin,
        energy_relative_residual=loss_residual)


def limited_port(d,volume,freq,rs,ls,cp,vmax,imax):
    one=port_response(d,volume,freq,rs,ls,cp)
    scales=np.array([np.full_like(np.asarray(freq,dtype=float),vmax),
        imax/abs(one['source_current']),d.xmax_mm*.001/(np.sqrt(2)*abs(one['x']))])
    source_voltage=np.min(scales,axis=0)
    return one,source_voltage,np.argmin(scales,axis=0)
