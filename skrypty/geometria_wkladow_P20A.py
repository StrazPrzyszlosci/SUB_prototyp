"""P20A: nominalne bryły, rozdzielne bilanse i konstruktywne tory wsuwania.

Bez CAD. Tylko obroty zerowe, translacje osiowe, ustalona kolejność.
Kolizje odcinka ruchu z AABB sprawdzane na całej objętości zamiatania.
"""
from dataclasses import dataclass
from itertools import product
import numpy as np


@dataclass(frozen=True)
class Box:
    lo:tuple
    hi:tuple
    name:str=''

    @property
    def volume(self):return float(np.prod(np.array(self.hi)-self.lo))


def intersects(a,b,gap=0.):
    return bool(np.all(np.array(a.hi)+gap>np.array(b.lo)+1e-12) and
                np.all(np.array(b.hi)+gap>np.array(a.lo)+1e-12))


def intersection_volume(a,b):
    return float(np.prod(np.maximum(0.,np.minimum(a.hi,b.hi)-np.maximum(a.lo,b.lo))))


def obstacles(cfg,ties):
    W,D,H=cfg['inside_width_depth_height_m'];s=cfg['cleat_size_m'];e=cfg['cleat_end_gap_m']
    boxes=[Box((e,0,0),(W-e,s,s),'cleat')]
    ty,tz=cfg['brace_section_y_z_m'];px,py,pz=cfg['brace_pad_x_y_z_m']
    locations=[.55] if ties==1 else [.4,.7] if ties==2 else []
    for k,f in enumerate(locations):
        y=D*f;z=H/2
        boxes += [Box((px,y-ty/2,z-tz/2),(W-px,y+ty/2,z+tz/2),f'tie{k}'),
                  Box((0,y-py/2,z-pz/2),(px,y+py/2,z+pz/2),f'padL{k}'),
                  Box((W-px,y-py/2,z-pz/2),(W,y+py/2,z+pz/2),f'padR{k}')]
    assert not any(intersects(a,b) for i,a in enumerate(boxes) for b in boxes[i+1:])
    return boxes


def liner_envelope_volume(cfg,hard):
    W,D,H=cfg['inside_width_depth_height_m'];t=cfg['lining_reserved_thickness_m']
    core=Box((t,0,t),(W-t,D-t,H-t))
    gross=W*D*H-core.volume
    occupied=sum(b.volume-intersection_volume(b,core) for b in hard)
    return gross-occupied


def position_bounds(outer,lo):
    lo=np.asarray(lo);return Box(tuple(lo),tuple(lo+np.asarray(outer)))


def axis_path_clear(positions,outer,hard,gap):
    for a,b in zip(positions[:-1],positions[1:]):
        a=np.array(a);b=np.array(b);assert np.count_nonzero(abs(a-b)>1e-12)<=1
        sweep=Box(tuple(np.minimum(a,b)),tuple(np.maximum(a,b)+outer))
        if any(intersects(sweep,o,gap) for o in hard):return False
    return True


def packing(cfg,outer,opening,ties):
    W,D,H=cfg['inside_width_depth_height_m'];a,c,b=outer;g=cfg['geometric_clearance_m_assumed']
    pad=cfg['lining_reserved_thickness_m']+g;spacing=cfg['packing_gap_m'];front=cfg['packing_front_y_m']
    aperture_ok=np.hypot(a,b)+2*g<=opening+1e-12
    def positions(total,size):
        n=int(np.floor((total-2*pad+spacing)/(size+spacing)+1e-10))
        if n==1:return [(total-size)/2]
        return list(np.linspace(pad,total-pad-size,n)) if n>1 else []
    xs,zs=positions(W,a),positions(H,b)
    ny=max(0,int(np.floor((D-pad-front+spacing)/(c+spacing)+1e-10)))
    ys=[front+i*(c+spacing) for i in range(ny)]
    hard=obstacles(cfg,ties);base_hard=list(hard)
    targets=sorted(product(xs,ys,zs),key=lambda p:(-p[1],p[2],p[0]))
    accepted=[];paths=[];final_reject=path_reject=0
    center=np.array([(W-a)/2,0.,(H-b)/2]);entry=cfg['cleat_size_m']+g
    start=center.copy();start[1]=-c-cfg['host_wall_thickness_m']-g
    entered=center.copy();entered[1]=entry
    for target in targets:
        target=np.array(target);box=position_bounds(outer,target)
        if any(intersects(box,o,g) for o in base_hard):final_reject+=1;continue
        if not aperture_ok:path_reject+=1;continue
        path=None
        for order in [(0,2),(2,0)]:
            points=[start.copy(),entered.copy()];p=entered.copy()
            for axis in order:p=p.copy();p[axis]=target[axis];points.append(p.copy())
            p=p.copy();p[1]=target[1];points.append(p)
            if axis_path_clear(points,np.array(outer),hard,g):path=points;break
        if path is None:path_reject+=1;continue
        hard.append(box);accepted.append(box);paths.append([p.tolist() for p in path])
    # Te same odcinki w odwrotnej kolejności usuwają moduły w odwrotnej kolejności.
    reverse=list(base_hard)+accepted
    for box,path in reversed(list(zip(accepted,paths))):
        reverse.pop();assert axis_path_clear(path[::-1],np.array(outer),reverse,g)
    return dict(outer_width_length_height_m=list(outer),opening_nominal_m=opening,ties=ties,
        aperture_cross_diagonal_m=float(np.hypot(a,b)),aperture_pass=bool(aperture_ok),
        nominal_grid_slots=len(targets),final_collision_rejections=final_reject,
        path_rejections=path_reject,accepted_modules=len(accepted),
        geometric_displacement_l=len(accepted)*float(np.prod(outer))*1000,
        reverse_removal_verified=True,paths=paths,
        final_boxes=[dict(lo=b.lo,hi=b.hi) for b in accepted],
        scope='One prescribed axis-aligned sequence with two orderings of x/z moves; no proof of globally maximal packing or impossibility with rotations.')
