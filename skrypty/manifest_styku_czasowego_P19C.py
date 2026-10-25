"""Pochodzenie P19C i jawna dziedzina;nie certyfikat produktu lub pelnej skrzyni."""
import ast
from datetime import datetime
import hashlib,json,os
from pathlib import Path
import platform
from zoneinfo import ZoneInfo
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,sympy,matplotlib

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    study=json.loads((OUT/'p19c_podsumowanie.json').read_text());checks=json.loads((OUT/'p19c_kontrole.json').read_text());audit=json.loads((OUT/'p19c_audyt_fizyki.json').read_text())
    inputs=set()
    for record in [study,checks,audit]:
        for name,h in record['input_sha256'].items():assert sha(ROOT/name)==h,name;inputs.add(ROOT/name)
    assert study['full_dof']==2959 and len(study['results'])==6 and len(study['full_time_comparison'])==3
    assert all(r['status']=='PERIODIC_WITHIN_STATED_CRITERION' for r in study['results'])
    assert audit['damping_control']['status']=='PERIODIC_WITHIN_STATED_CRITERION'
    assert audit['symbolic']['total_energy']=='0' and audit['symbolic']['gas_energy']=='0'
    pilot=OUT/'archiwum/P19C_pilot_M08';meta=json.loads((pilot/'snapshot_sha256.json').read_text())
    assert sha(pilot/'snapshot_sha256.json')==study['historical_pilot_snapshot_sha256']
    for name,h in meta.items():assert sha(pilot/name)==h,name
    # Archiwalny pilot ma te same rownania;roznice pozniejszego simulate
    # dotycza przygotowanego stanu i licznika czasu,nie sil lub energii.
    def methods(path):
        tree=ast.parse(path.read_text());result={}
        for cls in [n for n in tree.body if isinstance(n,ast.ClassDef)]:
            for fn in cls.body:
                if isinstance(fn,ast.FunctionDef) and fn.name!='simulate':result[(cls.name,fn.name)]=ast.dump(fn,include_attributes=False)
        return result
    assert methods(pilot/'model_styku_czasowego_P19C.py')==methods(ROOT/'skrypty/model_styku_czasowego_P19C.py')
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_styk_czasowy_P19C.py','wykresy_styku_czasowego_P19C.py','odtworz_wszystko.py',Path(__file__).name])
    outputs={p for pat in ['p19c_*','53_P19C*','54_P19C*'] for p in OUT.glob(pat) if p.is_file()}
    outputs.update(p for p in pilot.iterdir() if p.is_file())
    docs=[ROOT/n for n in ['AGENTS.md','README.md','PROGRAM_30_BADAN.md','raporty/README.md','baza_wiedzy/README.md',
                          'baza_wiedzy/24_styk_czasowy_i_energia.md','raporty/034_czasowy_styk_i_pelny_MES.md']]
    result=dict(status='P19C_ONE_SCOPED_CONTACT_CASE_EXECUTED_NOT_FINAL_CABINET',
                generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
                libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,SymPy=sympy.__version__,Matplotlib=matplotlib.__version__),
                input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
                output_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(outputs)},documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
                coverage=dict(historical_cold_pilot=1,new_reduced_runs=5,damping_control=1,full_FE_three_period_runs=3,full_dof=2959),
                limitations=['Jeden przypadek z20flag,nie cala pula kontaktow lub identyfikacja uszczelki.',
                             'PelnyMES z przygotowanej historii,3okresy;nie niezaleznyzimnystart lub dowodpelnejokresowosci.',
                             'Mocowanie/CG/tlumienie sa hipotezami;dzwiek,THD i przeciek niezwalidowane.',
                             'Objetosc szczeliny ma luzne ograniczenie2.5% ruchustozkaRMS;nieudowodniono bledu cisnienia<1%.'],
                next='Pelna rama i polaczenia obudowy,nastepnie regulacjaVb i poleprzestrzenne.')
    (OUT/'manifest_styku_czasowego_P19C.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('ManifestP19C:',len(inputs),'wejsc,',len(outputs),'artefaktow;2959DOF,pilotjawny,7odpowiedziROM i3pelneMES.')


if __name__=='__main__':main()
