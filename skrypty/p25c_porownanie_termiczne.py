"""Paired cold linear reference at identical clipped port waveform.
Finite-window acceleration RMS ratio, not measured acoustic compression.
"""
import json,csv
import numpy as np
from scipy.signal import StateSpace,lsim
from p25c_czas_ochrona import ROOT,OUT,CFG,setup,waves

def main():
 cfg=json.loads(CFG.read_text());meta,p=setup(cfg);t,w,raw=waves(cfg,cfg['sample_rate_hz'])
 measured=list(csv.DictReader((OUT/'p25c_kampania.csv').open()));result=[]
 for j,r in enumerate(meta):
  if r['strategy']!='rail' or r['volume_l']!=120 or r['Rth']!=1.2:continue
  k,m,rm,bl,le,re,rth,cth,xlim,ilim,ecap,si,mode,t0,sd=p[:,j]
  A=np.array([[0,1,0],[-k/m,-rm/m,bl/m],[0,-bl/le,-re/le]])
  B=np.array([0,0,1/le]);Cc=np.array([-k/m,-rm/m,bl/m])
  u=np.clip(w[int(si)],-cfg['rail_peak_v'],cfg['rail_peak_v'])
  _,a,_=lsim(StateSpace(A,B[:,None],Cc[None,:],np.zeros((1,1))),u,t,interp=True)
  cold=np.sqrt(np.mean(a[:-1]**2));hot=float(measured[j]['acceleration_rms_m_s2'])
  result.append(dict(index=j,candidate=r['candidate'],signal=r['signal'],cold_acceleration_rms_m_s2=cold,heated_acceleration_rms_m_s2=hot,heated_over_cold_dB=20*np.log10(hot/cold),theta_end_k=float(measured[j]['theta_end_k'])))
 (OUT/'p25c_termiczne_porownanie.json').write_text(json.dumps(dict(scope='Six-second RMS acceleration transfer at same rail-clipped waveform; heated start +60 K versus Re0. Not isolated self-heating or measured SPL.',rows=result),indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
