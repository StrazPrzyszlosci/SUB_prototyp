"""Odtwarzanie P19G: źródła/cache tylko po hashach, ciężkie przypadki kolejno."""
from pathlib import Path
import hashlib,json


def main():
    from archiwizuj_pola_globalne_P19G import main as parents
    from analiza_podmodelu_P19G import main as study
    from uzupelnij_zbieznosc_P19G import main as directional
    from sprawdz_transfer_P19G import main as checks
    from audyt_stopy_zamrozonej_P19G import main as foot
    from wykresy_i_ocena_P19G import main as plots
    from manifest_podmodelu_P19G import main as manifest
    root=Path(__file__).resolve().parents[1];path=root/'wyniki/p19g_pola_globalne.json';valid=False
    if path.exists():
        d=json.loads(path.read_text())
        valid=all((root/n).exists() and hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in d['input_sha256'].items())
        valid=valid and all((root/r['path']).exists() and hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in d['parents'])
    if not valid:parents()
    else:print('P19G: zgodne pola globalne z hashem; bez ponowienia dwóch globalnych modeli.')
    study();directional();checks();foot();plots();manifest()


if __name__=='__main__':main()
