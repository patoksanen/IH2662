from pathlib import Path
import json, sys
import numpy as np
import devsim as ds
root=Path(__file__).resolve().parent
cases=[("original",root.parent/"results"/"baseline_double_h1"),("global_07",root.parent/"results"/"baseline_double_h0.7"),("field_only",root/"field_only"),("local_010",root/"edge_010"),("local_007",root/"edge_007")]
out=[]
for i,(name,folder) in enumerate(cases):
    mesh=f"audit_mesh_{i}"; dev=f"audit_device_{i}"
    ds.create_gmsh_mesh(mesh=mesh,file=str(folder/"silicon_junction.msh"))
    ds.add_gmsh_region(mesh=mesh,gmsh_name="Silicon",region="Silicon",material="Silicon")
    for c in ["anode","cathode"]:
        ds.add_gmsh_contact(mesh=mesh,gmsh_name=c,region="Silicon",material="metal",name=c)
    ds.finalize_mesh(mesh=mesh); ds.create_device(mesh=mesh,device=dev)
    a=dict(device=dev,region="Silicon")
    volumes=np.array(ds.get_node_model_values(**a,name="NodeVolume"))
    couples=np.array(ds.get_edge_model_values(**a,name="EdgeCouple"))
    row={"case":name,"negative_node_volumes":int((volumes<0).sum()),"zero_node_volumes":int((volumes==0).sum()),"negative_edge_couples":int((couples < -1e-15).sum()),"min_node_volume":float(volumes.min()),"min_edge_couple":float(couples.min())}
    out.append(row)
    ds.delete_device(device=dev); ds.delete_mesh(mesh=mesh)
(root/"finite_volume_audit.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
