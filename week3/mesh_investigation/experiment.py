"""Isolated mesh experiments; leaves original results and parameters unchanged."""
from pathlib import Path
import argparse, json, sys, time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import silicon_baseline as base
parser=argparse.ArgumentParser()
parser.add_argument("variant",choices=["field_only","edge_010","edge_007","bulk15","edge_010_bulk15","edge_005", "edge_0035", "edge_0025"])
parser.add_argument("--mesh-only",action="store_true")
opt=parser.parse_args()
p=base.settings(); p["_precision"]="double"
if opt.variant in ("bulk15","edge_010_bulk15"): p["mesh_bulk_um"]=1.5
out=ROOT/opt.variant
out.mkdir(exist_ok=True)
original=base.geometry
def geometry(p,planar=False,scale=1):
    s=original(p,planar,scale)
    if opt.variant=="bulk15": return s
    if opt.variant=="field_only":
        s+="\nMesh.MeshSizeFromPoints=0;\nMesh.MeshSizeExtendFromBoundary=0;\nMesh.MeshSizeFromCurvature=0;\n"
    else:
        h={"edge_007":0.07,"edge_005":0.05, "edge_0035":0.035, "edge_0025":0.025}.get(opt.variant,0.1)
        s+=f"""
// Refine the ACTUAL peak-field area, including the depleted p-side.
// Base mesh elsewhere is unchanged. Gmsh combines the minimum targets.
Field[3]=Box;
Field[3].VIn={h*1e-4}; Field[3].VOut={p["mesh_bulk_um"]*1e-4};
Field[3].XMin=0.0039; Field[3].XMax=0.00445;
Field[3].YMin=0; Field[3].YMax=0.00045;
Field[3].Thickness=0.0001;
Field[4]=Min; Field[4].FieldsList={{2,3}};
Background Field=4;
Mesh.MeshSizeMin={h*1e-4};
"""
    return s
base.geometry=geometry
(out/"parameters_used.json").write_text(json.dumps(p,indent=2))
(out/"experiment.json").write_text(json.dumps({"variant":opt.variant,"purpose":"Mesh diagnostic with identical geometry, doping and physical model","start_time":time.time()},indent=2))
base.mesh(p,out,False,1)
if not opt.mesh_only: base.simulate(p,out,False,False)
