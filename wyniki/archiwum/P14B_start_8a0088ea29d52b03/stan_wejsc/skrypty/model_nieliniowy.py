"""P12/P13: pasywny model PM + współenergia + szczelny gaz idealny.

SI; x>0 na zewnątrz, Vgas=V0+Sd*x. Mms/Rms to efektywne parametry
odniesienia, BEZ nowego obciążenia promieniowaniem. Pole zewnętrzne jest
wyłącznie diagnostyczną normalizacją monopola4pi. Nie jest prognozą THD
egzemplarza. Wszystkie kształty wymagają jawnego pochodzenia w konfiguracji.
"""
from dataclasses import dataclass
import math
import numpy as np
from scipy.integrate import solve_ivp
from model_gazu import Medium


@dataclass(frozen=True)
class Plant:
    mass: float
    cms: float
    resistance: float
    bl0: float
    re: float
    le0: float
    sd: float
    xref: float

    def __post_init__(self):
        for key,value in vars(self).items():
            if not np.isfinite(value) or value<0 or (value==0 and key not in ['resistance','bl0','re','le0']):
                raise ValueError('Dodatnie parametry; Re/Rms/BL/Le mogą być zerem formalnej granicy')
        if self.le0==0 and self.re==0:raise ValueError('Le=Re=0 nie definiuje algebraicznego prądu')

    @classmethod
    def from_driver(cls,d):
        return cls(d.mms,d.cms,d.rms,d.bl,d.re_ohm,d.le_mh*1e-3,d.sd,d.xmax_mm*1e-3)


@dataclass(frozen=True)
class Shape:
    bl_asym: float=0.
    bl_decay: float=0.
    bl_fourth: float=0.
    k_asym: float=0.
    k_quad: float=0.
    k_fourth: float=0.
    l_asym: float=0.
    l_quad: float=0.
    leakage_fraction: float=.1
    saturation_a: float=np.inf
    r_velocity: float=0.
    velocity_reference_m_s: float=.5

    def __post_init__(self):
        for key,value in vars(self).items():
            if not np.isfinite(value) and not (key=='saturation_a' and np.isposinf(value)):
                raise ValueError('Skończone współczynniki; Is może być+inf')
        if min(self.bl_decay,self.bl_fourth,self.k_quad,self.k_fourth,self.r_velocity)<0 or self.velocity_reference_m_s<=0:
            raise ValueError('Niedopuszczalne współczynniki')
        # Fs=K0*x*(1+k1*q+k2*q²); dFs/dx=K0*(1+2*k1*q+3*k2*q²).
        if (self.k_quad==0 and self.k_asym!=0) or (self.k_quad>0 and self.k_asym**2>=3*self.k_quad):
            raise ValueError('Wymagana globalnie dodatnia styczna sztywność rodziny')
        if not 0<self.leakage_fraction<=1 or self.saturation_a<=0:
            raise ValueError('Dodatnia indukcyjność rozproszenia i prąd nasycenia')


def log_cosh(value):
    value=np.asarray(value,float);a=abs(value);out=np.empty_like(a)
    small=a<20
    out[small]=np.log1p(2*np.sinh(value[small]/2)**2)
    out[~small]=a[~small]-np.log(2)+np.log1p(np.exp(-2*a[~small]))
    return out


def u_minus_log1p(value):
    value=np.asarray(value,float);out=np.empty_like(value);small=abs(value)<1e-4
    u=value[small];out[small]=u*u*(.5+u*(-1/3+u*(.25+u*(-.2+u/6))))
    out[~small]=value[~small]-np.log1p(value[~small])
    return out


