"""Resolve flagged 80Hz port convergence; retain original coarse results."""
import json
import numpy as np
import pole_zintegrowanej_geometrii_P21D as model

def main():
 rows=[]
 for name,n,k in [('150',2,0),('120',11,1),('100',16,3)]:
  for proxy in ['A','B']:
   for step in [.025,.018]:
    model.CID='C02';model.set_obstacles(n,k,proxy);g=model.build(0,step,True)
    z,res=model.solve(g,80.)
    ref=model.MED.gamma*model.MED.p0_pa/(2*np.pi*80*sum(g['vol']))
    rows.append(dict(configuration=name,proxy=proxy,step_m=step,f_hz=80,dof=g['n'],Z_real=z.real,Z_imag=z.imag,residual=res,compliance_reference_magnitude=ref))
    print(name,proxy,step,g['n'],z,flush=True)
    (model.O/'p21d_dogeszczenie.json').write_text(json.dumps(dict(scope='C02 80Hz; extra grids for near-zero port, no continuum certificate',rows=rows),indent=2))
if __name__=='__main__':main()
