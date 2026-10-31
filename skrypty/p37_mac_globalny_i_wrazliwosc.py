#!/usr/bin/env python3
"""P37: true whole-cabinet Q4 numerical MAC (18 modes) and material sensitivity.
Research diagnostic ONLY. This imports the historic P33B and P33C solvers
and temporarily adds eigenvector export without changing source/history.
Requirements: numpy, scipy; run from repository root:
python skrypty/p37_mac_globalny_i_wrazliwosc.py --out wyniki/p37_globalny_mac_wrazliwosc.json
"""
import argparse, json, math, inspect, numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import linear_sum_assignment
import p33b_powlokowy_fem as gb
import p33c_hourglass_audyt as stab

# Read-only augmentation of the historical global solver.
src=inspect.getsource(gb.global_mesh)
assert 'lam=eigsh(' in src and 'return_eigenvectors=False' in src
src=src.replace('lam=eigsh(', 'lam,vec=eigsh(').replace('return_eigenvectors=False','return_eigenvectors=True')
anchor='f=np.sort(np.sqrt(np.maximum(0,lam))/(2*math.pi))'
assert anchor in src, 'P33B frequency calculation changed; review before rerun'
src=src.replace(anchor, 'f=np.sqrt(np.maximum(0,lam))/(2*math.pi); order=np.argsort(f); f=f[order]; vec=vec[:,order]')
marker="return {'mesh':mesh"
assert marker in src, 'P33B return statement changed; review before rerun'
src=src.replace(marker, "return {'modal_coords':pts[active], 'modal_tags':[name for ix in active for name,data in tab.items() if ix in data['node'].values()], 'modal_shapes':vec, 'modal_freqs':f, 'mesh':mesh")
exec(src, gb.__dict__)
global_solver=gb.__dict__['global_mesh']

def solve(gamma=.001,mesh=.11,E=2.1e9,rho=730.,kt=3e7,kr=3e3):
    gb.E=E;gb.rho=rho;stab.E=E;stab.rho=rho
    gb.shell_element=lambda lx,ly,t,cut=1:stab.element(lx,ly,t,gamma)*cut
    return global_solver(mesh=mesh,kTrans=kt,kRot=kr,driverMass=15,insertMass=8,brace=True)

def sample_physical_modes(run):
    xyz=run['modal_coords']; names=np.asarray(run['modal_tags'])
    vel=run['modal_shapes'].reshape(len(xyz),6,-1)[:,:3,:]
    faces=[('front',1.020,.500,0,2),('back',1.020,.500,0,2),
           ('top',1.020,.425,0,1),('bottom',1.020,.425,0,1),
           ('left',.425,.500,1,2),('right',.425,.500,1,2)]
    out=[];weights=[]
    for name,L,H,ax,ay in faces:
        mask=names==name
        tree=cKDTree(xyz[mask][:,[ax,ay]])
        field=vel[mask]
        for a in np.linspace(0,L,7)[1:-1]:
            for b in np.linspace(0,H,7)[1:-1]:
                if name=='front' and (a-.231)**2+(b-.250)**2<(.3558/2+.045)**2: continue
                if name in ('top','bottom') and (abs(a-.426)<.04 or abs(a-.701)<.04):continue
                distance,index=tree.query([a,b],k=4)
                w=1/(distance**2+1e-8);w/=w.sum()
                out.append(np.einsum('i,ijm->jm',w,field[index]))
                weights.append(L*H/25)
    A=np.asarray(out)*np.sqrt(np.asarray(weights))[:,None,None]
    u=A.reshape(-1,A.shape[2])
    norm=np.linalg.norm(u,axis=0)
    assert np.all(norm>0)
    return u/norm

def track(a,b):
    MAC=np.square(sample_physical_modes(a).T@sample_physical_modes(b))
    idsA,idsB=linear_sum_assignment(-MAC)
    result=[]
    for i,j in zip(idsA,idsB):
        f1=float(a['modal_freqs'][i]);f2=float(b['modal_freqs'][j])
        result.append({'mode_ref':int(i+1),'mode_target':int(j+1),
          'f_ref_Hz':round(f1,4),'f_target_Hz':round(f2,4),
          'MAC':round(float(MAC[i,j]),6),
          'delta_f_percent':round(100*(f2/f1-1),3)})
    return result

