"""Odtwórz zamrożonych świadków i termikę P15A bez dotykania żywej kampanii.

To odtwarzanie wybranego opublikowanego etapu, nie całego programu badań.
"""
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import scipy
import matplotlib
import sympy

ROOT=Path(__file__).resolve().parents[1]


def main():
    from sprawdz_emisje_P14B import main as emission_checks
    from raportuj_P14B_swiadkow import main as witnesses
    from analiza_topologii_termicznej_P15A import main as thermal
    from audyt_symboliczny_P15A import main as symbolic
    from sprawdz_granice_termiczne_P15A import main as limits
    emission_checks();witnesses();thermal();symbolic();limits()
    names=['model_wymuszen_P14B.py','model_emisji_P14B.py','sprawdz_emisje_P14B.py',
           'raportuj_P14B_swiadkow.py','model_termiczny_P15.py','analiza_topologii_termicznej_P15A.py',
           'audyt_symboliczny_P15A.py','sprawdz_granice_termiczne_P15A.py',Path(__file__).name,
           'model_promieniowania.py','model_gazu.py','model_nieliniowy.py','model_subwoofera.py',
           'projekcja_P14B.py','analiza_cewki_z_pamiecia.py','model_cewki_z_pamiecia.py']
    inputs=[ROOT/'skrypty'/name for name in names]+[ROOT/'brief_system_audio_DIY_v0.6.md']
    inputs+=[ROOT/'dane/konfiguracje'/name for name in ['p14b_IMD.json','p14b_emisja.json','p15a_topologia_termiczna.json','p12c_pamiec_cewki.json']]
    inputs+=[ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'wyniki/p14b_swiadkowie_emisji.npz',ROOT/'wyniki/p14b_swiadkowie_emisji.json']
    inputs+=[ROOT/'dane/zrodla'/name for name in ['P14B_IMD_AM_FM_i_emisja.json','P15A_topologie_i_cieplo.json']]
    outputs=[]
    for pattern in ['31_P14B*','32_P14B*','33_P14B*','34_P15A*','35_P15A*','p15a_*','p14b_kontrole_emisji.json','p14b_swiadkowie_wyniki.json']:
        outputs.extend((ROOT/'wyniki').glob(pattern))
    result=dict(status='REPLAY_SELECTED_STAGE_NOT_FULL_CAMPAIGN',
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,SymPy=sympy.__version__),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        output_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(outputs))},
        scope='15zamrożonych świadków iP15A. AktywneSQLite, globalny manifest i pozostałe pakiety nie są odtwarzane ani zamykane tą procedurą.')
    (ROOT/'wyniki/manifest_etap_P14B_P15A.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print('Zapisano manifest etapu; bez odczytu/modyfikacji aktywnych bazP14B.')
    return result


if __name__=='__main__':main()
