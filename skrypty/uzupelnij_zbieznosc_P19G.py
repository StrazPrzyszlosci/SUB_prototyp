"""Dwa niezależne kierunki dalszego zagęszczenia po 22 wykonanych przypadkach."""
from pathlib import Path
import csv,hashlib,json
from model_podmodelu_P19G import ParentField
from analiza_podmodelu_P19G import solve_case,table,source_fields

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cfgpath=ROOT/'dane/konfiguracje/p19g_podmodel_lokalny.json';cfg=json.loads(cfgpath.read_text())
    paths=source_fields(cfg);parent=ParentField(paths[(14,.03)],14,.03)
    cases=[dict(case_id='B30_middle_H0.0025_P14_X32',section_m=.03,domain='middle',yz_step_m=.0025,parent_n=14,nx=32),
           dict(case_id='B30_middle_H0.00125_P14_X8',section_m=.03,domain='middle',yz_step_m=.00125,parent_n=14,nx=8)]
    results=[]
    for c in cases:
        r=solve_case(cfg,parent,c)
        results.append(r);print('P19G refinement:',c['case_id'],r['case']['dof'],'DOF',flush=True)
    table('p19g_dodatkowe_przypadki.csv',[r['case'] for r in results])
    table('p19g_dodatkowe_okna.csv',[o for r in results for o in r['observations']])
    inputs=[cfgpath,Path(__file__),ROOT/'skrypty/model_podmodelu_P19G.py',ROOT/'skrypty/analiza_podmodelu_P19G.py',
            ROOT/'skrypty/analiza_listwy_stalego_frontu_P19F.py',ROOT/'skrypty/model_ramy_3D_P18C.py',ROOT/'skrypty/element_brylowy_P18C.py',paths[(14,.03)]]
    meta=dict(status='TWO_DIRECTIONAL_MESH_CONTROLS_NOT_CERTIFIED_CONTINUUM_ERROR',cases=len(results),
              input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (OUT/'p19g_dodatkowa_zbieznosc.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
