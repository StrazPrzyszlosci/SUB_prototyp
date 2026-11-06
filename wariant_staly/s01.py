"""Comparative architecture study. Run from any directory with the repository dependencies."""
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT/'skrypty'))
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import alignment, response, sealed_shape
from model_pokoju import ModalRoom
from wrazliwosc_P29C import envelope, value


def audio(d, v):
    f = np.linspace(10, 120, 441)
    w = 2*np.pi*f
    fc,q,f3 = alignment(d,v)
    raw = response(d,v,f)
    # Analogue Linkwitz transform plus LR4 low pass. Driver includes Le in its actual response.
    s = 1j*w
    target = sealed_shape(f,20,2**-.5)
    lp = (1+2**.5*s/(2*np.pi*80)+(s/(2*np.pi*80))**2)**-2
    eq = target/sealed_shape(f,fc,q)*lp
    band = (f>=20)&(f<=40)
    voltage = np.abs(eq)
    # Scale to 95 dB at 40 Hz, per module in half-space at one metre.
    i40 = np.argmin(abs(f-40))
    voltage *= 10**((95-raw['spl_rms_db'][i40])/20)/voltage[i40]
    result = response(d,v,f,voltage)
    actual = (s*d.mms+d.rms+(1/d.cms+1.2041*343**2*d.sd**2/(v*.001))/s)
    current = 1/(d.re_ohm+s*d.le_mh*.001+d.bl**2/actual)
    pressure = s*d.bl*current/actual*eq
    delay = -np.gradient(np.unwrap(np.angle(pressure)),w)*1000
    headroom = np.minimum.reduce([40/voltage,12/result['i_rms'],d.xmax_mm*.001/result['x_peak_m'],
                                  np.sqrt(50/result['p_copper_w'])])
    pick = [np.argmin(abs(f-k)) for k in (20,25,31.5,40,60,80)]
    return dict(driver=d.name,litres=v,fc=fc,qtc=q,f3=f3,
                freq_Hz=[20,25,31.5,40,60,80],raw_dB_1V=raw['spl_rms_db'][pick].tolist(),
                corrected_dB=result['spl_rms_db'][pick].tolist(),delay_ms=delay[pick].tolist(),
                eq_peak_dB=float(20*np.log10(abs(eq).max())),
                max_V=float(voltage[band].max()),max_A=float(result['i_rms'][band].max()),
                max_X_mm=float(result['x_peak_m'][band].max()*1000),
                max_Pcu_W=float(result['p_copper_w'][band].max()),
                headroom_dB=float(20*np.log10(headroom[band].min())))


def cabinet(v, ratio):
    # Clear width/height ratio. One mid-depth window frame, 30 mm border.
    t,depth=22.,328.
    extras={'driver_L':5.,'terminal_L':.175,'wiring_glue_L':.15}
    def geometry(h):
        w=ratio*h
        brace=(w*h-(w-60)*(h-60))*t*1e-6
        gross=w*h*depth*1e-6
        return gross,brace,gross-brace-sum(extras.values())
    h=brentq(lambda h:geometry(h)[2]-v,250,1100)
    w=ratio*h
    gross,brace,net=geometry(h)
    W,H=w+44,h+44
    shell=W*H*394e-6-gross-np.pi*(355.8/2)**2*44e-6
    # Solid rear plate simply supported on four edges, uniform 1 kPa.
    a,b=w*.001,h*.001
    rigidity=2e9*.022**3/(12*(1-.3**2))
    u=mx=my=volume_per_kPa=0.
    for m in range(1,32,2):
        for n in range(1,32,2):
            kx,ky=m*np.pi/a,n*np.pi/b
            term=16000*np.sin(m*np.pi/2)*np.sin(n*np.pi/2)/(np.pi**2*m*n*rigidity*(kx*kx+ky*ky)**2)
            # Integral of the sine-sine shape gives the swept air volume.
            modal_amplitude=term/(np.sin(m*np.pi/2)*np.sin(n*np.pi/2))
            volume_per_kPa+=modal_amplitude*4*a*b/(np.pi**2*m*n)
            u+=term
            mx+=rigidity*(kx*kx+.3*ky*ky)*term
            my+=rigidity*(ky*ky+.3*kx*kx)*term
    modes=sorted((np.pi/2*np.sqrt(rigidity/(800*.022))*((m/a)**2+(n/b)**2),m,n)
                 for m in range(1,4) for n in range(1,4))[:3]
    assert abs(net-v)<1e-6 and min(W,H)>400.4 and abs(394+38+18-450)<1e-9
    return dict(W=W,H=H,body_D=394,total_D=450,inner_mm=[w,h,depth],gross_L=gross,
                brace_L=brace,net_L=net,**extras,shell_MDF_L=shell,
                panel_mass_kg=.8*(shell+brace),rear_modes=modes,rear_center_mm_1kPa=u*1000,
                rear_center_MPa_1kPa=6*max(abs(mx),abs(my))/.022**2/1e6,
                rear_swept_cm3_per_kPa=volume_per_kPa*1e6,
                gas_first_axial_Hz=343/(2*max(a,b,.328)))


