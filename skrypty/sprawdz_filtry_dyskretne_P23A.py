"""Odrębne rachunki:80cyfr,równanie DF1 i symboliczne stabilne granice."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,csv
import mpmath as mp
import numpy as np
import sympy as sp
from scipy import signal
from model_filtrow_dyskretnych_P23 import (chain,schur,represent,frequency_response,
    quadratic,bilinear_second_order,feedback_convention,from_feedback)

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def df1(sos,x):
    out=np.array(x,dtype=float)
    for section in sos:
        b=section[:3];a=section[3:];y=np.zeros_like(out)
        xp=xpp=yp=ypp=0.
        for k,v in enumerate(out):
            z=b[0]*v+b[1]*xp+b[2]*xpp-a[1]*yp-a[2]*ypp
            y[k]=z;xpp,xp=xp,v;ypp,yp=yp,z
        out=y
    return out


def main():
    symbols=[];k,b,c=sp.symbols('k b c',positive=True);s,z=sp.symbols('s z')
    den=k*k+b*k+c;a1=(-2*k*k+2*c)/den;a2=(k*k-b*k+c)/den
    for lhs,rhs in [(1+a1+a2,4*c/den),(1-a1+a2,4*k*k/den),
                    (1-a2,2*b*k/den),(1+a2,2*(k*k+c)/den)]:
        assert sp.simplify(lhs-rhs)==0;symbols.append(str(sp.factor(rhs)))
    # Cayley:Re(s)<0 odpowiada |z|<1. Dodatnie współczynniki Hurwitza.
    p=sp.expand((1+s)**2+a1*(1+s)*(1-s)+a2*(1-s)**2)
    expected=(1-a1+a2)*s*s+2*(1-a2)*s+(1+a1+a2)
    assert sp.simplify(p-expected)==0;symbols.append('Cayley quadratic identity')
    wc,wt,qc,qt=sp.symbols('wc wt qc qt',positive=True)
    cabinet=s*s/(s*s+s*wc/qc+wc*wc);lt=(s*s+s*wc/qc+wc*wc)/(s*s+s*wt/qt+wt*wt)
    assert sp.simplify(cabinet*lt-s*s/(s*s+s*wt/qt+wt*wt))==0
    symbols.append('Le0 physical analog LT cancellation only')
    assert sp.limit(4*c/den,c,0)==0 and sp.limit(2*b*k/den,b,0)==0
    assert sp.limit(a1,k,sp.oo)==-2 and sp.limit(a2,k,sp.oo)==1
    symbols+=['cutoff0 margin0','Qinfinity margin0','Fs_infinity poles_to1']
    mp.mp.dps=80
    def exact(x):
        n,d=float(x).as_integer_ratio();return mp.mpf(n)/d
    refs=[];delaychecks=[];coefficient_checks=[];time=[]
    for fs in [48000,96000,192000]:
        sos=chain(57.,.93,25.,1/np.sqrt(2),18.,80.,fs)
        assert np.array_equal(from_feedback(feedback_convention(sos)),sos)
        for rep in ['float64','float32','decimal6']:
            test=represent(sos,rep)
            def hmp(f):
                q=mp.exp(-2j*mp.pi*f/fs);h=mp.mpc(1)
                for row in test:
                    v=list(map(exact,row));h*=(v[0]+v[1]*q+v[2]*q*q)/(v[3]+v[4]*q+v[5]*q*q)
                return h
            for f in [.5,20.,31.5,80.,500.]:
                h,tau=frequency_response(test,np.array([f]),fs);target=hmp(mp.mpf(f))
                error=float(abs(mp.mpc(h[0])-target)/abs(target));assert error<1e-9
                refs.append(dict(fs=fs,representation=rep,f_hz=f,relative_error=error))
                # Nie korzysta ze wzoru pochodnej zaimplementowanego w modelu.
                d=mp.diff(hmp,mp.mpf(f));delay=-mp.im(d/target)/(2*mp.pi)
                e=float(abs(mp.mpf(tau[0])-delay));assert e<1e-9
                delaychecks.append(dict(fs=fs,representation=rep,f_hz=f,absolute_delay_error_s=e))
        # Odrębna transformacja biblioteczna,w tym prewarp jawnie PRZED wywołaniem.
        for f in [.5,18.,80.,10000.]:
            q=1/np.sqrt(2);pre=fs/np.pi*np.tan(np.pi*f/fs)
            ours=bilinear_second_order([1.,0.,0.],quadratic(pre,q),fs)
            bs,ads=signal.bilinear([1.,0.,0.],quadratic(pre,q),fs=fs)
            error=float(np.max(abs(ours-np.r_[bs,ads])));assert error<2e-14
            # Oryginalne HPF/RBJ:po normalizacji a0,musi dać to samo.
            omega=2*np.pi*f/fs;alpha=np.sin(omega)/(2*q)
            rbj=np.array([(1+np.cos(omega))/2,-(1+np.cos(omega)),(1+np.cos(omega))/2,
                          1+alpha,-2*np.cos(omega),1-alpha])/(1+alpha)
            re=float(np.max(abs(ours-rbj)));assert re<2e-14
            coefficient_checks.append(dict(fs=fs,f_hz=f,scipy_error=error,rbj_error=re))
        t=np.arange(8000)/fs;x=.1*np.sin(2*np.pi*25*t)+.03*np.cos(2*np.pi*70*t)
        independent=df1(sos,x);sosout=signal.sosfilt(sos,x)
        e=float(np.max(abs(independent-sosout)));assert e<2e-8
        time.append(dict(fs=fs,n=len(x),max_absolute_DF1_vs_DF2T_error=e))
    boundary=np.array([1.,-1.,0.,1.,-1.5,.5]);verdict=schur(boundary)
    assert verdict['state']=='boundary' and verdict['p_plus1']==0
    # Dokładny licznik/mianownik mają wspólny z-1,lecz stan nadal ma biegun1.
    assert sp.simplify((z*z-z)/(z*z-sp.Rational(3,2)*z+sp.Rational(1,2))-z/(z-sp.Rational(1,2)))==0
    unstable=np.array([1.,0.,0.,1.,-1.9,.8]);assert schur(unstable)['state']=='outside'
    marginal=np.array([1.,0.,0.,1.,0.,1.]);assert schur(marginal)['state']=='boundary'
    # Niewłaściwa konwencja znaku w przykładzie z oficjalnej dokumentacji:
    # traktowanie dodatniego feedback c1 jako naszego a1 daje biegun poza kołem.
    official=np.array([.998191200483864,-1.9950521500467384,.996920046761057,
                       1.,-1.9950521500467384,.9951112472449212])
    wrong=official.copy();wrong[4:]*=-1
    assert schur(official)['state']=='strict' and schur(wrong)['state']=='outside'
    selected=[]
    with (OUT/'p23a_kaskady_i_kwantyzacja.csv').open() as f:campaign=list(csv.DictReader(f))
    for rep in ['float32','decimal6','decimal9']:
        worst=max((r for r in campaign if r['representation']==rep),key=lambda r:float(r['max_abs_gain_error_db']))
        fs=float(worst['sample_rate_hz']);base=chain(float(worst['fc_hz']),float(worst['qtc']),float(worst['target_hz']),1/np.sqrt(2),18.,80.,fs)
        quant=represent(base,rep);freq=np.unique(np.r_[np.geomspace(20,80,1001),20,25,31.5,40,63,80])
        href,_=frequency_response(base,freq,fs);hq,_=frequency_response(quant,freq,fs)
        errors=20*np.log10(abs(hq/href));i=int(np.argmax(abs(errors)));f=mp.mpf(float(freq[i]))
        def evaluate(coeff):
            q=mp.exp(-2j*mp.pi*f/fs);h=mp.mpc(1)
            for row in coeff:
                v=list(map(exact,row));h*=(v[0]+v[1]*q+v[2]*q*q)/(1+v[4]*q+v[5]*q*q)
            return h
        precise=20*mp.log10(abs(evaluate(quant)/evaluate(base)))
        error=float(abs(precise-float(errors[i])));assert error<1e-7
        selected.append(dict(configuration=worst['configuration'],representation=rep,f_hz=float(f),
            signed_error_db_float=float(errors[i]),signed_error_db_80digits=str(precise),absolute_difference_db=error))
    result=dict(status='COMPLETE_SCOPED_INDEPENDENT_DIGITAL_CONTROLS',symbolic_identities=symbols,
        high_precision_frequency=refs,high_precision_group_delay=delaychecks,
        independent_coefficients=coefficient_checks,DF1_time_comparisons=time,
        exact_boundary_and_sign_controls=4,
        selected_large_quantization_errors=selected,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            Path(__file__).resolve(),ROOT/'skrypty/model_filtrow_dyskretnych_P23.py',
            OUT/'p23a_kaskady_i_kwantyzacja.csv']},
        limitations=['80-digit evaluations validate stored coefficients,not unidentified hardware.',
            'Four exact algebraic boundary/sign controls do not exhaust nonlinear state arithmetic.',
            'Feedback interpretation of manufacturer example is an inference,not a measured import roundtrip.'])
    (OUT/'p23a_kontrole_niezalezne.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P23A controls:',len(symbols),'symbolic;',len(refs),'80-digit;',len(coefficient_checks),'coeff;',len(time),'DF1')


if __name__=='__main__':main()
