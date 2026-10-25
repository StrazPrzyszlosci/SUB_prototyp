"""P14B: ogólny port V(theta), fazory i pełny bilans okresu; bez zmianyP14A."""
import math
import numpy as np
from scipy.integrate import solve_ivp,quad


def rms_spectrum(values):
    values=np.asarray(values,float);coef=np.fft.rfft(values)/len(values)
    phasors=np.sqrt(2)*coef;phasors[0]=coef[0]
    if len(values)%2==0:phasors[-1]=coef[-1]
    return phasors


def total_flux(model,state):
    q=state[0];p=model.p
    if not model.has_current:raise ValueError('Ten audyt wymaga jawnego stanu prądu')
    current=state[2];flux=float(model.magnetic(q,current)['flux'])
    if hasattr(model,'branches'):
        for k,b in enumerate(model.branches):
            a=np.exp(.5*(b.slope*q+b.curvature*q*q))
            flux+=b.inductance_h*a*state[model.base_size+k]
    return flux


def integrate_forcing(model,signal,scale,cfg,method='LSODA',initial_q=0.,refine=False):
    omega=2*np.pi*signal.base_hz
    def rhs(phase,state):return model.scalar_rhs(np.pi/2,state,omega,float(scale*signal.value(phase)))
    def observe(phase,state):return model.observables(np.full_like(phase,np.pi/2),state,omega,scale*signal.value(phase))
    def domain(phase,state):return min(model.q_domain-abs(state[0]),1+model.eta*state[0]-.05)
    domain.terminal=True;domain.direction=-1
    scale_states=np.ones(model.size)
    if model.has_current:scale_states[2]=max(scale*np.sqrt(2)*sum(signal.weights_rms)/model.p.re,1.)
    state=np.zeros(model.size);state[0]=initial_q;start=0.;cycles=cfg['initial_cycles'];nfev=0
    startup_x=abs(initial_q)*model.p.xref;startup_i=0.;startup_v=0.
    rtol=cfg['rtol'] if not refine else min(cfg['rtol'],2e-11)
    atol=cfg['atol'] if not refine else min(cfg['atol'],2e-13)
    closure_limit=cfg['closure_tolerance'] if not refine else min(cfg['closure_tolerance'],1e-9)
    maximum=cfg['maximum_cycles'] if not refine else max(cfg['maximum_cycles'],128)
    while True:
        end=2*np.pi*cycles
        sol=solve_ivp(rhs,[start,end],state,method=method,rtol=rtol,atol=atol*scale_states,
                      dense_output=True,max_step=2*np.pi/(32*max(signal.orders)),events=domain)
        nfev+=sol.nfev
        if not sol.success:raise RuntimeError(sol.message)
        # Ekstrema z węzłów adaptacyjnych i środków; nie globalny certyfikat ciągłego maksimum.
        probe_t=np.sort(np.r_[sol.t,.5*(sol.t[:-1]+sol.t[1:])]);probe=sol.sol(probe_t)
        startup_x=max(startup_x,float(max(abs(probe[0])))*model.p.xref)
        startup_v=max(startup_v,float(max(abs(probe[1])))*omega*model.p.xref)
        if model.has_current:startup_i=max(startup_i,float(max(abs(probe[2]))))
        if len(sol.t_events[0]):
            return dict(status='MODEL_DOMAIN_EXCEEDED',end_cycles=float(sol.t[-1]/(2*np.pi)),nfev=nfev,
                        startup_x_observed_m=startup_x,startup_current_peak_observed_a=startup_i,
                        startup_velocity_observed_m_s=startup_v),None
        times=np.linspace(end-2*np.pi,end,129)
        closure=float(np.max(abs((sol.sol(times)-sol.sol(times-2*np.pi))/scale_states[:,None])))
        if closure<closure_limit or cycles>=maximum:break
        start=end;state=sol.y[:,-1];cycles+=8
    spp=cfg['samples_per_period']*(2 if refine else 1);n=cfg['analysis_cycles']*spp
    first=end-cfg['analysis_cycles']*2*np.pi;phase=first+np.arange(n)*cfg['analysis_cycles']*2*np.pi/n
    data=observe(phase,sol.sol(phase));xs=rms_spectrum(data['x']);ispec=rms_spectrum(data['current'])
    f=np.fft.rfftfreq(n,d=1/(signal.base_hz*spp));keep=f<=cfg['stored_spectrum_max_hz']+1e-10
    arr=np.asarray([xs[keep],ispec[keep]],dtype='<c16')
    time_rms=float(np.sqrt(np.mean(data['current']**2)));spectral_rms=float(np.linalg.norm(ispec))
    boundary_t=np.array([first,end]);boundary_y=sol.sol(boundary_t);boundary=observe(boundary_t,boundary_y)
    net=np.mean(data['input_power']-data['copper_power']-data['mechanical_loss']-data['thermal_exergy_loss'])
    elapsed=(end-first)/omega;energy_change=(boundary['energy'][1]-boundary['energy'][0])/elapsed
    flux_change=(total_flux(model,boundary_y[:,1])-total_flux(model,boundary_y[:,0]))/elapsed
    p,h=model.p,model.shape
    xa,xb=p.xref*boundary_y[0]
    def bl(x):
        q=x/p.xref;return p.bl0*math.exp(h.bl_asym*q-h.bl_decay*q*q-h.bl_fourth*q**4)
    pm_change=quad(bl,xa,xb,epsabs=1e-15,epsrel=1e-10)[0]/elapsed
    electrical_mean_error=float(np.mean(data['voltage'])-p.re*np.mean(data['current'])-flux_change-pm_change)
    tail=~keep
    spacing=signal.base_hz/cfg['analysis_cycles'];ids=np.arange(len(f));off_grid=(ids%cfg['analysis_cycles'])!=0
    structural=data.get('structural_loss',data['mechanical_loss'])
    eddy=data.get('eddy_loss',np.zeros_like(data['current']))
    result=dict(status='PERIODIC_WITHIN_MODEL_TOLERANCE' if closure<closure_limit else 'NOT_SETTLED',
                end_cycles=cycles,closure_error=closure,nfev=nfev,frequency_spacing_hz=spacing,
                startup_x_observed_m=startup_x,startup_current_peak_observed_a=startup_i,
                startup_velocity_observed_m_s=startup_v,
                x_peak_sampled_m=float(max(abs(data['x']))),x_dc_m=float(np.mean(data['x'])),
                current_peak_sampled_a=float(max(abs(data['current']))),current_rms_a=time_rms,
                current_dc_a=float(np.mean(data['current'])),voltage_dc_v=float(np.mean(data['voltage'])),
                voltage_rms_v=float(np.sqrt(np.mean(data['voltage']**2))),voltage_peak_sampled_v=float(max(abs(data['voltage']))),
                mean_input_w=float(np.mean(data['input_power'])),mean_copper_w=float(np.mean(data['copper_power'])),
                mean_Rms_effective_loss_w=float(np.mean(structural)),mean_eddy_loss_w=float(np.mean(eddy)),
                mean_gas_exergy_loss_w=float(np.mean(data['thermal_exergy_loss'])),
                energy_relative_residual=float(abs(net-energy_change)/max(np.mean(data['input_power']),1.)),
                mean_voltage_identity_error_v=electrical_mean_error,
                current_Parseval_relative_error=float(abs(time_rms-spectral_rms)/max(time_rms,1e-30)),
                x_tail_RMS_ratio=float(np.linalg.norm(xs[tail])/max(np.linalg.norm(xs),1e-30)),
                current_tail_RMS_ratio=float(np.linalg.norm(ispec[tail])/max(spectral_rms,1e-30)),
                x_offgrid_RMS_ratio=float(np.linalg.norm(xs[off_grid])/max(np.linalg.norm(xs),1e-30)),
                temperature_gas_min_k=float(min(data['temperature_k'])),temperature_gas_max_k=float(max(data['temperature_k'])),
                volume_ratio_min_sampled=float(1+model.eta*min(sol.sol(phase)[0])),
                band_spectrum_shape=list(arr.shape))
    return result,arr
