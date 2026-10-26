"""Pochodzenie odrębnego liniowego rozszerzenia SB, nie zamknięcie P29."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    study = json.loads((ROOT/'wyniki/sb_rozszerzenie_weryfikacja.json').read_text())
    for name, value in study['input_sha256'].items():
        assert sha(ROOT/name)==value, name
    assert study['point_cases']==5832 and study['physical_products']==26
    assert study['electrical_configurations']==27
    inputs = {ROOT/name for name in study['input_sha256']}
    inputs.update(ROOT/name for name in ['dane/zrodla/SB_rozszerzenie_pochodzenie.json',
                                       'skrypty/manifest_rozszerzenia_SB.py', 'skrypty/odtworz_wszystko.py'])
    outputs = sorted([*ROOT.glob('wyniki/sb_rozszerzenie_*.csv'),
                      *ROOT.glob('wyniki/61_SB_*'), ROOT/'wyniki/sb_rozszerzenie_weryfikacja.json'])
    docs = [ROOT/name for name in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md',
                                   'raporty/README.md','raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md',
                                   'baza_wiedzy/README.md','baza_wiedzy/ZRODLA.md',
                                   'baza_wiedzy/26_dwie_cewki_i_porownywanie_SB.md']]
    result = dict(status=study['status'], generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
                  libraries=study['libraries'], coverage=dict(products=26, configurations=27, points=5832),
                  input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
                  output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
                  documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
                  limitations=study['scope'])
    (ROOT/'wyniki/manifest_rozszerzenia_SB.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest SB:', len(inputs), 'wejść,', len(outputs), 'wyników; zakres liniowy, bez końcowego wyboru.')


if __name__=='__main__':
    main()
