"""Masa i nominalna sztywność PASA zginanego; nie identyfikacja płyty 2D.

B=Em*t^3/12 to proxy belki o jednostkowej szerokości. Nie przyjmujemy
Em za pełny tensor 3D ani Gr planar shear za Gxy. Kierunki i wilgotność
producenta pozostają oddzielne. Nominalne grubości, bez bonusu za laminat.
"""
from pathlib import Path
import hashlib,json
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    path=ROOT/'dane/materialy/sklejka_pierwotne_P20B.json';data=json.loads(path.read_text())
    basepath=ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json';base=json.loads(basepath.read_text())
    a=.458;ref_t=.018;E=base['mdf_E_pa_assumed'];rho=base['mdf_density_kg_m3_assumed']
    refB=E*ref_t**3/12;refmass=rho*ref_t*a*a;rows=[]
    for r in data['records']:
        t=r['nominal_thickness_m'];mass=r['approx_areal_mass_kg_m2']*a*a
        ba=r['Em_a_bending_pa']*t**3/12;bb=r['Em_b_bending_pa']*t**3/12
        rows.append(dict(product=r['product'],t_mm=t*1000,panel_side_m=a,panel_mass_kg_approx=mass,
            mass_ratio_to_MDF18_assumption=mass/refmass,strip_Ba_n_m=ba,strip_Bb_n_m=bb,
            Ba_ratio_to_MDF18_assumption=ba/refB,Bb_ratio_to_MDF18_assumption=bb/refB,
            mass_specific_strip_ratio_a=(ba/mass)/(refB/refmass),mass_specific_strip_ratio_b=(bb/mass)/(refB/refmass),
            manufacturer_moisture_content_percent=r['moisture_content_percent'],source_id=r['source_id'],pdf_page=r['pdf_page'],
            scope='Nominal directional strip proxy; no 2D plate,damping,adhesion or equal-moisture qualification.'))
    table('p20b_materialy_masa_i_pas.csv',rows)
    inputs=[path,basepath,Path(__file__)]
    summary=dict(status=data['status'],cases=len(rows),reference_MDF18_assumed=dict(t_m=ref_t,E_pa=E,rho_kg_m3=rho,panel_mass_kg=refmass,strip_B_n_m=refB),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Two axes do not identify twisting,cross-coupling,transverse shear or damping of a plate.',
            'Published moisture12%/10% differs between product families; MDF assumption has no measured matching condition.',
            'No transfer of coated Form/FormPLUS facts to bare Birch; no conclusion of final superiority from strip stiffness alone.'])
    (OUT/'p20b_materialy_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20B materials:',len(rows),'primary directional strip/mass comparisons; full material law open.')


if __name__=='__main__':main()
