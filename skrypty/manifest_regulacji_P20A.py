"""Ślad pochodzenia P20A i granice modeli wkładów, szczelin i mocowań."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib,json,os,platform
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p20a_podsumowanie.json','p20a_naped_podsumowanie.json','p20a_kontrole_niezalezne.json','p20a_kanaliki_podsumowanie.json','p20a_ocena_projektowa.json']
    records=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for r in records:
        for n,h in r['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
    study,drive,checks,neck,post=records
    assert study['cases']['layouts']==108 and study['cases']['module_models']==78 and study['cases']['port_rows']==5616
    assert drive['point_cases']==40068 and drive['electrical_configurations']==27
    assert len(checks['navier'])==9 and len(checks['full_nodal_gas_comparisons'])==36 and len(checks['module_mesh'])==12
    assert len(checks['pressure_mode_checks'])==4 and checks['verified_continuous_segments']==1344
    assert neck['cases']==9 and neck['frequency_rows']==7209 and neck['amplitude_screens']==36
    assert post['spatially_unqualified_formal_mode_count']==27
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_regulacje_P20A.py','manifest_regulacji_P20A.py','odtworz_wszystko.py'])
    outputs=sorted(p for pat in ['p20a_*','70_P20A*','71_P20A*','72_P20A*','73_P20A*'] for p in OUT.glob(pat) if p.is_file())
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md',
        'raporty/README.md','raporty/042_regulacja_Vb_i_wklady_wypornosciowe.md',
        'baza_wiedzy/README.md','baza_wiedzy/30_wklady_objetosc_gaz_i_mocowanie.md']]
    result=dict(status=study['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,SymPy=sympy.__version__),
        coverage=dict(layouts=108,module_models=78,drive_points=40068,port_rows=5616,thermal_states=702,neck_frequency_rows=7209),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=study['limitations']+drive['limitations']+neck['limitations'],next=post['next'])
    (OUT/'manifest_regulacji_P20A.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P20A:',len(inputs),'wejść,',len(outputs),'wyników;108układów,78modułów,40068punktów; kwalifikacja materiału/3D otwarta.')


if __name__=='__main__':main()
