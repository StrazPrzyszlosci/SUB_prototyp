"""P20A: podatne panele zamkniętego wkładu, gaz wewnętrzny i przeciek.

Wszystkie mody zadanej siatki MITC; sześć aktywnych ścian w trzech parach.
Rodziny krawędzi nie zastępują rzeczywistej ramy3D i naroży modułu.
"""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import brentq
from model_plyty_MITC_P18 import PlateMaterial,RectangularPlate
from model_gazu import Medium


@dataclass
class PlatePort:
    plate:object
    K:object
    M:object
    eigenvalues:np.ndarray
    coupling:np.ndarray
    static_compliance:float
    peak_displacement_per_pa:float
    static_modal_relative_error:float
    bending_stress_per_pa:float
    edge_moment_per_pa:float


@lru_cache(maxsize=256)
def plate_port(a,b,h,boundary,n=10,E=2.1e9,nu=.3,density=730.):
    if a>b:a,b=b,a
    p=RectangularPlate(a,b,n,n,PlateMaterial(E,nu,density,h),boundary=boundary)
    values,vectors=eigh(p.K.toarray(),p.M.toarray());assert values.min()>0
    coupling=vectors.T@p.F;q=p.static();static=float(p.F@q)
    error=float(abs(np.sum(coupling**2/values)/static-1));assert error<1e-7
    return PlatePort(p,p.K,p.M,values,coupling,static,float(max(abs(p.transverse_displacements(q)))),error,p.peak_principal_bound(q),p.edge_moment_peak(q))


def tied_port(base,k,mrod,mpad,pad_side):
    p=base.plate;patch=p.patch_average((p.a/2,p.b/2),(pad_side,pad_side))
    K,M=p.tied_pair(patch,k,mrod,'symmetric',mpad)
    values,vectors=eigh(K.toarray(),M.toarray());coupling=vectors.T@p.F
    q=p.static(K);static=float(p.F@q)
    error=float(abs(np.sum(coupling**2/values)/static-1));assert error<1e-7
    return PlatePort(p,K,M,values,coupling,static,float(max(abs(p.transverse_displacements(q)))),error,p.peak_principal_bound(q),p.edge_moment_peak(q))


