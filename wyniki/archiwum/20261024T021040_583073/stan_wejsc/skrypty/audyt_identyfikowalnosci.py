"""P03/P05: strukturalna nieidentyfikowalność i syntetyczna identyfikacja.

Nie są to pomiary urządzeń. W eksperymencie odwrotnym Re,Le i Sd są znane,
a objętości60/100l mają idealną podatność, bez przecieku i wypełnienia.
"""
from dataclasses import replace
from pathlib import Path
import csv,json
import numpy as np
import sympy as sp
from scipy.optimize import brentq
from model_subwoofera import Driver,response,RHO,C

ROOT=Path(__file__).resolve().parents[1]


def identify_combinations(z,f,re,le):
    s=2j*np.pi*f
    motional=z-re-s*le
    # motional*(s²+r*s+k)=b*s; r=Rms/Mms,k=Kms/Mms,b=BL²/Mms.
    a=np.column_stack([motional*s,motional,-s]);target=-motional*s*s
    aa=np.vstack([a.real,a.imag]);yy=np.concatenate([target.real,target.imag])
    scales=np.linalg.norm(aa,axis=0)
    fit,_,rank,_=np.linalg.lstsq(aa/scales,yy,rcond=None)
    if rank!=3:raise ArithmeticError('Niedostateczny rząd eksperymentu')
    return fit/scales,float(np.linalg.cond(aa/scales))


def main():
    b,m,r,k=sp.symbols('B M R K',positive=True)
    jac=sp.Matrix([b*b/m,r/m,k/m]).jacobian([b,m,r,k])
    assert jac.rank()==3
    assert sp.simplify(jac*sp.Matrix([b/2,m,r,k]))==sp.zeros(3,1)
    catalog=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())
    f=np.geomspace(2,300,161);s=2j*np.pi*f
    rows=[];max_scale=max_recovery=max_unknown_sd=0.
    for raw in catalog['drivers']:
        d=Driver(**raw['model'])
        free=d.re_ohm+s*d.le_mh*1e-3+d.bl*d.bl*s/(d.mms*s*s+d.rms*s+1/d.cms)
        for alpha in (.25,4.):
            scaled=d.re_ohm+s*d.le_mh*1e-3+(alpha*d.bl*d.bl)*s/(alpha*d.mms*s*s+alpha*d.rms*s+alpha/d.cms)
            err=float(np.max(abs(scaled/free-1)));max_scale=max(max_scale,err)
            assert err<2e-12
            # Przy nieznanymSd nawet znana skrzynia+SPL nie usuwa tej swobody.
            alternative=replace(d,sd_cm2=d.sd_cm2*np.sqrt(alpha))
            za=response(d,100,f);zb=response(alternative,100,f)
            err2=float(np.max(abs(zb['z']/za['z']-1)));max_unknown_sd=max(max_unknown_sd,err2)
            assert err2<2e-12
            np.testing.assert_allclose(za['spl_rms_db'],zb['spl_rms_db'],atol=2e-11)
        z60=response(d,60,f)['z'];z100=response(d,100,f)['z']
        c60,cond60=identify_combinations(z60,f,d.re_ohm,d.le_mh*1e-3)
        c100,cond100=identify_combinations(z100,f,d.re_ohm,d.le_mh*1e-3)
        kb60=RHO*C*C*d.sd*d.sd/.06;kb100=RHO*C*C*d.sd*d.sd/.1
        estimated_mass=(kb60-kb100)/(c60[1]-c100[1])
        error=abs(estimated_mass/d.mms-1);max_recovery=max(max_recovery,float(error))
        assert error<1e-9
        rows.append({'candidate_id':raw['candidate_id'],'driver':d.name,'synthetic_mms_g':d.mms*1000,
                     'identified_mms_g':estimated_mass*1000,'relative_recovery_error':error,
                     'scaled_design_condition_60l':cond60,'scaled_design_condition_100l':cond100})
    with (ROOT/'wyniki/p03_identyfikacja_syntetyczna.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Oddzielne projekcje tabeli pomiarowej: bez przypisywania nieznanegoLe próbkom.
    published=json.loads((ROOT/'dane/zrodla/pomiary_opublikowane/scan32_voicecoil_2013.json').read_text())
    sets=published['parameter_sets'][:]
    current=next(x['model'] for x in catalog['drivers'] if x['candidate_id']=='C10')
    sets.append({'label':'FACTORY_CURRENT','fs_hz':current['fs_hz'],'qms':current['qms'],
                 'qes':current['qes'],'vas_l':current['vas_l'],'method':'factory_current'})
    projections=[]
    for item in sets:
        q=item['qms']*item['qes']/(item['qms']+item['qes'])
        for vb in (40.,50.,67.,100.,150.):
            scale=np.sqrt(1+item['vas_l']/vb);fc=item['fs_hz']*scale;qt=q*scale
            def power(freq):return freq**4/((fc*fc-freq*freq)**2+(freq*fc/qt)**2)
            f3=brentq(lambda freq:power(freq)-.5,1e-5,1000)
            projections.append({'parameter_set':item['label'],'method':item['method'],'vb_l':vb,'qts':q,
                                'fc_hz':fc,'qtc':qt,'f3_classical_projection_hz':f3,
                                'normalized_gain_20hz_db':10*np.log10(power(20.)),
                                'scope':'PROJEKCJA_2_RZEDU_NIE_ODTWORZENIE_LEAP5_LTD_ANI_POMIAR_SKRZYNI'})
    with (ROOT/'wyniki/p03_scan32_zestawy_opublikowane.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(projections[0]));w.writeheader();w.writerows(projections)
    result={'status':'DOWOD_MODELOWY_I_EKSPERYMENT_SYNTETYCZNY_NIE_POMIAR','drivers':len(rows),
            'symbolic_rank':3,'mechanical_unknowns':4,'scaling_null_vector':'[B/2,M,R,K]',
            'max_relative_free_air_scaling_error':max_scale,'max_relative_two_volume_mass_recovery_error':max_recovery,
            'max_relative_unknown_Sd_closed_box_scaling_error':max_unknown_sd,
            'published_parameter_projections':len(projections),
            'limitations':['ZnaneRe,Le,Sd i idealne podatności; brak szumu w eksperymencie identyfikacji.',
                           'Dwie próbki nie określają rozkładu populacji.','TabeliLTD nie uznano za kompletny modelLEAP5.']}
    (ROOT/'wyniki/p03_identyfikowalnosc.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
