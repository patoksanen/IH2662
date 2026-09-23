# IH2662 Week 1: your first simulation session

Everything here belongs to the separate Python environment in `.venv`.
Open PowerShell in this folder (File Explorer address bar: type `powershell`).
Use `./ih2662.cmd` below so Windows finds Python and the DEVSIM math library.
DEVSIM and PyVista are Python libraries; they do not have separate desktop editors.

## What the four tools do

Gmsh defines geometry and divides it into small triangles (2D) or tetrahedra (3D).
DEVSIM applies material properties, doping, contacts and equations to that mesh,
then solves for potential, electrons and holes. Electric field follows from the
potential gradient. ParaView displays result files through a graphical interface.
PyVista lets you make repeatable visualizations in Python.

Workflow: geometry -> mesh -> physics and bias -> solve -> plots -> validation.

## 1. Run the official 1D diode (about 10 minutes to explore)

    ./ih2662.cmd week1.py diode

The original code is `examples/diode/diode_1d.py`; helpers are in `diode_common.py`.
Open the source in your text editor and follow these steps:
1. CreateMesh defines the 1D points, semiconductor region and two contacts.
2. SetParameters and SetNetDoping set material values and the p/n doping.
3. InitialSolution and the first solve find an electrostatic starting solution.
4. DriftDiffusionInitialSolution adds the electron and hole transport equations.
5. The while loop raises the top contact from 0 to 0.5 V in 0.1 V steps.
6. PrintCurrents reports contact currents; write_devices saves the state.

Open `results/diode_1d.png` and `results/diode_1d.csv`.
The plots show the FINAL 0.5 V state, not the full bias sweep.
Position in the CSV is cm; the plot converts it to micrometres (1 cm = 10,000 um).
Carrier densities are in cm^-3. A logarithmic axis makes many orders of magnitude visible.
This is a forward-bias installation example, not a breakdown-voltage measurement.
Exercise: identify the electron-rich and hole-rich sides using the carrier curves.
Copy the example before changing it; try a smaller bias step and compare convergence.

## 2. Generate and explore the official 2D MOSFET mesh

    ./ih2662.cmd week1.py mesh
    ./ih2662.cmd week1.py gmsh

The geometry is `examples/mobility/gmsh_mos2d.geo`.
The generated mesh is `gmsh_mos2d_generated.msh` in the same folder.
Drag to rotate, scroll to zoom; use an XY view for this flat cross section.
Inspect the named physical groups: bulk, oxide, gate and the contacts/interfaces.
These names connect geometry to DEVSIM regions and boundary conditions.
Smaller elements resolve sharp changes better but increase solve cost.
Our generator saves ASCII MSH 2.2 for compatibility with the DEVSIM example.
The generated mesh is separate from the packaged reference mesh.

## 3. Solve the official 2D MOSFET

    ./ih2662.cmd week1.py mos

Read `examples/mobility/gmsh_mos2d_create.py` to see the Gmsh import and physical
name mapping. Read `gmsh_mos2d.py` for the physics and voltage ramps.
This command initially uses the packaged reference `gmsh_mos2d.msh`.
It exports the final state to `results/mos2d.vtm` and companion files.
Keep the VTM and its companion files together when copying results.
A MOSFET is the roadmap's training example, not the final power-junction design.

## 4. View it with ParaView

Launch ParaView from the Start menu.
1. File > Open: choose `C:/Users/oksan/IH2662/results/mos2d.vtm`.
2. Click Apply in the Properties panel (opening alone may not display the data).
3. Select Potential in the coloring dropdown and click Rescale to Data Range.
4. Choose Surface With Edges to see the mesh and use the +Z view for the XY plane.
5. Select logElectrons to explore the carrier distribution in the silicon regions.
6. File > Save Screenshot exports a picture. File > Save State saves your view setup.

Potential is voltage; it is not electric-field magnitude. Do not call the region
with the highest potential the region with the highest electric field.

## 5. View the same result with PyVista

    ./ih2662.cmd week1.py view

Drag to rotate, scroll to zoom, press r to reset the camera, q to close.
To save a repeatable picture without opening a viewer:

    ./ih2662.cmd week1.py screenshot

Read the small `view()` function in week1.py: read loads the VTM, combine joins
its blocks for plotting, add_mesh chooses the scalar/coloring, view_xy sets the camera.
Exercise: change Potential to logElectrons in a copy and compare the images.

## Week 1 completion and limits

Check logs for successful runs, rather than assuming that an import proves a solver works.
Repeat installation and the diode run on your teammate's laptop; this setup is local to yours.
The roadmap also asks your team to choose voltage class and 3D scope and send a proposal.
Those decisions and sending the proposal are not performed by this installation.
Before the power-device study, establish your Week 2 physical parameters and units.
Mesh refinement and comparison with an analytical result are needed before trusting a
breakdown estimate. Reaching an assumed critical field is a criterion, not an automatic
avalanche-physics model.

## Official references

- Gmsh: https://gmsh.info/doc/texinfo/gmsh.html
- DEVSIM installation: https://github.com/devsim/devsim/blob/main/INSTALL.md
- DEVSIM diode: https://devsim.net/examples_diode.html
- DEVSIM meshing: https://devsim.net/meshing.html
- ParaView: https://docs.paraview.org/en/latest/UsersGuide/introduction.html
- PyVista: https://docs.pyvista.org/getting-started/

The official example files were copied from the installed DEVSIM 2.11.0 distribution;
their original copyright and license headers are retained. week1.py is a teaching wrapper.
