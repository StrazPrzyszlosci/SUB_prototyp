"""P14B: projekcje stałego ruchu i oddzielny kontrolny ruchomy monopol.

Stałe geometrie NIE zmieniają ponownie obciążenia ruchu. MOVING jest
źródłem objętościowym w równaniu fali, nie rozwiązaniem całej membrany.
"""
import numpy as np
from scipy.interpolate import CubicSpline
from model_gazu import Medium
from model_promieniowania import piston_on_axis_pressure,piston_far_pressure,spherical_cap_field


def fixed_operators(plant,volume_l,frequencies,cfg,medium=Medium()):
    f=np.asarray(frequencies,float);s=2j*np.pi*f;r=cfg['distance_m']
    b=(3*volume_l*.001/(4*np.pi))**(1/3)+cfg['sphere_shell_offset_m']
    cap=np.zeros(len(f),complex);positive=f>0
    cap[positive]=spherical_cap_field(f[positive],plant.sd,b,b+r,[1.],cfg['sphere_terms'],medium)[0][:,0]
    return dict(MONOPOLE_4PI=medium.rho*s*plant.sd*np.exp(-s*r/medium.c)/(4*np.pi*r),
                BAFFLE_AXIS=piston_on_axis_pressure(f,plant.sd,r,medium),
                BAFFLE_60DEG_FAR=piston_far_pressure(f,plant.sd,r,np.pi/3,medium)[:,0],
                SPHERE_CAP_AXIS=cap)


def retarded_time(observer_times,position_velocity,r,mu,c,tolerance=1e-12,iterations=20,max_mach=.2):
    """t=tau+R(tau)/c, R=sqrt(r²+x²-2*r*x*mu), |v|/c<max_mach<1."""
    times=np.asarray(observer_times,float);tau=times-r/c;observed_mach=0.
    for k in range(iterations):
        x,v=position_velocity(tau);speed=abs(v)/c
        observed_mach=max(observed_mach,float(max(speed)))
        if observed_mach>=max_mach:raise ValueError('Poza przyjętą dziedziną prędkości kontrolnego źródła')
        distance=np.sqrt(r*r+x*x-2*r*x*mu)
        if np.any(distance<=0):raise ValueError('Źródło w punkcie obserwatora')
        new=times-distance/c
        error=float(max(abs(new-tau)));tau=new
        if error<=tolerance:break
    else:raise RuntimeError('Nie osiągnięto tolerancji czasu opóźnionego')
    x,v=position_velocity(tau);distance=np.sqrt(r*r+x*x-2*r*x*mu)
    toward_mach=v*(r*mu-x)/(c*distance)
    residual=float(max(abs(times-tau-distance/c)))
    return tau,distance,toward_mach,dict(iterations=k+1,max_observed_mach=observed_mach,
                                        max_retarded_residual_s=residual,min_distance_m=float(min(distance)))


