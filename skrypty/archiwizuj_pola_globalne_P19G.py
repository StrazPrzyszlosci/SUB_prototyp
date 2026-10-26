"""Dwa dodatkowe pola źródłowe do podmodelu; nie ponawia kampanii20wariantów."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
from model_listwy_naroznej_P19F import model
from analiza_listwy_stalego_frontu_P19F import solve_refined

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cfgpath=ROOT/'dane/konfiguracje/p19g_podmodel_lokalny.json';cfg=json.loads(cfgpath.read_text())
    previous={r['case_id']:r for r in csv.DictReader((OUT/'p19f_geometrie_i_podatnosc.csv').open())}
    refs=[]
    for entry in cfg['new_parent_fields']:
        n,s=entry['mesh_n'],entry['section_m'];cid=f'N{n}_B{int(s*1000)}_REF'
        E,t,nu=cfg['E_glue_pa'],cfg['glue_thickness_m'],cfg['nu_glue_assumed']
        b=model(n=n,section=s,cross_intervals=4,kn=E/t,ks=E/(2*(1+nu)*t));b.set_floor()
        gravity=-9.80665*(b.M@b.R[:,2]);q,res=solve_refined(b.K+b.floor_K,np.column_stack([gravity,1000*b.pressure,b.frozen_original_pressure]))
        C=float(b.frozen_original_pressure@q[:,2]);err=abs(C/float(previous[cid]['supported_C_frozen_original_H_m3_pa'])-1);assert err<1e-9
        path=OUT/f'p19g_parent_{cid}.npz'
        np.savez_compressed(path,xyz_m=b.xyz,q_combined_m_rad=q[:,0]+q[:,1],
            q_gravity_m_rad=q[:,0],q_pressure_1kPa_m_rad=q[:,1],rigid_modes=b.R,
            actual_pressure_port=b.pressure,panel_names=np.array([p.name for p in b.panels]),
            panel_offsets=np.array([p.offset for p in b.panels]),panel_node_counts=np.array([len(p.xyz) for p in b.panels]),
            basket_reference_m=b.basket_reference)
        refs.append(dict(case_id=cid,mesh_n=n,section_m=s,path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),C_match_relative_error=err,residuals=res))
        print('P19G parent:',cid,b.ndof,'DOF;',err,flush=True)
    inputs=[cfgpath,Path(__file__),ROOT/'skrypty/model_listwy_naroznej_P19F.py',ROOT/'skrypty/analiza_listwy_stalego_frontu_P19F.py',ROOT/'skrypty/model_ramy_3D_P18C.py',ROOT/'skrypty/element_brylowy_P18C.py',OUT/'p19f_geometrie_i_podatnosc.csv']
    data=dict(status='ADDITIONAL_BOUNDARY_FIELDS_SAME_GLOBAL_MODEL_NOT_INDEPENDENT_VALIDATION',parents=refs,
              input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (OUT/'p19g_pola_globalne.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
