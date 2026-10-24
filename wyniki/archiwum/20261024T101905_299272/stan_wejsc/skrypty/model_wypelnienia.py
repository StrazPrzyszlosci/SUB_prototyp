"""ZK: okrągłe proste pory, nieruchomy/wiotki szkielet i warstwy 1D.

Nie jest identyfikacją konkretnej włókniny. Ciśnienie wejściowe jest
uśrednione po przekroju; przestrzenne sprzężenie kosza pozostaje P21.
"""
from dataclasses import dataclass
import numpy as np
from scipy.special import jve
from scipy.optimize import nnls, minimize_scalar
from model_gazu import Medium, ThermalSpectrum, conductance_from_reference
from model_subwoofera import P_REF


def bessel_averages(z):
    """F=2J1(z)/(zJ0(z)) i 1-F, stabilnie przy z->0 i dużym Im(z)."""
    z = np.asarray(z, complex)
    if np.any(~np.isfinite(z)):
        raise ValueError('Skończony argument Bessela')
    f, complement = np.empty_like(z), np.empty_like(z)
    small = abs(z) < 0.05
    zz = z[small]**2
    series = zz/8+zz**2/48+11*zz**3/3072+19*zz**4/30720
    f[small], complement[small] = 1+series, -series
    x = z[~small]
    f[~small] = 2*jve(1, x)/(x*jve(0, x))
    complement[~small] = 1-f[~small]
    return f, complement


@dataclass(frozen=True)
class CircularPores:
    radius_m: float = 0.0002
    porosity: float = 0.98
    frame: str = 'rigid'
    dry_density_kg_m3: float = 20.

    def __post_init__(self):
        if not np.isfinite(self.radius_m) or self.radius_m <= 0:
            raise ValueError('Dodatni promień poru, nie promień włókna')
        if not np.isfinite(self.porosity) or not 0 < self.porosity <= 1:
            raise ValueError('Porowatość geometryczna musi należeć do (0,1]')
        if self.frame not in ['rigid', 'limp'] or not np.isfinite(self.dry_density_kg_m3) or self.dry_density_kg_m3 <= 0:
            raise ValueError('Nieruchomy lub wiotki szkielet z dodatnią gęstością')

    def flow_resistivity(self, medium=Medium()):
        return 8*medium.viscosity_pa_s/(self.porosity*self.radius_m**2)

    def equivalent_properties(self, f_hz, medium=Medium()):
        f = np.asarray(f_hz, float)
        if not f.size or np.any(~np.isfinite(f)) or np.any(f <= 0):
            raise ValueError('ZK wymaga dodatnich częstotliwości; DC przez granice')
        w = 2*np.pi*f
        viscous = self.radius_m*np.sqrt(-1j*w*medium.rho/medium.viscosity_pa_s)
        thermal = self.radius_m*np.sqrt(-1j*w*medium.rho*medium.cp/medium.thermal_conductivity_w_m_k)
        _, cv = bessel_averages(viscous)
        ft, _ = bessel_averages(thermal)
        rigid_density = medium.rho/(self.porosity*cv)
        bulk = medium.gamma*medium.p0_pa/(self.porosity*(1+(medium.gamma-1)*ft))
        if self.frame == 'limp':
            rho_av = self.dry_density_kg_m3+self.porosity*medium.rho
            # Postać stabilna także przy |rho_rigid|->inf w granicy niskich f.
            density = (rho_av-medium.rho**2/rigid_density)/(1+(rho_av-2*medium.rho)/rigid_density)
        else:
            density = rigid_density
        return density, bulk


def layer_impedance(f_hz, area_m2, layers, medium=Medium()):
    """Warstwy od portu do sztywnej tylnej ściany, Q przez cały przekrój.

    layers=[(grubość_m, CircularPores lub None)] — None oznacza powietrze
    adiabatyczne. Rekurencja tangensa unika przepełnienia macierzy transferu.
    """
    f = np.asarray(f_hz, float)
    if not f.size or np.any(~np.isfinite(f)) or np.any(f <= 0) or not np.isfinite(area_m2) or area_m2 <= 0:
        raise ValueError('Dodatnia częstotliwość i przekrój')
    prepared = []
    for depth, material in layers:
        if not np.isfinite(depth) or depth < 0 or (material is not None and not isinstance(material, CircularPores)):
            raise ValueError('Niepoprawna warstwa')
        if depth > 0:prepared.append((depth, material))
    if not prepared:
        raise ValueError('Co najmniej jedna warstwa o dodatniej grubości')
    load = None
    for depth, material in reversed(prepared):
        if material is None:
            rho = np.full_like(f, medium.rho, dtype=complex)
            bulk = np.full_like(f, medium.gamma*medium.p0_pa, dtype=complex)
        else:
            rho, bulk = material.equivalent_properties(f, medium)
        wave = 2*np.pi*f*np.sqrt(rho/bulk)
        characteristic = np.sqrt(rho*bulk)/area_m2
        tangent = np.tan(wave*depth)
        if load is None:
            load = -1j*characteristic/tangent
        else:
            load = (load+1j*characteristic*tangent)/(1+1j*load/characteristic*tangent)
    return load


