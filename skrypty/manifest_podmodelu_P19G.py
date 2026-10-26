"""Pochodzenie lokalnych pól i jawna zależność od źródłowego modelu globalnego."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib,json,os,platform
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import numpy,scipy,matplotlib

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=['p19g_podsumowanie.json','p19g_pola_globalne.json','p19g_dodatkowa_zbieznosc.json',
           'p19g_transfer_i_obciazenia_kontrola.json','p19g_zamrozona_stopa_audyt.json','p19g_ocena_i_roznice.json']
    records=[json.loads((OUT/n).read_text()) for n in names];inputs=set()
    for r in records:
        for n,h in r['input_sha256'].items():assert sha(ROOT/n)==h,n;inputs.add(ROOT/n)
        for ref in r.get('parents',[]):assert sha(ROOT/ref['path'])==ref['sha256'],ref['path']
    base,parents,extra,checks,foot,post=records
    assert base['cases']==22 and extra['cases']==2 and post['cases']==24
    assert post['observation_rows']==144 and post['max_dof']==102033
    assert len(parents['parents'])==2 and len(checks['independent_load_integrals'])==3
    assert len(foot['feet'])==1 and foot['case_id']=='B30_middle_H0.0025_P14_X8'
    inputs.update(ROOT/'skrypty'/n for n in ['odtworz_podmodel_P19G.py','manifest_podmodelu_P19G.py','odtworz_wszystko.py'])
    outputs=sorted(p for pat in ['p19g_*','67_P19G*','68_P19G*','69_P19G*'] for p in OUT.glob(pat) if p.is_file())
    docs=[ROOT/n for n in ['README.md','AGENTS.md','PLAN_B_R.md','PROGRAM_30_BADAN.md',
        'raporty/README.md','raporty/041_lokalny_podmodel_i_granice_wiarygodnosci.md',
        'baza_wiedzy/README.md','baza_wiedzy/29_podmodel_i_transfer_obciazen.md']]
    result=dict(status=base['status'],generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
        libraries=dict(Python=platform.python_version(),NumPy=numpy.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__),
        coverage=dict(local_cases=24,observations=144,max_dof=102033,source_fields=3,new_source_fields=2,domains=3),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        output_sha256={str(p.relative_to(ROOT)):sha(p) for p in outputs},
        documentation_sha256={str(p.relative_to(ROOT)):sha(p) for p in docs},
        limitations=base['limitations']+post['no_claims'],
        next=post['next'])
    (OUT/'manifest_podmodelu_P19G.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('Manifest P19G:',len(inputs),'wejść,',len(outputs),'wyników;24podmodele,144okna,102033DOF;kwalifikacja spoin nadal otwarta.')


if __name__=='__main__':main()
