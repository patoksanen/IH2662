# IH2662 project status

**Status date:** 26 September 2026

## Scope

The project currently studies 2-D silicon junction termination. Week 1 is the
installation/tutorial path. Week 3 establishes a plain curved-edge baseline
and numerical controls. Week 4 adds one uncontacted floating guard diffusion.
A separate oxide field-plate case is now complete on Windows. The work is exploratory numerical research, not a validated device rating.

## Verified results

| Case | Criterion voltage | Mesh / note |
|---|---:|---|
| Flat planar control | 591.718 V | 1,478 nodes; 1.38% below 600 V |
| Curved edge, baseline | 127.140 V | 7,610 nodes; standard Week 3 case |
| Curved edge, finer | 131.357 V | 15,369 nodes; 3.21% change |
| Curved edge, accepted local refinement | 121.548 V | `week3/mesh_investigation/edge_0025`, 60,076 nodes |
| Floating guard ring, macOS rerun | 171.869 V | 156,010 nodes; convergence not established |
| Floating guard ring, original Windows run | 166.764 V | 156,242 nodes; archived under platform_runs/windows-20260924 |
| Field plate, Windows | 189.147 V | 1 um oxide, 5 um extension; convergence not established |

The accepted Week 3 local-refinement result is the reference used for the
Week 4 equal-bias comparison. The Week 3 standard baseline remains useful for
the documented control workflow; these are different meshes and must not be
silently substituted for one another.

## What the results mean

The planar control reproduces the analytical 600 V scale, within the expected
effects of the smooth Gaussian junction and finite numerical model. The curved
edge concentrates electric field and reaches the fixed 262,000 V/cm criterion
far earlier. The initial guard ring raises the criterion relative to the plain
edge, but the dominant peak moves to the outer ring edge.

Every threshold is a **constant-critical-field estimate**. No
impact-ionization or avalanche model is included. The separate field-plate model includes charge-free oxide electrostatics and an anode-connected electrode, but no oxide-breakdown/leakage, surface-charge or trap model. Do not report these numbers as measured or predictive
avalanche voltages.

## Validation completed

- Gmsh mesh generation and import.
- Independent doping and geometry checks.
- Positive mesh volumes.
- DEVSIM equilibrium and reverse-bias convergence.
- Electric-field reconstruction test.
- Contact-current balance.
- Planar analytical control.
- Initial local mesh sensitivity.
- Equal-bias Week 3/Week 4 field-map comparison.

## Open limitations

1. Guard-ring mesh convergence is not established.
2. Full domain-width, contact-placement, and outer-boundary sensitivity is
   not established.
3. Material and transport assumptions need sourced references before a final
   technical report.
4. The model is a straight 2-D cross-section; the ring is not an axisymmetric
   circular device.
5. The ring dimensions are a starting design, not an optimization.
6. SiC work must use separately sourced SiC parameters; do not reuse silicon
   intrinsic density or mobility values.

## Reproduction

Use `README.md`, `SETUP.md`, and the three `START-HERE` guides. All commands
are provided for Windows and macOS. Outputs are written under the relevant
`results/` directory; use a new output directory for experimental variants.

## Field-plate completion and integration
The full Windows field-plate sweep completed on 24 September: silicon threshold 189.147324 V, final bias 189.749268 V, oxide peak 6.02685 MV/cm and final contact-current imbalance 0.622%. The exact 121.749267578125 V comparison snapshot was saved. Files are in week4/field_plate/results/plate_L5_tox1_h0.025/.

The numerical implementation passed mesh/import/doping checks, an analytical two-dielectric capacitor check, equilibrium and a 1 V smoke test. The completed sweep's finite values, bias ordering, crossing interpolation and interface/plate residuals were also checked. These checks do not establish physical accuracy or mesh convergence.

During integration, the collaborator's macOS support, documentation and rerun results were retained. Original Windows records in overwritten result folders, including matching local mesh/VTK files, were moved to platform_runs/windows-20260924/. The accepted edge_0025 and field-plate folders were not moved. Consult the archive README for provenance. Large datasets remain local, as before.

Next: compare all three designs at the same bias, distinguish platform/mesh differences, and assess field-plate and oxide-edge sensitivity before optimizing or interpreting a device rating. The user chose to complete the core silicon 2D termination study before SiC; their SiC hand calculations are ready.
