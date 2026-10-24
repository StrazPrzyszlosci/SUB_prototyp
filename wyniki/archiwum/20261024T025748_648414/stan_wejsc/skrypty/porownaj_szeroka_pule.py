"""Selekcja fizyczna szerokiej puli, przy wspólnym V/I bez fałszywej termiki.

Pe o różnych protokołach nie służy jako wspólny limit cieplny. Wyniki są
granicami liniowych modeli, bez twierdzenia o THD lub spełnieniu całego briefu.
"""
import csv,json,os,hashlib
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_subwoofera import Driver,alignment,response,RHO,P_REF
from model_nieszczelnosci import leakage_response

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'dane/przetworniki/pula_rozszerzona.json'


def write_table(name,rows):
    with (ROOT/'wyniki'/name).open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    data=json.loads(CAT.read_text())
    volumes=np.arange(20.,151.)
    probes=np.array([20.,25.,31.5,40.,63.,80.])
    ratings=[('V40_I12',40.,12.),('V60_I20',60.,20.)]
    band,summary,ts_audit,leaks=[],[],[],[]
    fig,axes=plt.subplots(1,2,figsize=(15,max(6,.29*len(data['drivers']))))
    fplot=np.geomspace(10,100,400)
    for driver_index,raw in enumerate(data['drivers']):
        d=Driver(**raw['model'])
        vd=d.sd*d.xmax_mm  # m² * mm = litre
        # Niezależna od obudowy granica samego ruchu; monopól2π/1m,RMS.
        p20=RHO*(2*np.pi*20)**2*d.sd*(d.xmax_mm*1e-3/np.sqrt(2))/(2*np.pi)
        ceiling20=20*np.log10(p20/P_REF)
        x_for_100= P_REF*10**(100/20)*2*np.pi*np.sqrt(2)/(RHO*(2*np.pi*20)**2*d.sd)*1000
        optimum=(d.vas_l/((1/np.sqrt(2)/d.qts)**2-1)) if d.qts<1/np.sqrt(2) else None
        rows_for_driver=[]
        for vb in volumes:
            fc,qtc,f3=alignment(d,vb)
            one=response(d,vb,probes)
            for label,vmax,imax in ratings:
                for fraction in (.7,1.):
                    limits=np.array([fraction*d.xmax_mm*1e-3/one['x_peak_m'],
                                     np.full_like(probes,vmax),imax/one['i_rms']])
                    voltage=limits.min(axis=0)
                    out=response(d,vb,probes,voltage)
                    assert np.all(out['x_peak_m']<=fraction*d.xmax_mm*1e-3*(1+1e-12))
                    assert np.all(out['i_rms']<=imax*(1+1e-12))
                    row={'candidate_id':raw['candidate_id'],'driver':d.name,'vb_net_l':vb,'amp_scenario':label,
                         'fraction_of_catalog_xmax_not_thd':fraction,'fc_hz':fc,'qtc':qtc,'f3_hz':f3}
                    for i,f in enumerate(probes):
                        row[f'linear_spl_2pi_1m_rms_{f:g}hz_db']=out['spl_rms_db'][i]
                        row[f'voltage_{f:g}hz_rms']=voltage[i]
                        row[f'current_{f:g}hz_rms']=out['i_rms'][i]
                        row[f'x_peak_{f:g}hz_mm']=out['x_peak_m'][i]*1000
                        row[f'active_limit_{f:g}hz']=['catalog_x','amp_voltage','amp_current'][np.argmin(limits[:,i])]
                    band.append(row);rows_for_driver.append(row)
        picked=[r for r in rows_for_driver if r['vb_net_l']==100 and r['amp_scenario']=='V40_I12' and r['fraction_of_catalog_xmax_not_thd']==1.][0]
        best20=max(r['linear_spl_2pi_1m_rms_20hz_db'] for r in rows_for_driver if r['amp_scenario']=='V40_I12' and r['fraction_of_catalog_xmax_not_thd']==1.)
        item={'candidate_id':raw['candidate_id'],'manufacturer':raw['manufacturer'],'driver':d.name,
              'nominal_size_class_in':raw['nominal_size_class_in'],'qts_derived':d.qts,'vd_catalog_l':vd,
              'motion_only_20hz_spl_rms_2pi_1m_db':ceiling20,
              'x_peak_for_illustrative_100db_20hz_mm':x_for_100,
              'vbox_optimum_F3_only_l':optimum,'best_20hz_40v12a_in_20_150l_db':best20,
              'at100l_20hz_40v12a_db':picked['linear_spl_2pi_1m_rms_20hz_db'],
              'at100l_40hz_40v12a_db':picked['linear_spl_2pi_1m_rms_40hz_db'],
              'calculation_status':raw['calculation_status'],'forum_status':raw['forum_status'],
              'role':raw['role'],'source_url':raw['url']}
        summary.append(item)
        for key,value in [('qts',d.qts),('mms_g',d.mms*1000),('cms_mm_n',d.cms*1000),('bl_tm',d.bl)]:
            if key in raw['catalog_extra']:
                catalog=raw['catalog_extra'][key]
                delta=100*(value/catalog-1)
                ts_audit.append({'candidate_id':raw['candidate_id'],'driver':d.name,'parameter':key,'catalog':catalog,
                                 'derived':value,'relative_delta_pct':delta,'review':abs(delta)>10})
        sealed=leakage_response(d,100,probes,0.)
        for fl in (1.,3.,10.):
            leak=leakage_response(d,100,probes,fl)
            for i,f in enumerate(probes):
                leaks.append({'candidate_id':raw['candidate_id'],'driver':d.name,'vb_net_l':100,'fleak_hz':fl,
                              'f_hz':f,'delta_total_spl_4pi_db':leak['spl_4pi_db'][i]-sealed['spl_4pi_db'][i],
                              'x_ratio':leak['x_peak_m'][i]/sealed['x_peak_m'][i]})
        # Wspólny100l jest eksperymentem porównawczym, nie zatwierdzonym litrażem.
        base=response(d,100,fplot)
        v=np.minimum(d.xmax_mm*1e-3/base['x_peak_m'],np.minimum(40.,12./base['i_rms']))
        out=response(d,100,fplot,v)
        axes[0].semilogx(fplot,out['spl_rms_db'],label=raw['candidate_id'],
                         color=plt.cm.turbo(driver_index/max(1,len(data['drivers'])-1)),
                         linestyle='--' if driver_index>=10 else '-')
    ranked=sorted(summary,key=lambda r:r['motion_only_20hz_spl_rms_2pi_1m_db'])
    y=np.arange(len(ranked))
    axes[1].barh(y,[r['motion_only_20hz_spl_rms_2pi_1m_db'] for r in ranked],color='#3b6e8c')
    axes[1].set_yticks(y,[r['candidate_id']+' '+r['driver'] for r in ranked],fontsize=7)
    axes[1].set(xlabel='SPL RMS20Hz z samego Sd·Xmax [dB],2π/1m',title='Różne definicjeXmax; bez THD i termiki')
    axes[0].set(xlabel='Częstotliwość [Hz]',ylabel='Granica modeluSPL RMS [dB],2π/1m',title='Wspólne100l,40Vrms,12Arms; bez limituPe')
    axes[0].grid(True,which='both',alpha=.3)
    axes[0].legend(fontsize=6,ncol=2,loc='lower right')
    plt.tight_layout();plt.savefig(ROOT/'wyniki/09_szeroka_pula.png',dpi=180);plt.savefig(ROOT/'wyniki/09_szeroka_pula.svg');plt.close()
    write_table('pula_objetosci_i_naped.csv',band)
    write_table('pula_podsumowanie.csv',summary)
    write_table('pula_spojnosc_ts.csv',ts_audit)
    write_table('pula_nieszczelnosci.csv',leaks)
    result={'status':'POROWNANIE_WSTEPNE_NIE_FINALNY_WYBOR','data_sha256':hashlib.sha256(CAT.read_bytes()).hexdigest(),
            'driver_count':len(summary),'manufacturer_count':len(set(r['manufacturer'] for r in summary)),
            'volume_grid_l':{'from':20,'to':150,'step':1},'scenarios':len(band),
            'nominal_motion_leaders':[{'candidate_id':r['candidate_id'],'driver':r['driver'],
              'ceiling20_rms_db':r['motion_only_20hz_spl_rms_2pi_1m_db']} for r in sorted(summary,key=lambda r:r['motion_only_20hz_spl_rms_2pi_1m_db'],reverse=True)[:5]],
            'limitations':['Nie podano progówTHD ani zmierzonej kompresji.','Pe różnych protokołów nie potraktowano jako wspólnej granicy termicznej.',
                           '40/60Vrms i12/20Arms to scenariusze, nie wybrany wzmacniacz.',
                           'Zakres20–150l to obliczenia i analityczny warunekF3, nie gwarancja najlepszego litrażu.',
                           '0.7Xmax to scenariusz ruchu, nie gwarancja niskich zniekształceń.']}
    (ROOT/'wyniki/pula_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
