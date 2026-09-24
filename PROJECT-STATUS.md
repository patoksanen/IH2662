# IH2662 project status

**Status date:** 24 September 2026

## Scope

The project currently studies 2-D silicon junction termination. Week 1 is the
installation/tutorial path. Week 3 establishes a plain curved-edge baseline
and numerical controls. Week 4 adds one uncontacted floating guard diffusion.
The work is exploratory numerical research, not a validated device rating.

## Verified results

| Case | Criterion voltage | Mesh / note |
|---|---:|---|
| Flat planar control | 591.718 V | 1,478 nodes; 1.38% below 600 V |
| Curved edge, baseline | 127.140 V | 7,610 nodes; standard Week 3 case |
| Curved edge, finer | 131.357 V | 15,369 nodes; 3.21% change |
| Curved edge, accepted local refinement | 121.548 V | `week3/mesh_investigation/edge_0025`, 60,076 nodes |
| Floating guard ring | 171.869 V | 156,010 nodes; convergence not established |

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
impact-ionization, avalanche, breakdown, surface-charge, oxide, or field-plate
physics is included. Do not report these numbers as measured or predictive
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
