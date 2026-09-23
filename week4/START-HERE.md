# Week 4: first silicon floating guard ring

Start with results/guard_ring_gap3_h0.025/structure_closeup.png.
Open Open-Week4-ParaView.cmd to inspect structure.vtu. Click Apply, choose DopingSignedLog10, Surface With Edges and +Z. Coordinates in VTU are micrometres; Gmsh coordinates are cm. Negative net doping is p-type. This is a structure/doping preview, not a solved electric-field map.

## Initial design
The original silicon material, main junction, 120 um width, 63 um total thickness and two external contacts are retained. One Gaussian p-type diffusion is added beyond the main junction edge at x=43 um. It has a nominal 3 um junction-to-junction surface gap, a 2 um implant window (x=49 to 51 um), and 3 um depth. Its nominal surface span is x=46 to 54 um. Peak acceptors are 1e17 cm^-3. Acceptor tails add, so actual NetDoping=0 contours are checked separately in structure_checks.json.

These dimensions are adjustable starting assumptions, not an optimized or measured design. A ring appears as one isolated p region in this straight-edge 2D cross-section; this is not a circular axisymmetric model.

The ring has no contact or imposed voltage. Poisson and electron/hole continuity with the existing SRH model determine its potential during a DC solve. It is an uncontacted diffused ring, not a floating metal electrode. Only anode and cathode are physical contacts. Insulating outer boundaries retain the Week 3 assumptions; no oxide, surface charge or impact ionization is added.

## Mesh
The accepted 0.025 um target and main-edge refinement box are retained. A second fine box covers both ring edges and its junction. This is a larger new mesh, not the exact Week 3 mesh; matching target size does not establish convergence of the guard-ring solution. Week 3 outputs are preserved.

## Commands (PowerShell in week4)

```powershell
.\Run-Week4.cmd mesh
.\Run-Week4.cmd view-mesh
.\Run-Week4.cmd check
.\Run-Week4.cmd run
```

The mesh and check actions do not solve a bias sweep. The run action solves equilibrium, then ramps reverse bias to the constant 262000 V/cm peak-field criterion. It can take substantially longer than the baseline because the ring requires more fine elements. Wait for the final PASS, not just a CSV file. No improved voltage is assumed in advance.

The run saves equilibrium.vtu, final.vtu, field PNGs, peak_field.csv and summary.json. It also saves bias_121p749268V.vtu and the corresponding field PNG at exactly 121.749267578125 V if the sweep reaches it before stopping. This matches the accepted baseline final.vtu; use equal color scales for comparison. If the guard ring reaches the criterion earlier, the comparison snapshot will be absent and this is recorded in summary.json.

The final map is at the upper crossing bracket, not the interpolated criterion voltage. Ring potential can vary spatially: inspect Potential_V in the ring rather than assuming a prescribed value.

Changing parameters in parameters.json requires a new output folder, for example:

```powershell
.\Run-Week4.cmd run --output results\guard_ring_trial2
```

Existing solver outputs are protected. Use --overwrite only when intentionally replacing an existing run. To keep an equilibrium-only trial separate use --output results/equilibrium_trial.

## What to compare after solving
Compare the criterion voltage with the accepted plain-edge 121.54767 V. Compare both field maps at the saved identical bias and inspect all three edge regions (main junction, inner ring edge, outer ring edge). Record peak position and contact-current balance, and assess whether the ring spreads the field or introduces another dominant peak. The ideal 600 V target and flat control 591.718 V remain separate references.

## References and scope
The solver is adapted from ../week3/silicon_baseline.py, with its source hash recorded in provenance.json. DEVSIM contact setup uses the locally installed examples/diode/diode_common.py and simple_physics helpers (DEVSIM LLC, Apache-2.0).
- DEVSIM models: https://devsim.net/models.html
- Gmsh mesh sizing: https://gmsh.info/doc/texinfo/#Specifying-mesh-element-sizes
- Floating guard-ring design context (different sensor application, not a source for our dimensions): https://arxiv.org/abs/1609.04044

The present task prepares and checks the structure and solver import. A guard-ring threshold result is not established until a complete bias run and its checks have finished.
