#!/usr/bin/env python3
"""K34 exploratory 1D plate/foundation and portal support models; N/mm/MPa."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from scipy.linalg import solve
R=Path(__file__).resolve().parents[1]
def beam_matrix(n,length,EI):
 h=length/(n-1);K=np.zeros((2*n,2*n))
 ke=EI/h**3*np.array([[12,6*h,-12,6*h],[6*h,4*h*h,-6*h,2*h*h],[-12,-6*h,12,-6*h],[6*h,2*h*h,-6*h,4*h*h]])
 for i in range(n-1):K[2*i:2*i+4,2*i:2*i+4]+=ke
 return K

def plate(Ez,Ep,Fmain,Fret,n=81):
 # Gross unperforated strip. Springs are lumped normal compression only.
 z=np.linspace(-40,40,n);dx=z[1]-z[0];areas=np.full(n,18*dx);areas[[0,-1]]/=2
 k=Ez/22*areas;K=beam_matrix(n,80,Ep*18*4**3/12);f=np.zeros(2*n)
 for p,F in [(0,Fmain),(-32,Fret),(32,Fret)]:f[2*int(round((p+40)/dx))]+=F
 active=np.ones(n,dtype=bool)
 for it in range(100):
  A=K.copy();A[np.arange(n)*2,np.arange(n)*2]+=k*active
  u=solve(A,f,assume_a='sym');new=u[::2]>0
  if np.array_equal(active,new):break
  active=new
 else:raise RuntimeError('contact did not converge')
 reaction=k*np.maximum(u[::2],0);pressure=reaction/areas
 assert abs(sum(reaction)-sum(f))<1e-3, (n, sum(reaction)-sum(f))
 return dict(Ez_MPa=Ez,Ep_MPa=Ep,Fmain_N=Fmain,Fret_each_N=Fret,n=n,iterations=it+1,
  peak_gross_strip_pressure_MPa=float(max(pressure)),mean_gross_pressure_MPa=float(sum(f)/1440),
  peak_displacement_mm=float(max(u[::2])),contact_length_mm=float(sum(areas[active])/18),
  reaction_sum_N=float(sum(reaction)),applied_sum_N=float(sum(f)),z_mm=z.tolist(),pressure_MPa=pressure.tolist())

def unsupported_web(F):
 # Front adhesive edge deliberately absent; end supports at Z22/478 only.
 n=229;L=456;K=beam_matrix(n,L,2000*20*22**3/12);f=np.zeros(2*n)
 for zz in (66,182,298,404):f[2*int(zz/2)]+=F
 free=np.array([i for i in range(2*n) if i not in (0,2*n-2)])
 u=np.zeros(2*n);u[free]=solve(K[np.ix_(free,free)],f[free],assume_a='sym')
 r=K@u-f
 return dict(assumed_E_MPa=2000,force_per_bolt_N=F,deflection_mm=float(max(u[::2])),support_reactions_N=[float(r[0]),float(r[-2])],applied_N=4*F,
  note='Counterfactual unbonded front edge, no ribs/rear coupling; not full portal FEM.')

def main():
 k33=json.loads((R/'wyniki/k33_sztywna_blokada.json').read_text());b=k33['beam'][1];P=max(b['reactions_N'])
 preload=[]
 for Fi in (50,100,300,600):
  for C in (.1,.3,.5):
   sep=Fi<(1-C)*P
   bolt=P if sep else Fi+C*P;clamp=0 if sep else Fi-(1-C)*P
   preload.append(dict(preload_N=Fi,C=C,external_N=P,separated=sep,bolt_N=bolt,remaining_clamp_N=clamp,net_to_portal_N=bolt-clamp))
 cases=[plate(Ez,Ep,600,30) for Ez in (50,150,500) for Ep in (70000,200000)]
 convergence=[plate(150,200000,600,30,n) for n in (81,161,321)]
 # The actual bonded perimeter is geometric contact, not qualified adhesive.
 shear=dict(front_edge_area_mm2=22*456,rear_edge_area_mm2=22*456,top_edge_area_mm2=22*366,bottom_edge_area_mm2=22*366,
  assumed_front_only_load_N=4*b['reactions_N'][0],assumed_rear_only_load_N=4*b['reactions_N'][1],
  front_mean_shear_MPa=4*b['reactions_N'][0]/(22*456),rear_mean_shear_MPa=4*b['reactions_N'][1]/(22*456),
  note='Four rows loaded as large rows: common conservative scenario, not exact100L mass distribution. No preload added to global net force.')
 fit=dict(nominal_depth_mm=366,nominal_height_mm=456,depth_total_gap_range_mm=[-1.6,1.6],height_total_gap_range_mm=[-1.1,1.1],assumption='External D432/H500 held exactly; stock each±0.5, portal XY±0.1; not assembled tolerance.',measured_rule='panel_span=measured_cavity_span-2*g',trial_gap_each_mm=.2,measured_total_gap_range_mm=[.25,.55],measurement_assumption='Cavity measurement error±0.05 and panel cut±0.1; g unqualified.')
 out=dict(frame_fit=fit,status='CNC_HOLD',preload=preload,plate_cases=cases,convergence=convergence,edge_transfer=shear,loss_of_front_edge_bond=unsupported_web(P),
  inputs={'MDF_thickness_mm':22,'plate_gross_mm':[18,80,4],'retention_preload_each_N':30,'material_values':'assumed, not measured','load_source':'K33 maximum reaction including own mass'},
  limitations=['1D gross strip omits bores, local thread and edge splitting','Winkler independent springs omit MDF orthotropy/shear/creep','C values and preload are hypothetical, no torque instruction','No qualified bond, no cabinet plate coupling'])
 (R/'wyniki/k34_docisk_i_wrega.json').write_text(json.dumps(out,indent=2)+'\n')
 files=['brief_system_audio_DIY_v0.6.md','wyniki/k33_sztywna_blokada.json','wyniki/k32_retencja.json','skrypty/k34_docisk_i_wrega.py']
 (R/'wyniki/k34_manifest.json').write_text(json.dumps({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
 print(json.dumps({'pressure_range':[min(c['peak_gross_strip_pressure_MPa'] for c in cases),max(c['peak_gross_strip_pressure_MPa'] for c in cases)],'convergence':[c['peak_gross_strip_pressure_MPa'] for c in convergence],'edge':shear,'loss':out['loss_of_front_edge_bond']},indent=2))
if __name__=='__main__':main()
