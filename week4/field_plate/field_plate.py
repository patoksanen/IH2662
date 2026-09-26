"""Silicon field plate over explicit SiO2; constant silicon peak-field criterion."""
from pathlib import Path
import argparse, csv, json, math, shutil, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT / 'week3'))
from silicon_baseline import field
D = 'silicon_field_plate'
REGIONS = ('Silicon', 'Oxide')
EPS0 = 8.8541878128e-14


def validate(p):
    keys = ('oxide_thickness_um', 'oxide_relative_permittivity', 'plate_extension_um',
            'local_mesh_um', 'oxide_mesh_um', 'device_width_um', 'drift_thickness_um')
    if any(not math.isfinite(p[k]) or p[k] <= 0 for k in keys):
        raise ValueError('Geometry, mesh sizes and permittivity must be finite and positive')
    if p['plate_workfunction_offset_V'] != 0:
        raise ValueError('This tied-metal corner model requires plate_workfunction_offset_V=0; a different metal reference needs a revised boundary geometry')
    edge = p['implant_flat_extent_um'] + p['junction_depth_um']
    tip = edge + p['plate_extension_um']
    if not 0 < p['anode_extent_um'] < p['implant_flat_extent_um'] < edge < tip < p['device_width_um']-3:
        raise ValueError('Invalid anode/junction/plate geometry')
    if p['acceptor_peak_cm3'] <= p['donor_cm3'] or p['intrinsic_cm3'] <= 0:
        raise ValueError('Invalid doping')
    return edge, tip


def doping(p, x, y):
    length = p['junction_depth_um']*1e-4/math.sqrt(math.log(p['acceptor_peak_cm3']/p['donor_cm3']))
    return p['donor_cm3']-p['acceptor_peak_cm3']*np.exp(-(y*y+np.maximum(x-p['implant_flat_extent_um']*1e-4,0)**2)/length**2)


def geometry(p):
    edge, tip = validate(p)
    u=1e-4; a=p['implant_flat_extent_um']*u; c=p['anode_extent_um']*u
    j=p['junction_depth_um']*u; e=tip*u; w=p['device_width_um']*u
    d=(p['drift_thickness_um']+p['junction_depth_um'])*u; t=p['oxide_thickness_um']*u
    h=p['mesh_junction_um']*u; b=p['mesh_bulk_um']*u; fine=p['local_mesh_um']*u
    s=f'''// Coordinates in cm. Silicon depth positive; oxide above y=0.
Point(1)={{0,0,0,{h}}}; Point(2)={{{c},0,0,{fine}}};
Point(3)={{{edge*u},0,0,{fine}}}; Point(4)={{{e},0,0,{fine}}};
Point(5)={{{w},0,0,{b}}}; Point(6)={{{w},{d},0,{b}}};
Point(7)={{0,{d},0,{b}}}; Point(8)={{0,{j},0,{h}}};
Point(9)={{{a},{j},0,{h}}}; Point(10)={{{a},0,0,{h}}};
Point(11)={{{c},{-t},0,{fine}}}; Point(12)={{{e},{-t},0,{fine}}};
Point(13)={{{w},{-t},0,{p['oxide_mesh_um']*u}}};
Line(1)={{1,2}}; Line(2)={{2,3}}; Line(3)={{3,4}}; Line(4)={{4,5}};
Line(5)={{5,6}}; Line(6)={{6,7}}; Line(7)={{7,8}}; Line(8)={{8,1}};
Line(9)={{8,9}}; Circle(10)={{9,10,3}};
Line(11)={{2,11}}; Line(12)={{11,12}}; Line(13)={{12,13}}; Line(14)={{13,5}};
Curve Loop(1)={{1,2,3,4,5,6,7,8}}; Plane Surface(1)={{1}};
Curve Loop(2)={{11,12,13,14,-4,-3,-2}}; Plane Surface(2)={{2}};
Curve{{9,10}} In Surface{{1}};
Physical Surface("Silicon")={{1}}; Physical Surface("Oxide")={{2}};
Physical Curve("anode")={{1}}; Physical Curve("cathode")={{6}};
Physical Curve("plate")={{11,12}}; Physical Curve("silicon_oxide")={{2,3,4}};
Field[1]=Distance; Field[1].CurvesList={{9,10}}; Field[1].Sampling=500;
Field[2]=Threshold; Field[2].InField=1;
Field[2].SizeMin={h}; Field[2].SizeMax={b};
Field[2].DistMin={.7*u}; Field[2].DistMax={10*u};
'''
    boxes=[(39,44.5,-p['oxide_thickness_um'],4.5,p['local_mesh_um'],1),
           (tip-1.5,tip+1.5,-p['oxide_thickness_um'],2,p['local_mesh_um'],1),
           (p['anode_extent_um']-.5,p['anode_extent_um']+.5,-p['oxide_thickness_um'],1,p['local_mesh_um'],.5),
           (p['anode_extent_um'],p['device_width_um'],-p['oxide_thickness_um'],0,p['oxide_mesh_um'],.5)]
    for tag,(xmin,xmax,ymin,ymax,size,transition) in enumerate(boxes,3):
        s+=f'Field[{tag}]=Box; Field[{tag}].VIn={size*u}; Field[{tag}].VOut={b};\n'
        s+=f'Field[{tag}].XMin={xmin*u}; Field[{tag}].XMax={xmax*u};\n'
        s+=f'Field[{tag}].YMin={ymin*u}; Field[{tag}].YMax={ymax*u}; Field[{tag}].Thickness={transition*u};\n'
    return s+f'Field[7]=Min; Field[7].FieldsList={{2,3,4,5,6}}; Background Field=7;\nMesh.MeshSizeMin={fine}; Mesh.MeshSizeMax={b};\nMesh.Algorithm=5; Mesh.MshFileVersion=2.2; Mesh.Binary=0;\n'


