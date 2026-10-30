from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy.signal import butter,sosfreqz
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import RHO,C,alignment,dsp_shape
from model_wypelnienia import CircularPores,layer_impedance
from komora_warstwowa_P21C2 import port,modal_impedances,independent_mode_ladder,MED
from membrana_kolowa_P21C1 import solve
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
def write(name,rows):
 with (O/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
def panel_compliance(f,a,b,t=.022,E=2e9,rho=800,nu=.3,eta=.04,N=31):
 m,n=np.meshgrid(np.arange(1,N+1,2),np.arange(1,N+1,2));D=E*t**3/(12*(1-nu*nu));kn2=np.pi**2*((m/a)**2+(n/b)**2)
 stiffness=D*kn2**2;om2=stiffness/(rho*t)
 return np.array([np.sum(64*a*b/(np.pi**4*m*m*n*n*stiffness)/(1-(2*np.pi*hz)**2/om2+1j*eta)) for hz in f]),float(np.sqrt(om2.min())/(2*np.pi))
def drive(d,f,Z,theta=0,air_fraction=1,wallC=0):
 s=2j*np.pi*f;a=np.sqrt(d.sd/np.pi)
 # Replace unknown rear free-air mass fraction, range 0..1, one-side baffled disk proxy.
 ma=8*RHO*a**3/3
 mass=d.mms-air_fraction*ma
 assert mass>0
 load=1/(1/Z+s*wallC)
 zm=d.rms+s*mass+1/(s*d.cms)+d.sd*d.sd*load
 ze=d.re_ohm*(1+.004*theta)+s*d.le_mh*.001
 I=1/(ze+d.bl*d.bl/zm);v=d.bl*I/zm
 return I,v,load

def main():
 pool={cid:d for cid,pid,d,cat in candidates()};w=.836;h=.456;freq=np.array([20,25,31.5,40,50,63,80.]);rows=[];checks=[]
 # nominal acoustic dimensions correspond to net air-equivalent rectangular domain;
 # protrusions are volume bookkeeping, spatial scattering remains open.
 for cid in ['C02','C11','C20','C21','C04','C06','C15','C25','C26S']:
  d=pool[cid]
  for V in [100,120,140]:
   depth=V*.001/(w*h)
   for thick in [0,.025,.05,.1]:
    for radius in ([.0002] if thick==0 else [.00005,.0002,.001]):
     mat=CircularPores(radius,.98,'rigid',20.)
     layers=[(depth-thick,None),(thick,mat)]
     Z=port(w,h,layers,(w/4,h/2),d.sd,freq,100)
     assert min(Z.real)>-1e-7
     for theta in [0,80]:
      for airfrac in [0,1]:
       for wall in [False,True]:
        cp,fpanel=panel_compliance(freq,.28,.30)
        # 12 supported bays is a diagnostic compliance scenario, not actual full-box FE.
        wallC=12*cp if wall else 0
        I,v,load=drive(d,freq,Z,theta,airfrac,wallC)
        xp=np.sqrt(2)*abs(v)/(2*np.pi*freq);Re=d.re_ohm*(1+.004*theta)
        U=np.minimum.reduce([np.full_like(freq,40),12/abs(I),.7*d.xmax_mm*.001/xp,np.sqrt(50/Re)/abs(I)])
        spl=20*np.log10(RHO*2*np.pi*freq*d.sd*abs(v)*U/(2*np.pi*20e-6))
        for j,f in enumerate(freq):rows.append(dict(cid=cid,volume_l=V,layer_m=thick,pore_radius_m=radius,theta_K=theta,rear_air_fraction=airfrac,wall_proxy=wall,f_hz=f,Z_real=Z[j].real,Z_imag=Z[j].imag,allowed_Vrms=U[j],SPL_2pi_1m_RMS=spl[j],x_peak_mm=xp[j]*U[j]*1000,pcu_W=(abs(I[j])*U[j])**2*Re))
 # exact empty disk comparison, homogeneous fullface tube, and independent per-mode FV.
 d=pool['C02'];depth=.32
 z=port(w,h,[(depth,None)],(w/4,h/2),d.sd,freq,160)
 R=solve((w,depth,h),(w/4,h/2),np.sqrt(d.sd/np.pi),freq,160,C,RHO)[0]
 ref=R*RHO*C*C/(2j*np.pi*freq*w*depth*h)
 assert max(abs(z/ref-1))<1e-10
 checks.append(dict(test='empty_disk_vs_P21C1',relative_error=float(max(abs(z/ref-1)))))
 for f in [20,80,160]:
  layers=[(.27,None),(.05,CircularPores(.0002,.98,'rigid',20))]
  nx,nz,zs=modal_impedances(w,h,layers,f,3)
  for n,l in [(0,0),(1,0),(1,2),(3,3)]:
   errors=[]
   for nn in [64,128,256,512]:
    val=independent_mode_ladder(w,h,layers,f,n,l,nn);errors.append(float(abs(val/zs[n,l]-1)))
   assert errors[-1]<.001 and errors[-1]<errors[0]
   checks.append(dict(test='independent_FV_transverse_mode',f=f,n=n,l=l,errors=errors))
  exact=layer_impedance(np.array([f]),w*h,layers,MED)[0]
  assert abs(zs[0,0]/(w*h)/exact-1)<1e-12
 # source truncation on 3 witnesses; finite grid comparison, no analytic porous tail claim.
 for rad in [.00005,.0002,.001]:
  layers=[(.27,None),(.05,CircularPores(rad,.98,'rigid',20))]
  z1=port(w,h,layers,(w/4,h/2),d.sd,freq,100);z2=port(w,h,layers,(w/4,h/2),d.sd,freq,200)
  er=float(max(abs(z1-z2)/abs(z2)));assert er<.001
  checks.append(dict(test='porous_port_100_200',radius=rad,relative_change=er))
 write('p29b_warstwa_naped.csv',rows)
 # Multi-tone finite Fourier series; no assertion of measured music or robust limiter.
 tones=np.array([20,23,27,31,37,43,50,59,68,80]);fs=12000;tt=np.arange(fs)/fs;multi=[]
 for V in [100,120,140]:
  depth=V*.001/(w*h);layers=[(depth-.05,None),(.05,CircularPores(.0002,.98,'rigid',20))]
  Z=port(w,h,layers,(w/4,h/2),d.sd,tones,100)
  I,v,load=drive(d,tones,Z)
  x=v/(2j*np.pi*tones);hp=butter(2,20,'high',fs=fs,output='sos');lp=butter(4,80,'low',fs=fs,output='sos')
  H=sosfreqz(hp,worN=tones,fs=fs)[1]*sosfreqz(lp,worN=tones,fs=fs)[1]
  # equalize pressure per tone BEFORE HP/LP; inverse only on finite tones, not realizable preset.
  eq=H/(1j*tones*v);eq/=max(abs(eq))
  for kind in ['aligned','schroeder','random']:
   n=np.arange(len(tones));phase=np.zeros(len(n)) if kind=='aligned' else (-np.pi*n*(n-1)/len(n) if kind=='schroeder' else np.random.default_rng(291030).uniform(0,2*np.pi,len(n)))
   e=np.exp(2j*np.pi*tones[:,None]*tt+1j*phase[:,None]);ut=np.real(np.sum(eq[:,None]*e,axis=0));it=np.real(np.sum((eq*I)[:,None]*e,axis=0));xt=np.real(np.sum((eq*x)[:,None]*e,axis=0))
   scale=min(40*np.sqrt(2)/max(abs(ut)),12*np.sqrt(2)/max(abs(it)),.7*d.xmax_mm*.001/max(abs(xt)),np.sqrt(50/(d.re_ohm*np.mean(it*it))))
   # Continuous-time peak bounded between time samples by derivative supremum * dt/2.
   ub=max(abs(ut))+np.sum(abs(eq)*2*np.pi*tones)/(2*fs);ib=max(abs(it))+np.sum(abs(eq*I)*2*np.pi*tones)/(2*fs);xb=max(abs(xt))+np.sum(abs(eq*x)*2*np.pi*tones)/(2*fs)
   safe=min(40*np.sqrt(2)/ub,12*np.sqrt(2)/ib,.7*d.xmax_mm*.001/xb,np.sqrt(50/(d.re_ohm*np.mean(it*it))))
   multi.append(dict(V_l=V,phase=kind,Vpeak_bound=ub*safe,Ipeak_bound=ib*safe,Xpeak_mm_bound=xb*safe*1000,Pcu_W=d.re_ohm*np.mean(it*it)*safe*safe,sample_only_scale=scale,continuous_bound_scale=safe,crest_V=ub/np.sqrt(np.mean(ut*ut)),crest_X=xb/np.sqrt(np.mean(xt*xt))))
 write('p29b_wieloton.csv',multi)
 summary=dict(checks=checks,rows=len(rows),multitone_cases=len(multi),wall_bay_first_mode_hz=fpanel,geometry=dict(width_ext_m=.880,height_ext_m=.500,depth_ext_m=.480,side_m=.022,front_m=.044,inside_w_h_d=[w,h,.414],empty_gross_l=w*h*.414*1000),limitations=['No physical measurements','Layer spans whole section; not five-wall lining','Net-equivalent rectangle omits scattering by basket/braces','12 SSSS bays is diagnostic wall compliance, not full FE','Mms rear correction fraction 0..1 is scenario','50W copper budget not physical thermal certification','Finite-tone inverse not deployable DSP preset'])
 (O/'p29b_podsumowanie.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
