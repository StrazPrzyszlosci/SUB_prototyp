"""Build a single K38-based DXF review archive. No machine toolpaths."""
import argparse
import csv
import json
import math
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

import ezdxf
from ezdxf import bbox
from k39_proba_rzedu import evaluate as evaluate_clamp
from k38_tory import audit
from k38_zlozenie import ROOT, geometry, panel_list, preview_record, validate


def rectangle(space, layer, x, y, width, height, radius=0):
    r = radius
    if r:
        bulge = math.tan(math.pi/8)
        points = [(r,0,0),(width-r,0,bulge),(width,r,0),(width,height-r,bulge),
                  (width-r,height,0),(r,height,bulge),(0,height-r,0),(0,r,bulge)]
    else:
        points = [(0,0,0),(width,0,0),(width,height,0),(0,height,0)]
    space.add_lwpolyline([(x+u,y+v,b) for u,v,b in points], format='xyb',
                         close=True, dxfattribs={'layer':layer})


def draw(path, part):
    width, height = part['flat']
    doc = ezdxf.new('R2010')
    doc.units = 4
    for layer in ('OBRYS','OKNO','OTWOR_PRZELOT','REFERENCJA','KOSZ_REF','PCD_REF'):
        doc.layers.new(layer)
    space = doc.modelspace()
    rectangle(space,'OBRYS',0,0,width,height)
    for x,y,r in part['holes']:
        layer = 'REFERENCJA' if part['kind']=='front' else 'OTWOR_PRZELOT'
        space.add_circle((x,y),r,dxfattribs={'layer':layer})
    if part['kind']=='front':
        cx, cy, bore = part['holes'][0]
        if not math.isclose(2*bore,355.8):
            raise ValueError('Rozbieżność z kartą RSS390HF-4')
        space.add_circle((cx,cy),194.2,dxfattribs={'layer':'KOSZ_REF'})
        space.add_circle((cx,cy),184,dxfattribs={'layer':'PCD_REF'})
        for i in range(8):
            angle = math.radians(45*i)
            center = (cx+184*math.cos(angle),cy+184*math.sin(angle))
            space.add_circle(center,3.25,dxfattribs={'layer':'KOSZ_REF'})
    for x,y,u,v,r in part['windows']:
        rectangle(space,'OKNO',x,y,u-x,v-y,r)
    doc.saveas(path)
    check = ezdxf.readfile(path)
    audit = check.audit()
    if audit.errors or audit.fixes or check.units != 4:
        raise ValueError(path)
    entities = list(check.modelspace())
    if len(entities) != 1+len(part['holes'])+len(part['windows'])+10*(part['kind']=='front'):
        raise ValueError(path)
    for e in entities:
        bounds = bbox.extents([e])
        if (bounds.extmin.x < -1e-6 or bounds.extmin.y < -1e-6 or
            bounds.extmax.x > width+1e-6 or bounds.extmax.y > height+1e-6 or
            (e.dxftype()=='LWPOLYLINE' and not e.closed)):
            raise ValueError(path)
    outer = bbox.extents([entities[0]])
    if abs(outer.size.x-width)>1e-6 or abs(outer.size.y-height)>1e-6:
        raise ValueError(path)