def mesh(p,out):
    import gmsh
    import pyvista as pv
    (out/'field_plate.geo').write_text(geometry(p))
    gmsh.initialize()
    data={}
    try:
        gmsh.open(str(out/'field_plate.geo')); gmsh.model.mesh.generate(2)
        gmsh.write(str(out/'field_plate.msh'))
        groups={gmsh.model.getPhysicalName(dim,tag):(dim,tag) for dim,tag in gmsh.model.getPhysicalGroups()}
        assert set(groups)=={'Silicon','Oxide','anode','cathode','plate','silicon_oxide'}
        tags,xyz,_=gmsh.model.mesh.getNodes(); order=np.argsort(tags)
        tags=tags[order]; xyz=np.asarray(xyz).reshape(-1,3)[order]
        for region in REGIONS:
            _,physical=groups[region]; tris=[]
            for entity in gmsh.model.getEntitiesForPhysicalGroup(2,physical):
                types,_,nodes=gmsh.model.mesh.getElements(2,entity)
                assert list(types)==[2]
                tris.append(np.searchsorted(tags,np.asarray(nodes[0]).reshape(-1,3)))
            tri=np.concatenate(tris)
            used=np.unique(tri); mapping=np.full(len(xyz),-1); mapping[used]=np.arange(len(used))
            coords=xyz[used]; tri=mapping[tri]
            data[region]=(coords[:,0],coords[:,1],tri)
    finally: gmsh.finalize()
    blocks=pv.MultiBlock(); checks={}
    for region,(x,y,tri) in data.items():
        area=.5*np.abs((x[tri[:,1]]-x[tri[:,0]])*(y[tri[:,2]]-y[tri[:,0]])-(x[tri[:,2]]-x[tri[:,0]])*(y[tri[:,1]]-y[tri[:,0]]))
        expected=(p['device_width_um']*(p['drift_thickness_um']+p['junction_depth_um']) if region=='Silicon' else (p['device_width_um']-p['anode_extent_um'])*p['oxide_thickness_um'])*1e-8
        assert np.all(area>0) and np.isclose(area.sum(),expected,rtol=1e-10)
        grid=make_grid(x,y,tri)
        grid.cell_data['MaterialId']=np.full(len(tri),0 if region=='Silicon' else 1)
        if region=='Silicon':
            nd=doping(p,x,y); grid.point_data['NetDoping_cm-3']=nd
            grid.point_data['DopingSignedLog10']=np.sign(nd)*np.log10(1+np.abs(nd))
        blocks[region]=grid
        checks[region]={'nodes':len(x),'triangles':len(tri),'area_cm2':float(area.sum())}
    blocks.save(str(out/'structure.vtm'))
    edge,tip=validate(p)
    for closeup in (False,True):
        fig,ax=plt.subplots(figsize=(12,5))
        for region,(x,y,tri) in data.items():
            t=mtri.Triangulation(x*1e4,y*1e4,tri)
            if region=='Silicon':
                nd=doping(p,x,y); ax.tripcolor(t,facecolors=(nd[tri].mean(axis=1)<0).astype(float),cmap='coolwarm',vmin=0,vmax=1,rasterized=True)
                ax.tricontour(t,nd,levels=[0],colors='black',linewidths=1)
            else: ax.tripcolor(t,facecolors=np.ones(len(tri)),cmap='Greens',vmin=0,vmax=2,rasterized=True)
            ax.triplot(t,color='.25',linewidth=.065 if closeup else .02,rasterized=True)
        c=p['anode_extent_um']; ox=p['oxide_thickness_um']
        ax.plot([0,c,c,tip],[0,0,-ox,-ox],color='gold',lw=4,label='Anode-connected metal boundary')
        ax.set(xlabel='x (um)',ylabel='Depth (um)',title='Field plate: red p-type, blue n-type, green oxide; structure only')
        ax.set_aspect('equal'); ax.legend(loc='lower right')
        ax.set_xlim((35,tip+5) if closeup else (0,p['device_width_um']))
        ax.set_ylim((7,-ox-1) if closeup else (p['drift_thickness_um']+p['junction_depth_um'],-ox-2))
        fig.tight_layout(); fig.savefig(out/('structure_closeup.png' if closeup else 'structure.png'),dpi=180); plt.close(fig)
    checks.update(status='PASS: geometry and area checks',junction_edge_um=edge,plate_tip_um=tip,oxide_thickness_um=p['oxide_thickness_um'])
    (out/'structure_checks.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(checks,indent=2),flush=True)


def make_grid(x,y,tri):
    import pyvista as pv
    return pv.UnstructuredGrid(np.column_stack((np.full(len(tri),3),tri)).ravel(),np.full(len(tri),5,dtype=np.uint8),np.column_stack((x*1e4,y*1e4,np.zeros(len(x)))))


def set_bias(ds,p,v):
    ds.set_parameter(device=D,name='anode_bias',value=-v)
    ds.set_parameter(device=D,name='plate_bias',value=-v+plate_offset(p))


def plate_offset(p):
    vt=1.380649e-23*p['temperature_K']/1.602176634e-19
    # Same potential reference as the p-ohmic contact; ideal matched metal.
    return float(vt*np.arcsinh((p['donor_cm3']-p['acceptor_peak_cm3'])/(2*p['intrinsic_cm3'])))+p['plate_workfunction_offset_V']


def build(p,out,solve=False):
    import devsim as ds
    import devsim.umfpack.umfshim
    from devsim.python_packages import simple_physics as sp
    from devsim.python_packages.model_create import CreateSolution
    for name in ('extended_solver','extended_model','extended_equation'): ds.set_parameter(name=name,value=False)
    ds.create_gmsh_mesh(mesh='fp',file=str(out/'field_plate.msh'))
    for region in REGIONS: ds.add_gmsh_region(mesh='fp',gmsh_name=region,region=region,material=region)
    for contact,region in [('anode','Silicon'),('cathode','Silicon'),('plate','Oxide')]:
        ds.add_gmsh_contact(mesh='fp',gmsh_name=contact,region=region,name=contact,material='metal')
    ds.add_gmsh_interface(mesh='fp',gmsh_name='silicon_oxide',region0='Silicon',region1='Oxide',name='silicon_oxide')
    ds.finalize_mesh(mesh='fp'); ds.create_device(mesh='fp',device=D)
    args=dict(device=D,region='Silicon'); q=1.602176634e-19; k=1.380649e-23
    sp.SetSiliconParameters(D,'Silicon',p['temperature_K'])
    params={'Permittivity':p['relative_permittivity']*EPS0,'ElectronCharge':q,'T':p['temperature_K'],
            'kT':k*p['temperature_K'],'V_t':k*p['temperature_K']/q,'mu_n':p['electron_mobility_cm2_Vs'],
            'mu_p':p['hole_mobility_cm2_Vs'],'n_i':p['intrinsic_cm3'],'n1':p['intrinsic_cm3'],
            'p1':p['intrinsic_cm3'],'taun':p['lifetime_s'],'taup':p['lifetime_s']}
    for key,value in params.items(): ds.set_parameter(**args,name=key,value=value)
    ds.set_parameter(device=D,region='Oxide',name='Permittivity',value=p['oxide_relative_permittivity']*EPS0)
    length=p['junction_depth_um']*1e-4/math.sqrt(math.log(p['acceptor_peak_cm3']/p['donor_cm3']))
    # Scientific notation avoids integer-literal interpretation of large doping constants.
    ds.node_model(**args,name='Donors',equation=format(p['donor_cm3'],'.17e'))
    ds.node_model(**args,name='Acceptors',equation=f"{p['acceptor_peak_cm3']:.17e}*exp(-(y^2+max(x-{p['implant_flat_extent_um']*1e-4},0)^2)/{length**2})")
    ds.node_model(**args,name='NetDoping',equation='Donors-Acceptors')
    data={}
    for region in REGIONS:
        kw=dict(device=D,region=region)
        x=np.array(ds.get_node_model_values(**kw,name='x')); y=np.array(ds.get_node_model_values(**kw,name='y'))
        tri=np.array(ds.get_element_node_list(**kw),dtype=int)
        assert np.all(np.array(ds.get_node_model_values(**kw,name='NodeVolume'))>0)
        data[region]=(x,y,tri)
    x,y,_=data['Silicon']; nd=np.array(ds.get_node_model_values(**args,name='NetDoping'))
    expected=doping(p,x,y)
    if not np.allclose(nd,expected,rtol=1e-10,atol=1e3):
        i=int(np.argmax(np.abs(nd-expected)))
        raise RuntimeError(f'Doping mismatch: node {i}, actual {nd[i]}, expected {expected[i]}, position {(x[i],y[i])}')
    assert set(ds.get_contact_list(device=D))=={'anode','cathode','plate'}
    sp.CreateSiliconPotentialOnly(D,'Silicon')
    sp.CreateOxidePotentialOnly(D,'Oxide')
    set_bias(ds,p,0); ds.set_parameter(device=D,name='cathode_bias',value=0)
    for contact in ('anode','cathode'): sp.CreateSiliconPotentialOnlyContact(D,'Silicon',contact)
    sp.CreateOxideContact(D,'Oxide','plate')
    sp.CreateSiliconOxideInterface(D,'silicon_oxide')
    ds.set_node_values(**args,name='Potential',values=(params['V_t']*np.arcsinh(nd/(2*p['intrinsic_cm3']))).tolist())
    xo,yo,_=data['Oxide']
    initial=params['V_t']*np.arcsinh(doping(p,xo,np.zeros_like(xo))/(2*p['intrinsic_cm3']))
    ds.set_node_values(device=D,region='Oxide',name='Potential',values=initial.tolist())
    checks={'status':'PASS: two-region import, silicon doping, positive volumes, oxide-only plate contact',
            'contacts':list(ds.get_contact_list(device=D)),'interface':'silicon_oxide',
            'oxide_equations':list(ds.get_equation_list(device=D,region='Oxide')),'plate_offset_V':plate_offset(p)}
    (out/'import_checks.json').write_text(json.dumps(checks,indent=2))
    if solve:
        ds.solve(type='dc',symbolic_iteration_limit=0,absolute_error=1,relative_error=1e-10,maximum_iterations=100)
        for name,initial_name in [('Electrons','IntrinsicElectrons'),('Holes','IntrinsicHoles')]:
            CreateSolution(D,'Silicon',name); ds.set_node_values(**args,name=name,init_from=initial_name)
        sp.CreateSiliconDriftDiffusion(D,'Silicon')
        for contact in ('anode','cathode'): sp.CreateSiliconDriftDiffusionAtContact(D,'Silicon',contact)
        ds.solve(type='dc',symbolic_iteration_limit=0,absolute_error=1e4,relative_error=1e-4,maximum_iterations=100)
    return ds,data


def fields(ds,data):
    result={}
    for region,(x,y,tri) in data.items():
        potential=np.array(ds.get_node_model_values(device=D,region=region,name='Potential'))
        ex,ey,mag=field(potential,x,y,tri)
        if not np.all(np.isfinite(mag)): raise RuntimeError('Non-finite electric field')
        result[region]=(potential,ex,ey,mag)
    return result


def export(ds,p,data,out,label,bias):
    import pyvista as pv
    blocks=pv.MultiBlock(); fs=fields(ds,data)
    for region,(x,y,tri) in data.items():
        pot,ex,ey,mag=fs[region]; grid=make_grid(x,y,tri)
        grid.point_data['Potential_V']=pot
        grid.cell_data['ElectricField_V_cm']=mag
        grid.cell_data['ElectricFieldVector_V_cm']=np.column_stack((ex,ey,np.zeros(len(ex))))
        grid.field_data['ReverseVoltage_V']=np.array([bias])
        if region=='Silicon':
            grid.point_data['NetDoping_cm-3']=doping(p,x,y)
            for name in ('Electrons','Holes'): grid.point_data[name+'_cm-3']=ds.get_node_model_values(device=D,region=region,name=name)
        blocks[region]=grid
        grid.save(str(out/(label+'_'+region.lower()+'.vtu')))
    blocks.save(str(out/(label+'.vtm')))
    # Separate color scales: the silicon criterion is NOT applied to the oxide.
    fig,axes=plt.subplots(2,1,figsize=(11,8))
    edge,tip=validate(p)
    for ax,region in zip(axes,REGIONS):
        x,y,tri=data[region]; mag=fs[region][3]; t=mtri.Triangulation(x*1e4,y*1e4,tri)
        im=ax.tripcolor(t,facecolors=mag,shading='flat',cmap='inferno')
        if region=='Silicon': ax.tricontour(t,doping(p,x,y),levels=[0],colors='cyan',linewidths=.7)
        i=int(np.argmax(mag)); ax.plot(x[tri[i]].mean()*1e4,y[tri[i]].mean()*1e4,'x',color='lime')
        ax.set(xlabel='x (um)',ylabel='Depth (um)',title=f'{region}: reverse bias {bias:g} V')
        ax.set_xlim(35,tip+7)
        ax.set_ylim((8,0) if region=='Silicon' else (0,-p['oxide_thickness_um']))
        fig.colorbar(im,ax=ax,label='Electric field (V/cm)')
    fig.tight_layout(); fig.savefig(out/(label+'_field.png'),dpi=180); plt.close(fig)


def boundary_checks(ds,p,bias):
    residual=np.asarray(ds.get_interface_model_values(device=D,interface='silicon_oxide',name='continuousPotential'))
    kw=dict(device=D,region='Oxide')
    x=np.asarray(ds.get_node_model_values(**kw,name='x'))
    y=np.asarray(ds.get_node_model_values(**kw,name='y'))
    potential=np.asarray(ds.get_node_model_values(**kw,name='Potential'))
    _,tip=validate(p); c=p['anode_extent_um']*1e-4; t=p['oxide_thickness_um']*1e-4
    plate_nodes=(np.isclose(x,c,rtol=0,atol=1e-12)) | (np.isclose(y,-t,rtol=0,atol=1e-12) & (x<=tip*1e-4+1e-12))
    assert np.any(plate_nodes)
    plate=potential[plate_nodes]-ds.get_parameter(device=D,name='plate_bias')
    mismatch=float(np.max(np.abs(residual)))
    plate_error=float(np.max(np.abs(plate)))
    assert mismatch<1e-7, f'Interface potential mismatch {mismatch}'
    assert plate_error<1e-7, f'Plate boundary mismatch {plate_error}'
    assert abs(ds.get_parameter(device=D,name='anode_bias')+bias)<1e-9
    assert abs(ds.get_parameter(device=D,name='plate_bias')+bias-plate_offset(p))<1e-9
    assert set(ds.get_equation_list(device=D,region='Oxide'))=={'PotentialEquation'}
    return {'interface_potential_mismatch_V':mismatch,'plate_boundary_residual_V':plate_error}


def simulate(p,out,stop_at=None):
    ds,data=build(p,out,solve=True)
    export(ds,p,data,out,'equilibrium',0)
    rows=[]; snapshots=sorted(set(p['snapshot_voltages_V']))
    if any(not 0<t<=p['max_voltage_V'] for t in snapshots): raise ValueError('Invalid snapshot voltage')
    names={'Silicon':('Potential','Electrons','Holes'),'Oxide':('Potential',)}
    def sample(v):
        fs=fields(ds,data); checks=boundary_checks(ds,p,v)
        si=fs['Silicon'][3]; ox=fs['Oxide'][3]; i=int(np.argmax(si)); j=int(np.argmax(ox))
        x,y,tri=data['Silicon']; xo,yo,to=data['Oxide']
        currents=[sum(ds.get_contact_current(device=D,contact=c,equation=e) for e in ('ElectronContinuityEquation','HoleContinuityEquation')) for c in ('anode','cathode')]
        row=dict(reverse_voltage_V=v,peak_field_V_cm=float(si[i]),peak_x_um=float(x[tri[i]].mean()*1e4),peak_depth_um=float(y[tri[i]].mean()*1e4),
                 oxide_peak_field_V_cm=float(ox[j]),oxide_peak_x_um=float(xo[to[j]].mean()*1e4),oxide_peak_depth_um=float(yo[to[j]].mean()*1e4),
                 anode_A_per_cm=currents[0],cathode_A_per_cm=currents[1],**checks)
        rows.append(row)
        with (out/'peak_field.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(row)); writer.writeheader(); writer.writerows(rows)
        print(f"BIAS {v:.6f} V | silicon peak {si[i]:.6g} V/cm | oxide peak {ox[j]:.6g} V/cm",flush=True)
    sample(0); v=0.; step=.1; previous=None; previous_v=None; crossing=None
    limit=p['max_voltage_V'] if stop_at is None else stop_at
    while v<limit-1e-9 and rows[-1]['peak_field_V_cm']<p['critical_field_V_cm']:
        if rows[-1]['peak_field_V_cm']>.9*p['critical_field_V_cm']: step=min(step,p['crossing_step_V'])
        dv=min(step,limit-v)
        future=[t for t in snapshots if t>v+1e-8]
        if future: dv=min(dv,future[0]-v)
        saved={(r,n):np.array(ds.get_node_model_values(device=D,region=r,name=n)) for r in REGIONS for n in names[r]}
        while True:
            trial=v+dv
            if previous is not None:
                ratio=dv/(v-previous_v)
                for (r,n),current in saved.items():
                    old=previous[(r,n)]
                    predicted=current+ratio*(current-old) if n=='Potential' else current*np.exp(np.clip(ratio*np.log(np.maximum(current,1e-300)/np.maximum(old,1e-300)),-3,3))
                    ds.set_node_values(device=D,region=r,name=n,values=predicted.tolist())
            set_bias(ds,p,trial)
            try:
                ds.solve(type='dc',symbolic_iteration_limit=0,absolute_error=1e4,relative_error=1e-4,maximum_iterations=40)
                break
            except ds.error:
                for (r,n),values in saved.items(): ds.set_node_values(device=D,region=r,name=n,values=values.tolist())
                set_bias(ds,p,v); dv/=2
                if dv<min(.02,(limit-v)/4): raise RuntimeError(f'Convergence failed near {trial:g} V; CSV is partial')
                print(f'Retry with {dv:g} V step',flush=True)
        previous=saved; previous_v=v; v=trial; sample(v)
        for target in snapshots:
            if abs(v-target)<1e-8: export(ds,p,data,out,'bias_'+format(target,'.6f').replace('.','p')+'V',v)
        step=min(p['voltage_step_V'],dv*1.5)
        if rows[-1]['peak_field_V_cm']>=p['critical_field_V_cm']:
            lo,hi=rows[-2:]; crossing=lo['reverse_voltage_V']+(p['critical_field_V_cm']-lo['peak_field_V_cm'])*(hi['reverse_voltage_V']-lo['reverse_voltage_V'])/(hi['peak_field_V_cm']-lo['peak_field_V_cm'])
    export(ds,p,data,out,'final',v)
    fig,ax=plt.subplots(figsize=(8,5)); ax.plot([r['reverse_voltage_V'] for r in rows],[r['peak_field_V_cm'] for r in rows],'.-')
    ax.axhline(p['critical_field_V_cm'],color='red',ls='--'); ax.set(xlabel='Reverse voltage (V)',ylabel='Silicon peak field (V/cm)',title='Silicon field plate')
    ax.grid(alpha=.25); fig.tight_layout(); fig.savefig(out/'peak_field.png',dpi=180); plt.close(fig)
    if crossing is None and stop_at is None: raise RuntimeError('No silicon field-criterion crossing before voltage limit')
    last=rows[-1]; balance=abs(last['anode_A_per_cm']+last['cathode_A_per_cm'])/max(abs(last['anode_A_per_cm']),abs(last['cathode_A_per_cm']),1e-30)
    summary=dict(case='silicon_field_plate',status='silicon_threshold_reached' if crossing is not None else 'requested_test_bias_reached',criterion_voltage_V=crossing,last_voltage_V=v,
                 last_peak_field_V_cm=last['peak_field_V_cm'],last_oxide_peak_field_V_cm=last['oxide_peak_field_V_cm'],final_relative_current_imbalance=balance,
                 criterion='Silicon constant peak-field threshold; no avalanche or oxide-breakdown model',mesh_convergence='Not established for this geometry',
                 snapshot_voltages_saved_V=[t for t in snapshots if any(abs(r['reverse_voltage_V']-t)<1e-8 for r in rows)],parameters=p)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print('PASS: '+summary['status']+f'; final bias {v:.6f} V; threshold {crossing}',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['mesh','view-mesh','check','smoke','run'])
    parser.add_argument('--parameters',type=Path,default=ROOT/'parameters.json')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--overwrite',action='store_true')
    opt=parser.parse_args(); p=json.loads(opt.parameters.read_text(encoding='utf-8-sig')); validate(p)
    case=f"plate_L{p['plate_extension_um']:g}_tox{p['oxide_thickness_um']:g}_h{p['local_mesh_um']:g}"
    out=(opt.output or ROOT/('diagnostics' if opt.action=='smoke' else 'results')/case).resolve()
    out.mkdir(parents=True,exist_ok=True); param=out/'parameters_used.json'
    if param.exists() and json.loads(param.read_text())!=p: raise RuntimeError('Parameters differ: select a new --output folder')
    if opt.action in ('run','smoke','mesh') and (out/'equilibrium.vtm').exists() and not opt.overwrite:
        raise RuntimeError('Solved outputs exist; select --output or explicitly --overwrite')
    if opt.overwrite:
        # Remove only old generated artifacts, never source or arbitrary paths.
        for f in out.iterdir():
            if f.is_file() and (f.name in ('summary.json','peak_field.csv','peak_field.png') or f.name.startswith(('equilibrium','final','bias_'))): f.unlink()
    param.write_text(json.dumps(p,indent=2))
    if not (out/'field_plate.msh').exists() or opt.action=='mesh': mesh(p,out)
    if opt.action=='view-mesh':
        import gmsh
        gmsh.initialize()
        try: gmsh.open(str(out/'field_plate.msh')); gmsh.fltk.run()
        finally: gmsh.finalize()
    elif opt.action=='check': build(p,out); print('PASS: field-plate mesh and equation setup',flush=True)
    elif opt.action in ('run','smoke'): simulate(p,out,1.0 if opt.action=='smoke' else None)

if __name__=='__main__': main()
