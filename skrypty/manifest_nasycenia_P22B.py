"""Spójne648trajektorii,zachowane przekroczenia i odrębne kontroleciągłe."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,hashlib,json,platform
import numpy,scipy,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    records=[json.loads((OUT/n).read_text()) for n in ['p22b_podsumowanie.json','p22b_kontrole_niezalezne.json','p22b_ocena_projektowa.json']]
    study,checks,post=records;inputs=set()
    for record in records:
        for n,h in record['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
    assert study['cases']==648 and study['configurations']==27 and study['time_steps_per_case']==28800
    assert study['outside_catalog_x_reference']==208 and study['over_current_threshold_cases']==82
    assert checks['selected_continuous_cases']==7 and checks['time_step_comparisons']==28 and not checks['time_step_flags']
    assert checks['controller_root_checks']==100 and checks['kinematic_boundary_cases']==27 and checks['locally_infeasible_kinematic_cases']==11
    assert post['remaining_numerical_flags']==0 and len(study['retained_cases'])==3
    for n,count in [('p22b_trajektorie.csv',648),('p22b_zbieznosc_i_ciagle_ODE.csv',28),('p22b_wykonalnosc_stanu_granicznego.csv',27)]:
        with (OUT/n).open() as f:assert len(list(csv.DictReader(f)))==count,n
    with numpy.load(OUT/'p22b_przebiegi_reference.npz',allow_pickle=False) as states:
        assert set(states.files)==set(study['retained_cases'])
        for name in states.files:assert states[name].shape==(28800,8) and numpy.all(numpy.isfinite(states[name]))
    inputs.update(ROOT/'skrypty'/n for n in ['manifest_nasycenia_P22B.py','odtworz_nasycenie_P22B.py','odtworz_wszystko.py'])
    outputs=sorted(p for pat in ['p22b_*','89_P22B*','90_P22B*','91_P22B*'] for p in OUT.glob(pat) if p.is_file())
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md','raporty/README.md',
        'raporty/048_nasycenie_SEM_i_stan_pradu.md','baza_wiedzy/README.md','baza_wiedzy/36_nasycenie_energia_i_granice_integratora.md']]
    record=dict(status=post['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,SymPy=sympy.__version__),
        coverage=dict(cases=648,electrical_configurations=27,continuous_independent_ODE=7,time_step_comparisons=28,
            root_controls=100,kinematic_boundary_witnesses=27,locally_infeasible_boundary_witnesses=11,
            outside_catalog_X_reference=208,over_assumed_current_threshold=82),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},limitations=study['limitations']+checks['limitations']+post['limitations'],next=post['next'])
    (OUT/'manifest_nasycenia_P22B.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P22B:',len(inputs),'inputs,',len(outputs),'outputs;not current/X/T protection.')


if __name__=='__main__':main()
