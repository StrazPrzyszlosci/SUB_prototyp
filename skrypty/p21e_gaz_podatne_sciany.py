"""P21E: reciprocal low-frequency gas / compliant-panel model.
Run from repository root: OPENBLAS_NUM_THREADS=1 python skrypty/p21e_gaz_podatne_sciany.py
A two-DOF modal surrogate, NOT full spatial FEM, measured panel data or THD.
"""
from pathlib import Path
import csv, json, hashlib, platform
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'dane/konfiguracje/p21e_podatne_sciany.json'
POOL=ROOT/'dane/przetworniki/pula_rozszerzona.json'
OUT=ROOT/'wyniki'

def parameters(model,cfg):
    rho,c=cfg['rho_kg_m3'],cfg['sound_speed_m_s']
    sd=model['sd_cm2']*1e-4
    cms=model['vas_l']*1e-3/(rho*c*c*sd*sd)
    w0=2*np.pi*model['fs_hz']
    m=1/(cms*w0*w0)
    rm=w0*m/model['qms']
    bl=np.sqrt(w0*m*model['re_ohm']/model['qes'])
    return sd,cms,m,rm,bl,model['re_ohm'],model['le_mh']*1e-3

def solve(f,vb,compliance,fpanel,zeta,driver,cfg):
    sd,cms,m,rm,bl,re,le=parameters(driver,cfg)
    w=2*np.pi*f
    cg=(vb/1000)/(cfg['rho_kg_m3']*cfg['sound_speed_m_s']**2)
    cwall=compliance/(1-(f/fpanel)**2+1j*2*zeta*(f/fpanel))
    zbox=sd*sd/(1j*w*(cg+cwall))
    zbox_rigid=sd*sd/(1j*w*cg)
    zm=rm+1j*w*m+1/(1j*w*cms)

    def electric(z):
        ze=re+1j*w*le+bl*bl/z
        i=1/ze
        vel=bl*i/z
        return i,vel,ze

    ir,vr,_=electric(zm+zbox_rigid)
    i,v,ze=electric(zm+zbox)
    p=sd*v/(1j*w*(cg+cwall))
    qwall=cwall*p

    kw=1/compliance
    mw=kw/(2*np.pi*fpanel)**2
    rw=2*zeta*np.sqrt(kw*mw)
    zwall=kw-w*w*mw+1j*w*rw

    # Cross-check 1: two algebraically equivalent expressions for gas load.
    zport=sd*sd/(1j*w*(cg+1/zwall))
    port_residual=abs(zport-zbox)/max(abs(zbox),1e-50)

    # Cross-check 2: independent 2x2 stiffness/volume matrix with current
    # eliminated from Ze*i + BL*v = 1 V RMS.
    ze_block=re+1j*w*le
    A=np.array([[1j*w*zm+sd*sd/cg+bl*bl*1j*w/ze_block, -sd/cg],
                [-sd/cg, 1/cg+zwall]],dtype=complex)
    x2,y2=np.linalg.solve(A,np.array([bl/ze_block,0],dtype=complex))
    matrix_residual=abs(1j*w*x2-v)/max(abs(v),1e-50)

    return dict(v_gain_db=float(20*np.log10(abs(v/vr))),
        current_gain_db=float(20*np.log10(abs(i/ir))),
        p_gain_db=float(20*np.log10(abs(p/(sd*vr/(1j*w*cg))))),
        rigid_speed_m_s_V=float(abs(vr)),elastic_speed_m_s_V=float(abs(v)),
        box_mechanical_resistance_Ns_m=float(np.real(zbox)),
        electrical_impedance_real_ohm=float(np.real(ze)),
        wall_loss_rms_W=float(rw*(w*abs(qwall))**2),
        port_residual=float(port_residual),
        direct_matrix_residual=float(matrix_residual),
        gas_compliance_m3_Pa=float(cg),wall_compliance_abs_m3_Pa=float(abs(cwall)))

def main():
    cfg=json.loads(CFG.read_text());OUT.mkdir(exist_ok=True)
    names={d['model']['name']:d['model']
           for d in json.loads(POOL.read_text())['drivers']}
    rows=[]
    for name in cfg['candidates']:
      for vb in cfg['volumes_l']:
       for sf in cfg['compliance_scale']:
        for fpanel in cfg['panel_modes_hz']:
         for f in np.arange(cfg['frequency_start_hz'],
                            cfg['frequency_end_hz']+.0001,
                            cfg['frequency_step_hz']):
            cw=cfg['one_panel_compliance_m3_Pa']*cfg['panel_count']*sf
            r=solve(f,vb,cw,fpanel,cfg['damping_ratio'],names[name],cfg)
            rows.append(dict(candidate=name,volume_l=vb,compliance_scale=sf,
                panel_mode_hz=fpanel,frequency_hz=float(f),**r))

    path=OUT/'p21e_podatne_sciany.csv'
    with path.open('w',newline='') as h:
        wr=csv.DictWriter(h,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)

    err=max(r['port_residual'] for r in rows)
    independent_error=max(r['direct_matrix_residual'] for r in rows)
    bad=sum(r['box_mechanical_resistance_Ns_m']<-1e-8 or
            r['electrical_impedance_real_ohm']<=0 for r in rows)
    assert err<2e-12,err
    assert independent_error<2e-12,independent_error
    assert bad==0,bad

    static=[]
    for vb in cfg['volumes_l']:
        cg=(vb/1000)/(cfg['rho_kg_m3']*cfg['sound_speed_m_s']**2)
        cw=cfg['one_panel_compliance_m3_Pa']*cfg['panel_count']
        static.append(dict(volume_l=vb,compliance_ratio=cw/cg,
           reduction_air_stiffness_pct=100*(1-cg/(cg+cw)),
           equivalent_added_l=cw*cfg['rho_kg_m3']*cfg['sound_speed_m_s']**2*1000))
    summary={'n':len(rows),'independent_port_formula_error_max':err,
             'direct_2x2_matrix_error_max':independent_error,
             'nonpassive_cases':bad,'static_equivalents':static,
             'results_by_candidate':{},'model':'reduced reciprocal gas-panel; not spatial FEM'}
    for name in cfg['candidates']:
        target=[r for r in rows if r['candidate']==name]
        nom=[r for r in target if r['volume_l']==120 and
             r['compliance_scale']==1 and
             r['panel_mode_hz']==cfg['reference_panel_mode_hz']]
        summary['results_by_candidate'][name]={
            'scan_min_gain_db':min(r['v_gain_db'] for r in target),
            'scan_max_gain_db':max(r['v_gain_db'] for r in target),
            'nominal_min_gain_db':min(r['v_gain_db'] for r in nom),
            'nominal_max_gain_db':max(r['v_gain_db'] for r in nom),
            'nominal_20_40_80_db':{str(f):next(r['v_gain_db']
               for r in nom if r['frequency_hz']==f) for f in (20,40,80)}}
    output=OUT/'p21e_podsumowanie.json'
    output.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    files=[CFG,POOL,Path(__file__),path,output]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files}
    (OUT/'p21e_manifest.json').write_text(json.dumps({
        'python':platform.python_version(),'numpy':np.__version__,
        'files':hashes},indent=2)+'\n')
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
