"""Ślad pochodzenia ilości i rozmieszczenia wypełnienia; bez doboru produktu."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    record=json.loads((ROOT/'wyniki/p09c_podsumowanie.json').read_text())
    for name,value in record['input_sha256'].items():assert sha(ROOT/name)==value,name
    assert record['cases']['drive_frequency_cases']==17820
    assert record['cases']['independent_ladder_solves']==80
    inputs={ROOT/name for name in record['input_sha256']}
    inputs.update(ROOT/name for name in ['skrypty/manifest_wypelnienia_P09C.py','skrypty/odtworz_wszystko.py'])
    outputs=sorted(p for pattern in ['p09c_*','62_P09C*','63_P09C*'] for p in (ROOT/'wyniki').glob(pattern) if p.is_file())
    docs=[ROOT/name for name in ['AGENTS.md','README.md','PLAN_B_R.md','PROGRAM_30_BADAN.md',
        'raporty/README.md','raporty/039_wypelnienie_ilosc_polozenie_i_straty.md',
        'baza_wiedzy/README.md','baza_wiedzy/27_ilosc_i_polozenie_wypelnienia.md']]
    result=dict(status=record['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=record['libraries'],coverage=record['cases'],limitations=record['limitations'],
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs})
    (ROOT/'wyniki/manifest_wypelnienia_P09C.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P09C:',len(inputs),'wejść,',len(outputs),'wyników;18geometrii,17820punktów,80FV.')


if __name__=='__main__':main()
