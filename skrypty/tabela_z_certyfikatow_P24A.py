"""Odtwórz tabelę z wersjonowanych świadków;stdlib,bez nowego SDP."""
from pathlib import Path
from fractions import Fraction as F
import csv,json

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main(target=None):
    cfg=json.loads((ROOT/'dane/konfiguracje/p24a_wspolny_obszar_niezmienniczy.json').read_text())
    summary=json.loads((OUT/'p24a_podsumowanie.json').read_text());assert summary['cases']==972
    records=[json.loads(p.read_text()) for p in (ROOT/summary['checkpoint_folder']).glob('*.json')]
    records.sort(key=lambda r:(r['configuration'],cfg['volumes_l'].index(r['volume_l']),
        cfg['thermal_resistance_k_w_assumed'].index(r['Rth_assumed_k_w']),
        cfg['temperature_rise_limit_k_assumed'].index(r['temperature_rise_limit_k']),
        cfg['catalog_x_reference_fraction'].index(r['X_catalog_reference_fraction'])))
    assert len(records)==972;rows=[]
    for r in records:
        cert=r['certificate'];rows.append(dict(case_id=r['case_id'],configuration=r['configuration'],driver_name=r['driver_name'],
            volume_l=r['volume_l'],Rth_assumed_k_w=r['Rth_assumed_k_w'],temperature_rise_limit_k=r['temperature_rise_limit_k'],
            X_catalog_reference_fraction=r['X_catalog_reference_fraction'],status=r['status'],
            source_peak_voltage_v=float(F(cert['source_peak_voltage_v'])) if cert else '',
            current_peak_bound_a=float(F(cert['parameters']['Icap'])) if cert else '',
            X_reference_mm=float(F(cert['parameters']['Xref'])*1000) if cert else '',
            lambda_value_per_s=float(F(cert['lambda_value'])) if cert else '',
            trial_count=len(r['trials']),accepted_lambda_witnesses=sum(v.get('candidate_accepted',False) for v in r['trials'])))
    target=Path(target) if target else OUT/'p24a_obszary_i_poziomy.csv'
    with target.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('P24A:table reconstructed from972stored witnesses;not a new SDP search.')


if __name__=='__main__':main()
