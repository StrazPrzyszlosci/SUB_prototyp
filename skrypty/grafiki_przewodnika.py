"""Własne grafiki redakcyjne SVG/PNG; schemat koncepcji,nie wynik symulacji.

PNG1280x640 spełnia zalecany format GitHub Social preview. Nie ustawia
zdalnego pola Social preview; taki status trzeba sprawdzić osobno.
"""
from pathlib import Path
import hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle,FancyBboxPatch,Arc
import numpy as np

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'grafika'
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'path','svg.hashsalt':'SUB_prototyp-editorial-v1'})


def counts():
    base=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    extra=json.loads((ROOT/'dane/przetworniki/rozszerzenie_SB_20261025.json').read_text())['products']
    return len(base)+len(extra),len({x['manufacturer'] for x in base+extra})


def make(height,name):
    width=1280;social=height==640
    fig=plt.figure(figsize=(width/100,height/100),dpi=100,facecolor='#0b1523')
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,width),ylim=(0,height));ax.set_axis_off()
    for x in range(0,width,64):ax.plot([x,x],[0,height],color='#172738',lw=.5,zorder=0)
    for y in range(0,height,64):ax.plot([0,width],[y,y],color='#172738',lw=.5,zorder=0)
    ax.add_patch(Polygon([[720,0],[1280,0],[1280,height],[960,height]],facecolor='#102333',edgecolor='none',zorder=0))
    for r in np.linspace(210,40,12):ax.add_patch(Circle((1050,height*.53),r,facecolor='#3abbaa',alpha=.013,edgecolor='none'))
    x=74
    def label(y,text,size=16,color='#ecf3f6',weight='normal',alpha=1):
        ax.text(x,y,text,fontsize=size,color=color,fontweight=weight,va='center',alpha=alpha)
    label(height*.91,'AKUSTYKA  /  ELEKTROAKUSTYKA  /  DIY',13,color='#69dfcd',weight='bold')
    label(height*.75,'SUB_prototyp',52 if social else 47,weight='bold')
    label(height*.53 if social else height*.49,'Subwoofer DIY\nod teorii do prototypu',29 if social else 25,weight='bold')
    label(height*.32 if social else height*.27,'Źródła · obliczenia · symulacje',16 if social else 14,color='#b8cbd4')
    models,makers=counts();label(height*.22 if social else height*.16,f'{models} modeli głośników  ·  {makers} producentów',18 if social else 15,color='#69dfcd',weight='bold')
    badge_y=height*.105 if social else height*.065
    ax.add_patch(FancyBboxPatch((x-2,badge_y-14),302 if social else 268,29,boxstyle='round,pad=0.02,rounding_size=6',facecolor='#20303a',edgecolor='#3a4e55',lw=.8))
    ax.add_patch(Circle((x+14,badge_y),4,facecolor='#f3c768',edgecolor='none'))
    ax.text(x+28,badge_y,'BADANIA PRZED BUDOWĄ',fontsize=12 if social else 10.5,color='#f3c768',va='center',fontweight='bold')
    if social:ax.text(x,20,'github.com/StrazPrzyszlosci/SUB_prototyp',fontsize=12,color='#8da9b5',va='center')
    # Ortogonalny rzut izometryczny rzeczywistej geometrii odniesienia.
    # Wymiary są wejściami modeli,nie końcowym wynikiem optymalizacji prototypu.
    cfg=json.loads((ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json').read_text())
    W,D,H=(np.array(cfg['inside_width_depth_height_m'])+2*cfg['host_wall_thickness_m'])*1000
    source=json.loads((ROOT/'dane/zrodla/P18B_geometria_i_ograniczenia.json').read_text())
    driver=next(r['facts'] for r in source['sources'] if r['source_id']=='SRC03')
    basis=np.array([[np.sqrt(3)/2,np.sqrt(3)/2,0.],[-.5,.5,1.]])
    assert np.allclose(np.linalg.norm(basis,axis=0),1.)
    corners=np.array([(xx,yy,zz) for xx in [0,W] for yy in [0,D] for zz in [0,H]])
    projected=corners@basis.T;lo=projected.min(axis=0);hi=projected.max(axis=0)
    scale=min(390/(hi[0]-lo[0]),height*(.62 if social else .70)/(hi[1]-lo[1]))
    offset=np.array([1040.,height*.55])-(lo+hi)/2*scale
    def project(points):return np.asarray(points)@basis.T*scale+offset
    front=project([[0,0,0],[W,0,0],[W,0,H],[0,0,H]])
    side=project([[W,0,0],[W,D,0],[W,D,H],[W,0,H]])
    top=project([[0,0,H],[W,0,H],[W,D,H],[0,D,H]])
    ax.add_patch(Polygon(side,facecolor='#122638',edgecolor='#3d7381',lw=1.4))
    ax.add_patch(Polygon(top,facecolor='#284052',edgecolor='#54838c',lw=1.4))
    ax.add_patch(Polygon(front,facecolor='#1b3042',edgecolor='#77c9c4',lw=1.7))
    angles=np.linspace(0,2*np.pi,160)
    radius=driver['outside_diameter_mm']/2
    def ring(center,rr,color,lw=1.):
        points=np.column_stack([center[0]+rr*np.cos(angles),np.zeros_like(angles),center[1]+rr*np.sin(angles)])
        ax.add_patch(Polygon(project(points),closed=True,facecolor=color,edgecolor='#6fa6ad',lw=lw))
    # Zewnętrzny obrys kosza z rysunku C04; wnętrze stożka ma charakter ilustracyjny.
    for rr,color in [(radius,'#0a1521'),(radius*.88,'#33505f'),(radius*.79,'#112331'),(radius*.58,'#264655'),(radius*.30,'#142634')]:
        ring((W/2,H/2),rr,color)
    for angle in np.linspace(0,2*np.pi,driver['bolt_count'],endpoint=False):
        center=(W/2+driver['bolt_circle_mm']/2*np.cos(angle),H/2+driver['bolt_circle_mm']/2*np.sin(angle))
        ring(center,driver['bolt_hole_mm']/2,'#d0e1e7',lw=.2)
    bottom=(lo[1]*scale+offset[1])
    ax.text(1040,bottom-23,'OBUDOWA ODNIESIENIA',ha='center',fontsize=10,color='#8badb8')
    ax.text(1040,bottom-42,f'{W:.0f} × {D:.0f} × {H:.0f} mm',ha='center',fontsize=11,color='#b8cbd4')
    ax.text(1040,bottom-57,'szerokość × głębokość × wysokość',ha='center',fontsize=8,color='#8badb8')
    for ext in ['svg','png']:
        target=OUT/(name+'.'+ext)
        fig.savefig(target,dpi=100,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else {'Software':'SUB_prototyp / grafiki_przewodnika.py'})
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True);make(420,'README_baner');make(640,'social-preview')
    assert (OUT/'social-preview.png').stat().st_size<1_000_000
    paths=[ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json',ROOT/'dane/zrodla/P18B_geometria_i_ograniczenia.json',Path(__file__),ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'dane/przetworniki/rozszerzenie_SB_20261025.json']
    cfg=json.loads(paths[0].read_text());inside=cfg['inside_width_depth_height_m'];wall=cfg['host_wall_thickness_m']
    record=dict(status='REFERENCE_GEOMETRY_VISUALISATION_NOT_FINAL_PROTOTYPE',
        inside_width_depth_height_mm=[1000*v for v in inside],wall_mm=wall*1000,
        outside_width_depth_height_mm=[1000*(v+2*wall) for v in inside],
        model_and_manufacturer_counts=counts(),
        projection='Orthographic isometric;equal projected length per unit along all3axes.',
        driver='Nominal flange and bolt pattern of C04/SB34SWPL76-4;cone shading illustrative;not a final driver choice.',
        input_sha256={str(v.relative_to(ROOT)):hashlib.sha256(v.read_bytes()).hexdigest() for v in paths},
        output_sha256={str(v.relative_to(ROOT)):hashlib.sha256(v.read_bytes()).hexdigest() for v in sorted(OUT.glob('*')) if v.suffix in ['.svg','.png']})
    (OUT/'pochodzenie.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('Created reference-geometry banners;1280x420 and1280x640;outer504x684x504mm;not final design.')


if __name__=='__main__':main()
