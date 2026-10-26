"""Ślad P20C: dane brył, spoin, gazu, rozstrzygnięć siatki i napędu."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib,json,os,platform
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p20c_podsumowanie.json','p20c_kontrole_niezalezne.json','p20c_klej_podsumowanie.json','p20c_siatka_podsumowanie.json',
        'p20c_dalsza_siatka_podsumowanie.json','p20c_naped_podsumowanie.json','p20c_ocena_projektowa.json']
    records=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for r in records:
        for n,h in r['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
    study,checks,glue,mesh,refine,drive,post=records
    assert study['status']=='COMPLETE_SCOPED_3D_MODULE_FAMILIES' and study['cases']==study['expected_cases']==18
    assert study['mechanical_rows']==162 and study['gas_rows']==1944 and study['joint_rows']==252
    assert len(checks['geometry'])==6 and len(checks['hydrostatic'])==2 and len(checks['full_nodal_gas'])==24
    assert glue['root_cases']==6 and len(glue['derivative_checks'])==6 and mesh['cases']==24
    assert mesh['outside_assumed_5pct_port_screen']==8 and refine['previous_flagged_rows']==refine['rows']==8 and refine['remaining_flags']==0
    assert refine['probe_rows']==24 and drive['cases']==11664 and drive['electrical_configurations']==27 and post['unresolved_resonance_mesh_flags']==0
    folder=ROOT/study['checkpoint_folder'];casefiles=sorted(folder.glob('*.json'));assert len(casefiles)==18
    for p in casefiles:
        r=json.loads(p.read_text());assert r['run_sha256']==study['run_sha256'] and r['input_sha256']==study['input_sha256']
        if 'state_sha256' in r:assert sha(OUT/'p20c_pole_reference.npz')==r['state_sha256']
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_modul_3D_P20C.py','manifest_modulu_3D_P20C.py','odtworz_wszystko.py'])
    outputs=sorted(set([p for pat in ['p20c_*','78_P20C*','79_P20C*','80_P20C*'] for p in OUT.glob(pat) if p.is_file()]+casefiles))
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md','raporty/README.md',
        'raporty/044_modul_3D_dwa_porty_i_wymagania_kleju.md','baza_wiedzy/README.md','baza_wiedzy/32_dwa_porty_bryly_i_gaz_przestrzenny.md']]
    j=dict(status=study['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),run_sha256=study['run_sha256'],
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,SymPy=sympy.__version__),
        coverage=dict(primary_models=18,mechanical_rows=162,gas_rows=1944,joint_rows=252,independent_full_gas_cases=24,
            hydrostatic_cases=2,initial_mesh_flags=8,further_N16_rows=8,resolved_mesh_flags=8,drive_points=11664,electrical_configurations=27),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=study['limitations']+checks['limitations']+glue['limitations']+mesh['limitations']+refine['limitations']+drive['limitations']+post['limitations'],
        next=post['next'])
    (OUT/'manifest_modulu_3D_P20C.json').write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P20C:',len(inputs),'inputs,',len(outputs),'outputs;18models/11664drive;8flags separately resolved; physical qualification open.')


if __name__=='__main__':main()
