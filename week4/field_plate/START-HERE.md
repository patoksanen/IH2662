# Silicon field plate - initial design

This is a separate field-plate comparison case, with no guard ring. The original plain silicon doping profile and transport parameters are retained. Field maps and thresholds from different termination cases belong in separate folders.

## Start here
Open results/plate_L5_tox1_h0.025/structure_closeup.png to see the main junction, oxide and connected metal boundary. In week4, double-click Run-FieldPlate.cmd:
1. Generate the structure and mesh.
2. View the mesh in Gmsh.
3. Check the DEVSIM import, doping and equation setup.
4. Run the full reverse-bias sweep.
5. Run an independent equilibrium-to-1 V diagnostic in diagnostics/.

Open-FieldPlate-ParaView.cmd opens the full-run final.vtm if present, otherwise structure.vtm. It searches for installed ParaView versions. Click Apply and +Z. For structure.vtm, use MaterialId to distinguish silicon (0) from oxide (1); use the Silicon block and DopingSignedLog10 for doping. Use Surface With Edges to inspect triangles. Gmsh coordinates are cm; exported VTK coordinates are micrometres.

## Geometry and initial assumptions
- Silicon: 120 um width and 63 um total thickness; donor doping 3.67e14 cm^-3.
- Main Gaussian p diffusion: 1e17 cm^-3 peak and 3 um junction depth, with curved surface edge at x=43 um.
- Anode ohmic contact: x=0 to 38 um at y=0; cathode at the bottom.
- SiO2: x=38 to 120 um, from y=-1 to 0 um; relative permittivity 3.9.
- Anode-connected plate: vertical oxide boundary at x=38 um, then the oxide top to x=48 um. This is a 10 um overhang from the contact edge, or **5 um beyond the p-n junction surface edge**.
- Ideal metal is represented by a fixed-potential boundary, not a meshed metal volume. Both plate and anode follow the same applied reverse bias.
- The oxide metal potential includes the p-ohmic built-in potential reference, so it is not incorrectly equated to raw applied voltage. The default ideal metal is matched to the p-contact reference (plate_workfunction_offset_V=0). No specific real metal work function is claimed. The shared-corner model currently requires this offset to stay zero; another metal reference requires revising the boundary model.
- Remaining external boundaries have zero normal flux. No air domain, interface traps, fixed oxide charge, surface recombination, tunnelling or dielectric leakage/breakdown model is included.

The 1 um oxide and 5 um extension are adjustable starting choices, not optimized or course-prescribed dimensions. Adding oxide changes the surface electrostatics as well as adding the electrode. An oxide-only control could later separate those effects.

## Equations and criterion
Silicon solves Poisson plus electron/hole drift-diffusion with the same SRH and constant mobilities as the accepted baseline. Oxide solves charge-free electrostatics only: div(epsilon grad(phi))=0. Potential is continuous at the silicon/oxide interface; the assembled interface equation balances normal displacement flux for zero sheet charge. Carriers cannot flow into oxide. Anode and plate meet at a shared endpoint; their default reference potentials agree there, and solved interface/plate residuals are checked.

The stopping criterion is the maximum **silicon** field reaching 262000 V/cm. Oxide fields are recorded separately; the silicon threshold must never be applied to oxide. Sharp ideal metal edges can produce mesh-sensitive oxide peaks, so oxide maxima are diagnostics, not validated dielectric-breakdown predictions. No impact-ionization model is included.

## Mesh and validation
The accepted 0.025 um local target is retained around the curved junction, with extra refinement at the contact/oxide corner and plate tip. The oxide also has its own 0.15 um background target. This is a new two-region mesh; convergence of the field plate is not established by reusing a mesh target.

check_interface.py checks the same dielectric contact/interface helpers against an analytical two-layer capacitor at 1 and 2 V, including electric fields, charge balance and potential continuity. It does not validate the complete device physically.

The check action verifies material areas, independent silicon doping, positive control volumes and oxide-only electrode equations. The smoke action checks equilibrium and a short reverse ramp to 1 V with the actual working mesh. A successful smoke test does not establish convergence of the full high-voltage sweep.

## Outputs
Full-run outputs: results/plate_L5_tox1_h0.025/.
Short-test outputs: diagnostics/plate_L5_tox1_h0.025/.

- structure.vtm and its companion directory: two-material mesh and doping preview.
- equilibrium.vtm, final.vtm and their companion directories: solved silicon and oxide fields.
- *_silicon.vtu and *_oxide.vtu: standalone regional datasets, convenient for comparing silicon only.
- *_field.png: separate silicon and oxide panels, each with its own color scale.
- peak_field.csv: silicon/oxide peak fields and positions, silicon contact currents and boundary residuals at each completed voltage.
- peak_field.png: silicon peak field versus reverse bias.
- summary.json: completion status and interpolated silicon threshold, if reached.
- bias_121p749268V*: exact 121.749267578125 V comparison snapshot, saved if reached before the silicon criterion.

A diagnostic summary at 1 V is not a breakdown result. Wait for the full-run status silicon_threshold_reached before reporting a threshold. Solver failures leave a partial CSV, not a completed threshold. Even successful full runs need physical interpretation, current-balance assessment and mesh/domain checks.

## Commands
From week4:
```powershell
.\Run-FieldPlate.cmd mesh
.\Run-FieldPlate.cmd check
.\Run-FieldPlate.cmd smoke
.\Run-FieldPlate.cmd run
```
For a new parameter case, edit a copy of field_plate/parameters.json and choose a separate result folder:
```powershell
.\Run-FieldPlate.cmd run --parameters field_plate/my_parameters.json --output field_plate/results/trial2
```
Existing solved cases are protected. --overwrite explicitly replaces generated solver outputs for unchanged parameters. Keeping separate case directories is preferable for research records.

## References
- DEVSIM equation assembly and interfaces: https://devsim.net/models.html
- Installed DEVSIM 2.11.0 helpers: devsim/python_packages/simple_physics.py, CreateOxidePotentialOnly, CreateOxideContact and CreateSiliconOxideInterface; DEVSIM LLC, Apache-2.0. The installed helper uses relative oxide permittivity 3.9; source material constants for the final report separately.
- Local working example of silicon/oxide coupling: examples/mobility/gmsh_mos2d.py.
- Field-plate edge dependence on geometry (not a source for our initial dimensions): https://doi.org/10.1049/ip-smt:20030852

## Completed Windows run
The full sweep completed on 24 September 2026 at a silicon threshold estimate of 189.147324 V. Final bias: 189.749268 V; oxide peak: 6.02685 MV/cm; final contact-current imbalance: 0.622%. The silicon hotspot is near x=47.93477 um, depth=0.00594 um. The same-bias 121.749267578125 V snapshot is present. This is not a validated device rating: field-plate mesh convergence and oxide breakdown remain unmodelled/unverified.
