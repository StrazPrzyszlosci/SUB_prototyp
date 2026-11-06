"""Counterexamples from the method audit, exercised through the actual exporter CLI."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from k38_zlozenie import ROOT, geometry, preview_record

with TemporaryDirectory() as tmp:
    folder=Path(tmp)
    data=preview_record()
    data['reference_design']='K38'
    data['records']={'stock':'TEST','dry_fit':'TEST'}
    data['dry_fit']['finished_thickness_mm']=geometry(data,True,True,True)['finish']
    data['dry_fit']['support_top_z_mm']['RAIL_A_0_F']-=1.5
    for axis,expected,code in [(None,42,0),('Y',34,2),('Z',34,2)]:
        if axis:
            for size in data['dry_fit']['insert_xyz_mm'].values():
                size[axis]+=2
        card=folder/'card.json'
        card.write_text(json.dumps(data))
        archive=folder/f'{axis}.zip'
        result=subprocess.run([sys.executable,str(ROOT/'skrypty/k40_pakiet_dxf.py'),str(archive),'--karta-fit',str(card)])
        assert result.returncode==code
        with ZipFile(archive) as z:
            report=json.loads(z.read('KONTROLA.json'))
            assert sum(n.endswith('.dxf') for n in z.namelist())==(95 if code==0 else 0)
            motion=report['ruch_proponowanej_geometrii']
            assert motion['clear']==expected
            if axis:
                assert any(err['margin_mm']<0 and err['obstacle'] for e in motion['events'] for err in e['errors'])
            row=report['podparcie_wkladow']['M0N']
            assert row['rozrzut_podpor_z_pomiarow_mm']==1.5 and row['rozrzut_podpor_proponowany_mm']==0
            assert row['proba_rzedu_po_zamknieciu_100L'] is None
        if axis:
            for size in data['dry_fit']['insert_xyz_mm'].values():
                size[axis]-=2
    clamp=json.loads((ROOT/'dane/k39_proba_rzedu.json').read_text())
    clamp.update(rzad_i_konfiguracja='0/100L',protokol_montazu_K38='TEST',
                 partia_i_wymiary_podkladek='TEST',protokol='TEST K39',podstawa_limitow_sily='TEST',
                 luz_min_mm=6.1,luz_max_mm=7.7,dystans_mm=2,blad_dystansu_mm=.1,
                 blad_wysokosci_mm=.05,blad_sily_N=1,min_docisk_N=10,max_docisk_N=50)
    trial=clamp['proby'][0]
    trial.update(dict.fromkeys(trial,True))
    trial.update(wysokosc_mala_mm=3.95,wysokosc_duza_mm=5.85,maks_sila_mala_N=49,
                 min_sila_duza_N=11,czas_mala_h=24,czas_duza_h=24,pelne_podparcie=False)
    clamp_file=folder/'clamp.json'
    clamp_file.write_text(json.dumps(clamp))
    card.write_text(json.dumps(data))
    target=folder/'clamp.zip'
    subprocess.run([sys.executable,str(ROOT/'skrypty/k40_pakiet_dxf.py'),str(target),
                    '--karta-fit',str(card),'--proba-k39',str(clamp_file)],check=True)
    with ZipFile(target) as z:
        entry=json.loads(z.read('KONTROLA.json'))['podparcie_wkladow']['M0N']
        assert entry['ruch_po_korekcie'] and entry['proba_rzedu_po_zamknieciu_100L']['wynik']=='ODRZUĆ'
    with ZipFile(ROOT/'dokumentacja/cnc/K45_PROBA_FRONTU/SUB_K45_PROBA_FRONTU.zip') as z:
        for name in z.namelist():
            path=ROOT/name if name!='START.md' else ROOT/'dokumentacja/cnc/K45_PROBA_FRONTU/START.md'
            assert z.read(name)==path.read_bytes()
        z.extractall(folder/'front')
    subprocess.run([sys.executable,'skrypty/sprawdz_k43.py'],cwd=folder/'front',check=True)
print('K46: eksport, diagnostyka podparcia i paczka warsztatowa OK')