class HollowModule:
    def __init__(self,outer,width,boundary,cfg,n=None,braced=False):
        self.outer=np.array(outer,float);self.wall=width;self.inside=self.outer-2*width
        if min(self.inside)<=0:raise ValueError('Dodatnie wymiary wewnętrzne wkładu')
        self.outer_volume=float(np.prod(self.outer));self.inner_volume=float(np.prod(self.inside))
        self.dry_mass=cfg['mdf_density_kg_m3_assumed']*(self.outer_volume-self.inner_volume)
        self.mass_with_sealed_air=self.dry_mass+Medium().rho*self.inner_volume
        self.boundary=boundary;self.zeta=cfg['plate_modal_damping_ratio_assumed'];self.faces=[]
        self.braced=braced;self.tie=None
        for normal in range(3):
            other=[i for i in range(3) if i!=normal]
            p=plate_port(*sorted(self.inside[other]),width,boundary,cfg['plate_mesh_intervals'] if n is None else n,
                         cfg['mdf_E_pa_assumed'],cfg['mdf_nu_assumed'],cfg['mdf_density_kg_m3_assumed'])
            self.faces.append(p)
        if braced:
            axis=int(np.argmax([np.prod(np.delete(self.inside,k)) for k in range(3)]))
            t=cfg['internal_tie_reference'];E=cfg['mdf_E_pa_assumed'];rho=cfg['mdf_density_kg_m3_assumed']
            length=self.inside[axis]-2*t['pad_thickness_m'];assert length>0
            area=t['rod_area_m2'];padarea=t['pad_side_m']**2
            compliance=length/(E*area)+2*(t['pad_thickness_m']/(E*padarea)+t['glue_thickness_m']/(t['effective_glue_E_pa']*padarea))
            mrod=rho*area*length;mpad=rho*padarea*t['pad_thickness_m']
            self.faces[axis]=tied_port(self.faces[axis],1/compliance,mrod,mpad,t['pad_side_m'])
            occupied=area*length+2*padarea*t['pad_thickness_m'];self.inner_volume-=occupied
            self.dry_mass+=rho*occupied;self.mass_with_sealed_air=self.dry_mass+Medium().rho*self.inner_volume
            self.tie=dict(normal_axis=axis,stiffness_n_m=1/compliance,occupied_volume_m3=occupied,mass_kg=mrod+2*mpad)
        self.values=np.concatenate([p.eigenvalues for p in self.faces])
        self.a=np.sqrt(2)*np.concatenate([p.coupling for p in self.faces])
        self.chi_static=float(sum(2*p.static_compliance for p in self.faces))
        self.peak_w_per_pa=max(p.peak_displacement_per_pa for p in self.faces)

    def wall_compliance(self,f):
        w=2*np.pi*np.asarray(f,float)
        if np.any(w<=0):raise ValueError('f>0; DC liczone osobno')
        den=self.values[None,:]-w[:,None]**2+2j*self.zeta*np.sqrt(self.values)[None,:]*w[:,None]
        return np.sum(self.a[None,:]**2/den,axis=1)

    def port(self,f,kappa=1.4,leak_corner_hz=0.,medium=Medium()):
        if not np.isfinite(kappa) or kappa<=0 or np.isnan(leak_corner_hz) or leak_corner_hz<0:raise ValueError('Dodatnie kappa, nieujemny przeciek')
        f=np.asarray(f,float);s=2j*np.pi*f;chi=self.wall_compliance(f)
        ci=self.inner_volume/(kappa*medium.p0_pa)
        if np.isposinf(leak_corner_hz):
            pi=np.ones_like(s);g=np.inf
        else:
            g=2*np.pi*leak_corner_hz*ci
            pi=(g+s*chi)/(g+s*(chi+ci))
        difference=1-pi;Y=s*ci*pi
        wall_loss=abs(difference)**2*np.real(s*chi)
        leak_loss=np.zeros_like(f) if np.isposinf(g) else g*abs(difference)**2
        residual=np.real(Y)-wall_loss-leak_loss
        return dict(admittance=Y,effective_compliance=Y/s,inside_to_outer_pressure=pi,
                    wall_loss_per_outer_pa2_w=wall_loss,leak_loss_per_outer_pa2_w=leak_loss,
                    power_residual_per_outer_pa2_w=residual,inner_compliance=ci,leak_conductance=g)

    def pressure_mode_frequency(self,kappa=1.4,medium=Medium()):
        """Pierwszy gazowo sprzężony mod portu w tej dyskretyzacji bez tłumienia.

        Zgrupowane zdegenerowane wartości, odrzucone wyłącznie śladowe
        sprzężenia <1e-12 całkowitej wagi portu. Nie wszystkie mody pudełka.
        """
        ci=self.inner_volume/(kappa*medium.p0_pa);order=np.argsort(self.values)
        groups=[]
        for value,weight in zip(self.values[order],self.a[order]**2):
            if groups and abs(value/groups[-1][0]-1)<1e-9:groups[-1][1]+=weight
            else:groups.append([float(value),float(weight)])
        active=[(v,w) for v,w in groups if w>np.sum(self.a**2)*1e-12]
        l1,l2=active[0][0],active[1][0]
        def equation(x):return 1+sum(w/(v-x) for v,w in active)/ci
        root=brentq(equation,l1+(l2-l1)*1e-10,l2-(l2-l1)*1e-10,xtol=1e-6)
        return float(np.sqrt(root)/(2*np.pi))

    def sealed_temperature_equilibrium(self,delta_T,delta_outer_pressure,medium=Medium()):
        """Idealny gaz stałej masy i liniowa statyczna podatność ścian.

        Ti jest zadanym rzeczywistym stanem temperatury, nie obliczeniem
        ogrzewania modułu od cewki. Dotyczy hermetycznego wkładu.
        """
        lam=self.chi_static*medium.p0_pa/self.inner_volume
        b=1+delta_outer_pressure/medium.p0_pa;t=1+delta_T/medium.temperature_k
        if min(b,t)<=0:raise ValueError('Dodatnia bezwzględna temperatura/ciśnienie')
        epsilon=2*lam*(t-b)/(1+lam*b+np.sqrt((1-lam*b)**2+4*lam*t))
        pressure_inside=medium.p0_pa*t/(1+epsilon)
        pressure_difference=pressure_inside-(medium.p0_pa+delta_outer_pressure)
        residual=epsilon*self.inner_volume-self.chi_static*pressure_difference
        return dict(relative_inner_volume_change=float(epsilon),pressure_difference_pa=float(pressure_difference),
                    peak_wall_deflection_m=float(abs(pressure_difference)*self.peak_w_per_pa),
                    w_over_t=float(abs(pressure_difference)*self.peak_w_per_pa/self.wall),
                    volume_equilibrium_residual_m3=float(residual))
