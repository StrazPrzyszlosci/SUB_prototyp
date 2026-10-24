"""Analityczne kandydaty optimum po dodatnim Vb, przy pojedynczym sinusie.

W tym modelu maksymalizujemy min(granicaX,granicaV,granicaI), bez Pe/THD.
Nie jest to optymalna skrzynia dla całej muzyki, DSP i konstrukcji.
"""
import numpy as np
from model_subwoofera import RHO,C


def roots_quadratic(a,b,c):
    scale=max(abs(a),abs(b),abs(c),1.)
    if a==0:
        return [] if b==0 else [-c/b]
    a,b,c=a/scale,b/scale,c/scale
    disc=b*b-4*a*c
    if disc<0:return []
    q=-.5*(b+np.copysign(np.sqrt(disc),b))
    if q==0:return [-b/(2*a)]
    return [q/a,c/q]


def global_bound(d,f_hz,vmax,imax,fraction=1.,tolerance_db=.5):
    if not all(np.isfinite(x) and x>0 for x in (f_hz,vmax,imax,fraction,tolerance_db)):
        raise ValueError('Dodatnie skończone parametry')
    w=2*np.pi*f_hz;l=d.le_mh*1e-3;b=d.bl;r=d.rms
    # kappa=Ks+Kb-M*w²; dozwolone kappa>=kmin (Kb>=0).
    kmin=1/d.cms-d.mms*w*w
    aa=d.re_ohm**2+(w*l)**2
    bb=2*w*w*l*b*b
    cc=w**4*l*l*r*r+w*w*(d.re_ohm*r+b*b)**2
    kv=-bb/(2*aa)
    candidates=[kmin,max(kmin,kv),max(kmin,0.)]
    # Rozwiązujemy w bezwymiarowej zmiennej kappa/kscale, aby nie porównywać
    # współczynników o różnych jednostkach ani nie usuwać małego członu kwadratowego.
    kscale=max(1/d.cms,d.mms*w*w)
    roots=roots_quadratic((vmax*vmax-imax*imax*aa)*kscale**2,
                     -imax*imax*bb*kscale,vmax*vmax*(w*r)**2-imax*imax*cc)
    candidates += [x*kscale for x in roots if x*kscale>=kmin]
    def velocity(k):
        # Bez rozwijania wielomianu przy ocenie, aby uniknąć znoszenia.
        den=(d.re_ohm*k-w*w*l*r)**2+(w*l*k+w*(d.re_ohm*r+b*b))**2
        gv=vmax*b*w/np.sqrt(den)
        gi=imax*b*w/np.hypot(k,w*r)
        gx=w*d.xmax_mm*1e-3*fraction/np.sqrt(2)
        return min(gv,gi,gx)
    velocities=[velocity(k) for k in candidates]
    index=int(np.argmax(velocities));maximum=velocities[index];chosen=candidates[index]
    target=maximum*10**(-tolerance_db/20)
    radv2=((vmax*b*w/target)**2-cc+bb*bb/(4*aa))/aa
    radi2=(imax*b*w/target)**2-(w*r)**2
    if min(radv2,radi2)<-1e-9:raise ArithmeticError('Brak realnego zakresu blisko optimum')
    radv,radi=np.sqrt(max(0,radv2)),np.sqrt(max(0,radi2))
    left=max(kmin,kv-radv,-radi);right=min(kv+radv,radi)
    if right<left-1e-7:raise ArithmeticError('Pusty przedział objętości')
    factor=RHO*C*C*d.sd*d.sd*1000 # Vb w litrach.
    return {'maximum_velocity_rms_m_s':maximum,
            'single_frequency_spl_2pi_1m_db':20*np.log10(RHO*w*d.sd*maximum/(2*np.pi*20e-6)),
            'candidate_vb_l':None if chosen==kmin else factor/(chosen-kmin),
            'candidate_is_infinite_volume_limit':bool(chosen==kmin),
            'within_db':tolerance_db,'vb_min_within_tolerance_l':None if right<=kmin else factor/(right-kmin),
            'vb_max_within_tolerance_l':None if left<=kmin else factor/(left-kmin),
            'kmin_n_m':kmin,'selected_kappa_n_m':chosen,'candidate_count':len(candidates)}
