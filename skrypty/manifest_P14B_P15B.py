"""Audyt artefaktów wykonanego etapu, nie zamknięcie programu30badań."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import sqlite3
import zipfile
from zoneinfo import ZoneInfo
import numpy as np
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import scipy,matplotlib,sympy
from projekcja_P14B import read_checkpoints
from rozstrzygnij_P14B import load_resolutions

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p14=json.loads((OUT/'p14b_podsumowanie.json').read_text());p15=json.loads((OUT/'p15b_podsumowanie.json').read_text())
    projection=json.loads((OUT/'p14b_projekcja.json').read_text());verification=json.loads((OUT/'p14b_weryfikacja_wybranych.json').read_text())
    heat_audit=json.loads((OUT/'p15b_audyt_sprzezenia.json').read_text());archive=json.loads((OUT/'p15b_checkpoint_archiwum.json').read_text())
    for hashes in (p14['input_sha256'],p15['input_sha256'],projection['input_sha256'],archive['input_sha256']):
        for name,value in hashes.items():assert digest(ROOT/name)==value,name
    raw,h=read_checkpoints();rows=load_resolutions(raw,h)
    assert h==p14['run_sha256']==projection['dynamic_run_sha256']==verification['dynamic_run_sha256']
    assert len(raw)==3312 and all(r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE' for r,a,d in rows)
    assert len(verification['comparisons'])==4 and len(verification['emission_convergence'])==4
    assert verification['script_sha256']==digest(ROOT/'skrypty/sprawdz_kampanie_P14B.py')
    assert len(heat_audit['full_audio'])==4
    assert all(x=='0' for x in heat_audit['identities']['identities'].values())
    assert p15['cases']==2304 and p15['status_counts']=={'COMPLETED_CONDITIONAL_TRAJECTORY':2304}
    dbs=sorted(OUT.glob('p14b_C*_*.sqlite3'));assert len(dbs)==24
    for p in dbs:
        con=sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True)
        try:assert con.execute('PRAGMA quick_check').fetchone()[0]=='ok',str(p)
        finally:con.close()
    zip_path=OUT/archive['archive_file'];assert digest(zip_path)==archive['archive_sha256']
    with zipfile.ZipFile(zip_path) as z:
        meta=json.loads(z.read('metadata.json'));assert meta['run_sha256']==p15['run_sha256']
        assert len(meta['file_sha256'])==2304
        for name,value in meta['file_sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==value
    inputs=set([ROOT/'brief_system_audio_DIY_v0.6.md',Path(__file__)])
    for hashes in (p14['input_sha256'],p15['input_sha256'],projection['input_sha256']):inputs.update(ROOT/name for name in hashes)
    inputs.update(ROOT/'skrypty'/name for name in ['podsumuj_studia_P14B.py','raportuj_pelne_P14B.py','sprawdz_kampanie_P14B.py',
        'audyt_dynamiki_P14B.py','audyt_sprzezenia_Re_T_P15B.py','raportuj_sprzezenie_Re_T_P15B.py','archiwum_P15B.py','odtworz_wszystko.py'])
    inputs.update(ROOT/'dane/zrodla'/name for name in ['P14B_IMD_AM_FM_i_emisja.json','P15A_topologie_i_cieplo.json','P15B_sprzezenie_i_konflikt_alpha.json'])
    outputs=set(dbs)
    for pattern in ['p14b_*','p15b_*','36_P15B*','37_P15B*','38_P15B*','39_P14B*','40_P14B*']:
        outputs.update(p for p in OUT.glob(pattern) if p.is_file())
    for folder in ['p14b_rozstrzygniecia','p14b_wybrane_radau']:
        outputs.update(p for p in (OUT/folder).rglob('*') if p.is_file())
    # Część wejść stanowią zapisane rozstrzygnięcia: ich hashe są także wprojection.
    docs=[ROOT/name for name in ['AGENTS.md','README.md','PROGRAM_30_BADAN.md','raporty/026_P14B_pelna_kampania_dwutonowa.md',
        'raporty/027_P15B_sprzezenie_grzania_i_napedu.md','baza_wiedzy/18_sprzezenie_termiczne_i_obwiednia.md','baza_wiedzy/ZRODLA.md']]
    result=dict(status='WYKONANY_ZAKRES_P14B_I_P15B_NIE_KONIEC_PROGRAMU_PROTOTYPU',generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,SymPy=sympy.__version__),
        P14B_run_sha256=h,P15B_run_sha256=p15['run_sha256'],
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(outputs)},
        documentation_sha256={str(p.relative_to(ROOT)):digest(p) for p in docs},
        coverage=dict(P14B_cases=3312,raw_NOT_SETTLED=23,periodic_after_separate_refinements=3312,
            independent_Radau_witnesses=4,P15B_conditional_trajectories=2304,full_audio_thermal_witnesses=4,checkpoint_records_in_zip=2304),
        limitations=['Hashe i cache potwierdzają pochodzenie/odtworzenie, nie niezależną fizyczną walidację.',
            'Krzywe nieliniowe i chłodzenie są scenariuszami,nie parametrami zidentyfikowanych24produktów.',
            'Wciąż otwarte:P17synteza,P18–P21mechanika/klej,P22–P25napęd/ochrona/sygnały,P26–P29integracja/wybór,P30końcowyPDF.'])
    (OUT/'manifest_P14B_P15B.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print('Manifest etapu:24bazy,3312widm,2304checkpointyZIP;',len(inputs),'wejść,',len(outputs),'wyników;4Radau i4pełneODEaudio.')
    return result


if __name__=='__main__':main()
