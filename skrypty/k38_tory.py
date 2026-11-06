"""Continuous straight service sweeps with actual occupancy, rounded frames and end contacts."""
import json
import math
from pathlib import Path

from k36_bank_z_pomiarow import K32, K33, keeper_parts

ROOT = Path(__file__).resolve().parents[1]
ROUTES = json.loads((ROOT/'wyniki/k30_stale_kanaly_audyt.json').read_text())
KEEPERS = {(a['row'], a['extended']):keeper_parts(a) for a in K33['assemblies']}
# Hypothetical post-measurement tolerances in mm, not machining guarantees.
FIXED_FACE = .25  # cut .10 + locating .10 + reading .05
POSE = .15        # locating .10 + reading .05
SIZE = .10        # total span error of finished part
SEP_FINISH = .10  # total thickness error; centred about separator mid-plane



def bounds(part, offset=(0.,0.,0.)):
    lo = tuple(p+d for p,d in zip(part['o'],offset))
    return lo, tuple(p+s for p,s in zip(lo,part['s']))


def expand(rect, low, high=None):
    high = low if high is None else high
    return tuple(x-e for x,e in zip(rect[0],low)),tuple(x+e for x,e in zip(rect[1],high))


def sweep(part, start, end):
    if sum(abs(a-b)>1e-8 for a,b in zip(start,end))>1:
        raise ValueError('A diagonal requires a different sweep model')
    a, b = bounds(part,start),bounds(part,end)
    return tuple(map(min,zip(a[0],b[0]))),tuple(map(max,zip(a[1],b[1])))


def gap_axis(a,b,j):
    return max(b[0][j]-a[1][j],a[0][j]-b[1][j])


def separation(a,b):
    return max(gap_axis(a,b,j) for j in range(3))


def rounded_margin(y,z,window):
    """Signed Euclidean margin of a point inside a rounded rectangle."""
    lo_y,lo_z,hi_y,hi_z,r=window
    qy=abs(y-(lo_y+hi_y)/2)-(hi_y-lo_y)/2+r
    qz=abs(z-(lo_z+hi_z)/2)-(hi_z-lo_z)/2+r
    return r-math.hypot(max(qy,0.),max(qz,0.))-min(max(qy,qz),0.)


def spread(part, kind, robust):
    if not robust:
        return (0.,)*3,(0.,)*3
    if kind=='fixed':
        return (FIXED_FACE,)*3,(FIXED_FACE,)*3
    if kind=='box':
        return (POSE,)*3,(POSE+SIZE,)*3
    if kind=='separator':
        return (POSE+SEP_FINISH/2,POSE,POSE),(POSE+SEP_FINISH/2,POSE+SIZE,POSE+SIZE)
    if kind=='tool':
        return (.20,)*3,(.20,)*3
    return (FIXED_FACE,)*3,(FIXED_FACE,)*3  # machined assembly and locating uncertainty


def gauge(row, y):
    original_y=341 if y==347 else y
    old=next(t for t in ROUTES['tool_paths'] if t['row']==row and t['y']==original_y)
    path=[]
    for index,pt in enumerate(old['waypoints']):
        path.append([pt[0],pt[1]+1+(y-original_y if index else 0),pt[2]+1])
    return [{'id':'tool','o':[0,0,0],'s':[60,18,18]}],path


def fasteners(row):
    z=(88,204,320,426)[row]
    pieces=[]
    for y in (55,347):
        for tag,x,length,radius in [('head',424,5,5),('washer',429,1,6),('shank',430,49,2.5)]:
            pieces.append({'id':f'M5_{tag}_{row}_{y}',
                           'o':[x,y-radius,z-radius],'s':[length,2*radius,2*radius]})
    return pieces


