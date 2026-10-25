"""Wirtualny ubytek spoiny:pelna rama,energia potencjalna,styk po zamknieciu.

Gdelta jest energia dla skonczonego przyrostu defektu w modelu,nie Gc
materialu ani dowod inicjacji/zyciazmeczeniowego. Statyka,male deformacje.
"""
import csv,hashlib,json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from model_ramy_3D_P18C import Cabinet3D,BondPiece,clip_rectangle,polygon_quadrature,inverse_quad
from kontakt_brylowy_P19 import solve_hinges

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def cut_front_bottom(b,length):
    K=b.K-b.Kbond+b.floor_K;contact=[];weights=[];removed_area=0.;remaining=[];normal_axis=1
    cutoff=b.h-length
    for piece in b.bonds:
        if piece.name!='front_bottom':
            K+=piece.matrix(b.ndof);remaining.append(piece);continue
        first=b.xyz[piece.nodes[:4]][:,[0,2]];second=b.xyz[piece.nodes[4:]][:,[0,2]]
        lo=second.min(axis=0);hi=second.max(axis=0)
        for cracked in [False,True]:
            lower=lo.copy();upper=hi.copy()
            if cracked:lower[1]=max(lower[1],cutoff)
            else:upper[1]=min(upper[1],cutoff)
            if min(upper-lower)<=0:continue
            poly=clip_rectangle(first,lower,upper)
            if len(poly)<3:continue
            L=np.zeros((8,8));area=0.
            for point,w in polygon_quadrature(poly,4):
                N1=inverse_quad(first,point);N2=inverse_quad(second,point);d=np.r_[N1,-N2];area+=w
                if cracked:
                    # Front do korpusu:+y;d_y>0 oznacza scisniecie powierzchni.
                    ids=3*piece.nodes+normal_axis
                    contact.append(sparse.csr_matrix((d,(np.zeros(8,int),ids)),shape=(1,b.ndof)));weights.append(w)
                else:L+=w*np.outer(d,d)
            if cracked:removed_area+=area
            elif area>1e-18:
                part=BondPiece(piece.name,piece.nodes,L,area,normal_axis,piece.kn,piece.ks)
                K+=part.matrix(b.ndof);remaining.append(part)
    D=sparse.vstack(contact,format='csr') if contact else sparse.csr_matrix((0,b.ndof))
    return K,D,np.array(weights),removed_area,remaining


def tensile_measures(b,q):
    output={}
    for piece in b.bonds:
        axis=piece.normal_axis;other=[i for i in range(3) if i!=axis]
        first=b.xyz[piece.nodes[:4]][:,other];second=b.xyz[piece.nodes[4:]][:,other]
        poly=clip_rectangle(first,second.min(axis=0),second.max(axis=0))
        u=q[(3*piece.nodes[:,None]+np.arange(3)).ravel()].reshape(8,3)
        sign=-1 if piece.name.startswith(('front_','bottom_')) else 1
        item=output.setdefault(piece.name,dict(area=0.,positive2=0.,compression2=0.,peak_gauss=0.))
        for point,w in polygon_quadrature(poly,4):
            d=np.r_[inverse_quad(first,point),-inverse_quad(second,point)]
            stress=sign*piece.kn*(d@u[:,axis])
            item['area']+=w;item['positive2']+=w*max(stress,0)**2;item['compression2']+=w*min(stress,0)**2
            item['peak_gauss']=max(item['peak_gauss'],stress)
    return [dict(joint=name,tensile_spatial_rms_pa=float(np.sqrt(v['positive2']/v['area'])),
                 compressive_spatial_rms_pa=float(np.sqrt(v['compression2']/v['area'])),
                 sampled_tensile_max_pa=float(v['peak_gauss']),
                 scope='RMSpo powierzchni i probkowanymax;nie osobliwy peak3D/MDF ani dopuszczalna wytrzymalosc.') for name,v in output.items()]


def main():
    b=Cabinet3D(n=10);b.set_floor(1e5,1e4)
    gravity=-9.80665*(b.M@b.R[:,2]);conditions=[('GRAVITY',gravity),('GRAVITY_PLUS_STATIC_1KPA',gravity+1000*b.pressure)]
    rows=[];tractions=[]
    for label,F in conditions:
        q=spsolve(b.K+b.floor_K,F)
        for row in tensile_measures(b,q):tractions.append(dict(load=label,**row))
        previous_energy=.5*F@q;previous_area=0.
        base_energy=float(previous_energy)
        for length in [.005,.010,.015]:
            K,D,w,area,pieces=cut_front_bottom(b,length)
            q,J,active,meta=solve_hinges(K,D,w*b.bond_kn,np.zeros(len(w)),F,tol=1e-9)
            energy=float(.5*F@q);increment=(energy-previous_energy)/(area-previous_area)
            assert increment>=-1e-7,'Usuniecie spoiny nie moze zwiekszac energii potencjalnej minimalnej'
            margins=[float(-foot['k'][2]*(foot['P']@q)[2]) for foot in b.feet]
            assert min(margins)>0
            gap=-D@q;result=dict(load=label,crack_length_m=length,removed_area_m2=float(area),work_energy_j=energy,
                total_potential_release_j=energy-base_energy,finite_increment_release_j_m2=float(increment),
                active_compressive_contact_area_fraction=float(sum(w*active)/area),
                maximum_opening_sampled_m=float(max(max(gap),0)),minimum_floor_normal_reaction_n=min(margins),
                contact_newton_relative_residual=meta['residual'])
            rows.append(result);previous_area=area;previous_energy=energy
            print('P19D:',result,flush=True)
    for filename,items in [('p19d_wirtualne_rozwarstwienie.csv',rows),('p19d_naprezenia_rozciagajace.csv',tractions)]:
        keys=list(dict.fromkeys(k for r in items for k in r))
        with (OUT/filename).open('w',newline='') as f:
            writer=csv.DictWriter(f,keys);writer.writeheader();writer.writerows(items)
    out=dict(status='FINITE_VIRTUAL_DEBOND_SCREENING_NOT_MATERIAL_FRACTURE_OR_FATIGUE_TEST',cases=len(rows),
             debond='front_bottom,od krawedzi wewnetrznej wglab szerokosci spoiny;pelna szerokosc frontu.',
             contact='Po odspojeniu normalna kompresja zachowana,bez tarcia;rozciaganie i scinanie usuniete.',
             unresolved=['BrakGc/Kc/SN/J(t) spoinyMDF;nie wolno zGdelta oglosic zdatnosci kleju.',
                         'N10,zalecana odrebna zbieznosc defektu i pola dla decyzji o trwalosci.',
                         'Obciazenie1kPa jest osobna quasistatyczna kontrola,nie pasmem/audioRMS.',
                         'Brak geometrii czola pekniecia3D,MDFortotropii i lokalnej strefy kohezji.'],
             input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                           ['skrypty/rozwarstwienie_spoiny_P19D.py','skrypty/model_ramy_3D_P18C.py','skrypty/element_brylowy_P18C.py','skrypty/kontakt_brylowy_P19.py']})
    (OUT/'p19d_podsumowanie.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))


if __name__=='__main__':main()
