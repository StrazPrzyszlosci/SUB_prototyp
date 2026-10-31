"""P25E: sampled energy barrier with bounded sensor/T-S uncertainty, sealed 0D model.
Run: python skrypty/p25e_robustna_bariera.py [--fs 24000] [--duration 0.8]
All results are model-only; no product-level safety or SPL/THD claims.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.signal import butter, sosfilt
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
# With the file installed under skrypty, ROOT refers to repository root.
OUT = ROOT / 'wyniki'
CFG_FILE = ROOT / 'dane' / 'konfiguracje' / 'p25e_odpornosc_obserwacji.json'


def model(nom, rho=1.2, c=343.0, volume_l=120.0):
    fs, qes, qms, vas, sd, re, le, xmax = nom
    sd *= 1.e-4
    cms = vas*1.e-3/(rho*c*c*sd*sd)
    w0 = 2*np.pi*fs
    mass = 1./(w0*w0*cms)
    k = 1./cms + rho*c*c*sd*sd/(volume_l*1.e-3)
    return [k,mass,w0*mass/qms,np.sqrt(w0*mass*re/qes),le*1.e-3,re,xmax*1.e-3]


def waveforms(fs, duration, cfg):
    t=np.arange(round(fs*duration)+1,dtype=float)/fs
    f=np.array([20.,25.,31.,40.,50.,63.,80.,100.])
    a=1/np.sqrt(f/20)
    a0=np.sum(a[:,None]*np.sin(2*np.pi*f[:,None]*t),axis=0)
    a1=np.sin(2*np.pi*7*t)+.5*np.sin(2*np.pi*35*t)+3*np.exp(-((t-.12)/.004)**2)
    z=np.array([a0,a1]);z/=np.sqrt(np.mean(z*z,axis=1))[:,None]
    envelope=np.minimum(t/.02,1)
    envelope[t>duration-.10]=0
    z*=envelope
    sos=np.vstack((butter(2,20,'high',fs=fs,output='sos'),
                   butter(2,80,'low',fs=fs,output='sos'),butter(2,80,'low',fs=fs,output='sos')))
    return sosfilt(sos,z,axis=1)*cfg['input_rms_v']


def build_cases(cfg):
    records=[];p=[]
    for cid,nom in cfg['candidates'].items():
        K,M,Rm,BL,L,R0,xcat = model(nom)
        for therm in cfg['thermal_cases']:
            rth, cth, theta_init=therm
            for sign in [-1,1]:
                dk=cfg['uncertainty']['K_fraction']
                dm=cfg['uncertainty']['M_fraction']
                dl=cfg['uncertainty']['L_fraction']
                dbl=cfg['uncertainty']['BL_fraction']
                drm=cfg['uncertainty']['Rm_fraction']
                dre=cfg['uncertainty']['Re_fraction']
                k=K*(1+sign*dk)
                m=M*(1-sign*dm)
                le=L*(1-sign*dl)
                rm=Rm*(1-sign*drm)
                bl=BL*(1+sign*dbl)
                re=R0*(1-sign*dre)
                re_low=R0*(1-dre)
                re_high=R0*(1+dre)
                xlim=cfg['xmax_fraction']*xcat
                ilim=min(cfg['hardware_current_peak_a'],np.sqrt(cfg['temperature_limit_k']/(rth*re_high*(1+cfg['alpha_k_inv']*cfg['temperature_limit_k']))))
                ecap=.5*min(K*(1-dk)*xlim*xlim,L*(1-dl)*ilim*ilim)
                for wi,label in enumerate(cfg['signals']):
                    for mode in cfg['strategies']:
                        records.append(dict(candidate=cid,theta_init_k=theta_init,uncertainty_sign=sign,
                                            signal=label,mode=mode))
                        p.append([k,m,rm,bl,le,re,rth,cth,theta_init,xlim,ilim,ecap,
                                  K,M,L,R0,re_low,K*(1+dk),M*(1+dm),L*(1+dl),wi])
    return records,np.array(p,dtype=np.float64)


@njit(cache=True)
def derivatives(x,v,i,theta,u,p,alpha):
    k,m,rm,bl,le,re,rth,cth=p[:8]
    RT=re*(1+alpha*theta)
    return (v,(bl*i-rm*v-k*x)/m,(u-RT*i-bl*v)/le,(RT*i*i-theta/rth)/cth)


@njit(cache=True)
def simulate(p, waves, fs, rate, cfg_array):
    # p rows: physical k,m,rm,bl,L,Re,Rth,Cth,t0,Xlim,Ilim,Ecap,
    # nominal K,M,L,Re,Re_min and upper K,M,L,signal_index.
    N=len(p); steps=fs//rate; dt=1./fs; hold_time=1./rate
    alpha,rail,sens_x,sens_v,sens_i = cfg_array
    x=np.zeros(N);v=np.zeros(N);i=np.zeros(N);theta=p[:,8].copy()
    u=np.zeros(N);old_u=np.zeros(N);old_bound=np.zeros(N)
    peakE=np.zeros(N);peakX=np.zeros(N);peakI=np.zeros(N);peakTheta=theta.copy()
    sumU2=np.zeros(N);sumX2=np.zeros(N);sum_acc2=np.zeros(N)
    energy_errors=np.zeros(N);thermal_errors=np.zeros(N)
    accin=np.zeros(N);accmech=np.zeros(N);acccu=np.zeros(N);acccool=np.zeros(N)
    for j in range(waves.shape[1]-1):
        if j%steps==0:
            for c in range(N):
                k,m,rm,bl,L,re,rth,cth,t0,xlim,ilim,ecap=p[c,:12]
                K0,M0,L0,R0,re_low=p[c,12:17]
                Kmax,Mmax,Lmax=p[c,17:20]
                widx=int(p[c,20])
                cmd=max(-rail,min(rail,waves[widx,j]))
                # Deterministic bounded errors; amplitude exact <= sensor specification.
                tm=j/fs; phase=0.19*c
                xm=x[c]+sens_x*np.sin(2*np.pi*11*tm+phase)
                vm=v[c]+sens_v*np.cos(2*np.pi*13*tm+.37*phase)
                im=i[c]+sens_i*np.sin(2*np.pi*17*tm+.71*phase)
                e_true=.5*(k*x[c]**2+m*v[c]**2+L*i[c]**2)
                e_naive=.5*(K0*xm*xm+M0*vm*vm+L0*im*im)
                e_upper=.5*(Kmax*(abs(xm)+sens_x)**2+
                            Mmax*(abs(vm)+sens_v)**2+
                            Lmax*(abs(im)+sens_i)**2)
                mode=c%4  # input strategies order exact, naive, robust_now, robust_delayed
                if mode==0:
                    bound=e_true;resist=re
                elif mode==1:
                    bound=e_naive;resist=R0
                elif mode==2:
                    bound=e_upper;resist=re_low
                else:
                    bound=e_upper if j==0 else old_bound[c]+old_u[c]**2*hold_time/(4*re_low)
                    resist=re_low
                ucap=np.sqrt(max(0.,4*resist*(ecap-bound)/hold_time))
                u[c]=max(-ucap,min(ucap,cmd))
                old_bound[c]=e_upper
                old_u[c]=u[c]
        for c in range(N):
            a=derivatives(x[c],v[c],i[c],theta[c],u[c],p[c],alpha)
            b=derivatives(x[c]+dt*a[0]/2,v[c]+dt*a[1]/2,i[c]+dt*a[2]/2,theta[c]+dt*a[3]/2,u[c],p[c],alpha)
            d=derivatives(x[c]+dt*b[0]/2,v[c]+dt*b[1]/2,i[c]+dt*b[2]/2,theta[c]+dt*b[3]/2,u[c],p[c],alpha)
            e=derivatives(x[c]+dt*d[0],v[c]+dt*d[1],i[c]+dt*d[2],theta[c]+dt*d[3],u[c],p[c],alpha)
            # Simpson weights for integrated energy work and thermal flow
            jj=(a[2],b[2],d[2],e[2]); vv=(a[1],b[1],d[1],e[1])
            x0,v0,i0,T0=x[c],v[c],i[c],theta[c]
            y0=(x0,v0,i0,T0)
            y1=(x0+dt*a[0]/2,v0+dt*a[1]/2,i0+dt*a[2]/2,T0+dt*a[3]/2)
            y2=(x0+dt*b[0]/2,v0+dt*b[1]/2,i0+dt*b[2]/2,T0+dt*b[3]/2)
            y3=(x0+dt*d[0],v0+dt*d[1],i0+dt*d[2],T0+dt*d[3])
            wts=(1.,2.,2.,1.)
            for z in range(4):
                X,V,I,T=(y0,y1,y2,y3)[z]
                weight=wts[z]*dt/6
                accin[c]+=weight*u[c]*I
                accmech[c]+=weight*p[c,2]*V*V
                acccu[c]+=weight*p[c,5]*(1+alpha*T)*I*I
                acccool[c]+=weight*T/p[c,6]
            x[c]+=dt*(a[0]+2*b[0]+2*d[0]+e[0])/6
            v[c]+=dt*(a[1]+2*b[1]+2*d[1]+e[1])/6
            i[c]+=dt*(a[2]+2*b[2]+2*d[2]+e[2])/6
            theta[c]+=dt*(a[3]+2*b[3]+2*d[3]+e[3])/6
            k,m,rm,bl,L,re,rth,cth,t0,xlim,ilim,ecap=p[c,:12]
            energy=.5*(k*x[c]**2+m*v[c]**2+L*i[c]**2)
            peakE[c]=max(peakE[c],energy/ecap)
            peakX[c]=max(peakX[c],abs(x[c])/xlim)
            peakI[c]=max(peakI[c],abs(i[c])/ilim)
            peakTheta[c]=max(peakTheta[c],theta[c])
            sumU2[c]+=dt*u[c]*u[c]
            sumX2[c]+=dt*x[c]*x[c]
            sum_acc2[c]+=dt*a[1]*a[1]
    dur=(waves.shape[1]-1)/fs
    for c in range(N):
        k,m,rm,bl,L,re,rth,cth,t0,xlim,ilim,ecap=p[c,:12]
        endE=.5*(k*x[c]**2+m*v[c]**2+L*i[c]**2)
        energy_errors[c]=(endE-accin[c]+accmech[c]+acccu[c])/max(ecap,1e-10)
        thermal_errors[c]=(cth*(theta[c]-t0)-acccu[c]+acccool[c])/max(cth,1e-10)
    return peakE,peakX,peakI,peakTheta,np.sqrt(sumU2/dur),np.sqrt(sumX2/dur),np.sqrt(sum_acc2/dur),energy_errors,thermal_errors


def evaluate(cfg,fs,duration):
    rows,p=build_cases(cfg)
    waves=waveforms(fs,duration,cfg)
    results=[]
    for rate in cfg['controller_rates_hz']:
        assert fs%rate==0
        vals=simulate(p,waves,fs,rate,np.array([cfg['alpha_k_inv'],cfg['rail_peak_v'],
                                                cfg['sensor_bounds']['x_m'],cfg['sensor_bounds']['v_m_s'],
                                                cfg['sensor_bounds']['i_a']]))
        for k,r in enumerate(rows):
            o=dict(r,controller_hz=rate,integration_hz=fs)
            for key,v in zip(['max_E_ratio','max_X_ratio','max_I_ratio','max_theta_k',
                              'u_rms_v','x_rms_m','a_rms_m_s2','energy_balance_scaled',
                              'thermal_balance_k'],vals):o[key]=float(v[k])
            o['E_over']=o['max_E_ratio']>1.00005
            o['X_over']=o['max_X_ratio']>1.00005
            o['I_over']=o['max_I_ratio']>1.00005
            results.append(o)
    return results


def summarize(rows):
    res={'n':len(rows),'groups':{},'checks':{}}
    for rate in sorted(set(r['controller_hz'] for r in rows)):
        for mode in ['ideal','naive','robust_now','robust_delay']:
            subset=[r for r in rows if r['controller_hz']==rate and r['mode']==mode]
            key=f'{mode}_{rate}'
            res['groups'][key]={
                'n':len(subset),'E_violations':sum(r['E_over'] for r in subset),
                'X_violations':sum(r['X_over'] for r in subset),
                'I_violations':sum(r['I_over'] for r in subset),
                'peak_E_cap':max(r['max_E_ratio'] for r in subset),
                'peak_X_ref':max(r['max_X_ratio'] for r in subset),
                'peak_I_ref':max(r['max_I_ratio'] for r in subset),
                'median_output_voltage_rms_v':float(np.median([r['u_rms_v'] for r in subset])),
                'median_x_rms_mm':float(np.median([r['x_rms_m']*1000 for r in subset]))}
    res['checks']={'energy_balance_scaled_max':max(abs(r['energy_balance_scaled']) for r in rows),
                   'thermal_balance_k_max':max(abs(r['thermal_balance_k']) for r in rows)}
    return res


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fs',type=int,default=24000)
    ap.add_argument('--duration',type=float,default=.8)
    args=ap.parse_args();cfg=json.loads(CFG_FILE.read_text())
    OUT.mkdir(exist_ok=True,parents=True)
    rows=evaluate(cfg,args.fs,args.duration)
    result=summarize(rows)
    if args.fs==24000:
        with (OUT/'p25e_kampania.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
        (OUT/'p25e_podsumowanie.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
        files=[CFG_FILE,Path(__file__),OUT/'p25e_kampania.csv',OUT/'p25e_podsumowanie.json']
        (OUT/'p25e_manifest.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,
            'scipy':scipy.__version__,'numba':__import__('numba').__version__,
            'sha256':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in files}},indent=2))
    else:
        (OUT/f'p25e_zbieznosc_{args.fs}.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