def audit(scene,robust):
    parts=scene['parts']
    frames=[parts[name] for name in ('PORTAL','MID_PORTAL')]
    mat={'id':'MAT','o':[22,360,22],'s':[1036,50,456]}
    stationary=[p for p in parts.values() if p['kind']=='fixed' and not p['windows']]
    stationary+=scene['plates']+K32['hardware']+[mat]
    front=parts['FR2']['o'][1]+parts['FR2']['s'][1]+(.15 if robust else 0)
    obstacles=[(p['id'],expand(bounds(p),*spread(p,'fixed',robust)),p) for p in stationary]
    installed={}
    locked={row:False for row in range(4)}  # False=short keeper; all four fitted in empty 150 state.
    events=[]

    def visit(tag,kind,row,movers,path,action,transition, *, tool_axis=None):
        # Removal traverses exactly these same segments in reverse with the same bystanders.
        bystanders=list(obstacles)
        for name,(item,item_kind) in installed.items():
            bystanders.append((name,expand(bounds(item),*spread(item,item_kind,robust)),item))
        for other,extended in locked.items():
            for p in KEEPERS[other,extended]+fasteners(other):
                bystanders.append((f'locked{other}/{p["id"]}',expand(bounds(p),*spread(p,'steel',robust)),p))
        errors=[]
        contacts=set()
        minimum=(float('inf'),'')
        def note(value,where,seg):
            nonlocal minimum
            if value<minimum[0]:
                minimum=(value,where)
            if value<1e-8:
                errors.append({'segment':seg,'obstacle':where,'margin_mm':round(value,5)})
        for index,(start,end) in enumerate(zip(path,path[1:])):
            final=index==len(path)-2
            for mover in movers:
                sw=expand(sweep(mover,start,end),*spread(mover,kind,robust))
                endpoint=bounds(mover,end)
                landing=final and kind in ('box','separator') and start[2]>end[2]
                docking=final and kind=='keeper' and mover['id']=='bar' and end[0]>start[0]
                for name,other,original in bystanders:
                    if landing and name.startswith('RAIL_') and name.split('_')[2]==str(row):
                        top=original['o'][2]+original['s'][2]
                        if (abs(endpoint[0][2]-top)<=.50+1e-9
                            and bounds(mover,start)[0][2]-(POSE if robust else 0)>other[1][2]
                            and max(gap_axis(sw,other,0),gap_axis(sw,other,1))<=0):
                            contacts.add(name)
                            continue
                    if (final and tool_axis is not None and name==f'locked{row}/M5_head_{row}_{tool_axis}'
                        and abs(endpoint[1][0]-original['o'][0])<1e-8):
                        contacts.add(name)
                        continue
                    note(separation(sw,other),name,index)
                e=FIXED_FACE if robust else 0.
                for frame in frames:
                    outer=expand(bounds(frame),(e,)*3)
                    xgap=gap_axis(sw,outer,0)
                    if xgap>1e-8:
                        continue
                    if docking and frame['id']=='PORTAL' and abs(endpoint[1][0]-frame['o'][0])<1e-8:
                        contacts.add('PORTAL/seat_X')
                        continue
                    margins=[]
                    for number,(u,v,U,V,r) in enumerate(frame['windows']):
                        window=(frame['o'][1]+u+e,frame['o'][2]+v+e,
                                frame['o'][1]+U-e,frame['o'][2]+V-e,r)
                        bottom=sw[0][2]
                        # A downward last leg stops on the highest bearing surface.
                        # Only its lower face is clipped; top, side and R4 checks still apply.
                        if (landing and frame['id']=='MID_PORTAL' and number==row
                            and abs(endpoint[0][2]-(frame['o'][2]+v))<=.5+1e-9
                            and bounds(mover,start)[0][2]-(POSE if robust else 0)>window[1]
                            and bottom<=window[1]):
                            contacts.add('MID_PORTAL/sill')
                            # At floor contact both lower corners must lie on the straight
                            # part of the sill. Still require positive margins on the sides/top.
                            margins.append(min(sw[0][1]-window[0]-r,window[2]-r-sw[1][1],
                                               window[3]-sw[1][2]))
                            continue
                        margins.append(min(rounded_margin(y,z,window)
                                           for y in (sw[0][1],sw[1][1]) for z in (bottom,sw[1][2])))
                    best=max(margins)
                    note(max(xgap,gap_axis(sw,outer,1),gap_axis(sw,outer,2),best),frame['id'],index)
                # Through-front slab and exact radial envelope (including centre and radius errors).
                centre_err=.1 if robust else 0.
                radius=177.9-centre_err
                radial=radius-max(math.hypot(abs(x-231)+centre_err,abs(z-250)+centre_err)
                                  for x in (sw[0][0],sw[1][0]) for z in (sw[0][2],sw[1][2]))
                note(max(-sw[1][1],sw[0][1]-front,radial),'front/bore',index)
        events.append({'transition':transition,'action':action,'object':tag,'kind':kind,
                       'clear':not errors,'errors':errors,'terminal_contacts':sorted(contacts),
                       'critical_noncontact_obstacle':minimum[1],
                       'minimum_test_margin_mm':round(minimum[0],5)})

    def keeper(row,extended,action,transition):
        original=next(k for k in ROUTES['keeper_paths'] if k['row']==row and k['extended']==extended)
        visit(f'keeper_{row}_'+('long' if extended else 'short'),'keeper',row,
              KEEPERS[row,extended],original['shifts'],action,transition)

    def tool(row,action,transition):
        for y in (55,347):
            pieces,path=gauge(row,y)
            visit(f'tool_{row}_{y}','tool',row,pieces,path,action,transition,tool_axis=y)

    def add(name,row,transition):
        is_box=name.startswith('M')
        body=scene['boxes'][name] if is_box else parts[name]
        o=body['o'];length,width,height=body['s'];travel=body['travel_z_mm']
        entry=231.-length/2
        path=[[entry,-width-10,250-height/2],[entry,70,250-height/2],
              [entry,70,travel],[o[0],70,travel],o]
        item={'id':name,'o':[0.,0.,0.],'s':body['s']}
        kind='box' if is_box else 'separator'
        visit(name,kind,row,[item],path,'insert',transition)
        installed[name]=(body,kind)

    schedule=[('150→120',0,('M0F','SEP_0','M0N'),False),
              ('150→120',1,('M1F',),True),
              ('150→120',3,('M3F','SEP_3','M3N'),False),
              ('120→100',1,('SEP_1','M1N'),False),
              ('120→100',2,('M2F','SEP_2','M2N'),False)]
    for transition,row,additions,extended in schedule:
        tool(row,'undo_M5',transition)
        old=locked.pop(row)
        keeper(row,old,'remove',transition)
        for name in additions:
            add(name,row,transition)
        keeper(row,extended,'install',transition)
        locked[row]=extended
        tool(row,'fasten_M5',transition)
    return {'events':events,'count':len(events),'clear':sum(e['clear'] for e in events),
            'reverse_sequence':'100→120→150 retraces the forward events in exact reverse occupancy',
            'error_model':'axis-aligned hard parts; terminal contact stops on first face; no pads, hand, rotation or deformation'}
