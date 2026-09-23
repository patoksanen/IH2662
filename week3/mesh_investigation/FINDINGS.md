# Week 3 mesh investigation — 21 September 2026

The original mesh is geometrically valid, but its resolution was not demonstrated sufficient for a precise peak-field breakdown estimate. The conspicuous density on the left is partly the sizing rules; the accuracy issue is inadequate and unverified resolution of the peak-field region.

**Convergence status: not established.** The 0.10 -> 0.07 -> 0.05 um local sequence gives 128.02 -> 130.61 -> 127.84 V. The last change is 2.17% and is non-monotonic, so even the finest tested mesh should not be labelled a converged final result.

## Controlled results
All cases use the same device dimensions, doping profile, contacts, materials and critical-field criterion. Only meshing changes. These are **field-threshold estimates**, not avalanche-model predictions.

| Mesh | Nodes | Threshold (V) | Longest edge of peak-field triangle (um) |
|---|---:|---:|---:|
| Original | 7,610 | 127.163 | 0.358 |
| Global x0.7 | 15,366 | 131.313 | 0.235 |
| Field only | 3,189 | 124.376 | 0.423 |
| Local 0.10 um | 10,803 | 128.021 | 0.108 |
| Local 0.07 um | 14,381 | 130.610 | 0.090 |
| Local 0.05 um | 20,661 | 127.840 | 0.055 |
| Bulk max 1.5 um | 15,211 | 127.130 | 0.358 |
| Local 0.10 + bulk 1.5 | 18,742 | 127.732 | 0.108 |

The standard and extended precision solutions on the original mesh gave the same threshold. This makes mesh discretization, rather than solver precision alone, the relevant next question.

## What was wrong with the mesh strategy?
1. **Small point sizes were spreading into the device.** The generator assigns 0.30 um to points along the anode-side boundary while also specifying a background size field. Gmsh normally combines sizing sources and extends boundary sizes inward. The script did not disable that behavior. Removing point/boundary-driven sizing reduced the mesh from 7,610 to 3,189 nodes (58.1% fewer), but moved the threshold by 2.19%. That coarser field-only mesh is a diagnostic, not a validated fix.
2. **Refinement was centered on the doping-zero contour, not the whole high-field region.** The minimum-size band extended only 0.70 um from that contour. The original maximum-field triangle was about 0.954 um from it, on the depleted p-side near the surface (x=42.038 um, depth=0.184 um). The important region was already in the size-transition zone.
3. **The starting spacing was comparable to the doping-gradient length.** For the actual Gaussian acceptor profile, the local e-folding length at the doping-zero junction is 0.267 um. A 0.30 um target provides roughly one element per such length, not several. At the original peak, the local gradient length is about 0.392 um and the triangle's longest edge is 0.358 um. This is not a mesh-accuracy proof by itself, but explains why local refinement was necessary to test.
4. **The convergence check was incomplete.** The original test changed all sizes together (0.30/3.0 um to 0.21/2.1 um), and the threshold shifted 3.16%. The checker's 5% acceptance was a loose initial setup criterion, not a justified accuracy bound. A solver PASS, acceptable triangle shapes, or agreement of a flat control with the hand calculation does not establish convergence of the curved-edge peak field.

## What the additional tests rule out or narrow down
- Original/finer triangle minimum angles were about 34.3/33.3 degrees; no degenerate triangles were found.
- DEVSIM control volumes were positive, and there were no significantly negative edge-coupling weights in the original, global-refinement, field-only, 0.10 um or 0.07 um meshes.
- Halving the bulk-size parameter alone moved the threshold from 127.163 to 127.130 V. With the 0.10 um local patch in place, changing the surrounding bulk-size parameter moved it from 128.021 to 127.732 V. These tests point away from deep-bulk resolution as the dominant issue, while not constituting a domain-size or full drift-region validation.
- Local sizes of 0.10, 0.07 and 0.05 um gave 128.021, 130.610 and 127.840 V. Successive changes are 1.98% and 2.17% (relative to the finer result).
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
