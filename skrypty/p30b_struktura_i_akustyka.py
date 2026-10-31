#!/usr/bin/env python3
"""P30B/P30C analytic cross-check: Kirchhoff simply supported plate and
ideal second order closed-box T/S, demonstrative sensitivity only, NOT FEM.
All material properties and T/S variation are assumed, not measured.
"""
from pathlib import Path
import math, json, itertools
from statistics import mean
ROOT=Path(__file__).resolve().parent
ROOT=(ROOT.parent/"wyniki") if ROOT.name=="skrypty" else ROOT
GEOM=json.loads((ROOT/'p30a_geometria_przeglad_20261031.json').read_text())

def plate_f11(a,b,E,rho,t=.022,nu=.3):
    D=E*t**3/(12*(1-nu**2))
    return math.pi/2 * math.sqrt(D/(rho*t))*(1/a**2+1/b**2)

def navier_center_deflection_per_Pa(a,b,E,t=.022,nu=.3,lim=15):
    D=E*t**3/(12*(1-nu**2))
    total=0.
    for m in range(1,lim+1,2):
      for n in range(1,lim+1,2):
        sgn=(-1)**((m-1)//2+(n-1)//2)
        total+=sgn/(m*n*((m/a)**2+(n/b)**2)**2)
    return 16*total/(math.pi**6*D)

def box_params(fs,qts,vas,v):
    r=math.sqrt(1+vas/v); q=qts*r; fc=fs*r
    A=2-1/q**2
    y=(-A+math.sqrt(A*A+4))/2
    f3=fc*math.sqrt(y)
    def db(f):
       z=f/fc
       return 20*math.log10(z*z/math.sqrt((1-z*z)**2+(z/q)**2))
    return dict(fc_hz=fc,qtc=q,f3_hz=f3,db20=db(20),db40=db(40))

def run():
  structural=[];acoustic=[];ref=[]
  for g in GEOM['tested_variants']:
    w=g['width_mm']; d=g['body_depth_mm']; inside=g['inside_mm']
    for E,rho,span in itertools.product([1.5e9,2e9,2.5e9,3e9,4e9],[650,730,800],['full','ideally_split']):
       a=(inside[0] if span=='full' else 300)/1000
       b=inside[1]/1000
       f=plate_f11(a,b,E,rho)
       # static uniform pressure center deflection per Pa, 15-terms series
       w0=navier_center_deflection_per_Pa(a,b,E)
       structural.append(dict(outer_width_mm=w,outer_depth_mm=d,fill_mm=g['rear_mat_thickness_mm'],
            E_GPa=E/1e9,rho_kg_m3=rho,ideal_support=span,f11_hz=round(f,5),
            midspan_static_um_per_kPa=round(w0*1e9,6)))
    for nominal_set, cfg in g['family_p20d_counts'].items():
      for v in [cfg['net_stress_l'][0],cfg['net_nom_l'],cfg['net_stress_l'][1]]:
        for vas,qts in itertools.product([190,212,234],[.38,.43,.48]):
          x=box_params(19.5,qts,vas,v)
          acoustic.append(dict(width_mm=w,body_depth_mm=d,fill_mm=g['rear_mat_thickness_mm'],
            state=nominal_set, vnet_l=round(v,4), vas_l=vas,qts=qts,
            fc_hz=round(x['fc_hz'],4),qtc=round(x['qtc'],5),f3_hz=round(x['f3_hz'],4),
            normalized_20hz_db=round(x['db20'],4)))
  # independent analytical checks: uniform load navier convergence; a=b square f11 exact formula
  for g in GEOM['tested_variants']:
    a=g['inside_mm'][0]/1000;b=g['inside_mm'][1]/1000
    d11=navier_center_deflection_per_Pa(a,b,2.1e9,lim=11)
    d21=navier_center_deflection_per_Pa(a,b,2.1e9,lim=21)
    f11=plate_f11(a,b,2.1e9,730)
    sq_f=plate_f11(.3,.3,2.1e9,730)
    ref.append(dict(w_mm=g['width_mm'],d_mm=g['body_depth_mm'],
      full_panel_nominal_f11_hz=round(f11,4),
      split_300mm_nominal_f11_hz=round(plate_f11(.3,b,2.1e9,730),4),
      static_11_um_per_kPa=round(d11*1e9,7),static_21_um_per_kPa=round(d21*1e9,7),
      navier_rel_diff=abs(d21-d11)/max(abs(d21),1e-18)))
  assert len(structural)==6*5*3*2
  assert len(acoustic)==6*3*3*3*3
  assert all(x['f11_hz']>0 for x in structural)
  assert max(x['navier_rel_diff'] for x in ref)<.001
  assert all(x['f3_hz']>0 for x in acoustic)
  # for each volume nominal 5% change of T/S should be bounded by computed extremes; no claims distribution.
  result=dict(date='2026-10-31',study='P30B_P30C',
    theoretical_scope='Simply supported isotropic Kirchhoff plate + lossless sealed T/S second-order (no geometry coupling)',
    structural_case_count=len(structural),acoustic_case_count=len(acoustic),
    structural=structural,acoustic=acoustic,baseline_comparisons=ref,
    material_assumptions={'E_GPa':[1.5,2,2.5,3,4], 'rho_kg_m3':[650,730,800], 'poisson':.3, 'wall_t_mm':22,
      'support_scenarios':['full unbraced panel','artificial rigid support with 300mm span']},
    acoustic_assumptions={'driver':'C02 Dayton RSS390HF-4','fs_hz':19.5,'vas_l':[190,212,234],
      'qts':[.38,.43,.48],'vnet_l':'3 finite stress states from P30A',
      'omissions':'no damping, leaks, filling acoustic effect, driver nonlinearities or room'},
    limits=[
      'Ideal 300-mm panel supports are NOT actual ring brace stiffness; P18E found 143Hz reduced-mode for existing layout versus naive 395Hz ideal field.',
      'Full-panel and ideal-support plate frequencies bound neither the physical enclosure nor the electromagnetic/acoustic output.',
      'Material E and density, Qts Vas and net volume ranges are arbitrary parameter stress cases; not calibrated probabilities or component specs.',
      'The rear mat thickness changes 50->30mm between designs; no claim of equal acoustic damping.',
      'No new hardware, manufacturing drawing, FEM coupling or full enclosure assembly testing.'])
  (ROOT/'p30bc_paneli_ts_20261031.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  print('STRUCTURAL',len(structural),'ACOUSTIC',len(acoustic),'NAVIER',max(x['navier_rel_diff'] for x in ref))
  for r in ref:print('PANEL',r)
  for g in GEOM['tested_variants']:
     selected=[x for x in acoustic if x['width_mm']==g['width_mm'] and x['body_depth_mm']==g['body_depth_mm'] and x['state']=='120_l']
     print('ACOUSTIC',g['width_mm'],g['body_depth_mm'],'F3minmax',min(x['f3_hz'] for x in selected),max(x['f3_hz'] for x in selected))
if __name__=='__main__':run()
