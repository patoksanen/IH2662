# IH2662 start here

This page is the shortest complete path from a fresh clone to the first
validated simulation. Use the command set for your operating system; do not
mix Windows and macOS path syntax.

## 1. Install and verify

Read `SETUP.md` first.

**Windows (PowerShell):**

```powershell
.\Setup.cmd
.\Setup.cmd -CheckOnly
```

**macOS (Terminal):**

```bash
./setup.sh
./ih2662.sh check_setup.py
```

The smoke check verifies pinned packages, Gmsh meshing, meshio, PyVista,
Matplotlib, and a real DEVSIM diode solve. It does not run the long Week 3/4
sweeps.

## 2. Week 1 tutorial

Run these in order:

```text
diode -> mesh -> mos -> view -> screenshot
```

Windows:

```powershell
.\ih2662.cmd week1.py diode
.\ih2662.cmd week1.py mesh
.\ih2662.cmd week1.py mos
.\ih2662.cmd week1.py view
.\ih2662.cmd week1.py screenshot
```

macOS:

```bash
./ih2662.sh week1.py diode
./ih2662.sh week1.py mesh
./ih2662.sh week1.py mos
./ih2662.sh week1.py view
./ih2662.sh week1.py screenshot
```

Inspect `results/diode_1d.png`, `results/mos2d.png`, and
`results/paraview_mos2d.png`. The diode is a forward-bias installation
example; it is not a breakdown simulation.

## 3. Week 3 silicon baseline

Read `week3/START-HERE.txt` for assumptions, equations, units, controls, and
interpretation. The minimum validated sequence is:

```text
mesh -> equilibrium -> run -> planar control -> finer mesh -> check_results.py
```

Windows:

```powershell
.\ih2662.cmd week3\silicon_baseline.py mesh
.\ih2662.cmd week3\silicon_baseline.py equilibrium
.\ih2662.cmd week3\silicon_baseline.py run
.\ih2662.cmd week3\silicon_baseline.py run --planar
.\ih2662.cmd week3\silicon_baseline.py run --mesh-scale 0.7
.\ih2662.cmd week3\check_results.py
```

macOS:

```bash
./ih2662.sh week3/silicon_baseline.py mesh
./ih2662.sh week3/silicon_baseline.py equilibrium
./ih2662.sh week3/silicon_baseline.py run
./ih2662.sh week3/silicon_baseline.py run --planar
./ih2662.sh week3/silicon_baseline.py run --mesh-scale 0.7
./ih2662.sh week3/check_results.py
```

Expected validated values are approximately 127.14 V for the standard curved
case, 131.36 V for the finer mesh, and 591.72 V for the planar control.

## 4. Week 4 floating guard ring

Read `week4/START-HERE.md` before changing parameters. Run:

Windows:

```powershell
.\ih2662.cmd week4\guard_ring.py mesh
.\ih2662.cmd week4\guard_ring.py check
.\ih2662.cmd week4\guard_ring.py run
```

macOS:

```bash
./ih2662.sh week4/guard_ring.py mesh
./ih2662.sh week4/guard_ring.py check
./ih2662.sh week4/guard_ring.py run
```

The saved initial design gives approximately 171.87 V. This is a promising
comparison, not an optimized design or a converged guard-ring result.

## 5. Viewing outputs

Use ParaView for `.vtu`/`.vtm` files and PyVista for scripted screenshots.

| Dataset | Windows | macOS |
|---|---|---|
| Week 1 MOSFET | `Open-ParaView.cmd` | `./Open-ParaView.command` |
| Week 3 final field | `week3/Open-Week3-ParaView.cmd` | `./week3/Open-Week3-ParaView.command` |
| Week 4 structure | `week4/Open-Week4-ParaView.cmd` | `./week4/Open-Week4-ParaView.command` |

In ParaView click **Apply**, select the documented scalar (`ElectricField_V_cm`
or `DopingSignedLog10`), enable **Surface With Edges**, use **+Z**, and
rescale the color range. Never interpret `Potential_V` as electric field.
