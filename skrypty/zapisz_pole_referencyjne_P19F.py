"""Zachowuje pole N14/B30 dla przyszłego podmodelu, nie nowy ranking."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
from analiza_listwy_stalego_frontu_P19F import solve_refined,joint_fields
from model_listwy_naroznej_P19F import model

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p19f_listwa_stalego_frontu.json').read_text())
    E=cfg['glue_reference_effective_E_pa'];t=cfg['glue_thickness_m'];nu=cfg['glue_nu_assumed']
    b=model(n=14,section=.03,cross_intervals=4,kn=E/t,ks=E/(2*(1+nu)*t))
    b.set_floor();g=-9.80665*(b.M@b.R[:,2])
    q,res=solve_refined(b.K+b.floor_K,np.column_stack([g,1000*b.pressure,b.frozen_original_pressure]))
    archived=next(r for r in csv.DictReader((OUT/'p19f_geometrie_i_podatnosc.csv').open()) if r['case_id']=='N14_B30_REF')
    C=float(b.frozen_original_pressure@q[:,2]);err=abs(C/float(archived['supported_C_frozen_original_H_m3_pa'])-1)
    assert err<1e-9
    path=OUT/'p19f_pole_referencyjne_N14_B30.npz'
    np.savez_compressed(path,xyz_m=b.xyz,q_gravity_m_rad=q[:,0],q_pressure_1kPa_m_rad=q[:,1],
        q_combined_m_rad=q[:,0]+q[:,1],rigid_modes=b.R,actual_pressure_port=b.pressure,
        panel_names=np.array([p.name for p in b.panels]),panel_offsets=np.array([p.offset for p in b.panels]),
        panel_node_counts=np.array([len(p.xyz) for p in b.panels]),basket_reference_m=b.basket_reference)
    sources=[Path(__file__),ROOT/'skrypty/model_listwy_naroznej_P19F.py',
             ROOT/'skrypty/analiza_listwy_stalego_frontu_P19F.py',ROOT/'skrypty/model_ramy_3D_P18C.py',
             ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'dane/konfiguracje/p19f_listwa_stalego_frontu.json',
             OUT/'p19f_geometrie_i_podatnosc.csv']
    meta=dict(status='REFERENCE_FIELD_FOR_LATER_SUBMODELING_NOT_INDEPENDENT_VALIDATION',
        case_id='N14_B30_REF',dof=b.ndof,linear_residuals=res,C_match_relative_error=err,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        output_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()},
        array_units='xyz m; translations m, last 3 generalized basket rotations rad; pressure port N/Pa',
        scope='Full original supported displacement field retained; do not reinterpret as measured deformation. Geometry C04 reference, not selected driver.')
    (OUT/'p19f_pole_referencyjne.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    print('Reference P19F:',b.ndof,'DOF; C replay difference',err,flush=True)


if __name__=='__main__':main()
