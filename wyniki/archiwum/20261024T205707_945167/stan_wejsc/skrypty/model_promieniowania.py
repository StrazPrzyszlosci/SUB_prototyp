"""P11: spójne impedancje promieniowania i pola dla wzorcowych geometrii.

exp(+jwt), prędkości i ciśnienia RMS, mechaniczna impedancja F/v [N s/m].
Modele nie są geometrią rzeczywistego kosza ani wybraną skrzynią CNC.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import j1,struve
from scipy.special import dawsn
from model_gazu import Medium


def _frequency(f):
    f=np.atleast_1d(np.asarray(f,float))
    if f.ndim!=1 or not f.size or np.any(~np.isfinite(f)) or np.any(f<0):
        raise ValueError('Nieujemne skończone częstotliwości')
    return f


def _positive(x,name):
    if not np.isfinite(x) or x<=0:raise ValueError(f'{name}: dodatnia skończona liczba')
    return float(x)


def jinc(x):
    x=np.asarray(x,float);out=np.empty_like(x)
    small=abs(x)<1e-3;z=x[small]**2
    out[small]=1-z/8+z*z/192-z**3/9216+z**4/737280
    out[~small]=2*j1(x[~small])/x[~small]
    return out


def piston_impedance(f_hz,area_m2,medium=Medium()):
    f=_frequency(f_hz);area=_positive(area_m2,'Sd');radius=np.sqrt(area/np.pi)
    q=2*np.pi*f*radius/medium.c
    re=np.empty_like(q);im=np.empty_like(q);small=q<.01;x=q[small]
    re[small]=x*x/2-x**4/12+x**6/144-x**8/2880+x**10/86400
    im[small]=(8*x/3-32*x**3/45+128*x**5/1575-512*x**7/99225+2048*x**9/9823275)/np.pi
    z=q[~small]
    re[~small]=1-j1(2*z)/z
    im[~small]=struve(1,2*z)/z
    return medium.rho*medium.c*area*(re+1j*im)


def piston_added_mass_static(area_m2,medium=Medium()):
    radius=np.sqrt(_positive(area_m2,'Sd')/np.pi)
    return 8*medium.rho*radius**3/3


def piston_rayleigh_impedance(f_hz,area_m2,order=256,medium=Medium()):
    """Odrębna całka1D z pola nakładania dwóch dysków, bez Struve'a."""
    f=_frequency(f_hz);a=np.sqrt(_positive(area_m2,'Sd')/np.pi)
    nodes,weights=leggauss(order);r=a*(nodes+1);weights=weights*a
    overlap=2*a*a*np.arccos(r/(2*a))-.5*r*np.sqrt(np.maximum(4*a*a-r*r,0))
    s=2j*np.pi*f
    return medium.rho*s*(np.exp(-s[:,None]*r[None,:]/medium.c)@(weights*overlap))


def piston_on_axis_pressure(f_hz,area_m2,distance_m,medium=Medium()):
    """Dokładne p/v na osi, odległość od płaszczyzny tłoka, także z=0."""
    f=_frequency(f_hz);a=np.sqrt(_positive(area_m2,'Sd')/np.pi)
    if not np.isfinite(distance_m) or distance_m<0:raise ValueError('z>=0')
    delta=a*a/(np.sqrt(distance_m**2+a*a)+distance_m)
    s=2j*np.pi*f
    return -medium.rho*medium.c*np.exp(-s*distance_m/medium.c)*np.expm1(-s*delta/medium.c)


def piston_far_pressure(f_hz,area_m2,distance_m,theta_rad=0.,medium=Medium()):
    f=_frequency(f_hz);area=_positive(area_m2,'Sd');r=_positive(distance_m,'r')
    theta=np.atleast_1d(np.asarray(theta_rad,float))
    if np.any(~np.isfinite(theta)) or np.any((theta<0)|(theta>np.pi/2)):
        raise ValueError('Kąty w promieniującej półprzestrzeni')
    s=2j*np.pi*f;a=np.sqrt(area/np.pi)
    return medium.rho*s[:,None]*area*np.exp(-s[:,None]*r/medium.c)/(2*np.pi*r)*jinc(2*np.pi*f[:,None]*a/medium.c*np.sin(theta))


