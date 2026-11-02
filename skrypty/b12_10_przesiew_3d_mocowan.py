#!/usr/bin/env python3
"""B12-10: conditional exact 3D prism/AABB collisions, insert web and bolt-stack screening.
No CAD of actual driver, tested joints, physical tolerances or CNC approval.
Run: python3 skrypty/b12_10_przesiew_3d_mocowan.py
"""
import itertools, json, math, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'; OUT.mkdir(exist_ok=True)
CUT=355.8/2; R_BOLT=368/2; R_FLANGE=388.4/2
FRONT=44.; D=425.; INNER_LEFT=22.; INNER_TOP=478.
# P39C reference: front transverse brace at x448..470, y44..54, z44..456;
# horizontal rails x448..470, z22..44 and 456..478; back brace not near pad.
OBSTACLES = [
    ('left_wall',(0,22,44,403,0,500)),
    ('bottom_wall',(22,998,44,403,0,22)),
    ('top_wall',(22,998,44,403,478,500)),
    ('front_brace',(448,470,44,54,44,456)),
    ('lower_brace_rail',(448,470,44,403,22,44)),
    ('upper_brace_rail',(448,470,44,403,456,478)),
]

def pad_footprint(cx,phase,outer,width,inner):
    a=math.radians(phase); u=(math.cos(a),math.sin(a));v=(-u[1],u[0]);
    return [(cx+r*u[0]+t*v[0],250+r*u[1]+t*v[1])
            for r,t in [(inner,-width/2),(outer,-width/2),
                        (outer,width/2),(inner,width/2)]]

def projection(poly,ax):
    vals=[x*ax[0]+z*ax[1] for x,z in poly]
    return min(vals),max(vals)

def polygon_overlap(a,b):
    """Separating axis test for convex x,z polygons; contact is not penetration."""
    for poly in (a,b):
        for i in range(len(poly)):
            x,z=poly[i];xp,zp=poly[(i+1)%len(poly)]; axis=(z-zp,xp-x)
            if axis==(0,0):continue
            amin,amax=projection(a,axis);bmin,bmax=projection(b,axis)
            if amax<=bmin+1e-8 or bmax<=amin+1e-8:return False
    return True

def prism_hits(poly,depth,bounds):
    x0,x1,y0,y1,z0,z1=bounds
    if 44+depth <= y0+1e-9 or y1<=44+1e-9:return False
    rect=[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]
    return polygon_overlap(poly,rect)

