#!/usr/bin/env python3
"""P30D: mass centroid and ideal rigid-block tip-over statics for vertical sealed cabinets.
An analytic diagnostic, not an accident safety certification; ignores anchors and floor dynamics.
Requires NumPy and p30a_robust_geometry.py in same directory (or skrpyty path).
"""
from pathlib import Path
import numpy as np,math,itertools,json
from p30a_robust_geometry import geo,volume
ROOT=Path(__file__).resolve().parent
OUT=(ROOT.parent/'wyniki') if ROOT.name=='skrypty' else ROOT
G=9.81

def mass_elem(box,density):
    vol=volume(box)/1e9
    assert vol>0
    return vol*density,tuple(box.mean(axis=0))

def cabinet_shell(W,D,H,rho):
    t=22;front=44;xi=231;zi=250;R=177.9
    p=[(
        W*H*front-math.pi*R*R*front,(W/2,front/2,H/2),'front-minus-hole'),
        (W*H*t,(W/2,D-t/2,H/2),'back'),
        (t*(D-front-t)*H,(t/2,(front+D-t)/2,H/2),'left'),
        (t*(D-front-t)*H,(W-t/2,(front+D-t)/2,H/2),'right'),
        ((W-2*t)*(D-front-t)*t,(W/2,(front+D-t)/2,t/2),'bottom'),
        ((W-2*t)*(D-front-t)*t,(W/2,(front+D-t)/2,H-t/2),'top')]
    # correct the front centroid because the off-axis baffle cutout removes material at xi.
    Vfront=W*H*front-math.pi*R*R*front
    front_x=(W*H*front*(W/2)-math.pi*R*R*front*xi)/Vfront
    p[0]=(Vfront,(front_x,front/2,H/2),'front-minus-hole')
    assert all(x[0]>0 for x in p)
    return [(V*1e-9*rho,xyz,label) for V,xyz,label in p]

def inserts_for_mode(mods,mode,rho):
    mode_counts={'150':(2,0),'120':(11,1),'100':(16,3)}
    large,small=mode_counts[mode]
    choices=mods[:small]+mods[4:4+large]
    assert len(choices)==small+large
    output=[]
    for m in choices:
        dims=m[1]-m[0]
        # 8 mm MDF nominal shell volume; empty air inside is not part of insert mass.
        vsolid=np.prod(dims)-np.prod(dims-16)
        assert vsolid>0
        center=m.mean(axis=0)+[22,44,22]
        output.append((vsolid*1e-9*rho,center,'insert'))
    return output

def scene(W,D,H,fill,mode,rho,driver_mass,driver_y,driver_up):
    L,br,mods,mat=geo(W,D,fill)
    parts=cabinet_shell(W,D,H,rho)
    for b in br:
        parts.append(mass_elem(b+np.array([[22,44,22],[22,44,22]]),rho)+('brace',))
    parts+=inserts_for_mode(mods,mode,rho)
    # approximate 40mm/35mm/50mm 20 kg/m3 fill only within porosity volume envelope;
    # structural interactions and cutouts are not geometrically modelled in this COM screen.
    matmass=(L[0]*L[2]*fill/1e9)*20
    parts.append((matmass,(W/2,D-22-fill/2,H/2),'rear-mat'))
    parts.append((driver_mass,(231,driver_y,250),'driver-center-model'))
    masses=np.array([item[0] for item in parts]); centers=np.array([item[1] for item in parts])
    mass=masses.sum();com=(masses[:,None]*centers).sum(axis=0)/mass
    if driver_up:
        zheight=W-com[0]  # rotate around the old x axis; high driver location
    else:
        zheight=com[0]    # speaker close to lower end
    planar_x= com[1]     # front/back: D axis
    planar_y= com[2]     # side-to-side: old H axis
    edges={'front':planar_x, 'rear':D-planar_x, 'sideL':planar_y, 'sideR':H-planar_y}
    assert min(edges.values())>0 and zheight>0
    min_edge=min(edges,key=edges.get);dist=edges[min_edge]
    angle=math.degrees(math.atan2(dist,zheight))
    # horizontal static force acting at cabinet top 1040mm above the ground
    force=mass*G*dist/W
    mu_crit=dist/W
    return dict(W_mm=W,D_mm=D,mode=mode,driver_up=driver_up,rho=rho,
      driver_mass_kg=driver_mass,driver_center_depth_mm=driver_y,
      modeled_mass_kg=round(mass,4),COM_height_mm=round(zheight,3),
      COM_from_front_mm=round(planar_x,3),COM_from_side_mm=round(planar_y,3),
      most_vulnerable_edge=min_edge,static_tip_angle_deg=round(angle,3),
      quasi_static_horizontal_top_force_N=round(force,3),
      mu_critical_for_tipping_before_sliding=round(mu_crit,4))

