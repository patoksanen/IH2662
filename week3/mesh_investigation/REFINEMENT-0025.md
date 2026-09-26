# Local refinement update: 0.025 um

The 0.025 um run completed successfully. Physics and refinement box match the previous local runs.

| Variant | Nodes | Field threshold (V) | Final peak x (um) | Final peak depth (um) |
|---|---:|---:|---:|---:|
| edge_005 | 20661 | 127.840435 | 42.256671 | 0.028884 |
| edge_0035 | 34180 | 120.760831 | 42.074977 | 0.621603 |
| edge_0025 | 60076 | 121.547670 | 41.988574 | 0.006954 |

Voltage change from 0.035 to 0.025 um: 0.647% relative to the finer result. This satisfies the proposed 1% target for this pair only. Full convergence is not established: the previous pair differed by more than 1%, and the peak moved to a near-surface triangle.

In edge_0025 the peak moves from (42.228965, 0.709838) um at 119.7493 V to (41.988574, 0.006954) um at 120.7493 V. Inspect both regions in ParaView; do not assume the previous focal point is the new maximum.

Open edge_0025/final.vtu with ElectricField_V_cm and Surface With Edges. The final export is at 121.7493 V, above the interpolated threshold. Compare saved final maps with that bias difference in mind.

Validation details and final contact-current imbalance are in refinement_0025_comparison.json. These checks verify the run outputs, not physical accuracy or full mesh convergence. The result remains a constant critical-field estimate without impact ionization.

Reproduce from the repository root:

Windows: `ih2662.cmd week3/mesh_investigation/experiment.py edge_0025`

macOS: `./ih2662.sh week3/mesh_investigation/experiment.py edge_0025`

Rerunning replaces this variant output.
