"""Galerkin + jednostronne sprezyny + port ruchu wzglednego i gaz z pamiecia.

SI w mechanice; integrator uzywa czasu theta=omega*t i skalowanego stanu.
Nie pomijamy offsetu docisku, przekroju stozka ani sprzezenia kinetycznego.
"""
import csv
import json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.linalg import eigh
from scipy.sparse.linalg import eigsh,splu
from scipy.integrate import solve_ivp,trapezoid
from model_frontu_z_otworem_P18B import PlateMaterial,FrontWithHole,MountedFront
from analiza_styku_frontu_P19B import contact_quadrature,solve_offset_hinges

ROOT=Path(__file__).resolve().parents[1]


class FullContact:
    def __init__(self,cfg=None):
        self.cfg=cfg or json.loads((ROOT/'dane/konfiguracje/p19c_styk_czasowy.json').read_text())
        c=self.cfg
        p=FrontWithHole(*c['span_m'],c['hole_radius_m'],PlateMaterial(c['E_pa'],c['nu'],c['density_kg_m3'],c['thickness_m']),
                        c['mesh_angular_per_side'],c['mesh_radial_layers'],c['boundary'])
        J=c['net_mass_kg']*(c['gyration_radius_m']**2+c['cg_depth_m']**2)
        base=p.mounted(c['bolt_circle_radius_m'],c['bolt_count'],c['net_mass_kg'],J,c['bolt_stiffness_n_m'],c['patch_radius_m'])
        Dg,area,xy=contact_quadrature(p,*c['gasket_radii_m'],c['gasket_quadrature_radial'],c['gasket_quadrature_angular'])
        self.plate=p;self.base=base;self.Dg=Dg;self.area=area;self.xy=xy
        self.D=sparse.vstack([Dg,-base.D],format='csr');self.ng=len(area)
        self.weights=np.r_[c['gasket_kn_pa_m']*area,np.full(c['bolt_count'],base.k)]
        self.offset=np.r_[np.zeros(self.ng),np.full(c['bolt_count'],c['bolt_T0_n']/base.k)]
        self.Ks=sparse.block_diag([p.K,sparse.csr_matrix((3,3))],format='csr');self.M=base.M
        self.Fgravity=base.load(moment_x_nm=c['net_mass_kg']*9.80665*c['cg_depth_m'])
        scale=max(np.linalg.norm(self.Fgravity),np.linalg.norm(base.D.T@np.full(c['bolt_count'],c['bolt_T0_n'])),1.)
        self.q0,self.Kt,self.active,self.preload=solve_offset_hinges(self.Ks,self.D,self.weights,self.offset,self.Fgravity,scale)
        self.z0=self.D@self.q0+self.offset;self.spring0=np.maximum(self.z0,0)
        # Wlasne wektory dla nowej kampanii maja jawny,deterministyczny start.
        val,vec=eigsh(self.Kt,k=48,M=self.M,sigma=0,which='LM',v0=np.sin(np.arange(self.M.shape[0])+1.))
        order=np.argsort(val);self.eigenvalues=val[order];self.eigenvectors=vec[:,order]
        w1=np.sqrt(self.eigenvalues[0]);w2=5*w1;zeta=c['zeta_reference']
        self.alpha=2*zeta*w1*w2/(w1+w2);self.beta=2*zeta/(w1+w2)
        self.damping_model=c.get('damping_model','FROZEN_PRELOAD_RAYLEIGH')
        if self.damping_model=='FROZEN_PRELOAD_RAYLEIGH':self.C=self.alpha*self.M+self.beta*self.Kt
        elif self.damping_model=='PLATE_MASS_RAYLEIGH':self.C=self.alpha*self.M+self.beta*self.Ks
        else:raise ValueError('Nieznany model tlumienia')
        self.H=base.load(pressure_pa=1,pressure_cap=True);self.e=np.zeros(self.M.shape[0]);self.e[-3]=1
        self.omega=2*np.pi*c['frequency_hz'];self.Kgas=c['p0_pa']/c['cavity_m3']
        self.tau=c['tau_s'];self.gamma=c['gamma'];self.sd=c['sd_m2']
        with (ROOT/'wyniki/p11_kalibracje_masy.csv').open() as f:
            row=next(r for r in csv.DictReader(f) if r['candidate_id']==c['candidate_id'] and r['reference']=='PISTON' and float(r['faces'])==c['moving_mass_reference_faces'])
        self.mm=float(row['effective_remaining_mass_kg']);self.factor=splu(self.Kt.tocsc())

    def basis(self,n,enrich=False):
        V=self.eigenvectors[:,:n].copy()
        if enrich:
            angle=np.arctan2(self.xy[:,1],self.xy[:,0]);patterns=[np.ones(len(angle))]
            for m in range(1,self.cfg['static_ring_harmonic_order']+1):patterns.extend([np.cos(m*angle),np.sin(m*angle)])
            loads=np.column_stack([self.H,self.e,*[self.Dg.T@(self.area*t) for t in patterns]])
            corrections=self.factor.solve(loads)
            # Usuniecie rzutu zmniejsza utrate dokladnosci przy zaleznosci liniowej.
            corrections-=V@(V.T@(self.M@corrections))
            norm=np.sqrt(np.maximum(np.sum(corrections*(self.M@corrections),axis=0),0))
            good=norm>1e-13*np.max(norm)
            W=corrections[:,good]/norm[good]
            g=W.T@(self.M@W);lam,U=eigh((g+g.T)/2);keep=lam>max(lam)*1e-10
            add=W@U[:,keep]/np.sqrt(lam[keep]);V=np.column_stack([V,add])
        mass=V.T@(self.M@V)
        # Poprawa ortonormalnosci tylko w malej przestrzeni.
        lam,U=eigh((mass+mass.T)/2);V=V@(U/np.sqrt(lam))
        assert np.linalg.norm(V.T@(self.M@V)-np.eye(V.shape[1]))<1e-7
        return V


