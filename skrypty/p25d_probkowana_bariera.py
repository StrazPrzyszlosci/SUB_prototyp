"""P25D: sample-and-hold energy limiter in a reduced 0D sealed box.
Numerical experiment, NOT a certified loudspeaker or miniDSP limiter.
Run: OPENBLAS_NUM_THREADS=1 python skrypty/p25d_probkowana_bariera.py
"""
from pathlib import Path
import csv, json, hashlib, platform
import numpy as np
import scipy
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'wyniki'
CFG = ROOT / 'dane/konfiguracje/p25d_probkowanie.json'
POOL = ROOT / 'dane/przetworniki/pula_rozszerzona.json'


def parameters(model, volume_l, rth, cth, t0, cfg):
    rho, c = cfg['rho_kg_m3'], cfg['sound_speed_m_s']
    sd = model['sd_cm2'] * 1e-4
    cms = model['vas_l'] * 1e-3 / (rho*c*c*sd*sd)
    w0 = 2*np.pi*model['fs_hz']
    mass = 1/(w0*w0*cms)
    rm = w0*mass/model['qms']
    bl = np.sqrt(w0*mass*model['re_ohm']/model['qes'])
    k = 1/cms + rho*c*c*sd**2/(volume_l*1e-3)
    le, re = model['le_mh']*1e-3, model['re_ohm']
    ilim = min(cfg['I_rail_peak_A'],
               np.sqrt(cfg['theta_limit_K'] /
                       (rth*re*(1+cfg['alpha_1_K']*cfg['theta_limit_K']))))
    xlim = cfg['fraction_Xmax']*model['xmax_mm']*1e-3
    ecap = min(k*xlim*xlim, le*ilim*ilim)/2
    return (k,mass,rm,bl,le,re,rth,cth,t0,ilim,xlim,ecap)


def signals(cfg):
    fs = cfg['integration_rate_hz']
    t = np.arange(int(cfg['duration_s']*fs)+1)/fs
    freqs = np.array([20,25,31,40,50,63,80,100], dtype=float)
    a = np.sqrt(20/freqs)
    aligned = np.sum(a[:,None]*np.sin(2*np.pi*freqs[:,None]*t),axis=0)
    sub = np.sin(2*np.pi*7*t)+.5*np.sin(2*np.pi*35*t) + \
          3*np.exp(-((t-.12)/.004)**2)
    wave = np.array([aligned,sub])
    wave /= np.sqrt(np.mean(wave**2,axis=1))[:,None]
    envelope = np.minimum(t/.02,1)
    envelope[t>cfg['duration_s']-.10] = 0
    wave *= envelope
    sos = np.vstack([butter(2,20,'high',fs=fs,output='sos'),
                     butter(2,80,'low',fs=fs,output='sos'),
                     butter(2,80,'low',fs=fs,output='sos')])
    return sosfilt(sos,wave,axis=1)*cfg['input_rms_V'], t