def main():
    cases=[(1000,440,500,50),(1040,430,500,40),(1050,425,500,35)]
    rows=[scene(*shape,mode,rho,m,ym,up) for shape in cases
      for mode,rho,m,ym,up in itertools.product(('150','120','100'),(650,800),(10,15,20),(90,130,170),(False,True))]
    assert len(rows)==3*3*2*3*3*2
    assert all(x['static_tip_angle_deg']>0 for x in rows)
    # symmetry test: just flipping driver side up/down changes COM height not its planar coordinates.
    for i in range(0,len(rows),2):
        a,b=rows[i:i+2]
        assert a['mode']==b['mode'] and a['W_mm']==b['W_mm']
        assert a['modeled_mass_kg']==b['modeled_mass_kg']
        assert a['COM_from_front_mm']==b['COM_from_front_mm']
        assert abs(a['COM_height_mm']+b['COM_height_mm']-a['W_mm'])<.0011
    summary=[]
    for W,D,H,fill in cases:
      for up in (False,True):
       sample=[r for r in rows if r['W_mm']==W and r['driver_up']==up]
       summary.append(dict(W_mm=W,D_mm=D,driver_up=up,
           min_tip_angle_deg=min(r['static_tip_angle_deg'] for r in sample),
           max_tip_angle_deg=max(r['static_tip_angle_deg'] for r in sample),
           min_static_top_push_N=min(r['quasi_static_horizontal_top_force_N'] for r in sample),
           max_COM_height_mm=max(r['COM_height_mm'] for r in sample)))
    out=dict(study='P30D',date='2026-10-31',status='rigid-block quasi-static tipping and mass distribution screen only',
      n_scenarios=len(rows),summary=summary,rows=rows,
      assumptions=['Position of driver mass approximated at outer x=231mm, z=250mm and y in [90,130,170]mm.',
        'Actual Dayton mass, screws, cable, feet, material and driver COM are not measured; driver mass 10/15/20kg assumed.',
        'All walls uniform assumed MDF rho 650 or 800kg/m3; front circular hole removed for mass and centroid.',
        'Braces are model P20D AABBs, module shells are hollow 8mm MDF, no braces or modules are proven structurally safe.',
        'Stationary upright body rotated so the driver is at its low end or high end. Feet are assumed flush; anchoring/impacts, friction, push at other height excluded.',
        'Angle and tip-force are ideal static block estimates only; NOT a safe handling or anti-tip threshold.'],
      decisions=['Prefer driver low when upright for a lower COM and reduced risk of tipping, subject to room acoustic positioning and real feet.',
        'Any floor or child/pet-contact exposure requires independent mechanical stability engineering and, where appropriate, anti-tip restraint.',
        'Confirm actual mass and mounting geometry before design of foot/anchor and transport fixtures.'])
    (OUT/'p30d_stabilnosc_pionowa_20261031.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('CASES',len(rows))
    print('SUMMARY',summary)
if __name__=='__main__':main()