def moving_monopole(x_rms,frequencies,sd,cfg,medium=Medium(),position_factor=1.,oversampling=None):
    """Psi=Q(tau)/[4pi*R*(1-Mr)], p=rho*dPsi/dt.

    Wynik dla modelu ciągłości (c^-2 dtt-Laplacian)Psi=Q(t)delta(x-z(t)).
    Pole jest liniowe w Q przy zadanym torze; tor zależny od ruchu czyni
    całą projekcję nieliniową. position_factor=0 jest kontrolą stałegoźródła.
    """
    f=np.asarray(frequencies,float);spacing=f[1]-f[0]
    window=1/spacing;count_base=int(round(window*5*4096))
    # Siatka wystarczająca dla pasma, niezależna od ustawień integratora.
    count_base=max(count_base,2**int(np.ceil(np.log2(16*len(f)))))
    factor=cfg['moving_source_oversampling'] if oversampling is None else oversampling
    n=int(count_base*factor);t=np.arange(n)*window/n
    coeff=np.asarray(x_rms,complex)/np.sqrt(2);coeff=coeff.copy();coeff[0]=x_rms[0]
    fft=np.zeros(n//2+1,complex);fft[:len(coeff)]=coeff*n
    x=np.fft.irfft(fft,n);times=np.r_[t,window]
    curve=CubicSpline(times,np.r_[x,x[0]],bc_type='periodic')
    # Maksimum pochodnej każdej części kwadratowej, a nie tylko próbek v.
    a,b,c=3*curve.c[0],2*curve.c[1],curve.c[2];dt=window/n
    candidates=[abs(c),abs(a*dt*dt+b*dt+c)]
    vertex=np.divide(-b,2*a,out=np.zeros_like(a),where=a!=0)
    inside=(a!=0)&(vertex>0)&(vertex<dt)
    candidates.append(np.where(inside,abs(a*vertex*vertex+b*vertex+c),0.))
    speed_bound=float(max(np.max(v) for v in candidates))*abs(position_factor)
    if speed_bound/medium.c>=cfg['moving_max_mach']:
        raise ValueError('Ciągła pochodna splajnu przekracza przyjętą dziedzinę Mach')
    # Wychylenie od węzła ograniczone przez całkę z osłony prędkości.
    position_bound=float(max(abs(x)))*abs(position_factor)+speed_bound*dt
    if position_bound>=cfg['distance_m']:raise ValueError('Tor źródła może osiągnąć obserwatora')
    def state(query):
        point=np.mod(query,window)
        return position_factor*curve(point),position_factor*curve(point,1)
    tau,distance,mach,diagnostic=retarded_time(t,state,cfg['distance_m'],1.,medium.c,
        cfg['retarded_time_tolerance_s'],cfg['retarded_time_max_iterations'],cfg['moving_max_mach'])
    volume_flow=sd*curve(np.mod(tau,window),1)  # Q nie skalujemy przez kontrolnyposition_factor.
    potential=volume_flow/(4*np.pi*distance*(1-mach))
    coef=np.fft.rfft(potential)/n;prms=np.sqrt(2)*coef[:len(f)]*medium.rho*2j*np.pi*f;prms[0]=0.
    diagnostic.update(source_samples=n,source_window_s=window,position_factor=position_factor,
                      spline_velocity_bound_m_s=speed_bound,spline_position_bound_m=position_bound,
                      scope='Kontrolny model ruchomego monopola, nie całe ruchome obciążenie membrany.')
    return prms,diagnostic


def mixing_products(frequencies):
    low,high=frequencies;result=[]
    for name,m,n in [('IM2_MINUS',-1,1),('IM2_PLUS',1,1),('IM3_DIFF_LOW',-2,1),
                     ('IM3_DIFF_HIGH',-1,2),('IM3_SUM_LOW',2,1),('IM3_SUM_HIGH',1,2)]:
        f=m*low+n*high
        if f<0:f=-f;m=-m;n=-n
        result.append((name,float(f),m,n))
    return result


def pressure_metrics(pressure,frequencies,case,dynamic_cfg):
    f=np.asarray(frequencies,float);p=np.asarray(pressure,complex);low,high=case['frequencies_hz']
    step=f[1]-f[0]
    def index(value):return int(round(value/step))
    fundamentals=np.array([index(low),index(high)]);denominator=float(np.linalg.norm(p[fundamentals]))
    if denominator==0:return dict(status='NO_FUNDAMENTAL_REFERENCE'),[]
    products=mixing_products(case['frequencies_hz']);lines=[];amplitudes={}
    for name,frequency,m,n in products:
        value=p[index(frequency)];ratio=float(abs(value)/denominator)
        referred=value/denominator*np.exp(-1j*(m*0.+n*case['phase2_rad']))
        visible=bool(ratio>dynamic_cfg['phase_relative_floor'])
        amplitudes[name]=abs(value)
        lines.append(dict(product=name,f_hz=frequency,order=abs(m)+abs(n),m=m,n=n,
                          pressure_real_pa=float(value.real),pressure_imag_pa=float(value.imag),
                          relative_to_fund_RSS_pct=100*ratio,phase_reference_real=float(referred.real),
                          phase_reference_imag=float(referred.imag),phase_visible=visible,
                          phase_referred_deg=float(np.angle(referred,deg=True)) if visible else None))
    band=(f>=dynamic_cfg['diagnostic_band_hz'][0])&(f<=dynamic_cfg['diagnostic_band_hz'][1]);band[fundamentals]=False
    im2=np.linalg.norm([amplitudes['IM2_MINUS'],amplitudes['IM2_PLUS']])
    im3diff=np.linalg.norm([amplitudes['IM3_DIFF_LOW'],amplitudes['IM3_DIFF_HIGH']])
    im3all=np.linalg.norm([amplitudes[n] for n in ['IM3_DIFF_LOW','IM3_DIFF_HIGH','IM3_SUM_LOW','IM3_SUM_HIGH']])
    row=dict(status='DEFINED_DIAGNOSTIC',fundamental_total_rms_pa=denominator,
             fundamental_total_SPL_rms_db=float(20*np.log10(denominator/20e-6)),
             IM2_pct=float(100*im2/denominator),IM3_difference_pct=float(100*im3diff/denominator),
             IM3_all_products_pct=float(100*im3all/denominator),
             noninput_band_pct=float(100*np.linalg.norm(p[band])/denominator))
    carrier=p[index(high)]
    if abs(carrier)<=denominator*dynamic_cfg['phase_relative_floor']:
        row['carrier_cluster_status']='CARRIER_BELOW_RELATIVE_FLOOR'
        return row,lines
    row['carrier_cluster_status']='CUSTOM_FIVE_LINE_DIAGNOSTIC_NOT_AN10_PROTOCOL'
    u=p[index(high+low)]/carrier;l=p[index(high-low)]/carrier
    row.update(first_sideband_AM_depth=float(abs(u+np.conj(l))),first_sideband_PM_index_rad=float(abs(u-np.conj(l))))
    theta=2*np.pi*np.arange(2048)/2048;envelope=np.ones(len(theta),complex);derivative=np.zeros_like(envelope)
    if high>2*low:
        for j in [-2,-1,1,2]:
            coefficient=p[index(high+j*low)]/carrier
            envelope+=coefficient*np.exp(1j*j*theta);derivative+=1j*j*coefficient*np.exp(1j*j*theta)
        absolute=abs(envelope);minimum=float(min(absolute));row['cluster_min_relative_envelope']=minimum
        if minimum>1e-8:
            fm=low*np.imag(derivative/envelope)
            row['cluster_AMD_rms_pct']=float(100*np.std(absolute)/np.mean(absolute))
            row['cluster_FM_rms_hz']=float(np.std(fm));row['cluster_envelope_valid']=True
        else:row['cluster_envelope_valid']=False
    return row,lines
