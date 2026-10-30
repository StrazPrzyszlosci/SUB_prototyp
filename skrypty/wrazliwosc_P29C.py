"""Dalsze badanie reguły wyboru i marginesu głębokości; brak pomiarów."""
from pathlib import Path
import csv,json
import numpy as np
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import RHO,C
ROOT=Path(__file__).resolve().parents[1]; O=ROOT/'wyniki'
x=np.load(O/'p29a_stress_samples.npy')[1:];w=2*np.pi*np.geomspace(20,80,121)
def envelope(d,v):
 M=d.mms*x[:,0,None];Cm=d.cms*x[:,1,None];BL=d.bl*x[:,2,None];Rm=d.rms*(x[:,3]+x[:,9])[:,None]
 Re=d.re_ohm*(x[:,4]*(1+.004*x[:,11]))[:,None];Le=d.le_mh*.001*x[:,5,None];Sd=d.sd*x[:,6,None]
 K=1/Cm+RHO*C*C*Sd**2*x[:,8,None]/(v*.001*x[:,7,None]);zm=Rm+1j*(w*M-K/w)
 i=1/(Re+1j*w*Le+BL**2/zm);vel=BL*i/zm;xp=np.sqrt(2)*abs(vel)/w
 ux=d.xmax_mm*.001*x[:,10,None]/xp
 un=np.minimum.reduce([np.full_like(ux,40),12/abs(i),ux])
 gain=RHO*w*Sd*abs(vel)/(2*np.pi*20e-6)
 # min over both scenario and frequency commutes with min over limits.
 return float(np.min(20*np.log10(gain*un))),float(np.min(20*np.log10(gain/np.sqrt(Re)/abs(i))))
def value(ab,p):return min(ab[0],ab[1]+10*np.log10(p))
def main():
 pool=candidates(); coeff={cid:envelope(d,120) for cid,_,d,_ in pool};rows=[]
 for p in np.arange(25,201):
  scores={cid:value(ab,p) for cid,ab in coeff.items()};win=max(scores,key=scores.get)
  rows.append(dict(pcu_w=int(p),winner=win,best_minband_db=scores[win],C02_db=scores['C02'],C11_db=scores['C11']))
 a,b=coeff['C02'],coeff['C11'];cross=10**((a[0]-b[1])/10)
 assert abs(value(a,cross)-value(b,cross))<1e-10
 d=next(d for cid,_,d,_ in pool if cid=='C02');vol=[]
 for v in range(70,161):vol.append(dict(volume_l=v,stress_minband_db=value(envelope(d,v),50)))
 plateau=max(r['stress_minband_db'] for r in vol);vfirst=next(r['volume_l'] for r in vol if plateau-r['stress_minband_db']<=.2)
 # Reproduce old screening at its shared grid points, independently reduce by budget.
 old=list(csv.DictReader((O/'p29a_screening.csv').open()));err=0
 for cid,ab in coeff.items():
  for p in [50,100,200]:
   r=next(r for r in old if r['configuration']==cid and int(r['volume_l'])==120 and int(r['vmax'])==40 and int(r['pcu_budget_w'])==p)
   err=max(err,abs(value(ab,p)-float(r['stress_minband_db'])))
 assert err<1e-10
 depth=[]
 for body in [450,460,466,470,476,480]:
  inner=body-44-22;gross=.836*.456*inner
  depth.append(dict(body_depth_mm=body,external_protrusion_budget_mm=500-body,inside_depth_mm=inner,net_nominal_10_modules_l=gross-8-.381216-30.6,net_nominal_16_modules_l=gross-8-.381216-48.96,old_module_to_mat_gap_mm=inner-50-360,old_layout_nonintersecting=inner>=410))
 summary=dict(scope='512 same Sobol points, 121 f 20–80 Hz, independent steady sinusoids 2pi/1m/RMS; not tolerance population or continuous-domain proof',thermal_coefficients=coeff,C02_C11_crossover_pcu_W=cross,shared_grid_reproduction_max_db_error=err,first_integer_volume_within_point2_db=vfirst,plateau_db=plateau,depth_budget=depth,heat_winner_transitions=[r for i,r in enumerate(rows) if i==0 or r['winner']!=rows[i-1]['winner']])
 for name,data in [('p29c_grzanie.csv',rows),('p29c_objetosc.csv',vol)]:
  with (O/name).open('w') as h:
   wr=csv.DictWriter(h,fieldnames=data[0]);wr.writeheader();wr.writerows(data)
 (O/'p29c_podsumowanie.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
