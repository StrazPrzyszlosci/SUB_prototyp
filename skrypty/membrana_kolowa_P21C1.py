"""Rigid empty cavity, uniform circular piston of catalog-equivalent Sd.
Derived cosine transform of a disk; no claim about cone/basket geometry.
Depth summed exactly. Parseval bounds transverse tail, float evaluation.
"""
from pathlib import Path
import json, hashlib, platform
import numpy as np
import scipy
from scipy.special import j1
from scipy.integrate import quad
from analiza_rozszerzenia_SB import candidates, BASE, EXT
from pilot_P21C_geometria import response as square_response, write_csv
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p21c1_membrana.json'

def disk_coeff(nx,nz,w,h,x,z,a):
    u=a*np.sqrt((np.pi*nx/w)**2+(np.pi*nz/h)**2)
    shape=np.ones_like(u,dtype=float);np.divide(2*j1(u),u,out=shape,where=u!=0)
    return np.cos(np.pi*nx*x/w)*np.cos(np.pi*nz*z/h)*shape

def solve(lengths,center,a,freq,N,c,rho):
    w,d,h=lengths; nx,nz=np.meshgrid(np.arange(N+1),np.arange(N+1),indexing='ij')
    q2=(np.pi*nx/w)**2+(np.pi*nz/h)**2
    weights=2.**((nx>0).astype(int)+(nz>0).astype(int))*disk_coeff(nx,nz,w,h,*center,a)**2
    # Parseval of indicator_disk/area in the rectangular cosine basis.
    total=w*h/(np.pi*a*a); residual=total-float(weights.sum())
    assert residual>=-1e-11*total
    residual=max(0.,residual)
    omitted_q=min(np.pi*(N+1)/w,np.pi*(N+1)/h)
    result=[]; bounds=[]
    for f in freq:
        k=2*np.pi*f/c; s=q2-k*k;term=np.empty_like(s)
        mask=s>0;al=np.sqrt(s[mask]);term[mask]=-d/(al*np.tanh(al*d))
        be=np.sqrt(-s[~mask]);term[~mask]=d/(be*np.tan(be*d))
        result.append(float(np.sum(weights*k*k*term)))
        amin=np.sqrt(omitted_q**2-k*k)
        bounds.append(float(residual*k*k*d/(amin*np.tanh(amin*d))))
    q=np.sqrt(q2[1:,:]); # zero mode handled separately below
    nzmask=q2>0;al=np.sqrt(q2[nzmask])
    mass=rho*(np.pi*a*a)**2/(w*d*h)*(d*d/3+np.sum(weights[nzmask]*d/(al*np.tanh(al*d))))
    mb=rho*(np.pi*a*a)**2/(w*d*h)*residual*d/(omitted_q*np.tanh(omitted_q*d))
    return np.array(result),np.array(bounds),float(mass),float(mb)

