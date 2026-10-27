"""Dokładny model i weryfikacja3x3bez solvera,numpy i próbkowaniatemperatury.

Certyfikat dotyczy jawnej rodziny modelu,nie niezmierzonego urządzenia.
Parametry są zapisanymi liczbami dziesiętnymi,racjonalnymi w tej definicji.
"""
from fractions import Fraction as F
from itertools import combinations
import math


def frac(x):return F(str(x))


def transpose(A):return [list(r) for r in zip(*A)]


def matmul(A,B):
    return [[sum((x*y for x,y in zip(a,b)),F(0)) for b in zip(*B)] for a in A]


def minors3(A):
    assert A==transpose(A)
    values=[]
    for i in range(3):values.append(A[i][i])
    for i,j in combinations(range(3),2):values.append(A[i][i]*A[j][j]-A[i][j]*A[j][i])
    values.append(A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])-
        A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])+
        A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]))
    return values


def model(parameters,theta):
    p={k:frac(v) for k,v in parameters.items()}
    M,K,Le,BL,Rm,Re,Rs=[p[k] for k in ['M','K','Le','BL','Rms','Re0','Rs']]
    scales=[p['Xref'],F(1),p['Icap']]
    resistance=Re*(1+p['alpha']*theta)+Rs
    A=[[F(0),F(1),F(0)],[-K/M,-Rm/M,BL/M],[F(0),-BL/Le,-resistance/Le]]
    A=[[A[i][j]*scales[j]/scales[i] for j in range(3)] for i in range(3)]
    B=[F(0),F(0),1/(Le*scales[2])]
    return A,B


def certify(parameters,X,lam,gamma,voltage):
    p={k:frac(v) for k,v in parameters.items()};X=[[frac(v) for v in row] for row in X]
    lam,gamma,voltage=map(frac,[lam,gamma,voltage])
    assert all(v>0 for v in minors3(X)),'X must be strictly positive definite'
    assert X[0][0]<=1 and X[2][2]<=1 and lam>0 and gamma>0
    assert voltage>0 and voltage*voltage<=lam*gamma
    assert p['Icap']**2<=p['Ihardware']**2
    assert p['Icap']**2*p['Rth']*p['Re0']*(1+p['alpha']*p['theta_limit'])<=p['theta_limit']
    residual_minors=[]
    for theta in [F(0),p['theta_limit']]:
        A,B=model(parameters,theta);AX=matmul(A,X);XA=matmul(X,transpose(A))
        negative=[[-AX[i][j]-XA[i][j]-lam*X[i][j]-gamma*B[i]*B[j] for j in range(3)] for i in range(3)]
        values=minors3(negative);assert all(v>=0 for v in values),'Endpoint LMI failed'
        residual_minors.append([str(v) for v in values])
    return dict(exact_status='VERIFIED_RATIONAL_MODEL_FAMILY',
        X_principal_minors=[str(v) for v in minors3(X)],negative_LMI_principal_minors=residual_minors,
        thermal_margin=str(p['theta_limit']-p['Icap']**2*p['Rth']*p['Re0']*(1+p['alpha']*p['theta_limit'])),
        voltage_margin=str(lam*gamma-voltage*voltage),
        scope='All theta in[0,theta_limit] and all measurable source voltage |u|<=voltage,initial xi.T*X^-1*xi<=1 and temperature in interval;only stated model.')


def lower_sqrt(value,places=6):
    value=frac(value);scale=10**places
    integer=math.isqrt(value.numerator*scale*scale//value.denominator)
    result=F(integer,scale);assert result*result<=value and (result+F(1,scale))**2>value
    return result