def run(cfg, controller_rate_hz, mode):
    fs = cfg['integration_rate_hz']
    assert fs%controller_rate_hz == 0
    steps = fs//controller_rate_hz
    h = 1/fs
    catalog = {v['model']['name']:v['model']
               for v in json.loads(POOL.read_text())['drivers']}
    cases, pars = [], []
    for name in cfg['candidates']:
        for therm in cfg['thermal_scenarios']:
            for vol in cfg['volume_l']:
                for wi, sig in enumerate(('multisine_aligned','subsonic_impulse')):
                    cases.append({'candidate':name,'thermal':therm[2],
                                  'volume_l':vol,'signal':sig,'mode':mode,
                                  'controller_rate_hz':controller_rate_hz})
                    pars.append(parameters(catalog[name],vol,*therm,cfg))
    (k,m,rm,bl,le,re,rth,cth,t0,ilim,xlim,ecap)=np.array(pars).T
    n=len(cases)
    x=np.zeros(n);v=np.zeros(n);i=np.zeros(n);theta=t0.copy()
    u=np.zeros(n);prior_u=np.zeros(n);prior_energy=np.zeros(n)
    max_energy=np.zeros(n);max_x=np.zeros(n);max_i=np.zeros(n)
    max_theta=theta.copy();max_u=np.zeros(n)
    wave,t=signals(cfg)
    wave_index=np.tile(np.array([0,1]),n//2)
    trace=[]
    for j in range(len(t)-1):
        if j%steps==0:
            command=np.clip(wave[wave_index,j],
                            -cfg['rail_peak_V'],cfg['rail_peak_V'])
            energy=(k*x*x+m*v*v+le*i*i)/2
            if mode=='rail':
                u=command
            elif mode=='sample_pointwise':
                resistance=re*(1+cfg['alpha_1_K']*theta)
                allowed=rm*v*v+resistance*i*i+ \
                        cfg['barrier_rate_per_s']*(ecap-energy)
                u=command.copy()
                mask=(u*i>allowed)&(abs(i)>1e-12)
                u[mask]=np.clip(allowed[mask]/i[mask],
                                -cfg['rail_peak_V'],cfg['rail_peak_V'])
            elif mode=='zoh_energy_bound':
                max_u_sample=np.sqrt(4*re*np.maximum(0.,ecap-energy)*
                                     controller_rate_hz)
                u=np.clip(command,-max_u_sample,max_u_sample)
            elif mode=='zoh_delayed_state':
                # At tk observe only the previous stored sample.
                # Bound present energy using the previous held voltage.
                upper = energy if j==0 else prior_energy+ \
                        prior_u*prior_u/(4*re*controller_rate_hz)
                max_u_sample=np.sqrt(4*re*np.maximum(0.,ecap-upper)*
                                     controller_rate_hz)
                new_u=np.clip(command,-max_u_sample,max_u_sample)
                prior_energy=energy.copy()
                prior_u=new_u.copy()
                u=new_u
            else:
                raise ValueError(mode)
        def rhs(X,V,I,T):
            resistance=re*(1+cfg['alpha_1_K']*T)
            return (V,(bl*I-rm*V-k*X)/m,
                    (u-resistance*I-bl*V)/le,
                    (resistance*I*I-T/rth)/cth)
        q1=rhs(x,v,i,theta)
        q2=rhs(x+.5*h*q1[0],v+.5*h*q1[1],
               i+.5*h*q1[2],theta+.5*h*q1[3])
        q3=rhs(x+.5*h*q2[0],v+.5*h*q2[1],
               i+.5*h*q2[2],theta+.5*h*q2[3])
        q4=rhs(x+h*q3[0],v+h*q3[1],
               i+h*q3[2],theta+h*q3[3])
        x+=h*(q1[0]+2*q2[0]+2*q3[0]+q4[0])/6
        v+=h*(q1[1]+2*q2[1]+2*q3[1]+q4[1])/6
        i+=h*(q1[2]+2*q2[2]+2*q3[2]+q4[2])/6
        theta+=h*(q1[3]+2*q2[3]+2*q3[3]+q4[3])/6
        energy=(k*x*x+m*v*v+le*i*i)/2
        max_energy=np.maximum(max_energy,energy/ecap)
        max_x=np.maximum(max_x,abs(x)/xlim)
        max_i=np.maximum(max_i,abs(i)/ilim)
        max_theta=np.maximum(max_theta,theta)
        max_u=np.maximum(max_u,abs(u))
        if (j+1)%(fs//200)==0:
            trace.append([float((j+1)/fs),float(x[0]/xlim[0]),
                          float(energy[0]/ecap[0]),float(u[0])])
    for row,E,X,I,T,U in zip(cases,max_energy,max_x,max_i,
                              max_theta,max_u):
        row.update(max_energy_fraction=float(E),max_x_fraction=float(X),
                   max_i_fraction=float(I),max_theta_K=float(T),
                   max_u_V=float(U),energy_violation=bool(E>1.00005),
                   x_violation=bool(X>1.00005),
                   i_violation=bool(I>1.00005))
    return cases, trace


def main():
    cfg=json.loads(CFG.read_text())
    OUT.mkdir(exist_ok=True)
    rows=[];traces={}
    for fs in cfg['controller_rates_hz']:
        for mode in cfg['modes']:
            subset,trace=run(cfg,fs,mode)
            rows.extend(subset)
            traces[f'{mode}_{fs}']=trace
    csv_path=OUT/'p25d_probkowanie.csv'
    with csv_path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    summary={'cases':len(rows),
             'scenarios':'C02 C11 C06; Vb=120l; cold/hot; 2 deterministic signals',
             'modes':{},'controller_hz':cfg['controller_rates_hz']}
    for mode in cfg['modes']:
        for fs in cfg['controller_rates_hz']:
            a=[r for r in rows if r['mode']==mode
               and r['controller_rate_hz']==fs]
            summary['modes'][f'{mode}_{fs}']={
                'n':len(a),
                'energy_violations':sum(r['energy_violation'] for r in a),
                'x_violations':sum(r['x_violation'] for r in a),
                'i_violations':sum(r['i_violation'] for r in a),
                'max_energy_fraction':max(r['max_energy_fraction'] for r in a),
                'max_x_fraction':max(r['max_x_fraction'] for r in a),
                'max_i_fraction':max(r['max_i_fraction'] for r in a)}
    sm=OUT/'p25d_podsumowanie.json'
    sm.write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    traces_path=OUT/'p25d_slady.json'
    traces_path.write_text(json.dumps(traces,ensure_ascii=False))
    paths=[CFG,POOL,Path(__file__),csv_path,sm,traces_path]
    manifest={'python':platform.python_version(),'numpy':np.__version__,
              'scipy':scipy.__version__,
              'files':{str(p.relative_to(ROOT)):
                       hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in paths}}
    (OUT/'p25d_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':
    main()
