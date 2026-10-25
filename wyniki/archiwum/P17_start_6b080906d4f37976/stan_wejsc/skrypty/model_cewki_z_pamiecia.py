"""P12C: dodatnia realizacja pamięci strumienia i kontrola naiwnego Foster.

Lgen=(Zblocked-Re)/s jest zespolone. Parametry nie są pomiarem produktu.
FROZEN x: obie realizacje mają ten sam Z; FLUX spełnia wzór18 Risbo2016.
NAIVE jest pasywną kontrolą błędnej interpretacji siły, nie kandydatem.
Mms/Rms pozostają efektywne, bez dodawania kolejny raz reakcji frontu.
"""
from dataclasses import dataclass,replace
import math
import numpy as np
from model_nieliniowy import NonlinearModel,Shape,simulate_sine
from model_gazu import Medium,ThermalSpectrum


@dataclass(frozen=True)
class FluxBranch:
    inductance_h: float
    tau_s: float
    slope: float=0.
    curvature: float=0.

    def __post_init__(self):
        if not np.isfinite(self.inductance_h) or self.inductance_h<=0:
            raise ValueError('Dodatnia indukcyjność gałęzi')
        if np.isnan(self.tau_s) or self.tau_s<=0:raise ValueError('tau>0; +inf jest granicą zamrożonego strumienia')
        if not np.isfinite(self.slope) or not np.isfinite(self.curvature):raise ValueError('Skończone współczynniki geometrii')


def generalized_inductance(f_hz,instant_h,branches,q=0.):
    f=np.asarray(f_hz,float)
    if np.any(~np.isfinite(f)) or np.any(f<0) or not np.isfinite(instant_h) or instant_h<0:
        raise ValueError('f>=0 i Linstant>=0')
    value=np.full(f.shape,instant_h,dtype=complex)
    for branch in branches:
        if np.isposinf(branch.tau_s):continue  # Najpierw tau->inf, zerowe stany początkowe.
        lj=branch.inductance_h*np.exp(branch.slope*q+branch.curvature*q*q)
        value+=lj/(1+2j*np.pi*f*branch.tau_s)
    return value


def blocked_impedance(f_hz,re_ohm,instant_h,branches,q=0.):
    f=np.asarray(f_hz,float)
    return re_ohm+2j*np.pi*f*generalized_inductance(f,instant_h,branches,q)


def calibrate_reference(plant,pole_hz,extra_resistance_fraction,descriptor='REAL_LGEN',reference_hz=1000.):
    """Jawna hipoteza znaczenia katalogowego Le i nieznanego Re(Zb)-Re.

    Nie jest pełnym dopasowaniem T/S. Przy zerowym prądzie, q=0.
    """
    if pole_hz<=0 or reference_hz<=0 or extra_resistance_fraction<0:
        raise ValueError('Dodatnie częstotliwości, nieujemna strata')
    if descriptor not in ['REAL_LGEN','ABS_LGEN']:raise ValueError('Nieznana definicja skalaru')
    omega=2*np.pi*reference_hz;tau=1/(2*np.pi*pole_hz)
    dr=extra_resistance_fraction*plant.re
    real_l=plant.le0
    if descriptor=='ABS_LGEN':
        if dr/omega>plant.le0:return None,'LOSS_EXCEEDS_MAGNITUDE_CONSTRAINT'
        real_l=np.sqrt(max(plant.le0**2-(dr/omega)**2,0.))
    dynamic_real=dr/(omega*omega*tau)
    instant=real_l-dynamic_real
    if instant<0:return None,'NEGATIVE_INSTANTANEOUS_INDUCTANCE'
    if dr==0:return (plant.le0,[]),'VALID'
    lj=dynamic_real*(1+(omega*tau)**2)
    return (float(instant),[FluxBranch(float(lj),float(tau))]),'VALID'


def linear_memory_response(plant,volume_l,f_hz,instant_h,branches,medium=Medium(),tau_s=.005):
    f=np.asarray(f_hz,float);s=2j*np.pi*f
    if np.any(f<=0) or volume_l<=0:raise ValueError('Dodatnie f,V')
    bulk=ThermalSpectrum((tau_s,),(1.,)).bulk_modulus(f,medium)
    zm=plant.resistance+s*plant.mass+1/(s*plant.cms)+plant.sd**2*bulk/(s*volume_l*.001)
    zb=blocked_impedance(f,plant.re,instant_h,branches)
    zin=zb+plant.bl0**2/zm
    current=1/zin;velocity=plant.bl0*current/zm
    x_peak=np.sqrt(2)*abs(velocity)/(2*np.pi*f)
    pressure=medium.rho*s*plant.sd*velocity*np.exp(-s/medium.c)/(4*np.pi)
    return dict(z_blocked=zb,z_input=zin,current=current,velocity=velocity,x_peak_m=x_peak,
                pressure_equivalent_pa=pressure,
                electrical_damping_at_f=np.real(plant.bl0**2/zb))


