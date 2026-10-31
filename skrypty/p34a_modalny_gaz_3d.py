#!/usr/bin/env python3
"""P34A - acoustic finite-disk source modal expansion in rigid Neumann box.
Equivalent-volume cuboids ONLY; does not reproduce spatial P30E insert blocks.
Usage: python skrypty/p34a_modalny_gaz_3d.py --out wyniki/p34a_modalny_gaz_20261031.json
Requires numpy scipy. An embedded modal truncation study tests 4/6/8/10/12 modes/axis.
"""
import argparse, json, math
import numpy as np
from scipy.special import j1

C=343.; R=.3558/2; DEP=.359; HEIGHT=.456; XC=.231; ZC=.25; ZETA=.03
FREQUENCIES=[20,40,60,80,100,150]
MODES=[4,6,8,10,12]
VOLUMES=[.100,.120,.150]

def evaluate(V,f,N,gridpoints=(13,7,9)):
    # Artificial equivalence: box has correct volume but real P30E modules are NOT along an end cut.
    lx=V/(DEP*HEIGHT);ly=DEP;lz=HEIGHT
    assert XC+R<lx, 'piston must fit in this hypothetical box'
    axes=[(np.arange(n)+.5)*length/n for n,length in zip(gridpoints,(lx,ly,lz))]
    xx,yy,zz=np.meshgrid(*axes,indexing='ij')
    x=xx.ravel();y=yy.ravel();z=zz.ravel()
    pressure=np.ones(x.shape,dtype=complex)
    wave=2*math.pi*f/C
    for nx in range(N+1):
        kx=nx*math.pi/lx
        a=np.cos(kx*x)
        sx=np.cos(kx*XC)
        for ny in range(N+1):
            ky=ny*math.pi/ly
            b=np.cos(ky*y)
            for nz in range(N+1):
                if nx==ny==nz==0:continue
                kz=nz*math.pi/lz
                kval=(kx*kx+ky*ky+kz*kz)**.5
                arg=R*(kx*kx+kz*kz)**.5
                piston=2*j1(arg)/arg if arg>1e-14 else 1.
                source=sx*np.cos(kz*ZC)*piston
                mult=2**(int(nx>0)+int(ny>0)+int(nz>0))
                weight=-(wave*wave)*mult*source/(kval*kval-wave*wave+2j*ZETA*kval*wave)
                pressure+=weight*a*b*np.cos(kz*z)
    amp=np.abs(pressure)
    return dict(volume_l=round(V*1000),f_hz=f,modes_per_axis=N,
                first_mode_hz=C/(2*max(lx,ly,lz)),equivalent_length_m=lx,
                max_amplitude_departure_pct=float(100*np.max(abs(amp-1))),
                rms_amplitude_departure_pct=float(100*np.sqrt(np.mean((amp-1)**2))),
                amplitude_95th_minus_one_pct=float(100*(np.percentile(amp,95)-1)),
                max_complex_departure_pct=float(100*np.max(abs(pressure-1))),
                max_abs_phase_deg=float(np.max(abs(np.rad2deg(np.angle(pressure))))))

def run():
    rows=[evaluate(v,f,n) for v in VOLUMES for f in FREQUENCIES for n in MODES]
    assert len(rows)==90
    for v in VOLUMES:
        for f in FREQUENCIES:
            a=next(x for x in rows if x['volume_l']==round(v*1000) and x['f_hz']==f and x['modes_per_axis']==10)
            b=next(x for x in rows if x['volume_l']==round(v*1000) and x['f_hz']==f and x['modes_per_axis']==12)
            a['max_departure_convergence_10vs12_percentage_points']=abs(a['max_amplitude_departure_pct']-b['max_amplitude_departure_pct'])
    return dict(study='P34A',date='2026-10-31',cases=len(rows),records=rows,
        physics='Analytic rigid-box Neumann modes, source disk Bessel J1 form factor, ζ=3% diagnostic mode damping',
        geometry=dict(physical_inner_w_d_h_m=[.976,.359,.456],equivalent_box_w_from_v_l=[100,120,150],
             disk_radius_m=R,source_xz_m=[XC,ZC]),
        warnings=[
          '100/120/150L states are fictitious equivalent rectangular cavities with shortened x; NOT actual P30E inserts, braces or porous mat.',
          'No coupled wall motion or driver acoustic impedance; assumed rigid walls, speed 343m/s and mode damping ζ=0.03.',
          'Uniform piston velocity and disk form factor; actual basket and front clearance unknown.',
          'Grid 13x7x9 interior sample locations, near-wall peak may differ; modal truncation tested N=4/6/8/10/12.',
          'No nonlinear distortion, sound pressure outside the box, or 0D alignment validation.',
          'P33C FEM hourglass issue is separate; this analytical acoustic control does not validate P33B.'
        ])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='wyniki/p34a_modalny_gaz_20261031.json')
    args=ap.parse_args()
    result=run()
    with open(args.out,'w',encoding='utf8') as fd:json.dump(result,fd,ensure_ascii=False,indent=2)
    print('P34A',len(result['records']),'modal evaluations')
