"""Read-only verification of saved Week 3 results."""
from pathlib import Path
import json
import numpy as np
import silicon_baseline as model

root=Path(__file__).resolve().parent
# Independent affine-field check, on two differently oriented triangles.
x=np.array([0.,1.,0.,1.])*1e-4
y=np.array([0.,0.,1.,1.])*1e-4
tri=np.array([[0,1,2],[1,3,2]])
ex,ey,mag=model.field(2*x-3*y+1,x,y,tri)
assert np.allclose(ex,-2) and np.allclose(ey,3) and np.allclose(mag,np.sqrt(13))
print("PASS: electric-field reconstruction on an affine potential")
cases={}
for name in ["baseline_double_h1","baseline_double_h0.7","planar_double_h1"]:
    folder=root/"results"/name
    summary=json.loads((folder/"summary.json").read_text())
    a=np.genfromtxt(folder/"peak_field.csv",delimiter=",",names=True)
    assert np.all(np.isfinite(a["peak_field_V_cm"]))
    assert np.all(np.diff(a["reverse_voltage_V"])>0)
    assert a["peak_field_V_cm"][-2]<summary["parameters"]["critical_field_V_cm"]<=a["peak_field_V_cm"][-1]
    mismatch=np.abs(a["anode_A_per_cm"]+a["cathode_A_per_cm"])
    assert np.all(mismatch <= 5e-12+1e-3*np.maximum(np.abs(a["anode_A_per_cm"]),np.abs(a["cathode_A_per_cm"])))
    for f in ["final.vtu","final_field.png","peak_field.png","mesh.png"]:
        assert (folder/f).is_file(),f
    cases[name]=summary
    print(f"PASS: {name}: {summary['criterion_voltage_V']:.3f} V, {summary['nodes']} nodes, max contact mismatch {mismatch.max():.3e} A/cm")
coarse=cases["baseline_double_h1"]["criterion_voltage_V"]
fine=cases["baseline_double_h0.7"]["criterion_voltage_V"]
control=cases["planar_double_h1"]["criterion_voltage_V"]
target=cases["planar_double_h1"]["parameters"]["target_voltage_V"]
change=100*abs(fine-coarse)/fine
error=100*abs(control-target)/target
print(f"Mesh change (relative to finer result): {change:.3f}%")
print(f"Planar control difference from 600 V target: {error:.3f}%")
reference=json.loads((root/"results"/"baseline_extended_h1"/"summary.json").read_text())
precision_change=100*abs(coarse-reference["criterion_voltage_V"])/reference["criterion_voltage_V"]
assert precision_change<0.1,"Precision comparison differs by more than 0.1%"
print(f"PASS: standard vs extended precision differs by {precision_change:.6g}%")
report={"precision_change_percent":precision_change,"cases":{k:{"criterion_voltage_V":v["criterion_voltage_V"],"nodes":v["nodes"]} for k,v in cases.items()},
        "mesh_change_percent":change,"planar_difference_percent":error,
        "scope":"One mesh-refinement comparison and one planar control; no full domain/surface/parameter validation."}
(root/"VALIDATION.json").write_text(json.dumps(report,indent=2))
assert error<10,"Planar control differs by more than 10%; investigate."
assert change<5,"Mesh sensitivity exceeds 5%; refine further."
print("PASS: initial setup checks. Further geometry/material validation is still required.")
