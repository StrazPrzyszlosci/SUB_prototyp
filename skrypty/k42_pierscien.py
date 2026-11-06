"""Nominal K42 trial drawings, local X/Z axes as viewed from cabinet front."""
from itertools import product
from math import cos, sin, radians, hypot, pi
from pathlib import Path
import ezdxf

OUT = Path(__file__).resolve().parents[1]/'dokumentacja/cnc/K42_PROBA_HOLD'
CENTER = (231.,250.)


def on_circle(radius, angle):
    return (CENTER[0]+radius*cos(radians(angle)), CENTER[1]+radius*sin(radians(angle)))


def draw(name, features, metal=False):
    doc = ezdxf.new('R2010')
    doc.units = 4
    space = doc.modelspace()
    if not metal:
        doc.layers.new('FORMAT_22')
        space.add_lwpolyline([(0,0),(1080,0),(1080,500),(0,500)],close=True,
                             dxfattribs={'layer':'FORMAT_22'})
    for layer, diameter, locations in features:
        doc.layers.new(layer)
        for pos in locations:
            space.add_circle(pos,diameter/2,dxfattribs={'layer':layer})
    path = OUT/(name+'_HOLD.dxf')
    doc.saveas(path)
    check = ezdxf.readfile(path)
    audit = check.audit()
    assert not audit.errors and not audit.fixes and check.units==4
    for layer, diameter, locations in features:
        circles = list(check.modelspace().query(f'CIRCLE[layer=="{layer}"]'))
        assert len(circles)==len(locations)
        for e,(x,y) in zip(circles,locations):
            assert abs(2*e.dxf.radius-diameter)<1e-8
            assert hypot(e.dxf.center.x-x,e.dxf.center.y-y)<1e-8


if __name__=='__main__':
    OUT.mkdir(exist_ok=True,parents=True)
    bolts=[on_circle(184,a) for a in range(0,360,45)]
    pins=[on_circle(194,a) for a in (90,270)]
    draw('FR1', [('KOSZ_PRZELOT',355.8,[CENTER]),('M5_LUZ_PROBA',5.6,bolts)])
    draw('FR2_OD_STRONY_FR1',[('KOSZ_PRZELOT',355.8,[CENTER]),
        ('KIESZEN_Z6_20',400.4,[CENTER]),('OD_DNA_Z4',6.5,bolts),
        ('KOLKI_OD_DNA_Z5',4.2,pins)])
    draw('STAL_6',[('OBRYS',400,[CENTER]),('WEW',358,[CENTER]),
        ('GWINT_M5x0_8_NOM',5,bolts),('KOLKI_NOM_4',4,pins)],True)
    # Length under head minus the entire stack before first steel face.
    # Ring can float against FR1 or against the pocket floor.
    cases=[]
    for L,washer,flange,gasket,front,offset,metal in product(
            (39.8,40.2),(.9,1.1),(10.3,10.7),(.7,1.3),(21.5,22.5),
            (0,.65),(5.9,6.1)):
        reach=L-washer-flange-gasket-front-offset
        cases.append((min(reach,metal),max(0,reach-metal)))
    print('gross engagement min / protrusion max',min(x for x,y in cases),max(y for x,y in cases))
    print('nominal gross steel mass kg',pi*(200**2-179**2)*6*7.85e-6)
