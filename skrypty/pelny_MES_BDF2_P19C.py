"""Odrębna integracja bez redukcji: BDF2 na pełnym MES z jednostronnym stykiem.

Przygotowana historia z ROM nie jest niezaleznym rozruchem. Kolejne okresy
sprawdzaja propagacje pelnego pola i zbieznosc czasu; nie waliduja materialu.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.integrate import trapezoid


def full_bdf2(full,reduced,trace,steps_per_cycle=512,cycles=3):
    w=full.omega;period=2*np.pi;dt=period/(w*steps_per_cycle);dtheta=w*dt
    end_theta=trace['theta'][-1]
    history=[]
    for theta in [end_theta-dtheta,end_theta]:
        y=trace['solution'].sol(theta);u,v,lag=reduced.decode(y)
        history.append((reduced.V@u,reduced.V@v,lag))
    qm,vm,lm=history[0];qn,vn,ln=history[1]
    D=full.D;weight=full.weights;z0=full.z0;spring0=full.spring0
    A=(9/(4*dt*dt)*full.M+3/(2*dt)*full.C+full.Ks).tocsc()
    ratio=2*dt/full.tau;lag_alpha=ratio/(3+ratio)
    kg=full.Kgas*(full.gamma-(full.gamma-1)*lag_alpha)
    H=full.H;last_mask=None;factor=None;zH=None;factorizations=0;maximum_residual=0.
    records=[];first_states=[];last_state=None
    for index in range(1,steps_per_cycle*cycles+1):
        theta=end_theta+index*dtheta;x,xp,xpp=reduced.drive(theta)
        vconst=(-4*qn+qm)/(2*dt)
        aconst=3/(2*dt)*vconst+(-4*vn+vm)/(2*dt)
        lag_const=(4*ln-lm)/(3+ratio)
        pconst=-kg*full.sd*x+full.Kgas*(full.gamma-1)*lag_const
        rhs=H*pconst-full.e*full.mm*w*w*xpp-full.M@aconst-full.C@vconst+D.T@(weight*spring0)
        q=2*qn-qm
        def energy(value):
            positive=np.maximum(z0+D@value,0)
            return float(.5*value@(A@value)+.5*kg*(H@value)**2+.5*np.dot(weight,positive*positive)-rhs@value)
        for iteration in range(24):
            gap=z0+D@q;active=gap>0
            residual=A@q+kg*H*(H@q)+D.T@(weight*np.maximum(gap,0))-rhs
            relative=float(np.linalg.norm(residual)/max(np.linalg.norm(rhs),1e-30))
            if relative<1e-10:break
            mask=np.packbits(active).tobytes()
            if mask!=last_mask:
                J=(A+D.T@sparse.diags(weight*active)@D).tocsc();factor=splu(J)
                zH=factor.solve(H);last_mask=mask;factorizations+=1
            # Dokladna eliminacja jednej galęzi gazu,bez gestego H*H.T.
            step0=factor.solve(-residual);step=step0-zH*(kg*(H@step0)/(1+kg*(H@zH)))
            E=energy(q);slope=float(residual@step);alpha=1.
            for _ in range(25):
                if energy(q+alpha*step)<=E+1e-4*alpha*slope+1e-12:break
                alpha*=.5
            q+=alpha*step
        else:raise RuntimeError('PelnyMES BDF2:brak zbieznosci styku w kroku '+str(index))
        maximum_residual=max(maximum_residual,relative)
        v=3/(2*dt)*q+vconst;acc=3/(2*dt)*v+(-4*vn+vm)/(2*dt)
        volume=full.sd*x+H@q;lag=lag_const+lag_alpha*volume
        p=-full.Kgas*(full.gamma*volume-(full.gamma-1)*lag)
        xd=w*xp;force=full.mm*(w*w*xpp+full.e@acc)-full.sd*p
        z=z0+D@q;delta=D@q
        U=.5*q@(full.Ks@q)+.5*np.dot(weight,np.maximum(z,0)**2-spring0**2)-np.dot(weight*spring0,delta)
        T=.5*v@(full.M@v)+full.mm*xd*(full.e@v)+.5*full.mm*xd*xd
        Ug=.5*full.Kgas*(volume*volume+(full.gamma-1)*(volume-lag)**2)
        data=dict(theta=theta,basket=float(q[-3]),pressure=float(p),energy=float(U+T+Ug),input_power=float(force*xd),
                  structural_loss=float(v@(full.C@v)),gas_loss=float(full.Kgas*(full.gamma-1)/full.tau*(volume-lag)**2),
                  open_fraction=float(sum(full.area*(z[:full.ng]<=0))/sum(full.area)),slack_bolts=int(sum(z[full.ng:]<=0)))
        records.append(data)
        qm,vm,lm=qn,vn,ln;qn,vn,ln=q,v,lag
        if index%steps_per_cycle==0:
            print('P19C fullBDF2',steps_per_cycle,'cycle',index//steps_per_cycle,'LU',factorizations,flush=True)
            if first_states:
                old=first_states[-1];dq=q-old[0];dv=v-old[1]
                periodic=float(np.sqrt((dq@(full.Kt@dq)+dv@(full.M@dv))/max(q@(full.Kt@q)+v@(full.M@v),1e-30)))
            else:periodic=None
            first_states.append((q.copy(),v.copy(),lag))
    data=records[-steps_per_cycle:];t=np.array([d['theta'] for d in data])/w
    last_previous=records[-steps_per_cycle-1] if len(records)>steps_per_cycle else records[0]
    series=[last_previous,*data];times=np.array([d['theta'] for d in series])/w
    power=np.array([d['input_power']-d['structural_loss']-d['gas_loss'] for d in series])
    energy=np.array([d['energy'] for d in series]);work=np.r_[0,np.cumsum((power[1:]+power[:-1])*np.diff(times)/2)]
    er=float(max(abs(energy-energy[0]-work))/max(trapezoid(abs(np.array([d['input_power'] for d in series])),times),max(abs(energy)),1e-30))
    phases={}
    # Nie dolaczamy konca okresu drugi raz; przesuniecie o1krok korygujemy faza.
    for name in ['basket','pressure']:
        values=np.array([d[name] for d in data]);fft=np.fft.rfft(values)/len(values)
        ph=np.sqrt(2)*fft[1:11]*np.exp(-1j*np.arange(1,11)*dtheta)
        phases[name]=dict(mean=float(fft[0].real),harmonics_rms_real=ph.real.tolist(),harmonics_rms_imag=ph.imag.tolist())
    result=dict(status='FULL_FE_PROPAGATION_FROM_PREPARED_ROM_HISTORY',full_dof=full.M.shape[0],steps_per_cycle=steps_per_cycle,cycles=cycles,
                maximum_newton_relative_residual=maximum_residual,LU_factorizations=factorizations,last_period_distance=periodic,
                relative_integrated_energy_residual=er,basket_peak_m=max(abs(d['basket']) for d in data),pressure_rms_pa=float(np.sqrt(np.mean([d['pressure']**2 for d in data]))),
                mean_open_area_fraction=float(np.mean([d['open_fraction'] for d in data])),max_open_area_fraction=max(d['open_fraction'] for d in data),
                max_slack_bolts=max(d['slack_bolts'] for d in data),phases=phases,
                scope='BDF2,bez redukcji przestrzeni;przygotowana historia nie jest niezaleznym zimnym rozruchem.')
    return result,data,dict(q=qn,v=vn,lag=ln)
