"""Oddzielna zbieznosc po grubosci;nie powtarza pierwotnej kampanii."""
import csv,gc,hashlib,json
from pathlib import Path
from model_ramy_3D_P18C import Cabinet3D
from uzupelnienie_siatki_ramy_P18C import point

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    old=json.loads((OUT/'p18c_adaptacja_i_granice.json').read_text())
    previous=old['thickness3'];rows=[]
    for layers in [4,5]:
        b=Cabinet3D(n=10,nt=layers);r=point(b,'THICKNESS_'+str(layers))
        r['layers']=layers;r['relative_change_compliance']=abs(r['compliance_m3_pa']/previous['compliance_m3_pa']-1)
        r['relative_change_f1']=abs(r['first_elastic_hz']/previous['first_elastic_hz']-1);rows.append(r)
        print('P18C thickness',r,flush=True);del b;gc.collect()
        if max(r['relative_change_compliance'],r['relative_change_f1'])<.01:break
        previous=r
    result=dict(status='SCOPED_THICKNESS_CONVERGENCE',rows=rows,
                criterion='Ostatnia zmiana C/f1<1%,nie scisly blad continuum;N10 pozostaje osobna dyskretyzacja.',
                input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                              ['skrypty/sprawdz_warstwy_ramy_P18C.py','skrypty/model_ramy_3D_P18C.py','skrypty/element_brylowy_P18C.py',
                               'skrypty/uzupelnienie_siatki_ramy_P18C.py','wyniki/p18c_adaptacja_i_granice.json']})
    (OUT/'p18c_zbieznosc_grubosci.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))


if __name__=='__main__':main()
