import json
from wklady_przestrzenne_P21C3 import build,solve,O,W,H,D
from komora_warstwowa_P21C2 import port
from model_wypelnienia import CircularPores
from analiza_rozszerzenia_SB import candidates
rows=[];d={i:d for i,p,d,c in candidates()}['C02']
for count,fill in [(0,True),(10,True),(16,True),(16,False)]:
 g=build(count,.016,fill);z,res=solve(g,80.)
 row=dict(count=count,fill=fill,step=.016,f=80.,dof=g['n'],gas_l=sum(g['vol'])*1000,Z_real=z.real,Z_imag=z.imag,residual=res)
 if count==0:
  ref=port(W,H,[(D-.05,None),(.05,CircularPores(.0002,.98,'rigid',20))],(W/4,H/2),d.sd,[80.],240)[0];row['empty_modal_relative_error']=float(abs(z/ref-1))
 rows.append(row);(O/'p21c3_dogeszczenie.json').write_text(json.dumps(rows,indent=2));print(row,flush=True)