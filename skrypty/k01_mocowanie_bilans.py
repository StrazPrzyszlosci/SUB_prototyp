#!/usr/bin/env python3
"""K01: reproducible cabinet-and-local-mount construction envelope screen.
Coordinates and solids follow P39C, not the unmeasured Dayton basket CAD.
Do NOT interpret positive SAT clearance as physical assembly or CNC approval.
Python 3 standard library only, run from repository root.
"""
import json, math, itertools, hashlib
from pathlib import Path
W,D,H=1020,425,500
FRONT=44
CUT_R,BOLT_R,FLANGE_R=177.9,184.,194.2
# x0,x1,y0,y1,z0,z1: P39C surrogate geometry, not final cabinetry.
OBSTACLES={
 'left':(0,22,44,403,0,500),
 'right':(998,1020,44,403,0,500),
 'bottom':(22,998,44,403,0,22),
 'top':(22,998,44,403,478,500),
 'brace1_web':(448,470,44,54,44,456),
 'brace1_bottom':(448,470,44,403,22,44),
 'brace1_top':(448,470,44,403,456,478),
 'brace2_web':(723,745,44,54,44,456)
}

def polygon(cx,angle,ri,ro,width):
 a=math.radians(angle);u=(math.cos(a),math.sin(a));v=(-u[1],u[0])
 return [(cx+r*u[0]+t*v[0],250+r*u[1]+t*v[1])
         for r,t in [(ri,-width/2),(ro,-width/2),(ro,width/2),(ri,width/2)]]

def overlap(a,b):
 for poly in [a,b]:
  for i,(x,z) in enumerate(poly):
   xx,zz=poly[(i+1)%len(poly)];ax=(z-zz,xx-x)
   aa=[p[0]*ax[0]+p[1]*ax[1] for p in a]
   bb=[p[0]*ax[0]+p[1]*ax[1] for p in b]
   if max(aa)<=min(bb)+1e-10 or max(bb)<=min(aa)+1e-10:return False
 return True

def collides(p,depth,rect,clearance):
 x0,x1,y0,y1,z0,z1=rect
 if FRONT+depth<=y0+1e-10 or FRONT>=y1-1e-10:return False
 b=[(x0-clearance,z0-clearance),(x1+clearance,z0-clearance),
    (x1+clearance,z1+clearance),(x0-clearance,z1+clearance)]
 return overlap(p,b)

def evaluate(cx,ri,ro,width,depth,margin):
 pads=[polygon(cx,i*45,ri,ro,width) for i in range(8)]
 hit=sorted(name for name,solid in OBSTACLES.items()
            if any(collides(p,depth,solid,margin) for p in pads))
 return {'cx_mm':cx,'radial_inner_mm':ri,'radial_outer_mm':ro,
         'tangential_width_mm':width,'block_depth_mm':depth,
         'assumed_obstacle_clearance_mm':margin,
         'pass_surrogate':not hit,'intersections':hit,
         'hole_footprint_clearance_mm':round(ri-CUT_R,2),
         'left_wall_clearance_mm':round(min(x for p in pads for x,z in p)-22,3),
         'block_total_displacement_L':round(8*(ro-ri)*width*depth/1e6,6)}

def run():
 cases=[evaluate(*v) for v in itertools.product(
        [231,235],[178.9,180.0],[200,203,205,207,211],
        [24,36,48],[20,30],[0,2,4,6])]
 assert len(cases)==480
 pass_by_margin={str(m):sum(c['pass_surrogate'] for c in cases
                   if c['assumed_obstacle_clearance_mm']==m) for m in [0,2,4,6]}
 assert pass_by_margin=={'0':108,'2':108,'4':84,'6':72}
 witness=evaluate(231,178.9,205,36,30,2)
 assert witness['pass_surrogate'] and witness['left_wall_clearance_mm']==4.0
 assert witness['hole_footprint_clearance_mm']==1.0
 assert witness['block_total_displacement_L']==0.225504
 # No pad vertex may project into the manufacturer's circular front opening.
 assert all(math.hypot(x-231,z-250)>=CUT_R-1e-9
            for i in range(8) for x,z in polygon(231,i*45,178.9,205,36))
 inserts=[{'insert_external_d_mm':d,
           'web_inner_mm':round(BOLT_R-d/2-178.9,2),
           'web_min_2mm_hypothesis':BOLT_R-d/2-178.9>=2-1e-10}
           for d in [6,8,10]]
 # Generic depth budget; grille and terminals remain UNMEASURED projections.
 depth=[{'grille_projection_mm':g,'terminal_projection_mm':t,
         'unallocated_mm':extra,'total_mm':D+g+t+extra,
         'positive_margin_mm':500-D-g-t-extra}
         for g,t,extra in itertools.product([25,36,45,55],
                                            [10,20,30,40],[0,5,10])]
 assert len(depth)==48
 nominal=next(v for v in depth if v['grille_projection_mm']==36 and
              v['terminal_projection_mm']==20 and v['unallocated_mm']==0)
 assert nominal['total_mm']==481 and nominal['positive_margin_mm']==19
 ring=math.pi/4*(400**2-356**2)*4/1e6
 summary={
  'geometry_cases':480,'pass_by_margin_mm':pass_by_margin,
  'pass_by_ro_with_margin_2mm':{str(ro):sum(c['pass_surrogate'] for c in cases
    if c['radial_outer_mm']==ro and c['assumed_obstacle_clearance_mm']==2)
    for ro in [200,203,205,207,211]},
  'pass_cx_231_2mm':sum(c['pass_surrogate'] for c in cases
    if c['cx_mm']==231 and c['assumed_obstacle_clearance_mm']==2),
  'pass_cx_235_2mm':sum(c['pass_surrogate'] for c in cases
    if c['cx_mm']==235 and c['assumed_obstacle_clearance_mm']==2),
  'conditional_geometry_witness':witness,'insert_outer_d_hypotheses':inserts,
  'P30E_reference_net_L':[100.12,119.92,150.16],
  'volume_of_8_new_blocks_L':witness['block_total_displacement_L'],
  'only_if_not_previously_counted_net_L':[
     round(v-witness['block_total_displacement_L'],4)
     for v in [100.12,119.92,150.16]],
  'P39C_hypothetical_ring_displacement_L':round(ring,6),
  'delta_8_blocks_instead_of_P39C_ring_L':round(
    witness['block_total_displacement_L']-ring,6),
  'depth_cases':48,'positive_margin_cases':sum(v['positive_margin_mm']>0 for v in depth),
  'depth_reference':nominal,'rigorous_status':'SURROGATE envelope ONLY, NOT CNC',
  'warnings':['Real rib and terminal silhouette unmeasured',
  'P30E and P39C are different research representations: no automatic double-counting',
  'No real screw/insert, adhesive and MDF strength or pilot-hole geometry',
  'The nominal 2mm obstacle margin is NOT a production tolerance',
  'The front insertion path of 20 modules with new pads and tools is not yet validated',
  'Tool access, bolt head size, cabinet joint and seal remain unverified']}
 out=Path('wyniki');out.mkdir(exist_ok=True)
 data={'study':'K01','source':'P39C and P30E surrogate cabinet, Dayton mounting dimensions',
       'summary':summary,'configurations':cases,'depth_budget_scenarios':depth}
 full=out/'k01_pelne_scenariusze.json'
 full.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (out/'k01_manifest_odtworzony.json').write_text(json.dumps({
    'summary':summary,'full_sha256':hashlib.sha256(full.read_bytes()).hexdigest(),
    'generated_by':'skrypty/k01_mocowanie_bilans.py'},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':run()
