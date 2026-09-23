"""Summarize completed mesh experiments and generate report figures."""
from pathlib import Path
import hashlib, json
import numpy as np
import pyvista as pv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mt
root=Path(__file__).resolve().parent
spec=[
("Original",root.parent/"results"/"baseline_double_h1"),
("Global x0.7",root.parent/"results"/"baseline_double_h0.7"),
("Field only",root/"field_only"),
("Local 0.10 um",root/"edge_010"),
("Local 0.07 um",root/"edge_007"),
("Local 0.05 um",root/"edge_005"),
("Bulk max 1.5 um",root/"bulk15"),
("Local 0.10 + bulk 1.5",root/"edge_010_bulk15"),
]
rows=[]
for label,folder in spec:
    s=json.loads((folder/"summary.json").read_text())
    csv=np.genfromtxt(folder/"peak_field.csv",delimiter=",",names=True)
    assert np.isfinite(csv["peak_field_V_cm"]).all()
    assert np.all(np.diff(csv["reverse_voltage_V"])>0)
    assert csv["peak_field_V_cm"][-2]<262000<=csv["peak_field_V_cm"][-1]
    g=pv.read(folder/"final.vtu")
    t=g.cells.reshape(-1,4)[:,1:]; v=g.points[t,:2]; c=v.mean(axis=1)
    i=int(g["ElectricField_V_cm"].argmax())
    lengths=np.stack([np.linalg.norm(v[:,1]-v[:,0],axis=1),np.linalg.norm(v[:,2]-v[:,1],axis=1),np.linalg.norm(v[:,0]-v[:,2],axis=1)],axis=1)
    row={"case":label,"folder":str(folder),"voltage_V":s["criterion_voltage_V"],"nodes":s["nodes"],"triangles":s["triangles"],"peak_x_um":float(c[i,0]),"peak_depth_um":float(c[i,1]),"peak_max_edge_um":float(lengths[i].max()),"E_at_100V_interpolated_V_cm":float(np.interp(100,csv["reverse_voltage_V"],csv["peak_field_V_cm"])),"max_current_imbalance_A_per_cm":float(np.abs(csv["anode_A_per_cm"]+csv["cathode_A_per_cm"]).max())}
    rows.append(row)
(root/"comparison.json").write_text(json.dumps(rows,indent=2))
fig,ax=plt.subplots(figsize=(10,5.8))
ax.barh([r["case"] for r in rows],[r["voltage_V"] for r in rows],color=["#888888","#888888","#cc8844","#4477aa","#4477aa","#228833","#888888","#aa4499"])
for i,r in enumerate(rows): ax.text(r["voltage_V"]+0.25,i,f'{r["voltage_V"]:.2f} V; {r["nodes"]:,} nodes',va="center",fontsize=9)
ax.set_xlim(115,143); ax.invert_yaxis()
ax.set(xlabel="Constant-field-criterion voltage (V)",title="Same silicon device and physics; different meshes")
fig.tight_layout(); fig.savefig(root/"comparison.png",dpi=150); fig.savefig(root/"comparison.jpg",dpi=120); plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11,4.5),sharex=True,sharey=True)
for ax,(label,folder) in zip(axes,[spec[0],spec[5]]):
    g=pv.read(folder/"final.vtu"); t=g.cells.reshape(-1,4)[:,1:]
    tr=mt.Triangulation(g.points[:,0],g.points[:,1],t)
    mag=g["ElectricField_V_cm"]; i=mag.argmax(); c=g.points[t[i]].mean(axis=0)
    im=ax.tripcolor(tr,facecolors=mag/1e5,cmap="inferno",vmin=0,vmax=2.7)
    ax.triplot(tr,color="white",linewidth=.25,alpha=.7)
    ax.tricontour(tr,g["NetDoping_cm-3"],levels=[0],colors=["cyan"])
    ax.plot(c[0],c[1],"gx",markersize=9)
    ax.set(xlim=(40.5,44),ylim=(2.5,0),xlabel="x (um)",title=label)
    ax.set_aspect("equal")
axes[0].set_ylabel("Depth (um)")
fig.suptitle("Near each run's threshold: cyan = junction; green = peak-field cell")
fig.subplots_adjust(right=.86,bottom=.15,top=.83,wspace=.13)
cax=fig.add_axes([.89,.17,.02,.62]); fig.colorbar(im,cax=cax,label="Electric field (100,000 V/cm)")
fig.savefig(root/"peak_region_comparison.png",dpi=160); fig.savefig(root/"peak_region_comparison.jpg",dpi=110); plt.close(fig)
local=[r for r in rows if r["case"] in ("Local 0.10 um","Local 0.07 um","Local 0.05 um")]
changes=[100*abs(local[i+1]["voltage_V"]-local[i]["voltage_V"])/local[i+1]["voltage_V"] for i in range(2)]
meta={"source_sha256":hashlib.sha256((root.parent/"silicon_baseline.py").read_bytes()).hexdigest(),"local_successive_changes_percent":changes,"scope":"mesh-resolution diagnosis, not validated device physics or asymptotic error bound"}
(root/"study_metadata.json").write_text(json.dumps(meta,indent=2))
print(json.dumps(rows,indent=2))
print("Local successive changes (%)",changes)

