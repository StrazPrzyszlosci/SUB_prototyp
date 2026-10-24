"""N7: wykonany eksperyment z4przetwornikami,6Vb,4przeciekami i3geometriami."""
import csv,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
from model_subwoofera import Driver, RHO, C
from model_nieszczelnosci import leakage_response

ROOT=Path(__file__).resolve().parents[1]


def main():
    drivers=[Driver(**r['model']) for r in json.loads((ROOT/'dane/przetworniki/kandydaci.json').read_text())['drivers']]
    freqs=np.array([20.,25.,31.5,40.,63.,80.])
    rows=[]
    geoms={'rowne_drogi':(0.,0.,0.),'przeciek_za_membrana_35cm':(0.,0.,-.35),'przeciek_z_boku_35cm':(.35,0.,0.)}
    for d in drivers:
        for vb in (30,45,60,80,100,120):
            for label,pos in geoms.items():
                sealed=leakage_response(d,vb,freqs,0.,vrms=2.83,leak=pos)
                for fl in (0.,1.,3.,10.):
                    out=leakage_response(d,vb,freqs,fl,vrms=2.83,leak=pos)
                    for i,f in enumerate(freqs):
                        rows.append({'driver':d.name,'vb_net_l':vb,'fleak_hz':fl,'geometry':label,'f_hz':f,
                          'voltage_rms':2.83,'distance_membrane_m':1.,'spl_4pi_total_rms_db':out['spl_4pi_db'][i],
                          'delta_from_sealed_db':out['spl_4pi_db'][i]-sealed['spl_4pi_db'][i],
                          'membrane_x_peak_mm':out['x_peak_m'][i]*1000,
                          'x_ratio_to_sealed':out['x_peak_m'][i]/sealed['x_peak_m'][i],
                          'current_rms_a':out['i_rms_a'][i],'leak_loss_w':out['p_leak_loss_w'][i],
                          'total_pressure_phase_deg':np.angle(out['p_total_pa'][i],deg=True),
                          'radiation_diagnostic_w':out['radiation_diagnostic_w'][i],
                          'energy_residual_w':out['energy_residual_w'][i]})
    with (ROOT/'wyniki/n7_pasma.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Stały przeciek fizyczny Ra przy zmianie Vb: odrębny eksperyment.
    # Te same fleak dla różnych Vb nie reprezentują tej samej szczeliny.
    fixed_ra=[]
    thresholds=[]
    guard=np.geomspace(20,80,1001)
    for d in drivers:
        for vb in (30,45,60,80,100,120):
            cab=vb*1e-3/(RHO*C*C)
            for ref_fl in (1.,3.,10.):
                ra=1/(2*np.pi*ref_fl*(.1/(RHO*C*C)))
                actual_fl=1/(2*np.pi*ra*cab)
                out=leakage_response(d,vb,freqs,actual_fl,vrms=2.83)
                base=leakage_response(d,vb,freqs,0.,vrms=2.83)
                for i,freq in enumerate(freqs):
                    fixed_ra.append({'driver':d.name,'vb_net_l':vb,'ra_pa_s_m3':ra,
                        'reference_fleak_at_100l_hz':ref_fl,'actual_fleak_hz':actual_fl,
                        'f_hz':freq,'delta_from_sealed_db':out['spl_4pi_db'][i]-base['spl_4pi_db'][i],
                        'x_peak_mm':out['x_peak_m'][i]*1000,'geometry':'rowne_drogi'})
            base=leakage_response(d,vb,guard,0.)
            for tolerance in (.1,.5,1.):
                # To progi pomocnicze eksperymentu, a nie zatwierdzona specyfikacja.
                def error(fl):
                    x=leakage_response(d,vb,guard,fl)
                    return float(np.max(abs(x['spl_4pi_db']-base['spl_4pi_db'])))
                fl_limit=brentq(lambda fl:error(fl)-tolerance,0.,30.,xtol=1e-10)
                ra_min=1/(2*np.pi*fl_limit*cab)
                refined=np.geomspace(20,80,2001)
                refined_error=float(np.max(abs(leakage_response(d,vb,refined,fl_limit)['spl_4pi_db']-
                                               leakage_response(d,vb,refined,0.)['spl_4pi_db'])))
                thresholds.append({'driver':d.name,'vb_net_l':vb,'screening_tolerance_db':tolerance,
                    'fleak_limit_hz':fl_limit,'ra_min_pa_s_m3':ra_min,'tau_min_s':ra_min*cab,
                    'guard_grid_error_db':error(fl_limit),'refined_grid_error_db':refined_error,
                    'geometry':'rowne_drogi','status':'prog_scenariusza_nie_zatwierdzone_wymaganie'})
    for name,data in [('n7_stala_rezystancja.csv',fixed_ra),('n7_kryteria_szczelnosci.csv',thresholds)]:
        with (ROOT/'wyniki'/name).open('w',newline='',encoding='utf-8') as h:
            w=csv.DictWriter(h,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    f=np.geomspace(.1,200,2200)
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    for d,ax in zip(drivers,axes.flat):
        vb=100 if '390' in d.name else 60
        base=leakage_response(d,vb,f,0.)
        for fl in (1.,3.,10.):
            out=leakage_response(d,vb,f,fl)
            ax.semilogx(f,out['spl_4pi_db']-base['spl_4pi_db'],label=f'fleak={fl:g}Hz')
        ax.set(title=f'{d.name}, {vb}l',xlabel='Częstotliwość [Hz]',ylabel='SPL całkowite − szczelne [dB]',xlim=(1,200))
        ax.grid(True,which='both',alpha=.3);ax.legend()
    fig.suptitle('N7: przeciek rezystancyjny, jednakowe drogi, wspólne2,83Vrms; model4π')
    plt.tight_layout();plt.savefig(ROOT/'wyniki/07_nieszczelnosc.png',dpi=160);plt.savefig(ROOT/'wyniki/07_nieszczelnosc.svg');plt.close()
    d=drivers[1];vb=100
    fig,axes=plt.subplots(2,1,figsize=(10,8))
    for label,pos in geoms.items():
        out=leakage_response(d,vb,f,10.,leak=pos)
        axes[0].semilogx(f,out['spl_4pi_db'],label=label)
    for fl in (0.,1.,3.,10.):
        out=leakage_response(d,vb,f,fl)
        axes[1].semilogx(f,out['x_peak_m']*1000,label=f'fleak={fl:g}Hz')
    axes[0].set(ylabel='SPL RMS [dB],4π/1m',title='Geometria sumowania ciśnień; to nie model pokoju')
    axes[1].set(xlabel='Częstotliwość [Hz]',ylabel='Wychylenie szczytowe [mm]',title='Ruch niezależny od kierunku i punktu obserwacji')
    for ax in axes:ax.grid(True,which='both',alpha=.3);ax.legend()
    plt.tight_layout();plt.savefig(ROOT/'wyniki/08_przeciek_geometria_i_ruch.png',dpi=160);plt.savefig(ROOT/'wyniki/08_przeciek_geometria_i_ruch.svg');plt.close()
    selected=[r for r in rows if r['vb_net_l']==(100 if '390' in r['driver'] else 60)
              and r['geometry']=='rowne_drogi' and r['f_hz'] in (20.,40.) and r['fleak_hz']==10.]
    summary={'status':'SYMULACJA_N7_NIE_IDENTYFIKACJA_RZECZYWISTEJ_SKRZYNI','band_rows':len(rows),
             'constant_resistance_band_rows':len(fixed_ra),'screening_thresholds':len(thresholds),
             'driver_box_leak_geometry_cases':len(rows)//6,'selected_cases':selected,
             'interpretation':'Radiacja jest diagnostyczna, bez zamknięcia jej reakcji w bilansie T/S; f_leak nie wyznacza powierzchni szczeliny.'}
    (ROOT/'wyniki/n7_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print('N7:',len(rows),'rekordów pasmowych,',len(rows)//6,'konfiguracji.')
    for r in selected:print(r['driver'],r['f_hz'],round(r['delta_from_sealed_db'],4),round(r['x_ratio_to_sealed'],5))


if __name__=='__main__':main()
