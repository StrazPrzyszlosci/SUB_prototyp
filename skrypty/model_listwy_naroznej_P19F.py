"""Addytywna bryła listwy front–dno: dwie spoiny, masa, poprawny port gazu.

Nie zmienia bazowego modelu P18C ani jego historycznych danych.
Współrzędne lokalne: x szerokość, y wgłąb, z wysokość, SI.
"""
import numpy as np
from scipy import sparse
from element_brylowy_P18C import isotropic_D
from model_ramy_3D_P18C import Cabinet3D, block_panel


def dilation_vector(b):
    return np.r_[b.xyz.ravel(),b.basket_reference,np.zeros(3)] if b.with_basket else b.xyz.ravel()


def add_cleat(b,section=.03,end_gap=.01,cross_intervals=4,kn=None,ks=None,
              E=2.1e9,nu=.3,density=730.):
    """Dodaje jedną listwę do nowo utworzonej ramy, przed ustawieniem podpór.

    Osobne węzły MDF oraz skończone kn/ks. Pokryte powierzchnie frontu/dna
    przestają przenosić ciśnienie; odsłonięte cztery ściany listwy je przenoszą.
    """
    if b.floor_K.nnz or hasattr(b,'cleat'):
        raise ValueError('Listwa przed podporami i tylko raz')
    W,D,H=b.inside;h=b.h
    if not (0<section<min(D,H)/3 and 0<2*end_gap<W and cross_intervals>=1):
        raise ValueError('Poprawny przekrój i prześwit końców')
    if h+section>=((H+2*h)/2-b.radius):
        raise ValueError('Listwa koliduje z nominalnym głównym otworem')
    kn=b.bond_kn if kn is None else kn
    ks=b.bond_ks if ks is None else ks
    if min(kn,ks,E,density)<=0:raise ValueError('Dodatnie parametry')
    p=block_panel('cleat',[
        np.linspace(h+end_gap,h+W-end_gap,b.n+1),
        np.linspace(h,h+section,cross_intervals+1),
        np.linspace(h,h+section,cross_intervals+1)],isotropic_D(E,nu),density,True)
    old_nodes=b.nnode;old_dof=b.ndof;extra_dof=3*len(p.xyz)
    volume_before=float(b.pressure@dilation_vector(b)/3)
    old_mass=float(b.R[:,2]@(b.M@b.R[:,2]))
    b.nnode+=len(p.xyz);b.ndof+=extra_dof
    # Przesuwamy sześć współrzędnych kosza na koniec; węzły ścian bez zmiany.
    old_to_new=np.r_[np.arange(3*old_nodes),
                     np.arange(3*old_nodes,old_dof)+extra_dof]
    T=sparse.csr_matrix((np.ones(old_dof),(old_to_new,np.arange(old_dof))),shape=(b.ndof,old_dof))
    embed=lambda A:(T@A@T.T).tocsr()
    for attr in ['K','Kmaterial','Kbond','M']:
        setattr(b,attr,embed(getattr(b,attr)))
    if b.with_basket:
        b.basket_K=embed(b.basket_K)
        b.basket_D=b.basket_D@T.T
    b.pressure=np.asarray(T@b.pressure).ravel()
    b.frozen_original_pressure=b.pressure.copy()
    p.offset=old_nodes;b.xyz=np.vstack([b.xyz,p.xyz])
    b.panels.append(p);b.byname[p.name]=p
    tail=6 if b.with_basket else 0
    Kp=sparse.block_diag([sparse.csr_matrix((3*old_nodes,3*old_nodes)),p.K,
                        sparse.csr_matrix((tail,tail))],format='csr')
    Mp=sparse.block_diag([sparse.csr_matrix((3*old_nodes,3*old_nodes)),p.M,
                        sparse.csr_matrix((tail,tail))],format='csr')
    b.K+=Kp;b.Kmaterial+=Kp;b.M+=Mp
    count=len(b.bonds);original_kn,original_ks=b.bond_kn,b.bond_ks
    b.bond_kn,b.bond_ks=kn,ks
    front=b.byname['front'];bottom=b.byname['bottom']
    b._flat_mortar(front,front.faces(1,h),p,p.faces(1,h),1,-1)
    b._flat_mortar(bottom,bottom.faces(2,h),p,p.faces(2,h),2,-1)
    b.bond_kn,b.bond_ks=original_kn,original_ks
    Knew=sum((piece.matrix(b.ndof) for piece in b.bonds[count:]),sparse.csr_matrix(b.K.shape))
    b.K+=Knew;b.Kbond+=Knew
    for axis,value,sign in [(0,h+end_gap,1),(0,h+W-end_gap,-1),
                             (1,h+section,-1),(2,h+section,-1)]:
        b.pressure+=b.surface_load(p,p.faces(axis,value),np.eye(3)[axis]*sign)
    b.R=b.rigid_modes();b.mass_rigid=b.R.T@(b.M@b.R)
    b.floor_K=sparse.csr_matrix(b.K.shape)
    volume=(W-2*end_gap)*section**2
    areas={name:sum(x.area for x in b.bonds[count:] if x.name==name)
           for name in ['front_cleat','bottom_cleat']}
    expected_area=(W-2*end_gap)*section
    assert all(abs(a/expected_area-1)<1e-9 for a in areas.values()),areas
    mass=float(b.R[:,2]@(b.M@b.R[:,2]))-old_mass
    volume_after=float(b.pressure@dilation_vector(b)/3)
    closure=float(np.linalg.norm(b.R.T@b.pressure))
    rigid_error=float(np.linalg.norm(b.K@b.R)/np.linalg.norm(b.K.data))
    checks=dict(added_mass_kg=mass,analytic_mass_kg=density*volume,
        occupied_volume_m3=volume,gas_port_volume_reduction_m3=volume_before-volume_after,
        pressure_rigid_resultant_norm=closure,rigid_K_relative_error=rigid_error,
        new_bond_areas_m2=areas)
    assert abs(mass/(density*volume)-1)<1e-9
    assert abs((volume_before-volume_after)/volume-1)<1e-8,checks
    assert closure<1e-9 and rigid_error<1e-12,checks
    b.cleat=dict(section_m=section,end_gap_m=end_gap,cross_intervals=cross_intervals,
                 panel=p,checks=checks)
    return b


def model(n=10,section=.03,cross_intervals=4,kn=None,ks=None,end_gap=.01):
    b=Cabinet3D(n=n)
    if section:add_cleat(b,section,end_gap,cross_intervals,kn,ks)
    return b
