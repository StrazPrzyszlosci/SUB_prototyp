"""P10: szczelny idealny gaz z Newtonowską wymianą ciepła i zadanym V(t).

Nie jest modelem THD konkretnego głośnika. Ruch jest zadany; pełne sprzężenie
nieliniowego silnika/zawieszenia pozostaje P12/P13.
"""
import numpy as np
from scipy.integrate import solve_ivp
from model_gazu import Medium


def periodic_gas(epsilon, omega_tau, samples=4096, medium=Medium(),
                 adiabatic_mode='initial_entropy'):
    if not np.isfinite(epsilon) or not 0 <= epsilon < 1:
        raise ValueError('epsilon=Sd*X/V musi należeć do [0,1)')
    if np.isnan(omega_tau) or omega_tau < 0 or not isinstance(samples, int) or samples < 64 or samples % 2:
        raise ValueError('omega*tau>=0; parzysta siatka co najmniej64')
    if adiabatic_mode not in ['initial_entropy', 'periodic_limit']:
        raise ValueError('Nieznana granica entropii')
    phase = 2*np.pi*np.arange(samples)/samples
    volume_ratio = 1+epsilon*np.sin(phase)
    g = volume_ratio**(medium.gamma-1)
    if omega_tau == 0:
        normalized_temperature = np.ones(samples)
    elif np.isposinf(omega_tau):
        entropy_factor = 1. if adiabatic_mode == 'initial_entropy' else np.mean(g)
        normalized_temperature = entropy_factor/g
    else:
        orders = np.fft.fftfreq(samples, d=1/samples)
        z = np.fft.ifft(np.fft.fft(g)/(1+1j*orders*omega_tau)).real
        normalized_temperature = z/g
    temperature = medium.temperature_k*normalized_temperature
    pressure = medium.p0_pa*normalized_temperature/volume_ratio
    coeff = np.fft.rfft(pressure-medium.p0_pa)/samples
    h1 = 2*abs(coeff[1])
    harmonic_ratios = (abs(coeff[2:11])/abs(coeff[1])) if epsilon > 0 else np.zeros(9)
    return dict(phase=phase, volume_ratio=volume_ratio, temperature_k=temperature,
                pressure_pa=pressure, fourier_pressure_pa=coeff,
                fundamental_peak_pa=float(h1), pressure_dc_relative_pa=float(np.mean(pressure)-medium.p0_pa),
                h2_to_h1_pct=float(100*harmonic_ratios[0]),
                h3_to_h1_pct=float(100*harmonic_ratios[1]),
                thd_pressure_h2_h10_pct=float(100*np.linalg.norm(harmonic_ratios)),
                pressure_max_pa=float(max(pressure)), pressure_min_pa=float(min(pressure)),
                temperature_mean_k=float(np.mean(temperature)),
                temperature_max_k=float(max(temperature)),temperature_min_k=float(min(temperature)))


def periodic_gas_ode(epsilon, omega_tau, samples=1024, medium=Medium()):
    """Niezależne strzelanie okresowe dla Z=T/T0*(V/V0)^(gamma-1)."""
    if not 0 < omega_tau < np.inf or not 0 <= epsilon < 1:
        raise ValueError('Skończony dodatni czas i dodatnia objętość')
    def rhs(t, y):
        return ((1+epsilon*np.sin(t))**(medium.gamma-1)-y)/omega_tau
    settings = dict(method='Radau', rtol=2e-11, atol=1e-13, max_step=2*np.pi/256)
    particular = solve_ivp(rhs, [0., 2*np.pi], [0.], **settings)
    if not particular.success:raise RuntimeError(particular.message)
    z0 = particular.y[0, -1]/(-np.expm1(-2*np.pi/omega_tau))
    phase = 2*np.pi*np.arange(samples)/samples
    sol = solve_ivp(rhs,[0.,2*np.pi],[z0],t_eval=np.append(phase,2*np.pi), **settings)
    if not sol.success:raise RuntimeError(sol.message)
    temperature = sol.y[0, :-1]/(1+epsilon*np.sin(phase))**(medium.gamma-1)
    pressure = medium.p0_pa*temperature/(1+epsilon*np.sin(phase))
    return pressure, temperature*medium.temperature_k, float(abs(sol.y[0,-1]-z0))


def cycle_energy(epsilon, frequency_hz, volume_l, tau_s, medium=Medium(), samples=4096):
    if not all(np.isfinite(v) and v > 0 for v in [frequency_hz, volume_l]) or medium.gamma <= 1:
        raise ValueError('Dodatnie f,V i gamma>1')
    w = 2*np.pi*frequency_hz
    data = periodic_gas(epsilon, w*tau_s, samples, medium)
    volume = volume_l*1e-3
    vdot = volume*epsilon*w*np.cos(data['phase'])
    work = -np.mean((data['pressure_pa']-medium.p0_pa)*vdot)
    if tau_s in [0., np.inf]:
        heat = dissipation = 0.
    else:
        m_cv = medium.p0_pa*volume/((medium.gamma-1)*medium.temperature_k)
        h = m_cv/tau_s
        dt = data['temperature_k']-medium.temperature_k
        heat = h*np.mean(dt)
        dissipation = h*np.mean(dt*dt/data['temperature_k'])
    return dict(work_mean_w=float(work), heat_to_environment_mean_w=float(heat),
                exergy_dissipation_mean_w=float(dissipation),
                energy_residual_w=float(work-heat), exergy_residual_w=float(work-dissipation))


def static_offset(d, volume_l, new_temperature_k, external_pressure_pa, medium=Medium()):
    """Hermetyczna masa początkowa; sprężyna Cms pozostaje liniowa.

    Wynik poza Xmax sygnalizuje granicę tego modelu zawieszenia, nie prognozę
    fizycznego położenia po uderzeniu w ogranicznik.
    """
    if not all(np.isfinite(v) and v > 0 for v in [volume_l, new_temperature_k, external_pressure_pa]):
        raise ValueError('Dodatnia objętość, temperatura i ciśnienie')
    volume = volume_l*1e-3
    k = volume/(d.cms*d.sd*d.sd)
    b = k+external_pressure_pa
    c = external_pressure_pa-medium.p0_pa*new_temperature_k/medium.temperature_k
    disc = (k-external_pressure_pa)**2+4*k*medium.p0_pa*new_temperature_k/medium.temperature_k
    eps = -2*c/(b+np.sqrt(disc))
    x = volume*eps/d.sd
    return dict(x_bias_m=float(x), volume_ratio=float(1+eps),
                inside_pressure_pa=float(medium.p0_pa*new_temperature_k/medium.temperature_k/(1+eps)),
                fraction_of_catalog_xmax=float(abs(x)/(d.xmax_mm*1e-3)))
