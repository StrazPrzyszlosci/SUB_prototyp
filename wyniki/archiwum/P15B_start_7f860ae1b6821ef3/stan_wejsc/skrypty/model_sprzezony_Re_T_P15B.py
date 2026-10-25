"""Wolna termika z quasistacjonarnym napędem; bez zmian dawnych modeli.

Re(theta) sprzęga się z prądem, ruchem, stratami i dodatnią siecią cieplną.
Nie identyfikuje chłodzenia ani nieliniowych krzywych produktów.
"""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from model_cewki_z_pamiecia import linear_memory_response,blocked_impedance
from model_gazu import Medium


@dataclass
class AveragedCoupledModel:
    plant:object
    volume_l:float
    frequencies:np.ndarray
    voltage_rms:np.ndarray
    instant_h:float
    branches:list
    thermal:object
    alpha_per_k:float
    eta_eddy_to_coil:float
    forced_g_per_velocity:float
    tau_gas_s:float=.005

    def __post_init__(self):
        self.frequencies=np.atleast_1d(np.asarray(self.frequencies,float));self.voltage_rms=np.asarray(self.voltage_rms,float)
        if self.frequencies.shape!=self.voltage_rms.shape or np.any(self.frequencies<=0) or np.any(self.voltage_rms<0):raise ValueError('Dodatnie f i nieujemne V, ten sam wymiar')
        if self.alpha_per_k<0 or not 0<=self.eta_eddy_to_coil<=1 or self.forced_g_per_velocity<0:raise ValueError('Nieujemne parametry termiki')
        cold=linear_memory_response(self.plant,self.volume_l,self.frequencies,self.instant_h,self.branches,tau_s=self.tau_gas_s)
        self.z_other=cold['z_input']-self.plant.re
        if np.any(self.z_other.real<-1e-10):raise ValueError('Wymagane bierne tło elektryczne')
        zb=blocked_impedance(self.frequencies,self.plant.re,self.instant_h,self.branches)
        self.eddy_resistance=np.maximum(zb.real-self.plant.re,0.)
        self.velocity_per_current=cold['velocity']/cold['current']
        self.cold=cold

    def response(self,temperature_rise_k,on=True):
        resistance=self.plant.re*(1+self.alpha_per_k*temperature_rise_k)
        if resistance<=0:raise ValueError('Re<=0 poza dziedziną modelu')
        current=(self.voltage_rms if on else np.zeros_like(self.voltage_rms))/(resistance+self.z_other)
        velocity=self.velocity_per_current*current
        current2=abs(current)**2;pcu=float(resistance*sum(current2));peddy=float(sum(self.eddy_resistance*current2))
        vrms=float(np.linalg.norm(velocity));gextra=self.forced_g_per_velocity*vrms
        pv=pcu+self.eta_eddy_to_coil*peddy;pm=(1-self.eta_eddy_to_coil)*peddy
        derivative=float(self.alpha_per_k*self.plant.re*sum(self.voltage_rms**2*(abs(self.z_other)**2-resistance**2)/abs(resistance+self.z_other)**4)) if on else 0.
        return dict(Re_ohm=float(resistance),current=current,velocity=velocity,pcu_w=pcu,peddy_w=peddy,
                    pv_w=pv,pm_w=pm,velocity_rms_m_s=vrms,extra_conductance_w_k=gextra,
                    pcu_slope_w_k=derivative,input_power_w=float(sum((resistance+self.z_other.real)*current2)))

    def rhs(self,t,state,on):
        tv,tm=state[:2];r=self.response(tv,on);g=self.thermal.conductance
        heat=np.array([r['pv_w'],r['pm_w']]);cooling=g@np.array([tv,tm])+np.array([r['extra_conductance_w_k']*tv,0.])
        derivative=(heat-cooling)/self.thermal.capacities
        environment=tv/self.thermal.coil_to_air_k_w+tm/self.thermal.magnet_to_air_k_w+r['extra_conductance_w_k']*tv
        return np.r_[derivative,sum(heat),environment]

    def equilibrium(self,maximum_rise_k):
        gv=1/self.thermal.coil_to_magnet_k_w;gm=1/self.thermal.magnet_to_air_k_w;ga=1/self.thermal.coil_to_air_k_w
        def residual(tv):
            r=self.response(tv);tm=(gv*tv+r['pm_w'])/(gv+gm)
            return r['pv_w']+gv*tm-(gv+ga+r['extra_conductance_w_k'])*tv
        if residual(maximum_rise_k)>=0:return dict(status='NO_ROOT_BRACKET_WITHIN_ANALYSIS_DOMAIN')
        tv=brentq(residual,0.,maximum_rise_k,xtol=1e-10,rtol=1e-12)
        r=self.response(tv);tm=(gv*tv+r['pm_w'])/(gv+gm)
        status='ROOT_WITHIN_ANALYSIS_DOMAIN' if max(tv,tm)<=maximum_rise_k else 'ROOT_MAGNET_OUTSIDE_ANALYSIS_DOMAIN'
        return dict(status=status,coil_rise_k=float(tv),magnet_rise_k=float(tm),residual_w=float(residual(tv)))


def simulate_thermal(model,on_intervals,cfg):
    end=cfg['end_s'];cuts=sorted({0.,float(end),*[float(x) for a in on_intervals for x in a]})
    if cuts[0]!=0 or cuts[-1]!=end:raise ValueError('Przedziały poza horyzontem')
    state=np.zeros(4);records=[];nfev=0;domain=False
    def event(t,y):return cfg['temperature_domain_rise_k']-max(y[:2])
    event.terminal=True;event.direction=-1
    for start,stop in zip(cuts[:-1],cuts[1:]):
        on=any(a<=.5*(start+stop)<b for a,b in on_intervals)
        fun=lambda t,y:model.rhs(t,y,on)
        result=solve_ivp(fun,[start,stop],state,rtol=cfg['rtol'],atol=np.array([cfg['atol_temperature_k']]*2+[1e-7]*2),
                         method='DOP853',dense_output=True,max_step=5.,events=event)
        nfev+=result.nfev
        if not result.success:raise RuntimeError(result.message)
        times=np.arange(start,result.t[-1]+cfg['sample_step_s']*.01,cfg['sample_step_s'])
        times=np.unique(np.r_[times,result.t[-1]])
        data=result.sol(times)
        for k,t in enumerate(times):
            r=model.response(data[0,k],on)
            stored=float(model.thermal.capacities@data[:2,k]);balance=float(stored-(data[2,k]-data[3,k]))
            records.append(dict(time_s=float(t),on=bool(on),coil_rise_k=float(data[0,k]),magnet_rise_k=float(data[1,k]),
                Re_ohm=r['Re_ohm'],pcu_w=r['pcu_w'],peddy_w=r['peddy_w'],velocity_rms_m_s=r['velocity_rms_m_s'],
                heat_in_j=float(data[2,k]),heat_out_j=float(data[3,k]),heat_balance_error_j=balance,
                current_rms_a=float(np.linalg.norm(r['current'])),
                motion_triangle_peak_m=float(np.sqrt(2)*sum(abs(r['velocity'])/(2*np.pi*model.frequencies)))))
        state=result.y[:,-1]
        if len(result.t_events[0]):domain=True;break
    return records,dict(status='THERMAL_DOMAIN_EXCEEDED' if domain else 'COMPLETED_CONDITIONAL_TRAJECTORY',nfev=nfev)
