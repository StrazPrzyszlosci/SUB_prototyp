"""P25C: actual time integration; reversible additive research. SI internally.
Run OPENBLAS_NUM_THREADS=1 python skrypty/p25c_czas_ochrona.py
No added radiation mass: Mms effective from T/S as in existing baseline.
"""
from pathlib import Path
import json, hashlib, csv, platform
import numpy as np
import scipy
from scipy.signal import butter,sosfilt
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import RHO,C
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p25c_sygnaly_ochrona.json'

def setup(cfg):
    pool={i:d for i,p,d,c in candidates()}; rows=[];pars=[]
    for cid in cfg['candidate_ids']:
      d=pool[cid]
      for vol in cfg['volume_l']:
       for si,signal in enumerate(cfg['signals']):
        for mode,strategy in enumerate(cfg['strategies']):
         for rth,cth,t0 in cfg['thermal_scenarios']:
          k=1/d.cms+RHO*C*C*d.sd*d.sd/(vol/1000)
          ilim=min(cfg['hardware_current_peak_a'],np.sqrt(cfg['theta_limit_k']/(rth*d.re_ohm*(1+cfg['alpha_per_k']*cfg['theta_limit_k']))))
          xlim=d.xmax_mm*.001*cfg['xmax_fraction']; ecap=min(k*xlim*xlim,d.le_mh*.001*ilim*ilim)/2
          rows.append(dict(candidate=cid,volume_l=vol,signal=signal,strategy=strategy,Rth=rth,Cth=cth,theta0=t0))
          pars.append([k,d.mms,d.rms,d.bl,d.le_mh*.001,d.re_ohm,rth,cth,xlim,ilim,ecap,si,mode,t0,d.sd])
    return rows,np.array(pars).T

def waves(cfg,fs):
    t=np.arange(round(cfg['duration_s']*fs)+1)/fs
    f=np.array(cfg['tone_hz']);a=1/np.sqrt(f/20)
    aligned=np.sum(a[:,None]*np.sin(2*np.pi*f[:,None]*t),axis=0)
    phase=-np.pi*np.arange(len(f))*(np.arange(len(f))-1)/len(f)
    sch=np.sum(a[:,None]*np.sin(2*np.pi*f[:,None]*t+phase[:,None]),axis=0)
    beat=np.mod(t,.5);burst=np.sin(2*np.pi*35*t)*np.exp(-beat/.065)+.2*np.sin(2*np.pi*73*t)
    sub=np.sin(2*np.pi*7*t)+.5*np.sin(2*np.pi*35*t)+3*np.exp(-((t-.12)/.004)**2)
    raw=np.array([aligned,sch,burst,sub]);raw/=np.sqrt(np.mean(raw**2,axis=1))[:,None]
    # Begin at rest, preserve explicit impulse/attack. Final 0.5 s zero input ringdown.
    env=np.minimum(t/.02,1);env[t>cfg['duration_s']-.5]=0
    raw*=env
    sos=np.vstack((butter(2,20,'high',fs=fs,output='sos'),butter(2,80,'low',fs=fs,output='sos'),butter(2,80,'low',fs=fs,output='sos')))
    u=sosfilt(sos,raw,axis=1)*cfg['input_rms_v']
    return t,u,raw

def rhs(z,cmd,p,cfg):
    k,m,rm,bl,le,re,rth,cth,xlim,ilim,ecap,si,mode,t0,sd=p
    x,v,i,theta=z[:4];r=re*(1+cfg['alpha_per_k']*theta)
    energy=(k*x*x+m*v*v+le*i*i)/2
    u=np.clip(cmd,-cfg['rail_peak_v'],cfg['rail_peak_v'])
    feedback=np.clip(cmd-cfg['current_feedback_ohm']*np.sign(i)*np.maximum(abs(i)-ilim,0),-cfg['rail_peak_v'],cfg['rail_peak_v'])
    u=np.where(mode==1,feedback,u)
    # Only restrict port power when outside the admissible half-space. No state clipping.
    allowed=rm*v*v+r*i*i+cfg['barrier_rate_per_s']*(ecap-energy)
    restricted=(mode==2)&(u*i>allowed)&(abs(i)>1e-12)
    u=np.where(restricted,allowed/np.where(abs(i)>1e-12,i,1),u)
    u=np.clip(u,-cfg['rail_peak_v'],cfg['rail_peak_v'])
    deriv=np.array([v,(bl*i-rm*v-k*x)/m,(u-r*i-bl*v)/le,(r*i*i-theta/rth)/cth,u*i,rm*v*v,r*i*i,theta/rth])
    return deriv,u,energy

