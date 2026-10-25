"""Niezależne wzorce płyty, blokady ścinania i sił ściągu; bez prototypu."""
import json
from pathlib import Path
import time
import numpy as np
from scipy.linalg import eigvalsh
from scipy.sparse.linalg import spsolve
from model_plyty_MITC_P18 import PlateMaterial,RectangularPlate,element_matrices,navier_reference

ROOT=Path(__file__).resolve().parents[1]


def main():
    m=PlateMaterial(2.1e9,.3,730,.022);a=.46;b=.64
    ke,me,fe=element_matrices(.1,.12,m)
    eig=eigvalsh(ke);rigid=int(sum(abs(eig)<max(abs(eig))*1e-10));assert rigid==3
    coordinates=np.array([[0.,0.],[.1,0.],[.1,.12],[0.,.12]])
    residual=[]
    for kind in ('translation','tilt_x','tilt_y'):
        q=np.zeros((4,3))
        if kind=='translation':q[:,0]=1.
        if kind=='tilt_x':q[:,0]=coordinates[:,0];q[:,1]=1.
        if kind=='tilt_y':q[:,0]=coordinates[:,1];q[:,2]=1.
        residual.append(float(np.linalg.norm(ke@q.ravel())/(np.linalg.norm(ke)*np.linalg.norm(q))))
    assert max(residual)<1e-13
    reference=navier_reference(a,b,m,401);convergence=[]
    for n in [4,8,12,20,28]:
        p=RectangularPlate(a,b,n,n,m);q=p.static();f=p.modes(3)[0]
        center=np.argmin(np.sum((p.xy-np.array([a/2,b/2]))**2,axis=1));w=p.transverse_displacements(q)[center]
        U=p.expand(q);reaction=p.full_K@U-p.full_F
        force_error=float(abs(sum(reaction[0::3])+a*b)/(a*b))
        energy_error=float(abs(q@(p.K@q)-q@p.F)/abs(q@p.F))
        convergence.append(dict(mesh_n=n,first_mode_hz=float(f[0]),center_m_pa=float(w),compliance_m3_pa=float(p.F@q),
            frequency_relative_error=float(abs(f[0]/reference['first_mode_hz']-1)),center_relative_error=float(abs(w/reference['center_static_m_per_pa']-1)),
            compliance_relative_error=float(abs(p.F@q/reference['volume_compliance_m3_pa']-1)),force_relative_error=force_error,energy_relative_error=energy_error))
    assert convergence[-1]['frequency_relative_error']<.002
    assert convergence[-1]['center_relative_error']<.002
    assert convergence[-1]['compliance_relative_error']<.005
    assert max(r['force_relative_error'] for r in convergence)<1e-8
    # Niezależna granicaKirchhoffa wraz z coraz cieńszą płytą; zwykłeQ4ulega blokadzie.
    locking=[]
    for thickness in [.04,.02,.005,.001]:
        mat=PlateMaterial(2.1e9,.3,730,thickness);ref=navier_reference(.5,.5,mat,101)
        vals=[]
        for form in ['MITC','Q4_FULL']:
            p=RectangularPlate(.5,.5,10,10,mat,formulation=form);q=p.static()
            vals.append(float(p.F@q/ref['volume_compliance_m3_pa']))
        locking.append(dict(thickness_m=thickness,MITC_compliance_ratio=vals[0],Q4_FULL_compliance_ratio=vals[1]))
    assert locking[-1]['MITC_compliance_ratio']>.97 and locking[-1]['Q4_FULL_compliance_ratio']<.1
    # Brzeg ze sprężyną obrotową pomiędzySSSS aCCCC dla statycznej pracyuniformp.
    compliances=[]
    for beta in [0.,1.,10.,100.,10000.,np.inf]:
        boundary='SSSS' if beta==0 else ('CCCC' if np.isposinf(beta) else 'ELASTIC')
        p=RectangularPlate(a,b,12,12,m,boundary,rotational_edge_n=beta*m.rigidity_nm/min(a,b))
        q=p.static();compliances.append(float(p.F@q))
    assert all(x>y for x,y in zip(compliances[:-1],compliances[1:]))
    p=RectangularPlate(a,b,16,16,m);patch=p.patch_average((a/2,b/2),(.08,.08));u=p.static();z=spsolve(p.K,patch)
    c=float(patch@z);d=float(patch@u);pair=[]
    for stiffness in [0.,1e3,1e5,1e7,1e10]:
        K,M=p.tied_pair(patch,stiffness,.25,pad_mass_each_kg=.08);q=p.static(K)
        predicted=u-z*(2*stiffness*d/(1+2*stiffness*c))
        error=float(np.linalg.norm(q-predicted)/np.linalg.norm(predicted));assert error<1e-8
        force=2*stiffness*float(patch@q)
        pair.append(dict(stiffness_n_m=stiffness,Sherman_Morrison_relative_error=error,tie_force_per_pa_n=force,
                         analytic_tie_force_per_pa_n=float(2*stiffness*d/(1+2*stiffness*c))))
    Ka,Ma=p.tied_pair(patch,4e6,.25,'antisymmetric',.08)
    assert np.linalg.norm((Ka-p.K).data)==0
    bare=p.modes(6)[0];antisym=p.modes(6,Ka,Ma)[0]
    assert max(antisym-bare)<1e-6
    dyn,_,rayleigh=p.frequency_response([20.,80.,bare[0],200.,500.],.03)
    assert max(r['relative_power_residual'] for r in dyn)<1e-8
    try:RectangularPlate(a,b,4,4,m,'FREE').static()
    except ValueError:free_rejected=True
    else:raise AssertionError('Swobodna płyta nie ma statycznego rozwiązania poduniformp')
    result=dict(status='PLATE_AND_TIE_NUMERICAL_CONTROLS_NOT_MDF_BATCH_VALIDATION',element_rigid_modes=rigid,rigid_residuals=residual,
        navier_reference=reference,mesh_convergence=convergence,shear_locking=locking,rotational_edge_compliance_sequence_m3_pa=compliances,
        pair_controls=pair,bare_modes_hz=bare.tolist(),antisymmetric_modes_hz=antisym.tolist(),dynamic_power_controls=dyn,free_static_rejected=free_rejected,
        scope='Prostokątne liniowe płyty,hardSSSS/CCCC/obrotowe sprężyny i skończona łata ściągu. Nie pełna skrzynia,otwórfrontu ani model pękania/pełzania kleju.')
    (ROOT/'wyniki/p18_kontrole_MITC.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
