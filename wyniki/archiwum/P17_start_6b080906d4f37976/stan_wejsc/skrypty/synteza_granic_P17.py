"""P17: ciągłe Vb, wspólne V/I i warunkowe chłodzenie przy stałym SPL.

u=1/Vb[1/m³]; wszystkie fazory elektryczne/akustyczne RMS.
Rozwiązanie analityczne warunkowych nierówności, nie certyfikat IV.
"""
from dataclasses import dataclass
import numpy as np
from model_gazu import Medium,ThermalSpectrum
from model_cewki_z_pamiecia import blocked_impedance


@dataclass(frozen=True)
class Interval:
    lower:float=0.
    upper:float=np.inf
    empty:bool=False

    def intersect(self,other):
        lo=max(self.lower,other.lower);hi=min(self.upper,other.upper)
        return Interval(lo,hi,self.empty or other.empty or hi<lo or hi<=0)

    def volume_l(self):
        if self.empty:return None,None
        return (0. if np.isposinf(self.upper) else 1000/self.upper,
                None if self.lower==0 else 1000/self.lower)


def complex_sublevel(offset,slope,limit):
    """|offset+slope*u|<=limit, u>=0. Granica u=0 oznacza V->inf."""
    if np.isnan(limit) or limit<0:raise ValueError('Nieujemny limit; +inf jest granicą bez ograniczenia')
    if np.isposinf(limit):return Interval()
    if slope==0:return Interval(empty=abs(offset)>limit)
    denominator=abs(slope)**2
    center=-np.real(offset*np.conj(slope))/denominator
    minimum=(np.imag(offset*np.conj(slope))/abs(slope))**2
    radius2=(limit*limit-minimum)/denominator
    if radius2<0:return Interval(empty=True)
    radius=np.sqrt(radius2)
    return Interval().intersect(Interval(float(center-radius),float(center+radius)))


def requirements(plant,f_hz,pressure_rms_pa,instant_h,branches,rise_k,alpha,distance_m=1.,tau_s=.005,medium=Medium()):
    if f_hz<=0 or pressure_rms_pa<0 or rise_k<0 or alpha<0 or distance_m<=0 or plant.bl0<=0:
        raise ValueError('f,r,BL>0; p,theta,alpha>=0; BL=0 nie pozwala zadać wymaganego ruchu przez prąd')
    w=2*np.pi*f_hz;s=1j*w
    bulk=ThermalSpectrum((tau_s,),(1.,)).bulk_modulus(np.array([f_hz]),medium)[0]
    h_pressure=medium.rho*s*plant.sd*np.exp(-s*distance_m/medium.c)/(4*np.pi*distance_m)
    velocity=pressure_rms_pa/h_pressure
    z0=plant.resistance+s*plant.mass+1/(s*plant.cms)
    z1=plant.sd**2*bulk/s
    i0=velocity*z0/plant.bl0;i1=velocity*z1/plant.bl0
    ratio=1+alpha*rise_k;re_hot=plant.re*ratio
    zb=blocked_impedance(np.array([f_hz]),re_hot,instant_h,branches)[0]
    red=blocked_impedance(np.array([f_hz]),plant.re,instant_h,branches)[0].real-plant.re
    return dict(f_hz=f_hz,velocity=velocity,x_required_peak_m=np.sqrt(2)*abs(velocity)/w,
                current_offset=i0,current_slope=i1,voltage_offset=zb*i0+plant.bl0*velocity,voltage_slope=zb*i1,
                Re_hot_ohm=re_hot,eddy_resistance_ohm=float(max(red,0.)),z0=z0,z1=z1,bulk_pa=bulk)


def feasible(requirement,plant,voltage_limit,current_limit,rise_k,thermal_Rth,eddy_factor=1.):
    if rise_k<0 or np.isnan(thermal_Rth) or thermal_Rth<0 or not 0<=eddy_factor<=1:raise ValueError('Nieujemne parametry testu cieplnego')
    if requirement['x_required_peak_m']>plant.xref:return Interval(empty=True),'CATALOGUE_X_REFERENCE_EXCEEDED'
    resistance= requirement['Re_hot_ohm']+eddy_factor*requirement['eddy_resistance_ohm']
    thermal_current=np.inf if thermal_Rth==0 or resistance==0 else np.sqrt(rise_k/(thermal_Rth*resistance))
    ilim=min(current_limit,thermal_current)
    current=complex_sublevel(requirement['current_offset'],requirement['current_slope'],ilim)
    voltage=complex_sublevel(requirement['voltage_offset'],requirement['voltage_slope'],voltage_limit)
    interval=current.intersect(voltage)
    return interval,('NO_POSITIVE_VOLUME_FOR_V_I_HEAT' if interval.empty else 'CONDITIONAL_INTERVAL')


def at_volume(requirement,volume_l,plant,rise_k,alpha):
    if np.isnan(volume_l) or volume_l<=0:raise ValueError('Vb>0; +inf tylko granicą matematyczną')
    u=1000/volume_l
    current=requirement['current_offset']+requirement['current_slope']*u
    voltage=requirement['voltage_offset']+requirement['voltage_slope']*u
    cold=abs(current)**2*plant.re;eddy=abs(current)**2*requirement['eddy_resistance_ohm']
    hot=cold*(1+alpha*rise_k)
    return dict(current_rms_a=float(abs(current)),voltage_rms_v=float(abs(voltage)),
        copper_at_allowed_rise_w=float(hot),eddy_w=float(eddy),
        Rth_max_all_heat_to_coil_k_w=float(rise_k/(hot+eddy)) if hot+eddy>0 else None,
        Rth_max_if_eddy_bypasses_coil_k_w=float(rise_k/hot) if hot>0 else None,
        Rth_current_feedback_critical_k_w=float(1/(alpha*cold)) if alpha*cold>0 else None)
