"""Audyt danych i pochodzenia mechaniki; otwarte bramki pozostają jawne."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
from zoneinfo import ZoneInfo
import zipfile
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,sympy,matplotlib

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p18=json.loads((OUT/'p18a_podsumowanie.json').read_text());p19=json.loads((OUT/'p19a_podsumowanie.json').read_text());p21=json.loads((OUT/'p21a_sprzezenie_podsumowanie.json').read_text())
    assert p18['cases']==172 and p18['dynamic_rows']==1996
    assert p19['cases']==656 and p19['dynamic_rows']==57 and p21['rows']==72
    for meta in [p18,p19]:
        for name,h in meta['input_sha256'].items():assert sha(ROOT/name)==h,name
    for stage in ['p18a','p19a']:
        m=json.loads((OUT/(stage+'_archiwum.json')).read_text());path=OUT/m['archive_file'];assert sha(path)==m['archive_sha256']
        with zipfile.ZipFile(path) as z:
            meta=json.loads(z.read('metadata.json'));assert sum(name.endswith('.json') for name in meta['file_sha256'])==m['cases']
            for name,h in meta['file_sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
    inputs={ROOT/name for meta in [p18,p19] for name in meta['input_sha256']}
    scripts=['sprawdz_MITC_P18.py','niezalezny_Ritz_P18.py','emisja_i_sprzezenie_plyty_P18.py','reakcja_powietrza_P21A.py',
        'sprawdz_reakcje_powietrza_P21A.py','sprawdz_polaczenie_normalne_P19.py','analiza_scinania_i_szczelnosci_P19.py',
        'model_szczeliny_P19.py','wymagania_zlaczy_i_pretow_P19.py','wymagany_modul_relaksacji_P19.py',
        'wykresy_mechaniki_P18_P19_P21.py','archiwum_mechaniki_P18_P19.py','odtworz_mechanike_P18_P19_P21.py','odtworz_wszystko.py','uruchom_badania.py',Path(__file__).name]
    inputs.update(ROOT/'skrypty'/name for name in scripts);inputs.add(ROOT/'dane/zrodla/P18_P19_materialy_i_metoda.json')
    outputs=set()
    for pattern in ['p18_*','p18a_*','p19a_*','p21a_*','43_P18A*','44_P18A*','45_P18A*','46_P19A*','47_P19A*','48_P19A*']:
        outputs.update(p for p in OUT.glob(pattern) if p.is_file())
    docs=[ROOT/name for name in ['AGENTS.md','README.md','PROGRAM_30_BADAN.md','baza_wiedzy/README.md','baza_wiedzy/ZRODLA.md',
        'baza_wiedzy/20_MES_paneli_i_sciagow.md','baza_wiedzy/21_mechanika_spoin_i_kwalifikacja.md','baza_wiedzy/22_reakcja_powietrza_na_panele.md',
        'raporty/029_P18A_plyty_sciagi_i_dynamika.md','raporty/030_P19A_obliczenia_spoin_i_material_kleju.md','raporty/031_P21A_reakcja_powietrza_i_bilans.md']]
    result=dict(status='WYKONANE_ZAKRESY_P18A_P19A_P21A_NIE_PELNA_KONSTRUKCJA',generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,SymPy=sympy.__version__,Matplotlib=matplotlib.__version__),
        runs=dict(P18A=p18['run_sha256'],P19A=p19['run_sha256']),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},output_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(outputs)},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        coverage=dict(plate_cases=172,normal_joint_cases=656,coupled_reference_points=72),
        open_gates=['Front z otworem,koszem,mocowaniem i rzeczywiste naroża nie są wykonane.',
            'Jedna sztuczna amplituda z P18A przekracza umowny wskaźnik liniowego ugięcia;nie kwalifikuje się jej jako nieliniowej odpowiedzi urządzenia.',
            'Nie wyznaczono realnego S-N/J(t),adhezji konkretnegoMDF i trwałości kleju.',
            'P21Ato odgroda i jednorodna komora0D,nie pełne pole3D i pokój.',
            'Zgodny cache i hashe nie są nową niezależną replikacją ani walidacją fizyczną.'])
    (OUT/'manifest_mechaniki_P18_P19_P21.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print('Manifest mechaniki:',len(inputs),'wejść,',len(outputs),'wyników,',len(docs),'dokumentów;172/656/72.');return result


if __name__=='__main__':main()
