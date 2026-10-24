"""P11: tłoki w nieskończonej odgrodzie i dokładne obrazy prostopadłych ścian.

Płaszczyzna odgrody y=0, tłoki mają środki(x,z). FLOOR:z=0, LEFT:x=0.
To geometrie wzorcowe, nie model wszystkich ścian rzeczywistego pokoju.
"""
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss
from model_promieniowania import piston_impedance,mutual_piston_impedance,disk_nodes,jinc
from model_gazu import Medium


def images(position_xz,walls=()):
    x,z=position_xz
    if any(w not in ['FLOOR','LEFT'] for w in walls):raise ValueError('Nieznana ściana')
    return [(sx*x,sz*z) for sx in ([1.,-1.] if 'LEFT' in walls else [1.])
            for sz in ([1.,-1.] if 'FLOOR' in walls else [1.])]


@lru_cache(maxsize=512)
def _mutual_cached(frequencies,area_a,area_b,distance,rho,c):
    # Średnia gęstość/c nie zmieniają geometrii ani pozostałych parametrów powietrza.
    medium=Medium(p0_pa=rho*c*c/1.4,temperature_k=c*c/(1.4*287.05))
    return mutual_piston_impedance(np.array(frequencies),area_a,area_b,distance,6,48,medium)


def image_radiation_matrix(f_hz,areas_m2,positions_xz,walls=(),medium=Medium()):
    f=np.atleast_1d(np.asarray(f_hz,float));areas=np.asarray(areas_m2,float)
    positions=np.asarray(positions_xz,float)
    if positions.shape!=(len(areas),2) or np.any(~np.isfinite(positions)) or np.any(areas<=0):
        raise ValueError('Niepoprawne pola i pozycje')
    for area,(x,z) in zip(areas,positions):
        a=np.sqrt(area/np.pi)
        if ('LEFT' in walls and x<=a) or ('FLOOR' in walls and z<=a):
            raise ValueError('Tłok przecina ścianę albo styka się z nią')
    n=len(areas);result=np.zeros((len(f),n,n),complex)
    for i in range(n):
        for j in range(n):
            for image_index,point in enumerate(images(positions[j],walls)):
                if i==j and image_index==0:
                    value=piston_impedance(f,areas[i],medium)
                else:
                    distance=float(np.linalg.norm(positions[i]-point))
                    value=_mutual_cached(tuple(f.tolist()),float(areas[i]),float(areas[j]),distance,medium.rho,medium.c)
                result[:,i,j]+=value
    return result


def image_pressure_operator(f_hz,areas_m2,positions_xz,observers_xyz,walls=(),medium=Medium(),radial_order=10,angular_order=96):
    f=np.atleast_1d(np.asarray(f_hz,float));areas=np.asarray(areas_m2,float)
    positions=np.asarray(positions_xz,float);observers=np.atleast_2d(np.asarray(observers_xyz,float))
    if positions.shape!=(len(areas),2) or observers.shape[1]!=3 or np.any(observers[:,1]<0):
        raise ValueError('Pozycje w odgrodzie, odbiornik po stronie y>=0')
    out=np.zeros((len(f),len(observers),len(areas)),complex)
    s=2j*np.pi*f
    for j,area in enumerate(areas):
        nodes,weights=disk_nodes(area,radial_order,angular_order)
        for point in images(positions[j],walls):
            source=np.stack([point[0]+nodes[:,0],np.zeros(len(nodes)),point[1]+nodes[:,1]],axis=1)
            for i,observer in enumerate(observers):
                distance=np.linalg.norm(observer-source,axis=1)
                if np.any(distance<=0):raise ValueError('Odbiornik w węźle powierzchni')
                out[:,i,j]+=medium.rho*s/(2*np.pi)*(np.exp(-s[:,None]*distance/medium.c)@(weights/distance))
    return out


def image_angular_resistance(f_hz,areas_m2,positions_xz,walls=(),medium=Medium(),order=64):
    """Niezależna całka mocy po kierunkach, macierz Grama >=0."""
    f=np.atleast_1d(np.asarray(f_hz,float));areas=np.asarray(areas_m2,float)
    positions=np.asarray(positions_xz,float)
    g,w=leggauss(order);mu=(g+1)/2;wm=w/2
    if 'FLOOR' in walls and 'LEFT' in walls:lo,hi=0.,np.pi/2
    elif 'FLOOR' in walls:lo,hi=0.,np.pi
    elif 'LEFT' in walls:lo,hi=-np.pi/2,np.pi/2
    else:lo,hi=0.,2*np.pi
    phi=lo+(g+1)*(hi-lo)/2;wp=w*(hi-lo)/2
    nx=(np.sqrt(1-mu[:,None]**2)*np.cos(phi)).ravel()
    nz=(np.sqrt(1-mu[:,None]**2)*np.sin(phi)).ravel()
    transverse=np.repeat(np.sqrt(1-mu**2),order)
    weights=(wm[:,None]*wp).ravel()
    result=np.empty((len(f),len(areas),len(areas)),complex)
    for q,frequency in enumerate(f):
        k=2*np.pi*frequency/medium.c
        field=[]
        for area,position in zip(areas,positions):
            phase=sum(np.exp(1j*k*(nx*x+nz*z)) for x,z in images(position,walls))
            field.append(area*jinc(k*np.sqrt(area/np.pi)*transverse)*phase)
        field=np.array(field).T
        result[q]=medium.rho*(2*np.pi*frequency)**2/(4*np.pi*np.pi*medium.c)*((field.conj().T*weights)@field)
    return result
