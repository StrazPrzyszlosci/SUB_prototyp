"""Kontrola wynikowych tabel: limity napędu i niezależny limit samego ruchu."""
import csv
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver,P_REF

ROOT=Path(__file__).resolve().parents[1]


def main():
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers={r['candidate_id']:Driver(**r['model']) for r in raw}
    summary=json.loads((ROOT/'wyniki/p09_p10_podsumowanie.json').read_text())
    rho=summary['medium']['rho_kg_m3']
    motion_errors=[];checked=0
    with (ROOT/'wyniki/p09_relaksacja_i_naped.csv').open() as handle:
        for r in csv.DictReader(handle):
            d=drivers[r['candidate_id']];f=float(r['f_hz'])
            assert float(r['thermal_loss_1v_w'])>=0 and float(r['leak_loss_1v_w'])>=0
            for vmax,imax in [(40.,12.),(60.,20.)]:
                for fraction in [.7,1.]:
                    prefix=f'V{int(vmax)}_X{fraction:g}'
                    voltage=float(r[prefix+'_voltage_rms'])
                    assert voltage<=vmax*(1+1e-12)
                    assert voltage*float(r['current_1v_rms_a'])<=imax*(1+1e-12)
                    assert voltage*float(r['x_peak_1v_mm'])<=fraction*d.xmax_mm*(1+1e-12)
                    if float(r['leak_ref_hz'])==0 and r[prefix+'_active_limit']=='catalog_x':
                        # Żaden K(s) nie zmienia p=omega²*rho*Sd*X/Ω przy osiągniętym X.
                        closed=rho*(2*np.pi*f)**2*d.sd*(d.xmax_mm*1e-3*fraction)/(np.sqrt(2)*2*np.pi)
                        from_table=P_REF*10**(float(r[prefix+'_spl_db'])/20)
                        motion_errors.append(abs(from_table/closed-1))
                    checked+=1
            if r['profile']=='ISOTHERMAL':
                expected=summary['medium']['gamma']*float(r['volume_l'])
                assert abs(float(r['equivalent_compliance_storage_l'])/expected-1)<1e-12
                assert abs(float(r['equivalent_compliance_loss_l']))<1e-12
    assert max(motion_errors)<1e-11
    material_checked=0
    with (ROOT/'wyniki/p09_modele_wypelnienia.csv').open() as handle:
        for r in csv.DictReader(handle):
            d=drivers[r['candidate_id']];f=float(r['f_hz'])
            assert float(r['internal_loss_1v_w'])>=-1e-12
            for vmax,imax in [(40.,12.),(60.,20.)]:
                for fraction in [.7,1.]:
                    prefix=f'V{int(vmax)}_X{fraction:g}'
                    voltage=float(r[prefix+'_voltage_rms'])
                    assert voltage<=vmax*(1+1e-12)
                    assert voltage*float(r['current_1v_rms_a'])<=imax*(1+1e-12)
                    assert voltage*float(r['x_peak_1v_mm'])<=fraction*d.xmax_mm*(1+1e-12)
                    if r[prefix+'_active_limit']=='catalog_x':
                        closed=rho*(2*np.pi*f)**2*d.sd*(d.xmax_mm*1e-3*fraction)/(np.sqrt(2)*2*np.pi)
                        from_table=P_REF*10**(float(r[prefix+'_spl_db'])/20)
                        motion_errors.append(abs(from_table/closed-1))
                    material_checked+=1
    assert max(motion_errors)<1e-11
    energy=list(csv.DictReader((ROOT/'wyniki/p10_bilans_energii.csv').open()))
    energy_error=max(abs(float(r['energy_residual_w']))/max(abs(float(r['work_mean_w'])),1e-10) for r in energy)
    exergy_error=max(abs(float(r['exergy_residual_w']))/max(abs(float(r['work_mean_w'])),1e-10) for r in energy)
    assert energy_error<1e-6 and exergy_error<1e-10
    result=dict(status='PASS_NAPED_I_NIEZALEZNY_LIMIT_RUCHU',sinusoidal_limits_checked=checked,
                material_sinusoidal_limits_checked=material_checked,
                motion_ceiling_identity_cases=len(motion_errors),
                max_relative_motion_ceiling_error=float(max(motion_errors)),
                nonlinear_cycles_checked=len(energy),max_relative_cycle_energy_error=energy_error,
                max_relative_cycle_exergy_error=exergy_error,
                scope='Graniczne tożsamości modelu, nie bezpieczna moc, pomiar THD ani tolerancje materiału.')
    (ROOT/'wyniki/p09_p10_kontrola_tabel.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':main()