def response_with_acoustic_impedance(d, f_hz, impedance_pa_s_m3, vrms=1.,
                                     medium=Medium(), leak_hz_ref=0.):
    f = np.asarray(f_hz, float)
    z = np.asarray(impedance_pa_s_m3, complex)
    if np.any(~np.isfinite(z)) or np.any(~np.isfinite(f)) or np.any(f <= 0) or np.any(~np.isfinite(vrms)) or np.any(np.asarray(vrms) < 0):
        raise ValueError('Skończona impedancja i napięcie, dodatnie częstotliwości')
    f, z, voltage = np.broadcast_arrays(f, z, np.asarray(vrms, float))
    s = 2j*np.pi*f
    g = conductance_from_reference(leak_hz_ref, medium)
    if np.isposinf(g):
        net_factor = np.zeros_like(z); loaded = np.zeros_like(z)
    else:
        net_factor = 1/(1+g*z); loaded = z*net_factor
    zm = d.rms+s*d.mms+1/(s*d.cms)+d.sd*d.sd*loaded
    ze = d.re_ohm+s*d.le_mh*1e-3
    current = voltage/(ze+d.bl*d.bl/zm)
    velocity = d.bl*current/zm
    net = d.sd*velocity*net_factor
    pressure_inside = -z*net
    external_pressure = medium.rho*s*net/(2*np.pi)
    p_in = np.real(voltage*np.conj(current))
    p_cu = d.re_ohm*abs(current)**2
    p_mech = d.rms*abs(velocity)**2
    p_porous = np.real(z)*abs(net)**2
    p_leak = np.zeros_like(f) if np.isposinf(g) else g*abs(pressure_inside)**2
    spl = np.full_like(f, -np.inf)
    np.log10(abs(external_pressure)/P_REF, out=spl, where=abs(external_pressure)>0);spl *= 20
    return dict(x_peak_m=np.sqrt(2)*abs(velocity)/(2*np.pi*f), i_rms_a=abs(current),
                current_complex_a=current, velocity_complex_m_s=velocity,
                spl_equivalent_db=spl,
                p_inside_pa=pressure_inside, p_input_w=p_in, p_copper_w=p_cu,
                p_mechanical_w=p_mech, p_porous_w=p_porous, p_leak_w=p_leak,
                energy_residual_w=p_in-p_cu-p_mech-p_porous-p_leak)


def fit_thermal_spectrum(material, frequencies_hz, terms=16, medium=Medium()):
    f = np.asarray(frequencies_hz, float)
    _, bulk = material.equivalent_properties(f, medium)
    target = material.porosity*bulk
    scale = medium.p0_pa*(medium.gamma-1)
    thermal_diff = medium.thermal_conductivity_w_m_k/(medium.rho*medium.cp)
    characteristic = material.radius_m**2/thermal_diff
    def cost(log_tau):
        spec = ThermalSpectrum((float(np.exp(log_tau)),), (1.,))
        return np.linalg.norm((spec.bulk_modulus(f, medium)-target)/medium.p0_pa)**2
    if terms == 1:
        opt = minimize_scalar(cost, bounds=(np.log(characteristic*1e-4),np.log(characteristic*10)), method='bounded')
        spectrum = ThermalSpectrum((float(np.exp(opt.x)),), (1.,))
    else:
        taus = np.geomspace(characteristic*1e-4, characteristic*10, terms)
        s = 2j*np.pi*f[:, None]
        matrix = s/(s+1/taus[None, :])
        goal = (target-medium.p0_pa)/scale
        aa = np.vstack([matrix.real, matrix.imag, 1000*np.ones((1,terms))])
        bb = np.concatenate([goal.real, goal.imag, [1000.]])
        weights, _ = nnls(aa, bb, maxiter=terms*20)
        weights /= sum(weights)
        spectrum = ThermalSpectrum(tuple(taus), tuple(weights))
    predicted = spectrum.bulk_modulus(f, medium)
    error = np.max(abs(predicted-target)/abs(target))
    return spectrum, float(error)


