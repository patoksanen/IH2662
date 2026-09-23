# IH2662 - Junction termination simulations

Silicon power-junction studies using Gmsh, DEVSIM and ParaView/PyVista.
Current work compares a plain curved junction with a floating guard ring.
Results use a constant peak-electric-field criterion, not an impact-ionization avalanche model.

## Project layout
- `week1.py`, `examples/`: introductory diode and MOSFET exercises.
- `week3/`: plain silicon junction, planar control and mesh investigation.
- `week3/mesh_investigation/edge_0025/`: accepted working baseline.
- `week4/`: silicon floating guard-ring geometry, solver and results.
- `PROJECT-STATUS.md`: chronological decisions and progress; later entries supersede earlier plans.
- `START-HERE.md`: initial setup and Week 1 walkthrough.

## Current saved results
| Case | Field-threshold estimate |
|---|---:|
| Flat silicon control | 591.718 V |
| Plain curved edge, local 0.025 um target | 121.548 V |
| Initial floating guard ring | 166.764 V |

The guard-ring value is from the saved completed run, not a new independent validation. Neither the guard-ring mesh nor physical-model accuracy is established by this table. See the per-case summaries and investigation notes.

## Running locally
On Windows, install **64-bit Python 3.12**, then double-click **`Setup.cmd`** in the repository root. Include the Python launcher when installing Python. Setup creates `.venv`, installs the pinned dependencies, checks MKL and tests meshing, plot/file output and a small DEVSIM diode solve. It requires internet access for the packages and can take several minutes. It does not run the full project simulations.

To check an existing environment without installing anything:
```powershell
.\Setup.cmd -CheckOnly
```

If Python is not detected automatically:
```powershell
.\Setup.cmd -PythonExe "C:\path\to\python.exe"
```

See [SETUP.md](SETUP.md) for troubleshooting. ParaView is optional and installed separately; setup reports whether it finds an installation. The package versions are pinned for reproducibility. This installer targets Windows and Python 3.12, not other platforms.

From the project root:
```powershell
.\ih2662.cmd week4\guard_ring.py mesh
.\ih2662.cmd week4\guard_ring.py check
.\ih2662.cmd week4\guard_ring.py run --output week4\results\new_guard_ring_run
```
The full bias run may take a long time. The Week 4 guide explains parameters, output protection and identical-voltage comparisons. Some viewer launchers and older notes contain paths for the original Windows computer; adjust those on another machine.

## Included and generated files
Source, parameters, notes, plots and compact CSV/JSON result records are tracked. The Python environment, logs, generated meshes and ParaView datasets are excluded. Original example meshes required by the teaching examples are retained. Existing saved result summaries do not imply that the large generated datasets are included in a clone; regenerate them using the documented commands and a new output folder.

The copied DEVSIM examples retain their original copyright and SPDX license headers. See `THIRD-PARTY-NOTICES.md`. No additional license is granted here for original project files.
