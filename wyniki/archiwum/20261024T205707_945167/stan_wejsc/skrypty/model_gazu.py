"""P09/P10: pasywny gaz z relaksacją cieplną, przeciekiem i napędem.

SI, exp(+jwt), fazory RMS. Parametry mechaniczne przetwornika są zamrożone;
zmiana temperatury ośrodka nie rekonstruuje mechaniki z nowego Vas.
"""
from dataclasses import dataclass
import numpy as np
from model_subwoofera import RHO, C, P_REF


@dataclass(frozen=True)
class Medium:
    p0_pa: float = 101325.
    temperature_k: float = 293.15
    gamma: float = 1.4
    gas_constant_j_kg_k: float = 287.05
    viscosity_pa_s: float = 1.81e-5
    thermal_conductivity_w_m_k: float = 0.0257

    def __post_init__(self):
        for key, val in vars(self).items():
            if not np.isfinite(val) or val <= 0:
                raise ValueError(f'{key}: dodatnia skończona wartość')
        if self.gamma < 1:
            raise ValueError('gamma>=1')

    @property
    def rho(self):
        return self.p0_pa/(self.gas_constant_j_kg_k*self.temperature_k)

    @property
    def c(self):
        return np.sqrt(self.gamma*self.gas_constant_j_kg_k*self.temperature_k)

    @property
    def cp(self):
        if self.gamma == 1:
            raise ValueError('Cp nieokreślone dla formalnego końca gamma=1')
        return self.gamma*self.gas_constant_j_kg_k/(self.gamma-1)

    @classmethod
    def legacy(cls):
        gamma, r = 1.4, 287.05
        return cls(p0_pa=RHO*C*C/gamma, temperature_k=C*C/(gamma*r))


@dataclass(frozen=True)
class ThermalSpectrum:
    times_s: tuple = (0.005,)
    weights: tuple = (1.,)

    def __post_init__(self):
        t, w = np.asarray(self.times_s, float), np.asarray(self.weights, float)
        if t.ndim != 1 or not len(t) or t.shape != w.shape or np.any(np.isnan(t)) or np.any(t < 0):
            raise ValueError('Czasy relaksacji: nieujemne, dopuszczalne +inf')
        if np.any(~np.isfinite(w)) or np.any(w < 0) or not np.isclose(sum(w), 1., rtol=0., atol=1e-12):
            raise ValueError('Wagi nieujemne i o sumie1')

    def bulk_modulus(self, f_hz, medium=Medium()):
        f = np.asarray(f_hz, float)
        if not f.size or np.any(~np.isfinite(f)) or np.any(f < 0):
            raise ValueError('Nieujemne skończone częstotliwości')
        s = 2j*np.pi*f
        value = np.full_like(s, medium.p0_pa, dtype=complex)
        for tau, weight in zip(self.times_s, self.weights):
            if tau == 0:
                term = np.zeros_like(s)
            elif np.isposinf(tau):
                # Granica adiabatyczna z zamrożoną entropią także w DC.
                term = np.ones_like(s)
            else:
                term = s/(s+1/tau)
            value += medium.p0_pa*(medium.gamma-1)*weight*term
        return value

    def mechanical_parts(self, sd, vb_m3, medium):
        base = medium.p0_pa*sd*sd/vb_m3
        finite = []
        for tau, weight in zip(self.times_s, self.weights):
            dk = medium.p0_pa*(medium.gamma-1)*sd*sd/vb_m3*weight
            if np.isposinf(tau):
                base += dk
            elif tau > 0 and dk > 0:
                finite.append((tau, dk))
        return base, finite


def conductance_from_reference(leak_hz_ref, medium, reference_l=100.):
    if np.ndim(leak_hz_ref) or np.isnan(leak_hz_ref) or leak_hz_ref < 0:
        raise ValueError('Nieujemna częstotliwość przecieku, dopuszczalne +inf')
    if not np.isfinite(reference_l) or reference_l <= 0:
        raise ValueError('Dodatnia objętość odniesienia')
    return 2*np.pi*leak_hz_ref*reference_l*1e-3/(medium.gamma*medium.p0_pa)


