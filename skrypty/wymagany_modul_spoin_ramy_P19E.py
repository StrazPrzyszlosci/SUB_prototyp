"""U-021:sztywnosc stalego frontu;monotoniczne progiE,nie nosnosc kleju."""
import csv,functools,hashlib,json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.optimize import brentq
from model_ramy_3D_P18C import Cabinet3D

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    rows=[]
    for n in [10,14]:
        b=Cabinet3D(n=n)
        reference_K=b.K.copy();Cref=float(b.pressure@b.balanced_static(b.pressure)[0])
        for scope in ['FRONT_ONLY','ALL_JOINTS']:
            variable=sum((p.matrix(b.ndof) for p in b.bonds if scope=='ALL_JOINTS' or p.name.startswith('front_')),
                         sparse.csr_matrix(b.K.shape))
            fixed=reference_K-variable
            @functools.lru_cache(maxsize=128)
            def response(beta):
                b.K=fixed+beta*variable
                q,F,acc=b.balanced_static(b.pressure)
                compliance=float(b.pressure@q);derivative=float(-q@(variable@q))
                return compliance,derivative
            for allowance in [.05,.10,.20]:
                def mismatch(log_beta):return response(float(np.exp(log_beta)))[0]/Cref-(1+allowance)
                lo=np.log(1e-5)
                assert mismatch(lo)>0 and mismatch(0)<=0
                log_root=brentq(mismatch,lo,0,xtol=1e-9)
                beta=float(np.exp(log_root));C,dC=response(beta)
                step=beta*1e-3;finite=(response(beta+step)[0]-response(beta-step)[0])/(2*step)
                derr=abs(finite/dC-1);assert derr<1e-3 and dC<0
                row=dict(mesh_n=n,scope=scope,relative_C_allowance=allowance,beta=beta,
                         effective_E_at_200um_pa=1718e6*beta,effective_E_at_50um_pa=1718e6*beta*.25,
                         effective_E_at_500um_pa=1718e6*beta*2.5,interface_kn_required_pa_m=b.bond_kn*beta,
                         reference_compliance_m3_pa=Cref,achieved_compliance_m3_pa=C,
                         analytic_dC_dbeta=dC,finite_difference_relative_error=float(derr))
                rows.append(row);print('P19E modulus',row,flush=True)
    with (OUT/'p19e_wymagane_moduly_stalego_frontu.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
    result=dict(status='STIFFNESS_REQUIREMENTS_FOR_FIXED_FRONT_NOT_STRENGTH_OR_FATIGUE',cases=len(rows),
                decision='U-021,frontstaly,niedemontowalny,podjedenwybranydocelowoprzetwornik',
                model_reference='C04niejestostatecznymwyboremglośnika',
                monotonicity='dC/dbeta=-qT*Kvariable*q<=0 przy stalymH i stalejmasie;beta>0.',
                assumptions=['5/10/20%to scenariusze przyrostuC,nie zatwierdzone progi briefu.',
                             'Eeff odwzorowuje jednoczesniekn/ks przy stalejnu_glue=.35;nie opisuje dowolnego konkretnego kleju.',
                             'Zmiana grubosci przeliczona dla tej samej lokalizacji interfejsu i liniowego prawa.',
                             'PrógE nie okresla adhezji,Gc,SN,J(t),szczelnosci lub trwalosci.',
                             'PorownanieN10/N14 jest skonczona kontrola siatki,nie dowod globalnego ekstremum.'],
                input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                              ['skrypty/wymagany_modul_spoin_ramy_P19E.py','skrypty/model_ramy_3D_P18C.py','skrypty/element_brylowy_P18C.py']})
    (OUT/'p19e_wymagane_moduly_podsumowanie.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))


if __name__=='__main__':main()
