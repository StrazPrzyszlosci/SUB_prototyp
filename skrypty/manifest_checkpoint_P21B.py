"""Jawna częściowa migawkaP21B do publikacji,bez deklaracji18/18."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,hashlib,json,shutil
from odtworz_wszystko import assert_no_live_spatial_campaign

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert_no_live_spatial_campaign()
    status=json.loads((OUT/'p21b_podsumowanie.json').read_text())
    assert status['cases']==17 and status['expected_cases']==18
    for n,h in status['input_sha256'].items():assert sha(ROOT/n)==h,n
    cases=sorted((ROOT/status['checkpoint_folder']).glob('*.json'));assert len(cases)==17
    for p in cases:
        j=json.loads(p.read_text());assert j['run_sha256']==status['run_sha256'] and j['input_sha256']==status['input_sha256']
    outputs=sorted([p for p in OUT.glob('p21b_*') if p.is_file()]+cases)
    # Zamrażamy własne wyniki,aby końcowe P21B mogło później odtworzyć
    # pliki robocze bez pozornego przepisywania tej historycznej migawki.
    snapshot=OUT/'checkpointy'/'P21B_20261027_17_modeli';frozen=[];mapping={}
    for source in outputs:
        relative=Path('przypadki')/source.name if source in cases else Path(source.name)
        target=snapshot/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert sha(target)==sha(source),'Do not overwrite an existing different snapshot'
        else:shutil.copy2(source,target)
        assert sha(target)==sha(source);frozen.append(target);mapping[str(source.relative_to(ROOT))]=str(target.relative_to(ROOT))
    record=dict(status='PARTIAL_RESEARCH_SNAPSHOT_17_OF_18_NOT_FINAL_P21B',
        generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),run_sha256=status['run_sha256'],
        completed_models=17,expected_models=18,saved_frequency_systems=status['frequency_cases'],saved_field_rows=status['field_rows'],
        process_state_at_snapshot='No held campaign flock;previous processes stopped before final atomic case checkpoint.',
        not_completed='TIED_E1.718e+09_N12 and full-stage mesh/postprocessing/report045;partial log frequencies are not a saved completed case.',
        input_sha256=status['input_sha256'],output_sha256={str(p.relative_to(ROOT)):sha(p) for p in frozen},
        original_working_paths_to_frozen_snapshot=mapping,
        current_constraints_sha256={'dane/konfiguracje/ograniczenia_gabarytow_v1_20261027.json':sha(ROOT/'dane/konfiguracje/ograniczenia_gabarytow_v1_20261027.json')},
        pending_postprocessing_code_sha256={str((ROOT/'skrypty'/n).relative_to(ROOT)):sha(ROOT/'skrypty'/n) for n in [
            'asymptotyka_gazu_P21B.py','granica_obciazenia_P21B.py','wykresy_i_ocena_gazu_P21B.py',
            'raportuj_gaz_przestrzenny_P21B.py','manifest_gazu_przestrzennego_P21B.py','odtworz_gaz_przestrzenny_P21B.py']},
        snapshot_code_sha256={str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__).resolve())},
        limitations=['This checkpoint is not manifest_gazu_przestrzennego_P21B.json and does not certify the complete18-model campaign.',
            'Do not infer current process liveness from the old PARTIAL_ACTIVE label in a stored status file;inspect process and actual flock.',
            'New U026 depth<=500mm excludes the old full-cabinet geometry as a final enclosure;module results remain conditional control data.'])
    (OUT/'manifest_checkpoint_P21B.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print('P21B checkpoint:17/18models,',status['frequency_cases'],'saved systems;partial,not final stage.')


if __name__=='__main__':main()
