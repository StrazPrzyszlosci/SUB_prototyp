"""Pakowanie/weryfikowane odtworzenie zgodnych checkpointów, bez zmiany ODE.

Zgodne odtworzenie cache nie jest niezależnym nowym rachunkiem2304ODE.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def pack():
    summary=json.loads((OUT/'p15b_podsumowanie.json').read_text());run=summary['run_sha256'];cache=ROOT/summary['checkpoint_folder']
    files=sorted(cache.glob('*.json'))
    assert len(files)==summary['cases']==2304
    for p in files:assert re.fullmatch(r'\d{4}\.json',p.name)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    metadata=dict(run_sha256=run,cases=len(files),input_sha256=summary['input_sha256'],file_sha256=hashes)
    target=OUT/('p15b_checkpoint_'+run[:16]+'.zip');temp=target.with_suffix('.tmp')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in [('metadata.json',json.dumps(metadata,ensure_ascii=False,sort_keys=True).encode()),*[(p.name,p.read_bytes()) for p in files]]:
            info=zipfile.ZipInfo(name,date_time=(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compresslevel=9)
    temp.replace(target)
    manifest=dict(status='PACKED_CONDITIONAL_SIMULATION_CHECKPOINTS_NOT_MEASUREMENTS',run_sha256=run,
        archive_file=target.name,archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),cases=len(files),input_sha256=summary['input_sha256'],
        scope='Przechowywanie zgodnych checkpointów do odtworzenia artefaktów. Niezależne sprawdzenia opisano osobno.')
    (OUT/'p15b_checkpoint_archiwum.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('ArchiwumP15B:',len(files),'rekordów,',target.stat().st_size,'bajtów');return manifest


def restore():
    manifest=json.loads((OUT/'p15b_checkpoint_archiwum.json').read_text());path=OUT/manifest['archive_file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['archive_sha256']
    for name,digest in manifest['input_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    target=OUT/'p15b_checkpoint'/manifest['run_sha256'][:16];target.mkdir(exist_ok=True,parents=True)
    with zipfile.ZipFile(path) as z:
        metadata=json.loads(z.read('metadata.json'));assert metadata['run_sha256']==manifest['run_sha256']
        assert len(metadata['file_sha256'])==manifest['cases']
        assert set(z.namelist())=={'metadata.json',*metadata['file_sha256']}
        for name,digest in metadata['file_sha256'].items():
            assert re.fullmatch(r'\d{4}\.json',name);data=z.read(name);assert hashlib.sha256(data).hexdigest()==digest
            destination=target/name
            if destination.exists():assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest,name
            else:destination.write_bytes(data)
    print('Sprawdzono/odtworzono',manifest['cases'],'checkpointyP15B; bez nowej integracjiODE.')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['pack','restore']);args=parser.parse_args()
    pack() if args.operation=='pack' else restore()
