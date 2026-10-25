"""Pochodzenie wykonanego P18B/P19B; bez kwalifikacji zmiennego styku w czasie."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
from zoneinfo import ZoneInfo
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    front=json.loads((OUT/'p18b_podsumowanie.json').read_text())
    contact=json.loads((OUT/'p19b_podsumowanie.json').read_text())
    check=json.loads((OUT/'p18b_weryfikacja.json').read_text())
    assert (front['cases'],front['modal_rows'],front['coupled_rows'])==(136,1088,90)
    assert (contact['static_cases'],contact['dynamic_cases'],contact['switching_flagged'])==(12,72,20)
    inputs=set()
    for record in [front,contact,check]:
        for path,h in record['input_sha256'].items():
            assert sha(ROOT/path)==h,path;inputs.add(ROOT/path)
    inputs.update(ROOT/'skrypty'/n for n in ['wykresy_frontu_i_styku_P18B_P19B.py','odtworz_front_i_styk_P18B_P19B.py','odtworz_wszystko.py',Path(__file__).name])
    outputs=set()
    for pat in ['p18b_*','p19b_*','49_P18B*','50_P18B*','51_P18B*','52_P19B*']:
        outputs.update(p for p in OUT.glob(pat) if p.is_file())
    outputs.update(p for p in (OUT/'archiwum/P19B_pierwsza_iteracja_bolty_dwustronne').iterdir() if p.is_file())
    docs=[ROOT/n for n in ['AGENTS.md','README.md','PROGRAM_30_BADAN.md','baza_wiedzy/README.md','baza_wiedzy/ZRODLA.md',
                          'baza_wiedzy/23_front_otwor_kosz_i_docisk.md','raporty/032_postep_po_mechanice_i_zakres_do_konca.md',
                          'raporty/033_front_otwor_kosz_i_styk_jednostronny.md']]
    result=dict(status='SCOPED_P18B_P19B_NOT_FULL_CABINET_OR_CONTACT_TIME_SOLUTION',
                generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
                libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__),
                input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
                output_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(outputs)},
                documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
                next='P19C:czasowa odpowiedź zmiennego styku w konkretnym przypadku80Hz,zbieżność redukcji i energia.',
                limits=['MasyCG/mocowania i uszczelka są częściowo hipotetyczne;nie ranking3produktów.',
                        '20flag zmiany styku nie jest obliczonym przebiegiem po otwarciu.',
                        'Brak pełnej skrzyni,otworówśrubowych3D,ścinania,pełzania i zewnętrznej radiacji.',
                        'Surowe oryginały nowych źródeł pozostają prywatne;publikujemy własne wyniki,fakty i hashe.'])
    (OUT/'manifest_frontu_P18B_P19B.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print('Manifest frontu:',len(inputs),'wejść,',len(outputs),'wyników,',len(docs),'dokumentów;136/90/12/72.')


if __name__=='__main__':main()
