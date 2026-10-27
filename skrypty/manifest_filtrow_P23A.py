"""Ślad P23A:nowe filtry nie stają się pomiarem lub ustawieniami hardware."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,hashlib,json,platform
import numpy,scipy,sympy,mpmath

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p23a_podsumowanie.json','p23a_kontrole_niezalezne.json','p23a_kolejnosc_podsumowanie.json']
    study,checks,order=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for record in [study,checks,order]:
        for n,h in record['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
    assert study['electrical_configurations']==27 and study['analog_designs']==972
    assert study['quantized_chains']==4860 and study['sections']==19440 and study['stress_filters']==300
    assert study['time_cases']==study['fs_mismatch_cases']==9 and not study['non_strict_chains']
    assert len(checks['symbolic_identities'])==9 and len(checks['high_precision_frequency'])==len(checks['high_precision_group_delay'])==45
    assert len(checks['selected_large_quantization_errors'])==3 and len(checks['DF1_time_comparisons'])==3
    assert len(checks['independent_coefficients'])==12 and order['orders']==12 and order['prefixes']==48
    expected={'p23a_kaskady_i_kwantyzacja.csv':4860,'p23a_wspolczynniki_i_Jury.csv':19440,
        'p23a_blad_transformacji_vs_analog.csv':972,'p23a_granice_rozdzielczosci.csv':300,
        'p23a_czas_i_arytmetyka.csv':9,'p23a_niezgodnosc_Fs.csv':9,
        'p23a_kolejnosc_i_poziomy_posrednie.csv':48}
    for n,count in expected.items():
        with (OUT/n).open() as f:rows=list(csv.DictReader(f))
        assert len(rows)==count,n
    sources=ROOT/'dane/zrodla/P23A_filtry_i_formaty.json';registry=json.loads(sources.read_text());assert len(registry['sources'])==4
    inputs.update([sources,ROOT/'skrypty/manifest_filtrow_P23A.py',ROOT/'skrypty/odtworz_filtry_P23A.py',
        ROOT/'skrypty/raport_i_wykresy_filtrow_P23A.py',ROOT/'skrypty/odtworz_wszystko.py'])
    outputs=sorted(p for pattern in ['p23a_*','84_P23A*','85_P23A*','86_P23A*'] for p in OUT.glob(pattern) if p.is_file())
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md','raporty/README.md',
        'raporty/046_filtry_cyfrowe_stabilnosc_i_zapas.md','baza_wiedzy/README.md',
        'baza_wiedzy/34_cyfrowe_filtry_stabilnosc_i_normy.md','baza_wiedzy/ZRODLA.md']]
    record=dict(status=study['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,SymPy=sympy.__version__,mpmath=mpmath.__version__),
        coverage=dict(configurations=27,designs=972,chains=4860,sections=19440,stress_filters=300,
            time_cases=9,fs_mismatch_cases=9,section_orders=12,intermediate_outputs=48,
            high_precision_frequency_checks=45,selected_high_precision_extreme_witnesses=3,
            high_precision_delay_checks=45,symbolic_identities=9,DF1_checks=3),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=study['limitations']+checks['limitations']+order['limitations'],next=study['next'])
    (OUT/'manifest_filtrow_P23A.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P23A:',len(inputs),'inputs,',len(outputs),'outputs;hardware/protection still open.')


if __name__=='__main__':main()
