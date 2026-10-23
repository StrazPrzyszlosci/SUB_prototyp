"""Pełny przebieg naukowy z zachowaniem poprzedniego stanu roboczego."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'wyniki'
    previous=[p for p in out.iterdir() if p.is_file()] if out.exists() else []
    if previous:
        stamp=datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y%m%dT%H%M%S_%f')
        archive=out/'archiwum'/stamp
        archive.mkdir(parents=True)
        old=json.loads((out/'manifest.json').read_text()) if (out/'manifest.json').exists() else {}
        mismatches=[]
        for p in previous:
            shutil.copy2(p,archive/p.name)
            expected=old.get('output_sha256',{}).get(str(p.relative_to(ROOT)))
            if expected and hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
                mismatches.append(p.name)
        inputs=archive/'stan_wejsc'
        inputs.mkdir()
        for name in ('skrypty','dane'):
            shutil.copytree(ROOT/name,inputs/name,ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('brief_system_audio_DIY_v0.6.md','DECYZJE_I_PYTANIA.md','PLAN_BADAN_NAUKOWYCH.md'):
            shutil.copy2(ROOT/name,inputs/name)
        (archive/'status_archiwum.json').write_text(json.dumps({
            'status':'migawka_poprzedniego_stanu_roboczego',
            'note':'Przy pierwszej archiwizacji mogą występować zmiany wykonane od ostatniego manifestu; nie jest to rzekomo odtworzony dawny przebieg.',
            'outputs_changed_since_manifest':mismatches},ensure_ascii=False,indent=2))
        print('Zachowano poprzedni stan roboczy:',archive.relative_to(ROOT))
    from sprawdz_model import main as checks
    from audyt_wykresow import main as images
    from analiza_fizyki import main as physics
    from analiza_celow_dsp import main as dsp
    from uruchom_badania import main as baseline
    checks()
    images()
    physics()
    dsp()
    baseline()  # Manifest powstaje po wszystkich obliczeniach.


if __name__=='__main__':
    main()
