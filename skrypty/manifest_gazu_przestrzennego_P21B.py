"""Ślad ukończonej rodziny gazu3D P21B,nie walidacja całego subwoofera."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib,json,os,platform
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p21b_podsumowanie.json','p21b_kontrole_niezalezne.json','p21b_granica_obciazenia_podsumowanie.json','p21b_asymptotyka_podsumowanie.json','p21b_ocena_projektowa.json']
    records=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for r in records:
        for n,h in r['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
    study,checks,bound,asymptote,post=records
    assert study['status']=='COMPLETE_CONFIGURED_SPATIAL_FAMILIES' and study['cases']==study['expected_cases']==18
    assert study['field_rows']==264 and study['frequency_cases']==132
    assert study['flagged_frequency_cases']==post['numerical_flagged_rows']==0
    assert len(checks['scalar_kronecker'])==3 and len(checks['rigid_eigenmodes'])==3 and len(checks['prescribed_piston'])==12
    assert len(checks['mean_split_comparisons'])==4 and len(checks['full_coupled_checks'])==4 and len(checks['formal0D_limit'])==12
    assert bound['cases']==108 and post['comparison_rows']==132
    assert asymptote['rows']==36
    folder=ROOT/study['checkpoint_folder'];casefiles=sorted(folder.glob('*.json'));assert len(casefiles)==18
    for p in casefiles:
        r=json.loads(p.read_text());assert r['run_sha256']==study['run_sha256'] and r['input_sha256']==study['input_sha256']
        if 'state_sha256' in r:assert sha(ROOT/study['reference_state_file'])==r['state_sha256']
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_gaz_przestrzenny_P21B.py','raportuj_gaz_przestrzenny_P21B.py','manifest_gazu_przestrzennego_P21B.py','odtworz_wszystko.py'])
    inputs.add(ROOT/'dane/zrodla/P21B_sprzezenie_i_postac_slaba.json')
    outputs=sorted(set([p for pat in ['p21b_*','81_P21B*','82_P21B*','83_P21B*'] for p in OUT.glob(pat) if p.is_file()]+casefiles))
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md','raporty/README.md',
        'raporty/045_gaz_przestrzenny_praca_i_granica0D.md','baza_wiedzy/README.md',
        'baza_wiedzy/33_przestrzenne_cisnienie_i_praca_granicy.md','baza_wiedzy/ZRODLA.md']]
    j=dict(status=study['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),run_sha256=study['run_sha256'],
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,SymPy=sympy.__version__),
        coverage=dict(primary_cases=18,frequency_systems=132,field_rows=264,rigid_reference_meshes=3,piston_cases=12,formal_limit_cases=12,scalar_load_bounds=108),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=study['limitations']+checks['limitations']+bound['limitations']+asymptote['limitations']+post['limitations'],next=post['next'])
    (OUT/'manifest_gazu_przestrzennego_P21B.json').write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P21B:',len(inputs),'inputs,',len(outputs),'outputs;18families/132systems;main cavity and physical losses open.')


if __name__=='__main__':main()
