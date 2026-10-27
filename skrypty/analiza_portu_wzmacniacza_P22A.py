"""27konfiguracji:rezystancja źródła,rozdzielone prądy i obwiednie V/I/X."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,hashlib,json,platform
import numpy as np
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import alignment,RHO,C
from model_portu_wzmacniacza_P22 import port_response,limited_port

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    cfgp=ROOT/'dane/konfiguracje/p22a_port_wzmacniacza.json';cfg=json.loads(cfgp.read_text());pool=candidates()
    f=np.unique(np.r_[np.geomspace(*cfg['band_hz'],cfg['band_points']),cfg['probes_hz']]);probes=np.array(cfg['probes_hz'])
    vlim,ilim=cfg['source_voltage_rms_limit_v_assumed'],cfg['source_current_rms_limit_a_assumed'];rows=[];sweeps=[];qs=[];energy=0.
    for cid,pid,d,cat in pool:
        for vb in cfg['volumes_l']:
            fc,qc,_=alignment(d,vb);K=1/d.cms+RHO*C*C*d.sd*d.sd/(vb*.001)
            baseline=port_response(d,vb,f)
            basep,basescale,baseactive=limited_port(d,vb,probes,0,0,0,vlim,ilim)
            for rs in cfg['source_resistance_ohm_assumed']:
                damping=d.rms+d.bl*d.bl/(d.re_ohm+rs)
                q_rs=np.sqrt(d.mms*K)/damping
                qs.append(dict(configuration=cid,driver_name=d.name,volume_l=vb,rs_ohm=rs,
                    fc_Le0_hz=fc,qtc_Le0_ideal=qc,qtc_Le0_with_source_R=q_rs,
                    relative_q_increase=q_rs/qc-1,
                    interpretation='Le0/C0/L0 projection;not one Q for the general RLC model.'))
                for network in cfg['passive_output_networks_assumed']:
                    ls,cp=network['series_h'],network['shunt_f'];r=port_response(d,vb,f,rs,ls,cp)
                    energy=max(energy,float(np.max(r['energy_relative_residual'])))
                    pressure_ratio=r['pressure']/baseline['pressure'];changes=20*np.log10(abs(pressure_ratio));worst=int(np.argmax(abs(changes)))
                    sweeps.append(dict(configuration=cid,driver_name=d.name,volume_l=vb,rs_ohm=rs,network=network['id'],
                        max_abs_constant_source_gain_change_db=float(np.max(abs(changes))),
                        witness_f_hz=float(f[worst]),signed_change_at_witness_db=float(changes[worst]),
                        max_terminal_voltage_per_source_voltage=float(np.max(abs(r['terminal_voltage']))),
                        max_source_current_per_driver_current=float(np.max(abs(r['source_current']/r['driver_current']))),
                        max_energy_relative_residual=float(np.max(r['energy_relative_residual']))))
                    a,scale,active=limited_port(d,vb,probes,rs,ls,cp,vlim,ilim)
                    spl=20*np.log10(abs(a['pressure'])*scale/20e-6)
                    base_spl=20*np.log10(abs(basep['pressure'])*basescale/20e-6)
                    for i,hz in enumerate(probes):
                        rows.append(dict(configuration=cid,driver_name=d.name,volume_l=vb,rs_ohm=rs,network=network['id'],f_hz=hz,
                            source_vrms=float(scale[i]),terminal_vrms=float(abs(a['terminal_voltage'][i])*scale[i]),
                            source_irms=float(abs(a['source_current'][i])*scale[i]),
                            driver_irms=float(abs(a['driver_current'][i])*scale[i]),
                            x_peak_mm=float(np.sqrt(2)*abs(a['x'][i])*scale[i]*1000),
                            spl_rms_2pi_1m_db=float(spl[i]),difference_from_ideal_source_db=float(spl[i]-base_spl[i]),
                            active_limit=['source_voltage','source_current','catalog_Xmax_reference'][active[i]],
                            source_resistance_loss_w=float(a['source_loss'][i]*scale[i]**2),
                            coil_copper_loss_w=float(a['coil_loss'][i]*scale[i]**2),
                            mechanical_loss_w=float(a['mechanical_loss'][i]*scale[i]**2)))
    assert energy<1e-10
    write('p22a_naped_z_portem.csv',rows);write('p22a_zmiana_transferu.csv',sweeps);write('p22a_Q_z_rezystancja.csv',qs)
    inputs=['brief_system_audio_DIY_v0.6.md','dane/konfiguracje/p22a_port_wzmacniacza.json',
        'dane/przetworniki/pula_rozszerzona.json','dane/przetworniki/rozszerzenie_SB_20261025.json',
        'skrypty/analiza_portu_wzmacniacza_P22A.py','skrypty/model_portu_wzmacniacza_P22.py',
        'skrypty/model_subwoofera.py','skrypty/analiza_rozszerzenia_SB.py']
    summary=dict(status='COMPLETE_SCOPED_PASSIVE_SOURCE_FAMILIES_NOT_REAL_AMPLIFIER',
        generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),configurations=len(pool),
        networks=len(sweeps),drive_rows=len(rows),Q_projections=len(qs),frequency_points_per_sweep=len(f),
        max_energy_relative_residual=energy,input_sha256={n:sha(ROOT/n) for n in inputs},
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__),limitations=cfg['limitations'],
        next='P22B/P24:saturated dynamic amplifier port,back-EMF/current feasibility and explicit protection;no product attribution.')
    (OUT/'p22a_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    print('P22A:',len(sweeps),'ports;',len(rows),'drive;',len(qs),'Q;energy',energy)


if __name__=='__main__':main()
