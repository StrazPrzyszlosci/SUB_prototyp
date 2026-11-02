#!/usr/bin/env python3
"""B12-09: reproducible, deliberately conditional 2D mounting and load screen.
Uses Python 3 stdlib only. Does not evaluate the strength of MDF/adhesive.
Run: python3 skrypty/b12_09_lokalne_mocowania.py
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'wyniki'
OUT.mkdir(parents=True, exist_ok=True)
CUT_R = 355.8 / 2
BOLT_R = 368 / 2
FLANGE_R = 388.4 / 2
G = 9.80665
MASS = 15.0  # hypothesis, not actual weighed product
ECC = 120.0  # mm, hypothetical center-of-mass lever arm
INNER = CUT_R + 1.0  # scenario: 1 mm projected clearance


def solve3(a, rhs):
    """3x3 Gaussian elimination with partial pivoting, no external deps."""
    t = [list(map(float, row)) + [float(b)] for row, b in zip(a, rhs)]
    for k in range(3):
        i = max(range(k, 3), key=lambda j: abs(t[j][k]))
        t[k], t[i] = t[i], t[k]
        if abs(t[k][k]) < 1e-8:
            raise ValueError('rank-deficient bolt group')
        for j in range(k + 1, 3):
            factor = t[j][k] / t[k][k]
            for l in range(k, 4):
                t[j][l] -= factor * t[k][l]
    x = [0.0] * 3
    for k in range(2, -1, -1):
        x[k] = (t[k][3] - sum(t[k][j] * x[j] for j in range(k + 1, 3))) / t[k][k]
    return x


def bolt_forces(accel_g, phase_deg, lost=None, direction='x'):
    """Rigid bolt group; least-squares normal bolt loads plus uniform shear.
    The direction of the signed normal is a convention: only magnitudes
    and tensile-side proxies are reported. Stiffness/contact is not solved.
    """
    pos = [(BOLT_R * math.cos(math.radians(phase_deg + i*45)),
            BOLT_R * math.sin(math.radians(phase_deg + i*45))) for i in range(8) if i != lost]
    n = len(pos)
    F = MASS * G * accel_g
    mx = F*ECC if direction == 'x' else 0.0
    mz = F*ECC if direction == 'z' else 0.0
    mat = [[n, sum(x for x,z in pos), sum(z for x,z in pos)],
           [sum(x for x,z in pos), sum(x*x for x,z in pos), sum(x*z for x,z in pos)],
           [sum(z for x,z in pos), sum(x*z for x,z in pos), sum(z*z for x,z in pos)]]
    a,b,c=solve3(mat,[0,mx,mz])
    normal=[a+b*x+c*z for x,z in pos]
    shear=F/n
    assert abs(sum(normal)) < 1e-6
    assert abs(sum(normal[i]*pos[i][0] for i in range(n))-mx)<1e-5
    assert abs(sum(normal[i]*pos[i][1] for i in range(n))-mz)<1e-5
    return {'normal_peak_N': max(max(normal),0), 'normal_abs_peak_N':max(map(abs,normal)),
            'shear_per_active_N':shear,
            'resultant_peak_N':max(math.hypot(q,shear) for q in normal), 'active':n}


def block_projection(x0, phase, outer, width, err):
    all_xy=[]
    for i in range(8):
        theta=math.radians(phase+i*45)
        u=(math.cos(theta),math.sin(theta))
        v=(-math.sin(theta),math.cos(theta))
        for rad in [INNER,outer]:
            for t in [-width/2,width/2]:
                all_xy.append((x0+rad*u[0]+t*v[0], 250+rad*u[1]+t*v[1]))
    # x=448 is only a projection of brace, not established 3D obstruction.
    edge={'left':min(x for x,z in all_xy)-22-err,
          'brace':448-max(x for x,z in all_xy)-err,
          'bottom':min(z for x,z in all_xy)-22-err,
          'top':478-max(z for x,z in all_xy)-err}
    return {'margins_mm':{k:round(v,3) for k,v in edge.items()},
            'min_margin_mm':round(min(edge.values()),3),
            'projection_screen_pass':min(edge.values()) >= 2-1e-9}


def main():
    drill_cases=[]
    for diameter in [4.0,4.5,5.0,5.5,6.5,8.0,10.0,12.0]:
        for offset in [0,0.5,1.0,2.0]:
            g=BOLT_R-CUT_R-diameter/2-offset
            drill_cases.append({'hypothetical_wood_or_insert_d_mm':diameter,
                 'relative_center_error_mm':offset,'radial_web_mm':round(g,3),
                 'screen_1mm_pass':g>=1-1e-9})
    geometry=[]
    for x0 in [231,235]:
        for phase in [0,22.5]:
            for outer in [205,211,217]:
                for width in [24,36,48]:
                    for err in [0,1,2]:
                        s=block_projection(x0,phase,outer,width,err)
                        geometry.append({'x_axis_mm':x0,'phase_deg':phase,'r_out_mm':outer,
                           'tangent_width_mm':width,'projection_error_mm':err,**s})
    loads=[]
    for g in [1,3,5,10]:
        for phase in [0,22.5]:
            for direction in ['x','z']:
                for lost in [None,*range(8)]:
                    loads.append({'accel_g':g,'phase_deg':phase,'direction':direction,
                         'lost_bolt':lost,**bolt_forces(g,phase,lost,direction)})
    bond_area=(205-INNER)*36-math.pi*8**2/4
    ref=bolt_forces(5,0,None,'x')
    peel=[]
    for h in [0,10,20]:
        for amplification in [1,3]:
            moment=ref['shear_per_active_N']*h
            sigma_edge=6*moment/(36*(205-INNER)**2)
            tensile=ref['normal_peak_N']/bond_area + sigma_edge
            peel.append({'shear_offset_mm':h,'comparison_multiplier':amplification,
                'mean_shear_required_MPa':round(amplification*ref['shear_per_active_N']/bond_area,4),
                'peak_tensile_proxy_MPa':round(amplification*tensile,4)})
    assert len(drill_cases)==32 and len(geometry)==108 and len(loads)==144
    assert abs(ref['normal_peak_N']-(MASS*G*5*ECC/(4*BOLT_R)))<1e-8
    assert abs(ref['shear_per_active_N']-MASS*G*5/8)<1e-9
    assert any(q['projection_screen_pass'] for q in geometry if q['r_out_mm']==205)
    sums={'geometry_cases':len(geometry),
          'projection_pass':sum(q['projection_screen_pass'] for q in geometry),
          'by_outer':{str(r):{'pass':sum(q['projection_screen_pass'] for q in geometry if q['r_out_mm']==r),
                               'total':sum(q['r_out_mm']==r for q in geometry)}
                       for r in [205,211,217]},
          'load_cases':len(loads),'drill_cases':len(drill_cases),
          'all_8_5g':ref,
          'worst_7_5g':max([r for r in loads if r['accel_g']==5 and r['lost_bolt'] is not None],
                            key=lambda r:r['resultant_peak_N']),
          'sample_bond_area_mm2':round(bond_area,3),
          'sample_bond':peel,
          'sample_projection':block_projection(231,0,205,36,2)}
    data={'id':'B12-09','date':'2026-11-02',
        'source':'SUB_prototyp main @ 72e0b6593f224ff148375675ea9982446ccb6487',
        'units':{'length':'mm','force':'N','stress':'N/mm2 (MPa)'},
        'inputs':{'cutout_d_mm':355.8,'bolt_pitch_d_mm':368,'flange_d_mm':388.4,
                  'basket_flange_hole_d_mm':6.5,'mass_scenario_kg':MASS,
                  'eccentricity_scenario_mm':ECC,'x_axis_mm':[231,235],
                  'z_axis_mm':250,'front_inner_left_mm':22,
                  'first_brace_projection_x_mm':448,
                  'inner_block_r_mm':INNER,'r_out_mm':[205,211,217],
                  'block_tangent_width_mm':[24,36,48]},
        'screening_thresholds_NOT_acceptance':{'projected_obstacle_clearance_mm':2,
                   'block_cutout_clearance_mm':1,'diameter_web_mm':1,
                   'relative_axis_error_mm':[0,0.5,1,2],
                   'stress_comparison_multiplier':[1,3]},
        'summary':sums,'drill_cases':drill_cases,
        'geometry_cases':geometry,'load_cases':loads,
        'limitations':['Only 2D: brace at x448 is projected, not a solid verified at block depth',
          'Unknown backside basket ribs, terminals, fastener and tool path',
          'Bond area subtracts a circular hole but assumes bonded contact elsewhere',
          'Peak tensile proxy uses an ideal elastic rectangular bond; no real peel law',
          'All fasteners assumed identically stiff; failed fastener is least-norm equilibrium',
          'No measured MDF/adhesive/insert thread/preload/fatigue/humidity/failure stress',
          '5g, 10g and x3 are scenarios, not design codes or safety factors',
          'No CNC/bolt specification permitted from these figures']}
    out=OUT/'b12_09_wyniki.json'
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    colors={'good':'#136f63','fail':'#b04437','ink':'#19232d'}
    rect=[]
    def t(x,y,value,size=13):
        return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" fill="{colors["ink"]}">{value}</text>'
    rect.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 390" role="img" aria-label="B12-09 geometry and loading proxies; not CNC">')
    rect.append('<rect width="880" height="390" fill="#fff"/>')
    rect.append(t(22,30,'B12-09 | Mocowanie lokalne — badania scenariuszowe, NIE CNC',19))
    rect.append(t(22,65,'Promieniowy pas MDF przy osi śruby (bez tolerancji), mm',14))
    for i,d in enumerate([4,4.5,5,5.5,6.5,8,10,12]):
        margin=BOLT_R-CUT_R-d/2
        y=93+i*33
        rect.append(t(25,y+15,'Ø'+str(d),12))
        rect.append('<rect x="%s" y="%s" width="%.2f" height="20" fill="%s"/>'%(95,y,max(1,margin)*78,colors['good'] if margin>=1 else colors['fail']))
        rect.append(t(110+max(1,margin)*78,y+15,f'{margin:.2f} mm',12))
    rect.append(t(490,65,'Pole klejenia vs koncentracja naprężeń',14))
    for i,p in enumerate(peel):
        y=96+i*39
        rect.append(t(494,y,f'h={p["shear_offset_mm"]} mm; k={p["comparison_multiplier"]}:',12))
        rect.append(t(680,y,f'{p["peak_tensile_proxy_MPa"]:.3f} MPa',12))
    rect.append(t(490,350,'Uwaga: k=3 to MNOŻNIK PORÓWNAWCZY,',12))
    rect.append(t(490,367,'nie norma, wytrzymałość lub certyfikat.',12))
    rect.append('</svg>')
    (OUT/'b12_09_geometria_i_naprezenia_NIE_CNC.svg').write_text('\n'.join(rect)+'\n',encoding='utf-8')
    print(json.dumps(sums,indent=2))
    print('JSON SHA256',hashlib.sha256(out.read_bytes()).hexdigest())


if __name__=='__main__':main()