base=rows[0]; field_only=rows[2]
local10=rows[3]; local07=rows[4]; local05=rows[5]
bulk=rows[6]; combined=rows[7]
table="\n".join(f"| {r['case']} | {r['nodes']:,} | {r['voltage_V']:.3f} | {r['peak_max_edge_um']:.3f} |" for r in rows)
report=f"""# Week 3 mesh investigation — 21 September 2026

The original mesh is geometrically valid, but its resolution was not demonstrated sufficient for a precise peak-field breakdown estimate. The conspicuous density on the left is partly the sizing rules; the accuracy issue is inadequate and unverified resolution of the peak-field region.

## Controlled results
All cases use the same device dimensions, doping profile, contacts, materials and critical-field criterion. Only meshing changes. These are **field-threshold estimates**, not avalanche-model predictions.

| Mesh | Nodes | Threshold (V) | Longest edge of peak-field triangle (um) |
|---|---:|---:|---:|
{table}

The standard and extended precision solutions on the original mesh gave the same threshold. This makes mesh discretization, rather than solver precision alone, the relevant next question.

## What was wrong with the mesh strategy?
1. **Small point sizes were spreading into the device.** The generator assigns 0.30 um to points along the anode-side boundary while also specifying a background size field. Gmsh normally combines sizing sources and extends boundary sizes inward. The script did not disable that behavior. Removing point/boundary-driven sizing reduced the mesh from {base['nodes']:,} to {field_only['nodes']:,} nodes ({100*(1-field_only['nodes']/base['nodes']):.1f}% fewer), but moved the threshold by {100*abs(field_only['voltage_V']-base['voltage_V'])/base['voltage_V']:.2f}%. That coarser field-only mesh is a diagnostic, not a validated fix.
2. **Refinement was centered on the doping-zero contour, not the whole high-field region.** The minimum-size band extended only 0.70 um from that contour. The original maximum-field triangle was about 0.954 um from it, on the depleted p-side near the surface (x=42.038 um, depth=0.184 um). The important region was already in the size-transition zone.
3. **The starting spacing was comparable to the doping-gradient length.** For the actual Gaussian acceptor profile, the local e-folding length at the doping-zero junction is 0.267 um. A 0.30 um target provides roughly one element per such length, not several. At the original peak, the local gradient length is about 0.392 um and the triangle's longest edge is 0.358 um. This is not a mesh-accuracy proof by itself, but explains why local refinement was necessary to test.
4. **The convergence check was incomplete.** The original test changed all sizes together (0.30/3.0 um to 0.21/2.1 um), and the threshold shifted 3.16%. The checker's 5% acceptance was a loose initial setup criterion, not a justified accuracy bound. A solver PASS, acceptable triangle shapes, or agreement of a flat control with the hand calculation does not establish convergence of the curved-edge peak field.

## What the additional tests rule out or narrow down
- Original/finer triangle minimum angles were about 34.3/33.3 degrees; no degenerate triangles were found.
- DEVSIM control volumes were positive, and there were no significantly negative edge-coupling weights in the original, global-refinement, field-only, 0.10 um or 0.07 um meshes.
- Halving the bulk-size parameter alone moved the threshold from {base['voltage_V']:.3f} to {bulk['voltage_V']:.3f} V. With the 0.10 um local patch in place, changing the surrounding bulk-size parameter moved it from {local10['voltage_V']:.3f} to {combined['voltage_V']:.3f} V. These tests point away from deep-bulk resolution as the dominant issue, while not constituting a domain-size or full drift-region validation.
- Local sizes of 0.10, 0.07 and 0.05 um gave {local10['voltage_V']:.3f}, {local07['voltage_V']:.3f} and {local05['voltage_V']:.3f} V. Successive changes are {changes[0]:.2f}% and {changes[1]:.2f}% (relative to the finer result).
- Gmsh may display y=0 at the bottom of the screen; the saved plots show depth downward. The dense junction-side corner should not be confused with the physical back-contact corner.

## What to do next
Use explicit, separately controlled sizing for (a) the curved junction and depleted p-side near the surface, (b) the rest of the junction and (c) the drift region. The tested local patch covers x=39–44.5 um and depths 0–4.5 um, with a 1 um transition. Set the global minimum small enough to allow the local field to act.

First stabilize the voltage and peak-field location with successive local refinements; a practical proposed acceptance target is less than 1% change on successive refinements. This is a numerical-study target, not an official course requirement or guaranteed absolute error. After that, simplify boundary-driven refinement and repeat the comparison. Merely removing the visually dense area is not an adequate correction.

Keep mesh convergence separate from testing the finite domain, contacts, surface-boundary assumptions and physical parameter sources. Do not tune a curved-edge result to equal the 600 V flat-junction target.

## Files and reproducibility
- edge_audit.png: original and first global-refinement close-ups.
- peak_region_comparison.png: original versus 0.05 um local refinement.
- comparison.png and comparison.json: all measured results.
- mesh_audit.json: triangle and gradient-length measurements.
- finite_volume_audit.json: DEVSIM geometric weight checks.
- Each experiment subfolder contains the generated .geo, .msh, voltage CSV, plots, VTU, parameters and summary.
- experiment.py reproduces each named variant, using the existing Week 3 model.
- study_metadata.json records the model source hash and local convergence changes.

Original Week 3 model, launchers and result folders were not replaced by these experiments.

## Source
[Gmsh manual — mesh size fields and boundary extension](https://gmsh.info/doc/texinfo/#Specifying-mesh-element-sizes) explains how point sizes, background fields and boundary-size extension interact. Numerical measurements above come from the local generated meshes and DEVSIM runs.
"""
(root/"FINDINGS.md").write_text(report,encoding="utf-8")
