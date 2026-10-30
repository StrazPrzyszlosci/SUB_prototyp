from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy.sparse.linalg import eigsh,spsolve
from scipy.signal import bilinear,bilinear_zpk,zpk2sos,sosfreqz,butter
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import RHO,C,alignment
from front_przesuniety_P18D import Offset
from model_frontu_z_otworem_P18B import FrontWithHole
from model_plyty_MITC_P18 import PlateMaterial
from wklady_przestrzenne_P21C3 import boxes,W,H,D
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
def overlap(a,b):return all(min(a[i+1],b[i+1])-max(a[i],b[i])>1e-9 for i in [0,2,4])
def swept(a,b):return tuple(v for i in [0,2,4] for v in [min(a[i],b[i]),max(a[i+1],b[i+1])])
def block(center):
 return tuple(v for q,half in zip(center,[.09,.085,.05]) for v in [q-half,q+half])
def main():
 checks=[];pool=candidates();samples=np.load(O/'p29a_stress_samples.npy')
 # Independent physical I,v,x linear system and input energy, selected stress witnesses.
 maxerr=maxenergy=0
 for cid,pid,d,cat in pool:
  for ix in [0,99,188,512]:
   m,cm,bl,rm,re,le,sd,vb,beta,extra,xf,theta=samples[ix];M=d.mms*m;Cm=d.cms*cm;BL=d.bl*bl;Rm=d.rms*(rm+extra);Re=d.re_ohm*re*(1+.004*theta);Le=d.le_mh*.001*le;Sd=d.sd*sd
   for f in [20,40,80]:
    s=2j*np.pi*f;K=1/Cm+RHO*C*C*Sd*Sd*beta/(.12*vb);zm=Rm+s*M+K/s;ze=Re+s*Le
    ia=1/(ze+BL*BL/zm);va=BL*ia/zm
    i,v,x=np.linalg.solve([[ze,BL,0],[-BL,Rm+s*M,K],[0,1,-s]],[1,0,0])
    maxerr=max(maxerr,abs(i/ia-1),abs(v/va-1));maxenergy=max(maxenergy,abs(i.real-Re*abs(i)**2-Rm*abs(v)**2)/max(i.real,1e-12))
 checks.append(dict(test='independent_324_I_v_x_energy',relative_error=float(maxerr),energy_relative=float(maxenergy)));assert maxerr<1e-11 and maxenergy<1e-11
 # Compare new offset mesh to original central-hole implementation.
 a=Offset(.88,.5,.44,.25,.1779,.044,12);b=FrontWithHole(.88,.5,.1779,PlateMaterial(2.1e9,.3,730,.044),12,6)
 err=np.linalg.norm((a.full_K-b.full_K).data)/np.linalg.norm(b.full_K.data);assert err<1e-12;checks.append(dict(test='offset_mesh_central_reduction',relative_error=float(err)))
 # Installation path for each box: through hole at source center, move row, move x, then depth.
 # Deep layer then front; in each row farther-right first prevents blocking.
 placed=[];paths=[]
 targets=boxes(16);targets=sorted(targets,key=lambda b:(-(b[2]+b[3]),b[4],-b[0]))
 for tar in targets:
  cx=(tar[0]+tar[1])/2;cy=(tar[2]+tar[3])/2;cz=(tar[4]+tar[5])/2
  centers=[(W/4,.095,H/2),(W/4,.095,cz),(cx,.095,cz),(cx,cy,cz)]
  # The moving box starts entirely inside after passing circular front aperture.
  assert np.hypot(.09,.05)<.1779
  for ca,cb in zip(centers,centers[1:]):
   sw=swept(block(ca),block(cb));assert all(sw[i]>=-1e-9 and sw[i+1]<=L+1e-9 for i,L in zip([0,2,4],[W,D,H]))
   assert not any(overlap(sw,bx) for bx in placed)
  assert not any(overlap(tar,bx) for bx in placed);placed.append(tar);paths.append(centers)
 checks.append(dict(test='16_installation_paths_empty_shell',segments=48,passed=True,exclusions='Driver removed. Braces, fasteners, tool access and handling NOT modelled; must preserve swept corridors.'))
 # Routing, symbolic architecture + sampled LR4 identity, no monitor-specific fit.
 routing=np.array([[1,0],[1,0],[1,0],[0,1],[0,1],[0,1],[.5,.5],[.5,.5]])
 assert np.max(np.sum(abs(routing),axis=1))==1
 f=np.geomspace(1,10000,1000);s=2j*np.pi*f;wc=2*np.pi*80;den=s*s+np.sqrt(2)*wc*s+wc*wc;lp=(wc*wc/den)**2;hp=(s*s/den)**2
 assert max(abs(abs(lp+hp)-1))<1e-12
 checks.append(dict(test='eight_channel_routing_and_ideal_LR4',max_row_l1=1,LR4_max_magnitude_error=float(max(abs(abs(lp+hp)-1))),limitation='Ideal acoustic monitor response. Delay and actual phase require measurements.'))
 # Software starting filters, no inverse large EQ; 96k only, no Dirac.
 fs=96000;sos=np.vstack([butter(2,20,'high',fs=fs,output='sos'),butter(2,80,'low',fs=fs,output='sos'),butter(2,80,'low',fs=fs,output='sos')]);poles=np.concatenate([np.roots(sec[3:]) for sec in sos]);assert max(abs(poles))<1
 (ROOT/'dane/konfiguracje/p29_filtry_startowe_96k.json').write_text(json.dumps(dict(fs=fs,HP='BW2 20Hz',LP='LR4 80Hz',sos=sos.tolist(),routing=routing.tolist(),scope='Software coefficients, NOT validated hardware preset or X/T protection. No automatic EQ boost.',max_pole_radius=float(max(abs(poles)))),indent=2))
 # Geometric volume and provisional mass budget.
 area=W*H;gross=area*D*1000;mat=area*.05;solid_mat=mat*.02*1000;rho=730;wood=.88*.5*.48-W*H*D-np.pi*.1779**2*.044
 geometry=dict(outside_W_D_H_mm=[880,480,500],max_overall_depth_with_grille_mm=500,grille_depth_budget_mm=20,inside_W_D_H_mm=[836,414,456],front_mm=44,other_walls_mm=22,source_center_from_outside_left_bottom_mm=[231,250],catalog_cutout_mm=355.8,cutout_tolerance='not CNC release; final clearance from physical unit/drawing',gross_empty_l=gross,driver_brace_hardware_reserve_nominal_l=8,reserve_stress_l=[4,11],porous_back_layer_mm=50,porous_envelope_l=mat*1000,porosity_assumed=.98,polyester_dry_density_assumed_kg_m3=20,nominal_dry_fill_mass_kg=mat*20,shell_mass_assumed_kg=wood*rho,module_outside_mm=[180,170,100],module_count_options=[0,10,16],module_mount='positive mechanical retention in all orientations; no loose blocks',module_paths=paths,configurations=[])
 for n in [0,10,16]:geometry['configurations'].append(dict(modules=n,nominal_net_air_l=gross-8-solid_mat-n*3.06,net_air_range_l=[gross-11-solid_mat-n*3.06,gross-4-solid_mat-n*3.06],rigid_module_displacement_l=n*3.06))
 (ROOT/'dane/konfiguracje/rekomendacja_prototypu_P29.json').write_text(json.dumps(geometry,indent=2))
 checks.append(dict(test='volume_accounting',geometry=geometry['configurations']))
 (O/'p29_kontrole_i_geometria.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
