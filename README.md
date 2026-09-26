# IH2662 silicon junction and termination study

This repository contains a reproducible teaching and research workflow for
2-D silicon power-junction simulations. It progresses from a 1-D diode and
2-D MOSFET tutorial (Week 1), to a curved silicon p-n junction baseline
(Week 3), and finally to an uncontacted floating guard-ring experiment
(Week 4), plus an anode-connected field plate over explicit oxide.

The simulations use **Gmsh** for meshing, **DEVSIM** for semiconductor
equations, and **PyVista/ParaView** for visualization. All voltages reported
as “threshold” or “criterion” values are the bias at which the simulated
maximum electric field crosses **262,000 V/cm**. This is a constant-field
criterion, **not** an avalanche-breakdown voltage: no impact-ionization model
is included.

## Findings at a glance

The baseline and guard-ring results support these conclusions:

1. The planar control reproduces the expected approximately 600 V scale:
   **591.718 V**, or **1.38% below** the nominal 600 V target.
2. Curving the junction edge reduces the fixed-field criterion to **121.548 V**
   in the accepted locally refined reference case. This is the numerical
   signature of edge-field crowding.
3. The first floating guard-ring design raises the criterion to **171.869 V**.
   That is a **41.4% increase** over the accepted plain-edge reference, but the
   peak moves to the outer guard-ring edge. This is an improvement, not proof
   of a converged or optimized termination.

These are simulation findings under the model described below, not measured
device breakdown ratings.

## Results table and data links

All criterion values use the same fixed threshold, **maximum electric field =
262,000 V/cm**. “Last solved bias” is the final bias written by the sweep; it
is not a separate physical threshold.

| Case | Criterion | Last solved bias | Peak field at last bias | Mesh | Primary data |
|---|---:|---:|---:|---:|---|
| Planar control | 591.718 V | 591.749 V | 262,007 V/cm | 1,478 nodes / 2,792 triangles | [`summary.json`](week3/results/planar_double_h1/summary.json) · [`peak_field.csv`](week3/results/planar_double_h1/peak_field.csv) |
| Curved edge, standard mesh | 127.140 V | 127.749 V | 262,924 V/cm | 7,610 / 14,885 | [`summary.json`](week3/results/baseline_double_h1/summary.json) · [`peak_field.csv`](week3/results/baseline_double_h1/peak_field.csv) |
| Curved edge, 0.7 mesh scale | 131.357 V | sweep output | — | 15,369 nodes | [`VALIDATION.json`](week3/VALIDATION.json) |
| Curved edge, accepted local refinement | **121.548 V** | 121.749 V | 262,327 V/cm | 60,076 / 119,609 | [`summary.json`](week3/mesh_investigation/edge_0025/summary.json) · [`peak_field.csv`](week3/mesh_investigation/edge_0025/peak_field.csv) |
| Floating guard ring | **171.869 V** | 172.460 V | 262,659 V/cm | 156,010 / 311,093 | [`summary.json`](week4/results/guard_ring_gap3_h0.025/summary.json) · [`peak_field.csv`](week4/results/guard_ring_gap3_h0.025/peak_field.csv) |

The standard and locally refined curved-edge results are deliberately both
shown: they are different meshes. The accepted local-refinement case is the
reference used for the Week 4 comparison; it must not be silently replaced by
the standard Week 3 result.

## Completed field plate and platform-specific records

The Windows field-plate run gives **189.147 V**, with 1 um oxide and a 5 um extension beyond the junction. Its final oxide peak is **6.027 MV/cm**; no oxide-breakdown model is included, so the silicon threshold is not a device rating. Field-plate mesh convergence is not established.

| Additional case | Criterion | Data |
|---|---:|---|
| Windows guard-ring run | 166.764 V | [archived summary](platform_runs/windows-20260924/week4/results/guard_ring_gap3_h0.025/summary.json) |
| Windows field plate | 189.147 V | [summary](week4/field_plate/results/plate_L5_tox1_h0.025/summary.json), [peak-field CSV](week4/field_plate/results/plate_L5_tox1_h0.025/peak_field.csv), [field plot](week4/field_plate/results/plate_L5_tox1_h0.025/final_field.png) |

The 171.869 V guard-ring entry above is the collaborator's macOS run. The original Windows run used 156,242 nodes, while that rerun used 156,010. Do not silently combine the results or attribute the difference solely to the operating system: the meshes also differ. Original Windows outputs overwritten by the macOS reruns are preserved under [platform_runs/windows-20260924](platform_runs/windows-20260924/README.md). Matching large Windows datasets were relocated there locally and remain excluded from Git.

The accepted local baseline and new field-plate output folders retain their original locations. On this Windows machine, open the archived guard-ring final.vtu for the original 166.764 V run; the default guard-ring folder now contains the macOS CSV/JSON/PNG records, without matching local VTK datasets.

Use `week4/Run-FieldPlate.cmd` on Windows, or `./ih2662.sh week4/field_plate/field_plate.py run --output week4/field_plate/results/new_run` on macOS. The field plate has been tested on Windows; macOS execution of this new case has not yet been verified. See [field-plate instructions](week4/field_plate/START-HERE.md).

## Figures and visual evidence

Open the generated figures directly from the repository:

| Evidence | Figure |
|---|---|
| Week 3 mesh | [`mesh.png`](week3/results/baseline_double_h1/mesh.png) |
| Week 3 equilibrium field | [`equilibrium_field.png`](week3/results/baseline_double_h1/equilibrium_field.png) |
| Week 3 final field | [`final_field.png`](week3/results/baseline_double_h1/final_field.png) |
| Week 3 peak-field map | [`peak_field.png`](week3/results/baseline_double_h1/peak_field.png) |
| Accepted refined-edge peak field | [`peak_field.png`](week3/mesh_investigation/edge_0025/peak_field.png) |
| Week 4 guard-ring structure | [`structure.png`](week4/results/guard_ring_gap3_h0.025/structure.png) · [`close-up`](week4/results/guard_ring_gap3_h0.025/structure_closeup.png) |
| Week 4 equal-bias comparison snapshot | [`bias_121p749268V_field.png`](week4/results/guard_ring_gap3_h0.025/bias_121p749268V_field.png) |
| Week 4 final field | [`final_field.png`](week4/results/guard_ring_gap3_h0.025/final_field.png) |
| Week 4 peak-field map | [`peak_field.png`](week4/results/guard_ring_gap3_h0.025/peak_field.png) |

The equal-bias snapshot is saved at **121.749267578125 V**, allowing the
guard-ring field map to be compared with the accepted plain-edge reference at
the same bias. The recorded comparison shows approximately **35.18% lower
peak field** for the guard-ring design at that equal bias; the guard-ring
criterion itself is the separate 171.869 V result above.

## What was validated

- Gmsh mesh generation and DEVSIM mesh import.
- Independent doping/geometry checks and positive node volumes.
- Equilibrium and reverse-bias solver convergence.
- Electric-field reconstruction and contact-current balance.
- Planar analytical control against the nominal 600 V scale.
- One standard-to-finer mesh comparison and one accepted local-refinement run.
- Equal-bias Week 3/Week 4 field-map comparison.

The machine-readable validation record is
[`week3/VALIDATION.json`](week3/VALIDATION.json); the guard-ring structural
checks are in [`devsim_checks.json`](week4/results/guard_ring_gap3_h0.025/devsim_checks.json).

The Week 3 working mesh is `week3/mesh_investigation/edge_0025/` (60,076
nodes, 0.025 µm local target). The Week 4 guard-ring mesh has 156,010 nodes
and 311,093 triangles. Guard-ring mesh convergence is not established.

## Repository map

| Path | Purpose |
|---|---|
| `week1.py`, `examples/` | Introductory diode and MOSFET workflow |
| `week3/` | Silicon baseline, planar control, mesh sensitivity, validation |
| `week3/mesh_investigation/` | Finer local-mesh experiments and accepted working case |
| `week4/` | Floating guard-ring geometry, solver, results, comparisons |
| `week4/field_plate/` | Separate oxide field-plate model, diagnostics and completed Windows run |
| `week3/parameters.json` | Week 3 inputs |
| `week4/parameters.json` | Week 4 inputs |
| `PROJECT-STATUS.md` | Current research status and limitations |
| `SETUP.md` | Complete installation guide for Windows and macOS |

## Quick start

### Windows

Install 64-bit Python 3.12, then from PowerShell:

```powershell
.\Setup.cmd
.\ih2662.cmd week1.py diode
.\ih2662.cmd week1.py mos
.\ih2662.cmd week3\silicon_baseline.py run
.\ih2662.cmd week4\guard_ring.py run
```

### macOS

Install Python 3.12+ and run from Terminal:

```bash
./setup.sh
./ih2662.sh week1.py diode
./ih2662.sh week1.py mos
./week3/Run-Week3.sh run
./week4/Run-Week4.sh run
```

Both platforms run the same Python sources and write the same CSV, JSON, PNG,
and VTK formats. Windows uses the Intel/MKL lockfile; macOS Apple Silicon
uses `requirements-macos.txt` and DEVSIM’s macOS UMFPACK/OpenBLAS backend.

## Recommended reading order

1. Read `SETUP.md` and complete the smoke check.
2. Follow `START-HERE.md` for the Week 1 tutorial.
3. Follow `week3/START-HERE.txt` for the silicon baseline and controls.
4. Follow `week4/START-HERE.md` for the guard-ring experiment.
5. Read `PROJECT-STATUS.md` before quoting results or planning new work.

## Reproducibility and interpretation

Each simulation records its input snapshot, mesh, peak-field CSV, plots, and
summary JSON. A CSV alone is not proof of a successful run: confirm the final
`PASS` message and inspect the corresponding summary/check files. The planar
control is a separate validation geometry; it must not be used to claim that
the curved edge should reach 600 V. Material sources, finite-domain effects,
surface assumptions, and full guard-ring convergence remain open research
checks.

### Scope of the findings

The threshold is a **constant-critical-field estimate**, not avalanche
breakdown. All cases omit impact ionization and avalanche multiplication. The baseline and guard-ring cases omit oxide and field plates. The separate field-plate case includes an ideal oxide dielectric and connected electrode, but omits oxide breakdown, leakage, fixed charge and traps. The Week 4 ring
is an **uncontacted semiconductor diffusion**, not a metal floating electrode.
The geometry is a straight 2-D cross-section rather than an axisymmetric
circular device. These limitations must be included whenever the numerical
values are cited.

Generated environments, logs, large meshes, and VTK datasets are not required
in a fresh clone. Regenerate them using the platform commands above.