def build(directory, data, *, measured=False, clamp_cards=()):
    scene = geometry(data, revised=True, dry=True, proposal=True)
    motion = audit(scene, robust=True)
    recorded = geometry(data, revised=data['reference_design']=='K38', dry=True, proposal=False)
    recorded_motion = audit(recorded, robust=True)
    clamps = {}
    for card in clamp_cards:
        row = card['rzad_i_konfiguracja']
        if (not measured or row not in {f'{i}/100L' for i in range(4)} or row in clamps
                or card.get('protokol_montazu_K38') != data['records']['dry_fit']):
            raise ValueError('Próba K39 wymaga zgodnej karty K38, rzędu 0/100L do 3/100L i jednego wyniku na rząd')
        clamps[row] = {'wynik': evaluate_clamp(card)['wynik_rzedu'], 'protokol': card['protokol']}
    def insertion_clear(result, name):
        return next(e['clear'] for e in result['events'] if e['object']==name and e['action']=='insert')
    supports = {}
    for name, box in scene['boxes'].items():
        supports[name] = {
            'ruch_po_korekcie': insertion_clear(motion, name),
            'ruch_stanu_wejsciowego': insertion_clear(recorded_motion, name),
            'rozrzut_podpor_z_pomiarow_mm': recorded['boxes'][name]['support_spread_mm'] if measured else None,
            'rozrzut_podpor_proponowany_mm': box['support_spread_mm'],
            'proba_rzedu_po_zamknieciu_100L': clamps.get(name[1]+'/100L')}
    clear = motion['clear']==motion['count']
    report = {'wydanie': 'CNC HOLD', 'zrodlo': 'karta fit' if measured else 'przyklad syntetyczny',
              'protokoly_K38':data['records'], 'rysunki_dopuszczone_do_przegladu':clear,
              'ruch_proponowanej_geometrii':motion, 'ruch_stanu_wejsciowego':recorded_motion,
              'podparcie_wkladow':supports}
    (directory/'KONTROLA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    if not clear:
        return False
    parts = dict(scene['parts'])
    for panel in panel_list(data):
        axis = panel['normal_axis']
        size = panel['size_xyz_mm']
        parts[panel['id']] = dict(id=panel['id'], kind='insert_panel',
            thickness=size[axis], flat=[dim for j,dim in enumerate(size) if j!=axis],
            holes=[], windows=[])
    wood = directory/'MDF_HOLD'
    wood.mkdir()
    with (directory/'wykaz_MDF.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['ID','szt','U_mm','V_mm','grubosc_gotowa_mm','status'])
        for name,p in sorted(parts.items()):
            draw(wood/(name+'.dxf'),p)
            writer.writerow([name,1,*[round(v,5) for v in p['flat']],round(p['thickness'],5),'HOLD'])
    metal = directory/'METAL_WIDOKI_HOLD'
    metal.mkdir()
    cnc = ROOT/'dokumentacja/cnc'
    for pattern in ('K36*/*.dxf','K33*/KOLNIERZ*.dxf','K32*/PLYTKA*.dxf'):
        for file in cnc.glob(pattern):
            shutil.copyfile(file,metal/file.name)
    if len(list(metal.iterdir()))!=5 or len(parts)!=90:
        raise ValueError('Błędna liczba części lub widoków')
    for file in [ROOT/'raporty/K40_pakiet_DXF.md',ROOT/'raporty/K39_proba_rzedu.md',ROOT/'raporty/K46_poprawki_po_audycie.md',
                 ROOT/'dane/k38_karta_pomiarow.json',ROOT/'dane/k39_proba_rzedu.json']:
        shutil.copy(file,directory/file.name)
    return True


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    parser.add_argument('--karta-fit',type=Path)
    parser.add_argument('--proba-k39',action='append',type=Path,default=[],
                        help='Karta próby danego rzędu w stanie 100 l, opcja powtarzalna')
    args=parser.parse_args()
    data=preview_record()
    if args.karta_fit:
        data=json.loads(args.karta_fit.read_text())
        validate(data,'fit')
    with TemporaryDirectory() as tmp:
        base=Path(tmp)
        cards=[json.loads(p.read_text()) for p in args.proba_k39]
        clear=build(base,data,measured=bool(args.karta_fit),clamp_cards=cards)
        (base/'zrodlo.json').write_text(json.dumps({'tryb':'fit' if args.karta_fit else 'przyklad nominalny','dane':data},indent=2))
        with ZipFile(args.archive,'x',ZIP_DEFLATED) as archive:
            for path in sorted(base.rglob('*')):
                if path.is_file():
                    archive.write(path,path.relative_to(base))
        if not clear:
            parser.exit(2,'Kolizje w proponowanej geometrii. ZIP zawiera diagnostykę bez rysunków DXF.\n')
