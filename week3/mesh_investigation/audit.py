from pathlib import Path
import json, sys
import numpy as np
import pyvista as pv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mt
root=Path(__file__).resolve().parent.parent
out=Path(__file__).resolve().parent
records=[]
fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,name in zip(axes,["baseline_double_h1","baseline_double_h0.7"]):
    folder=root/"results"/name
    g=pv.read(folder/"final.vtu")
    t=g.cells.reshape(-1,4)[:,1:]
    p=g.points[t,:2]; c=p.mean(axis=1)
    lengths=np.stack([np.linalg.norm(p[:,1]-p[:,0],axis=1),np.linalg.norm(p[:,2]-p[:,1],axis=1),np.linalg.norm(p[:,0]-p[:,2],axis=1)],axis=1)
    area=np.abs((p[:,1,0]-p[:,0,0])*(p[:,2,1]-p[:,0,1])-(p[:,1,1]-p[:,0,1])*(p[:,2,0]-p[:,0,0]))/2
    quality=4*np.sqrt(3)*area/(lengths**2).sum(axis=1)
    angles=np.arccos(np.clip(np.column_stack([(lengths[:,0]**2+lengths[:,2]**2-lengths[:,1]**2)/(2*lengths[:,0]*lengths[:,2]),(lengths[:,0]**2+lengths[:,1]**2-lengths[:,2]**2)/(2*lengths[:,0]*lengths[:,1]),(lengths[:,1]**2+lengths[:,2]**2-lengths[:,0]**2)/(2*lengths[:,1]*lengths[:,2])]),-1,1))*180/np.pi
    mag=g.cell_data["ElectricField_V_cm"]; i=mag.argmax()
    L2=9/np.log(1e17/3.67e14)
    r=np.hypot(np.maximum(c[:,0]-40,0),c[:,1])
    gradient_scale=L2/(2*np.maximum(r,1e-10))
    roi=(c[:,0]>38)&(c[:,0]<45)&(c[:,1]<5)
    neutral_p=(c[:,0]<37)&(c[:,1]<1)
    records.append({"case":name,"nodes":g.n_points,"triangles":g.n_cells,"quality_min":float(quality.min()),"angle_min_deg":float(angles.min()),"degenerate_triangles":int((area<=0).sum()),"peak_centroid_um":c[i].tolist(),"peak_triangle_vertices_um":p[i].tolist(),"peak_triangle_edges_um":lengths[i].tolist(),"peak_distance_to_metallurgical_junction_um":float(abs(r[i]-3)),"local_acceptor_efold_length_um":float(gradient_scale[i]),"global_junction_efold_length_um":float(L2/6),"peak_element_min_net_doping_cm3":float(g["NetDoping_cm-3"][t[i]].min()),"edge_patch_triangles":int(roi.sum()),"neutral_p_triangles":int(neutral_p.sum()),"peak_V_cm":float(mag[i])})
    tr=mt.Triangulation(g.points[:,0],g.points[:,1],t)
    ax.tripcolor(tr,facecolors=mag/1e5,cmap="inferno",vmin=0,vmax=2.7)
    ax.triplot(tr,color="white",linewidth=.35,alpha=.7)
    ax.tricontour(tr,g["NetDoping_cm-3"],levels=[0],colors=["cyan"])
    ax.plot(c[i,0],c[i,1],"gx",markersize=10)
    ax.set(xlim=(39,45),ylim=(4,0),xlabel="x (um)",ylabel="Depth (um)",title=name)
    ax.set_aspect("equal")
fig.suptitle("Junction-edge detail: cyan = doping zero; green = peak-field triangle")
fig.tight_layout(); fig.savefig(out/"edge_audit.png",dpi=180)
(out/"mesh_audit.json").write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
