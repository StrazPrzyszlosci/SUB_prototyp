"""972warunkowe świadki,dokładny audyt,36ODE i jawne ograniczenia fizyczne."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,hashlib,json,platform
import numpy,scipy,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p24a_podsumowanie.json','p24a_weryfikacja_dokladna_LDL.json','p24a_naped_i_ODE_podsumowanie.json','p24a_tozsamosci_symboliczne.json','p24a_ocena_projektowa.json']
    study,exact,drive,symbols,post=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for record in [study,exact,drive,symbols,post]:
        for n,h in record['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
    assert study['cases']==study['expected_cases']==study['accepted']==exact['accepted']==972
    assert exact['endpoint_LMI_checks']==1944 and exact['search_trials']==6804 and exact['rejected_search_trials']==3
    assert drive['performance_rows']==11664 and drive['thermal_comparison_rows']==23328 and drive['continuous_ODE_cases']==36
    assert drive['retained_wave_cases']==6 and len(symbols['identities'])==5
    for n,count in [('p24a_obszary_i_poziomy.csv',972),('p24a_naped_i_cena_zapasu.csv',11664),('p24a_gorna_obwiednia_temperatury.csv',23328),('p24a_ciagle_trajektorie_z_temperatura.csv',36)]:
        with (OUT/n).open() as f:assert len(list(csv.DictReader(f)))==count,n
    casefiles=sorted((ROOT/study['checkpoint_folder']).glob('*.json'));assert len(casefiles)==972
    for p in casefiles:
        r=json.loads(p.read_text());assert r['run_sha256']==study['run_sha256'] and r['input_sha256']==study['input_sha256'] and r['certificate']
    with numpy.load(OUT/'p24a_przebiegi_reference.npz',allow_pickle=False) as waves:
        assert len(waves.files)==6
        for n in waves.files:assert waves[n].shape==(38401,7) and numpy.all(numpy.isfinite(waves[n]))
    inputs.update(ROOT/'skrypty'/n for n in ['tabela_z_certyfikatow_P24A.py','manifest_obszarow_P24A.py','odtworz_obszary_P24A.py','odtworz_wszystko.py'])
    inputs.add(ROOT/'dane/zrodla/P24A_narzedzia_SDP.json')
    inputs.add(ROOT/'requirements.txt')
    outputs=sorted(set([p for pat in ['p24a_*','92_P24A*','93_P24A*','94_P24A*'] for p in OUT.glob(pat) if p.is_file()]+casefiles))
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md','raporty/README.md',
        'raporty/049_obszar_niezmienniczy_i_koszt_ochrony.md','baza_wiedzy/README.md','baza_wiedzy/37_wspolny_obszar_i_granica_wejscia.md','baza_wiedzy/ZRODLA.md']]
    initial_environment=json.loads((OUT/'p24a_srodowisko_poczatkowe.json').read_text())
    record=dict(status=post['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),run_sha256=study['run_sha256'],
        libraries_current_verification=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,SymPy=sympy.__version__),
        original_search_environment=initial_environment,
        reproduction='Default replays stored exact witnesses,independent rational checks and fresh36ODE;optional --search needs requirements_p24.txt. Reading matching checkpoints is not a new independent SDP solution.',
        coverage=dict(electrical_configurations=27,model_families=972,search_trials=6804,rejected_search_trials=3,
            exact_positive_X_checks=972,exact_endpoint_LMI_checks=1944,continuous_coupled_ODE=36,
            sine_comparisons=11664,thermal_comparison_rows=23328,symbolic_identities=5),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},limitations=study['limitations']+exact['limitations']+drive['limitations']+post['limitations'],next=post['next'])
    (OUT/'manifest_obszarow_P24A.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P24A:',len(inputs),'inputs,',len(outputs),'outputs;972conditional models,not device certification.')


if __name__=='__main__':main()
