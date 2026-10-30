"""Screen all 27 configurations. Scenario uncertainty is not population data.
Single steady sinusoids, equivalent monopole 2pi/1m/RMS. No room gain.
"""
from pathlib import Path
import json,hashlib,csv
import numpy as np
from scipy.stats import qmc
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import RHO,C
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
def main():
 f=np.geomspace(20,80,121);w=2*np.pi*f
 # independent parameter stress; same Sobol coordinates for comparison, not probability
 lo=np.array([.9,.85,.9,.7,.95,.8,.98,.97,.714,0,.5,0])
 hi=np.array([1.1,1.15,1.1,1.3,1.05,1.2,1.02,1.03,1,1,.8,80])
 x=lo+(hi-lo)*qmc.Sobol(12,scramble=True,seed=291030).random_base2(9)
 nominal=np.array([1,1,1,1,1,1,1,1,1,0,.7,0])
 x=np.vstack([nominal,x]);rows=[]
 for cid,pid,d,cat in candidates():
  for vb in [60,80,100,120,150]:
   M=d.mms*x[:,0,None];Cm=d.cms*x[:,1,None];BL=d.bl*x[:,2,None];Rm=d.rms*(x[:,3]+x[:,9])[:,None]
   Re=d.re_ohm*(x[:,4]*(1+.004*x[:,11]))[:,None];Le=d.le_mh*.001*x[:,5,None];Sd=d.sd*x[:,6,None]
   K=1/Cm+RHO*C*C*Sd*Sd*x[:,8,None]/(vb*.001*x[:,7,None])
   zm=Rm+1j*(w*M-K/w);ze=Re+1j*w*Le
   current=1/(ze+BL*BL/zm);velocity=BL*current/zm
   xp=np.sqrt(2)*abs(velocity)/w
   for vmax,imax in [(40,12),(60,20)]:
    for pcu in [50,100,200]:
     u=np.minimum.reduce([np.full_like(xp,vmax),imax/abs(current),d.xmax_mm*.001*x[:,10,None]/xp,np.sqrt(pcu/Re)/abs(current)])
     spl=20*np.log10(RHO*w*Sd*abs(velocity)*u/(2*np.pi*20e-6))
     band=np.min(spl,axis=1);j=int(np.argmin(band))
     rows.append(dict(configuration=cid,model=d.name,volume_l=vb,vmax=vmax,imax=imax,pcu_budget_w=pcu,nominal_minband_db=float(band[0]),stress_minband_db=float(min(band[1:])),stress_witness_index=j,nominal_max_cu_w=float(np.max((abs(current[0])*u[0])**2*Re[0]))))
 with (O/'p29a_screening.csv').open('w') as f0:
  wr=csv.DictWriter(f0,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 cfg=dict(date='2026-10-30',axes=['Mms','Cms','BL','Rms','Re','Le','Sd','Vb','bulk_factor','extra_Rms','X_fraction','delta_T_K'],low=lo.tolist(),high=hi.tolist(),seed=291030,stress_samples=512,frequency_points=121,frequency_range_hz=[20,80],thermal_note='Pcu budgets 50/100/200W are assumptions, not product ratings or temperature guarantees',scope='0D screening; finite geometry integrated separately')
 (ROOT/'dane/konfiguracje/p29a_screening.json').write_text(json.dumps(cfg,indent=2))
 np.save(O/'p29a_stress_samples.npy',x)
 for vm,pc in [(40,100),(60,100),(60,200)]:
  q=[r for r in rows if r['vmax']==vm and r['pcu_budget_w']==pc and r['volume_l']==100]
  print(vm,pc,sorted(q,key=lambda r:r['stress_minband_db'],reverse=True)[:8])
if __name__=='__main__':main()