def main():
    cfg=json.loads(CFG.read_text());freq=cfg['frequencies_hz'];c=cfg['c_m_s'];rho=cfg['rho_kg_m3'];t=cfg['wall_m'];orders=cfg['orders']
    products={pid:(d.name,d.sd) for cid,pid,d,cat in candidates()};rows=[];excluded=[];pairs=[];checks=[]
    for v in cfg['volumes_l']:
      for de in cfg['depth_ext_m']:
       d=de-2*t
       for aspect in cfg['width_height']:
        w=np.sqrt(v*.001/d*aspect);h=w/aspect
        for pid,(name,area) in products.items():
         a=np.sqrt(area/np.pi);answers={}
         for frac in [.5,.25]:
          x=w*frac;z=h/2;key=f'{pid}_V{v}_D{de}_A{aspect}_X{frac}'
          if min(x,w-x,z,h-z)<a:
           excluded.append(dict(case=key,product=pid,radius_m=a,available_radius_m=min(x,w-x,z,h-z)));continue
          assert max(freq)<c/(2*max(w,d,h))
          allans=[solve((w,d,h),(x,z),a,freq,n,c,rho) for n in orders]
          rr,bb,m,mb=allans[-1];delta=np.abs(rr-allans[-2][0]);answers[frac]=(rr,bb,m,mb)
          assert np.all(allans[-2][0]>=rr-1e-12)
          assert np.all(delta<=allans[-2][1]+1e-12)
          sq=square_response((w,d,h),(x,z),(np.sqrt(area),)*2,freq,orders[-1],c)
          # disk fit implies equal-area square fit (smaller half-side).
          for j,f in enumerate(freq):
           rows.append(dict(case=key,product=pid,model=name,volume_l=v,depth_ext_m=de,aspect=aspect,width_ext_m=w+2*t,height_ext_m=h+2*t,sd_m2=area,radius_m=a,x_fraction=frac,f_hz=f,R=rr[j],tail_bound=bb[j],last_change=delta[j],square_R=sq[j],circle_minus_square=rr[j]-sq[j],added_mass_kg=m,mass_tail_bound_kg=mb))
         if len(answers)==2:
          ce,off=answers[.5],answers[.25]
          pairs.append(dict(product=pid,volume_l=v,depth_ext_m=de,aspect=aspect,delta_mass_kg=off[2]-ce[2],delta_mass_lower_kg=off[2]-ce[2]-ce[3],delta_mass_upper_kg=off[2]-ce[2]+off[3],R80_center=ce[0][-1],R80_offset=off[0][-1]))
    # Independent disk integral: integrate the vertical chord analytically and x by quad.
    for n,l in [(0,0),(1,0),(0,2),(3,4),(11,7),(40,20)]:
     w,h,x,z,a=.7,.5,.2,.25,.12;kx=n*np.pi/w;kz=l*np.pi/h
     def integrand(dx):
      b=np.sqrt(max(0,a*a-dx*dx))
      vertical=2*b if l==0 else 2*np.cos(kz*z)*np.sin(kz*b)/kz
      return np.cos(kx*(x+dx))*vertical/(np.pi*a*a)
     val=quad(integrand,-a,a,epsabs=1e-11,limit=300)[0]
     exact=float(disk_coeff(np.array(n),np.array(l),w,h,x,z,a))
     assert abs(val-exact)<2e-10
     checks.append(dict(test='independent_disk_integral',n=n,l=l,error=abs(val-exact)))
    for a in [.08,.12,.16]:
     args=((.8,.4,.5),(.2,.25),a,[.1,20,80],320,c,rho)
     rr,bb,m,mb=solve(*args)
     rot=solve((.5,.4,.8),(.25,.2),a,[.1,20,80],320,c,rho)
     assert np.max(abs(rr-rot[0]))<1e-12
     inferred=(1-rr[0])*rho*c*c*(np.pi*a*a)**2/(.8*.4*.5)/(2*np.pi*.1)**2
     assert abs(inferred/m-1)<1e-6
     fine=solve((.8,.4,.5),(.2,.25),a,[.1,20,80],640,c,rho)
     assert np.all(rr-fine[0]>=-1e-12) and np.all(rr-fine[0]<=bb+1e-12)
     checks.append(dict(test='rotation_low_frequency_mass_tail',radius_m=a,rotation_error=float(max(abs(rr-rot[0]))),mass_relative_error=float(abs(inferred/m-1)),tail_witness_error=float(max(rr-fine[0]))))
    write_csv(OUT/'p21c1_membrana.csv',rows);write_csv(OUT/'p21c1_odrzucenia.csv',excluded);write_csv(OUT/'p21c1_przesuniecie.csv',pairs)
    summary=dict(date='2026-10-30',status='RIGID_DISK_PORT_NOT_FULL_DRIVER_OR_COMPLETE_P21C',products=len(products),geometry_count=27,accepted_sources=len(rows)//len(freq),rejected_sources=len(excluded),frequency_points=len(rows),paired_positions=len(pairs),max_tail_bound=max(r['tail_bound'] for r in rows),max_last_change=max(r['last_change'] for r in rows),max_shape_difference=max(rows,key=lambda r:abs(r['circle_minus_square'])),worst_R=min(rows,key=lambda r:r['R']),max_offset_mass=max(pairs,key=lambda r:r['delta_mass_kg']),checks=checks,libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__))
    inputs=[CFG,Path(__file__),BASE,EXT,ROOT/'skrypty/analiza_rozszerzenia_SB.py',ROOT/'skrypty/model_subwoofera.py',ROOT/'skrypty/pilot_P21C_geometria.py',ROOT/'brief_system_audio_DIY_v0.6.md']
    summary['input_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    (OUT/'p21c1_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
