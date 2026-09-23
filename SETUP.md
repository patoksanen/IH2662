# Set up IH2662 on Windows

1. Clone the repository or extract the complete ZIP into a normal folder.
2. Install **64-bit Python 3.12** from https://www.python.org/downloads/windows/ and include the Python launcher. Git is optional if you downloaded a ZIP.
3. Double-click **Setup.cmd**. Leave the window open while it downloads and installs the locked Python packages.
4. Confirm the final **PASS: IH2662 simulation environment is ready.** message. A failure exits with a nonzero code and prints the failing step.
5. Read week4/START-HERE.md. Regenerate meshes or run a new simulation case to obtain ParaView datasets; large datasets are not in Git.

No administrator privileges are normally required when the project folder is writable. Setup.cmd uses Windows PowerShell with a process-local execution-policy setting; it does not change the machine's execution policy. If an organization policy blocks it, follow that organization's software-installation procedure.

## What setup does
- Uses an existing .venv if present; otherwise creates one with 64-bit Python 3.12.
- Installs the exact versions in requirements-lock.txt. On an existing environment, this may align installed package versions with the lock file. Use check-only mode to avoid installation.
- Runs pip check and verifies every locked version.
- Checks the MKL DLL path expected by ih2662.cmd and sets DLL paths and thread limits for its own checks.
- Generates a tiny Gmsh mesh, reads it with meshio, saves/reads a PyVista dataset, generates a Matplotlib PNG, and runs the official 1D DEVSIM diode example with the project UMFPACK backend.
- Keeps test output in a temporary directory, leaving week3/week4 simulation results untouched.
- Detects ParaView on PATH or under Program Files, without installing or launching it.

## Commands
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
