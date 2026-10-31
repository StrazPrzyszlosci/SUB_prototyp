"""Decision-focused error scales and plots for P21D; retain near-zero flags."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pole_zintegrowanej_geometrii_P21D import O,MED,candidates

def main():
 s=json.loads((O/'p21d_wyniki.json').read_text());fine=json.loads((O/'p21d_dogeszczenie.json').read_text())['rows']
 d={cid:d for cid,pid,d,c in candidates()}['C02'];om=2*np.pi*80
 stats=[]
 def vel(z):
  zm=d.rms+1j*om*d.mms+1/(1j*om*d.cms)+d.sd**2*z
  return d.bl/(zm*(d.re_ohm+1j*om*d.le_mh*.001)+d.bl**2)
 for r in fine:
  if r['step_m']!=.018:continue
  z=complex(r['Z_real'],r['Z_imag'])
  prior=next(q for q in fine if q['configuration']==r['configuration'] and q['proxy']==r['proxy'] and q['step_m']==.025)
  zp=complex(prior['Z_real'],prior['Z_imag']);scale=r['compliance_reference_magnitude']
  stats.append(dict(configuration=r['configuration'],proxy=r['proxy'],dof=r['dof'],Z_real=z.real,Z_imag=z.imag,
           last_relative_port_change=abs(zp/z-1),last_change_scaled_to_0D=abs(zp-z)/scale,
           last_velocity_magnitude_change_dB=20*np.log10(abs(vel(zp)/vel(z)))))
 shapes=[]
 for name in ['150','120','100']:
  a=next(q for q in fine if q['configuration']==name and q['proxy']=='A' and q['step_m']==.018)
  b=next(q for q in fine if q['configuration']==name and q['proxy']=='B' and q['step_m']==.018)
  za=complex(a['Z_real'],a['Z_imag']);zb=complex(b['Z_real'],b['Z_imag'])
  shapes.append(dict(configuration=name,relative_port_change=abs(zb/za-1),change_scaled_to_0D=abs(zb-za)/a['compliance_reference_magnitude'],velocity_magnitude_change_dB=20*np.log10(abs(vel(zb)/vel(za)))))
 summary=dict(fine_mesh_statistics=stats,motor_shape_statistics=shapes,
    max_fine_port_change_scaled_to_0D=max(q['last_change_scaled_to_0D'] for q in stats),
    max_abs_fine_velocity_change_dB=max(abs(q['last_velocity_magnitude_change_dB']) for q in stats),
    max_abs_motor_shape_velocity_change_dB=max(abs(q['velocity_magnitude_change_dB']) for q in shapes),
    all_primary_input_power_balance_max=max(q['input_power_balance_relative'] for q in s['coupled']),
    scope='Refinement witnesses only C02 80Hz. No accuracy certificate for C11/C06 or continuous band.')
 (O/'p21d_podsumowanie.json').write_text(json.dumps(summary,indent=2))
 fig,axs=plt.subplots(1,3,figsize=(15,4.5))
 for cid in ['C02','C11','C06']:
  rows=[r for r in s['coupled'] if r['candidate']==cid and r['mass_convention']==0]
  for name in ['150','120','100']:
   q=[r for r in rows if r['configuration']==name]
   axs[0].plot([r['f_hz'] for r in q],[r['acceleration_vs_0D_dB'] for r in q],label=f'{cid}/{name}')
 axs[0].set(xlabel='f [Hz]',ylabel='Zmiana przyspieszenia względem 0D [dB]',title='Model pierwotny: 35 mm, proxy A')
 axs[0].legend(fontsize=6,ncol=3)
 for name in ['150','120','100']:
  for proxy in ['A','B']:
   q=[r for r in fine if r['configuration']==name and r['proxy']==proxy]
   axs[1].plot([r['step_m']*1000 for r in q],[r['Z_imag'] for r in q],'o-',label=f'{name}/{proxy}')
 axs[1].set(xlabel='Maksymalny krok siatki [mm]',ylabel='Im(Z) [Pa s/m³]',title='80 Hz: zmiana przy drobniejszych siatkach');axs[1].legend(fontsize=7,ncol=2)
 axs[2].bar([q['configuration'] for q in shapes],[q['velocity_magnitude_change_dB'] for q in shapes]);axs[2].set(xlabel='Stan objętości nominalnej [l]',ylabel='Zmiana amplitudy prędkości [dB]',title='Dwa zastępcze kosze po 5 l, 80 Hz')
 for ax in axs:ax.grid(alpha=.3)
 fig.tight_layout();fig.savefig(O/'101_P21D_komora_i_naped.png',dpi=160)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
