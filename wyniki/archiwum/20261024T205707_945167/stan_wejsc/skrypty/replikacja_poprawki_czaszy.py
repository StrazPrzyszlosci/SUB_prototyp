"""P11: odtworzenie opublikowanego wyniku Bellows2024, Eq4/5 i Fig3.

Porównanie wyniku teoretycznego, nie pomiar loudspeaker. Promień rzutu
czaszy b*sin(theta) różni się od promienia koła o tej samej powierzchni.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from model_gazu import Medium
from model_promieniowania import spherical_cap_added_mass_static
from analiza_promieniowania import table

ROOT=Path(__file__).resolve().parents[1]


def main():
    medium=Medium();b=1.
    def normalized(theta,terms=8192):
        area=2*np.pi*b*b*(1-np.cos(theta))
        ma=spherical_cap_added_mass_static(area,b,terms,medium)
        end=ma/(medium.rho*area)
        return end/(b*np.sin(theta))
    opt=minimize_scalar(normalized,bounds=(np.deg2rad(3),np.pi/2),method='bounded',options={'xatol':1e-10})
    minimum=float(opt.fun);angle=float(np.rad2deg(opt.x))
    assert abs(minimum-.6167)<5e-5 and abs(angle-50.5)<.2
    rows=[]
    for degrees in [3.,10.,20.,30.,50.5,60.,75.,90.]:
        theta=np.deg2rad(degrees)
        rows.append(dict(half_angle_degrees=degrees,end_correction_over_projected_cap_radius=normalized(theta),
                         source='BELLOWS2024_EQ4_5_FIG3',scope='REPLIKACJA_MODELU_TEORETYCZNEGO_NIE_POMIAR'))
    table('p11_replikacja_Bellows2024.csv',rows)
    result=dict(status='PASS_ZGODNOSC_Z_OPUBLIKOWANA_DOKLADNOSCIA',doi='10.1121/10.0026023',
                source_url='https://sambellows.github.io/assets/pdf/2024_spherical_cap.pdf',
                computed_minimum=minimum,published_rounded_minimum=.6167,
                computed_half_angle_degrees=angle,published_rounded_half_angle_degrees=50.5,
                difference_to_published_minimum=minimum-.6167,
                scope='Minimum dla0<theta<=90deg i promienia rzutu czaszy. Nie utożsamiać go z promieniem koła równej powierzchni.',
                caveat='Odtworzenie teorii i opublikowanego minimum nie waliduje geometrii prostokątnej skrzyni.')
    (ROOT/'wyniki/p11_replikacja_Bellows2024.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
