#!/usr/bin/env python3
"""One measurement record for the shell, guides and eight assembled inserts (mm)."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from k31_zlacze_i_pasowania import FACES, fit_panels
from k35_korpus_z_pomiarow import KEYS
from k36_bank_z_pomiarow import build
from k37_material_i_operacje import NOM
from k38_tory import FIXED_FACE, POSE, SIZE, SEP_FINISH, audit

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / 'dane/k30_zalozenia.json').read_text())
ROWS = SPEC['row_base_z_mm']
IDS = tuple(f'M{row}{side}' for row in range(4) for side in 'FN')
BANK_OPS = json.loads((ROOT / 'wyniki/k37_material_i_operacje.json').read_text())['operations']
OP_IDS = tuple(op['part'] for op in BANK_OPS)
TEMPLATE = ROOT / 'dane/k38_karta_pomiarow.json'
TARGET = {row: (round(volume * 1e6 / (260 * height), 1), 260., float(height))
          for row, (volume, height) in enumerate(zip(SPEC['box_volume_l'], SPEC['row_box_height_mm']))}
# Per-face error budgets AFTER propagating stock dimensions (not supplier capabilities).
SIDE_RESERVE = .10     # proposed free clearance at each separator face
NEW_JOINT = .35        # trial target; adhesive acceptance remains open


def template():
    return {
        'schema': 'SUB-K38-1', 'units': 'mm', 'reference_design': 'K37',
        'records': {'stock': None, 'dry_fit': None},
        'shell_mm': dict.fromkeys(KEYS),
        'guide_mm': dict.fromkeys(NOM),
        'insert_panels_mm': {name: dict.fromkeys(FACES) for name in IDS},
        'dry_fit': {
            'insert_xyz_mm': {name: dict.fromkeys('XYZ') for name in IDS},
            'insert_left_x_mm': dict.fromkeys(IDS),
            'finished_thickness_mm': dict.fromkeys(OP_IDS),
            'support_top_z_mm': dict.fromkeys(support_targets())
        }
    }


def support_targets():
    heights = {f'RAIL_{segment}_{row}_{face}': float(z) for row,z in enumerate(ROWS)
               for segment in ('A','B') for face in ('F','R')}
    heights.update({f'MID_SILL_{row}': float(z) for row,z in enumerate(ROWS)})
    return heights


def x_target(name):
    length = TARGET[int(name[1])][0]
    return 474. if name.endswith('N') else 474. + length + 8.


def target_thicknesses(shell, gap):
    return {name: bank_op_target(name, shell, gap) for name in OP_IDS}


def bank_op_target(name, shell, gap):
    if name.startswith('RAIL_'):
        return ROWS[0] - shell['BOTTOM'] - gap
    if name.startswith('TOP_KEEPER_'):
        return 500. - shell['TOP'] - gap - 466.
    if name.startswith('BACKSTOP_'):
        return 1080. - shell['SIDE_R'] - gap - 1018.
    return 7.8  # initial K37 separator, before the pair-specific measurement


def preview_record(shell=None, guides=None):
    data = template()
    data['shell_mm'] = dict.fromkeys(KEYS, 22.) if shell is None else dict(shell)
    data['guide_mm'] = dict(NOM) if guides is None else dict(guides)
    dry = data['dry_fit']
    for name in IDS:
        data['insert_panels_mm'][name] = dict.fromkeys(FACES, 8.)
        dry['insert_xyz_mm'][name] = dict(zip('XYZ', TARGET[int(name[1])]))
        dry['insert_left_x_mm'][name] = x_target(name)
    dry['support_top_z_mm'] = support_targets()
    dry['finished_thickness_mm'] = target_thicknesses(data['shell_mm'], .2)
    return data


def validate(data, mode):
    """Reject incomplete real records before writing files. No nominal substitutions."""
    if not isinstance(data,dict) or data.get('schema') != 'SUB-K38-1' or data.get('units') != 'mm':
        raise ValueError('Wymagane schema SUB-K38-1 i jednostki mm.')
    errors = []

    def check_keys(group, keys, path):
        if not isinstance(group, dict) or set(group) != set(keys):
            errors.append(f'{path}: wymagane dokładnie {", ".join(keys)}')
            return False
        return True

    def bounded(group, limits, path):
        if check_keys(group, limits, path):
            for key, (low, high) in limits.items():
                value = group[key]
                if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
                    errors.append(f'{path}.{key}: pomiar w zakresie {low:g}..{high:g} mm')

    if not check_keys(data, template(), 'plik'):
        raise ValueError('; '.join(errors))
    if data['reference_design'] not in ('K37','K38'):
        errors.append('reference_design: K37 lub K38')
    records = data['records']
    if check_keys(records, ('stock','dry_fit'), 'records'):
        for phase in (('stock',) if mode == 'stock' else ('stock','dry_fit')):
            if not isinstance(records[phase], str) or not records[phase].strip():
                errors.append('records.' + phase)
    bounded(data['shell_mm'], {key:(21.5,22.5) for key in KEYS}, 'shell_mm')
    guide_ranges = {key:(v-(.2 if key.startswith('P') else .5),
                         v+(.2 if key.startswith('P') else .5)) for key,v in NOM.items()}
    bounded(data['guide_mm'], guide_ranges, 'guide_mm')
    if check_keys(data['insert_panels_mm'], IDS, 'insert_panels_mm'):
        for name in IDS:
            bounded(data['insert_panels_mm'][name], {k:(7.5,8.5) for k in FACES}, name)
    if mode == 'fit':
        dry = data['dry_fit']
        if check_keys(dry, template()['dry_fit'], 'dry_fit'):
            bounded(dry['insert_left_x_mm'], {n:(x_target(n)-2, x_target(n)+2) for n in IDS}, 'insert_left_x_mm')
            if check_keys(dry['insert_xyz_mm'], IDS, 'insert_xyz_mm'):
                for name in IDS:
                    bounded(dry['insert_xyz_mm'][name],
                            {k:(v-2,v+2) for k,v in zip('XYZ', TARGET[int(name[1])])}, name+'.xyz')
            bounded(dry['support_top_z_mm'], {key:(v-2,v+2) for key,v in support_targets().items()}, 'support_top_z_mm')
            # Study domain, not acceptance limits. Out-of-tolerance parts are analysed inside it.
            bounded(dry['finished_thickness_mm'],
                    {op['part']:(op['finished_range_mm'][0]-2, op['finished_range_mm'][1]+2)
                     for op in BANK_OPS}, 'finished_thickness_mm')
    if errors:
        raise ValueError('Brak lub błędna wartość: ' + '; '.join(errors))


def separator_target(gap):
    # Near face can advance by pose + finished-size error. Half-thickness
    # variation and centring error act separately on the moving separator.
    half_budget = (POSE + SIZE) + POSE + SEP_FINISH/2 + SIDE_RESERVE
    thickness = math.floor((gap - 2*half_budget)*10 + 1e-9)/10
    if thickness <= 0:
        raise ValueError('Zbyt mało miejsca na przekładkę w badanym układzie.')
    return thickness


def panel_list(data):
    panels = []
    for name in IDS:
        parts = fit_panels(*TARGET[int(name[1])], data['insert_panels_mm'][name], .2)
        for part in parts:
            panels.append({'id': name+'_'+part['id'], 'local_origin_mm': part['o'],
                           'size_xyz_mm': part['s'], 'normal_axis': part['axis']})
    return panels


def geometry(data, revised=False, dry=True, proposal=False):
    """Use dry measurements as-is; a proposed recut gets its own separate scene."""
    gap = NEW_JOINT if revised else .2
    shell, guides = data['shell_mm'], data['guide_mm']
    assembly = build(shell, gap)
    finish = target_thicknesses(shell, gap)
    boxes = {}
    for name in IDS:
        length, width, height = TARGET[int(name[1])]
        left = x_target(name)
        if dry:
            dimensions = data['dry_fit']['insert_xyz_mm'][name]
            length,width,height = (dimensions[axis] for axis in 'XYZ')
            left = data['dry_fit']['insert_left_x_mm'][name]
        boxes[name] = {'id':name, 'o':[left,70.,ROWS[int(name[1])]], 's':[length,width,height]}
    if dry and not proposal:
        finish = dict(data['dry_fit']['finished_thickness_mm'])
    openings = {}
    for row in range(4):
        near, far = boxes[f'M{row}N'], boxes[f'M{row}F']
        left = near['o'][0]+near['s'][0]
        right = far['o'][0]
        openings[row] = (left,right)
        if revised and (proposal or not dry):
            finish[f'SEP_{row}'] = separator_target(right-left)

    for plate in assembly['plates']:
        plate['s'][0] = guides[plate['id']]
    max_plate = max(p['s'][0] for p in assembly['plates'])
    parts = {}
    for p in assembly['parts']:
        name = p['id']
        if p['kind'] in ('insert_panel','stop'):
            continue  # box cutlist and K36 metal assemblies are separate
        o,s = p['o'],p['s']
        if name.startswith('CHANNEL_WEB_'):
            s[1] = guides[name]
            o[1] = 68.-s[1] if name.endswith('_F') else 332.
            if '_A_' in name:
                end = o[0]+s[0]
                o[0] = max(474.,448.+shell['PORTAL']+max_plate+gap)
                s[0] = end-o[0]
        elif name.startswith(('RAIL_','TOP_KEEPER_')):
            o[1] = 68.+gap if name.endswith('_F') else 282.-gap
            if name.startswith('TOP_KEEPER_'):
                s[2] = finish[name]
                o[2] = 500.-shell['TOP']-gap-s[2]
            elif '_0_' in name:
                s[2] = finish[name]
            else:
                support_top = o[2]+s[2]
                s[2] = guides[name]
                o[2] = support_top-s[2]
        elif name.startswith('BACKSTOP_') and name != 'BACKSTOP_SMALL_EXTRA':
            s[0] = finish[name]
            o[0] = 1080.-shell['SIDE_R']-gap-s[0]
        elif name.startswith('SEP_'):
            left,right = openings[int(name[-1])]
            s[0] = finish[name]
            o[0] = (left+right-s[0])/2
        if dry and not proposal:
            measured_tops = data['dry_fit']['support_top_z_mm']
            if name.startswith('RAIL_'):
                o[2] = measured_tops[name]-s[2]
            if name=='MID_PORTAL':
                p['windows'] = [[u, measured_tops[f'MID_SILL_{row}']-o[2], U,V,r]
                                for row,(u,v,U,V,r) in enumerate(p['windows'])]
        p['thickness'] = s[p['axis']]
        p['flat'] = [s[j] for j in p['uv']]
        parts[name] = p
    spacer = parts['BACKSTOP_SMALL_EXTRA']
    spacer['s'][0] = spacer['thickness'] = guides[spacer['id']]
    spacer['o'][0] = parts['BACKSTOP_3']['o'][0]-spacer['thickness']
    for row in range(4):
        # Height of the highest shelf in this channel sets the traverse above it.
        supports = [p for name,p in parts.items() if name.startswith('RAIL_') and name.split('_')[2]==str(row)]
        mid = parts['MID_PORTAL']
        sill = mid['o'][2]+mid['windows'][row][1]
        for body in (boxes[f'M{row}N'],boxes[f'M{row}F'],parts[f'SEP_{row}']):
            left = body['o'][0]
            right = left+body['s'][0]
            tops = [p['o'][2]+p['s'][2] for p in supports
                    if min(p['o'][0]+p['s'][0],right)>max(p['o'][0],left)]
            if min(mid['o'][0]+mid['s'][0],right)>max(mid['o'][0],left):
                tops.append(sill)
            if not tops:
                raise ValueError('Brak podparcia dla '+body['id'])
            body['o'][2] = max(tops)
            body['support_spread_mm'] = max(tops)-min(tops)
            body['travel_z_mm'] = max([sill]+[p['o'][2]+p['s'][2] for p in supports])+.6
    return {'parts':parts, 'boxes':boxes, 'plates':assembly['plates'], 'gap':gap,
            'finish':finish, 'openings':openings}


def contact_budget(scene):
    rows=[]
    for row,(left,right) in scene['openings'].items():
        near,far = scene['boxes'][f'M{row}N'], scene['boxes'][f'M{row}F']
        sep = scene['parts'][f'SEP_{row}']['s'][0]
        stop = scene['parts']['BACKSTOP_SMALL_EXTRA' if row==3 else f'BACKSTOP_{row}']['o'][0]
        each = (right-left-sep)/2
        # Independent errors on two steel/wood contact faces, two box lengths and separator.
        hard_gap=stop-470.-near['s'][0]-sep-far['s'][0]
        hard_error=2*FIXED_FACE+2*SIZE+SEP_FINISH
        rows.append({'row':row,'between_reference_faces_mm':right-left,'separator_mm':sep,
            'near_gap_lower_mm':each-(POSE+SIZE)-POSE-SEP_FINISH/2,
            'far_gap_lower_mm':each-POSE-POSE-SEP_FINISH/2,
            'total_lower_with_centre_free_mm':right-left-sep-2*POSE-SIZE-SEP_FINISH,
            'hard_stack_gap_locked_mm':hard_gap,
            'hard_stack_gap_interval_mm':[hard_gap-hard_error,hard_gap+hard_error],
            'support_spread_mm':{x['id']:x['support_spread_mm'] for x in (near,far)},
            'support_spread_upper_mm':max(x['support_spread_mm'] for x in (near,far))+2*FIXED_FACE,
            'extended_hard_stack_gap_mm':stop-747.1-far['s'][0] if row==1 else None})
    g=scene['gap']
    return {'end_bond_mm':[g-FIXED_FACE,g+FIXED_FACE], 'rows':rows}


def family_audit():
    # The measured shell fixes all aperture Y/Z coordinates. Shell stock has nine
    # independent endpoints. Each guide face depends monotonically on its own
    # thickness, or on max(plate thicknesses). Per-coordinate unions therefore
    # cover the mixed guide extrema as well; they can overestimate collisions.
    from itertools import product
    from k38_tory import bounds
    reference=geometry(preview_record(),revised=True,proposal=True)
    endpoints={}
    count=0
    def eligible(scene):
        return [p for p in scene['parts'].values() if p['kind'] in ('fixed','front')]+scene['plates']
    for sizes in product((21.5,22.5),repeat=len(KEYS)):
        shell=dict(zip(KEYS,sizes))
        for sign in (-1,1):
            bank={key:value+sign*(.2 if key.startswith('P') else .5) for key,value in NOM.items()}
            scene=geometry(preview_record(shell,bank),revised=True,proposal=True)
            count+=1
            for part in eligible(scene):
                name=part['id']
                low,high=bounds(part)
                if name not in endpoints:
                    endpoints[name]=[list(low),list(high)]
                else:
                    limits=endpoints[name]
                    for j in range(3):
                        limits[0][j]=min(limits[0][j],low[j])
                        limits[1][j]=max(limits[1][j],high[j])
    for part in eligible(reference):
        low,high=endpoints[part['id']]
        if part.get('windows'):
            # Maintain global hole coordinates when enlarging the outside rectangle.
            dy,dz=part['o'][1]-low[1],part['o'][2]-low[2]
            part['windows']=[[u+dy,v+dz,U+dy,V+dz,r] for u,v,U,V,r in part['windows']]
        part['o']=low
        part['s']=[b-a for a,b in zip(low,high)]
    return {'stock_endpoint_scenes':count,'policy':'K38_trial',
            'fixed_part_envelopes':len(endpoints),'motions':audit(reference,robust=True),
            'scope':'reference locations and finished box sizes, face error budgets plus admissible raw stock'}


def write_atomic(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    with NamedTemporaryFile('w',dir=path.parent,delete=False,encoding='utf-8') as temp:
        tmp=Path(temp.name)
        try:
            json.dump(content,temp,indent=2,ensure_ascii=False,allow_nan=False)
            temp.write('\n')
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp,path)
    finally:
        tmp.unlink(missing_ok=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('preview','stock','fit'),required=True)
    parser.add_argument('--input',type=Path)
    parser.add_argument('--family',action='store_true',help='Zakres grubości surowych płyt w syntetycznej próbie preview')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.family and args.mode!='preview':
        parser.error('--family dotyczy wyłącznie syntetycznych zakresów partii.')
    if args.mode=='preview':
        if args.input:
            parser.error('Tryb preview generuje jawnie syntetyczny przykład. Do własnych danych użyj stock lub fit.')
        data=preview_record()
    else:
        if not args.input:
            parser.error('Wskaż --input z kartą pomiarów.')
        if args.input.resolve()==args.output.resolve():
            parser.error('Plik wyniku musi mieć inną nazwę niż karta pomiarów.')
        data=json.loads(args.input.read_text())
        try:
            validate(data,args.mode)
        except ValueError as err:
            parser.error(str(err))
    if args.output.resolve()==TEMPLATE.resolve():
        parser.error('Szablon wejściowy jest chroniony.')
    result={'schema':'K38-results-1','units':'mm','release':'CNC_HOLD','mode':args.mode,
            'records':data['records'], 'panels':panel_list(data),
            'inputs_sha256':hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()}
    for key,revised in [('as_recorded',data['reference_design']=='K38'),('K38_trial',True)]:
        measured_finish=args.mode!='stock'
        proposal=key=='K38_trial'
        scene=geometry(data,revised,measured_finish,proposal)
        block={'joint_target_mm':scene['gap'], 'operation_dimensions_mm':scene['finish'],
               'panel_blank_dimensions_xyz_mm':{n:p['s'] for n,p in scene['parts'].items()
                                                  if p['kind'] in ('front','fixed','separator')},
               'stock_values_supplied':args.mode!='preview',
               'finished_sizes_source':('design' if proposal or not measured_finish else 'dry_fit')}
        if measured_finish:
            block['contact']=contact_budget(scene)
            block['motions']=audit(scene,robust=True)
            block['nominal_motions']=audit(scene,robust=False)
        result[key]=block
    if args.family:
        result['stock_family']=family_audit()
    write_atomic(args.output,result)
    print(f'{args.mode}: {len(result["panels"])} paneli, {args.output}; CNC HOLD')

if __name__=='__main__':
    main()
