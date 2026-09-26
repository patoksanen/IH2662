# Original Windows simulation records

These records preserve the local Windows runs before integrating the macOS reruns from origin/main at 230253c. They were relocated on 26 September 2026, along with their matching local generated meshes and ParaView datasets, to avoid mixing Windows datasets with macOS summaries. The archive name denotes the historical Windows study set, not a claim that every run happened on that date.

Tracked source of the compact historical results: c366b48 (also unchanged in ca2e4b9). Large meshes/VTK datasets remain excluded from Git and are present only on the original computer.

Paths mirror the original project layout:
- results/: original Week 1 outputs.
- week3/results/baseline_double_h1/: original 127.162764 V result.
- week3/results/baseline_double_h0.7/: original 131.312714 V result.
- week3/results/planar_double_h1/: original planar control and its matching datasets.
- week3/VALIDATION.json: original validation record.
- week4/results/guard_ring_gap3_h0.025/: original 166.764157 V guard-ring run and matching local final.vtu.

The latest macOS run records remain at the original project paths. Their full VTK datasets were not supplied by Git. Do not compare a summary from one platform/run with a field dataset from another.

The accepted edge_0025 baseline and the new field-plate case were not affected by the incoming reruns and remain at their existing paths.
