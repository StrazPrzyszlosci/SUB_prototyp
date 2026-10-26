"""Wskaźnik pominiętej reakcji zwrotnej stopy dla zachowanego lokalnego pola.

Przelicza średnią na łacie: lokalne u wewnątrz wycinka, globalne poza nim.
Nie rozwiązuje ponownie układu i nie koryguje źródłowego wyniku podmodelu.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from model_podmodelu_P19G import ParentField

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cfgpath=ROOT/'dane/konfiguracje/p19g_podmodel_lokalny.json';cfg=json.loads(cfgpath.read_text())
    path=OUT/'p19g_pole_lokalne_B30_middle.npz';parentpath=ROOT/cfg['parent_reference_npz']
    parent=ParentField(parentpath,14,.03)
    with np.load(path,allow_pickle=False) as f:d={k:f[k] for k in f.files}
    idx=list(d['panel_names']).index('bottom');offset=int(d['panel_offsets'][idx]);count=int(d['panel_node_counts'][idx])
    xyz=d['xyz_m'][offset:offset+count];u=d['q_m'].reshape(-1,3)[offset:offset+count]
    shift=d['parent_rigid_shift'];absolute=u+shift[:3]+np.cross(np.broadcast_to(shift[3:],xyz.shape),xyz)
    x,y,z=(np.unique(xyz[:,i]) for i in range(3));local=RegularGridInterpolator((z,y,x),absolute.reshape(len(z),len(y),len(x),3))
    px=np.unique(parent.panels['bottom']['xyz'][:,0]);py=np.unique(parent.panels['bottom']['xyz'][:,1])
    k=np.array(cfg['floor_k_xyz_n_m']);size=cfg['floor_patch_size_m'];items=[];gauss,weight=np.polynomial.legendre.leggauss(2)
    for foot in parent.foot_tractions(k,size):
        lo=np.maximum(foot['lo'],[x[0],y[0]]);hi=np.minimum(foot['hi'],[x[-1],y[-1]])
        if np.any(hi<=lo):continue
        sx=np.r_[lo[0],np.unique(np.r_[x,px])[(np.unique(np.r_[x,px])>lo[0])&(np.unique(np.r_[x,px])<hi[0])],hi[0]]
        sy=np.r_[lo[1],np.unique(np.r_[y,py])[(np.unique(np.r_[y,py])>lo[1])&(np.unique(np.r_[y,py])<hi[1])],hi[1]]
        integral=np.zeros(3)
        for x0,x1 in zip(sx[:-1],sx[1:]):
            for y0,y1 in zip(sy[:-1],sy[1:]):
                pts=np.array([[(x0+x1)/2+a*(x1-x0)/2,(y0+y1)/2+b*(y1-y0)/2,0.] for a in gauss for b in gauss])
                weights=np.array([a*b for a in weight for b in weight])*(x1-x0)*(y1-y0)/4
                delta=local(pts[:,[2,1,0]])-parent.evaluate('bottom',pts,raw=True)
                integral+=weights@delta
        delta_force=-k*integral/size**2
        items.append(dict(parent_foot_force_n=foot['force'].tolist(),increment_from_local_patch_n=delta_force.tolist(),
                          increment_norm_relative_to_parent_force=float(np.linalg.norm(delta_force)/np.linalg.norm(foot['force'])),
                          modified_area_fraction=float(np.prod(hi-lo)/size**2)))
    inputs=[cfgpath,path,parentpath,Path(__file__),ROOT/'skrypty/model_podmodelu_P19G.py']
    result=dict(status='ONE_SAVED_FIELD_FROZEN_FOOT_FEEDBACK_INDICATOR_NOT_GLOBAL_COUPLED_SOLUTION',
                case_id='B30_middle_H0.0025_P14_X8',feet=items,
                scope='Outside local domain displacement retained from parent. Diagnostic only for this field; no claim for all24cases or nonlinear contact.',
                input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (OUT/'p19g_zamrozona_stopa_audyt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},ensure_ascii=False))


if __name__=='__main__':main()