def placements(shapes, driver, volume):
    cfg=json.loads((ROOT/'dane/konfiguracje/p26_scenariusze.json').read_text())
    rec=np.array(cfg['assumed_listener_xyz_m'])+np.array(cfg['diagnostic_neighbor_offsets_xyz_m'])
    f=np.arange(20,81,1)
    # From free-field pressure to relative volume velocity: p_halfspace is proportional to f*U.
    raw=response(driver,volume,f)
    fc,q,_=alignment(driver,volume)
    freq_ratio=1j*f/80
    eq=sealed_shape(f,20,2**-.5)/sealed_shape(f,fc,q)/(1+2**.5*freq_ratio+freq_ratio**2)**2
    relative_flow=10**((raw['spl_rms_db']-raw['spl_rms_db'][20])/20)*abs(eq/eq[20])*40/f
    results={}
    for name,left,right,height in [('RTV',.70,3.0,shapes['A']['H']/2000+.02),
                                   ('boki',.50,3.20,shapes['C']['H']/2000+.02),
                                   ('A_obrot',.50,3.20,shapes['A']['W']/2000+.02),
                                   ('asym',.70,2.85,shapes['B']['H']/2000+.02)]:
        sources=[[left,.48,height],[right,.66 if name=='asym' else .48,height]]
        H=ModalRoom().transfer(f,sources,rec,.4,.2,kmax_m_inv=40)
        options=[]
        for delay in (-4,-2,0,2,4):
            for gain in (.35,.5,.65):
                p=H[:,:,0]*gain+(1-gain)*H[:,:,1]*np.exp(-2j*np.pi*f[:,None]*delay*.001)
                db=20*np.log10(np.abs(p)*relative_flow[:,None])
                options.append((float(np.ptp(db[:,0])),float(abs(db-db[:,[0]]).max()),delay,gain,db[:,0]))
        ripple,head,delay,gain,spectrum=min(options,key=lambda row:(round(row[0],8),row[1],abs(row[2])))
        controls=[]
        for t60,tau,kmax in ((.2,.02,40),(.8,2.,40),(.4,.2,60)):
            h=ModalRoom().transfer(f,sources,rec,t60,tau,kmax_m_inv=kmax)
            combined=gain*h[:,:,0]+(1-gain)*h[:,:,1]*np.exp(-2j*np.pi*f[:,None]*delay*.001)
            db=20*np.log10(abs(combined)*relative_flow[:,None])
            controls.append(dict(T60=t60,tau0=tau,kmax=kmax,ripple_dB=float(np.ptp(db[:,0])),
                                 peak_head_dB=float(abs(db-db[:,[0]]).max())))
        results[name]=dict(controls=controls,ripple_20_40_dB=float(np.ptp(spectrum[:21])),source_xyz=sources,ripple_20_80_dB=ripple,max_head_change_dB=head,
                          right_delay_ms=delay,left_share=gain,relative_to_40Hz_dB=(spectrum-spectrum[20]).tolist())
    return results


def main():
    pool={i:d for i,_,d,_ in candidates()}
    rows=list(csv.DictReader((ROOT/'wyniki/p29c_objetosc.csv').open()))
    score={int(r['volume_l']):float(r['stress_minband_db']) for r in rows}
    # Smallest nominal volume with a preliminary +/-3 litre construction budget.
    plateau=max(score.values())
    v=next(k for k in sorted(score) if k-3 in score and k+3 in score and
           min(score[j] for j in range(k-3,k+4))>=plateau-.2)
    shapes={n:cabinet(v,r) for n,r in [('A',1.8),('B',1.0),('C',.62)]}
    finalist_ids=('C02','C11','C06','C19')
    stress={i:{str(p):value(envelope(pool[i],v),p) for p in (25,50,100)} for i in finalist_ids}
    result=dict(stress_minband_dB=stress,net_target=v,robust_loss_dB=plateau-min(score[j] for j in range(v-3,v+4)),
                finalists=[audio(pool[i],v) for i in ('C02','C11','C06','C19')],
                volume_sweep=[audio(pool['C02'],k) for k in sorted(score)],
                shapes=shapes,room=placements(shapes,pool['C02'],v))
    (HERE/'s01_wyniki.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(v)
    for key,val in shapes.items():print(key,{k:round(val[k],2) for k in ('W','H','gross_L','brace_L','panel_mass_kg','rear_center_mm_1kPa','rear_center_MPa_1kPa')},val['rear_modes'][0])
    for r in result['finalists']:print(r['driver'],*[round(r[k],2) for k in ('fc','qtc','f3','eq_peak_dB','max_V','max_A','max_X_mm','max_Pcu_W','headroom_dB')])
    for k,r in result['room'].items(): print(k,r['ripple_20_80_dB'],r['max_head_change_dB'],r['right_delay_ms'],r['left_share'])


if __name__=='__main__':
    main()
