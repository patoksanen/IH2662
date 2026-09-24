# Set up IH2662 on Windows and macOS

## Windows
1. Install 64-bit Python 3.12 from https://www.python.org/downloads/windows/ and include the Python launcher.
2. Double-click `Setup.cmd`, or run `.\Setup.cmd` from PowerShell.
3. Confirm the final `PASS: IH2662 simulation environment is ready.` message.

## macOS
1. Install Python 3.12 or newer and ensure `python3` is on PATH.
2. From Terminal, run `./setup.sh`. It creates `.venv`, installs the ARM-compatible dependency subset, and runs the smoke checks.
3. Use `./ih2662.sh` for simulations. The macOS setup intentionally omits Intel MKL packages unavailable on Apple Silicon; DEVSIM uses its macOS UMFPACK/OpenBLAS backend.
4. Optional ParaView: `brew install --cask paraview`.

Both platforms should read `week4/START-HERE.md` after setup. Regenerate meshes or
run a new simulation case to obtain ParaView datasets; large datasets are not in Git.

No administrator privileges are normally required when the project folder is writable. `Setup.cmd` uses a process-local PowerShell execution policy and does not change the machine policy.

## What setup does
- Uses an existing .venv if present; otherwise creates one with 64-bit Python 3.12.
- Installs the exact versions in requirements-lock.txt. On an existing environment, this may align installed package versions with the lock file. Use check-only mode to avoid installation.
- Runs pip check and verifies every locked version.
- Checks the MKL DLL path expected by ih2662.cmd and sets DLL paths and thread limits for its own checks.
- Generates a tiny Gmsh mesh, reads it with meshio, saves/reads a PyVista dataset, generates a Matplotlib PNG, and runs the official 1D DEVSIM diode example with the project UMFPACK backend.
- Keeps test output in a temporary directory, leaving week3/week4 simulation results untouched.
- Detects ParaView on PATH or under Program Files, without installing or launching it.

On macOS, install ParaView with `brew install --cask paraview`. The repository
includes `Open-ParaView.command`, `week3/Open-Week3-ParaView.command`, and
`week4/Open-Week4-ParaView.command` for opening the generated datasets. These
launchers prefer a corrected user-local copy at
`~/Applications/ParaView-6.1.1.app` when present, then fall back to the
system app or Homebrew launcher.

## Windows commands
```powershell
.\Setup.cmd
.\Setup.cmd -CheckOnly
.\Setup.cmd -PythonExe "C:\path\to\python.exe"
```
Setup.cmd pauses before closing so errors remain visible. For an unattended terminal run:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

## Troubleshooting
- **Python not found or wrong version:** install 64-bit Python 3.12, or provide its full executable path with -PythonExe. This option is used only when creating a new environment.
- **Existing .venv uses another Python version or is incomplete:** rename it to preserve it, then rerun setup with Python 3.12. Setup never deletes an existing environment.
- **Download/installation failure:** check internet access, proxy settings and the printed pip error, then rerun setup. No silent fallback to different dependency versions is made.
- **Dependency or MKL check fails:** rerun normal setup rather than -CheckOnly. Preserve the full error if it persists.
- **ParaView not found:** install it separately from https://www.paraview.org/download/. You can still simulate and inspect PNG results without it. The existing viewer launchers may refer to ParaView 6.1.1; open ParaView manually if your installation path differs.
- **Solver outputs already exist after cloning:** use a new --output folder for a fresh simulation, as described in the Week 4 guide. Tracked summaries and plots are saved research records, not a resumable solver state.

The smoke test checks the installed tools, not mesh convergence or physical accuracy of the research model. A clean-machine test may still reveal machine-specific runtime issues.

## macOS commands

```bash
./setup.sh
./ih2662.sh week1.py diode
./ih2662.sh week1.py mesh
./ih2662.sh week1.py mos
./ih2662.sh week1.py screenshot
./week3/Run-Week3.sh mesh
./week4/Run-Week4.sh check
```

The `.cmd` and `.ps1` files remain the Windows path; the `.sh` and `.command`
files are the macOS path.
