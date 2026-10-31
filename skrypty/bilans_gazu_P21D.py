"""Independent power balance evaluation of the FV fields, Q=1 unit port."""
import json
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve
import pole_zintegrowanej_geometrii_P21D as m

def main():
 rows=[]
 for config,n,k in [('150',2,0),('100',16,3)]:
  m.CID='C02';m.set_obstacles(n,k,'A');g=m.build(0,.035,True);f=80.;omega=2*np.pi*f
  density=np.full(g['n'],m.MED.rho,complex);bulk=np.full(g['n'],m.MED.gamma*m.MED.p0_pa,complex)
  rp,kp=m.CircularPores(.0002,m.PHI,'rigid',20).equivalent_properties([f],m.MED)
  density[g['flags']]=rp[0];bulk[g['flags']]=kp[0]
  a,b=g['A'],g['B'];conduct=g['area']/(density[a]*g['da']+density[b]*g['db']);comp=g['vol']/bulk
  matrix=coo_matrix((np.r_[conduct,conduct,-conduct,-conduct],(np.r_[a,b,a,b],np.r_[a,b,b,a])),shape=(g['n'],g['n'])).tocsc()-diags(omega**2*comp)
  p=spsolve(matrix,1j*omega*g['source'])
  port=(g['source']@p).real
  viscous=np.sum(conduct.imag/omega*abs(p[a]-p[b])**2)
  thermal=np.sum(-omega*comp.imag*abs(p)**2)
  residual=abs(port-viscous-thermal)/max(abs(port),1e-12)
  assert residual<1e-8 and viscous>=0 and thermal>=0
  rows.append(dict(configuration=config,f_hz=f,Q_normalization_m3_s=1,power_port=port,power_viscous=viscous,power_thermal=thermal,relative_residual=residual))
 (m.O/'p21d_bilans_gazu.json').write_text(json.dumps(dict(scope='Algebraic FV power balance, not independent validation of physical material; RMS complex convention',rows=rows),indent=2))
 print(rows)
if __name__=='__main__':main()
