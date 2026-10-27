"""P22B:niezależne ciągłeODE,krokczasowy,monotonicznyroot i graniceenergii."""
from pathlib import Path
from itertools import product
import csv,hashlib,json,time
import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from analiza_rozszerzenia_SB import candidates
from analiza_nasycenia_i_pradu_P22B import specifications,simulate
from model_subwoofera import RHO,C
from model_nasycenia_P22B import midpoint_voltage

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    cfgp=ROOT/'dane/konfiguracje/p22b_nasycenie_i_prad.json';cfg=json.loads(cfgp.read_text());specs=specifications(cfg)
    with (OUT/'p22b_trajektorie.csv').open() as f:campaign=list(csv.DictReader(f))
    look={s['case_id']:s for s in specs};selected=[]
    for target in cfg['retained_wave_cases']:
        selected.append(next(s['case_id'] for s in specs if s['configuration']==target['configuration'] and s['volume_l']==target['volume_l'] and s['signal']==target['signal'] and s['scale']==target['scale'] and s['gain']==target['feedback_ohm']))
    for gain in [0.,10.]:
        family=[r for r in campaign if float(r['feedback_gain_ohm'])==gain]
        for field in ['x_to_catalog_reference','current_to_assumed_peak_threshold']:
            selected.append(max(family,key=lambda r:float(r[field]))['case_id'])
    selected=list(dict.fromkeys(selected));subset=[look[c] for c in selected]
    threshold,rail=cfg['current_threshold_peak_a_assumed'],cfg['source_rail_peak_v_assumed']
    refs={};continuous=[];start=time.monotonic()
    for spec in subset:
        d=spec['driver'];le=d.le_mh*.001;rs=cfg['source_series_resistance_ohm_assumed']
        K=1/d.cms+RHO*C*C*d.sd*d.sd/(spec['volume_l']*.001)
        def voltage(t,i):
            ramp=np.sin(np.pi*.5*np.clip(t/cfg['ramp_s'],0,1))**2
            if spec['signal']=='sine20':wave=np.sqrt(2)*np.sin(2*np.pi*20*t)
            elif spec['signal']=='sine80':wave=np.sqrt(2)*np.sin(2*np.pi*80*t)
            else:wave=np.sin(2*np.pi*20*t)+np.sin(2*np.pi*85*t+.3)
            cmd=cfg['source_voltage_rms_reference_v']*spec['scale']*ramp*wave
            return np.clip(cmd-spec['gain']*np.sign(i)*max(abs(i)-threshold,0.),-rail,rail)
        def rhs(t,z):
            x,v,i=z[:3];u=voltage(t,i)
            return [v,(d.bl*i-d.rms*v-K*x)/d.mms,(u-(d.re_ohm+rs)*i-d.bl*v)/le,
                u*i,d.re_ohm*i*i,rs*i*i,d.rms*v*v,max(-u*i,0.)]
        sol=solve_ivp(rhs,[0,cfg['duration_s']],np.zeros(8),method='LSODA',rtol=2e-10,
            atol=[1e-12,1e-10,1e-10,1e-10,1e-10,1e-10,1e-10,1e-10],max_step=1/(85*80),dense_output=True)
        assert sol.success,sol.message
        final=sol.y[:,-1];energy=.5*(K*final[0]**2+d.mms*final[1]**2+le*final[2]**2)
        residual=energy-final[3]+sum(final[4:7]);norm=max(energy+abs(final[3])+sum(final[4:7]),1e-20)
        assert abs(residual)/norm<2e-7
        refs[spec['case_id']]=sol
        continuous.append(dict(case_id=spec['case_id'],method='LSODA',function_calls=sol.nfev,
            stored_energy_j=energy,input_energy_j=float(final[3]),copper_heat_j=float(final[4]),
            returned_energy_j=float(final[7]),energy_relative_residual=float(abs(residual)/norm)))
        print('P22B continuous checked',spec['case_id'],sol.nfev,flush=True)
    grid=[];finest=[]
    for rate in cfg['verification_rates_hz']:
        rows,waves,stats=simulate(subset,cfg,rate,range(len(subset)))
        for k,spec in enumerate(subset):
            history=waves[k];reference=refs[spec['case_id']].sol(history[:,0])[:3].T
            delta=np.max(abs(history[:,3:6]-reference),axis=0)
            scales=np.array([spec['driver'].xmax_mm*.001,2*np.pi*80*spec['driver'].xmax_mm*.001,threshold])
            normalized=delta/scales
            row=dict(case_id=spec['case_id'],integration_rate_hz=rate,
                max_absolute_x_error_m=float(delta[0]),max_absolute_velocity_error_m_s=float(delta[1]),
                max_absolute_current_error_a=float(delta[2]),max_error_scaled_by_catalog_X_velocity80_and_Ithreshold=float(np.max(normalized)),
                energy_relative_residual=rows[k]['energy_relative_residual'],
                current_to_assumed_peak_threshold=rows[k]['current_to_assumed_peak_threshold'],
                x_to_catalog_reference=rows[k]['x_to_catalog_reference'])
            grid.append(row)
            if rate==cfg['integration_rate_hz']:finest.append(row)
        print('P22B rate verified',rate,flush=True)
    with (OUT/'p22b_zbieznosc_i_ciagle_ODE.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(grid[0]));w.writeheader();w.writerows(grid)
    # Odrębny skalar brentq:bez powielania zamkniętej postaci sterownika.
    rng=np.random.default_rng(22027);root_error=0.
    for a,b,gain,cmd in zip(rng.uniform(-50,50,100),10**rng.uniform(-5,0,100),rng.choice([0.,.1,10.,100.],100),rng.uniform(-200,200,100)):
        def F(u):
            i=a+b*u;dead=np.sign(i)*max(abs(i)-threshold,0.)
            return u-np.clip(cmd-gain*dead,-rail,rail)
        independent=brentq(F,-rail,rail,xtol=1e-12)
        own=float(midpoint_voltage(a,b,cmd,gain,threshold,rail));root_error=max(root_error,abs(own-independent))
    assert root_error<1e-9
    # Symboliczna tożsamość energii i diagnostyczna granica braku L-stabilności.
    a,b,p,h,lam=sp.symbols('a b p h lam',positive=True)
    assert sp.expand(p*(b*b-a*a)/2-p*(b-a)*(a+b)/2)==0
    assert sp.limit((1-lam*h/2)/(1+lam*h/2),lam,sp.oo)==-1
    gates=[]
    for cid,pid,d,cat in candidates():
        R=d.re_ohm+cfg['source_series_resistance_ohm_assumed'];velocity=2*np.pi*80*d.xmax_mm*.001
        margin=rail+R*threshold-abs(d.bl*velocity)
        gates.append(dict(configuration=cid,driver_name=d.name,f_kinematic_hz=80.,
            velocity_from_catalog_X_at80_m_s=velocity,back_emf_magnitude_v=d.bl*velocity,
            required_boundary_voltage_margin_v=margin,
            locally_feasible_at_opposed_current_boundary=margin>=0,
            critical_kinematic_frequency_hz=(rail+R*threshold)/(2*np.pi*d.bl*d.xmax_mm*.001),
            initial_kinetic_plus_inductor_energy_j=.5*d.mms*velocity**2+.5*d.le_mh*.001*threshold**2,
            interpretation='Kinematic state witness at x=0,i opposed to velocity;not proof this controller reaches it.'))
    with (OUT/'p22b_wykonalnosc_stanu_granicznego.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(gates[0]));w.writeheader();w.writerows(gates)
    flags=[r for r in finest if r['max_error_scaled_by_catalog_X_velocity80_and_Ithreshold']>.01]
    result=dict(status='COMPLETE_SCOPED_CONTINUOUS_SOURCE_CONTROLS' if not flags else 'OPEN_NUMERICAL_TIME_STEP_FLAGS',
        selected_continuous_cases=len(subset),continuous_controls=continuous,time_step_comparisons=len(grid),
        integration_rate_screen_hz=cfg['integration_rate_hz'],assumed_scaled_error_screen=.01,time_step_flags=flags,
        controller_root_checks=100,max_controller_root_error_v=root_error,kinematic_boundary_cases=len(gates),
        locally_infeasible_kinematic_cases=sum(not r['locally_feasible_at_opposed_current_boundary'] for r in gates),
        symbolic_identities=['quadratic energy discrete chain rule','implicit midpoint amplification tends to -1 in stiff damping limit'],
        elapsed_s=time.monotonic()-start,
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__).resolve(),cfgp,
            ROOT/'skrypty/model_nasycenia_P22B.py',ROOT/'skrypty/analiza_nasycenia_i_pradu_P22B.py',OUT/'p22b_trajektorie.csv']},
        limitations=['Selected continuous controls do not certify every point or a physical device.',
            'Implicit midpoint preserves the quadratic discrete energy identity but is not L-stable;do not claim a uniform Le->0 discretisation.',
            'Catalog-X/80Hz boundary states are local kinematic examples,not demonstrated reachable trajectories or measured overloads.',
            '1percent normalized state error is a numerical comparison screen,not a brief THD specification.'])
    (OUT/'p22b_kontrole_niezalezne.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P22B controls:',len(subset),'continuous;',len(grid),'steps;flags',len(flags),flush=True)


if __name__=='__main__':main()
