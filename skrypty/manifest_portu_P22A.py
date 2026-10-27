"""Ślad modelu źródła i rozdzielonych portów,bez identyfikacji wzmacniacza."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,hashlib,json,platform
import numpy,scipy,sympy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    study=json.loads((OUT/'p22a_podsumowanie.json').read_text());checks=json.loads((OUT/'p22a_kontrole_niezalezne.json').read_text());inputs=set()
    for record in [study,checks]:
        for n,h in record['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
    assert study['configurations']==27 and study['networks']==3240 and study['drive_rows']==19440 and study['Q_projections']==648
    assert checks['independent_KCL_KVL_points']==19440 and checks['independent_state_space_points']==162
    assert checks['monotonic_envelope_groups']==648 and len(checks['symbolic_identities'])==3
    for n,count in [('p22a_naped_z_portem.csv',19440),('p22a_zmiana_transferu.csv',3240),('p22a_Q_z_rezystancja.csv',648)]:
        with (OUT/n).open() as f:assert len(list(csv.DictReader(f)))==count,n
    inputs.update(ROOT/'skrypty'/n for n in ['manifest_portu_P22A.py','odtworz_port_P22A.py','raport_i_wykresy_portu_P22A.py','odtworz_wszystko.py'])
    outputs=sorted(p for pat in ['p22a_*','87_P22A*','88_P22A*'] for p in OUT.glob(pat) if p.is_file())
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md','raporty/README.md',
        'raporty/047_port_zrodla_tlumienie_i_bilans.md','baza_wiedzy/README.md','baza_wiedzy/35_port_zrodla_i_wykonalnosc_ochrony.md']]
    record=dict(status=study['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,SymPy=sympy.__version__),
        coverage=dict(configurations=27,source_families=3240,sine_drive_cases=19440,Q_projections=648,
            direct_KCL_KVL_checks=19440,state_space_checks=162,pure_R_monotonic_groups=648,symbolic_identities=3),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=study['limitations']+checks['limitations'],next=study['next'])
    (OUT/'manifest_portu_P22A.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P22A:',len(inputs),'inputs,',len(outputs),'outputs;clipping/physical electronics not identified.')


if __name__=='__main__':main()