def run():
    cases=[('coarse',{'mesh':.15}),('reference',{'mesh':.11}),
           ('fine',{'mesh':.085}),('gamma01',{'mesh':.11,'gamma':.01}),
           ('soft',{'mesh':.11,'kt':3e6,'kr':3e2}),
           ('stiff',{'mesh':.11,'kt':3e8,'kr':3e4})]
    models={};summ=[]
    for name,kwargs in cases:
        z=solve(**kwargs);models[name]=z
        summ.append({'id':name,'step_mm':z['mesh']*1000,'ndof':z['ndof'],
          'f1_to_f8_Hz':[round(float(v),5) for v in z['modal_freqs'][:8]],
          'max_ugięcie_um':round(z['max_static_disp_um'],5)})
    comparisons=[]
    for a,b in [('coarse','reference'),('reference','fine'),('reference','gamma01'),
                ('reference','soft'),('reference','stiff')]:
        match=track(models[a],models[b]);scores=[x['MAC'] for x in match]
        comparisons.append({'a':a,'b':b,'avg_MAC':round(float(np.mean(scores)),6),
          'min_MAC':min(scores),'below_0_90':sum(x<.9 for x in scores),
          'reordered':sum(x['mode_ref']!=x['mode_target'] for x in match),
          'matches':match})
    sensit=[]
    for par,fac in [('E',(.9,1.1)),('rho',(.9,1.1)),('kt',(.1,10)),('kr',(.1,10))]:
        q=[]
        for factor in fac:
            kw={'E':2.1e9,'rho':730.,'kt':3e7,'kr':3e3}
            kw[par]*=factor
            z=solve(mesh=.11,**kw)
            matches=track(models['reference'],z)
            q.append({'factor':factor,'f1':float(z['modal_freqs'][0]),
                      'max_ugięcie_um':z['max_static_disp_um'],
                      'first_five_MAC':[m['MAC'] for m in matches[:5]]})
        denom=math.log(fac[1]/fac[0])
        sensit.append({'parameter':par,'low':q[0],'high':q[1],
          'elasticity_f1':round(math.log(q[1]['f1']/q[0]['f1'])/denom,6),
          'elasticity_displacement':round(math.log(q[1]['max_ugięcie_um']/q[0]['max_ugięcie_um'])/denom,6)})
    assert len(models)==6 and len(sensit)==4
    assert abs(models['reference']['max_static_disp_um']-83.09005)<3
    return {'study':'P37','date':'2026-11-01','full_global_models':14,'modal_modes_each':18,
      'reference_material':{'MDF_E_GPa':2.1,'rho':730,'joint_trans_Nm2':3e7,
      'joint_rot_N':3e3,'gamma':.001},
      'models':summ,'MAC_comparisons':comparisons,'material_joint_sensitivity':sensit,
      'warnings':['P33B numerical shell model remains UNVALIDATED, with nonconformal driver hole, idealized joints, feet and braces.',
       'Mode tracking uses weighted displacement samples at common points, NOT an exact mass-MAC of identical finite elements.',
       'Near-degenerate modes need cluster/subspace MAC; low MAC of high modes can be sampling or mode-truncation artefact.',
       'Stabilization gamma is arbitrary numerical regularization; modes are not proven structural resonances of a real cabinet.',
       'Elasticities are finite differences in the model, not confidence intervals from MDF or glue measurements.',
       'No release for CAD/CNC, real SPL, THD or safety certification.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='wyniki/p37_globalny_mac_wrazliwosc_20261101.json')
    args=parser.parse_args()
    data=run()
    with open(args.out,'w',encoding='utf-8') as f:json.dump(data,f,indent=2,ensure_ascii=False)
    print(json.dumps({'global_models':data['full_global_models'],
        'comparisons':[{k:v for k,v in s.items() if k!='matches'} for s in data['MAC_comparisons']],
        'sensitivities':[{k:v for k,v in s.items() if k not in ('low','high')} for s in data['material_joint_sensitivity']]},indent=2))
