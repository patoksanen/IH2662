"""Week 4 silicon: one uncontacted guard diffusion in a straight-edge 2D section."""
from pathlib import Path
import argparse, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import solver_core as core
ROOT=Path(__file__).resolve().parent

def dimensions(p):
    edge=p['implant_flat_extent_um']+p['junction_depth_um']
    left=edge+p['ring_gap_um']+p['ring_depth_um']
    return edge,left,left+p['ring_implant_width_um']

def profiles(p,x,y):
    _,left,right=dimensions(p)
    lm=p['junction_depth_um']*1e-4/math.sqrt(math.log(p['acceptor_peak_cm3']/p['donor_cm3']))
    lr=p['ring_depth_um']*1e-4/math.sqrt(math.log(p['ring_peak_cm3']/p['donor_cm3']))
    main=p['acceptor_peak_cm3']*np.exp(-(y*y+np.maximum(x-p['implant_flat_extent_um']*1e-4,0)**2)/lm**2)
    distance=np.maximum(np.maximum(left*1e-4-x,x-right*1e-4),0)
    ring=p['ring_peak_cm3']*np.exp(-(y*y+distance**2)/lr**2)
    return main,ring

def validate(p):
    for key in ('ring_gap_um','ring_depth_um','ring_implant_width_um','local_mesh_um'):
        if not math.isfinite(p[key]) or p[key]<=0: raise ValueError(f'{key} must be finite and positive')
    if p['ring_peak_cm3']<=p['donor_cm3']: raise ValueError('Ring acceptors must exceed donors')
    edge,left,right=dimensions(p)
    if right+p['ring_depth_um']+2>=p['device_width_um']: raise ValueError('Ring too close to domain boundary')
    if p['ring_depth_um']+2>=p['drift_thickness_um']+p['junction_depth_um']: raise ValueError('Ring too close to cathode')
    sx=np.linspace(0,p['device_width_um'],120001)*1e-4
    a,b=profiles(p,sx,np.zeros_like(sx)); net=p['donor_cm3']-a-b
    crossings=np.where(np.diff(net<0))[0]
    if len(crossings)!=3: raise ValueError('Expected separate main and ring p regions: three surface crossings')
    roots=[float((sx[i]-net[i]*(sx[i+1]-sx[i])/(net[i+1]-net[i]))*1e4) for i in crossings]
    # Both acceptor profiles decrease with depth; the n-type surface gap
    # therefore separates the p diffusions throughout the thickness.
    mid=(roots[0]+roots[1])/2*1e-4
    a,b=profiles(p,np.array([mid]),np.array([0.]))
    assert p['donor_cm3']-a[0]-b[0]>0
    return dict(surface_junctions_um=roots,actual_surface_gap_um=roots[1]-roots[0],ring_implant_window_um=[left,right],nominal_main_edge_um=edge)

def geometry(p,planar=False,scale=1):
    if planar: raise ValueError('Guard ring is not a planar control')
    s=core.original_geometry(p,False,scale)
    _,left,right=dimensions(p); h=p['local_mesh_um']*1e-4*scale; b=p['mesh_bulk_um']*1e-4*scale
    boxes=[(39,44.5,4.5),(left-p['ring_depth_um']-1,right+p['ring_depth_um']+1,p['ring_depth_um']+1.5)]
    for tag,(xmin,xmax,ymax) in enumerate(boxes,3):
        s+=f'\nField[{tag}]=Box;\nField[{tag}].VIn={h}; Field[{tag}].VOut={b};\n'
        s+=f'Field[{tag}].XMin={xmin*1e-4}; Field[{tag}].XMax={xmax*1e-4};\n'
        s+=f'Field[{tag}].YMin=0; Field[{tag}].YMax={ymax*1e-4};\nField[{tag}].Thickness=0.0001;\n'
    return s+f'Field[5]=Min; Field[5].FieldsList={{2,3,4}};\nBackground Field=5;\nMesh.MeshSizeMin={h};\n'

