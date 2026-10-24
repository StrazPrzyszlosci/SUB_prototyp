"""P11: kalibracja referencji powietrznej i sprzężony liniowy napęd portów."""
from dataclasses import dataclass
import numpy as np
from model_promieniowania import piston_impedance,gaussian_free_impedance
from model_gazu import Medium


@dataclass(frozen=True)
class Motor:
    mass_kg: float
    compliance_m_n: float
    resistance_n_s_m: float
    bl_tm: float
    re_ohm: float
    le_h: float
    area_m2: float
    xmax_m: float

    def __post_init__(self):
        for k,v in vars(self).items():
            if not np.isfinite(v) or v<0 or (v==0 and k!='le_h'):
                raise ValueError(f'{k}: wymagane dodatnie wartości, Le>=0')


def reference_calibration(driver,faces=2.,reference='PISTON',sigma_m=.12,medium=Medium()):
    if not np.isfinite(faces) or faces<0:raise ValueError('Nieujemna liczba referencyjnych powierzchni')
    if reference=='PISTON':z=piston_impedance([driver.fs_hz],driver.sd,medium)[0]
    elif reference=='GAUSSIAN':z=gaussian_free_impedance([driver.fs_hz],driver.sd,sigma_m,medium)[0]
    else:raise ValueError('Nieznana referencja')
    ma=z.imag/(2*np.pi*driver.fs_hz);ra=z.real
    mass=driver.mms-faces*ma;resistance=driver.rms-faces*ra
    if mass<=0 or resistance<=0:
        raise ValueError('Odrzucona kalibracja: niedodatnia masa lub opór mechaniczny')
    motor=Motor(mass,driver.cms,resistance,driver.bl,driver.re_ohm,driver.le_mh*1e-3,driver.sd,driver.xmax_mm*1e-3)
    return motor,dict(reference=reference,faces=faces,reference_f_hz=driver.fs_hz,
                      subtracted_mass_kg=faces*ma,subtracted_resistance_n_s_m=faces*ra,
                      effective_remaining_mass_kg=mass,effective_remaining_resistance_n_s_m=resistance,
                      scope='DOPASOWANIE_REAKTANCJI_I_OPORU_W_FS_NIE_NIEZALEZNY_POMIAR_MMD')


def solve_motor_ports(f_hz,motors,rear_impedances,radiation_matrix,drive_vrms):
    f=np.atleast_1d(np.asarray(f_hz,float));n=len(motors)
    if np.any(~np.isfinite(f)) or np.any(f<=0) or not n:raise ValueError('Dodatnie częstotliwości i co najmniej1port')
    rear=np.broadcast_to(np.asarray(rear_impedances,complex),(len(f),n))
    radiation=np.asarray(radiation_matrix,complex)
    if radiation.shape!=(len(f),n,n) or np.any(~np.isfinite(radiation)) or np.any(~np.isfinite(rear)):
        raise ValueError('Niepoprawne impedancje')
    voltage=np.broadcast_to(np.asarray(drive_vrms,complex),(len(f),n))
    if np.any(~np.isfinite(voltage)):raise ValueError('Skończone napięcia')
    velocity=np.empty((len(f),n),complex);current=np.empty_like(velocity)
    for j,frequency in enumerate(f):
        s=2j*np.pi*frequency
        ze=np.array([m.re_ohm+s*m.le_h for m in motors])
        b=np.array([m.bl_tm for m in motors])
        diagonal=np.array([m.resistance_n_s_m+s*m.mass_kg+1/(s*m.compliance_m_n) for m in motors])+rear[j]+b*b/ze
        matrix=np.diag(diagonal)+radiation[j]
        velocity[j]=np.linalg.solve(matrix,b*voltage[j]/ze)
        current[j]=(voltage[j]-b*velocity[j])/ze
    pin=np.real(np.sum(voltage*np.conj(current),axis=1))
    copper=np.sum(abs(current)**2*np.array([m.re_ohm for m in motors]),axis=1)
    structural=np.sum(abs(velocity)**2*np.array([m.resistance_n_s_m for m in motors]),axis=1)
    rear_power=np.sum(rear.real*abs(velocity)**2,axis=1)
    radiation_power=np.real(np.einsum('fi,fij,fj->f',np.conj(velocity),radiation,velocity))
    return dict(velocity=velocity,current=current,voltage=voltage,
                x_peak_m=np.sqrt(2)*abs(velocity)/(2*np.pi*f[:,None]),
                input_w=pin,copper_w=copper,structural_w=structural,rear_w=rear_power,
                radiation_w=radiation_power,energy_residual_w=pin-copper-structural-rear_power-radiation_power)


def common_drive_envelope(result,motors,amp_vrms,amp_irms,x_fraction=1.):
    if not all(np.isfinite(x) and x>0 for x in [amp_vrms,amp_irms,x_fraction]):raise ValueError('Dodatnie ograniczenia')
    voltage=abs(result['voltage']);current=abs(result['current']);motion=result['x_peak_m']
    with np.errstate(divide='ignore'):
        limits=np.stack([np.min(amp_vrms/np.maximum(voltage,1e-300),axis=1),
                         np.min(amp_irms/np.maximum(current,1e-300),axis=1),
                         np.min(x_fraction*np.array([m.xmax_m for m in motors])[None,:]/np.maximum(motion,1e-300),axis=1)])
    return limits.min(axis=0),np.argmin(limits,axis=0)