def gas_response(d, vb_l, f_hz, spectrum=ThermalSpectrum(), medium=Medium(),
                 leak_hz_ref=0., vrms=1., extra_r_n_s_m=0., solid_angle=2*np.pi, distance_m=1.):
    f = np.asarray(f_hz, float)
    if (not f.size or np.any(~np.isfinite(f)) or np.any(f < 0)
            or not np.isfinite(vb_l) or vb_l <= 0
            or not np.isfinite(extra_r_n_s_m) or extra_r_n_s_m < 0
            or not np.isfinite(solid_angle) or solid_angle <= 0
            or not np.isfinite(distance_m) or distance_m <= 0
            or np.any(~np.isfinite(vrms)) or np.any(np.asarray(vrms) < 0)):
        raise ValueError('Niepoprawne wejścia gazu/napędu')
    f, voltage = np.broadcast_arrays(f, np.asarray(vrms, float))
    s = 2j*np.pi*f
    vb = vb_l*1e-3
    bulk = spectrum.bulk_modulus(f, medium)
    km = bulk*d.sd**2/vb
    g = conductance_from_reference(leak_hz_ref, medium)
    if g == 0:
        transfer = np.ones_like(s)
    elif np.isposinf(g):
        transfer = np.zeros_like(s)
    else:
        transfer = s/(s+g*km/(d.sd*d.sd))
    keff = km*transfer
    dynamic = d.mms*s*s+(d.rms+extra_r_n_s_m)*s+1/d.cms+keff
    den = (d.re_ohm+s*d.le_mh*1e-3)*dynamic+d.bl*d.bl*s
    x = d.bl*voltage/den
    current = dynamic*voltage/den
    velocity = s*x
    y = transfer*x
    force = km*y
    pi = -force/d.sd
    u_net = d.sd*s*y  # Stabilnie bez odejmowania prawie równych przepływów.
    u_mem = d.sd*velocity
    u_leak = u_net-u_mem
    pressure = medium.rho*s*u_net*np.exp(-s*distance_m/medium.c)/(solid_angle*distance_m)
    p_heat = np.zeros_like(f)
    _, finite = spectrum.mechanical_parts(d.sd, vb, medium)
    for tau, dk in finite:
        difference = y*s/(s+1/tau)
        p_heat += dk/tau*abs(difference)**2
    p_leak = np.zeros_like(f) if np.isposinf(g) else g*abs(pi)**2
    p_cu = d.re_ohm*abs(current)**2
    p_mech = (d.rms+extra_r_n_s_m)*abs(velocity)**2
    p_in = np.real(voltage*np.conj(current))
    spl = np.full_like(f, -np.inf)
    np.log10(abs(pressure)/P_REF, out=spl, where=abs(pressure)>0); spl *= 20
    return dict(x_complex_m=x, x_peak_m=np.sqrt(2)*abs(x), current_complex_a=current,
                i_rms_a=abs(current), velocity_complex_m_s=velocity, y_complex_m=y,
                bulk_modulus_pa=bulk, box_force_n=force, p_inside_pa=pi,
                u_net_m3_s=u_net, u_membrane_m3_s=u_mem, u_leak_m3_s=u_leak,
                pressure_equivalent_pa=pressure, spl_equivalent_db=spl,
                p_input_w=p_in, p_copper_w=p_cu, p_mechanical_w=p_mech,
                p_thermal_w=p_heat, p_leak_w=p_leak,
                energy_residual_w=p_in-p_cu-p_mech-p_heat-p_leak)


def gas_state(d, vb_l, spectrum, medium=Medium(), leak_hz_ref=0., extra_r_n_s_m=0.):
    """Minimalizacja końców tau=0/inf, Ra=0/inf i Le=0, zero offsetu gazu."""
    if not np.isfinite(vb_l) or vb_l <= 0 or not np.isfinite(extra_r_n_s_m) or extra_r_n_s_m < 0:
        raise ValueError('Niepoprawna objętość lub strata')
    g = conductance_from_reference(leak_hz_ref, medium)
    base, finite = spectrum.mechanical_parts(d.sd, vb_l*1e-3, medium)
    opened = np.isposinf(g)
    if opened:
        base, finite = 0., []
    names = (['i'] if d.le_mh > 0 else [])+['x', 'v']
    if g > 0 and not opened:
        names += ['y']
    names += [f'q{j}' for j in range(len(finite))]
    idx = {n:i for i, n in enumerate(names)}
    a, b = np.zeros((len(names), len(names))), np.zeros(len(names))
    a[idx['x'], idx['v']] = 1.
    iy = idx.get('y', idx['x'])
    force = np.zeros(len(names)); force[iy] = base+sum(dk for _, dk in finite)
    for j, (_, dk) in enumerate(finite):force[idx[f'q{j}']] = -dk
    iv = idx['v']
    a[iv] -= force/d.mms
    a[iv, idx['x']] -= 1/(d.cms*d.mms)
    a[iv, iv] -= (d.rms+extra_r_n_s_m)/d.mms
    if d.le_mh > 0:
        ii = idx['i']; le = d.le_mh*1e-3
        a[ii, ii], a[ii, iv], b[ii] = -d.re_ohm/le, -d.bl/le, 1/le
        a[iv, ii] += d.bl/d.mms
    else:
        a[iv, iv] -= d.bl*d.bl/(d.re_ohm*d.mms)
        b[iv] = d.bl/(d.re_ohm*d.mms)
    if 'y' in idx:
        a[iy, iv] = 1.
        a[iy] -= g/(d.sd*d.sd)*force
    for j, (tau, _) in enumerate(finite):
        iq = idx[f'q{j}']; a[iq, iy] = 1/tau; a[iq, iq] = -1/tau
    # E = 0.5*z^T W z; kontrola a^T W+W a niezależna od symulacji sinusów.
    w = np.zeros_like(a)
    if 'i' in idx:w[idx['i'], idx['i']] = d.le_mh*1e-3
    w[idx['x'], idx['x']] += 1/d.cms
    w[iv, iv] = d.mms
    if not opened:
        w[iy, iy] += base
        for j, (_, dk) in enumerate(finite):
            iq=idx[f'q{j}']; w[iy, iy]+=dk; w[iq, iq]+=dk
            w[iy, iq]-=dk; w[iq, iy]-=dk
    return a, b, idx, w