class NonlinearModel:
    def __init__(self,plant,volume_l,shape=Shape(),tau_s=np.inf,gas_nonlinear=True,medium=Medium(),q_domain=1.25):
        if not (volume_l>0 and (np.isfinite(volume_l) or np.isposinf(volume_l))):raise ValueError('Vb>0')
        if np.isnan(tau_s) or tau_s<0 or not np.isfinite(q_domain) or q_domain<=0:raise ValueError('tau>=0, dodatnia dziedzina')
        if medium.gamma<=1:raise ValueError('Bilans cieplny wymaga gamma>1')
        self.p=plant;self.shape=shape;self.medium=medium;self.volume=volume_l*1e-3
        self.eta=0. if np.isposinf(volume_l) else plant.sd*plant.xref/self.volume
        self.tau=tau_s;self.gas_nonlinear=gas_nonlinear;self.q_domain=q_domain
        self.has_current=plant.le0>0
        self.has_temperature=self.eta>0 and 0<tau_s<np.inf
        self.size=2+int(self.has_current)+int(self.has_temperature)
        self.it=2+int(self.has_current) if self.has_temperature else None

    def magnetic(self,q,current):
        p,h=self.p,self.shape;q=np.asarray(q);current=np.asarray(current)
        lp=p.le0*(1-h.leakage_fraction)*np.exp(h.l_asym*q+h.l_quad*q*q)
        lx=lp*(h.l_asym+2*h.l_quad*q)/p.xref
        leak=p.le0*h.leakage_fraction
        if np.isposinf(h.saturation_a):
            flux=(leak+lp)*current;ld=leak+lp;flux_x=lx*current
            force=.5*lx*current**2;coenergy=.5*(leak+lp)*current**2
        else:
            z=current/h.saturation_a;t=np.tanh(z)
            flux=leak*current+lp*h.saturation_a*t
            ld=leak+lp*(1-t*t);flux_x=lx*h.saturation_a*t
            coenergy=.5*leak*current**2+lp*h.saturation_a**2*log_cosh(z)
            force=lx*h.saturation_a**2*log_cosh(z)
        energy=current*flux-coenergy
        return dict(flux=flux,differential_l=ld,flux_x=flux_x,force=force,coenergy=coenergy,energy=energy)

    def gas(self,q,z=None):
        q=np.asarray(q,float);u=self.eta*q
        if not self.eta:return np.zeros_like(q),np.zeros_like(q),np.ones_like(q),np.zeros_like(q)
        if np.any(u<=-1):raise ValueError('Nie dodatnia objętość gazu')
        m=self.medium
        if self.tau==0:delta=np.zeros_like(q)
        elif np.isposinf(self.tau):
            delta=np.expm1((1-m.gamma)*np.log1p(u)) if self.gas_nonlinear else -(m.gamma-1)*u
        else:delta=self.eta*np.asarray(z)
        theta=1+delta
        if self.gas_nonlinear:
            pressure_delta=m.p0_pa*(delta-u)/(1+u)
            energy=m.p0_pa*self.volume*(u_minus_log1p(u)+u_minus_log1p(delta)/(m.gamma-1))
        else:
            pressure_delta=m.p0_pa*(delta-u)
            energy=.5*m.p0_pa*self.volume*(u*u+delta*delta/(m.gamma-1))
        dissipation=(m.p0_pa*self.volume/(m.gamma-1)/self.tau*delta**2/
                     (theta if self.gas_nonlinear else 1.)) if self.has_temperature else np.zeros_like(q)
        return pressure_delta,energy,theta,dissipation

    def scalar_rhs(self,phase,state,omega,voltage_peak,omit_reluctance=False):
        # Odrębna skalarna ścieżka dla wydajności ODE; funkcje wektorowe służą audytowi.
        p,h,m=self.p,self.shape,self.medium;q,vn=state[:2];v=omega*p.xref*vn
        bl=p.bl0*math.exp(h.bl_asym*q-h.bl_decay*q*q-h.bl_fourth*q**4)
        voltage=voltage_peak*math.sin(phase)
        current=state[2] if self.has_current else (voltage-bl*v)/p.re
        lp=p.le0*(1-h.leakage_fraction)*math.exp(h.l_asym*q+h.l_quad*q*q)
        lx=lp*(h.l_asym+2*h.l_quad*q)/p.xref
        if math.isinf(h.saturation_a):
            ld=p.le0*h.leakage_fraction+lp;flux_x=lx*current;rel=.5*lx*current*current
        else:
            a=current/h.saturation_a;t=math.tanh(a)
            lc=math.log1p(2*math.sinh(a/2)**2) if abs(a)<20 else abs(a)-math.log(2)+math.log1p(math.exp(-2*abs(a)))
            ld=p.le0*h.leakage_fraction+lp*(1-t*t)
            flux_x=lx*h.saturation_a*t;rel=lx*h.saturation_a**2*lc
        if omit_reluctance:rel=0.  # Celowy model błędny, wyłącznie audyt energii.
        ratio=max(1+self.eta*q,1e-12)  # Za dziedziną solver zatrzymuje zdarzenie.
        if self.tau==0:delta=0.
        elif math.isinf(self.tau):
            delta=math.expm1((1-m.gamma)*math.log(ratio)) if self.gas_nonlinear else -(m.gamma-1)*self.eta*q
        else:delta=self.eta*state[self.it] if self.has_temperature else 0.
        pressure=m.p0_pa*(delta-self.eta*q)/(ratio if self.gas_nonlinear else 1.)
        fs=p.xref/p.cms*q*(1+h.k_asym*q+h.k_quad*q*q+h.k_fourth*q**4)
        resistance=p.resistance*(1+h.r_velocity*(v/h.velocity_reference_m_s)**2)
        acc=(bl*current+rel-fs-resistance*v+p.sd*pressure)/p.mass
        dy=[vn,acc/(omega*omega*p.xref)]
        if self.has_current:dy.append((voltage-p.re*current-(bl+flux_x)*v)/(omega*ld))
        if self.has_temperature:
            theta=1+delta
            dy.append(-(m.gamma-1)*(theta/ratio if self.gas_nonlinear else 1.)*vn-state[self.it]/(omega*self.tau))
        return np.asarray(dy)

    def observables(self,phase,state,omega,voltage_peak):
        p,h=self.p,self.shape;q=state[0];x=p.xref*q;v=omega*p.xref*state[1]
        voltage=voltage_peak*np.sin(phase);bl=p.bl0*np.exp(h.bl_asym*q-h.bl_decay*q*q-h.bl_fourth*q**4)
        current=state[2] if self.has_current else (voltage-bl*v)/p.re
        mag=self.magnetic(q,current);pressure,gas_energy,theta,dheat=self.gas(q,state[self.it] if self.has_temperature else None)
        fs=x/p.cms*(1+h.k_asym*q+h.k_quad*q*q+h.k_fourth*q**4)
        potential=p.xref**2/p.cms*(q*q/2+h.k_asym*q**3/3+h.k_quad*q**4/4+h.k_fourth*q**6/6)
        rm=p.resistance*(1+h.r_velocity*(v/h.velocity_reference_m_s)**2)
        acc=(bl*current+mag['force']-fs-rm*v+p.sd*pressure)/p.mass
        energy=.5*p.mass*v*v+potential+mag['energy']+gas_energy
        return dict(x=x,v=v,current=current,voltage=voltage,acc=acc,energy=energy,
                    temperature_k=theta*self.medium.temperature_k,pressure_inside_delta_pa=pressure,
                    input_power=voltage*current,copper_power=p.re*current**2,
                    mechanical_loss=rm*v*v,thermal_exergy_loss=dheat,reluctance_force=mag['force'])


