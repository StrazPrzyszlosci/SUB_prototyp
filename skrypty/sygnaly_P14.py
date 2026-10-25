"""Koherentne sygnały i jawne limity wspólne; żadnego sumowania limitówSPL."""
from dataclasses import dataclass
from math import gcd
import numpy as np


@dataclass(frozen=True)
class TonePair:
    frequencies_hz: tuple
    weights_rms: tuple=(1.,1.)
    phases_rad: tuple=(0.,0.)

    def __post_init__(self):
        if len(self.frequencies_hz)!=2 or len(set(self.frequencies_hz))!=2:raise ValueError('Dwa różne tony')
        if any(not np.isfinite(f) or f<=0 or int(f)!=f for f in self.frequencies_hz):raise ValueError('Ten protokół używa dodatnich całkowitychHz')
        if len(self.weights_rms)!=2 or any(not np.isfinite(v) or v<=0 for v in self.weights_rms):raise ValueError('Dodatnie wagiRMS')
        if len(self.phases_rad)!=2 or not np.all(np.isfinite(self.phases_rad)):raise ValueError('Dwie skończone fazy')

    @property
    def base_hz(self):return gcd(*(int(f) for f in self.frequencies_hz))

    @property
    def orders(self):return np.asarray(self.frequencies_hz,int)//self.base_hz

    def value(self,phase):
        phase=np.asarray(phase)
        return np.sqrt(2)*sum(w*np.cos(n*phase+p) for w,n,p in zip(self.weights_rms,self.orders,self.phases_rad))

    def phase_period_second_tone(self):return 2*np.pi/self.orders[0]


def sampled_peak_enclosure(phasors_rms,orders,samples=4096):
    """M_sample<=M_true<=M_sample+B2*(pi/N)^2/2 dla ustalonych współczynników.

    Dowód: w globalnym maksimum okresowej funkcji pochodna jest zerowa,
    najbliższa próbka odległa<=pi/N, |f''|<=sqrt(2)*sum(n²*|a_n|).
    Arytmetykafloat nie jest certyfikatem całej niepewności fizycznych wejść.
    """
    phase=2*np.pi*np.arange(samples)/samples
    waveform=np.sqrt(2)*np.real(sum(a*np.exp(1j*n*phase) for a,n in zip(phasors_rms,orders)))
    peak=float(max(abs(waveform)))
    remainder=float(.5*np.sqrt(2)*sum(n*n*abs(a) for a,n in zip(phasors_rms,orders))*(np.pi/samples)**2)
    # Szczyt próbki może już osiągać dokładną osłonę trójkątną (np.fazy0).
    # Minimum dwóch górnych osłon pozostaje górną osłoną, bez sztucznego nadmiaru.
    triangle=float(np.sqrt(2)*sum(abs(a) for a in phasors_rms))
    upper=max(peak,min(peak+remainder,triangle))
    return peak,upper,upper-peak


def mixing_collisions(frequencies_hz,order=3):
    f1,f2=frequencies_hz;lines={}
    for m in range(-order,order+1):
        for n in range(-order,order+1):
            if not 0<abs(m)+abs(n)<=order:continue
            frequency=m*f1+n*f2
            if frequency<=0:continue
            lines.setdefault(frequency,[]).append((m,n))
    return {int(f):pairs for f,pairs in lines.items() if len(pairs)>1}


def joint_reference(plant,pair,response,amp_vrms=40.,amp_arms=12.,samples=4096):
    weights=np.asarray(pair.weights_rms);angles=np.exp(1j*np.asarray(pair.phases_rad));orders=pair.orders
    voltage=weights*angles;current=response['current']*voltage
    displacement=response['velocity']/(2j*np.pi*np.array(pair.frequencies_hz))*voltage
    vp,vupper,verr=sampled_peak_enclosure(voltage,orders,samples)
    xp,xupper,xerr=sampled_peak_enclosure(displacement,orders,samples)
    vrms=float(np.linalg.norm(weights));irms=float(np.linalg.norm(current))
    separate=min(float(min(amp_vrms/weights)),float(min(amp_arms/(abs(response['current'])*weights))),
                 float(min(plant.xref/(response['x_peak_m']*weights))))
    joint=min(amp_vrms/vrms,np.sqrt(2)*amp_vrms/vupper,amp_arms/irms,plant.xref/xupper)
    triangle=min(amp_vrms/vrms,amp_vrms/sum(weights),amp_arms/irms,
                 plant.xref/(np.sqrt(2)*sum(abs(displacement))))
    assert triangle<=joint*(1+1e-12)
    return dict(scale_separate_sinusoid_limits=separate,scale_joint=joint,scale_phase_independent=triangle,
                change_from_separate_db=float(20*np.log10(joint/separate)),
                voltage_peak_per_scale=vp,voltage_peak_upper_per_scale=vupper,
                voltage_peak_sampling_allowance=verr,x_peak_per_scale=xp,
                x_peak_upper_per_scale=xupper,x_peak_sampling_allowance=xerr,
                voltage_rms_per_scale=vrms,current_rms_per_scale=irms)