def run(cfg,fs,selection=None):
    rows,p=setup(cfg)
    if selection is not None:rows=[rows[q] for q in selection];p=p[:,selection]
    t,w,raw=waves(cfg,fs);h=1/fs;n=len(rows)
    z=np.zeros((8,n));z[3]=p[13];mx=np.zeros((4,n));eu=np.zeros(n);uu=np.zeros(n);ii=np.zeros(n);aa=np.zeros(n);sat=np.zeros(n);trace=[]
    for j in range(len(t)-1):
      a=w[p[11].astype(int),j];b=w[p[11].astype(int),j+1];mid=(a+b)/2
      q1,u,e=rhs(z,a,p,cfg);q2,_,_=rhs(z+h*q1/2,mid,p,cfg);q3,_,_=rhs(z+h*q2/2,mid,p,cfg);q4,_,_=rhs(z+h*q3,b,p,cfg)
      z+=h*(q1+2*q2+2*q3+q4)/6
      mx=np.maximum(mx,abs(z[:4]));eu=np.maximum(eu,e/p[10]);uu+=u*u*h;ii+=z[2]**2*h;aa+=q1[1]**2*h
      sat+=(abs(a)>cfg['rail_peak_v'])*h
      if j%int(fs/200)==0:trace.append(np.vstack([z[:4],u[None],(e/p[10])[None]]).T)
    energy=(p[0]*z[0]**2+p[1]*z[1]**2+p[4]*z[2]**2)/2
    emerr=energy-z[4]+z[5]+z[6]
    therr=p[7]*(z[3]-p[13])-z[6]+z[7]
    for q,r in enumerate(rows):
      r.update(x_peak_mm=mx[0,q]*1000,x_ratio=mx[0,q]/p[8,q],i_peak_a=mx[2,q],i_ratio=mx[2,q]/p[9,q],theta_peak_k=mx[3,q],theta_end_k=z[3,q],energy_ratio_max=eu[q],u_rms_v=np.sqrt(uu[q]/cfg['duration_s']),i_rms_a=np.sqrt(ii[q]/cfg['duration_s']),Pcu_average_W=z[6,q]/cfg['duration_s'],input_rail_exceedance_s=sat[q],electromechanical_energy_error_J=emerr[q],thermal_energy_error_J=therr[q],energy_error_relative=abs(emerr[q])/max(abs(z[4,q]),1e-9),acceleration_rms_m_s2=np.sqrt(aa[q]/cfg['duration_s']),X_reference_mm=p[8,q]*1000,I_reference_a=p[9,q],energy_cap_J=p[10,q])
    return rows,p,t,w,raw,np.array(trace),z

def independent(cfg,selection):
    rows,p=setup(cfg);p=p[:,selection];t,w,_=waves(cfg,cfg['sample_rate_hz']);checks=[]
    # Independently written scalar equations, DOP853 adaptive integration.
    for q,ix in enumerate(selection):
      k,m,rm,bl,le,re,rth,cth,xlim,ilim,ecap,si,mode,t0,sd=p[:,q]
      def fun(tt,z):
        x,v,i,theta=z;cmd=np.interp(tt,t,w[int(si)]);resistance=re*(1+.004*theta)
        if mode==1:cmd-=10*np.sign(i)*max(abs(i)-ilim,0)
        u=max(-cfg['rail_peak_v'],min(cfg['rail_peak_v'],cmd))
        if mode==2 and i!=0:
          e=(k*x*x+m*v*v+le*i*i)/2;power=rm*v*v+resistance*i*i+cfg['barrier_rate_per_s']*(ecap-e)
          if u*i>power:u=max(-cfg['rail_peak_v'],min(cfg['rail_peak_v'],power/i))
        return [v,(bl*i-rm*v-k*x)/m,(u-resistance*i-bl*v)/le,(resistance*i*i-theta/rth)/cth]
      sol=solve_ivp(fun,(0,cfg['duration_s']),[0,0,0,t0],method='DOP853',rtol=2e-8,atol=[1e-11,1e-9,1e-9,1e-8],max_step=1/3000)
      assert sol.success
      checks.append(dict(index=ix,final_state=sol.y[:,-1].tolist(),nfev=sol.nfev))
    return checks

