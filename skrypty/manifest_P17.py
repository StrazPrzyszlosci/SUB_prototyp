"""Pochodzenie i kontrole wykonanego warunkowego zakresu P17."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
from zoneinfo import ZoneInfo
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    study=json.loads((OUT/'p17_podsumowanie.json').read_text());check=json.loads((OUT/'p17_weryfikacja.json').read_text())
    for name,value in study['input_sha256'].items():assert sha(ROOT/name)==value,name
    assert study['point_cases']==31104 and study['band_cases']==5184
    assert check['point_cases']==31104 and check['direct_complex_boundary_checks']==26246
    assert all(v=='0' for v in check['symbolic_identities'].values())
    inputs={ROOT/name for name in study['input_sha256']}
    inputs.update(ROOT/'skrypty'/name for name in ['sprawdz_synteze_P17.py','raportuj_synteze_P17.py','odtworz_wszystko.py',Path(__file__).name])
    outputs=[*sorted(p for p in OUT.glob('p17_*') if p.is_file()),*sorted(OUT.glob('41_P17*')),*sorted(OUT.glob('42_P17*'))]
    docs=[ROOT/name for name in ['AGENTS.md','README.md','PROGRAM_30_BADAN.md','baza_wiedzy/README.md','baza_wiedzy/19_staly_poziom_i_wspolne_ograniczenia.md','raporty/028_P17_synteza_napedu_objetosci_i_ciepla.md']]
    result=dict(status='P17_WYKONANY_ZAKRES_WARUNKOWY_NIE_FINALNY_WYBOR',generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        run_sha256=study['run_sha256'],libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,SymPy=sympy.__version__),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        coverage=dict(points=31104,six_frequency_cases=5184,direct_boundary_checks=26246,analytic_identities=3),
        scope=study['limitations'])
    (OUT/'manifest_P17.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print('ManifestP17:',len(inputs),'wejść,',len(outputs),'wyników,',len(docs),'dokumentów.');return result


if __name__=='__main__':main()