class ReducedContact:
    def __init__(self,full,V,amplitude_rms=None,linear=False):
        self.full=full;self.V=V;self.n=V.shape[1];self.linear=linear
        self.Ks=V.T@(full.Ks@V);self.Kt=V.T@(full.Kt@V);self.C=V.T@(full.C@V)
        self.G=np.asarray(full.D@V);self.h=full.H@V;self.e=full.e@V
        self.pos_scale=.001*np.sqrt(full.cfg['net_mass_kg']);self.vol_scale=full.sd*.001
        self.amplitude_rms=full.cfg['cone_relative_rms_m'] if amplitude_rms is None else amplitude_rms
        self.A=np.sqrt(2)*self.amplitude_rms;self.dim=2*self.n+1
        # Dodatnia energia kinetyczna z zadanym,ale fizycznie sprzezonym stozkiem.
        assert np.linalg.eigvalsh(np.eye(self.n)-full.mm*np.outer(self.e,self.e)).min()>0

    def drive(self,theta):
        tr=2*np.pi*self.full.cfg['ramp_cycles']
        if theta<tr:
            u=max(theta,0)/tr;g=10*u**3-15*u**4+6*u**5
            gp=(30*u*u-60*u**3+30*u**4)/tr;gpp=(60*u-180*u*u+120*u**3)/tr**2
        else:g=1.;gp=0.;gpp=0.
        sn=np.sin(theta);cs=np.cos(theta)
        # Pochodne po theta,nie po sekundach.
        return self.A*g*sn,self.A*(gp*sn+g*cs),self.A*(gpp*sn+2*gp*cs-g*sn)

    def decode(self,y):
        n=self.n;S=self.pos_scale;w=self.full.omega
        return S*y[:n],w*S*y[n:2*n],self.vol_scale*y[-1]

    def mechanics(self,theta,y):
        f=self.full;u,v,lag=self.decode(y);x,xp,xpp=self.drive(theta)
        volume=f.sd*x+self.h@u;p=-f.Kgas*(f.gamma*volume-(f.gamma-1)*lag)
        if self.linear:force=(self.Kt-self.Ks)@u
        else:
            force=self.G.T@(f.weights*(np.maximum(f.z0+self.G@u,0)-f.spring0))
        acceleration=-self.C@v-self.Ks@u-force+self.h*p-self.e*f.mm*f.omega**2*xpp
        return u,v,lag,x,xp,xpp,volume,p,acceleration

    def rhs(self,theta,y):
        f=self.full;u,v,lag,x,xp,xpp,volume,p,acc=self.mechanics(theta,y)
        return np.r_[y[self.n:2*self.n],acc/(f.omega**2*self.pos_scale),(volume-lag)/(f.omega*f.tau*self.vol_scale)]

    def jac(self,theta,y):
        f=self.full;n=self.n;u,_,_=self.decode(y)
        if self.linear:K=self.Kt
        else:K=self.Ks+self.G.T@((f.weights*(f.z0+self.G@u>0))[:,None]*self.G)
        J=np.zeros((self.dim,self.dim));J[:n,n:2*n]=np.eye(n)
        J[n:2*n,:n]=-(K+f.Kgas*f.gamma*np.outer(self.h,self.h))/f.omega**2
        J[n:2*n,n:2*n]=-self.C/f.omega
        J[n:2*n,-1]=self.h*f.Kgas*(f.gamma-1)*self.vol_scale/(f.omega**2*self.pos_scale)
        J[-1,:n]=self.h*self.pos_scale/(f.omega*f.tau*self.vol_scale);J[-1,-1]=-1/(f.omega*f.tau)
        return J

    def metric(self,y):
        f=self.full;u,v,lag=self.decode(y)
        return float(u@self.Kt@u+v@v+f.Kgas*((self.h@u)**2+(f.gamma-1)*(self.h@u-lag)**2))

    def energy_rates(self,theta,y):
        f=self.full;u,v,lag,x,xp,xpp,volume,p,acc=self.mechanics(theta,y)
        xd=f.omega*xp;xdd=f.omega**2*xpp
        kinetic=.5*v@v+f.mm*xd*(self.e@v)+.5*f.mm*xd*xd
        delta=self.G@u;z=f.z0+delta
        if self.linear:elastic=.5*u@self.Kt@u
        else:elastic=.5*u@self.Ks@u+.5*np.dot(f.weights,np.maximum(z,0)**2-f.spring0**2)-np.dot(f.weights*f.spring0,delta)
        gas=.5*f.Kgas*(volume*volume+(f.gamma-1)*(volume-lag)**2)
        force=f.mm*(xdd+self.e@acc)-f.sd*p
        ps=force*xd;ds=v@self.C@v;dg=f.Kgas*(f.gamma-1)/f.tau*(volume-lag)**2
        return dict(energy=float(kinetic+elastic+gas),input_power=float(ps),structural_loss=float(ds),gas_loss=float(dg),
                    basket=float(self.e@u),pressure=float(p),volume=float(volume),force=float(force),
                    open_fraction=float(np.sum(f.area*(z[:f.ng]<=0))/sum(f.area)),
                    slack_bolts=int(np.sum(z[f.ng:]<=0)),
                    max_gasket_pressure=float(f.cfg['gasket_kn_pa_m']*max(np.maximum(z[:f.ng],0))))

    def linear_reference(self):
        f=self.full;w=f.omega;s=1j*w
        cab=f.cfg['cavity_m3']/(f.cfg['p0_pa']*(1+(f.gamma-1)*s*f.tau/(1+s*f.tau)))
        Z=self.Kt-w*w*np.eye(self.n)+s*self.C
        rhs=self.e*f.mm*w*w*self.amplitude_rms
        zi=np.linalg.solve(Z,rhs);zh=np.linalg.solve(Z,self.h)
        p=-(f.sd*self.amplitude_rms+self.h@zi)/(cab+self.h@zh);q=zi+zh*p
        return dict(basket=self.e@q,pressure=p,state=q)

    def simulate(self,method='Radau',rtol=None,atol=None,max_cycles=None,initial_state=None,start_cycle=0):
        c=self.full.cfg;period=2*np.pi;y=np.zeros(self.dim) if initial_state is None else np.array(initial_state,copy=True)
        t=start_cycle*period;successive=0;history=[];nfev=0
        for cycle in range(1,(max_cycles or c['maximum_cycles'])+1):
            sol=solve_ivp(self.rhs,(t,(start_cycle+cycle)*period),y,method=method,jac=self.jac,
                          rtol=rtol or c['rtol'],atol=atol or c['atol_dimensionless'],max_step=period/64,dense_output=True)
            if not sol.success:raise RuntimeError(sol.message)
            end=sol.y[:,-1];distance=np.sqrt(self.metric(end-y)/max(self.metric(end),self.metric(y),1e-30))
            history.append(float(distance));nfev+=sol.nfev
            if start_cycle+cycle>c['ramp_cycles'] and distance<c['periodicity_relative_energy_norm']:successive+=1
            else:successive=0
            if cycle%8==0:print('P19C',self.n,method,'cycle',cycle,'distance',distance,flush=True)
            if successive>=c['required_consecutive_periods']:break
            y=end;t=(start_cycle+cycle)*period
        # Jesli limit jest osiagniety,wynik i flaga pozostaja;nie udajemy okresowosci.
        settled=successive>=c['required_consecutive_periods']
        theta=np.linspace((start_cycle+cycle-1)*period,(start_cycle+cycle)*period,c['sample_points_per_cycle']+1)
        Y=sol.sol(theta);data=[self.energy_rates(th,Y[:,i]) for i,th in enumerate(theta)]
        time=theta/self.full.omega;energy=np.array([d['energy'] for d in data]);power=np.array([d['input_power']-d['structural_loss']-d['gas_loss'] for d in data])
        cumulative=np.r_[0,np.cumsum((power[1:]+power[:-1])*np.diff(time)/2)]
        # Globalny bilans z osobnego wzoru energii;nie tylko iloczyn reszty ODE.
        absolute=float(max(abs(energy-energy[0]-cumulative)))
        work=float(trapezoid(np.abs([d['input_power'] for d in data]),time))
        relative=absolute/max(work,max(abs(energy)),1e-30)
        basket=np.array([d['basket'] for d in data[:-1]]);pressure=np.array([d['pressure'] for d in data[:-1]])
        phases={}
        for name,array in [('basket',basket),('pressure',pressure)]:
            fft=np.fft.rfft(array)/len(array);ph=np.sqrt(2)*fft[1:11]
            phases[name]=dict(mean=float(fft[0].real),harmonics_rms_real=ph.real.tolist(),harmonics_rms_imag=ph.imag.tolist(),
                              diagnostic_H2_H10_ratio=float(np.linalg.norm(ph[1:])/max(abs(ph[0]),1e-30)))
        linear=self.linear_reference()
        result=dict(status='PERIODIC_WITHIN_STATED_CRITERION' if settled else 'NOT_SETTLED',dimension=self.n,method=method,cycles=cycle,start_cycle=start_cycle,nfev=nfev,
                    periodic_distance=history[-1],periodic_history=history,relative_integrated_energy_residual=float(relative),
                    max_open_area_fraction=max(d['open_fraction'] for d in data),mean_open_area_fraction=float(np.mean([d['open_fraction'] for d in data[:-1]])),
                    max_slack_bolts=max(d['slack_bolts'] for d in data),basket_peak_m=float(max(abs(basket))),pressure_rms_pa=float(np.sqrt(np.mean(pressure**2))),
                    phases=phases,linear_basket_rms_real=float(linear['basket'].real),linear_basket_rms_imag=float(linear['basket'].imag),
                    linear_pressure_rms_real=float(linear['pressure'].real),linear_pressure_rms_imag=float(linear['pressure'].imag),
                    damping_model=self.full.damping_model,
                    input_power_mean_w=float(trapezoid([d['input_power'] for d in data],time)/(time[-1]-time[0])),
                    structural_loss_mean_w=float(trapezoid([d['structural_loss'] for d in data],time)/(time[-1]-time[0])),
                    gas_loss_mean_w=float(trapezoid([d['gas_loss'] for d in data],time)/(time[-1]-time[0])))
        return result,dict(theta=theta,y=Y,data=data,solution=sol,V=self.V)