def main():
    cfg=json.loads(CFG.read_text());rows,p,t,w,raw,tr,z=run(cfg,cfg['sample_rate_hz'])
    with (OUT/'p25c_kampania.csv').open('w') as f:
      wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
    # Select hardest x/i/temperature witnesses and one from each strategy.
    ix=sorted(set([int(np.argmax([r['x_ratio'] for r in rows])),int(np.argmax([r['i_ratio'] for r in rows])),int(np.argmax([r['theta_peak_k'] for r in rows])),0,2,4]))
    finer=run(cfg,cfg['sample_rate_hz']*2,ix)[0];conv=[]
    for i,rr in zip(ix,finer):
      conv.append(dict(index=i,x_scaled_difference=abs(rr['x_peak_mm']-rows[i]['x_peak_mm'])/rr['X_reference_mm'],i_scaled_difference=abs(rr['i_peak_a']-rows[i]['i_peak_a'])/rr['I_reference_a'],theta_difference_K=abs(rr['theta_peak_k']-rows[i]['theta_peak_k'])))
    independ=independent(cfg,[0,4])
    for c in independ:c['scaled_final_error']=float(np.max(abs(np.array(c['final_state'])-z[:4,c['index']])/np.array([p[8,c['index']],1,p[9,c['index']],80])))
    assert max(x['x_scaled_difference'] for x in conv)<.01
    assert max(x['i_scaled_difference'] for x in conv)<.01
    assert max(x['scaled_final_error'] for x in independ)<.002
    assert max(r['energy_error_relative'] for r in rows)<.001
    barrier=[r for r in rows if r['strategy']=='energy_barrier']
    assert max(r['energy_ratio_max'] for r in barrier)<1.002
    summary=dict(cases=len(rows),scope=cfg['scope'],convergence=conv,independent_DOP853=independ,max_energy_relative_error=max(r['energy_error_relative'] for r in rows),max_thermal_balance_error_J=max(abs(r['thermal_energy_error_J']) for r in rows),signal_crest_factor_before_filter=(np.max(abs(raw),axis=1)/np.sqrt(np.mean(raw**2,axis=1))).tolist(),signal_crest_factor_after_filter=(np.max(abs(w),axis=1)/np.sqrt(np.mean(w**2,axis=1))).tolist(),strategies={s:dict(max_x_ratio=max(r['x_ratio'] for r in rows if r['strategy']==s),max_i_ratio=max(r['i_ratio'] for r in rows if r['strategy']==s),max_theta_K=max(r['theta_peak_k'] for r in rows if r['strategy']==s)) for s in cfg['strategies']})
    (OUT/'p25c_podsumowanie.json').write_text(json.dumps(summary,indent=2))
    fig,axs=plt.subplots(2,2,figsize=(12,8));ts=np.arange(len(tr))/200
    for idx in [0,2,4]:
      lab=rows[idx]['strategy'];axs[0,0].plot(ts,tr[:,idx,0]*1000,label=lab);axs[0,1].plot(ts,tr[:,idx,2],label=lab);axs[1,0].plot(ts,tr[:,idx,3],label=lab);axs[1,1].plot(ts,tr[:,idx,4],label=lab)
    for ax,title in zip(axs.flat,['Ruch [mm]','Prad [A]','Przyrost temperatury [K]','Napiecie portu [V]']):ax.set(xlabel='Czas [s]',ylabel=title);ax.legend();ax.grid()
    fig.suptitle('P25C: C02 / 100 l / multisine aligned / Rth=0.3, Cth=200, start cold\nModel 0D; scenariusze, nie pomiar ani preset DSP');fig.tight_layout();fig.savefig(OUT/'p25c_przebiegi.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for s in cfg['strategies']:
      subset=[r for r in rows if r['strategy']==s];ax.scatter([r['Pcu_average_W'] for r in subset],[r['x_ratio'] for r in subset],s=14,alpha=.6,label=s)
    ax.axhline(1,color='k',ls='--');ax.set(xlabel='Srednie straty miedzi w 6 s [W]',ylabel='max |x| / (0.6 Xmax katalogowe)',title='216 scenariuszy C02/C11/C06; brak rankingu rzeczywistego THD');ax.legend();ax.grid();fig.tight_layout();fig.savefig(OUT/'p25c_ograniczenia.png',dpi=150)
    inputs=[CFG,ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'dane/przetworniki/rozszerzenie_SB_20261025.json',ROOT/'brief_system_audio_DIY_v0.6.md',Path(__file__),ROOT/'skrypty/model_subwoofera.py',ROOT/'skrypty/analiza_rozszerzenia_SB.py']
    outputs=list(OUT.glob('p25c_*'));outputs=[x for x in outputs if 'manifest' not in x.name]
    manifest=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,files={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs+outputs})
    (OUT/'p25c_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