def disk_nodes(area_m2,radial_order=8,angular_order=64):
    area=_positive(area_m2,'Sd');a=np.sqrt(area/np.pi)
    x,w=leggauss(radial_order);radius=a*np.sqrt((x+1)/2)
    phi=2*np.pi*np.arange(angular_order)/angular_order
    pts=np.stack([(radius[:,None]*np.cos(phi)).ravel(),(radius[:,None]*np.sin(phi)).ravel()],axis=1)
    weights=np.repeat(w*area/(2*angular_order),angular_order)
    return pts,weights


def mutual_piston_impedance(f_hz,area_a,area_b,separation_m,radial_order=8,angular_order=64,medium=Medium()):
    """Dwa niepokrywające się tłoki w tej samej nieskończonej odgrodzie."""
    f=_frequency(f_hz);d=_positive(separation_m,'rozstaw')
    if d<=np.sqrt(area_a/np.pi)+np.sqrt(area_b/np.pi):
        raise ValueError('Dyski muszą być rozłączne; granica styczna wymaga innej kwadratury')
    a,wa=disk_nodes(area_a,radial_order,angular_order)
    b,wb=disk_nodes(area_b,radial_order,angular_order);b[:,0]+=d
    distance=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2).ravel()
    weight=(wa[:,None]*wb[None,:]).ravel()/distance
    out=np.empty(len(f),complex)
    for i,frequency in enumerate(f):
        s=2j*np.pi*frequency
        out[i]=medium.rho*s/(2*np.pi)*np.dot(np.exp(-s*distance/medium.c),weight)
    return out


def _legendre_coefficients(mu0,terms):
    p=np.empty(terms+2);p[0]=1.;p[1]=mu0
    for n in range(1,terms+1):p[n+1]=((2*n+1)*mu0*p[n]-n*p[n-1])/(n+1)
    coeff=np.empty(terms+1);coeff[0]=(1-mu0)/2
    coeff[1:]=.5*(p[:-2]-p[2:])
    return coeff


def _hankel_logarithmic(x,terms):
    """D_n=h_n'(x)/h_n(x), h_n^(2), bez obliczania ogromnych y_n."""
    x=np.atleast_1d(x)
    ratio=1/x+1j
    derivative=np.empty((len(x),terms+1),complex);derivative[:,0]=-ratio
    inverse_h=np.empty_like(derivative);inverse_h[:,0]=-1j*x*np.exp(1j*x)
    ratios=[]
    for n in range(1,terms+1):
        ratios.append(ratio)
        inverse_h[:,n]=inverse_h[:,n-1]/ratio
        ratio=(2*n+1)/x-1/ratio
        derivative[:,n]=n/x-ratio
    return derivative,inverse_h,ratios


def spherical_cap_impedance(f_hz,area_m2,body_radius_m,terms=512,medium=Medium()):
    f=_frequency(f_hz);area=_positive(area_m2,'powierzchnia czaszy');b=_positive(body_radius_m,'promień obudowy')
    if area>4*np.pi*b*b:raise ValueError('Czasza nie może mieć większej powierzchni niż sfera')
    if not isinstance(terms,int) or terms<1:raise ValueError('Dodatnia liczba wyrazów')
    mu0=1-area/(2*np.pi*b*b);coef=_legendre_coefficients(mu0,terms)
    result=np.zeros(len(f),complex);nonzero=f>0
    x=2*np.pi*f[nonzero]*b/medium.c
    derivative,_,_=_hankel_logarithmic(x,terms)
    n=np.arange(terms+1)
    result[nonzero]=-1j*4*np.pi*medium.rho*medium.c*b*b*np.sum(coef**2/((2*n+1)*derivative),axis=1)
    return result


def spherical_cap_added_mass_static(area_m2,body_radius_m,terms=2048,medium=Medium()):
    b=_positive(body_radius_m,'promień obudowy');area=_positive(area_m2,'powierzchnia')
    if area>4*np.pi*b*b:raise ValueError('Niepoprawna czasza')
    coef=_legendre_coefficients(1-area/(2*np.pi*b*b),terms);n=np.arange(terms+1)
    return 4*np.pi*medium.rho*b**3*np.sum(coef**2/((2*n+1)*(n+1)))


