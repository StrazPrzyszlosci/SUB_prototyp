"""Wymaganie zachowania podatności dla dodatniego długoczasowego modułu.

To granica E_infinity w tym samym modelu,nie wyznaczony J(t),czas pełzania
czy trwałość produktu. Nie utożsamiać z zerwaniem lub pustą szczeliną.
"""
import csv
import json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.optimize import brentq
from model_plyty_MITC_P18 import PlateMaterial,RectangularPlate
from model_normalnego_polaczenia_P19 import normal_joint

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    rows=[];targets=[]
    for boundary in ['SSSS','CCCC']:
        for gap in [.0002,.0005]:
            panel=RectangularPlate(.46,.64,16,24,PlateMaterial(2.1e9,.3,730,.022),boundary)
            system=normal_joint(panel,.08,.018,2.2e9,1.718e9,gap,.15,2.1e9,.00088,.46,8)
            traction=system['traction_quad'];W=sparse.diags(system['weights']);kn=system['kn_n_m3']
            per_kn=(traction.T@(W@traction))/(kn*kn)
            base=system['K']-kn*per_kn;normal_mdf=system['c_mdf_m_pa'];F=system['force']
            def at(E):
                g=1/(gap/E+normal_mdf);q=spsolve(base+g*per_kn,F)
                C=float(F@q);peak=float(max(abs(system['traction_probe']@q)))*g/kn
                return C,peak
            reference=at(1.718e9)[0]
            for E in np.geomspace(1e4,1.718e9,17):
                C,peak=at(E)
                rows.append(dict(boundary=boundary,gap_m=gap,assumed_relaxed_E_pa=float(E),compliance_to_reference=C/reference,
                    normal_peak_at1kpa_pa=1000*peak,linear_glue_strain_demand_at1kpa=1000*peak/E,
                    scope='E_INFINITY_STRESS_NOT_TIME_HISTORY_OR_MANUFACTURER_CREEP'))
            target=brentq(lambda log:at(np.exp(log))[0]/reference-1.1,np.log(1e4),np.log(1.718e9),xtol=1e-10)
            modulus=float(np.exp(target));C,peak=at(modulus)
            targets.append(dict(boundary=boundary,gap_m=gap,declared_compliance_increase_reference=0.1,
                required_relaxed_E_pa=modulus,compliance_ratio=C/reference,linear_strain_demand_at1kpa=1000*peak/modulus,
                scope='10%TO_KRYTERIUM_KONTROLNE_NIE_ZATWIERDZONE_WYMAGANIE_BRIEFU'))
    with (OUT/'p19a_relaksacja_wymagania.csv').open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result=dict(status='RELAXED_MODULUS_REQUIREMENTS_NOT_CREEP_LIFETIME_PREDICTION',targets=targets,
        scope='Wszystkie pozostałe elementy liniowo sprężyste. MDFteż może pełzać,a model nie identyfikuje tego procesu. Zbytduży nominalnystrain sygnalizuje wyjściepoza model liniowej spoiny.')
    (OUT/'p19a_relaksacja_progi.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
