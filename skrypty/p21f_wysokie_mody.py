"""P21F refinement check: 288 independent frequency/geometry/scenario witnesses.
Run: OPENBLAS_NUM_THREADS=1 python skrypty/p21f_wysokie_mody.py
Requires skrypty/p21f_mody_gaz_panele.py and its configuration.
"""
import json
from pathlib import Path
from p21f_mody_gaz_panele import CFG,POOL,OUT,evaluate
import numpy as np

def main():
    c=json.loads(CFG.read_text())
    pool={x['model']['name']:x['model'] for x in json.loads(POOL.read_text())['drivers']}
    rows=[]
    for name in c['candidate_model_names']:
      for vb in c['volume_l']:
        for x in c['driver_centres_xz_m']:
          for kind in c['panel_scenarios']:
            for f in (20.,40.,60.,80.):
                values=[evaluate(f,c,pool[name],vb,x,kind,cut)['velocity_m_s_per_V']
                        for cut in (5,6,7,8)]
                db=[float(20*np.log10(values[j+1]/values[j])) for j in range(3)]
                rows.append(dict(candidate=name,volume_l=vb,x_m=x,scenario=kind,
                    frequency_hz=f,db_5_to_6=db[0],db_6_to_7=db[1],db_7_to_8=db[2]))
    assert len(rows)==288
    r={'cases':len(rows),'truncations':[5,6,7,8],
       'frequency_hz':[20,40,60,80],
       'max_abs_db':{k:max(abs(z[k]) for z in rows)
            for k in ('db_5_to_6','db_6_to_7','db_7_to_8')},
       'note':'Selected 288 witnesses; no guarantee of monotonic convergence or continuous-band error'}
    OUT.mkdir(exist_ok=True)
    (OUT/'p21f_wysokie_mody.json').write_text(json.dumps({'summary':r,'rows':rows},indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
