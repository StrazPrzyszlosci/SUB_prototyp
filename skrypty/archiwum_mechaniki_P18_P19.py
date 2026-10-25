"""Wersjonowane archiwa zamkniętych checkpointów mechaniki,bez usuwania danych."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def paths(stage):
    if stage not in ['p18a','p19a']:raise ValueError('p18a albo p19a')
    summary=json.loads((OUT/(stage+'_podsumowanie.json')).read_text())
    return summary,OUT/(stage+'_checkpoint_'+summary['run_sha256'][:16]+'.zip'),OUT/(stage+'_archiwum.json')


def pack(stage):
    summary,target,manifest=paths(stage);folder=ROOT/summary['checkpoint_folder']
    files=sorted(p for p in folder.iterdir() if p.suffix in ['.json','.npz'])
    assert sum(p.suffix=='.json' for p in files)==summary['cases']
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    metadata=dict(run_sha256=summary['run_sha256'],cases=summary['cases'],input_sha256=summary['input_sha256'],file_sha256=hashes)
    temp=target.with_suffix('.tmp')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        entries=[('metadata.json',json.dumps(metadata,sort_keys=True,ensure_ascii=False).encode()),*[(p.name,p.read_bytes()) for p in files]]
        for name,data in entries:
            assert name=='metadata.json' or re.fullmatch(r'\d{4}\.(json|npz)',name)
            info=zipfile.ZipInfo(name,date_time=(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compresslevel=9)
    temp.replace(target)
    result=dict(status='IMMUTABLE_CHECKPOINT_ARCHIVE_NOT_INDEPENDENT_REPLICATION',stage=stage,cases=summary['cases'],archive_file=target.name,
        archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),input_sha256=summary['input_sha256'],run_sha256=summary['run_sha256'])
    manifest.write_text(json.dumps(result,indent=2,ensure_ascii=False));print(stage,'archiwum:',target.stat().st_size,'bajtów');return result


def restore(stage):
    summary,target,manifest=paths(stage);meta=json.loads(manifest.read_text())
    assert hashlib.sha256(target.read_bytes()).hexdigest()==meta['archive_sha256']
    for name,h in meta['input_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    folder=ROOT/summary['checkpoint_folder'];folder.mkdir(exist_ok=True,parents=True)
    with zipfile.ZipFile(target) as z:
        data=json.loads(z.read('metadata.json'));assert data['run_sha256']==summary['run_sha256']
        assert set(z.namelist())=={'metadata.json',*data['file_sha256']}
        for name,h in data['file_sha256'].items():
            assert re.fullmatch(r'\d{4}\.(json|npz)',name)
            raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==h;path=folder/name
            if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==h,name
            else:path.write_bytes(raw)
    print(stage,'checkpointy sprawdzone/odtworzone; bez świeżychODE/MES.');return meta


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['pack','restore']);parser.add_argument('stage',choices=['p18a','p19a']);args=parser.parse_args()
    pack(args.stage) if args.operation=='pack' else restore(args.stage)