def sorptive_impedance(f_hz, volume_l, filling_fraction, geometric_porosity,
                       apparent_porosity, relaxation_s, medium=Medium()):
    """Umowna pasywna rodzina sorpcji; nie identyfikacja granulek węgla.

    Wartość statyczna zgodna z równaniem11 Venegas2023. Widmo relaksacji
    jest założeniem. Nie dodajemy tu oporu przepływu ani jego masy.
    """
    f = np.asarray(f_hz, float)
    if np.any(~np.isfinite(f)) or np.any(f <= 0) or not np.isfinite(volume_l) or volume_l <= 0:
        raise ValueError('Dodatnie f i objętość')
    if not 0 <= filling_fraction <= 1 or not 0 < geometric_porosity <= 1 or not np.isfinite(apparent_porosity):
        raise ValueError('Niepoprawny udział lub porowatość')
    if np.isnan(relaxation_s) or relaxation_s < 0 or apparent_porosity < geometric_porosity/medium.gamma:
        raise ValueError('Rodzina wymaga dodatniej dodatkowej podatności i tau>=0')
    volume = volume_l*1e-3; q = filling_fraction
    fast = volume*((1-q)+q*geometric_porosity)/(medium.gamma*medium.p0_pa)
    slow = volume*((1-q)/medium.gamma+q*apparent_porosity)/medium.p0_pa
    s = 2j*np.pi*f
    relaxation = 0. if np.isposinf(relaxation_s) else 1/(1+s*relaxation_s)
    compliance = fast+(slow-fast)*relaxation
    return 1/(s*compliance)


def two_temperature_modulus(f_hz, volume_air_l, heat_capacity_ratio=10.,
                             gas_exchange_s=0.005, solid_to_environment_s=np.inf,
                             medium=Medium()):
    """Dwa bilanse cieplne dla gazu i wypełnienia o skończonym Cs/Cg.

    Wymuszenie: względne zwiększenie objętości o amplitudzie1. Jest to
    liniowa funkcja przenoszenia, nie fizyczny ruch100% objętości.
    """
    f = np.asarray(f_hz,float)
    if np.any(~np.isfinite(f)) or np.any(f <= 0) or not all(np.isfinite(x) and x > 0 for x in [volume_air_l,heat_capacity_ratio,gas_exchange_s]):
        raise ValueError('Dodatnie częstotliwości, objętość, stosunek Cp i czas wymiany')
    if np.isnan(solid_to_environment_s) or solid_to_environment_s <= 0:
        raise ValueError('Dodatni czas wymiany z otoczeniem, dopuszczalne +inf')
    if medium.gamma <= 1:raise ValueError('Model cieplny wymaga gamma>1')
    s = 2j*np.pi*f
    volume = volume_air_l*1e-3
    cg = medium.p0_pa*volume/((medium.gamma-1)*medium.temperature_k)
    cs = heat_capacity_ratio*cg
    hgs = cg/gas_exchange_s
    hs0 = 0. if np.isposinf(solid_to_environment_s) else cs/solid_to_environment_s
    if hs0 == 0:
        # Skracamy wspólne s; różnica Hgs² w wyznaczniku traciła cyfry przy f->0.
        denominator = cg*cs*s+hgs*(cg+cs)
        tg = -medium.p0_pa*volume*(cs*s+hgs)/denominator
        ts = -medium.p0_pa*volume*hgs/denominator
        difference = -medium.p0_pa*volume*cs*s/denominator
    else:
        det = cg*cs*s*s+s*(cg*(hgs+hs0)+cs*hgs)+hgs*hs0
        tg = -medium.p0_pa*volume*s*(cs*s+hgs+hs0)/det
        ts = -medium.p0_pa*volume*s*hgs/det
        difference = -medium.p0_pa*volume*s*(cs*s+hs0)/det
    modulus = medium.p0_pa-medium.p0_pa*tg/medium.temperature_k
    dissipation = (hgs*abs(difference)**2+hs0*abs(ts)**2)/medium.temperature_k
    return dict(bulk_modulus_pa=modulus, gas_temperature_per_strain_k=tg,
                solid_temperature_per_strain_k=ts,
                thermal_dissipation_per_rms_strain_w=dissipation,
                cg_j_k=cg, cs_j_k=cs, hgs_w_k=hgs, hs0_w_k=hs0)
