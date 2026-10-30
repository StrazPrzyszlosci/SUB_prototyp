"""P21C0: exact rectangular Neumann modal series, uniform square piston.

Empty rigid lossless cavity. Restoring mean pressure at the source divided
by lumped-gas restoring pressure: 1 + sum a_n*k²/(k²-k_n²).
Nonzero modes have zero volume mean. Finite piston area is essential.
No driver, porous material, flexible wall, room or SPL is identified here.
"""
from pathlib import Path
import csv, hashlib, json, platform
import numpy as np
from scipy.integrate import quad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p21c0_geometria.json'


def axis_average(n, length, center, side):
    return np.cos(n*np.pi*center/length)*np.sinc(n*side/(2*length))


def response_3d(lengths, center, sides, frequencies, order, c):
    w,d,h=lengths
    nx,ny,nz=np.meshgrid(*(np.arange(order+1),)*3,indexing='ij')
    kn2=(np.pi*nx/w)**2+(np.pi*ny/d)**2+(np.pi*nz/h)**2
    coeff=axis_average(nx,w,center[0],sides[0])*axis_average(nz,h,center[1],sides[1])
    weights=2.**((nx>0).astype(int)+(ny>0).astype(int)+(nz>0).astype(int))*coeff**2
    mask=kn2>0
    kn2,weights=kn2[mask],weights[mask]
    return np.array([1+np.sum(weights*(2*np.pi*f/c)**2/((2*np.pi*f/c)**2-kn2)) for f in frequencies])


def response(lengths, center, sides, frequencies, order, c):
    """Sum the entire depth series analytically; truncate only transverse modes.

    sum_{ny>=0} eps_n/(q²-(pi*n/d)²) = d*cot(q*d)/q.
    For q=i*a this equals -d*coth(a*d)/a. All cases are below first mode.
    """
    w,d,h=lengths
    nx,nz=np.meshgrid(*(np.arange(order+1),)*2,indexing='ij')
    transverse=(np.pi*nx/w)**2+(np.pi*nz/h)**2
    coeff=axis_average(nx,w,center[0],sides[0])*axis_average(nz,h,center[1],sides[1])
    weights=2.**((nx>0).astype(int)+(nz>0).astype(int))*coeff**2
    result=[]
    for f in frequencies:
        k=2*np.pi*f/c;q2=k*k-transverse
        propagating=q2>0;term=np.empty_like(q2)
        q=np.sqrt(q2[propagating]);term[propagating]=d/(q*np.tan(q*d))
        a=np.sqrt(-q2[~propagating]);term[~propagating]=-d/(a*np.tanh(a*d))
        result.append(np.sum(weights*k*k*term))
    return np.array(result)


def write_csv(path, rows):
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def transverse_tail_bound(lengths, sides, frequency, order, c):
    """Analytic absolute tail bound, evaluated in floating point.

    Parseval: sum eps_n*avg(cos)^2 = L/side. For n>N, sinc² <=
    (2L/(pi*n*side))² and sum_{n>N} n^-2 <= 1/N. Bound the union
    of two omitted transverse strips; double counting only enlarges bound.
    """
    w,d,h=lengths;k=2*np.pi*frequency/c;bound=0.
    for length,side,other_length,other_side in [(w,sides[0],h,sides[1]),(h,sides[1],w,sides[0])]:
        a=np.sqrt((np.pi*(order+1)/length)**2-k*k)
        tail_weights=8*length*length/(np.pi**2*side*side*order)
        bound+=k*k*d/(a*np.tanh(a*d))*tail_weights*(other_length/other_side)
    return float(bound)