def main():
    # 2*2*3*3*3*3=324 layouts: eight pads per layout.
    envelopes=[]
    for x0,phase,inner,outer,width,depth in itertools.product(
            [231,235],[0,22.5],[178.,178.9,180.],[205,211,217],[24,36,48],[10,20,30]):
        paths=[]
        for j in range(8):
            polygon=pad_footprint(x0,phase+45*j,outer,width,inner)
            hits=[name for name,box in OBSTACLES if prism_hits(polygon,depth,box)]
            paths.append({'point':j,'hits':hits})
        envelopes.append({'x0':x0,'phase':phase,'inner':inner,'outer':outer,
             'width':width,'depth':depth,'collision_free':not any(p['hits'] for p in paths),
             'collided_points':sum(bool(p['hits']) for p in paths),
             'obstacles':sorted(set(h for p in paths for h in p['hits']))})
    # A constant cylinder is a CONTROL HYPOTHESIS, not the tapered basket's CAD.
    basket_cases=[]
    for spec in envelopes:
        for basket_r in [170.,175.,177.9,180.]:
            for insert_d in [6.,8.,10.]:
                for web in [1.,2.]:
                    radial_material=R_BOLT-insert_d/2-spec['inner']
                    clearance=spec['inner']-basket_r
                    basket_cases.append({'x0':spec['x0'],'phase':spec['phase'],
                         'inner':spec['inner'],'outer':spec['outer'],'width':spec['width'],
                         'depth':spec['depth'],'basket_radius_hypothesis':basket_r,
                         'insert_outer_d_hypothesis':insert_d,'web_threshold':web,
                         'basket_clearance_mm':round(clearance,3),
                         'inner_web_mm':round(radial_material,3),
                         'cabinet_clear':spec['collision_free'],
                         'basket_clear':clearance>=1-1e-9,
                         'web_clear':radial_material>=web-1e-9,
                         'full_screen_pass':spec['collision_free'] and clearance>=1-1e-9 and radial_material>=web-1e-9})
    # Screw length from flange TOP. Gasket, head, washers etc. not included.
    bolt_lengths=[]
    for block_depth, L, min_engage, rear_margin in itertools.product(
            [10,20,30],[60,65,70,75],[6,10,14],[3]):
        embed=L-(10.5+44.)
        bolt_lengths.append({'block_depth':block_depth,'screw_length_from_flange_top_mm':L,
                             'required_engagement_mm':min_engage,'rear_margin_mm':rear_margin,
                             'actual_engagement_mm':embed,
                             'pass':embed>=min_engage-1e-9 and embed<=block_depth-rear_margin+1e-9})
    assert all(s['inner']<=184<=s['outer'] for s in envelopes)
    assert len(envelopes)==324 and len(basket_cases)==324*4*3*2 and len(bolt_lengths)==36
    summary={'footprint_cases':len(envelopes),
             'footprint_clear':sum(z['collision_free'] for z in envelopes),
             'footprint_clear_by_x':{str(x):sum(z['collision_free'] for z in envelopes if z['x0']==x) for x in [231,235]},
             'footprint_clear_by_outer':{str(r):sum(z['collision_free'] for z in envelopes if z['outer']==r) for r in [205,211,217]},
             'basket_insert_cases':len(basket_cases),
             'basket_insert_pass':sum(z['full_screen_pass'] for z in basket_cases),
             'by_insert_web':{f'd{d:g}_web{w:g}':sum(z['full_screen_pass'] for z in basket_cases if z['insert_outer_d_hypothesis']==d and z['web_threshold']==w) for d in [6.,8.,10.] for w in [1.,2.]},
             'by_basket_radius':{str(r):sum(z['full_screen_pass'] for z in basket_cases if z['basket_radius_hypothesis']==r) for r in [170.,175.,177.9,180.]},
             'screw_stacks':len(bolt_lengths),
             'stack_pass':sum(z['pass'] for z in bolt_lengths),
             'by_depth_screw':{str(d):sorted(set(z['screw_length_from_flange_top_mm'] for z in bolt_lengths if z['block_depth']==d and z['pass'])) for d in [10,20,30]},
             'sample_insert_inner_web':{str(d):round(184-d/2-178.9,3) for d in [6,8,10]},
             'outer_flange_max_radial_head_radius_mm':round(R_FLANGE-R_BOLT,3),
             'bolt_axis_to_cutout_mm':round(R_BOLT-CUT,3)}
    result={'study':'B12-10','units':'mm',
            'model':'3D polygon prisms vs P39C simplified solids; CIRCULAR basket envelope proxy; hypothetical bolt stack',
            'date':'2026-11-02',
            'provenance':{'B12-09_head_sha':'538b2b1cbdd26fdfb32ae9def516d64765bb3b09',
                 'official_dimensions':'https://www.parts-express.com/pedocs/specs/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf',
                 'brace_surrogate':'dokumentacja/P39C_front_korpus_pierscien_REFERENCYJNY_NIE_CNC.scad'},
            'summary':summary,'envelopes':envelopes,'basket_insert_cases':basket_cases,'bolt_stacks':bolt_lengths,
            'limitations':['No measured profile r(y) of Dayton basket at block depths; basket cylinder values are what-if bounds.',
                 'Collisions against P39C simplified braces, not physical cabinet.',
                 'Phases 0/22.5 degrees assumed relative to cabinet; terminal clocking unverified.',
                 'Insert d is FULL OUTER diameter, not screw or flange hole diameter.',
                 'Web 1/2mm is a SCREENING threshold, not structural acceptance.',
                 'Axial screw stack ignores head/gasket/washer/tolerance/preload.',
                 'No measured contact, adhesive, joints, hand/driver swept volume, vent flow or CNC approval.']}
    dest=OUT/'b12_10_przesiew_3d.json'
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    (OUT/'b12_10_manifest.json').write_text(json.dumps({
        'summary':summary,'full_json_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
        'source':'skrypty/b12_10_przesiew_3d_mocowan.py',
        'full_json':'wyniki/b12_10_przesiew_3d.json'},indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