def structure(p,out):
    import gmsh
    import pyvista as pv
    gmsh.initialize()
    try:
        gmsh.open(str(out/'silicon_junction.msh'))
        groups={gmsh.model.getPhysicalName(d,t):d for d,t in gmsh.model.getPhysicalGroups()}
        assert groups=={'Silicon':2,'anode':1,'cathode':1},groups
        tags,xyz,_=gmsh.model.mesh.getNodes(); order=np.argsort(tags)
        tags=tags[order]; xyz=np.asarray(xyz).reshape(-1,3)[order]
        types,_,nodes=gmsh.model.mesh.getElements(2); assert list(types)==[2]
        tri=np.searchsorted(tags,np.asarray(nodes[0]).reshape(-1,3))
    finally: gmsh.finalize()
    x,y=xyz[:,0],xyz[:,1]; ma,ra=profiles(p,x,y); nd=p['donor_cm3']-ma-ra
    a=xyz[tri[:,1],:2]-xyz[tri[:,0],:2]; b=xyz[tri[:,2],:2]-xyz[tri[:,0],:2]
    area=.5*np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])
    assert np.all(area>0) and np.all(np.isfinite(nd))
    expected=p['device_width_um']*(p['drift_thickness_um']+p['junction_depth_um'])*1e-8
    assert np.isclose(area.sum(),expected,rtol=1e-10)
    grid=pv.UnstructuredGrid(np.column_stack((np.full(len(tri),3),tri)).ravel(),np.full(len(tri),5,dtype=np.uint8),xyz*1e4)
    for name,values in [('NetDoping_cm-3',nd),('MainAcceptors_cm-3',ma),('RingAcceptors_cm-3',ra)]: grid.point_data[name]=values
    grid.point_data['DopingSignedLog10']=np.sign(nd)*np.log10(1+np.abs(nd))
    grid.save(str(out/'structure.vtu'))
    triang=mtri.Triangulation(x*1e4,y*1e4,tri); _,left,right=dimensions(p)
    for closeup in (False,True):
        fig,ax=plt.subplots(figsize=(12,4.8))
        ax.tripcolor(triang,facecolors=(nd[tri].mean(axis=1)<0).astype(float),cmap='coolwarm',vmin=0,vmax=1,rasterized=True)
        ax.triplot(triang,color='0.2',linewidth=.09 if closeup else .025,rasterized=True)
        ax.tricontour(triang,nd,levels=[0],colors='black',linewidths=1)
        ax.plot([0,p['anode_extent_um']],[0,0],lw=5,color='gold',label='Anode contact')
        ax.text((left+right)/2,-.3,'Floating p ring',ha='center',fontsize=10)
        ax.set(xlabel='x (um)',ylabel='Depth (um)',title='Guard-ring structure: red p-type, blue n-type; no bias solved')
        ax.set_aspect('equal')
        if closeup: ax.set_xlim(35,right+p['ring_depth_um']+3); ax.set_ylim(7,-1)
        else: ax.set_xlim(0,p['device_width_um']); ax.set_ylim(p['drift_thickness_um']+p['junction_depth_um'],-2)
        ax.legend(loc='lower right'); fig.tight_layout()
        fig.savefig(out/('structure_closeup.png' if closeup else 'structure.png'),dpi=180); plt.close(fig)
    checks=validate(p)
    checks.update(nodes=len(x),triangles=len(tri),physical_groups=groups,local_target_um=p['local_mesh_um'],status='PASS: geometry and doping only; no bias solution',minimum_triangle_area_cm2=float(area.min()))
    (out/'structure_checks.json').write_text(json.dumps(checks,indent=2)); print(json.dumps(checks,indent=2),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['mesh','check','view-mesh','equilibrium','run'])
    parser.add_argument('--parameters',type=Path,default=ROOT/'parameters.json')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--overwrite',action='store_true',help='Allow replacement of existing case outputs')
    opt=parser.parse_args(); p=json.loads(opt.parameters.read_text(encoding='utf-8-sig')); p['_precision']='double'; validate(p)
    out=opt.output or ROOT/'results'/f"guard_ring_gap{p['ring_gap_um']:g}_h{p['local_mesh_um']:g}"
    out=out.resolve(); out.mkdir(parents=True,exist_ok=True); saved=out/'parameters_used.json'
    if saved.exists() and json.loads(saved.read_text())!=p and not opt.overwrite: raise RuntimeError('Parameters changed: choose --output for a new case')
    if opt.action in ('run','equilibrium') and (out/'equilibrium.vtu').exists() and not opt.overwrite: raise RuntimeError('Solver outputs exist: choose --output or explicitly --overwrite')
    if opt.action=='mesh' and (out/'final.vtu').exists() and not opt.overwrite: raise RuntimeError('Completed results exist: choose --output for a new case')
    saved.write_text(json.dumps(p,indent=2)); core.geometry=geometry
    if opt.action=='mesh' or not (out/'silicon_junction.msh').exists() or opt.overwrite: core.mesh(p,out,False,1); structure(p,out)
    if opt.action=='view-mesh':
        import gmsh
        gmsh.initialize()
        try: gmsh.open(str(out/'silicon_junction.msh')); gmsh.fltk.run()
        finally: gmsh.finalize()
    elif opt.action=='check':
        ds,D,R,x,y,tri,nd=core.build(p,out,False,solve=False)
        assert set(ds.get_contact_list(device=D))=={'anode','cathode'}
        volumes=np.asarray(ds.get_node_model_values(device=D,region=R,name='NodeVolume'))
        assert np.all(volumes>0)
        report={'status':'PASS: DEVSIM mesh import, independent doping check, two contacts only, positive node volumes',
                'nodes':len(x),'triangles':len(tri),'min_node_volume_cm2':float(volumes.min()),'bias_solved':False}
        (out/'devsim_checks.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
    elif opt.action in ('equilibrium','run'): core.simulate(p,out,False,opt.action=='equilibrium')

if __name__=='__main__': main()
