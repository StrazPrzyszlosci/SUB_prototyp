"""Fizyczny stan cewki przy saturacji źródła;implicit midpoint z energią.

Model:Le*di/dt=u-(Re+Rs)*i-BL*v;M*dv/dt=BL*i-Rms*v-K*x.
Sterownik:u=clip(cmd-G*deadzone(i,Ithr),-rail,+rail).
G to wzmocnienie statyczne w ohm;nie twardy limiter stanu prądu.
"""
import numpy as np
from model_subwoofera import RHO,C


def linear_state(d,volume_l,rs):
    le=d.le_mh*.001
    if le<=0 or volume_l<=0 or rs<0:raise ValueError('Le>0,V>0,Rs>=0')
    stiffness=1/d.cms+RHO*C*C*d.sd*d.sd/(volume_l*.001)
    A=np.array([[0.,1.,0.],[-stiffness/d.mms,-d.rms/d.mms,d.bl/d.mms],
                [0.,-d.bl/le,-(d.re_ohm+rs)/le]])
    B=np.array([0.,0.,1/le]);P=np.array([stiffness,d.mms,le])
    return A,B,P


def midpoint_maps(A,B,h):
    eye=np.broadcast_to(np.eye(3),A.shape)
    inverse=np.linalg.inv(eye-h*A/2)
    feed=np.einsum('...ij,...j->...i',inverse,B)*h/2
    assert np.all(feed[...,2]>0)
    return inverse,feed


def current_feedback(i,threshold):
    return np.sign(i)*np.maximum(abs(i)-threshold,0.)


def midpoint_voltage(free_i,feed_i,command,gain,threshold,rail):
    # I_mid=free_i+feed_i*u. Rozwiązujemy ciągłe,piecewise-linear prawo
    # sprzężenia w środku kroku,zamiast opóźniać reakcję o pełny krok.
    at_command=free_i+feed_i*command
    positive=(command+gain*threshold-gain*free_i)/(1+gain*feed_i)
    negative=(command-gain*threshold-gain*free_i)/(1+gain*feed_i)
    unconstrained=np.where(at_command>threshold,positive,
        np.where(at_command < -threshold,negative,command))
    # Monotonia prawa sprzężenia gwarantuje,że przycięcie tego rozwiązania
    # do przedziału napięcia rozwiązuje również nasycone równanie skalarne.
    return np.clip(unconstrained,-rail,rail)


def command(t,kind,reference_rms,scale,ramp_s):
    ramp=np.sin(np.pi/2*min(max(t/ramp_s,0.),1.))**2
    if kind=='sine20':wave=np.sqrt(2)*np.sin(2*np.pi*20*t)
    elif kind=='sine80':wave=np.sqrt(2)*np.sin(2*np.pi*80*t)
    elif kind=='two20_85':wave=np.sin(2*np.pi*20*t)+np.sin(2*np.pi*85*t+.3)
    else:raise ValueError(kind)
    return reference_rms*scale*ramp*wave


def continuous_voltage(t,z,cfg,kind,scale,gain):
    cmd=command(t,kind,cfg['source_voltage_rms_reference_v'],scale,cfg['ramp_s'])
    return float(np.clip(cmd-gain*current_feedback(z[2],cfg['current_threshold_peak_a_assumed']),
        -cfg['source_rail_peak_v_assumed'],cfg['source_rail_peak_v_assumed']))
