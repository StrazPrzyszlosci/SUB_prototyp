"""Wyszukiwanie numeryczne;przyjęcie wyłącznie po dokładnym certify().

X w znormalizowanych współrzędnych x/Xref,v/(1m/s),i/Icap.
Nie certyfikuje globalnej optymalności U ani fizycznych parametrów produktów.
"""
from fractions import Fraction as F
import warnings
import numpy as np
import cvxpy as cp
from certyfikat_przedzialu_P24 import model,certify,lower_sqrt,frac


def find(parameters,lambda_fractions=(.02,.05,.1,.2,.4,.6,.8)):
    endpoints=[model(parameters,t) for t in [F(0),frac(parameters['theta_limit'])]]
    A=[np.array(a,dtype=float) for a,b in endpoints];B=np.array(endpoints[0][1],float)
    decay=min(-float(np.max(np.linalg.eigvals(a).real)) for a in A)
    assert decay>0
    X=cp.Variable((3,3),symmetric=True);gamma=cp.Variable(nonneg=True);lam=cp.Parameter(nonneg=True)
    constraints=[X>>1e-7*np.eye(3),X[0,0]<=1,X[2,2]<=1]
    for a in A:constraints.append(a@X+X@a.T+lam*X+gamma*np.outer(B,B)<<-1e-5*np.eye(3))
    problem=cp.Problem(cp.Maximize(gamma),constraints);accepted=[];trials=[]
    for fraction in lambda_fractions:
        value=F(str(round(2*decay*fraction,8)));lam.value=float(value)
        try:
            with warnings.catch_warnings(record=True) as messages:
                result=problem.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9,max_iter=200)
            trial=dict(lambda_fraction=fraction,lambda_value=str(value),solver_status=problem.status,
                warnings=[str(m.message) for m in messages],candidate_accepted=False)
            if X.value is not None and gamma.value is not None and gamma.value>0:
                # Zmniejszenie ellipsoidy i budżetu wejścia daje margines przed
                # zaokrągleniem. Ostateczne kryterium to dokładne nierówności.
                rational=[[F(str(round(float(v)*.98,12))) for v in row] for row in (X.value+X.value.T)/2]
                g=F(str(float(gamma.value)))*F(98,100)*F(95,100)
                voltage=lower_sqrt(value*g,6)
                check=certify(parameters,rational,value,g,voltage)
                candidate=dict(parameters=parameters,X=[[str(v) for v in row] for row in rational],
                    lambda_value=str(value),gamma=str(g),source_peak_voltage_v=str(voltage),
                    verification=check,solver_status=problem.status,
                    search_scope='Feasible witness at one of seven selected lambda;not global voltage optimum.')
                accepted.append(candidate);trial['candidate_accepted']=True;trial['voltage_float']=float(voltage)
            trials.append(trial)
        except Exception as e:
            trials.append(dict(lambda_fraction=fraction,lambda_value=str(value),candidate_accepted=False,error=type(e).__name__+': '+str(e)))
    if not accepted:return None,trials
    return max(accepted,key=lambda r:frac(r['source_peak_voltage_v'])),trials
