"""Wspólne częstotliwości przy modach i osobne kierunki siatki3D.

Porównanie przy tych samych Hz,nie różnych węzłach wokół przesuniętych modów.
Próg5% to roboczy ekran eksperymentu,nie oszacowanie błędu fizycznego.
"""
from pathlib import Path
from itertools import product
import gc,hashlib,json,resource
import numpy as np
from model_modulu_3D_P20C import SolidModule,gas_port
from analiza_modulu_3D_P20C import modal_chi
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def matrix(row):
    return np.array([[complex(row[f'chi_{a}{b}_re_m3_pa'],row[f'chi_{a}{b}_im_m3_pa']) for b in range(2)] for a in range(2)])


def main():
    cp=ROOT/'dane/konfiguracje/p20c_modul_pelny_3D.json';cfg=json.loads(cp.read_text());bp=ROOT/cfg['reference_insert_config'];base=json.loads(bp.read_text())
    stage=json.loads((OUT/'p20c_podsumowanie.json').read_text());assert stage['cases']==stage['expected_cases']==18
    folder=ROOT/stage['checkpoint_folder'];rows=[];sources=[];ng=cfg['glue_elements'];nt=cfg['wall_elements']
    n0,n1=cfg['mesh_resolution_cases'][-2:]
    def compare(m,label,reference,frequencies):
        out=m.direct(frequencies);ref=np.array([matrix(next(r for r in reference['mechanical_ports'] if r['f_hz']==f)) for f in frequencies])
        value=np.linalg.norm(out['chi']-ref,axis=(1,2))/np.linalg.norm(ref,axis=(1,2))
        Ci=m.inner_volume/(1.4*101325.);ym=gas_port(frequencies,out['chi'],Ci)['admittance'];yr=gas_port(frequencies,ref,Ci)['admittance']
        for j,f in enumerate(frequencies):
            rows.append(dict(comparison=label,reference_case=reference['summary']['case_id'],f_hz=f,
                matrix_relative_difference=float(value[j]),sealed_admittance_relative_difference=float(abs(ym[j]/yr[j]-1)),
                common_pressure_relative_difference=float(abs(out['chi'][j].sum()/ref[j].sum()-1)),
                power_residual=out['power_residual'],ndof=m.ndof,
                within_assumed_5pct_port_screen=bool(max(value[j],abs(ym[j]/yr[j]-1))<=cfg['mesh_relative_change_screen_assumed'])))
    for braced,eg in product([False,True],[min(cfg['glue_E_pa_cases_assumed']),max(cfg['glue_E_pa_cases_assumed'])]):
        key=f"{'TIED' if braced else 'BARE'}_E{eg:g}"
        finepath=folder/f'{key}_N{n1}.json';fine=json.loads(finepath.read_text());sources.append(finepath)
        frequencies=[r['f_hz'] for r in fine['mechanical_ports'] if not r['is_probe']]
        m=SolidModule(base,cfg,n0,braced=braced,glue_E=eg);compare(m,f'N{n0}_vs_N{n1}_COMMON_HZ',fine,frequencies)
        print('P20C common-frequency audit:',key,len(frequencies),flush=True);del m;gc.collect()
    # Grubość MDF i grubość spoiny zagęszczamy osobno; nie zmieniamy geometrii.
    key=f'TIED_E{max(cfg["glue_E_pa_cases_assumed"]):g}_N{n0}';path=folder/(key+'.json');ref=json.loads(path.read_text());sources.append(path)
    frequencies=[20.,80.]+[r['f_hz'] for r in ref['mechanical_ports'] if not r['is_probe']]
    for nw,ngl,label in [(2*nt,ng,'WALL_LAYERS_2_TO_4'),(nt,2*ng,'GLUE_LAYERS_1_TO_2')]:
        m=SolidModule(base,cfg,n0,braced=True,glue_E=max(cfg['glue_E_pa_cases_assumed']),wall_elements=nw,glue_elements=ngl)
        compare(m,label,ref,frequencies);print('P20C layer audit:',label,'DOF',m.ndof,flush=True);del m;gc.collect()
    table('p20c_niezalezna_siatka_i_wspolne_Hz.csv',rows)
    inputs=[cp,bp,Path(__file__),ROOT/'skrypty/model_modulu_3D_P20C.py',ROOT/'skrypty/analiza_modulu_3D_P20C.py',
        ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'skrypty/model_ramy_3D_P18C.py',*sources]
    summary=dict(status='SELECTED_SAME_FREQUENCY_AND_SEPARATE_THICKNESS_WITNESSES',cases=len(rows),
        outside_assumed_5pct_port_screen=sum(not r['within_assumed_5pct_port_screen'] for r in rows),
        max_matrix_relative_difference=max(r['matrix_relative_difference'] for r in rows),
        max_sealed_admittance_relative_difference=max(r['sealed_admittance_relative_difference'] for r in rows),
        peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Selected common-Hz and thickness witnesses,not continuum or all-frequency certification.',
            'Gas reduction beyond empty-cavity reference is formal; it does not validate a physical spatial mode.'])
    (OUT/'p20c_siatka_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20C mesh audit:',len(rows),'points;',summary['outside_assumed_5pct_port_screen'],'flags',flush=True)


if __name__=='__main__':main()