def spherical_cap_field(f_hz,area_m2,body_radius_m,observer_radius_m,mu,
                        terms=512,medium=Medium()):
    """Dokładne p/v_cap i v_radial/v_cap poza kontrolną sztywną sferą."""
    f=_frequency(f_hz);b=_positive(body_radius_m,'promień obudowy');r=_positive(observer_radius_m,'r')
    area=_positive(area_m2,'powierzchnia czaszy');mu=np.atleast_1d(np.asarray(mu,float))
    if r<=b or np.any(~np.isfinite(mu)) or np.any(abs(mu)>1) or np.any(f<=0) or area>4*np.pi*b*b:
        raise ValueError('Obserwator poza sferą, f>0, -1<=cos(theta)<=1')
    coeff=_legendre_coefficients(1-area/(2*np.pi*b*b),terms)
    x=2*np.pi*f*b/medium.c;y=2*np.pi*f*r/medium.c
    db,_,rb=_hankel_logarithmic(x,terms)
    dr,_,rr=_hankel_logarithmic(y,terms)
    relative=np.empty_like(db);relative[:,0]=b/r*np.exp(-1j*(y-x))
    for n in range(1,terms+1):relative[:,n]=relative[:,n-1]*rr[n-1]/rb[n-1]
    p=np.zeros((len(f),len(mu)),complex);v=np.zeros_like(p)
    pnm1=np.ones_like(mu);pn=mu.copy()
    for n in range(terms+1):
        if n==0:leg=pnm1
        elif n==1:leg=pn
        else:
            leg=((2*n-1)*mu*pn-(n-1)*pnm1)/n;pnm1,pn=pn,leg
        factor=coeff[n]*relative[:,n]/db[:,n]
        p+=(-1j*medium.rho*medium.c*factor)[:,None]*leg
        v+=(factor*dr[:,n])[:,None]*leg
    return p,v


def spherical_cavity_impedance(f_hz,area_m2,volume_m3,terms=512,medium=Medium(),bulk_modulus_pa=None):
    """Wewnętrzna komora sferyczna i radialna czasza; F_restoring/v.

    Część jednorodna ma podany K(s), reszta jest bezstratną akustyką
    adiabatyczną. Bez strat wyższe rezonanse mają bieguny na osi urojonej.
    """
    f=_frequency(f_hz);area=_positive(area_m2,'powierzchnia');volume=_positive(volume_m3,'objętość')
    if np.any(f<=0):raise ValueError('W DC komora ma biegun podatności; użyj granicy K/s')
    b=(3*volume/(4*np.pi))**(1/3)
    if area>4*np.pi*b*b:raise ValueError('Za duża czasza')
    coef=_legendre_coefficients(1-area/(2*np.pi*b*b),terms)
    x=2*np.pi*f*b/medium.c
    # Regularna funkcja j_n jest rozwiązaniem minimalnym: rekurencja w dół.
    ratios=np.empty((len(x),terms+1),float);ratio=np.zeros(len(x))
    for n in range(terms+80,-1,-1):
        ratio=1/((2*n+3)/x-ratio)
        if n<=terms:ratios[:,n]=ratio
    n=np.arange(terms+1)
    derivative=n[None,:]/x[:,None]-ratios
    remainder=np.sum(coef[1:]**2/((2*n[1:]+1)*derivative[:,1:]),axis=1)
    small=x<.1;z=x[small]
    remainder0=np.empty_like(x)
    remainder0[small]=z/5+z**3/175+2*z**5/7875+37*z**7/3031875+118*z**9/197071875
    remainder0[~small]=1/derivative[~small,0]+3/x[~small]
    remainder+=coef[0]**2*remainder0
    bulk=medium.gamma*medium.p0_pa if bulk_modulus_pa is None else np.asarray(bulk_modulus_pa,complex)
    return area*area*bulk/(2j*np.pi*f*volume)+1j*4*np.pi*medium.rho*medium.c*b*b*remainder


def gaussian_free_impedance(f_hz,area_m2,sigma_m,medium=Medium()):
    """4π, równy rozkład Gaussa źródła i odbioru; mechaniczna F/v.

    To wzorzec portu objętościowego dla P26, nie promień membrany.
    """
    f=_frequency(f_hz);area=_positive(area_m2,'Sd');sigma=_positive(sigma_m,'sigma')
    w=2*np.pi*f;t=w*sigma/medium.c
    acoustic_re=medium.rho*w*w/(4*np.pi*medium.c)*np.exp(-t*t)
    acoustic_im=medium.rho*w/(4*np.pi**1.5*sigma)*(1-2*t*dawsn(t))
    return area*area*(acoustic_re+1j*acoustic_im)
