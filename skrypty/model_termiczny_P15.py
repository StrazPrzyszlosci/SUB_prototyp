"""P15A: fizyczna sieć dwóch skupionych mas i równoważny port Foster.

Temperatury są przyrostami względem stałego otoczenia[K]. C[J/K],R[K/W].
Parametry nie są danymi identyfikującymi którykolwiek produkt.
"""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import expm,eigh


@dataclass(frozen=True)
class ThermalCauer:
    coil_capacity_j_k:float
    magnet_capacity_j_k:float
    coil_to_magnet_k_w:float
    magnet_to_air_k_w:float
    coil_to_air_k_w:float=np.inf

    def __post_init__(self):
        for c in (self.coil_capacity_j_k,self.magnet_capacity_j_k):
            if not np.isfinite(c) or c<=0:raise ValueError('C>0, skończone')
        for r in (self.coil_to_magnet_k_w,self.magnet_to_air_k_w,self.coil_to_air_k_w):
            if np.isnan(r) or r<=0:raise ValueError('R>0; +inf oznacza brak ścieżki')

    @property
    def capacities(self):return np.array([self.coil_capacity_j_k,self.magnet_capacity_j_k])

    @property
    def conductance(self):
        gv=1/self.coil_to_magnet_k_w;gm=1/self.magnet_to_air_k_w;ga=1/self.coil_to_air_k_w
        return np.array([[gv+ga,-gv],[-gv,gv+gm]])

    @property
    def state_matrix(self):return -self.conductance/self.capacities[:,None]

    def steady(self,powers):return np.linalg.solve(self.conductance,np.asarray(powers,float))

    def step(self,times,powers,initial=(0.,0.)):
        t=np.atleast_1d(np.asarray(times,float));power=np.asarray(powers,float)
        if np.any(t<0) or power.shape!=(2,):raise ValueError('t>=0, dwa źródła mocy[W]')
        augmented=np.zeros((3,3));augmented[:2,:2]=self.state_matrix;augmented[:2,2]=power/self.capacities
        state=np.r_[np.asarray(initial,float),1.]
        return np.array([(expm(augmented*value)@state)[:2] for value in t])

    def impedance(self,s):
        return np.array([np.linalg.solve(self.conductance+value*np.diag(self.capacities),[1.,0.])[0] for value in np.atleast_1d(s)])

    def foster_port(self):
        """Port w cewce: Z=sum(Rk/(1+s*tauk)); ukryte stany NIE są Tmagnet."""
        cv=self.coil_capacity_j_k;inv=1/np.sqrt(self.capacities)
        decay,vectors=eigh(self.conductance*inv[:,None]*inv[None,:])
        if np.any(decay<=0):raise ValueError('Brak skończonego stanu ustalonego')
        impulse_weights=vectors[0]**2/cv
        if np.any(impulse_weights<=0):raise ValueError('Zredukować nieobserwowalną gałąź')
        return ThermalFoster(tuple(impulse_weights/decay),tuple(1/decay))

    def current_heating_stability(self,cold_copper_power_w,alpha_per_k):
        """Idealne utrzymanie I: Pcu=P0*(1+alpha*theta_coil), bez innych sprzężeń."""
        if cold_copper_power_w<0 or alpha_per_k<0:raise ValueError('P0,alpha>=0')
        g=self.conductance.copy();feedback=cold_copper_power_w*alpha_per_k;g[0,0]-=feedback
        inv=1/np.sqrt(self.capacities);values=eigh(g*inv[:,None]*inv[None,:],eigvals_only=True)
        return dict(feedback_w_k=feedback,dc_resistance_k_w=float(self.steady([1.,0.])[0]),
                    smallest_decay_per_s=float(min(values)),stable=bool(min(values)>0))


@dataclass(frozen=True)
class ThermalFoster:
    resistances_k_w:tuple
    time_constants_s:tuple

    def __post_init__(self):
        if len(self.resistances_k_w)!=len(self.time_constants_s) or not len(self.time_constants_s):raise ValueError('R,tau: ten sam dodatni wymiar')
        values=np.r_[self.resistances_k_w,self.time_constants_s]
        if np.any(~np.isfinite(values)) or np.any(values<=0):raise ValueError('Dodatnie skończone R,tau')

    @property
    def equivalent_capacities_j_k(self):return np.array(self.time_constants_s)/np.array(self.resistances_k_w)

    def impedance(self,s):
        s=np.atleast_1d(s)
        return np.sum(np.array(self.resistances_k_w)/(1+s[:,None]*np.array(self.time_constants_s)),axis=1)

    def step_states(self,times,power_w):
        t=np.atleast_1d(times)
        if np.any(t<0) or power_w<0:raise ValueError('t,P>=0')
        return power_w*np.array(self.resistances_k_w)*(-np.expm1(-t[:,None]/np.array(self.time_constants_s)))

    def step(self,times,power_w):return np.sum(self.step_states(times,power_w),axis=1)


def indistinguishable_cooling_family(cv,a,d_over_cm,b_squared_over_cm,b):
    """Jawna rodzina dodatnich Cauer o identycznym Z11(s).

    a=gvm+gva; D=(gvm+gma)/Cm; E=gvm²/Cm; swobodne b=gvm.
    Dziedzina E/D < b < a daje wszystkie trzy dodatnie przewodności.
    """
    D=d_over_cm;E=b_squared_over_cm
    if min(cv,a,D,E)<=0 or not E/D<b<a:raise ValueError('Wymagane Cv,a,D,E>0 oraz E/D<b<a')
    cm=b*b/E;gma=D*cm-b;gva=a-b
    return ThermalCauer(cv,cm,1/b,1/gma,1/gva)