def simulate_sine(model,frequency_hz,vrms,cycles=16,max_cycles=64,samples_per_cycle=256,
                  rtol=2e-8,atol=2e-10,method='LSODA',closure_tolerance=2e-7,initial=None):
    if frequency_hz<=0 or vrms<0 or samples_per_cycle<64 or cycles<8:raise ValueError('Niepoprawny przebieg')
    omega=2*np.pi*frequency_hz;peak=np.sqrt(2)*vrms
    start=0.;state=np.zeros(model.size) if initial is None else np.asarray(initial,float)
    def rhs(t,y):return model.scalar_rhs(t,y,omega,peak)
    def domain(t,y):return min(model.q_domain-abs(y[0]),1+model.eta*y[0]-.05)
    domain.terminal=True;domain.direction=-1
    end_cycles=cycles;total_nfev=0;closure=np.inf
    current_scale=max(peak/max(model.p.re,1e-6),1.)
    scales=np.ones(model.size)
    if model.has_current:scales[2]=current_scale
    while True:
        end=2*np.pi*end_cycles
        sol=solve_ivp(rhs,[start,end],state,method=method,rtol=rtol,atol=atol*scales,
                      dense_output=True,max_step=2*np.pi/32,events=domain)
        total_nfev+=sol.nfev
        if not sol.success:raise RuntimeError(sol.message)
        if len(sol.t_events[0]):
            return dict(status='MODEL_DOMAIN_EXCEEDED',end_cycles=float(sol.t[-1]/(2*np.pi)),nfev=total_nfev,
                        x_fraction_at_stop=float(sol.y[0,-1]),closure_error=None)
        probe=np.linspace(end-2*np.pi,end,65)
        closure=float(np.max(abs((sol.sol(probe)-sol.sol(probe-2*np.pi))/scales[:,None])))
        if closure<=closure_tolerance or end_cycles>=max_cycles:break
        start=end;state=sol.y[:,-1];end_cycles=min(end_cycles+8,max_cycles)
    # W ostatnim segmencie jest >=8 cykli; analizujemy cztery pełne cykle.
    first=end-8*np.pi;n=4*samples_per_cycle
    phase=first+np.arange(n)*8*np.pi/n;y=sol.sol(phase)
    data=model.observables(phase,y,omega,peak)
    coeff=np.fft.rfft(data['x'])/n;fundamental=4
    h=np.arange(1,11)
    pressure_coeff=(-model.medium.rho*model.p.sd/(4*np.pi)*(h*omega)**2*
                    coeff[h*fundamental]*np.exp(-1j*h*omega/model.medium.c))
    harmonic=abs(pressure_coeff[1:])/max(abs(pressure_coeff[0]),1e-300)
    endpoints=sol.sol(np.array([first,end]));boundary=model.observables(np.array([first,end]),endpoints,omega,peak)
    mean_net=float(np.mean(data['input_power']-data['copper_power']-data['mechanical_loss']-data['thermal_exergy_loss']))
    delta_energy_rate=float((boundary['energy'][-1]-boundary['energy'][0])*omega/(end-first))
    energy_relative=abs(mean_net-delta_energy_rate)/max(float(np.mean(data['input_power'])),1.)
    result=dict(status='PERIODIC_WITHIN_MODEL_TOLERANCE' if closure<=closure_tolerance else 'NOT_SETTLED',
                end_cycles=end_cycles,nfev=total_nfev,closure_error=closure,
                x_peak_m=float(max(abs(data['x']))),x_dc_m=float(np.mean(data['x'])),
                current_rms_a=float(np.sqrt(np.mean(data['current']**2))),
                current_peak_a=float(max(abs(data['current']))),
                x_fundamental_peak_m=float(2*abs(coeff[fundamental])),
                spl_fundamental_equivalent_4pi_1m_db=float(20*np.log10(max(np.sqrt(2)*abs(pressure_coeff[0])/20e-6,1e-300))),
                h2_pressure_pct=float(100*harmonic[0]),h3_pressure_pct=float(100*harmonic[1]),
                thd_pressure_h2_h10_pct=float(100*np.linalg.norm(harmonic)),
                max_gas_temperature_k=float(max(data['temperature_k'])),
                mean_gas_temperature_k=float(np.mean(data['temperature_k'])),
                mean_input_w=float(np.mean(data['input_power'])),mean_copper_w=float(np.mean(data['copper_power'])),
                mean_mechanical_loss_w=float(np.mean(data['mechanical_loss'])),
                mean_thermal_exergy_loss_w=float(np.mean(data['thermal_exergy_loss'])),
                energy_relative_residual=float(energy_relative),
                volume_fraction_peak=float(model.eta*max(abs(y[0]))),
                pressure_phase_rad=float(np.angle(pressure_coeff[0])))
    return result
