"""Niezależne całki powierzchni,momentów i zbieżność normalnego submodelu."""
import json
from pathlib import Path
import numpy as np
from model_plyty_MITC_P18 import PlateMaterial,RectangularPlate
from model_normalnego_polaczenia_P19 import normal_joint,solve_joint

ROOT=Path(__file__).resolve().parents[1]


def main():
    panel=RectangularPlate(.46,.64,12,16,PlateMaterial(2.1e9,.3,730,.022),'SSSS');rigid=[]
    for defect in ['NONE','EDGE_5MM','CENTER_30PCT']:
        sys=normal_joint(panel,.08,.018,2.2e9,1.718e9,.0002,.15,2.1e9,.00088,.46,8,.005,defect)
        pad=sys['pad'];T=np.zeros((sys['K0'].shape[0],3));nmain=sys['nmain']
        x=pad.xy[:,0]-.04;y=pad.xy[:,1]-.04
        T[nmain+np.arange(0,len(pad.full_F),3),0]=1
        T[nmain+np.arange(0,len(pad.full_F),3),1]=x
        T[nmain+np.arange(1,len(pad.full_F),3),1]=1
        T[nmain+np.arange(0,len(pad.full_F),3),2]=y
        T[nmain+np.arange(2,len(pad.full_F),3),2]=1
        matrix=T.T@(sys['K0']@T)
        pos=sys['positions'];weights=sys['weights'];basis=np.c_[np.ones(len(weights)),pos]
        independent=sys['kn_n_m3']*((basis.T*weights)@basis)
        error=np.linalg.norm(matrix-independent)/np.linalg.norm(independent);assert error<1e-11
        force=-sys['b'];q=T@np.linalg.solve(matrix,T.T@force)
        stresses=sys['traction_probe']@q
        if defect=='NONE':
            expected=1/(.08*.08)*(1+6*.005/.08)
            assert abs(max(abs(stresses))/expected-1)<1e-10
        area_expected=.08**2 if defect=='NONE' else ((.08-.005)*.08 if defect=='EDGE_5MM' else .7*.08**2)
        assert abs(sys['bond_area_m2']/area_expected-1)<1e-12
        rigid.append(dict(defect=defect,rigid_reduced_matrix_relative_error=float(error),area_m2=sys['bond_area_m2'],max_rigid_traction_per_n_pa=float(max(abs(stresses)))))
    convergence=[]
    for main_nx,main_ny,pad_n in [(8,12,4),(16,24,8),(24,36,12),(32,48,16)]:
        p=RectangularPlate(.46,.64,main_nx,main_ny,PlateMaterial(2.1e9,.3,730,.022),'SSSS')
        sys=normal_joint(p,.08,.018,2.2e9,1.718e9,.0002,.15,2.1e9,.00088,.46,pad_n,.005,'NONE')
        q,result=solve_joint(sys)
        assert result['force_balance_relative_error']<1e-8 and result['moment_balance_relative_error']<1e-8
        convergence.append(dict(main_nx=main_nx,main_ny=main_ny,pad_n=pad_n,**result))
    change=abs(convergence[-1]['maximum_normal_traction_per_pa']/convergence[-2]['maximum_normal_traction_per_pa']-1)
    assert change<.05
    result=dict(status='NORMAL_JOINT_ANALYTIC_AND_MESH_CONTROLS',rigid_limit_controls=rigid,mesh_convergence=convergence,
        last_normal_peak_relative_change=float(change),
        scope='Dokładna granica sztywnej nakładki oraz dyskretyzacja submodeluWinklera. Nie model pękania interfejsu3D,fatigue/creep ani dowódadhesji do MDFkonkretnejpartii.')
    (ROOT/'wyniki/p19a_niezalezne_kontrole.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
