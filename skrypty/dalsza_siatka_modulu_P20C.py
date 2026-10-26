"""Rozstrzygnięcie8flag przy wspólnych Hz,dalsza siatkaN16;bez zmianyprogu.

Pierwotne wyniki N8/N12 pozostają bez zmian. Zagęszczamy wszystkie cztery
rodziny z flagami,nie tylko wygodny wariant prototypu.
"""
from pathlib import Path
import csv,gc,hashlib,json,resource
import numpy as np
from model_modulu_3D_P20C import SolidModule,gas_port
from sprawdz_modul_3D_P20C import invariants
from sprawdz_siatke_modulu_P20C import matrix
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cp=ROOT/'dane/konfiguracje/p20c_modul_pelny_3D.json';cfg=json.loads(cp.read_text());bp=ROOT/cfg['reference_insert_config'];base=json.loads(bp.read_text())
    stage=json.loads((OUT/'p20c_podsumowanie.json').read_text());folder=ROOT/stage['checkpoint_folder']
    source=OUT/'p20c_niezalezna_siatka_i_wspolne_Hz.csv'
    with source.open() as f:flags=[r for r in csv.DictReader(f) if r['within_assumed_5pct_port_screen']=='False']
    assert len(flags)==8 and len({r['reference_case'] for r in flags})==4
    rows=[];probe_rows=[];controls=[];sources=[]
    for case in sorted({r['reference_case'] for r in flags}):
        path=folder/(case+'.json');ref=json.loads(path.read_text());sources.append(path)
        braced=ref['summary']['braced'];eg=ref['summary']['glue_E_pa'];frequencies=sorted({float(r['f_hz']) for r in flags if r['reference_case']==case})
        available=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))*1024
        if available<2_500_000_000:raise RuntimeError('Available RAM guard before N16: preserve results and resume after memory is available.')
        m=SolidModule(base,cfg,16,braced=braced,glue_E=eg);controls.append(dict(case=case,**invariants(m)))
        allf=sorted(set(frequencies+cfg['probe_frequencies_hz']));direct=m.direct(allf);Ci=m.inner_volume/(1.4*101325.)
        reference_matrices={r['f_hz']:matrix(r) for r in ref['mechanical_ports']}
        for i,f in enumerate(allf):
            c=direct['chi'][i];old=reference_matrices[f];Y=gas_port([f],c[None,:,:],Ci)['admittance'][0];Yref=gas_port([f],old[None,:,:],Ci)['admittance'][0]
            err=float(np.linalg.norm(c-old)/np.linalg.norm(old));yer=float(abs(Y/Yref-1))
            row=dict(reference_case=case,mesh_resolution=16,ndof=m.ndof,f_hz=f,matrix_relative_difference=err,sealed_admittance_relative_difference=yer,
                within_assumed_5pct_port_screen=bool(max(err,yer)<=cfg['mesh_relative_change_screen_assumed']),
                normalized_power_residual=direct['power_residual'],returned_storage_l=float((Y/(2j*np.pi*f)).real*1.4*101325*1000))
            for a in range(2):
                for b in range(2):row[f'chi_{a}{b}_re_m3_pa']=float(c[a,b].real);row[f'chi_{a}{b}_im_m3_pa']=float(c[a,b].imag)
            (rows if f in frequencies else probe_rows).append(row)
        print('P20C N16:',case,'DOF',m.ndof,'max flagged-Hz matrix change',max(r['matrix_relative_difference'] for r in rows if r['reference_case']==case),flush=True)
        table('p20c_dalsza_siatka_przy_modach.csv',rows);table('p20c_dalsza_siatka_w_pasmie.csv',probe_rows)
        del m;gc.collect()
    inputs=[cp,bp,source,Path(__file__),ROOT/'skrypty/model_modulu_3D_P20C.py',ROOT/'skrypty/sprawdz_modul_3D_P20C.py',ROOT/'skrypty/sprawdz_siatke_modulu_P20C.py',
        ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'skrypty/model_ramy_3D_P18C.py',*sources]
    j=dict(status='ADDITIONAL_N16_FOR_ALL_FOUR_FLAGGED_FAMILIES_NOT_CONTINUUM_CERTIFICATE',previous_flagged_rows=len(flags),rows=len(rows),probe_rows=len(probe_rows),
        remaining_flags=sum(not r['within_assumed_5pct_port_screen'] for r in rows),controls=controls,
        peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Same absolute frequencies and unchanged5%screen;selected finite witnesses,not every continuous frequency.',
            'Main N12driver study remains its own approximation;N16band differences separately retained.',
            'Formal gas0D reduction near/above first empty-cavity reference is not physical mode validation.'])
    (OUT/'p20c_dalsza_siatka_podsumowanie.json').write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20C N16 audit:',len(rows),'former flags;',j['remaining_flags'],'remaining;',j['peak_rss_mib'],'MiB',flush=True)


if __name__=='__main__':main()
