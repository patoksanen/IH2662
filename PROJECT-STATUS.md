# IH2662 project status - 23 September 2026

## Accepted working silicon baseline
User accepted edge_0025 as the working mesh and ended further mesh refinement for now.
Result folder: week3/mesh_investigation/edge_0025
Local refinement target: 0.025 um (not a uniform whole-device mesh).
Nodes: 60076; triangles: 119609.
Constant critical-field threshold: 121.54766993123499 V.
Final field export: 121.749267578125 V reverse-bias magnitude.
Latest threshold change: 0.647% relative to the finer mesh.
Similar final maps were inspected by the user at identical bias for edge_0035 and edge_0025.
Full mesh convergence is not claimed; the peak location changes between meshes. This is a documented limitation, not a requirement to continue refining now.
No impact-ionization model is included.

## Silicon comparison to carry into the report
Ideal hand-calculation target: 600 V.
Flat planar control: 591.718 V, about 1.38% below target.
Curved, unterminated edge working result: 121.548 V, about 20.26% of target.
The flat control checks the ideal planar calculation. The curved edge is a different geometry and must not be tuned to match 600 V.
The accepted mesh remains in its experiment folder. The original parameters.json and Run-Week3.cmd still refer to the earlier baseline; they have not been relabelled as edge_0025.

## Next project stage
The user's IH2662_Project_Roadmap.docx places silicon carbide baseline work in Week 4, before termination structures in Week 5.
First obtain and verify the Week 2 SiC calculation inputs and their sources: material/polytype, donor density, depletion/drift dimensions, critical field and permittivity.
Then assemble a consistent SiC material model, including carrier statistics and transport parameters, and validate a flat control against its own analytical result before interpreting the curved-edge result.
Do not carry silicon-specific intrinsic carrier density or transport constants into SiC without justification.
Material sources, finite-domain sensitivity and surface assumptions remain limitations/checks to address; no extra mesh-refinement runs are scheduled.

## References in this workspace
week3/mesh_investigation/REFINEMENT-0025.md
week3/mesh_investigation/refinement_0025_comparison.json
C:/Users/oksan/Downloads/IH2662_Project_Roadmap.docx
C:/Users/oksan/Downloads/Week2 Project.pdf (not yet extracted in this session)

## Week 4 guard-ring setup - created 23 September 2026
The user chose to complete the core silicon 2D termination study before moving to SiC. This supersedes the earlier roadmap-order note above; the SiC hand calculations are ready for the later material comparison.
Created week4/START-HERE.md, guard_ring.py, solver_core.py, parameters.json, Run-Week4.cmd and Open-Week4-ParaView.cmd.
Initial uncontacted p ring: 3 um surface junction gap, 2 um implant window (49-51 um), 3 um diffusion depth, peak acceptors 1e17 cm^-3. These are starting assumptions, not optimized dimensions.
Local target 0.025 um at both main edge and ring. Mesh: 156242 nodes, 311557 triangles.
Geometry/doping separation, triangular mesh area, DEVSIM import, independently evaluated doping, two external contacts only, and positive node volumes all passed.
Results: week4/results/guard_ring_gap3_h0.025/structure_closeup.png and structure.vtu.
No equilibrium or reverse-bias sweep has been run for the guard ring. Next inspect the structure, then run week4/Run-Week4.cmd run. The sweep is configured to save an identical-bias field map at 121.749267578125 V if reached before the threshold.