class MemoryModel(NonlinearModel):
    def __init__(self,plant,volume_l,instant_h,branches,shape=Shape(),tau_s=.005,
                 gas_nonlinear=True,medium=Medium(),q_domain=1.25,realization='FLUX'):
        if realization not in ['FLUX','NAIVE']:raise ValueError('FLUX lub kontrolaNAIVE')
        if not np.isfinite(instant_h) or instant_h<0:raise ValueError('Linstant>=0')
        super().__init__(replace(plant,le0=instant_h),volume_l,shape,tau_s,gas_nonlinear,medium,q_domain)
        self.base_size=self.size;self.branches=tuple(branches);self.size+=len(branches)
        self.realization=realization
        self.cycle_statistics=None

    def scalar_rhs(self,phase,state,omega,voltage_peak,omit_reluctance=False):
        p,h,m=self.p,self.shape,self.medium;q,vn=state[:2];v=omega*p.xref*vn
        bl=p.bl0*math.exp(h.bl_asym*q-h.bl_decay*q*q-h.bl_fourth*q**4)
        voltage=voltage_peak*math.sin(phase);j=state[self.base_size:]
        a=[math.exp(.5*(b.slope*q+b.curvature*q*q)) for b in self.branches]
        ax=[a[k]*(b.slope+2*b.curvature*q)/(2*p.xref) for k,b in enumerate(self.branches)]
        if self.has_current:current=state[2]
        elif self.realization=='FLUX':
            numerator=voltage-bl*v-sum(b.inductance_h*ax[k]*j[k]*v-b.inductance_h*a[k]*j[k]/b.tau_s for k,b in enumerate(self.branches))
            denominator=p.re+sum(b.inductance_h*a[k]**2/b.tau_s for k,b in enumerate(self.branches))
            current=numerator/denominator
        else:
            numerator=voltage-bl*v+sum(b.inductance_h*a[k]**2*j[k]/b.tau_s for k,b in enumerate(self.branches))
            denominator=p.re+sum(b.inductance_h*a[k]**2/b.tau_s for k,b in enumerate(self.branches))
            current=numerator/denominator
        lp=p.le0*(1-h.leakage_fraction)*math.exp(h.l_asym*q+h.l_quad*q*q)
        lx=lp*(h.l_asym+2*h.l_quad*q)/p.xref
        if math.isinf(h.saturation_a):
            ld=p.le0*h.leakage_fraction+lp;flux_x=lx*current;force=.5*lx*current*current
        else:
            z=current/h.saturation_a;t=math.tanh(z)
            lc=math.log1p(2*math.sinh(z/2)**2) if abs(z)<20 else abs(z)-math.log(2)+math.log1p(math.exp(-2*abs(z)))
            ld=p.le0*h.leakage_fraction+lp*(1-t*t);flux_x=lx*h.saturation_a*t
            force=lx*h.saturation_a**2*lc
        dj=[];branch_voltage=0.
        for k,b in enumerate(self.branches):
            if self.realization=='FLUX':
                derivative=(a[k]*current-j[k])/b.tau_s
                branch_voltage+=b.inductance_h*(a[k]*derivative+ax[k]*j[k]*v)
                force+=b.inductance_h*ax[k]*current*j[k]
            else:
                derivative=(current-j[k])/b.tau_s-2*ax[k]/a[k]*j[k]*v
                branch_voltage+=b.inductance_h*a[k]**2/b.tau_s*(current-j[k])
                force+=b.inductance_h*a[k]*ax[k]*j[k]**2
            dj.append(derivative)
        if omit_reluctance:force=0.
        ratio=max(1+self.eta*q,1e-12)
        if self.tau==0:delta=0.
        elif math.isinf(self.tau):delta=math.expm1((1-m.gamma)*math.log(ratio)) if self.gas_nonlinear else -(m.gamma-1)*self.eta*q
        else:delta=self.eta*state[self.it] if self.has_temperature else 0.
        pressure=m.p0_pa*(delta-self.eta*q)/(ratio if self.gas_nonlinear else 1.)
        fs=p.xref/p.cms*q*(1+h.k_asym*q+h.k_quad*q*q+h.k_fourth*q**4)
        rm=p.resistance*(1+h.r_velocity*(v/h.velocity_reference_m_s)**2)
        acc=(bl*current+force-fs-rm*v+p.sd*pressure)/p.mass
        dy=[vn,acc/(omega*omega*p.xref)]
        if self.has_current:dy.append((voltage-p.re*current-(bl+flux_x)*v-branch_voltage)/(omega*ld))
        if self.has_temperature:dy.append(-(m.gamma-1)*((1+delta)/ratio if self.gas_nonlinear else 1.)*vn-state[self.it]/(omega*self.tau))
        dy.extend(value/omega for value in dj)
        return np.asarray(dy)

    def observables(self,phase,state,omega,voltage_peak):
        p,h=self.p,self.shape;q=state[0];x=p.xref*q;v=omega*p.xref*state[1]
        voltage=voltage_peak*np.sin(phase);bl=p.bl0*np.exp(h.bl_asym*q-h.bl_decay*q*q-h.bl_fourth*q**4)
        j=state[self.base_size:]
        a=[np.exp(.5*(b.slope*q+b.curvature*q*q)) for b in self.branches]
        ax=[a[k]*(b.slope+2*b.curvature*q)/(2*p.xref) for k,b in enumerate(self.branches)]
        if self.has_current:current=state[2]
        elif self.realization=='FLUX':
            numerator=voltage-bl*v-sum(b.inductance_h*ax[k]*j[k]*v-b.inductance_h*a[k]*j[k]/b.tau_s for k,b in enumerate(self.branches))
            current=numerator/(p.re+sum(b.inductance_h*a[k]**2/b.tau_s for k,b in enumerate(self.branches)))
        else:
            numerator=voltage-bl*v+sum(b.inductance_h*a[k]**2*j[k]/b.tau_s for k,b in enumerate(self.branches))
            current=numerator/(p.re+sum(b.inductance_h*a[k]**2/b.tau_s for k,b in enumerate(self.branches)))
        mag=self.magnetic(q,current);pressure,gas_energy,theta,dheat=self.gas(q,state[self.it] if self.has_temperature else None)
        memory_energy=np.zeros_like(q);eddy_loss=np.zeros_like(q);rel=mag['force'].copy()
        for k,b in enumerate(self.branches):
            if self.realization=='FLUX':
                memory_energy+=.5*b.inductance_h*j[k]**2
                eddy_loss+=b.inductance_h/b.tau_s*(a[k]*current-j[k])**2
                rel+=b.inductance_h*ax[k]*current*j[k]
            else:
                memory_energy+=.5*b.inductance_h*a[k]**2*j[k]**2
                eddy_loss+=b.inductance_h*a[k]**2/b.tau_s*(current-j[k])**2
                rel+=b.inductance_h*a[k]*ax[k]*j[k]**2
        fs=x/p.cms*(1+h.k_asym*q+h.k_quad*q*q+h.k_fourth*q**4)
        potential=p.xref**2/p.cms*(q*q/2+h.k_asym*q**3/3+h.k_quad*q**4/4+h.k_fourth*q**6/6)
        rm=p.resistance*(1+h.r_velocity*(v/h.velocity_reference_m_s)**2)
        acc=(bl*current+rel-fs-rm*v+p.sd*pressure)/p.mass
        if np.size(q)>2:
            self.cycle_statistics=dict(mean_eddy_loss_w=float(np.mean(eddy_loss)),
                                       mean_structural_loss_w=float(np.mean(rm*v*v)),
                                       max_memory_energy_j=float(np.max(memory_energy)))
        # Interfejs integratora sumuje tę pozycję w bilansie; wrapper rozdziela nazwy strat.
        return dict(x=x,v=v,current=current,voltage=voltage,acc=acc,
                    energy=.5*p.mass*v*v+potential+mag['energy']+memory_energy+gas_energy,
                    temperature_k=theta*self.medium.temperature_k,pressure_inside_delta_pa=pressure,
                    input_power=voltage*current,copper_power=p.re*current**2,
                    mechanical_loss=rm*v*v+eddy_loss,thermal_exergy_loss=dheat,
                    structural_loss=rm*v*v,eddy_loss=eddy_loss,memory_energy=memory_energy,
                    reluctance_force=rel)


def simulate_memory_sine(model,*args,**kwargs):
    model.cycle_statistics=None
    result=simulate_sine(model,*args,**kwargs)
    if model.cycle_statistics is not None:
        result['mean_structural_plus_eddy_loss_w']=result.pop('mean_mechanical_loss_w')
        result.update(model.cycle_statistics)
    return result
