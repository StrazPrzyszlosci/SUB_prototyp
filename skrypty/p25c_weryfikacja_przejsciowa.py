"""Additional independent transient check, not merely ringdown final state."""
import json
import numpy as np
from scipy.integrate import solve_ivp
from p25c_czas_ochrona import CFG,OUT,setup,waves,run

def main():
 cfg=json.loads(CFG.read_text());fs=cfg['sample_rate_hz'];meta,allp=setup(cfg)
 selection=[54,5];_,p,t,w,raw,tr,z=run(cfg,fs,selection)
 # run() stores state AFTER the integration step, every fs/200 iterations.
 times=np.arange(len(tr))/200+1/fs
 stop=1.25;take=times<=stop;tt=times[take]
 result=[]
 for j,ix in enumerate(selection):
  k,m,r,bl,le,re,rth,cth,xlim,ilim,ecap,si,mode,t0,sd=p[:,j]
  def equations(time,state):
   x,v,i,theta=state
   cmd=np.interp(time,t,w[int(si)]);resistance=re*(1+cfg['alpha_per_k']*theta)
   if mode==1:cmd-=cfg['current_feedback_ohm']*np.sign(i)*max(abs(i)-ilim,0)
   u=np.clip(cmd,-cfg['rail_peak_v'],cfg['rail_peak_v'])
   if mode==2 and abs(i)>1e-12:
    energy=.5*(k*x*x+m*v*v+le*i*i)
    power=r*v*v+resistance*i*i+cfg['barrier_rate_per_s']*(ecap-energy)
    if u*i>power:u=np.clip(power/i,-cfg['rail_peak_v'],cfg['rail_peak_v'])
   return [v,(bl*i-r*v-k*x)/m,(u-resistance*i-bl*v)/le,(resistance*i*i-theta/rth)/cth]
  sol=solve_ivp(equations,(0,stop),[0,0,0,t0],t_eval=tt,method='DOP853',rtol=3e-7,atol=[1e-10,1e-8,1e-8,1e-7],max_step=1/1500)
  assert sol.success
  scale=np.array([xlim,1,ilim,80])
  err=np.max(abs(sol.y.T-tr[take,j,:4])/scale,axis=0)
  assert max(err)<.003
  result.append(dict(index=ix,case=meta[ix],duration_s=stop,nfev=sol.nfev,checkpoints=len(tt),max_scaled_trajectory_error=err.tolist(),scales=['Xref_m','1_m_s','Icap_A','80_K']))
  print(ix,err,flush=True)
 (OUT/'p25c_weryfikacja_przejsciowa.json').write_text(json.dumps(dict(scope='Independent scalar ODE versus RK4 full trajectory at 200Hz checkpoints through 1.25s, same interpolated input; no continuous error bound or hardware validation.',results=result),indent=2))
if __name__=='__main__':main()
