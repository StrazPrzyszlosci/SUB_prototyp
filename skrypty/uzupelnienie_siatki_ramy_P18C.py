"""Adaptacyjna kontrola siatki,warstw,kwadratury i scenariusza zamocowan."""
import csv,gc,hashlib,json,resource
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from model_ramy_3D_P18C import Cabinet3D,BondPiece,clip_rectangle,polygon_quadrature,inverse_quad

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def point(b,label):
    q,F,a=b.balanced_static(b.pressure);values,vectors=b.free_modes(6)
    return dict(label=label,n=b.n,dof=b.ndof,compliance_m3_pa=float(b.pressure@q),
                first_elastic_hz=float(np.sqrt(values[6])/(2*np.pi)),
                peak_process_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)


def main():
    with (OUT/'p18c_rama.csv').open() as f:base=list(csv.DictReader(f))
    prev=next(x for x in base if x['case_id']=='MESH_14')
    previousC=float(prev['wall_volume_compliance_m3_pa']);previousF=float(prev['first_elastic_hz'])
    rows=[];unexecuted=[]
    for n in [18,22]:
        available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
        if available<1_500_000_000:
            unexecuted.append(dict(n=n,reason='MEMORY_GUARD',available_bytes=available));break
        b=Cabinet3D(n=n);r=point(b,'ADAPTIVE_'+str(n));rows.append(r)
        r['relative_change_compliance']=float(abs(r['compliance_m3_pa']/previousC-1));r['relative_change_f1']=float(abs(r['first_elastic_hz']/previousF-1))
        print('P18C adaptive',r,flush=True);del b;gc.collect()
        if max(r['relative_change_compliance'],r['relative_change_f1'])<.01:break
        previousC=r['compliance_m3_pa'];previousF=r['first_elastic_hz']
    b=Cabinet3D(n=10,nt=3);thickness=point(b,'THICKNESS_3');del b;gc.collect()
    b=Cabinet3D(n=10);baseline=point(b,'QUADRATURE3')
    pieces=[];deltaF=np.zeros(b.ndof)
    for piece in b.bonds:
        axis=piece.normal_axis;other=[i for i in range(3) if i!=axis]
        first=b.xyz[piece.nodes[:4]][:,other];second=b.xyz[piece.nodes[4:]][:,other]
        poly=clip_rectangle(first,second.min(axis=0),second.max(axis=0));L=np.zeros((8,8));area=0.
        for p,w in polygon_quadrature(poly,4):
            N1=inverse_quad(first,p);N2=inverse_quad(second,p);d=np.r_[N1,-N2]
            L+=w*np.outer(d,d);area+=w
        assert abs(area/piece.area-1)<1e-10
        new=BondPiece(piece.name,piece.nodes,L,area,axis,piece.kn,piece.ks);pieces.append(new)
        sign=-1 if piece.name.startswith(('front_','bottom_')) else 1
        difference=L[:4,:4].sum(axis=1)-piece.L[:4,:4].sum(axis=1)
        deltaF[3*piece.nodes[:4]+axis]-=sign*difference
    Knew=sum((p.matrix(b.ndof) for p in pieces),sparse.csr_matrix(b.K.shape))
    b.K=b.K-b.Kbond+Knew;b.Kbond=Knew;b.bonds=pieces;b.pressure+=deltaF
    quadrature=point(b,'QUADRATURE4')
    Kg=sparse.csr_matrix(b.K.shape)
    for p in pieces:
        L=p.L.copy();L[:4,4:]=0;L[4:,:4]=0
        Kg+=BondPiece(p.name,p.nodes,L,p.area,p.normal_axis,p.kn,p.ks).matrix(b.ndof)
    locked=b.Kmaterial+b.basket_K+Kg;qq=spsolve(locked,b.pressure)
    fixture=dict(scope='Kazda strona spoiny osobno do nieruchomej sprezystej podpory;nie gorna/dolna granica realnejskrzyni.',
                 compliance_m3_pa=float(b.pressure@qq),full_frame_to_fixed_sides_ratio=float(quadrature['compliance_m3_pa']/(b.pressure@qq)))
    gravity_checks=[];K0=b.K.copy();M0=b.M.copy()
    for count in [0,1,2]:
        b.K=K0.copy();b.M=M0.copy();b.add_ties(count)
        for support in [1e4,1e5,1e6]:
            b.set_floor(support,support/10);F=-9.80665*(b.M@b.R[:,2]);q=spsolve(b.K+b.floor_K,F)
            translation=float(max(abs(np.r_[q[:3*b.nnode],q[-6:-3]])));all_slots=float(max(abs(q)))
            gravity_checks.append(dict(ties=count,support=support,max_translation_m=translation,max_all_generalized_slots=all_slots,
                                       translation_is_maximum=translation==all_slots))
    assert all(r['translation_is_maximum'] for r in gravity_checks)
    del b;gc.collect()
    free=Cabinet3D(n=3,bond_kn=0,bond_ks=0);rigids=[]
    for p in free.panels:
        R=np.zeros((free.ndof,6));ids=slice(3*p.offset,3*(p.offset+len(p.xyz)));R[ids]=free.R[ids]
        if p.name=='front':R[-6:]=free.R[-6:]
        rigids.append(R)
    R=np.column_stack(rigids);rigid_error=float(np.linalg.norm(free.K@R)/np.linalg.norm(free.K.data))
    assert np.linalg.matrix_rank(R)==36 and rigid_error<1e-12
    result=dict(status='ADAPTIVE_SCOPED_MESH_AND_BOUNDARY_CONTROLS',adaptive=rows,unexecuted=unexecuted,
                stopping_rule='Ostatnia zmiana C i f1<1%;to kontrola siatki,nie certyfikat bledu continuum.',
                thickness3=thickness,quadrature3=baseline,quadrature4=quadrature,fixed_sides_experiment=fixture,
                gravity_translation_field_checks=gravity_checks,zero_bond_independent_rigid_modes=36,zero_bond_rigid_relative_error=rigid_error,
                input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                              ['skrypty/element_brylowy_P18C.py','skrypty/model_ramy_3D_P18C.py','skrypty/uzupelnienie_siatki_ramy_P18C.py','wyniki/p18c_rama.csv']})
    (OUT/'p18c_adaptacja_i_granice.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P18C adaptacja complete',fixture,'warstwy3',thickness,flush=True)


if __name__=='__main__':main()
