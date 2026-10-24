"""P11: kontrola V/I/X oraz niezależnych tożsamości gotowych tabel."""
import csv
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver,P_REF
from model_gazu import Medium

ROOT=Path(__file__).resolve().parents[1]


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p11_promieniowanie.json').read_text())
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers={r['candidate_id']:Driver(**r['model']) for r in raw}
    medium=Medium();counts={};groups={};max_analytic_error=0.;max_mach=0.;min_port_power=np.inf
    files=[('p11_geometrie_i_naped.csv','voltage_rms','current_1v_rms_a','x_peak_1v_mm'),
           ('p11_sciany_i_wzajemne.csv','voltage_per_amp_rms','max_current_per_amp_1v_rms_a','max_x_peak_1v_mm'),
           ('p11_pokoj_sprzezenie_zwrotne.csv','voltage_per_amp_rms','max_current_per_amp_1v_rms_a','max_x_peak_1v_mm')]
    for name,vfield,ifield,xfield in files:
        count=0
        with (ROOT/'wyniki'/name).open() as handle:
            for row in csv.DictReader(handle):
                d=drivers[row['candidate_id']];freq=float(row['f_hz'])
                for vmax,imax in cfg['amplifier_scenarios']:
                    for fraction in cfg['x_fractions']:
                        prefix=f'V{vmax:g}_X{fraction:g}'
                        voltage=float(row[prefix+'_'+vfield])
                        assert voltage<=vmax*(1+1e-11)
                        assert voltage*float(row[ifield])<=imax*(1+1e-11)
                        assert voltage*float(row[xfield])<=fraction*d.xmax_mm*(1+1e-11)
                        if name=='p11_geometrie_i_naped.csv':
                            if row['calibration_role']!='DOUBLE_COUNT_CONTROL':
                                max_mach=max(max_mach,2*np.pi*freq*voltage*float(row[xfield])*1e-3/medium.c)
                            if row[prefix+'_limit']=='catalog_x':
                                value=float(row[prefix+'_spl_1m_rms_db'])
                                key=(row['candidate_id'],row['volume_l'],row['geometry'],freq,fraction)
                                groups.setdefault(key,[]).append(value)
                                if row['geometry']=='INFINITE_BAFFLE_LUMPED':
                                    radius=np.sqrt(d.sd/np.pi)
                                    delta=radius*radius/(np.sqrt(1+radius*radius)+1)
                                    closed=2*medium.rho*medium.c*abs(np.sin(np.pi*freq*delta/medium.c))*2*np.pi*freq*d.xmax_mm*1e-3*fraction/np.sqrt(2)
                                    observed=P_REF*10**(value/20)
                                    max_analytic_error=max(max_analytic_error,abs(observed/closed-1))
                        count+=1
                if 'min_input_power_per_amp_1v_w' in row:
                    min_port_power=min(min_port_power,float(row['min_input_power_per_amp_1v_w']))
        counts[name]=count
    max_spread=max(max(v)-min(v) for v in groups.values())
    assert max_spread<1e-9 and max_analytic_error<1e-10
    normalization_error=0.;normalization_rows=0
    with (ROOT/'wyniki/p11_normalizacje_odniesienia.csv').open() as handle:
        for row in csv.DictReader(handle):
            normalization_error=max(normalization_error,abs(float(row['equivalent_2pi_1m_1v_db'])-float(row['equivalent_4pi_1m_1v_db'])-20*np.log10(2)))
            normalization_rows+=1
    assert normalization_error<1e-11
    dense=json.loads((ROOT/'wyniki/p11_pokoj_gesty_skan.json').read_text())
    assert dense['cases']==24*4*4*3*3*2 and dense['frequency_points']==601
    assert dense['max_relative_energy_residual']<1e-10
    spatial=json.loads((ROOT/'wyniki/p11_pokoj_zbieznosc_przestrzenna.json').read_text())
    assert spatial['max_relative_port_difference']<1e-7
    assert np.isfinite(min_port_power)
    result=dict(status='PASS_LIMITOW_I_TOZSAMOSCI_P11_NIE_WALIDACJA_URZADZENIA',
                sinusoidal_combinations_checked=sum(counts.values()),counts=counts,
                motion_limited_groups=len(groups),max_motion_limited_group_spread_db=max_spread,
                max_relative_closed_axis_motion_ceiling_error=max_analytic_error,
                normalization_rows=normalization_rows,max_normalization_difference_error_db=normalization_error,
                max_peak_mach_in_calibrated_scalar_cases=max_mach,
                minimum_per_amp_input_power_1v_w=min_port_power,
                scope='Ograniczenia liniowych sinusów V/I/X. Mach jest cechą modelu, nie gwarancją THD lub bezpiecznej mocy.')
    (ROOT/'wyniki/p11_kontrola_pakietu.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
