"""Ślad wejść, wyników i granic porównania przegrody z modułami."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib,json,os,platform
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    records=[json.loads((OUT/n).read_text()) for n in ['p20b_podsumowanie.json','p20b_naped_podsumowanie.json',
        'p20b_kontrole_niezalezne.json','p20b_materialy_podsumowanie.json','p20b_ocena_projektowa.json']]
    inputs=set()
    for r in records:
        for name,expected in r['input_sha256'].items():
            p=ROOT/name;assert sha(p)==expected,name;inputs.add(p)
    study,drive,checks,material,post=records
    assert study['cases']==dict(structural_models=56,geometry_rows=80,mechanical_port_rows=336,network_rows=13836,amplitude_rows=27216)
    assert drive['point_cases']==72432 and drive['electrical_configurations']==27
    assert len(checks['full_nodal_coupled'])==64 and len(checks['mechanical_direct'])==16
    assert len(checks['static_hermetic_gas'])==72 and len(checks['geometry'])==72 and len(checks['selected_mesh'])==12
    assert len(checks['navier'])==3 and material['cases']==9 and post['dense_frequency_rows']==6005
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_przegrode_P20B.py','manifest_przegrody_P20B.py','odtworz_wszystko.py'])
    outputs=sorted(p for pat in ['p20b_*','74_P20B*','75_P20B*','76_P20B*','77_P20B*'] for p in OUT.glob(pat) if p.is_file())
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md','raporty/README.md',
        'raporty/043_przegroda_dwie_komory_i_materialy.md','baza_wiedzy/README.md','baza_wiedzy/ZRODLA.md',
        'baza_wiedzy/31_przegroda_dwa_cisnienia_i_anizotropia.md']]
    result=dict(status=study['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,SymPy=sympy.__version__),
        coverage=dict(structural_models=56,geometry_rows=80,network_rows=13836,drive_points=72432,electrical_configurations=27,
            full_nodal_coupled=64,static_gas=72,primary_material_rows=9),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=study['limitations']+drive['limitations']+checks['limitations']+material['limitations']+post['limitations'],next=post['next'])
    (OUT/'manifest_przegrody_P20B.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P20B:',len(inputs),'inputs,',len(outputs),'outputs; 56structural/72432drive; physical qualification open.')


if __name__=='__main__':main()