def main():
    cfg=json.loads(CFG.read_text());rows=[];convergence=[];checks=[]
    t=cfg['wall_m_assumed'];c=cfg['sound_speed_m_s_assumed'];freq=cfg['frequencies_hz']
    for volume in cfg['empty_internal_volume_l_cases']:
        for depth in cfg['external_depth_m_cases']:
            d=depth-2*t
            for aspect in cfg['internal_width_height_ratio_cases']:
                w=np.sqrt(volume*.001/d*aspect);h=w/aspect
                for side in cfg['square_piston_side_m_cases']:
                    for fraction in cfg['source_x_fraction_cases']:
                        center=(w*fraction,h/2)
                        fits=min(center[0],w-center[0],center[1],h-center[1])>=side/2
                        key=f'V{volume}_D{depth}_A{aspect}_S{side}_X{fraction}'
                        if not fits:
                            rows.append(dict(case_id=key,volume_l=volume,depth_ext_m=depth,width_ext_m=w+2*t,height_ext_m=h+2*t,
                                aspect=aspect,piston_side_m=side,source_fraction=fraction,fits=False,first_rigid_mode_hz=c/(2*max(w,d,h)),
                                f_hz='',restoring_pressure_ratio='',correction_db='',last_order_change='',analytic_tail_bound=''))
                            continue
                        answers=[response((w,d,h),center,(side,side),freq,n,c) for n in cfg['orders']]
                        delta=np.abs(answers[-1]-answers[-2]);rotated=response((h,d,w),(center[1],center[0]),(side,side),freq,cfg['orders'][-1],c)
                        assert np.max(np.abs(rotated-answers[-1]))<1e-12
                        assert max(freq)<c/(2*max(w,d,h))
                        for j,f in enumerate(freq):
                            rows.append(dict(case_id=key,volume_l=volume,depth_ext_m=depth,width_ext_m=w+2*t,height_ext_m=h+2*t,
                                aspect=aspect,piston_side_m=side,source_fraction=fraction,fits=True,first_rigid_mode_hz=c/(2*max(w,d,h)),
                                f_hz=f,restoring_pressure_ratio=answers[-1][j],correction_db=20*np.log10(abs(answers[-1][j])),last_order_change=delta[j],
                                analytic_tail_bound=transverse_tail_bound((w,d,h),(side,side),f,cfg['orders'][-1],c)))
                            convergence.append(dict(case_id=key,f_hz=f,**{f'order_{n}':answers[i][j] for i,n in enumerate(cfg['orders'])},
                                previous_change=abs(answers[1][j]-answers[0][j]),last_change=delta[j],rotation_error=abs(rotated[j]-answers[-1][j])))
    # Independent 1D closed tube with piston covering entire front.
    for depth in [.306,.456,.8]:
        for f in [20.,80.]:
            got=response_3d((.6,depth,.5),(.3,.25),(.6,.5),[f],120,c)[0]
            kd=2*np.pi*f/c*depth;exact=kd/np.tan(kd)
            summed=response((.6,depth,.5),(.3,.25),(.6,.5),[f],40,c)[0]
            assert abs(summed-exact)<1e-12
            # Exact series tail bounded by integral sum(n^-2), below first pole.
            tail=2*kd**2/(np.pi**2*120*(1-(kd/(np.pi*121))**2))
            assert abs(got-exact)<=tail*(1+1e-10)
            checks.append(dict(type='full_face_tube',depth_m=depth,f_hz=f,value=got,exact=exact,error=abs(got-exact),tail_bound=tail))
    # Independent, finite triple series approaches depth-summed solution from above
    # below the first mode (every omitted nonzero modal term is negative).
    for order in [10,20,40,80]:
        finite=response_3d((.99,.306,.495),(.2475,.2475),(.2,.2),[80.],order,c)[0]
        summed=response((.99,.306,.495),(.2475,.2475),(.2,.2),[80.],order,c)[0]
        assert finite>summed
        checks.append(dict(type='triple_series_vs_depth_sum',order=order,finite=finite,depth_summed=summed,gap=finite-summed))
    gaps=[r['gap'] for r in checks if r['type']=='triple_series_vs_depth_sum']
    assert all(b<a for a,b in zip(gaps,gaps[1:]))
    for order in [10,20,40,80,160]:
        finite=response((.99,.306,.495),(.2475,.2475),(.2,.2),[80.],order,c)[0]
        finer=response((.99,.306,.495),(.2475,.2475),(.2,.2),[80.],2*order,c)[0]
        bound=transverse_tail_bound((.99,.306,.495),(.2,.2),80.,order,c)
        assert 0<=finite-finer<=bound
        checks.append(dict(type='transverse_tail_bound_witness',order=order,change=finite-finer,bound=bound))
    # Independent quadrature of finite-area cosine source coupling.
    for n in [0,1,2,7,19]:
        val=quad(lambda x:np.cos(n*np.pi*x/.8),.1,.3,epsabs=1e-12)[0]/.2
        exact=axis_average(n,.8,.2,.2)
        assert abs(val-exact)<1e-12
        checks.append(dict(type='source_quadrature',mode=n,error=float(abs(val-exact))))
    write_csv(OUT/'p21c0_geometria_i_port.csv',rows);write_csv(OUT/'p21c0_zbieznosc.csv',convergence)
    admitted=[r for r in rows if r['fits']];worst=max(admitted,key=lambda r:abs(1-r['restoring_pressure_ratio']))
    summary=dict(status='EMPTY_RIGID_CAVITY_PILOT_NOT_COMPLETE_P21C',date='2026-10-29',
        geometry_count=27,source_cases=108,accepted_source_cases=len({r['case_id'] for r in admitted}),
        rejected_source_cases=sum(not r['fits'] for r in rows),frequency_points=len(admitted),
        max_last_order_absolute_change=max(r['last_order_change'] for r in admitted),worst_case=worst,
        max_analytic_tail_bound=max(r['analytic_tail_bound'] for r in admitted),
        independent_checks=checks,libraries=dict(Python=platform.python_version(),NumPy=np.__version__),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CFG,Path(__file__)]},
        limitations=cfg['limitations'])
    (OUT/'p21c0_podsumowanie.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    fig,axes=plt.subplots(1,2,figsize=(11,4.4))
    for fraction,style in [(0.5,'-'),(.25,'--')]:
        for volume,color in [(60,'#1c827d'),(100,'#b16a22'),(150,'#66549c')]:
            selected=[r for r in admitted if r['volume_l']==volume and r['depth_ext_m']==.5 and r['aspect']==1.5 and r['piston_side_m']==.2 and r['source_fraction']==fraction]
            axes[0].plot([r['f_hz'] for r in selected],[100*(r['restoring_pressure_ratio']-1) for r in selected],style,color=color,label=f'{volume} l, x/W={fraction}')
    axes[0].set(xlabel='Częstotliwość [Hz]',ylabel='Zmiana nacisku zwrotnego względem 0D [%]',title='D=500 mm, W/H=1,5, tłok kwadratowy 200 mm')
    axes[0].legend(fontsize=7);axes[0].grid(alpha=.2)
    for depth,color in [(.35,'#1c827d'),(.425,'#b16a22'),(.5,'#66549c')]:
        selected=[r for r in admitted if r['depth_ext_m']==depth and r['f_hz']==80 and r['source_fraction']==.25 and r['piston_side_m']==.2]
        axes[1].scatter([r['first_rigid_mode_hz'] for r in selected],[100*abs(1-r['restoring_pressure_ratio']) for r in selected],label=f'D={depth*1000:g} mm',color=color)
    axes[1].set(xlabel='Najniższy mod sztywnej pustej komory [Hz]',ylabel='Moduł korekty nacisku przy 80 Hz [%]',title='Pozycja w środku połowy frontu, 27 geometrii')
    axes[1].legend(fontsize=8);axes[1].grid(alpha=.2)
    fig.suptitle('Model gazu: brak włókniny, wkładów i podatności ścian; korekta nie jest zmianą SPL',fontsize=10)
    fig.tight_layout();fig.savefig(OUT/'95_P21C0_plytka_komora.png',dpi=170);plt.close(fig)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['independent_checks','input_sha256','limitations']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
