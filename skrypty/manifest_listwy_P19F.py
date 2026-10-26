"""Pochodzenie wyników listwy i otwarta zbieżność lokalnego pola spoin."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib,json,platform,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p19f_podsumowanie.json','p19f_kontrola_niezalezna.json','p19f_ocena_zbieznosci.json','p19f_pole_referencyjne.json']
    records=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for r in records:
        for name,h in r['input_sha256'].items():assert sha(ROOT/name)==h,name;inputs.add(ROOT/name)
        for name,h in r.get('output_sha256',{}).items():assert sha(ROOT/name)==h,name
    study,control,post,field=records
    assert study['cases']==20 and study['load_cases']==40 and post['joint_rows']==548
    assert field['dof']==17592 and field['C_match_relative_error']<1e-9
    assert all(abs(r['relative_change_N14_N18'])>.15 for r in post['local_stress_mesh_comparisons'])
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_listwe_P19F.py','manifest_listwy_P19F.py','odtworz_wszystko.py'])
    outputs=sorted(p for pat in ['p19f_*','64_P19F*','65_P19F*','66_P19F*'] for p in OUT.glob(pat) if p.is_file())
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md',
        'raporty/README.md','raporty/040_listwa_stalego_frontu_i_droga_sily.md',
        'baza_wiedzy/README.md','baza_wiedzy/28_listwa_i_lokalna_droga_sily.md']]
    result=dict(status=study['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__),
        coverage=dict(cases=20,loads=40,joint_rows=548,max_global_dof=27036,reference_field_dof=17592),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=study['limitations'],
        next='Zgodny lokalny podmodel front–dno–listwa30mm z polemN14/B30,porownaniem20mm i odleglosci granicy; nie zamykac nosnosci z globalnegoC.')
    (OUT/'manifest_listwy_P19F.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P19F:',len(inputs),'wejść,',len(outputs),'wyników; lokalne naprężenia jawnie niezbieżne.')


if __name__=='__main__':main()
