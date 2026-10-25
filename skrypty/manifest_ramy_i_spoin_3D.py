"""Pochodzenie referencji ramy i niezbieżnego screeningu defektu;nie certyfikat."""
from datetime import datetime
import hashlib,json,os
from pathlib import Path
import platform
from zoneinfo import ZoneInfo
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p18c_podsumowanie.json','p18c_kontrole.json','p18c_adaptacja_i_granice.json','p18c_zbieznosc_grubosci.json',
           'p19d_podsumowanie.json','p19d_weryfikacja.json','p19e_wymagane_moduly_podsumowanie.json']
    records=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for record in records:
        for name,h in record['input_sha256'].items():assert sha(ROOT/name)==h,name;inputs.add(ROOT/name)
    study,checks,adaptive,thickness,debond,checkdebond,modulus=records
    assert study['case_count']==12 and study['harmonic_rows']==168 and debond['cases']==6
    assert max(x['dof'] for x in adaptive['adaptive'])==36771 and not adaptive['unexecuted']
    assert adaptive['zero_bond_independent_rigid_modes']==36
    assert len(checkdebond['mesh_comparisons'])==2
    assert all(r['relative_change']>.2 for r in checkdebond['mesh_comparisons'])
    assert modulus['cases']==12
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_rame_i_spoiny_3D.py','wykresy_ramy_3D_P18C.py','odtworz_wszystko.py',Path(__file__).name])
    inputs.add(ROOT/'dane/zrodla/P18C_teoria_3D_i_metoda.json')
    outputs={p for pattern in ['p18c_*','p19d_*','p19e_*','55_P18C*','56_P18C*','57_P18C*','58_P19D*','59_P19D*','60_P19E*'] for p in OUT.glob(pattern) if p.is_file()}
    docs=[ROOT/n for n in ['AGENTS.md','README.md','PROGRAM_30_BADAN.md','raporty/README.md','baza_wiedzy/README.md','baza_wiedzy/ZRODLA.md',
                          'baza_wiedzy/25_pelna_rama_i_spoiny_3D.md','raporty/035_pelna_rama_3D_spoiny_i_podparcie.md','raporty/036_spoiny_3D_i_wirtualne_odspojenie.md',
                          'raporty/037_staly_front_wymagany_modul_spoin.md','DECYZJE_I_PYTANIA.md','WYMAGANIA.md','PLAN_B_R.md']]
    result=dict(status='EXECUTED_REFERENCE_FRAME_AND_NONCONVERGED_FINITE_DEFECT_SCREENING',
                generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
                libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,
                               longdouble_mantissa_bits=int(numpy.finfo(numpy.longdouble).nmant)),
                input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
                output_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(outputs)},
                documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
                coverage=dict(main_blocks=12,one_reference_repeated=True,harmonic_samples=168,max_dof=36771,virtual_defect_cases=6,fixed_front_modulus_requirements=12),
                open_gates=['U-021:front staly podjedenmodel;geometria i materialstalepolaczenie wymagaja dalszego doboru.',
                            'Gdelta ma27/41% roznicymiedzyN10/N14;nieprognozaGc,trwalosci lub inicjacji.',
                            'Ostatnie zmiany siatki i warstw<1% nie sa globalnymcertyfikatembledu.',
                            'Sztywny glosnik6DOF z zablokowanymruchemstozka;niepelnaelektroakustyka.',
                            'MDF/spoiny/podparcieczesciowohipotetyczne;bezfinalnegoVnet i promieniowania.'],
                next='Lokalna geometria i przenoszeniesil wstalymfront–korpus,U-021;nastepnieP20/P21.')
    (OUT/'manifest_ramy_i_spoin_3D.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest3D:',len(inputs),'wejsc,',len(outputs),'wynikow;',36771,'DOF;screeningGjawnie niezbieżny.')


if __name__=='__main__':main()
