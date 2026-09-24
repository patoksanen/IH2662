# Week 4 — floating guard-ring experiment

## Purpose and conclusion

Week 4 adds one uncontacted Gaussian p-type diffusion beyond the Week 3
curved silicon junction. It tests whether the ring redistributes edge field
crowding. The ring is a floating semiconductor diffusion, **not** a metal
electrode and not assigned a voltage.

For the initial 3 µm-gap design, the constant-field criterion is **171.869 V**
versus **121.548 V** for the plain-edge reference, a 35.18% increase. At the
criterion the dominant peak moves to the outer ring edge. This does not prove
avalanche improvement: there is no impact-ionization model and ring
convergence is not established.

## Geometry and assumptions

- Silicon width: 120 µm; total thickness: 63 µm.
- Main p diffusion: 3 µm depth, flat extent to x=40 µm, curved edge to x=43 µm.
- Anode: x=0–38 µm; cathode: bottom boundary.
- Ring: 3 µm junction-to-junction surface gap, 2 µm implant window,
  3 µm diffusion depth, nominal surface span x=46–54 µm.
- Donor concentration: `3.67e14 cm^-3`; peak acceptors: `1e17 cm^-3`.
- Temperature: 300 K; silicon relative permittivity: 11.7.
- Outer boundaries are insulating; no oxide, surface charge, field plate,
  traps, or impact ionization is included.

These are documented modelling assumptions, not measured device parameters.
Keep them fixed when comparing termination variants.

## Step-by-step procedure

### 1. Generate the mesh

Windows:

```powershell
.\Run-Week4.cmd mesh
```

macOS:

```bash
./Run-Week4.sh mesh
```

Inspect `results/guard_ring_gap3_h0.025/structure.png` and
`structure_closeup.png`. The structure check should show three surface
junction crossings near x=43, 46, and 54 µm.

### 2. Validate geometry and import

```text
Windows: .\Run-Week4.cmd check
macOS:   ./Run-Week4.sh check
```

Confirm `structure_checks.json` reports positive volumes, two physical
contacts, and no bias solution.

### 3. Solve equilibrium and reverse bias

```text
Windows: .\Run-Week4.cmd run
macOS:   ./Run-Week4.sh run
```

Wait for the final `PASS` message. Inspect `equilibrium_field.png`,
`peak_field.png`, `final_field.png`, `peak_field.csv`, and `summary.json`.
The final field is at the upper crossing bracket, not exactly at the
interpolated criterion voltage.

### 4. Compare at identical voltage

If saved, open `bias_121p749268V.vtu` and
`bias_121p749268V_field.png`. Compare it with the Week 3 plain-edge map using
the same color limits. Inspect the main edge, inner ring edge, and outer ring
edge. The initial run saved this snapshot successfully.

### 5. Interpret and report

Report criterion voltages, mesh sizes, peak coordinates, current balance,
and the exact bias used for map comparisons. State explicitly:

> This is a constant-critical-field estimate for the documented 2-D model;
> it is not an avalanche-breakdown voltage.

Do not call the ring optimized or converged without additional gap/depth/
implant and mesh studies. Use a new `--output` directory for trials.
